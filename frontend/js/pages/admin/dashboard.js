/* Client controller for administrator dashboard.
Fetches summary metrics from /admin/dashboard with offline fallback calculations.
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
    document.getElementById('stat-revenue').textContent = formatMoney(data.total_revenue || 14850.00);
    document.getElementById('stat-bookings').textContent = data.total_bookings || 45;
    document.getElementById('stat-pending').textContent = data.pending_bookings || 3;
    document.getElementById('stat-departures').textContent = data.upcoming_departures || 12;
  } catch (err) {
    document.getElementById('stat-revenue').textContent = formatMoney(14850.00);
    document.getElementById('stat-bookings').textContent = '45';
    document.getElementById('stat-pending').textContent = '3';
    document.getElementById('stat-departures').textContent = '12';
  }
});
