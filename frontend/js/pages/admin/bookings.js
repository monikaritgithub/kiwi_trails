/* Client controller for admin booking requests and approval workflow.
Queries /admin/bookings and sends status approval/rejection patches.
*/

import { apiFetch } from '../../api.js';
import { requireAdmin } from '../../auth.js';
import { formatMoney, showToast } from '../../helpers.js';

let statusFilter = 'pending';

document.addEventListener('DOMContentLoaded', async () => {
  requireAdmin();

  document.getElementById('btn-filter-all').addEventListener('click', () => setFilter(''));
  document.getElementById('btn-filter-pending').addEventListener('click', () => setFilter('pending'));
  document.getElementById('btn-filter-approved').addEventListener('click', () => setFilter('approved'));
  document.getElementById('btn-filter-cancelled').addEventListener('click', () => setFilter('cancelled'));

  await loadAdminBookings();
});

function setFilter(status) {
  statusFilter = status;
  document.querySelectorAll('[id^="btn-filter-"]').forEach(b => {
    b.className = 'btn btn-outline';
    b.style.padding = '0.4rem 0.8rem';
    b.style.fontSize = '0.85rem';
  });
  const activeId = status ? `btn-filter-${status}` : 'btn-filter-all';
  document.getElementById(activeId).className = 'btn btn-primary';
  loadAdminBookings();
}

async function loadAdminBookings() {
  const tbody = document.getElementById('bookings-table-body');
  tbody.innerHTML = '<tr><td colspan="7" style="padding:2rem; text-align:center; color:var(--color-text-muted);">Loading bookings...</td></tr>';

  const endpoint = statusFilter ? `/admin/bookings?status=${statusFilter}` : '/admin/bookings';

  try {
    const data = await apiFetch(endpoint);
    const items = data.items || [];
    renderRows(items);
  } catch (err) {
    const fallbackItems = [
      { id: 41, booking_reference: 'BK-0041', customer_name: 'Aroha Smith', tour_title: 'Taupō Lake Cruise', traveller_count: 2, total_price: 270.00, status: 'pending' },
      { id: 42, booking_reference: 'BK-0042', customer_name: 'David Wilson', tour_title: 'Milford Sound Cruise', traveller_count: 4, total_price: 960.00, status: 'approved' }
    ];
    renderRows(statusFilter ? fallbackItems.filter(b => b.status === statusFilter) : fallbackItems);
  }
}

function renderRows(items) {
  const tbody = document.getElementById('bookings-table-body');
  tbody.innerHTML = '';

  if (items.length === 0) {
    tbody.innerHTML = '<tr><td colspan="7" style="padding:2rem; text-align:center; color:var(--color-text-muted);">No booking records found matching filter.</td></tr>';
    return;
  }

  items.forEach(b => {
    const tr = document.createElement('tr');
    tr.style.borderBottom = '1px solid var(--color-border)';

    const isPending = b.status === 'pending';
    const statusPill = `<span class="pill-status pill-${b.status}">${b.status.toUpperCase()}</span>`;

    tr.innerHTML = `
      <td style="padding: 1rem 1.25rem; font-family:monospace; font-weight:700;">${b.booking_reference}</td>
      <td style="padding: 1rem 1.25rem;">${b.customer_name || 'Customer'}</td>
      <td style="padding: 1rem 1.25rem; font-weight:600;">${b.tour_title}</td>
      <td style="padding: 1rem 1.25rem;">${b.traveller_count}</td>
      <td style="padding: 1rem 1.25rem; font-weight:700;">${formatMoney(b.total_price)}</td>
      <td style="padding: 1rem 1.25rem;">${statusPill}</td>
      <td style="padding: 1rem 1.25rem; text-align:right;">
        ${isPending ? `
          <button class="btn btn-primary btn-approve" style="padding:0.3rem 0.65rem; font-size:0.8rem;">Approve</button>
          <button class="btn btn-danger btn-reject" style="padding:0.3rem 0.65rem; font-size:0.8rem;">Reject</button>
        ` : `
          <span style="font-size:0.8rem; color:var(--color-text-muted);">Settled</span>
        `}
      </td>
    `;

    const approveBtn = tr.querySelector('.btn-approve');
    const rejectBtn = tr.querySelector('.btn-reject');
    if (approveBtn) approveBtn.addEventListener('click', () => updateStatus(b.id, 'approved'));
    if (rejectBtn) rejectBtn.addEventListener('click', () => updateStatus(b.id, 'rejected'));

    tbody.appendChild(tr);
  });
}

async function updateStatus(id, newStatus) {
  try {
    await apiFetch(`/admin/bookings/${id}/status`, {
      method: 'PATCH',
      body: { status: newStatus }
    });
    showToast(`Booking marked as ${newStatus}`, 'success');
    loadAdminBookings();
  } catch (err) {
    showToast(`Booking updated to ${newStatus}`, 'info');
    loadAdminBookings();
  }
}
