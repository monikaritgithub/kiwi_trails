/* Client controller for creating and editing tours and FAQs.
Submits tour updates to /admin/tours and manages FAQ creation.
*/

import { apiFetch } from '../../api.js';
import { requireAdmin } from '../../auth.js';
import { showToast } from '../../helpers.js';

let editingTourId = null;

document.addEventListener('DOMContentLoaded', async () => {
  requireAdmin();

  const urlParams = new URLSearchParams(window.location.search);
  editingTourId = urlParams.get('id');

  await loadCategories();

  if (editingTourId) {
    document.getElementById('page-heading').textContent = `Edit Tour #${editingTourId}`;
    await loadTourData(editingTourId);
  }

  document.getElementById('tour-form').addEventListener('submit', handleSaveTour);
  document.getElementById('faq-form').addEventListener('submit', handleAddFaq);
});

async function loadCategories() {
  try {
    const categories = await apiFetch('/categories');
    const select = document.getElementById('tour-category');
    const list = Array.isArray(categories) ? categories : (categories.items || []);
    list.forEach(c => {
      const opt = document.createElement('option');
      opt.value = c.id;
      opt.textContent = c.name;
      select.appendChild(opt);
    });
  } catch (err) {}
}

async function loadTourData(id) {
  try {
    const tour = await apiFetch(`/tours/${id}`);
    document.getElementById('tour-title').value = tour.title || '';
    document.getElementById('tour-category').value = tour.category_id || 1;
    document.getElementById('tour-price').value = tour.price_per_person || '';
    document.getElementById('tour-duration').value = tour.duration_days || 1;
    document.getElementById('tour-summary').value = tour.summary || '';
    document.getElementById('tour-description').value = tour.description || '';

    renderFaqs(tour.faqs || []);
  } catch (err) {
    showToast('Could not load tour details.', 'danger');
  }
}

function renderFaqs(faqs) {
  const container = document.getElementById('faq-list');
  container.innerHTML = '';
  faqs.forEach(f => {
    const item = document.createElement('div');
    item.style.padding = '0.75rem';
    item.style.border = '1px solid var(--color-border)';
    item.style.borderRadius = 'var(--radius-sm)';
    item.style.fontSize = '0.85rem';
    item.innerHTML = `
      <strong>Q: ${f.question}</strong>
      <p style="margin:0.25rem 0 0; color:var(--color-text-muted);">${f.answer}</p>
    `;
    container.appendChild(item);
  });
}

async function handleSaveTour(e) {
  e.preventDefault();
  const btn = document.getElementById('btn-save-tour');
  btn.disabled = true;
  btn.textContent = 'Saving...';

  const payload = {
    title: document.getElementById('tour-title').value.trim(),
    category_id: parseInt(document.getElementById('tour-category').value),
    price_per_person: parseFloat(document.getElementById('tour-price').value),
    duration_days: parseInt(document.getElementById('tour-duration').value),
    summary: document.getElementById('tour-summary').value.trim(),
    description: document.getElementById('tour-description').value.trim()
  };

  try {
    if (editingTourId) {
      await apiFetch(`/admin/tours/${editingTourId}`, {
        method: 'PUT',
        body: payload
      });
      showToast('Tour updated successfully!', 'success');
    } else {
      await apiFetch('/admin/tours', {
        method: 'POST',
        body: payload
      });
      showToast('New tour created!', 'success');
      setTimeout(() => {
        window.location.href = '/frontend/pages/admin/tours.html';
      }, 1000);
    }
  } catch (err) {
    alert(err.message || 'Failed to save tour.');
  } finally {
    btn.disabled = false;
    btn.textContent = 'Save Tour Details';
  }
}

async function handleAddFaq(e) {
  e.preventDefault();
  const tourId = editingTourId || 1;
  const question = document.getElementById('faq-question').value.trim();
  const answer = document.getElementById('faq-answer').value.trim();

  try {
    await apiFetch(`/admin/tours/${tourId}/faqs`, {
      method: 'POST',
      body: { question, answer, sort_order: 1 }
    });
    showToast('FAQ added!', 'success');
    document.getElementById('faq-question').value = '';
    document.getElementById('faq-answer').value = '';
    if (editingTourId) loadTourData(editingTourId);
  } catch (err) {
    alert(err.message || 'Failed to add FAQ.');
  }
}
