/* Client controller for admin booking requests and approval workflow.
Queries /admin/bookings and sends status approval/rejection patches with optional status reasons.
*/

import { apiFetch } from '../../api.js';
import { requireAdmin } from '../../auth.js';
import { formatMoney, formatDateTime, showToast } from '../../helpers.js';

let statusFilter = 'pending';
let rejectingBookingId = null;

document.addEventListener('DOMContentLoaded', async () => {
  requireAdmin();

  document.getElementById('btn-filter-all').addEventListener('click', () => setFilter(''));
  document.getElementById('btn-filter-pending').addEventListener('click', () => setFilter('pending'));
  document.getElementById('btn-filter-approved').addEventListener('click', () => setFilter('approved'));
  document.getElementById('btn-filter-cancelled').addEventListener('click', () => setFilter('cancelled'));

  document.getElementById('btn-cancel-reject').addEventListener('click', closeRejectModal);
  document.getElementById('btn-confirm-reject').addEventListener('click', handleConfirmReject);
  document.getElementById('reject-modal').addEventListener('click', (e) => {
    if (e.target.id === 'reject-modal') closeRejectModal();
  });

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
  tbody.innerHTML = '<tr><td colspan="7" style="padding:2.5rem; text-align:center; color:var(--color-text-muted);">Loading bookings...</td></tr>';

  const endpoint = statusFilter ? `/admin/bookings?status=${statusFilter}` : '/admin/bookings';

  try {
    const data = await apiFetch(endpoint);
    const items = data.items || [];
    renderRows(items);
  } catch (err) {
    tbody.innerHTML = '<tr><td colspan="7" style="padding:2.5rem; text-align:center; color:var(--color-danger);">Failed to load booking records from server.</td></tr>';
  }
}

function renderRows(items) {
  const tbody = document.getElementById('bookings-table-body');
  tbody.innerHTML = '';

  if (items.length === 0) {
    tbody.innerHTML = '<tr><td colspan="7" style="padding:2.5rem; text-align:center; color:var(--color-text-muted);">No booking records found matching filter.</td></tr>';
    return;
  }

  items.forEach(b => {
    const tr = document.createElement('tr');
    tr.style.borderBottom = '1px solid var(--color-border)';

    const isPending = b.status === 'pending';
    const statusPill = `<span class="pill-status pill-${b.status}">${b.status.toUpperCase()}</span>`;

    const customerName = (b.customer && b.customer.full_name) ? b.customer.full_name : (b.customer_name || 'Customer');
    const customerEmail = (b.customer && b.customer.email) ? b.customer.email : '';
    const customerPhone = (b.customer && b.customer.phone) ? b.customer.phone : '';

    const tourTitle = (b.tour && b.tour.title) ? b.tour.title : (b.tour_title || 'Guided Tour');
    const depTime = (b.departure && b.departure.start_datetime) ? b.departure.start_datetime : (b.departure_date || b.created_at);

    const attendanceBadge = b.attendance
      ? `<span class="badge" style="font-size:0.75rem; background:#E2E8F0; margin-top:0.25rem;">Att: ${b.attendance.toUpperCase()}</span>`
      : '';

    const requirementsList = [];
    if (b.pickup_preference) requirementsList.push(`Pickup: ${b.pickup_preference}`);
    if (b.dietary_requirements) requirementsList.push(`Diet: ${b.dietary_requirements}`);
    if (b.accessibility_needs) requirementsList.push(`Access: ${b.accessibility_needs}`);
    const reqHtml = requirementsList.length > 0
      ? `<div style="font-size:0.78rem; color:var(--color-text-muted); margin-top:0.2rem;">${requirementsList.join(' • ')}</div>`
      : '';

    tr.innerHTML = `
      <td style="padding: 1rem 1.25rem; font-family:monospace; font-weight:700;">${b.booking_reference}</td>
      <td style="padding: 1rem 1.25rem;">
        <strong>${customerName}</strong>
        <div style="font-size:0.8rem; color:var(--color-text-muted);">${customerEmail}${customerPhone ? ` • ${customerPhone}` : ''}</div>
      </td>
      <td style="padding: 1rem 1.25rem;">
        <strong>${tourTitle}</strong>
        <div style="font-size:0.8rem; color:var(--color-text-muted);">${formatDateTime(depTime)}</div>
      </td>
      <td style="padding: 1rem 1.25rem;">
        <strong>${b.traveller_count} Pax</strong>
        ${reqHtml}
      </td>
      <td style="padding: 1rem 1.25rem; font-weight:700; color:var(--color-primary);">${formatMoney(b.total_price)}</td>
      <td style="padding: 1rem 1.25rem;">
        ${statusPill}
        ${attendanceBadge}
      </td>
      <td style="padding: 1rem 1.25rem; text-align:right;">
        ${isPending ? `
          <button class="btn btn-primary btn-approve" style="padding:0.3rem 0.65rem; font-size:0.8rem;">Approve</button>
          <button class="btn btn-danger btn-reject" style="padding:0.3rem 0.65rem; font-size:0.8rem;">Reject</button>
        ` : `
          <span style="font-size:0.8rem; color:var(--color-text-muted);">${(b.status || 'Settled').toUpperCase()}</span>
        `}
      </td>
    `;

    const approveBtn = tr.querySelector('.btn-approve');
    const rejectBtn = tr.querySelector('.btn-reject');
    if (approveBtn) approveBtn.addEventListener('click', () => updateStatus(b.id, 'approved'));
    if (rejectBtn) rejectBtn.addEventListener('click', () => openRejectModal(b.id));

    tbody.appendChild(tr);
  });
}

function openRejectModal(bookingId) {
  rejectingBookingId = bookingId;
  document.getElementById('reject-reason').value = '';
  document.getElementById('reject-modal').style.display = 'flex';
}

function closeRejectModal() {
  rejectingBookingId = null;
  document.getElementById('reject-modal').style.display = 'none';
}

async function handleConfirmReject() {
  if (!rejectingBookingId) return;
  const reason = document.getElementById('reject-reason').value.trim();
  const bookingId = rejectingBookingId;
  closeRejectModal();
  await updateStatus(bookingId, 'rejected', reason || undefined);
}

async function updateStatus(id, newStatus, reason = undefined) {
  try {
    const payload = { status: newStatus };
    if (reason) payload.reason = reason;

    await apiFetch(`/admin/bookings/${id}/status`, {
      method: 'PATCH',
      body: payload
    });
    showToast(`Booking marked as ${newStatus}`, 'success');
    loadAdminBookings();
  } catch (err) {
    alert(err.message || `Failed to update booking to ${newStatus}.`);
    loadAdminBookings();
  }
}
