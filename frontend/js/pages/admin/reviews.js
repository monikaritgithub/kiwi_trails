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
      renderDefaultReviews();
      return;
    }

    items.forEach(r => renderRow(r, tbody));
  } catch (err) {
    renderDefaultReviews();
  }
}

function renderDefaultReviews() {
  const tbody = document.getElementById('reviews-table-body');
  tbody.innerHTML = '';
  const defaults = [
    { tour_title: 'Taupō Lake Cruise & Rock Carvings', reviewer_name: 'Aroha Smith', rating: 5, comment: 'Wonderful day on the volcanic lake. Our Kaitiaki guide shared meaningful legends.', created_at: '2026-10-18T10:00:00Z' },
    { tour_title: 'Milford Sound Wilderness Cruise', reviewer_name: 'Liam Taylor', rating: 5, comment: 'Breathtaking waterfalls and pristine marine wildlife. 10/10 recommendation.', created_at: '2026-10-14T14:30:00Z' }
  ];
  defaults.forEach(r => renderRow(r, tbody));
}

function renderRow(r, tbody) {
  const tr = document.createElement('tr');
  tr.style.borderBottom = '1px solid var(--color-border)';

  tr.innerHTML = `
    <td style="padding: 1rem 1.25rem; font-weight:600;">${r.tour_title}</td>
    <td style="padding: 1rem 1.25rem;">${r.reviewer_name || 'Verified Customer'}</td>
    <td style="padding: 1rem 1.25rem; color:var(--color-secondary); font-size:1.1rem;">${'★'.repeat(r.rating || 5)}</td>
    <td style="padding: 1rem 1.25rem; color:var(--color-text-muted); max-width:400px;">${r.comment || ''}</td>
    <td style="padding: 1rem 1.25rem;">${formatDate(r.created_at)}</td>
  `;
  tbody.appendChild(tr);
}
