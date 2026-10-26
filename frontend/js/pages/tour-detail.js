/* Client script for tour details.
Fetches /tours/{id}, departures, and reviews, populating gallery, itinerary, meeting coordinates, FAQs, and verified reviews.
*/

import { apiFetch } from '../api.js';
import { formatMoney, formatDateTime, formatDate } from '../helpers.js';
import { isAuthenticated } from '../auth.js';

document.addEventListener('DOMContentLoaded', async () => {
  setupNavbar();
  const urlParams = new URLSearchParams(window.location.search);
  const tourId = urlParams.get('id') || '1';

  try {
    const tour = await apiFetch(`/tours/${tourId}`);
    renderTourDetails(tour);
    await loadTourReviews(tourId);
  } catch (err) {
    document.getElementById('loading-state').textContent = 'Unable to load tour details.';
  }
});

function setupNavbar() {
  if (isAuthenticated()) {
    const navLogin = document.getElementById('nav-login');
    const navProfile = document.getElementById('nav-profile');
    const navBookings = document.getElementById('nav-bookings');
    if (navLogin) navLogin.style.display = 'none';
    if (navProfile) navProfile.style.display = 'inline-block';
    if (navBookings) navBookings.style.display = 'inline-block';
  }
}

function renderTourDetails(tour) {
  document.getElementById('loading-state').style.display = 'none';
  document.getElementById('tour-content').style.display = 'block';

  document.title = `${tour.title} — Kiwi Trails`;
  document.getElementById('tour-title').textContent = tour.title;
  document.getElementById('tour-category-badge').textContent = tour.category || 'Guided Eco-Tour';

  const locEl = document.getElementById('tour-location-badge');
  if (locEl) locEl.textContent = tour.location || 'New Zealand';

  const locText = document.getElementById('tour-location-text');
  if (locText) locText.textContent = tour.location ? `📍 Located in ${tour.location}` : '';

  const durEl = document.getElementById('tour-duration-badge');
  if (durEl) durEl.textContent = `${tour.duration_days || 1} Day${(tour.duration_days || 1) > 1 ? 's' : ''}`;

  document.getElementById('tour-description').textContent = tour.description || '';
  document.getElementById('tour-price').textContent = formatMoney(tour.price_per_person);

  const cancelDays = tour.cancellation_days !== undefined ? tour.cancellation_days : 3;
  const cancelEl = document.getElementById('tour-cancellation-badge');
  if (cancelEl) {
    cancelEl.textContent = cancelDays > 0 ? `Free Cancellation (${cancelDays}d window)` : 'Non-refundable';
  }

  const itinEl = document.getElementById('tour-itinerary');
  if (itinEl) {
    itinEl.textContent = tour.itinerary || 'Daily itinerary schedule provided upon booking confirmation.';
  }

  if (tour.meeting_point && tour.meeting_point.name) {
    document.getElementById('meeting-point-name').textContent = tour.meeting_point.name;
    const coords = (tour.meeting_point.lat !== null && tour.meeting_point.lng !== null)
      ? `GPS Coordinates: ${tour.meeting_point.lat.toFixed(5)}, ${tour.meeting_point.lng.toFixed(5)}`
      : '';
    document.getElementById('meeting-point-coords').textContent = coords;
  } else {
    document.getElementById('meeting-point-name').textContent = 'Meeting point details communicated prior to departure.';
  }

  const accessEl = document.getElementById('tour-accessibility');
  if (accessEl && tour.accessibility_info) {
    accessEl.textContent = tour.accessibility_info;
  }

  const guideEl = document.getElementById('tour-guidelines');
  if (guideEl && tour.visitor_guidelines) {
    guideEl.textContent = tour.visitor_guidelines;
  }

  const images = tour.images || [];
  const mainImg = document.getElementById('main-tour-img');
  if (images.length > 0) {
    mainImg.src = images[0].image_url;
    const thumbContainer = document.getElementById('gallery-thumbnails');
    thumbContainer.innerHTML = '';
    images.forEach(img => {
      const thumb = document.createElement('img');
      thumb.src = img.image_url;
      thumb.alt = img.alt_text || 'Tour preview';
      thumb.style.width = '80px';
      thumb.style.height = '60px';
      thumb.style.objectFit = 'cover';
      thumb.style.borderRadius = 'var(--radius-sm)';
      thumb.style.cursor = 'pointer';
      thumb.style.border = '2px solid transparent';
      thumb.addEventListener('click', () => {
        mainImg.src = img.image_url;
      });
      thumbContainer.appendChild(thumb);
    });
  } else {
    mainImg.src = '/media/seed/tours/milford-sound-cruise-1.jpg';
  }

  if (tour.guide) {
    document.getElementById('guide-name').textContent = tour.guide.full_name || tour.guide.name || 'Kaitiaki Guide';
    document.getElementById('guide-bio').textContent = tour.guide.bio || 'Professional Kaitiaki Wilderness Guide';
    const langs = tour.guide.languages || ['English', 'Te Reo Māori'];
    const langsArr = Array.isArray(langs) ? langs : [langs];
    document.getElementById('guide-langs').textContent = `Languages: ${langsArr.join(', ')}`;
  }

  const ratingEl = document.getElementById('rating-summary');
  if (ratingEl) {
    if (tour.average_rating !== null && tour.average_rating !== undefined) {
      ratingEl.textContent = `⭐ ${parseFloat(tour.average_rating).toFixed(1)} / 5.0`;
    } else {
      ratingEl.textContent = '⭐ No ratings yet';
    }
  }

  const countEl = document.getElementById('review-count-text');
  if (countEl) {
    countEl.textContent = `${tour.review_count || 0} verified customer review${(tour.review_count || 0) === 1 ? '' : 's'}`;
  }

  renderDepartures(tour.departures || [], tour.id);
  renderFaqs(tour.faqs || []);
}

