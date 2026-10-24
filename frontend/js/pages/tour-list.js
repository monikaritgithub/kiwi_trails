/* Client script for the public tours catalog.
Queries /tours and /categories, renders tour cards with badges, prices, and pagination.
*/

import { apiFetch } from '../api.js';
import { formatMoney, formatDate } from '../helpers.js';
import { isAuthenticated } from '../auth.js';

let currentPage = 1;

document.addEventListener('DOMContentLoaded', async () => {
  setupNavbar();
  await loadCategories();
  await loadTours();

  document.getElementById('btn-apply-filters').addEventListener('click', () => {
    currentPage = 1;
    loadTours();
  });

  document.getElementById('search-input').addEventListener('keypress', (e) => {
    if (e.key === 'Enter') {
      currentPage = 1;
      loadTours();
    }
  });
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
  const sort = document.getElementById('sort-select').value;

  const params = new URLSearchParams();
  if (search) params.append('search', search);
  if (categoryId) params.append('category_id', categoryId);
  if (sort) params.append('sort', sort);
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

  const primaryImg = (tour.images && tour.images.length > 0)
    ? (tour.images.find(img => img.is_primary) || tour.images[0]).image_url
    : '/media/seed/tours/milford-sound-cruise-1.jpg';

  const departureText = tour.next_departure_date
    ? `Next: ${formatDate(tour.next_departure_date)}`
    : 'Upcoming departures';

  card.innerHTML = `
    <div class="card-img-wrap">
      <img src="${primaryImg}" alt="${tour.title}" class="card-img" onerror="this.src='https://images.unsplash.com/photo-1507699622108-4be3abd695ad?auto=format&fit=crop&w=800&q=80'">
    </div>
    <div class="card-body">
      <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:0.5rem;">
        <span class="badge badge-tikanga">${tour.category_name || 'Guided Eco-Tour'}</span>
        <span style="font-size:0.8rem; color:var(--color-text-muted);">${departureText}</span>
      </div>
      <h3 class="card-title">${tour.title}</h3>
      <p class="card-text">${tour.summary || tour.description || ''}</p>
      <div class="card-footer">
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
