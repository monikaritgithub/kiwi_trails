/* Client script for submitting customer tour reviews.
Handles 5-star selection and submits feedback to /reviews.
*/

import { apiFetch } from '../api.js';
import { requireAuth } from '../auth.js';
import { showToast } from '../helpers.js';

let selectedRating = 5;

document.addEventListener('DOMContentLoaded', () => {
  requireAuth();

  const urlParams = new URLSearchParams(window.location.search);
  const bookingId = urlParams.get('booking_id') || '41';
  document.getElementById('booking-id-input').value = bookingId;

  setupStarRating();

  const form = document.getElementById('review-form');
  const errorBanner = document.getElementById('error-banner');
  const successBanner = document.getElementById('success-banner');
  const submitBtn = document.getElementById('btn-submit');

  form.addEventListener('submit', async (e) => {
    e.preventDefault();
    errorBanner.style.display = 'none';
    successBanner.style.display = 'none';

    const booking_id = parseInt(document.getElementById('booking-id-input').value);
    const rating = selectedRating;
    const comment = document.getElementById('comment').value.trim();

    submitBtn.disabled = true;
    submitBtn.textContent = 'Submitting review...';

    try {
      await apiFetch('/reviews', {
        method: 'POST',
        body: { booking_id, rating, comment }
      });

      successBanner.textContent = 'Ngā mihi nui! Your review has been recorded.';
      successBanner.style.display = 'block';
      showToast('Review submitted successfully!', 'success');

      setTimeout(() => {
        window.location.href = '/frontend/pages/my-bookings.html';
      }, 1200);
    } catch (err) {
      errorBanner.textContent = err.message || 'Failed to submit review. Each completed booking may only be reviewed once.';
      errorBanner.style.display = 'block';
      submitBtn.disabled = false;
      submitBtn.textContent = 'Submit Review';
    }
  });
});

function setupStarRating() {
  const container = document.getElementById('star-rating');
  const stars = container.querySelectorAll('span');

  function updateStars(val) {
    stars.forEach(s => {
      const starVal = parseInt(s.dataset.value);
      s.style.color = starVal <= val ? '#D4AF37' : '#CBD5E1';
    });
  }

  updateStars(selectedRating);

  stars.forEach(s => {
    s.addEventListener('mouseover', () => {
      updateStars(parseInt(s.dataset.value));
    });

    s.addEventListener('mouseout', () => {
      updateStars(selectedRating);
    });

    s.addEventListener('click', () => {
      selectedRating = parseInt(s.dataset.value);
      document.getElementById('rating-input').value = selectedRating;
      updateStars(selectedRating);
    });
  });
}
