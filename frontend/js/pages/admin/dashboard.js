/* Client controller for administrator operations dashboard.
Fetches summary analytics from /admin/dashboard, renders booking pipeline, and enables 1-click triage table.
*/

import { apiFetch } from '../../api.js';
import { requireAdmin, logout } from '../../auth.js';
import { formatMoney, formatDateTime, showToast, getIcon } from '../../helpers.js';

let pendingRejectionId = null;

document.addEventListener('DOMContentLoaded', async () => {
  requireAdmin();

  const logoutBtn = document.getElementById('btn-admin-logout');
  if (logoutBtn) logoutBtn.addEventListener('click', () => logout());

  setupClock();
  setupRejectModal();

  await loadDashboardData();
  await loadTriageTable();
  await loadMaoriVerificationStatus();
});

function setupClock() {
  const clockEl = document.getElementById('nz-time-clock');
  if (!clockEl) return;

  function update() {
    const now = new Date();
    try {
      const options = {
        timeZone: 'Pacific/Auckland',
        year: 'numeric',
        month: 'short',
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit',
        second: '2-digit',
        hour12: false
      };
      const formatted = new Intl.DateTimeFormat('en-NZ', options).format(now);
      clockEl.textContent = `Auckland Time: ${formatted} NZDT`;
    } catch (e) {
      clockEl.textContent = `Local Time: ${now.toLocaleTimeString()}`;
    }
  }

  update();
  setInterval(update, 1000);
}

function setupRejectModal() {
  const modal = document.getElementById('dashboard-reject-modal');
  const cancelBtn = document.getElementById('dashboard-reject-cancel');
  const confirmBtn = document.getElementById('dashboard-reject-confirm');
  const reasonInput = document.getElementById('dashboard-reject-reason');

  if (!modal || !confirmBtn || !cancelBtn) return;

  cancelBtn.addEventListener('click', () => {
    modal.style.display = 'none';
    pendingRejectionId = null;
    reasonInput.value = '';
  });

  confirmBtn.addEventListener('click', async () => {
    if (!pendingRejectionId) return;
    const reason = reasonInput.value.trim() || undefined;
    confirmBtn.disabled = true;
    confirmBtn.textContent = 'Declining...';

    try {
      await apiFetch(`/admin/bookings/${pendingRejectionId}/status`, {
        method: 'PATCH',
        body: { status: 'rejected', reason }
      });
      showToast('Reservation declined successfully', 'success');
      modal.style.display = 'none';
      pendingRejectionId = null;
      reasonInput.value = '';
      await loadDashboardData();
      await loadTriageTable();
    } catch (err) {
      alert(err.message || 'Failed to decline reservation.');
    } finally {
      confirmBtn.disabled = false;
      confirmBtn.textContent = 'Confirm Decline';
    }
  });
}

async function loadDashboardData() {
  try {
    const data = await apiFetch('/admin/dashboard');

    const rawRevenue = data.total_value !== undefined && data.total_value !== null ? data.total_value : (data.total_revenue !== undefined ? data.total_revenue : 0);
    const revenue = Number(rawRevenue) || 0;

    let totalBookings = 0;
    let pendingBookings = 0;
    let approvedBookings = 0;
    let completedBookings = 0;
    let cancelledBookings = 0;
    let rejectedBookings = 0;

    if (data.bookings_by_status && typeof data.bookings_by_status === 'object') {
      const stats = data.bookings_by_status;
      pendingBookings = Number(stats.pending) || 0;
      approvedBookings = Number(stats.approved) || 0;
      completedBookings = Number(stats.completed) || 0;
      cancelledBookings = Number(stats.cancelled) || 0;
      rejectedBookings = Number(stats.rejected) || 0;
      totalBookings = Object.values(stats).reduce((acc, count) => acc + (Number(count) || 0), 0);
    } else {
      totalBookings = data.total_bookings !== undefined ? Number(data.total_bookings) : 0;
      pendingBookings = data.pending_bookings !== undefined ? Number(data.pending_bookings) : 0;
    }

    const departures = data.upcoming_departures !== undefined && data.upcoming_departures !== null ? Number(data.upcoming_departures) : 0;

    document.getElementById('stat-revenue').textContent = formatMoney(revenue);
    document.getElementById('stat-bookings').textContent = String(totalBookings);
    document.getElementById('stat-pending').textContent = String(pendingBookings);
    document.getElementById('stat-departures').textContent = String(departures);

    renderPipeline(totalBookings, {
      pending: pendingBookings,
      approved: approvedBookings,
      completed: completedBookings,
      cancelled: cancelledBookings,
      rejected: rejectedBookings
    });
  } catch (err) {
    document.getElementById('stat-revenue').textContent = formatMoney(0);
    document.getElementById('stat-bookings').textContent = '0';
    document.getElementById('stat-pending').textContent = '0';
    document.getElementById('stat-departures').textContent = '0';
  }
}

