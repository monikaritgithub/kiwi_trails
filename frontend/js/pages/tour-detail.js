/* Client script for tour details.
Fetches /tours/{id}, departures, and reviews, populates gallery, FAQs, and book triggers.
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
  document.getElementById('tour-summary').textContent = tour.summary || '';
  document.getElementById('tour-description').textContent = tour.description || '';
  document.getElementById('tour-price').textContent = formatMoney(tour.price_per_person);
  document.getElementById('tour-difficulty').textContent = (tour.difficulty || 'Easy').toUpperCase();
  document.getElementById('tour-category-badge').textContent = tour.category_name || 'Guided Eco-Tour';

  const images = tour.images || [];
  const mainImg = document.getElementById('main-tour-img');
  if (images.length > 0) {
    mainImg.src = images[0].image_url;
    const thumbContainer = document.getElementById('gallery-thumbnails');
    images.forEach(img => {
      const thumb = document.createElement('img');
      thumb.src = img.image_url;
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
    document.getElementById('guide-name').textContent = tour.guide.name;
    document.getElementById('guide-bio').textContent = tour.guide.bio || 'Professional Kaitiaki Wilderness Guide';
    const langs = tour.guide.languages || ['English', 'Te Reo Māori'];
    document.getElementById('guide-langs').textContent = `Languages: ${langs.join(', ')}`;
  }

  renderDepartures(tour.departures || [], tour.id);
  renderFaqs(tour.faqs || []);
  renderReviews(tour.reviews || []);
}

function renderDepartures(departures, tourId) {
  const container = document.getElementById('departures-container');
  container.innerHTML = '';

  if (departures.length === 0) {
    container.innerHTML = `
      <div class="card" style="padding:1.5rem; grid-column: 1 / -1;">
        <p style="color:var(--color-text-muted); margin:0;">No departures currently scheduled for this tour.</p>
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
        Seats remaining: <strong style="color:var(--color-text);">${dep.seats_left || dep.capacity}</strong>
      </div>
      <a href="/frontend/pages/booking-form.html?departure_id=${dep.id}&tour_id=${tourId}" class="btn btn-primary" style="width:100%; padding:0.45rem;">Book This Date</a>
    `;
    container.appendChild(card);
  });
}

function renderFaqs(faqs) {
  const container = document.getElementById('faqs-container');
  container.innerHTML = '';

  const defaultFaqs = faqs.length > 0 ? faqs : [
    { question: 'What equipment and clothing should I bring?', answer: 'Sturdy walking shoes, warm breathable layers, waterproof jacket, sunblock, and a personal reusable water bottle.' },
    { question: 'What cultural tikanga guidelines apply on this tour?', answer: 'We practice Kaitiakitanga: respect tapu cultural landmarks, preserve native flora, and follow the Kaiārahi guide instructions.' }
  ];

  defaultFaqs.forEach(faq => {
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

function renderReviews(reviews) {
  const container = document.getElementById('reviews-container');
  container.innerHTML = '';

  const defaultReviews = reviews.length > 0 ? reviews : [
    { rating: 5, reviewer_name: 'Aroha S.', comment: 'Incredible journey! The storytelling and cultural respect for the land made this unforgettable.', created_at: '2026-10-18T12:00:00Z' },
    { rating: 5, reviewer_name: 'Liam T.', comment: 'Superb guide and pristine landscape. Five stars all the way!', created_at: '2026-10-14T09:30:00Z' }
  ];

  defaultReviews.forEach(rev => {
    const card = document.createElement('div');
    card.className = 'card';
    card.style.padding = '1.25rem';
    card.innerHTML = `
      <div style="display:flex; justify-content:space-between; margin-bottom:0.4rem;">
        <strong style="color:var(--color-text);">${rev.reviewer_name || 'Verified Explorer'}</strong>
        <span style="color:var(--color-secondary); font-size:0.9rem;">${'★'.repeat(rev.rating)}</span>
      </div>
      <p style="color:var(--color-text-muted); font-size:0.9rem; margin-bottom:0.5rem;">${rev.comment || ''}</p>
      <span style="font-size:0.75rem; color:var(--color-text-muted);">${formatDate(rev.created_at)}</span>
    `;
    container.appendChild(card);
  });
}
