/* Client controller for guides and categories management.
Submits new guides and categories to admin endpoints and renders live database tables.
*/

import { apiFetch } from '../../api.js';
import { requireAdmin } from '../../auth.js';
import { showToast } from '../../helpers.js';

document.addEventListener('DOMContentLoaded', async () => {
  requireAdmin();

  document.getElementById('create-guide-form').addEventListener('submit', handleCreateGuide);
  document.getElementById('create-category-form').addEventListener('submit', handleCreateCategory);

  await Promise.all([loadGuidesTable(), loadCategoriesTable()]);
});

async function loadCategoriesTable() {
  const tbody = document.getElementById('categories-table-body');
  tbody.innerHTML = '<tr><td colspan="3" style="padding: 2rem; text-align: center; color: var(--color-text-muted);">Loading categories...</td></tr>';

  try {
    const res = await apiFetch('/categories');
    const items = Array.isArray(res) ? res : (res.items || []);
    document.getElementById('categories-count').textContent = `${items.length} Active`;

    if (items.length === 0) {
      tbody.innerHTML = '<tr><td colspan="3" style="padding: 2rem; text-align: center; color: var(--color-text-muted);">No categories defined yet.</td></tr>';
      return;
    }

    tbody.innerHTML = '';
    items.forEach(c => {
      const tr = document.createElement('tr');
      tr.style.borderBottom = '1px solid var(--color-border)';
      tr.innerHTML = `
        <td style="padding: 1rem 1.25rem; font-family: monospace; color: var(--color-text-muted);">${c.id}</td>
        <td style="padding: 1rem 1.25rem; font-weight: 700; color: var(--color-primary);">${c.name}</td>
        <td style="padding: 1rem 1.25rem; color: var(--color-text);">${c.description || '<em style="color:var(--color-text-muted);">No description provided</em>'}</td>
      `;
      tbody.appendChild(tr);
    });
  } catch (err) {
    tbody.innerHTML = '<tr><td colspan="3" style="padding: 2rem; text-align: center; color: var(--color-text-muted);">Unable to load categories.</td></tr>';
  }
}

async function loadGuidesTable() {
  const tbody = document.getElementById('guides-table-body');
  tbody.innerHTML = '<tr><td colspan="4" style="padding: 2rem; text-align: center; color: var(--color-text-muted);">Loading guides...</td></tr>';

  try {
    const guides = [];
    for (let id = 1; id <= 10; id++) {
      try {
        const g = await apiFetch(`/guides/${id}`);
        if (g && g.id) guides.push(g);
      } catch (e) {}
    }

    document.getElementById('guides-count').textContent = `${guides.length} Certified`;

    if (guides.length === 0) {
      tbody.innerHTML = '<tr><td colspan="4" style="padding: 2rem; text-align: center; color: var(--color-text-muted);">No Kaitiaki guides registered yet.</td></tr>';
      return;
    }

    tbody.innerHTML = '';
    guides.forEach(g => {
      const tr = document.createElement('tr');
      tr.style.borderBottom = '1px solid var(--color-border)';

      const langBadges = (g.languages || []).map(l =>
        `<span style="background: #EBF3ED; color: var(--color-primary); font-size: 0.75rem; font-weight: 600; padding: 0.2rem 0.5rem; border-radius: 999px; margin-right: 0.35rem; display: inline-block;">${l}</span>`
      ).join('');

      const photoHtml = g.photo_url
        ? `<img src="${g.photo_url}" alt="${g.full_name}" style="width: 32px; height: 32px; border-radius: 50%; object-fit: cover;">`
        : `<div style="width: 32px; height: 32px; border-radius: 50%; background: var(--color-border); display: flex; align-items: center; justify-content: center; font-size: 0.8rem; font-weight: 700; color: var(--color-primary);">${g.full_name.charAt(0)}</div>`;

      tr.innerHTML = `
        <td style="padding: 1rem 1.25rem; font-family: monospace; color: var(--color-text-muted);">${g.id}</td>
        <td style="padding: 1rem 1.25rem;">
          <div style="display: flex; align-items: center; gap: 0.75rem;">
            ${photoHtml}
            <span style="font-weight: 700;">${g.full_name}</span>
          </div>
        </td>
        <td style="padding: 1rem 1.25rem;">${langBadges || '<span style="color:var(--color-text-muted);">English</span>'}</td>
        <td style="padding: 1rem 1.25rem; color: var(--color-text); font-size: 0.9rem; max-width: 420px;">${g.bio || '<em style="color:var(--color-text-muted);">No bio recorded</em>'}</td>
      `;
      tbody.appendChild(tr);
    });
  } catch (err) {
    tbody.innerHTML = '<tr><td colspan="4" style="padding: 2rem; text-align: center; color: var(--color-text-muted);">Unable to load guides.</td></tr>';
  }
}

async function handleCreateGuide(e) {
  e.preventDefault();
  const btn = document.getElementById('btn-save-guide');
  btn.disabled = true;

  const full_name = document.getElementById('guide-name').value.trim();
  const bio = document.getElementById('guide-bio').value.trim();
  const photo_url = document.getElementById('guide-photo').value.trim() || null;
  const languagesRaw = document.getElementById('guide-languages').value.trim();
  const languages = languagesRaw.split(',').map(s => s.trim()).filter(Boolean);

  try {
    await apiFetch('/admin/guides', {
      method: 'POST',
      body: { full_name, bio, photo_url, languages }
    });
    showToast(`Kaitiaki guide "${full_name}" registered successfully!`, 'success');
    document.getElementById('create-guide-form').reset();
    await loadGuidesTable();
  } catch (err) {
    alert(err.message || 'Failed to create guide.');
  } finally {
    btn.disabled = false;
  }
}

async function handleCreateCategory(e) {
  e.preventDefault();
  const btn = document.getElementById('btn-save-cat');
  btn.disabled = true;

  const name = document.getElementById('cat-name').value.trim();
  const description = document.getElementById('cat-description').value.trim() || '';

  try {
    await apiFetch('/admin/categories', {
      method: 'POST',
      body: { name, description }
    });
    showToast(`Category "${name}" created successfully!`, 'success');
    document.getElementById('create-category-form').reset();
    await loadCategoriesTable();
  } catch (err) {
    alert(err.message || 'Failed to create category.');
  } finally {
    btn.disabled = false;
  }
}
