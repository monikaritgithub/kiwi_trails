/* Client controller for creating and editing tours, gallery images, and FAQs.
Submits tour updates to /admin/tours and handles multi-asset uploads.
*/

import { apiFetch } from '../../api.js';
import { requireAdmin } from '../../auth.js';
import { showToast } from '../../helpers.js';

let editingTourId = null;

document.addEventListener('DOMContentLoaded', async () => {
  requireAdmin();

  const urlParams = new URLSearchParams(window.location.search);
  editingTourId = urlParams.get('id');

  await Promise.all([loadCategories(), loadGuides()]);

  if (editingTourId) {
    document.getElementById('page-heading').textContent = `Edit Tour #${editingTourId}`;
    document.getElementById('image-upload-form').style.display = 'block';
    document.getElementById('image-upload-notice').style.display = 'none';
    await loadTourData(editingTourId);
  }

  document.getElementById('tour-form').addEventListener('submit', handleSaveTour);
  document.getElementById('image-upload-form').addEventListener('submit', handleUploadImage);
  document.getElementById('faq-form').addEventListener('submit', handleAddFaq);
});

async function loadCategories() {
  try {
    const res = await apiFetch('/categories');
    const select = document.getElementById('tour-category');
    select.innerHTML = '';
    const list = Array.isArray(res) ? res : (res.items || []);
    list.forEach(c => {
      const opt = document.createElement('option');
      opt.value = c.id;
      opt.textContent = c.name;
      select.appendChild(opt);
    });
  } catch (err) {}
}

async function loadGuides() {
  const select = document.getElementById('tour-guide');
  const existingOptions = select.innerHTML;
  try {
    const guides = [];
    for (let id = 1; id <= 6; id++) {
      try {
        const g = await apiFetch(`/guides/${id}`);
        if (g && g.id) guides.push(g);
      } catch (e) {}
    }
    guides.forEach(g => {
      const opt = document.createElement('option');
      opt.value = g.id;
      opt.textContent = `${g.full_name} (${(g.languages || []).join(', ') || 'Guide'})`;
      select.appendChild(opt);
    });
  } catch (err) {}
}

async function loadTourData(id) {
  try {
    const tour = await apiFetch(`/tours/${id}`);
    document.getElementById('tour-title').value = tour.title || '';
    if (tour.category_id) {
      document.getElementById('tour-category').value = tour.category_id;
    }
    document.getElementById('tour-location').value = tour.location || '';
    document.getElementById('tour-price').value = tour.price_per_person || '';
    document.getElementById('tour-duration').value = tour.duration_days || 1;
    document.getElementById('tour-cancellation').value = tour.cancellation_days !== undefined ? tour.cancellation_days : 7;

    const guideId = tour.guide ? tour.guide.id : (tour.guide_id || '');
    if (guideId) {
      document.getElementById('tour-guide').value = String(guideId);
    }

    document.getElementById('tour-description').value = tour.description || '';
    document.getElementById('tour-itinerary').value = tour.itinerary || '';

    if (tour.meeting_point) {
      document.getElementById('meeting-point-name').value = tour.meeting_point.name || '';
      document.getElementById('meeting-lat').value = tour.meeting_point.lat !== undefined ? tour.meeting_point.lat : '';
      document.getElementById('meeting-lng').value = tour.meeting_point.lng !== undefined ? tour.meeting_point.lng : '';
    } else {
      document.getElementById('meeting-point-name').value = tour.meeting_point_name || '';
      document.getElementById('meeting-lat').value = tour.meeting_lat !== undefined ? tour.meeting_lat : '';
      document.getElementById('meeting-lng').value = tour.meeting_lng !== undefined ? tour.meeting_lng : '';
    }

    document.getElementById('accessibility-info').value = tour.accessibility_info || '';
    document.getElementById('visitor-guidelines').value = tour.visitor_guidelines || '';

    renderImagesPreview(tour.images || []);
    renderFaqs(tour.faqs || []);
  } catch (err) {
    showToast('Could not load tour details.', 'danger');
  }
}

