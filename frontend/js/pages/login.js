/* Client script for customer and administrator login.
Sends credentials to /auth/login and stores session state.
*/

import { apiFetch } from '../api.js';
import { setAuthSession, isAuthenticated, getUserRole } from '../auth.js';
import { showToast } from '../helpers.js';

document.addEventListener('DOMContentLoaded', () => {
  if (isAuthenticated()) {
    const role = getUserRole();
    window.location.href = role === 'admin' ? '/frontend/pages/admin/dashboard.html' : '/frontend/pages/tour-list.html';
    return;
  }

  const form = document.getElementById('login-form');
  const errorBanner = document.getElementById('error-banner');
  const submitBtn = document.getElementById('btn-submit');

  form.addEventListener('submit', async (e) => {
    e.preventDefault();
    errorBanner.style.display = 'none';
    submitBtn.disabled = true;
    submitBtn.textContent = 'Signing in...';

    const email = document.getElementById('email').value.trim();
    const password = document.getElementById('password').value;

    try {
      const data = await apiFetch('/auth/login', {
        method: 'POST',
        body: { email, password }
      });

      setAuthSession(data.token, data.user);
      showToast('Login successful! Welcome back.', 'success');

      setTimeout(() => {
        if (data.user && data.user.role === 'admin') {
          window.location.href = '/frontend/pages/admin/dashboard.html';
        } else {
          window.location.href = '/frontend/pages/tour-list.html';
        }
      }, 500);
    } catch (err) {
      errorBanner.textContent = err.message || 'Invalid email or password. Please try again.';
      errorBanner.style.display = 'block';
      submitBtn.disabled = false;
      submitBtn.textContent = 'Sign In';
    }
  });
});
