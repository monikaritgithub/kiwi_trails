/* Client script for customer account registration.
Validates inputs and submits registration payload to /auth/register.
*/

import { apiFetch } from '../api.js';
import { showToast } from '../helpers.js';

document.addEventListener('DOMContentLoaded', () => {
  const form = document.getElementById('register-form');
  const errorBanner = document.getElementById('error-banner');
  const successBanner = document.getElementById('success-banner');
  const submitBtn = document.getElementById('btn-submit');

  form.addEventListener('submit', async (e) => {
    e.preventDefault();
    errorBanner.style.display = 'none';
    successBanner.style.display = 'none';

    const full_name = document.getElementById('full_name').value.trim();
    const email = document.getElementById('email').value.trim();
    const phone = document.getElementById('phone').value.trim();
    const password = document.getElementById('password').value;

    if (password.length < 8) {
      errorBanner.textContent = 'Password must be at least 8 characters in length.';
      errorBanner.style.display = 'block';
      return;
    }

    submitBtn.disabled = true;
    submitBtn.textContent = 'Creating account...';

    try {
      await apiFetch('/auth/register', {
        method: 'POST',
        body: {
          full_name,
          email,
          password,
          phone: phone || undefined
        }
      });

      successBanner.textContent = 'Account created successfully! Redirecting to sign in...';
      successBanner.style.display = 'block';
      showToast('Registration successful!', 'success');

      setTimeout(() => {
        window.location.href = '/frontend/pages/login.html';
      }, 1200);
    } catch (err) {
      errorBanner.textContent = err.message || 'Registration failed. Email may already be in use.';
      errorBanner.style.display = 'block';
      submitBtn.disabled = false;
      submitBtn.textContent = 'Create Account';
    }
  });
});
