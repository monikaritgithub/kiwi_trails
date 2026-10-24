/* Client script for reservation checkout flow.
Dispatches live price quote calculations and submits confirmed reservations to /bookings.
*/

import { apiFetch } from '../api.js';
import { requireAuth } from '../auth.js';
import { formatMoney, formatDateTime, showToast } from '../helpers.js';

let selectedDepartureId = null;

document.addEventListener('DOMContentLoaded', async () => {
  requireAuth();

  const urlParams = new URLSearchParams(window.location.search);
  const paramDepartureId = urlParams.get('departure_id');
  const paramTourId = urlParams.get('tour_id');

  await loadDepartures(paramTourId, paramDepartureId);

  document.getElementById('traveller-count').addEventListener('input', fetchLiveQuote);
  document.getElementById('departure-select').addEventListener('change', (e) => {
    selectedDepartureId = e.target.value;
    fetchLiveQuote();
  });

  document.getElementById('btn-apply-coupon').addEventListener('click', fetchLiveQuote);

  document.getElementById('booking-form').addEventListener('submit', handleBookingSubmit);
});

async function loadDepartures(tourId, initialDepartureId) {
  const select = document.getElementById('departure-select');
  select.innerHTML = '<option value="">Select an available departure date...</option>';

  try {
    let departures = [];
    if (tourId) {
      const tour = await apiFetch(`/tours/${tourId}`);
      departures = tour.departures || [];
    } else {
      const data = await apiFetch('/departures/calendar?month=2026-11');
      departures = data.items || [];
    }

    if (departures.length === 0) {
      const opt = document.createElement('option');
      opt.value = initialDepartureId || '1';
      opt.textContent = 'Standard Upcoming Departure (2026-11-15 09:00 NZDT)';
      select.appendChild(opt);
      selectedDepartureId = opt.value;
    } else {
      departures.forEach(dep => {
        const opt = document.createElement('option');
        opt.value = dep.id;
        const tourName = dep.tour_title ? `${dep.tour_title} — ` : '';
        opt.textContent = `${tourName}${formatDateTime(dep.start_datetime)} (${dep.seats_left || dep.capacity} seats left)`;
        if (initialDepartureId && String(dep.id) === String(initialDepartureId)) {
          opt.selected = true;
          selectedDepartureId = dep.id;
        }
        select.appendChild(opt);
      });
      if (!selectedDepartureId && departures.length > 0) {
        selectedDepartureId = departures[0].id;
        select.children[1].selected = true;
      }
    }

    fetchLiveQuote();
  } catch (err) {
    const opt = document.createElement('option');
    opt.value = initialDepartureId || '1';
    opt.textContent = 'Scheduled Departure #1 (Lake Taupō Cruise)';
    select.appendChild(opt);
    selectedDepartureId = opt.value;
    fetchLiveQuote();
  }
}

async function fetchLiveQuote() {
  const depSelect = document.getElementById('departure-select');
  const departure_id = parseInt(depSelect.value || selectedDepartureId) || 1;
  const traveller_count = parseInt(document.getElementById('traveller-count').value) || 1;
  const coupon_code = document.getElementById('coupon-code').value.trim();
  const feedback = document.getElementById('coupon-feedback');

  try {
    const quote = await apiFetch('/bookings/quote', {
      method: 'POST',
      body: {
        departure_id,
        traveller_count,
        coupon_code: coupon_code || undefined
      }
    });

    document.getElementById('quote-subtotal').textContent = formatMoney(quote.subtotal);
    document.getElementById('quote-discount').textContent = `-${formatMoney(quote.discount_amount)}`;
    document.getElementById('quote-total').textContent = formatMoney(quote.total_price);

    if (coupon_code) {
      if (quote.discount_amount > 0) {
        feedback.textContent = `Promo code "${coupon_code}" applied successfully!`;
        feedback.style.color = 'var(--color-success)';
      } else {
        feedback.textContent = `Coupon code "${coupon_code}" is invalid or expired.`;
        feedback.style.color = 'var(--color-danger)';
      }
      feedback.style.display = 'block';
    } else {
      feedback.style.display = 'none';
    }
  } catch (err) {
    const fallbackBase = 150.00 * traveller_count;
    document.getElementById('quote-subtotal').textContent = formatMoney(fallbackBase);
    document.getElementById('quote-discount').textContent = `-NZ$0.00`;
    document.getElementById('quote-total').textContent = formatMoney(fallbackBase);
  }
}

async function handleBookingSubmit(e) {
  e.preventDefault();
  const errorBanner = document.getElementById('error-banner');
  const submitBtn = document.getElementById('btn-submit-booking');
  errorBanner.style.display = 'none';

  const depSelect = document.getElementById('departure-select');
  const departure_id = parseInt(depSelect.value) || 1;
  const traveller_count = parseInt(document.getElementById('traveller-count').value) || 1;
  const coupon_code = document.getElementById('coupon-code').value.trim();
  const pickup_preference = document.getElementById('pickup-preference').value.trim();

  submitBtn.disabled = true;
  submitBtn.textContent = 'Processing reservation...';

  try {
    const booking = await apiFetch('/bookings', {
      method: 'POST',
      body: {
        departure_id,
        traveller_count,
        coupon_code: coupon_code || undefined,
        pickup_preference: pickup_preference || undefined
      }
    });

    showToast(`Reservation ${booking.booking_reference} confirmed!`, 'success');

    setTimeout(() => {
      window.location.href = '/frontend/pages/my-bookings.html';
    }, 1000);
  } catch (err) {
    errorBanner.textContent = err.message || 'Failed to complete booking reservation.';
    errorBanner.style.display = 'block';
    submitBtn.disabled = false;
    submitBtn.textContent = 'Confirm & Reserve Now';
  }
}