function renderPipeline(total, counts) {
  const totalLabel = document.getElementById('pipeline-total-label');
  if (totalLabel) totalLabel.textContent = `${total} Total Recorded Bookings`;

  const bar = document.getElementById('pipeline-bar');
  if (!bar) return;

  const segPending = bar.querySelector('.pipeline-segment-pending');
  const segApproved = bar.querySelector('.pipeline-segment-approved');
  const segCompleted = bar.querySelector('.pipeline-segment-completed');
  const segCancelled = bar.querySelector('.pipeline-segment-cancelled');
  const segRejected = bar.querySelector('.pipeline-segment-rejected');

  if (total === 0) {
    if (segPending) segPending.style.width = '0%';
    if (segApproved) segApproved.style.width = '0%';
    if (segCompleted) segCompleted.style.width = '0%';
    if (segCancelled) segCancelled.style.width = '0%';
    if (segRejected) segRejected.style.width = '0%';
    return;
  }

  const pPending = ((counts.pending / total) * 100).toFixed(1);
  const pApproved = ((counts.approved / total) * 100).toFixed(1);
  const pCompleted = ((counts.completed / total) * 100).toFixed(1);
  const pCancelled = ((counts.cancelled / total) * 100).toFixed(1);
  const pRejected = ((counts.rejected / total) * 100).toFixed(1);

  if (segPending) segPending.style.width = `${pPending}%`;
  if (segApproved) segApproved.style.width = `${pApproved}%`;
  if (segCompleted) segCompleted.style.width = `${pCompleted}%`;
  if (segCancelled) segCancelled.style.width = `${pCancelled}%`;
  if (segRejected) segRejected.style.width = `${pRejected}%`;

  const elPending = document.getElementById('legend-pending');
  const elApproved = document.getElementById('legend-approved');
  const elCompleted = document.getElementById('legend-completed');
  const elCancelled = document.getElementById('legend-cancelled');
  const elRejected = document.getElementById('legend-rejected');

  if (elPending) elPending.textContent = `${counts.pending} (${pPending}%)`;
  if (elApproved) elApproved.textContent = `${counts.approved} (${pApproved}%)`;
  if (elCompleted) elCompleted.textContent = `${counts.completed} (${pCompleted}%)`;
  if (elCancelled) elCancelled.textContent = `${counts.cancelled} (${pCancelled}%)`;
  if (elRejected) elRejected.textContent = `${counts.rejected} (${pRejected}%)`;
}

