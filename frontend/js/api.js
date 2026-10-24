/* Core API client wrapper for HTTP network calls.
Handles bearer authentication headers, envelope unwrapping, and mock toggling.
*/

import { CONFIG } from './config.js';
import { getAuthToken } from './auth.js';

export async function apiFetch(endpoint, options = {}) {
  if (CONFIG.USE_MOCK) {
    return handleMockRequest(endpoint, options);
  }

  const url = `${CONFIG.API_BASE_URL}${endpoint}`;
  const headers = {
    'Accept': 'application/json',
    ...(options.headers || {})
  };

  const token = getAuthToken();
  if (token) {
    headers['Authorization'] = `Bearer ${token}`;
  }

  if (options.body && typeof options.body === 'object' && !(options.body instanceof FormData)) {
    headers['Content-Type'] = 'application/json';
    options.body = JSON.stringify(options.body);
  }

  const response = await fetch(url, {
    ...options,
    headers
  });

  const contentType = response.headers.get('content-type') || '';
  if (!contentType.includes('application/json')) {
    if (!response.ok) {
      throw new Error(`Request failed with status ${response.status}`);
    }
    return response;
  }

  const payload = await response.json();

  if (!response.ok || payload.success === false) {
    const errorMsg = (payload.error && payload.error.message) || `HTTP error ${response.status}`;
    const err = new Error(errorMsg);
    err.status = response.status;
    err.payload = payload.error || payload;
    throw err;
  }

  return payload.data !== undefined ? payload.data : payload;
}

async function handleMockRequest(endpoint, options) {
  let mockFile = 'tours.json';
  if (endpoint.includes('/auth/')) mockFile = 'auth.json';
  else if (endpoint.includes('/bookings')) mockFile = 'bookings.json';
  else if (endpoint.includes('/departures')) mockFile = 'departures.json';
  else if (endpoint.includes('/coupons')) mockFile = 'coupons.json';

  const res = await fetch(`/frontend/js/mock/${mockFile}`);
  const data = await res.json();
  return data;
}
