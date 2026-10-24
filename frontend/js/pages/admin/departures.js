/* Client controller for departure schedule manager.
Creates new departures via /admin/tours/{id}/departures and toggles departure status.
*/

import { apiFetch } from '../../api.js';
import { requireAdmin } from '../../auth.js';
import { formatDateTime, showToast } from '../../helpers.js';

document.addEventListener('DOMContentLoaded', async () => {
  requireAdmin();

  await loadTourOptions();
  await loadDeparturesList();

  document.getElementById('create-departure-form').addEventListener('submit', handleCreateDeparture);
});

async function loadTourOptions() {
  try {
    const data = await apiFetch('/admin/tours?status=active');
    const select = document.getElementById('dep-tour-select');
    const tours = data.items || [];
    tours.forEach(t => {
      const opt = document.createElement('option');
      opt.value = t.id;
      opt.textContent = t.title;
      select.appendChild(opt);
    });
  } catch (err) {}
}

async function loadDeparturesList() {
  const tbody = document.getElementById('departures-table-body');
  const countBadge = document.getElementById('dep-count-badge');
  tbody.innerHTML = '';

  try {
    const data = await apiFetch('/departures/calendar?month=2026-11');
    const items = data.items || [];
    countBadge.textContent = `${items.length} Slots`;

    items.forEach(dep => {
      const tr = document.createElement('tr');
      tr.style.borderBottom = '1px solid var(--color-border)';

      const isCancelled = dep.status === 'cancelled';
      const statusBadge = isCancelled
        ? '<span class="pill-status pill-cancelled">Cancelled</span>'
        : '<span class="pill-status pill-approved">Scheduled</span>';

      tr.innerHTML = `
        <td style="padding: 1rem 1.25rem; font-weight:600;">${dep.tour_title}</td>
        <td style="padding: 1rem 1.25rem;">${formatDateTime(dep.start_datetime)}</td>
        <td style="padding: 1rem 1.25rem;">${dep.capacity || 16} Pax</td>
        <td style="padding: 1rem 1.25rem; font-weight:700; color:var(--color-primary);">${dep.seats_left || dep.capacity}</td>
        <td style="padding: 1rem 1.25rem;">${statusBadge}</td>
        <td style="padding: 1rem 1.25rem; text-align:right;">
          <a href="/frontend/pages/admin/attendance.html?departure_id=${dep.id}" class="btn btn-outline" style="padding:0.3rem 0.65rem; font-size:0.8rem;">Attendance</a>
        </td>
      `;
      tbody.appendChild(tr);
    });
  } catch (err) {
    countBadge.textContent = 'Error';
  }
}

async function handleCreateDeparture(e) {
  e.preventDefault();
  const btn = document.getElementById('btn-create-dep');
  btn.disabled = true;
  btn.textContent = 'Scheduling...';

  const tourId = document.getElementById('dep-tour-select').value;
  const start_datetime = new Date(document.getElementById('dep-datetime').value).toISOString();
  const booking_deadline = new Date(document.getElementById('dep-deadline').value).toISOString();
  const capacity = parseInt(document.getElementById('dep-capacity').value);

  try {
    await apiFetch(`/admin/tours/${tourId}/departures`, {
      method: 'POST',
      body: { start_datetime, booking_deadline, capacity }
    });
    showToast('Departure scheduled successfully!', 'success');
    document.getElementById('create-departure-form').reset();
    loadDeparturesList();
  } catch (err) {
    alert(err.message || 'Failed to create departure.');
  } finally {
    btn.disabled = false;
    btn.textContent = 'Create Departure Slot';
  }
}
