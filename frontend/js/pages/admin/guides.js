/* Client controller for guides and categories management.
Submits new guides to /admin/guides and new categories to /admin/categories.
*/

import { apiFetch } from '../../api.js';
import { requireAdmin } from '../../auth.js';
import { showToast } from '../../helpers.js';

document.addEventListener('DOMContentLoaded', () => {
  requireAdmin();

  document.getElementById('create-guide-form').addEventListener('submit', handleCreateGuide);
  document.getElementById('create-category-form').addEventListener('submit', handleCreateCategory);
});

async function handleCreateGuide(e) {
  e.preventDefault();
  const btn = document.getElementById('btn-save-guide');
  btn.disabled = true;

  const name = document.getElementById('guide-name').value.trim();
  const bio = document.getElementById('guide-bio').value.trim();
  const languagesRaw = document.getElementById('guide-languages').value.trim();
  const languages = languagesRaw.split(',').map(s => s.trim()).filter(Boolean);

  try {
    await apiFetch('/admin/guides', {
      method: 'POST',
      body: { name, bio, languages }
    });
    showToast(`Guide "${name}" created successfully!`, 'success');
    document.getElementById('create-guide-form').reset();
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
  const description = document.getElementById('cat-description').value.trim();

  try {
    await apiFetch('/admin/categories', {
      method: 'POST',
      body: { name, description }
    });
    showToast(`Category "${name}" created successfully!`, 'success');
    document.getElementById('create-category-form').reset();
  } catch (err) {
    alert(err.message || 'Failed to create category.');
  } finally {
    btn.disabled = false;
  }
}