async function loadTriageTable() {
  const tbody = document.getElementById('triage-table-body');
  if (!tbody) return;

  try {
    const data = await apiFetch('/admin/bookings?status=pending&page_size=6');
    const items = data.items || [];

    if (items.length === 0) {
      tbody.innerHTML = `
        <tr>
          <td colspan="7" style="padding: 2.25rem 1rem; text-align: center; color: var(--color-text-muted);">
            <div style="display:inline-flex; align-items:center; gap:0.5rem; color:var(--color-primary); font-weight:600; font-size:1rem; margin-bottom:0.25rem;">
              <svg class="icon icon-stroke" viewBox="0 0 24 24"><path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/><polyline points="9 12 11 14 15 10"/></svg>
              All Caught Up
            </div>
            <p style="margin:0; font-size:0.875rem;">Zero pending bookings require triage at this moment.</p>
          </td>
        </tr>
      `;
      return;
    }

    tbody.innerHTML = '';
    items.forEach(b => {
      const tr = document.createElement('tr');
      const ref = b.booking_reference || `#BK-${b.id}`;
      const customerName = (b.customer && b.customer.full_name) ? b.customer.full_name : (b.customer_name || 'Guest');
      const customerEmail = (b.customer && b.customer.email) ? b.customer.email : '';
      const tourTitle = (b.tour && b.tour.title) ? b.tour.title : (b.tour_title || 'Guided Expedition');
      const depTime = (b.departure && b.departure.start_datetime) ? formatDateTime(b.departure.start_datetime) : 'Scheduled Date';
      const guests = b.traveller_count || 1;
      const amount = formatMoney(b.total_price || 0);

      tr.innerHTML = `
        <td style="font-family:monospace; font-weight:700; color:var(--color-primary);">${ref}</td>
        <td>
          <strong style="display:block; font-size:0.9rem;">${customerName}</strong>
          <span style="font-size:0.75rem; color:var(--color-text-muted);">${customerEmail}</span>
        </td>
        <td style="font-weight:600; font-size:0.875rem;">${tourTitle}</td>
        <td style="font-size:0.85rem; color:var(--color-text);">${depTime}</td>
        <td style="font-size:0.85rem; font-weight:600; text-align:center;">${guests}</td>
        <td style="font-size:0.9rem; font-weight:700; color:var(--color-primary);">${amount}</td>
        <td style="text-align:right;">
          <div style="display:inline-flex; gap:0.4rem; justify-content:flex-end;">
            <button class="action-btn-sm action-btn-approve" data-id="${b.id}">
              <svg class="icon icon-stroke" viewBox="0 0 24 24"><polyline points="20 6 9 17 4 12"/></svg> Approve
            </button>
            <button class="action-btn-sm action-btn-reject" data-id="${b.id}">
              <svg class="icon icon-stroke" viewBox="0 0 24 24"><line x1="18" y1="6" x2="6" y2="18"/><line x1="6" y1="6" x2="18" y2="18"/></svg> Decline
            </button>
          </div>
        </td>
      `;

      const approveBtn = tr.querySelector('.action-btn-approve');
      const rejectBtn = tr.querySelector('.action-btn-reject');

      approveBtn.addEventListener('click', async () => {
        approveBtn.disabled = true;
        approveBtn.textContent = 'Approving...';
        try {
          await apiFetch(`/admin/bookings/${b.id}/status`, {
            method: 'PATCH',
            body: { status: 'approved' }
          });
          showToast(`Reservation ${ref} approved`, 'success');
          await loadDashboardData();
          await loadTriageTable();
        } catch (err) {
          alert(err.message || 'Failed to approve booking.');
          approveBtn.disabled = false;
          approveBtn.textContent = 'Approve';
        }
      });

      rejectBtn.addEventListener('click', () => {
        pendingRejectionId = b.id;
        const modal = document.getElementById('dashboard-reject-modal');
        if (modal) modal.style.display = 'flex';
      });

      tbody.appendChild(tr);
    });
  } catch (err) {
    tbody.innerHTML = `
      <tr>
        <td colspan="7" style="padding: 1.5rem; text-align: center; color: var(--color-danger);">
          Unable to synchronize pending reservations from backend.
        </td>
      </tr>
    `;
  }
}

async function loadMaoriVerificationStatus() {
  const statusEl = document.getElementById('maori-verification-status');
  if (!statusEl) return;

  try {
    const data = await apiFetch('/tours?page_size=50');
    const items = data.items || [];
    const verifiedCount = items.filter(t => t.maori_led).length;
    statusEl.textContent = `${verifiedCount} active verified Maori led expeditions endorsed by regional Iwi.`;
  } catch (err) {
    statusEl.textContent = 'Verified Maori operator network active.';
  }
}