function renderDepartures(departures, tourId) {
  const container = document.getElementById('departures-container');
  container.innerHTML = '';

  if (departures.length === 0) {
    container.innerHTML = `
      <div class="card" style="padding:1.5rem; grid-column: 1 / -1; text-align:center;">
        <p style="color:var(--color-text-muted); margin:0;">No upcoming departures currently scheduled for this tour.</p>
      </div>
    `;
    return;
  }

  departures.forEach(dep => {
    const card = document.createElement('div');
    card.className = 'card';
    card.style.padding = '1.25rem';
    card.innerHTML = `
      <div style="font-weight:700; color:var(--color-primary); font-size:1.05rem; margin-bottom:0.35rem;">
        ${formatDateTime(dep.start_datetime)}
      </div>
      <div style="font-size:0.85rem; color:var(--color-text-muted); margin-bottom:1rem;">
        Seats remaining: <strong style="color:var(--color-text);">${dep.seats_left !== undefined ? dep.seats_left : dep.capacity}</strong>
      </div>
      <a href="/frontend/pages/booking-form.html?departure_id=${dep.id}&tour_id=${tourId}" class="btn btn-primary" style="width:100%; padding:0.45rem;">Book This Date</a>
    `;
    container.appendChild(card);
  });
}

function renderFaqs(faqs) {
  const container = document.getElementById('faqs-container');
  container.innerHTML = '';

  if (!faqs || faqs.length === 0) {
    container.innerHTML = `
      <div class="card" style="padding:1.5rem; text-align:center;">
        <p style="color:var(--color-text-muted); margin:0;">No frequently asked questions currently listed for this tour.</p>
      </div>
    `;
    return;
  }

  faqs.forEach(faq => {
    const details = document.createElement('details');
    details.className = 'card';
    details.style.padding = '1rem 1.25rem';
    details.style.cursor = 'pointer';
    details.innerHTML = `
      <summary style="font-weight:700; color:var(--color-primary);">${faq.question}</summary>
      <p style="margin-top:0.75rem; margin-bottom:0; color:var(--color-text); font-size:0.92rem;">${faq.answer}</p>
    `;
    container.appendChild(details);
  });
}

async function loadTourReviews(tourId) {
  const container = document.getElementById('reviews-container');
  container.innerHTML = '<p style="grid-column:1/-1; color:var(--color-text-muted);">Loading traveler reviews...</p>';

  try {
    const data = await apiFetch(`/tours/${tourId}/reviews`);
    const reviews = data.items || [];
    container.innerHTML = '';

    if (reviews.length === 0) {
      container.innerHTML = `
        <div class="card" style="padding:2rem; grid-column:1/-1; text-align:center;">
          <p style="color:var(--color-text-muted); margin:0;">No customer reviews have been submitted for this tour yet.</p>
        </div>
      `;
      return;
    }

    reviews.forEach(rev => {
      const card = document.createElement('div');
      card.className = 'card';
      card.style.padding = '1.25rem';
      const stars = '⭐'.repeat(Math.max(1, Math.min(5, rev.rating || 5)));
      card.innerHTML = `
        <div style="display:flex; justify-content:space-between; margin-bottom:0.4rem;">
          <strong style="color:var(--color-text);">${rev.reviewer_name || 'Verified Explorer'}</strong>
          <span style="font-size:0.85rem;">${stars}</span>
        </div>
        <p style="color:var(--color-text-muted); font-size:0.9rem; margin-bottom:0.5rem; line-height:1.6;">${rev.comment || 'Authentic Aotearoa experience.'}</p>
        <span style="font-size:0.75rem; color:var(--color-text-muted);">${formatDate(rev.created_at)}</span>
      `;
      container.appendChild(card);
    });
  } catch (err) {
    container.innerHTML = `
      <div class="card" style="padding:1.5rem; grid-column:1/-1; text-align:center;">
        <p style="color:var(--color-text-muted); margin:0;">No customer reviews submitted yet.</p>
      </div>
    `;
  }
}
