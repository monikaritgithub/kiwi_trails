"""Matching domain services for evaluating and ranking tours.
Only interfaces with the catalog and departures domains through their public services.
Calculates explainable scores and transparent matching reasons.
"""

from apps.catalog.services import list_tours
from apps.departures.services import get_seats_taken, is_booking_open, list_tour_departures
from apps.matching.constants import (
    MAX_SCORE,
    WEIGHT_ACCESSIBILITY,
    WEIGHT_AVAILABILITY,
    WEIGHT_BUDGET,
    WEIGHT_DURATION,
    WEIGHT_INTEREST,
    WEIGHT_RATING,
)


def _format_price(price):
    try:
        val = float(price)
        return f"{val:.0f}" if val.is_integer() else f"{val:.2f}"
    except (ValueError, TypeError):
        return str(price)


def match_tours(criteria):
    """Rank active tours based on quiz preferences and provide clear explanations."""
    interests = [i.strip().lower() for i in criteria.get("interests", []) if i.strip()]
    budget = criteria.get("budget_per_person")
    if budget is not None:
        try:
            budget = float(budget)
        except (ValueError, TypeError):
            budget = None

    max_days = criteria.get("max_days")
    travellers = criteria.get("travellers") or 1
    accessibility_needs = bool(criteria.get("accessibility_needs", False))
    target_month = criteria.get("month")
    prefer_maori_led = bool(criteria.get("prefer_maori_led", False))

    # Retrieve all active tours with their annotated aggregates
    tours = list_tours({})
    results = []

    for tour in tours:
        score = 0.0
        reasons = []

        # 1. Interest Match (30 pts)
        cat_name = tour.category.name if tour.category else ""
        if interests:
            if cat_name.lower() in interests:
                score += WEIGHT_INTEREST
                reasons.append(f"Matches your interest: {cat_name}")
        else:
            score += WEIGHT_INTEREST

        # 2. Budget Match (20 pts)
        price = float(tour.price_per_person)
        if budget is not None and budget > 0:
            formatted_p = _format_price(price)
            formatted_b = _format_price(budget)
            if price <= budget:
                score += WEIGHT_BUDGET
                reasons.append(f"Within budget (NZ${formatted_p} of NZ${formatted_b})")
            elif price < 1.5 * budget:
                scale = max(0.0, 1.0 - (price - budget) / (0.5 * budget))
                score += WEIGHT_BUDGET * scale
                reasons.append(f"Near budget (NZ${formatted_p} vs NZ${formatted_b})")
        else:
            score += WEIGHT_BUDGET
            reasons.append(f"Price: NZ${_format_price(price)} per person")

        # 3. Duration Match (15 pts)
        if max_days is not None:
            if tour.duration_days <= max_days:
                score += WEIGHT_DURATION
                day_str = (
                    f"{tour.duration_days} day"
                    if tour.duration_days == 1
                    else f"{tour.duration_days} days"
                )
                reasons.append(f"Fits duration limit ({day_str})")
        else:
            score += WEIGHT_DURATION

        # 4. Accessibility Match (15 pts)
        if accessibility_needs:
            info = (tour.accessibility_info or "").strip()
            if info:
                score += WEIGHT_ACCESSIBILITY
                first_sentence = info.split(".")[0].strip()
                if first_sentence:
                    reasons.append(first_sentence)
                else:
                    reasons.append("Accessibility accommodations provided")
        else:
            score += WEIGHT_ACCESSIBILITY

        # 5. Rating (10 pts)
        avg_rating = tour.annotated_average_rating
        rev_count = tour.annotated_review_count or 0
        if avg_rating is not None and avg_rating > 0:
            rating_val = float(avg_rating)
            score += WEIGHT_RATING * (rating_val / 5.0)
            plural = "guests" if rev_count != 1 else "guest"
            reasons.append(f"Rated {rating_val:.1f} by {rev_count} {plural}")
        else:
            score += WEIGHT_RATING * 0.95
            reasons.append("Highly recommended new journey")

        # 6. Availability (10 pts)
        matched_departure = None
        matched_seats = None
        departures = list_tour_departures(tour.id)
        open_deps = []

        for dep in departures:
            if not is_booking_open(dep):
                continue
            seats_left = dep.capacity - get_seats_taken(dep)
            if seats_left < travellers:
                continue
            if target_month:
                dep_month = dep.start_datetime.strftime("%Y-%m")
                if dep_month != target_month:
                    continue
            open_deps.append((dep, seats_left))

        if open_deps:
            score += WEIGHT_AVAILABILITY
            best_dep, seats_left = open_deps[0]
            day_num = best_dep.start_datetime.day
            month_abbrev = best_dep.start_datetime.strftime("%b")
            traveller_word = "travellers" if travellers > 1 else "traveller"
            reasons.append(f"Seats for {travellers} {traveller_word} on {day_num} {month_abbrev}")
            matched_departure = best_dep.start_datetime.strftime("%Y-%m-%dT%H:%M:%SZ")
            matched_seats = seats_left
        else:
            if getattr(tour, "annotated_next_departure", None):
                matched_departure = tour.annotated_next_departure.strftime("%Y-%m-%dT%H:%M:%SZ")
            matched_seats = getattr(tour, "annotated_seats_left", None)

        # 7. Māori led Verified Operator
        is_maori = bool(tour.maori_led and tour.operator_verified)
        if is_maori:
            if tour.operator_name:
                reasons.append(f"Verified Māori led experience by {tour.operator_name}")
            else:
                reasons.append("Verified Māori led experience")
            if prefer_maori_led:
                score = min(float(MAX_SCORE), score + 5.0)

        final_score = int(round(min(float(MAX_SCORE), max(0.0, score))))

        results.append({
            "tour_id": tour.id,
            "title": tour.title,
            "score": final_score,
            "price_per_person": tour.price_per_person,
            "next_departure": matched_departure,
            "seats_left": matched_seats,
            "reasons": reasons,
            "operator_name": tour.operator_name or "",
            "maori_led": is_maori,
            "image_url": tour.annotated_image_url,
            "location": tour.location,
            "category": cat_name,
            "duration_days": tour.duration_days,
        })

    # Sort results by match score descending, then price ascending
    results.sort(key=lambda x: (-x["score"], x["price_per_person"], x["tour_id"]))
    return results
