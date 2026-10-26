/* Client controller for customer review moderation.
Fetches customer reviews from /admin/reviews and populates moderation table.
*/

import { apiFetch } from '../../api.js';
import { requireAdmin } from '../../auth.js';
import { formatDate } from '../../helpers.js';

document.addEventListener('DOMContentLoaded', async () => {
  requireAdmin();
  await loadReviews();
});

async function loadReviews() {
  const tbody = document.getElementById('reviews-table-body');
  tbody.innerHTML = '';

  try {
    const data = await apiFetch('/admin/reviews');
    const items = data.items || [];

    if (items.length === 0) {
      renderEmptyReviews('No customer reviews submitted yet.');
      return;
    }

    items.forEach(r => renderRow(r, tbody));
  } catch (err) {
    renderEmptyReviews('No customer reviews submitted yet or unable to load reviews.');
  }
}

function renderEmptyReviews(message) {
  const tbody = document.getElementById('reviews-table-body');
  tbody.innerHTML = `<tr><td colspan="5" style="padding: 2.5rem; text-align: center; color: var(--color-text-muted);">${message}</td></tr>`;
}

function renderRow(r, tbody) {
  const tr = document.createElement('tr');
  tr.style.borderBottom = '1px solid var(--color-border)';

  const starCount = Math.max(1, Math.min(5, Math.round(Number(r.rating) || 5)));

  tr.innerHTML = `
    <td style="padding: 1rem 1.25rem; font-weight:600;">${r.tour_title || 'Tour'}</td>
    <td style="padding: 1rem 1.25rem;">${r.reviewer_name || 'Verified Customer'}</td>
    <td style="padding: 1rem 1.25rem; color:var(--color-secondary); font-size:1.1rem;">${'★'.repeat(starCount)}</td>
    <td style="padding: 1rem 1.25rem; color:var(--color-text-muted); max-width:400px;">${r.comment || ''}</td>
    <td style="padding: 1rem 1.25rem;">${formatDate(r.created_at)}</td>
  `;
  tbody.appendChild(tr);
}
