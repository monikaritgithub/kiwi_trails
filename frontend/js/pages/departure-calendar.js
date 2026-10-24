/* Client script for monthly departure availability calendar.
Queries /departures/calendar, builds day cells, and reveals departure details.
*/

import { apiFetch } from '../api.js';
import { formatDateTime, formatDate } from '../helpers.js';
import { isAuthenticated } from '../auth.js';

let activeYear = 2026;
let activeMonth = 11;
let departuresMap = {};

document.addEventListener('DOMContentLoaded', () => {
  setupNavbar();
  renderCalendar();

  document.getElementById('btn-prev-month').addEventListener('click', () => {
    activeMonth--;
    if (activeMonth < 1) {
      activeMonth = 12;
      activeYear--;
    }
    renderCalendar();
  });

  document.getElementById('btn-next-month').addEventListener('click', () => {
    activeMonth++;
    if (activeMonth > 12) {
      activeMonth = 1;
      activeYear++;
    }
    renderCalendar();
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

async function renderCalendar() {
  const monthString = `${activeYear}-${String(activeMonth).padStart(2, '0')}`;
  const dateObj = new Date(activeYear, activeMonth - 1, 1);
  const monthName = dateObj.toLocaleString('en-NZ', { month: 'long', year: 'numeric' });
  document.getElementById('current-month-label').textContent = monthName;

  try {
    const data = await apiFetch(`/departures/calendar?month=${monthString}`);
    const items = data.items || [];
    departuresMap = {};
    items.forEach(dep => {
      const dayKey = dep.start_datetime.substring(0, 10);
      if (!departuresMap[dayKey]) departuresMap[dayKey] = [];
      departuresMap[dayKey].push(dep);
    });
  } catch (err) {
    departuresMap = {};
  }

  buildGrid();
}

function buildGrid() {
  const grid = document.getElementById('calendar-grid');
  grid.innerHTML = '';

  const firstDayIndex = new Date(activeYear, activeMonth - 1, 1).getDay();
  const daysInMonth = new Date(activeYear, activeMonth, 0).getDate();

  for (let i = 0; i < firstDayIndex; i++) {
    const blank = document.createElement('div');
    blank.style.minHeight = '90px';
    blank.style.background = '#F8FAF9';
    blank.style.borderRadius = 'var(--radius-sm)';
    grid.appendChild(blank);
  }

  for (let day = 1; day <= daysInMonth; day++) {
    const dayKey = `${activeYear}-${String(activeMonth).padStart(2, '0')}-${String(day).padStart(2, '0')}`;
    const cell = document.createElement('div');
    cell.style.minHeight = '90px';
    cell.style.padding = '0.5rem';
    cell.style.border = '1px solid var(--color-border)';
    cell.style.borderRadius = 'var(--radius-sm)';
    cell.style.background = 'var(--color-surface)';
    cell.style.cursor = 'pointer';

    const dayNumber = document.createElement('div');
    dayNumber.textContent = day;
    dayNumber.style.fontWeight = '700';
    dayNumber.style.fontSize = '0.85rem';
    dayNumber.style.marginBottom = '0.25rem';
    cell.appendChild(dayNumber);

    const deps = departuresMap[dayKey] || [];
    if (deps.length > 0) {
      cell.style.background = '#F0FDF4';
      cell.style.borderColor = '#86EFAC';
      const indicator = document.createElement('div');
      indicator.className = 'badge badge-kaitiaki';
      indicator.style.fontSize = '0.7rem';
      indicator.textContent = `${deps.length} tour${deps.length > 1 ? 's' : ''}`;
      cell.appendChild(indicator);
    }

    cell.addEventListener('click', () => showDateDetails(dayKey, deps));
    grid.appendChild(cell);
  }
}

function showDateDetails(dayKey, deps) {
  const panel = document.getElementById('date-details-panel');
  const label = document.getElementById('selected-date-label');
  const toursList = document.getElementById('selected-date-tours');

  panel.style.display = 'block';
  label.textContent = `Departures on ${formatDate(dayKey)}`;
  toursList.innerHTML = '';

  if (deps.length === 0) {
    toursList.innerHTML = '<p style="color:var(--color-text-muted);">No departures scheduled on this date.</p>';
    return;
  }

  deps.forEach(dep => {
    const item = document.createElement('div');
    item.className = 'card';
    item.style.padding = '1rem 1.25rem';
    item.style.flexDirection = 'row';
    item.style.justifyContent = 'space-between';
    item.style.alignItems = 'center';
    item.innerHTML = `
      <div>
        <h4 style="margin-bottom:0.25rem;">${dep.tour_title}</h4>
        <p style="font-size:0.85rem; color:var(--color-text-muted); margin:0;">
          Time: ${formatDateTime(dep.start_datetime)} &bull; Seats left: <strong>${dep.seats_left || dep.capacity}</strong>
        </p>
      </div>
      <a href="/frontend/pages/booking-form.html?departure_id=${dep.id}&tour_id=${dep.tour_id}" class="btn btn-primary" style="padding:0.45rem 1rem;">Book Now</a>
    `;
    toursList.appendChild(item);
  });

  panel.scrollIntoView({ behavior: 'smooth' });
}
