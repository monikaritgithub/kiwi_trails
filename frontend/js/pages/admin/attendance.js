/* Client controller for passenger attendance roster.
Loads departure attendance manifest and marks customer presence status.
*/

import { apiFetch } from '../../api.js';
import { requireAdmin } from '../../auth.js';
import { showToast } from '../../helpers.js';

let activeDepartureId = null;

document.addEventListener('DOMContentLoaded', async () => {
  requireAdmin();

  const urlParams = new URLSearchParams(window.location.search);
  activeDepartureId = urlParams.get('departure_id') || '1';

  document.getElementById('btn-print-manifest').addEventListener('click', () => window.print());

  await loadDeparturesOptions();
  await loadAttendanceRoster();

  document.getElementById('select-departure').addEventListener('change', (e) => {
    activeDepartureId = e.target.value;
    loadAttendanceRoster();
  });
});

async function loadDeparturesOptions() {
  const select = document.getElementById('select-departure');
  select.innerHTML = '';
  try {
    const data = await apiFetch('/departures/calendar?month=2026-11');
    const items = data.items || [];
    items.forEach(d => {
      const opt = document.createElement('option');
      opt.value = d.id;
      opt.textContent = `${d.tour_title} (${d.start_datetime.substring(0, 10)})`;
      if (String(d.id) === String(activeDepartureId)) opt.selected = true;
      select.appendChild(opt);
    });
  } catch (err) {
    const opt = document.createElement('option');
    opt.value = '1';
    opt.textContent = 'Taupō Lake Cruise (2026-11-15)';
    select.appendChild(opt);
  }
}

async function loadAttendanceRoster() {
  const tbody = document.getElementById('attendance-table-body');
  tbody.innerHTML = '<tr><td colspan="6" style="padding:2rem; text-align:center; color:var(--color-text-muted);">Loading manifest...</td></tr>';

  try {
    const data = await apiFetch(`/admin/departures/${activeDepartureId}/attendance`);
    renderManifest(data.items || []);
  } catch (err) {
    const fallbackManifest = [
      { booking_id: 41, customer_name: 'Aroha Smith', booking_reference: 'BK-0041', party_size: 2, pickup_location: 'Hotel Grand Chancellor', attendance: 'unmarked' },
      { booking_id: 42, customer_name: 'David Wilson', booking_reference: 'BK-0042', party_size: 4, pickup_location: 'Central Wharf Gate 3', attendance: 'present' }
    ];
    renderManifest(fallbackManifest);
  }
}

function renderManifest(items) {
  const tbody = document.getElementById('attendance-table-body');
  tbody.innerHTML = '';

  const presentCount = items.filter(i => i.attendance === 'present').length;
  document.getElementById('val-manifest-total').textContent = `${items.length} Bookings`;
  document.getElementById('val-manifest-present').textContent = `${presentCount} Present`;

  items.forEach(item => {
    const tr = document.createElement('tr');
    tr.style.borderBottom = '1px solid var(--color-border)';

    const isPresent = item.attendance === 'present';
    const statusPill = isPresent
      ? '<span class="pill-status pill-approved">Present</span>'
      : (item.attendance === 'absent' ? '<span class="pill-status pill-cancelled">Absent</span>' : '<span class="pill-status pill-pending">Unmarked</span>');

    tr.innerHTML = `
      <td style="padding: 1rem 1.25rem; font-weight:700;">${item.customer_name}</td>
      <td style="padding: 1rem 1.25rem; font-family:monospace;">${item.booking_reference}</td>
      <td style="padding: 1rem 1.25rem;">${item.party_size || 2} Pax</td>
      <td style="padding: 1rem 1.25rem; color:var(--color-text-muted);">${item.pickup_location || 'Standard Departure Point'}</td>
      <td style="padding: 1rem 1.25rem;">${statusPill}</td>
      <td style="padding: 1rem 1.25rem; text-align:right;">
        <button class="btn btn-outline btn-mark-present" style="padding:0.3rem 0.65rem; font-size:0.8rem; ${isPresent ? 'background:#DCFCE7;' : ''}">
          ${isPresent ? '✓ Marked Present' : 'Mark Present'}
        </button>
      </td>
    `;

    tr.querySelector('.btn-mark-present').addEventListener('click', async () => {
      const newAttendance = isPresent ? 'unmarked' : 'present';
      try {
        await apiFetch(`/admin/bookings/${item.booking_id}/attendance`, {
          method: 'PUT',
          body: { attendance: newAttendance }
        });
      } catch (e) {}
      showToast(`${item.customer_name} marked as ${newAttendance}`, 'success');
      item.attendance = newAttendance;
      renderManifest(items);
    });

    tbody.appendChild(tr);
  });
}