function renderImagesPreview(images) {
  const container = document.getElementById('tour-images-preview');
  container.innerHTML = '';
  if (!images || images.length === 0) {
    container.innerHTML = '<p style="grid-column: 1 / -1; color: var(--color-text-muted); font-size: 0.85rem;">No gallery photos uploaded yet.</p>';
    return;
  }

  images.forEach(img => {
    const card = document.createElement('div');
    card.style.border = '1px solid var(--color-border)';
    card.style.borderRadius = 'var(--radius-sm)';
    card.style.overflow = 'hidden';
    card.style.position = 'relative';

    card.innerHTML = `
      <img src="${img.image_url}" alt="${img.alt_text || 'Tour preview'}" style="width: 100%; height: 85px; object-fit: cover; display: block;">
      <div style="padding: 0.4rem; font-size: 0.75rem; display: flex; justify-content: space-between; align-items: center; background: #fff;">
        <span style="color: var(--color-text-muted);">#${img.sort_order || 0}</span>
        <button class="btn-delete-img" style="background: none; border: none; color: var(--color-error, #b91c1c); cursor: pointer; font-size: 0.75rem; font-weight: 700;">Delete</button>
      </div>
    `;

    card.querySelector('.btn-delete-img').addEventListener('click', async () => {
      if (!confirm('Delete this gallery photo?')) return;
      try {
        await apiFetch(`/admin/tour-images/${img.id}`, { method: 'DELETE' });
        showToast('Image deleted.', 'success');
        await loadTourData(editingTourId);
      } catch (e) {
        showToast(e.message || 'Failed to delete image.', 'danger');
      }
    });

    container.appendChild(card);
  });
}

function renderFaqs(faqs) {
  const container = document.getElementById('faq-list');
  container.innerHTML = '';
  if (!faqs || faqs.length === 0) {
    container.innerHTML = '<p style="color: var(--color-text-muted); font-size: 0.85rem;">No FAQs currently added for this tour.</p>';
    return;
  }

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

  const guideVal = document.getElementById('tour-guide').value;
  const latVal = document.getElementById('meeting-lat').value.trim();
  const lngVal = document.getElementById('meeting-lng').value.trim();
  const cancelVal = document.getElementById('tour-cancellation').value.trim();

  const payload = {
    title: document.getElementById('tour-title').value.trim(),
    category_id: parseInt(document.getElementById('tour-category').value, 10),
    location: document.getElementById('tour-location').value.trim(),
    price_per_person: parseFloat(document.getElementById('tour-price').value),
    duration_days: parseInt(document.getElementById('tour-duration').value, 10),
    description: document.getElementById('tour-description').value.trim(),
    itinerary: document.getElementById('tour-itinerary').value.trim(),
    cancellation_days: cancelVal ? parseInt(cancelVal, 10) : 7,
    guide_id: guideVal ? parseInt(guideVal, 10) : null,
    meeting_point_name: document.getElementById('meeting-point-name').value.trim() || null,
    meeting_lat: latVal ? parseFloat(latVal) : null,
    meeting_lng: lngVal ? parseFloat(lngVal) : null,
    accessibility_info: document.getElementById('accessibility-info').value.trim() || null,
    visitor_guidelines: document.getElementById('visitor-guidelines').value.trim() || null
  };

  try {
    if (editingTourId) {
      await apiFetch(`/admin/tours/${editingTourId}`, {
        method: 'PUT',
        body: payload
      });
      showToast('Tour updated successfully!', 'success');
      await loadTourData(editingTourId);
    } else {
      const created = await apiFetch('/admin/tours', {
        method: 'POST',
        body: payload
      });
      showToast('New tour created successfully!', 'success');
      const newId = created.id || created.pk;
      if (newId) {
        setTimeout(() => {
          window.location.href = `/frontend/pages/admin/tour-form.html?id=${newId}`;
        }, 800);
      } else {
        setTimeout(() => {
          window.location.href = '/frontend/pages/admin/tours.html';
        }, 800);
      }
    }
  } catch (err) {
    alert(err.message || 'Failed to save tour.');
  } finally {
    btn.disabled = false;
    btn.textContent = 'Save Tour Details';
  }
}

async function handleUploadImage(e) {
  e.preventDefault();
  if (!editingTourId) return;

  const fileInput = document.getElementById('tour-image-file');
  if (!fileInput.files || fileInput.files.length === 0) {
    showToast('Please select an image file to upload.', 'danger');
    return;
  }

  const btn = document.getElementById('btn-upload-image');
  btn.disabled = true;
  btn.textContent = 'Uploading...';

  const formData = new FormData();
  formData.append('image', fileInput.files[0]);
  formData.append('alt_text', document.getElementById('tour-image-alt').value.trim());
  formData.append('sort_order', document.getElementById('tour-image-order').value.trim() || '1');

  try {
    await apiFetch(`/admin/tours/${editingTourId}/images`, {
      method: 'POST',
      body: formData
    });
    showToast('Image uploaded successfully!', 'success');
    document.getElementById('image-upload-form').reset();
    await loadTourData(editingTourId);
  } catch (err) {
    alert(err.message || 'Failed to upload image.');
  } finally {
    btn.disabled = false;
    btn.textContent = 'Upload Gallery Image';
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
    showToast('FAQ added successfully!', 'success');
    document.getElementById('faq-question').value = '';
    document.getElementById('faq-answer').value = '';
    if (editingTourId) await loadTourData(editingTourId);
  } catch (err) {
    alert(err.message || 'Failed to add FAQ.');
  }
}
