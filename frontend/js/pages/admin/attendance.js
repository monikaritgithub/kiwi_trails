/* Client controller for passenger attendance roster.
Loads departure attendance manifest dynamically and manages passenger presence status.
*/

import { apiFetch } from '../../api.js';
import { requireAdmin } from '../../auth.js';
import { showToast } from '../../helpers.js';

let activeDepartureId = null;

document.addEventListener('DOMContentLoaded', async () => {
  requireAdmin();

  const urlParams = new URLSearchParams(window.location.search);
  activeDepartureId = urlParams.get('departure_id');

  document.getElementById('btn-print-manifest').addEventListener('click', () => window.print());

  await loadDeparturesOptions();
  if (activeDepartureId) {
    await loadAttendanceRoster();
  }

  document.getElementById('select-departure').addEventListener('change', (e) => {
    activeDepartureId = e.target.value;
    loadAttendanceRoster();
  });
});

async function loadDeparturesOptions() {
  const select = document.getElementById('select-departure');
  select.innerHTML = '';
  try {
    const now = new Date();
    const currentMonth = `${now.getFullYear()}-${String(now.getMonth() + 1).padStart(2, '0')}`;
    const nextDate = new Date(now.getFullYear(), now.getMonth() + 1, 1);
    const nextMonth = `${nextDate.getFullYear()}-${String(nextDate.getMonth() + 1).padStart(2, '0')}`;

    const [curRes, nextRes] = await Promise.allSettled([
      apiFetch(`/departures/calendar?month=${currentMonth}`),
      apiFetch(`/departures/calendar?month=${nextMonth}`)
    ]);

    const items = [];
    if (curRes.status === 'fulfilled' && curRes.value?.items) {
      items.push(...curRes.value.items);
    }
    if (nextRes.status === 'fulfilled' && nextRes.value?.items) {
      items.push(...nextRes.value.items);
    }

    if (items.length === 0) {
      select.innerHTML = '<option value="">No upcoming departures scheduled</option>';
      renderEmptyManifest('No upcoming departures scheduled.');
      return;
    }

    items.forEach(d => {
      const opt = document.createElement('option');
      opt.value = d.id;
      const dateStr = d.start_datetime ? d.start_datetime.substring(0, 10) : '';
      opt.textContent = `${d.tour_title || 'Tour'} (${dateStr})`;
      if (String(d.id) === String(activeDepartureId)) opt.selected = true;
      select.appendChild(opt);
    });

    if (!activeDepartureId && items.length > 0) {
      activeDepartureId = String(items[0].id);
      select.value = activeDepartureId;
    }
  } catch (err) {
    select.innerHTML = '<option value="">Unable to load departures</option>';
    renderEmptyManifest('Unable to load departures.');
  }
}

async function loadAttendanceRoster() {
  if (!activeDepartureId) return;
  const tbody = document.getElementById('attendance-table-body');
  tbody.innerHTML = '<tr><td colspan="5" style="padding:2rem; text-align:center; color:var(--color-text-muted);">Loading manifest...</td></tr>';

  try {
    const data = await apiFetch(`/admin/departures/${activeDepartureId}/attendance`);
    const items = data.items || [];
    if (items.length === 0) {
      renderEmptyManifest('No passenger bookings found for this departure.');
      return;
    }
    renderManifest(items);
  } catch (err) {
    renderEmptyManifest('No passenger bookings found or unable to load manifest.');
  }
}

function renderEmptyManifest(message) {
  document.getElementById('val-manifest-total').textContent = '0 Bookings';
  document.getElementById('val-manifest-present').textContent = '0 Present';
  const tbody = document.getElementById('attendance-table-body');
  tbody.innerHTML = `<tr><td colspan="5" style="padding: 2.5rem; text-align: center; color: var(--color-text-muted);">${message}</td></tr>`;
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
    const isAbsent = item.attendance === 'absent';
    const statusPill = isPresent
      ? '<span class="pill-status pill-approved">Present</span>'
      : (isAbsent ? '<span class="pill-status pill-cancelled">Absent</span>' : '<span class="pill-status pill-pending">Unmarked</span>');

    tr.innerHTML = `
      <td style="padding: 1rem 1.25rem; font-weight:700;">${item.customer_name || 'Passenger'}</td>
      <td style="padding: 1rem 1.25rem; font-family:monospace;">${item.booking_reference}</td>
      <td style="padding: 1rem 1.25rem;">${item.traveller_count || 1} Pax</td>
      <td style="padding: 1rem 1.25rem;">${statusPill}</td>
      <td style="padding: 1rem 1.25rem; text-align:right;">
        <button class="btn btn-outline btn-toggle-attendance" style="padding:0.3rem 0.65rem; font-size:0.8rem; ${isPresent ? 'background:#DCFCE7;' : ''}">
          ${isPresent ? 'Mark Absent' : 'Mark Present'}
        </button>
      </td>
    `;

    tr.querySelector('.btn-toggle-attendance').addEventListener('click', async () => {
      const newStatus = isPresent ? 'absent' : 'present';
      try {
        await apiFetch(`/admin/bookings/${item.booking_id}/attendance`, {
          method: 'PUT',
          body: { status: newStatus }
        });
        showToast(`${item.customer_name || 'Passenger'} marked as ${newStatus}`, 'success');
        item.attendance = newStatus;
        renderManifest(items);
      } catch (e) {
        showToast(e.message || 'Failed to update attendance status', 'danger');
      }
    });

    tbody.appendChild(tr);
  });
}
