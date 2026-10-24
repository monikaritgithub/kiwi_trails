/* Client script for customer profile management.
Fetches user details and submits profile updates to /users/me.
*/

import { apiFetch } from '../api.js';
import { requireAuth, getCurrentUser, setAuthSession, logout, getAuthToken } from '../auth.js';
import { showToast } from '../helpers.js';

document.addEventListener('DOMContentLoaded', async () => {
  requireAuth();

  const form = document.getElementById('profile-form');
  const errorBanner = document.getElementById('error-banner');
  const successBanner = document.getElementById('success-banner');
  const submitBtn = document.getElementById('btn-submit');
  const logoutBtn = document.getElementById('btn-logout');

  if (logoutBtn) {
    logoutBtn.addEventListener('click', () => logout());
  }

  const cachedUser = getCurrentUser();
  if (cachedUser) {
    populateFields(cachedUser);
  }

  try {
    const user = await apiFetch('/users/me');
    populateFields(user);
    setAuthSession(getAuthToken(), user);
  } catch (err) {
    if (!cachedUser) {
      errorBanner.textContent = 'Failed to load profile details.';
      errorBanner.style.display = 'block';
    }
  }

  function populateFields(user) {
    document.getElementById('email').value = user.email || '';
    document.getElementById('full_name').value = user.full_name || '';
    document.getElementById('phone').value = user.phone || '';
    const roleBadge = document.getElementById('role-badge');
    if (roleBadge) {
      roleBadge.textContent = user.role === 'admin' ? 'Administrator' : 'Customer';
    }
  }

  form.addEventListener('submit', async (e) => {
    e.preventDefault();
    errorBanner.style.display = 'none';
    successBanner.style.display = 'none';

    const full_name = document.getElementById('full_name').value.trim();
    const phone = document.getElementById('phone').value.trim();

    submitBtn.disabled = true;
    submitBtn.textContent = 'Saving changes...';

    try {
      const updated = await apiFetch('/users/me', {
        method: 'PUT',
        body: { full_name, phone }
      });

      populateFields(updated);
      setAuthSession(getAuthToken(), updated);

      successBanner.textContent = 'Profile updated successfully!';
      successBanner.style.display = 'block';
      showToast('Profile updated!', 'success');
    } catch (err) {
      errorBanner.textContent = err.message || 'Failed to update profile.';
      errorBanner.style.display = 'block';
    } finally {
      submitBtn.disabled = false;
      submitBtn.textContent = 'Save Changes';
    }
  });
});
