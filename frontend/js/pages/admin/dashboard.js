/* Client controller for administrator dashboard.
Fetches summary analytics from /admin/dashboard and displays dynamic operational metrics.
*/

import { apiFetch } from '../../api.js';
import { requireAdmin, logout } from '../../auth.js';
import { formatMoney } from '../../helpers.js';

document.addEventListener('DOMContentLoaded', async () => {
  requireAdmin();

  const logoutBtn = document.getElementById('btn-admin-logout');
  if (logoutBtn) logoutBtn.addEventListener('click', () => logout());

  try {
    const data = await apiFetch('/admin/dashboard');

    const rawRevenue = data.total_value !== undefined && data.total_value !== null ? data.total_value : (data.total_revenue !== undefined ? data.total_revenue : 0);
    const revenue = Number(rawRevenue) || 0;

    let totalBookings = 0;
    let pendingBookings = 0;
    if (data.bookings_by_status && typeof data.bookings_by_status === 'object') {
      totalBookings = Object.values(data.bookings_by_status).reduce((acc, count) => acc + (Number(count) || 0), 0);
      pendingBookings = Number(data.bookings_by_status.pending) || 0;
    } else {
      totalBookings = data.total_bookings !== undefined ? Number(data.total_bookings) : 0;
      pendingBookings = data.pending_bookings !== undefined ? Number(data.pending_bookings) : 0;
    }

    const departures = data.upcoming_departures !== undefined && data.upcoming_departures !== null ? Number(data.upcoming_departures) : 0;

    document.getElementById('stat-revenue').textContent = formatMoney(revenue);
    document.getElementById('stat-bookings').textContent = String(totalBookings);
    document.getElementById('stat-pending').textContent = String(pendingBookings);
    document.getElementById('stat-departures').textContent = String(departures);
  } catch (err) {
    document.getElementById('stat-revenue').textContent = formatMoney(0);
    document.getElementById('stat-bookings').textContent = '0';
    document.getElementById('stat-pending').textContent = '0';
    document.getElementById('stat-departures').textContent = '0';
  }
});
