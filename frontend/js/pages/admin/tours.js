/* Client controller for admin tour management.
Queries /admin/tours with status filters and updates tour active/archived state.
*/

import { apiFetch } from '../../api.js';
import { requireAdmin } from '../../auth.js';
import { formatMoney, showToast } from '../../helpers.js';

let activeFilter = '';

document.addEventListener('DOMContentLoaded', async () => {
  requireAdmin();

  document.getElementById('filter-all').addEventListener('click', () => setFilter(''));
  document.getElementById('filter-active').addEventListener('click', () => setFilter('active'));
  document.getElementById('filter-archived').addEventListener('click', () => setFilter('archived'));

  await loadAdminTours();
});

function setFilter(status) {
  activeFilter = status;
  document.querySelectorAll('[id^="filter-"]').forEach(btn => {
    btn.className = 'btn btn-outline';
    btn.style.padding = '0.4rem 0.8rem';
    btn.style.fontSize = '0.85rem';
  });
  const activeBtnId = status ? `filter-${status}` : 'filter-all';
  const activeBtn = document.getElementById(activeBtnId);
  if (activeBtn) activeBtn.className = 'btn btn-primary';
  loadAdminTours();
}

async function loadAdminTours() {
  const loading = document.getElementById('loading-state');
  const tableContainer = document.getElementById('tours-table-container');
  const tbody = document.getElementById('tours-table-body');

  loading.style.display = 'block';
  tableContainer.style.display = 'none';
  tbody.innerHTML = '';

  const endpoint = activeFilter ? `/admin/tours?status=${activeFilter}` : '/admin/tours';

  try {
    const data = await apiFetch(endpoint);
    const items = data.items || [];

    loading.style.display = 'none';
    tableContainer.style.display = 'block';

    items.forEach(tour => {
      tbody.appendChild(createTourTableRow(tour));
    });
  } catch (err) {
    loading.textContent = 'Error loading tour records.';
  }
}

function createTourTableRow(tour) {
  const tr = document.createElement('tr');
  tr.style.borderBottom = '1px solid var(--color-border)';

  const isArchived = tour.status === 'archived';
  const statusBadge = isArchived
    ? '<span class="badge" style="background:#E2E8F0; color:#475569;">Archived</span>'
    : '<span class="badge badge-kaitiaki">Active</span>';

  tr.innerHTML = `
    <td style="padding: 1rem 1.25rem; font-weight:600;">
      <a href="/frontend/pages/tour-detail.html?id=${tour.id}" target="_blank" style="color:var(--color-primary);">${tour.title}</a>
    </td>
    <td style="padding: 1rem 1.25rem; color:var(--color-text-muted);">${tour.category_name || 'Standard'}</td>
    <td style="padding: 1rem 1.25rem; font-weight:700;">${formatMoney(tour.price_per_person)}</td>
    <td style="padding: 1rem 1.25rem;">${tour.duration_days || 1} Day(s)</td>
    <td style="padding: 1rem 1.25rem;">${statusBadge}</td>
    <td style="padding: 1rem 1.25rem; text-align:right;">
      <div style="display:inline-flex; gap:0.4rem;">
        <a href="/frontend/pages/admin/tour-form.html?id=${tour.id}" class="btn btn-outline" style="padding:0.3rem 0.65rem; font-size:0.8rem;">Edit</a>
        <button class="btn btn-outline btn-toggle-status" style="padding:0.3rem 0.65rem; font-size:0.8rem;">
          ${isArchived ? 'Activate' : 'Archive'}
        </button>
      </div>
    </td>
  `;

  tr.querySelector('.btn-toggle-status').addEventListener('click', async () => {
    const newStatus = isArchived ? 'active' : 'archived';
    try {
      await apiFetch(`/admin/tours/${tour.id}/status`, {
        method: 'PATCH',
        body: { status: newStatus }
      });
      showToast(`Tour status updated to ${newStatus}`, 'success');
      loadAdminTours();
    } catch (err) {
      alert(err.message || 'Failed to update tour status');
    }
  });

  return tr;
}
