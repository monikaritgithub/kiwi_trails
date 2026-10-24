/* Client script for customer booking management.
Fetches /bookings/my, handles detail modal, invoice/calendar downloads, and cancellations.
*/

import { apiFetch } from '../api.js';
import { requireAuth, logout } from '../auth.js';
import { formatMoney, formatDateTime, showToast } from '../helpers.js';
import { downloadInvoice, downloadCalendar } from '../download.js';

let activeBooking = null;

document.addEventListener('DOMContentLoaded', async () => {
  requireAuth();

  const logoutBtn = document.getElementById('btn-nav-logout');
  if (logoutBtn) logoutBtn.addEventListener('click', () => logout());

  document.getElementById('btn-close-modal').addEventListener('click', closeModal);
  document.getElementById('booking-modal').addEventListener('click', (e) => {
    if (e.target.id === 'booking-modal') closeModal();
  });

  document.getElementById('btn-download-invoice').addEventListener('click', () => {
    if (activeBooking) downloadInvoice(activeBooking.id);
  });

  document.getElementById('btn-download-calendar').addEventListener('click', () => {
    if (activeBooking) downloadCalendar(activeBooking.id);
  });

  document.getElementById('btn-cancel-booking').addEventListener('click', handleCancelBooking);

  await loadMyBookings();
});

async function loadMyBookings() {
  const loading = document.getElementById('loading-state');
  const empty = document.getElementById('empty-state');
  const list = document.getElementById('bookings-list');

  loading.style.display = 'block';
  empty.style.display = 'none';
  list.innerHTML = '';

  try {
    const data = await apiFetch('/bookings/my');
    const items = data.items || [];
    loading.style.display = 'none';

    if (items.length === 0) {
      empty.style.display = 'block';
      return;
    }

    items.forEach(booking => {
      list.appendChild(createBookingRow(booking));
    });
  } catch (err) {
    loading.textContent = 'Unable to load booking history.';
  }
}

function createBookingRow(b) {
  const row = document.createElement('div');
  row.className = 'card';
  row.style.padding = '1.25rem 1.5rem';
  row.style.flexDirection = 'row';
  row.style.justifyContent = 'space-between';
  row.style.alignItems = 'center';
  row.style.flexWrap = 'wrap';
  row.style.gap = '1rem';

  const statusClass = `pill-${b.status || 'pending'}`;

  row.innerHTML = `
    <div>
      <div style="display:flex; align-items:center; gap:0.75rem; margin-bottom:0.25rem;">
        <span class="pill-status ${statusClass}">${(b.status || 'Pending').toUpperCase()}</span>
        <span style="font-family:monospace; font-size:0.85rem; color:var(--color-text-muted);">${b.booking_reference}</span>
      </div>
      <h3 style="margin-bottom:0.25rem; font-size:1.15rem;">${b.tour_title || 'New Zealand Tour'}</h3>
      <p style="font-size:0.85rem; color:var(--color-text-muted); margin:0;">
        Departure: <strong>${formatDateTime(b.departure_date || b.created_at)}</strong> &bull; Total: <strong>${formatMoney(b.total_price)}</strong>
      </p>
    </div>
    <div style="display:flex; gap:0.5rem;">
      <button class="btn btn-outline btn-manage" style="padding:0.45rem 0.9rem;">View Details</button>
    </div>
  `;

  row.querySelector('.btn-manage').addEventListener('click', () => openModal(b));
  return row;
}

async function openModal(b) {
  activeBooking = b;
  const modal = document.getElementById('booking-modal');
  modal.style.display = 'flex';

  document.getElementById('modal-tour-title').textContent = b.tour_title || 'Tour Reservation';
  document.getElementById('modal-reference').textContent = b.booking_reference;
  document.getElementById('modal-departure-time').textContent = formatDateTime(b.departure_date || b.created_at);
  document.getElementById('modal-travellers').textContent = `${b.traveller_count || 1} Person(s)`;
  document.getElementById('modal-total-price').textContent = formatMoney(b.total_price);

  const pill = document.getElementById('modal-status-pill');
  pill.className = `pill-status pill-${b.status || 'pending'}`;
  pill.textContent = (b.status || 'Pending').toUpperCase();

  const cancelBtn = document.getElementById('btn-cancel-booking');
  const reviewBtn = document.getElementById('btn-leave-review');

  if (b.status === 'cancelled') {
    cancelBtn.style.display = 'none';
  } else {
    cancelBtn.style.display = 'block';
  }

  if (b.status === 'completed' || b.status === 'approved') {
    reviewBtn.style.display = 'block';
    reviewBtn.onclick = () => {
      window.location.href = `/frontend/pages/review-form.html?booking_id=${b.id}&tour_id=${b.tour_id || 1}`;
    };
  } else {
    reviewBtn.style.display = 'none';
  }
}

function closeModal() {
  document.getElementById('booking-modal').style.display = 'none';
  activeBooking = null;
}

async function handleCancelBooking() {
  if (!activeBooking) return;
  if (!confirm(`Are you sure you want to cancel booking ${activeBooking.booking_reference}?`)) return;

  try {
    await apiFetch(`/bookings/${activeBooking.id}/cancel`, {
      method: 'POST'
    });
    showToast('Booking cancelled successfully.', 'info');
    closeModal();
    loadMyBookings();
  } catch (err) {
    alert(err.message || 'Could not cancel booking.');
  }
}
