/* Client script for the public tours catalog.
Queries /tours and /categories, renders tour cards with badges, prices, and pagination.
Includes interactive Trip Match recommendation quiz and Maori led operator filtering.
*/

import { apiFetch } from '../api.js';
import { formatMoney, formatDate, getIcon } from '../helpers.js';
import { isAuthenticated } from '../auth.js';

let currentPage = 1;

document.addEventListener('DOMContentLoaded', async () => {
  setupNavbar();
  await loadCategories();
  await loadTours();

  // Filters
  document.getElementById('btn-apply-filters').addEventListener('click', () => {
    currentPage = 1;
    loadTours();
  });

  const maoriFilter = document.getElementById('maori-led-filter');
  const urlParams = new URLSearchParams(window.location.search);
  if (urlParams.get('maori_led') === 'true' && maoriFilter) {
    maoriFilter.checked = true;
  }
  if (maoriFilter) {
    maoriFilter.addEventListener('change', () => {
      currentPage = 1;
      loadTours();
    });
  }

  document.getElementById('search-input').addEventListener('keypress', (e) => {
    if (e.key === 'Enter') {
      currentPage = 1;
      loadTours();
    }
  });

  // Trip Match Quiz controls
  setupTripMatch();
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

async function loadCategories() {
  try {
    const categories = await apiFetch('/categories');
    const select = document.getElementById('category-select');
    const list = Array.isArray(categories) ? categories : (categories.items || []);
    list.forEach(cat => {
      const opt = document.createElement('option');
      opt.value = cat.id;
      opt.textContent = cat.name;
      select.appendChild(opt);
    });
  } catch (err) {}
}

async function loadTours() {
  const loading = document.getElementById('loading-state');
  const empty = document.getElementById('empty-state');
  const grid = document.getElementById('tours-grid');

  loading.style.display = 'block';
  empty.style.display = 'none';
  grid.style.display = 'none';

  const search = document.getElementById('search-input').value.trim();
  const categoryId = document.getElementById('category-select').value;
  const sort = document.getElementById('sort-select').value || 'newest';
  const maoriLed = document.getElementById('maori-led-filter')?.checked;

  const params = new URLSearchParams();
  if (search) params.append('search', search);
  if (categoryId) params.append('category_id', categoryId);
  if (sort) params.append('sort', sort);
  if (maoriLed) params.append('maori_led', 'true');
  params.append('page', currentPage);

  try {
    const data = await apiFetch(`/tours?${params.toString()}`);
    const items = data.items || [];

    loading.style.display = 'none';

    if (items.length === 0) {
      empty.style.display = 'block';
      return;
    }

    grid.innerHTML = '';
    items.forEach(tour => {
      grid.appendChild(createTourCard(tour));
    });
    grid.style.display = 'grid';

    renderPagination(data.total || items.length, data.page_size || 9);
  } catch (err) {
    loading.textContent = 'Error loading tours. Please try again.';
  }
}

function createTourCard(tour) {
  const card = document.createElement('div');
  card.className = 'card';

  let primaryImg = tour.image_url;
  if (!primaryImg && tour.images && tour.images.length > 0) {
    const primary = tour.images.find(img => img.is_primary) || tour.images[0];
    primaryImg = primary.image_url;
  }
  if (!primaryImg) {
    primaryImg = '/media/seed/tours/milford-sound-cruise-1.jpg';
  }

  const departureDate = tour.next_departure || tour.next_departure_date;
  const departureText = departureDate
    ? `Next: ${formatDate(departureDate)}`
    : 'Upcoming departures';

  const categoryName = tour.category || tour.category_name || 'Guided Eco Tour';
  const ratingHtml = tour.average_rating
    ? `<span style="font-size:0.85rem; font-weight:700; color:var(--color-secondary); display:inline-flex; align-items:center; gap:0.25rem;">${getIcon('star')} ${Number(tour.average_rating).toFixed(1)}</span>`
    : '';

  // Maori led verified badge
  let maoriBadge = '';
  if (tour.maori_led) {
    maoriBadge = `<span class="badge badge-maori">${getIcon('verified')} Māori Led</span>`;
  }

  // Operator attribution if available
  let operatorInfo = '';
  if (tour.operator_name) {
    operatorInfo = `<span style="font-size:0.8rem; color:var(--color-text-muted); display:block; margin-top:0.25rem;">Operator: <strong>${tour.operator_name}</strong></span>`;
  }

  card.innerHTML = `
    <div class="card-img-wrap">
      <img src="${primaryImg}" alt="${tour.title}" class="card-img" onerror="this.onerror=null; if(!this.src.includes('127.0.0.1:8000')){ this.src='http://127.0.0.1:8000' + '${tour.image_url || ''}'; }">
    </div>
    <div class="card-body">
      <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:0.5rem; flex-wrap:wrap; gap:0.35rem;">
        <div style="display:flex; gap:0.35rem; align-items:center; flex-wrap:wrap;">
          <span class="badge badge-tikanga">${categoryName}</span>
          ${maoriBadge}
        </div>
        <div style="display:flex; align-items:center; gap:0.5rem;">
          ${ratingHtml}
          <span style="font-size:0.8rem; color:var(--color-text-muted);">${departureText}</span>
        </div>
      </div>
      <h3 class="card-title">${tour.title}</h3>
      <p class="card-text">${tour.location ? `Experience pristine landscapes and sacred heritage in ${tour.location}.` : 'Authentic guided conservation journey.'} (${tour.duration_days || 1} Day${(tour.duration_days || 1) > 1 ? 's' : ''})</p>
      ${operatorInfo}
      <div class="card-footer" style="margin-top: auto; padding-top: 1rem;">
        <div>
          <span style="font-size:0.8rem; color:var(--color-text-muted); display:block;">From</span>
          <span style="font-weight:800; font-size:1.25rem; color:var(--color-primary);">${formatMoney(tour.price_per_person)}</span>
        </div>
        <a href="/frontend/pages/tour-detail.html?id=${tour.id}" class="btn btn-primary" style="padding:0.45rem 1rem;">View Tour</a>
      </div>
    </div>
  `;
  return card;
}

function renderPagination(total, pageSize) {
  const container = document.getElementById('pagination-container');
  container.innerHTML = '';
  const totalPages = Math.ceil(total / pageSize);
  if (totalPages <= 1) return;

  for (let i = 1; i <= totalPages; i++) {
    const btn = document.createElement('button');
    btn.className = `btn ${i === currentPage ? 'btn-primary' : 'btn-outline'}`;
    btn.textContent = i;
    btn.style.padding = '0.35rem 0.85rem';
    btn.addEventListener('click', () => {
      currentPage = i;
      loadTours();
      window.scrollTo({ top: 300, behavior: 'smooth' });
    });
    container.appendChild(btn);
  }
}

function setupTripMatch() {
  const modal = document.getElementById('quiz-modal');
  const btnOpen = document.getElementById('btn-open-trip-match');
  const btnClose = document.getElementById('btn-close-quiz');
  const btnCancel = document.getElementById('btn-cancel-quiz');
  const form = document.getElementById('trip-match-form');
  const resultsContainer = document.getElementById('quiz-results-container');
  const resultsList = document.getElementById('quiz-results-list');
  const btnRetake = document.getElementById('btn-retake-quiz');

  if (!modal || !btnOpen) return;

  const urlParams = new URLSearchParams(window.location.search);
  if (urlParams.get('quiz') === '1' || window.location.hash === '#trip-match') {
    modal.style.display = 'flex';
  }

  btnOpen.addEventListener('click', () => {
    modal.style.display = 'flex';
  });

  const closeModal = () => {
    modal.style.display = 'none';
  };

  if (btnClose) btnClose.addEventListener('click', closeModal);
  if (btnCancel) btnCancel.addEventListener('click', closeModal);

  // Interest pill toggles
  const pills = document.querySelectorAll('#quiz-interests-group .quiz-pill');
  pills.forEach(pill => {
    pill.addEventListener('click', () => {
      pill.classList.toggle('active');
    });
  });

  // Retake / modify
  if (btnRetake) {
    btnRetake.addEventListener('click', () => {
      resultsContainer.style.display = 'none';
      form.style.display = 'block';
    });
  }

  // Submit quiz
  if (form) {
    form.addEventListener('submit', async (e) => {
      e.preventDefault();
      const submitBtn = document.getElementById('btn-submit-quiz');
      submitBtn.disabled = true;
      submitBtn.textContent = 'Analyzing journeys...';

      // Gather interests
      const activePills = document.querySelectorAll('#quiz-interests-group .quiz-pill.active');
      const selectedInterests = Array.from(activePills).map(p => p.dataset.interest);

      const budgetVal = document.getElementById('quiz-budget').value.trim();
      const travellersVal = document.getElementById('quiz-travellers').value.trim();
      const daysVal = document.getElementById('quiz-days').value.trim();
      const monthVal = document.getElementById('quiz-month').value.trim();
      const accessVal = document.getElementById('quiz-accessibility').checked;
      const maoriVal = document.getElementById('quiz-maori-led').checked;

      const payload = {
        interests: selectedInterests,
        budget_per_person: budgetVal ? parseFloat(budgetVal) : null,
        travellers: travellersVal ? parseInt(travellersVal, 10) : 1,
        max_days: daysVal ? parseInt(daysVal, 10) : null,
        month: monthVal || null,
        accessibility_needs: accessVal,
        prefer_maori_led: maoriVal
      };

      try {
        const res = await apiFetch('/matches', {
          method: 'POST',
          body: payload
        });

        const items = res.items || [];
        resultsList.innerHTML = '';

        if (items.length === 0) {
          resultsList.innerHTML = '<p style="text-align:center; color:var(--color-text-muted);">No tours matched your criteria. Try adjusting your budget or dates.</p>';
        } else {
          items.forEach(item => {
            const card = document.createElement('div');
            card.className = 'match-result-card';

            const maoriBadge = item.maori_led
              ? `<span class="badge badge-maori">${getIcon('verified')} Māori Led</span>`
              : '';

            const reasonsHtml = (item.reasons || [])
              .map(r => `<li class="match-reason-item">${getIcon('check')} <span>${r}</span></li>`)
              .join('');

            const imgUrl = item.image_url || '/media/seed/tours/milford-sound-cruise-1.jpg';

            card.innerHTML = `
              <div style="width:100%; height:110px; border-radius:var(--radius-md); overflow:hidden; background:#E2E8F0;">
                <img src="${imgUrl}" alt="${item.title}" style="width:100%; height:100%; object-fit:cover;" onerror="this.src='https://images.unsplash.com/photo-1507699622108-4be3abd695ad?auto=format&fit=crop&w=400&q=80'">
              </div>
              <div>
                <div style="display:flex; align-items:center; gap:0.5rem; margin-bottom:0.35rem; flex-wrap:wrap;">
                  <span class="match-score-badge">${item.score}% Match</span>
                  <span class="badge badge-tikanga">${item.category}</span>
                  ${maoriBadge}
                </div>
                <h4 style="margin:0 0 0.25rem; font-size:1.15rem; color:var(--color-primary);">${item.title}</h4>
                <div style="font-size:0.85rem; color:var(--color-text-muted); margin-bottom:0.5rem;">
                  <strong>${formatMoney(item.price_per_person)}</strong> per person &bull; ${item.location} &bull; ${item.duration_days} Day(s)
                </div>
                <strong style="font-size:0.8rem; text-transform:uppercase; letter-spacing:0.5px; color:var(--color-primary);">Why this fits you:</strong>
                <ul class="match-reasons-list">
                  ${reasonsHtml}
                </ul>
              </div>
              <div style="text-align:right;">
                <a href="/frontend/pages/tour-detail.html?id=${item.tour_id}" class="btn btn-primary" style="padding:0.55rem 1.25rem; white-space:nowrap;">View Tour</a>
              </div>
            `;
            resultsList.appendChild(card);
          });
        }

        form.style.display = 'none';
        resultsContainer.style.display = 'block';
      } catch (err) {
        alert(err.message || 'Failed to calculate tour recommendations.');
      } finally {
        submitBtn.disabled = false;
        submitBtn.textContent = 'Calculate My Matches';
      }
    });
  }
}
