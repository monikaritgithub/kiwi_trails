/* Authentication state management for browser storage.
Stores bearer tokens and user roles, handles logout and route redirects.
*/

const TOKEN_KEY = 'kiwi_trails_token';
const USER_KEY = 'kiwi_trails_user';

export function getAuthToken() {
  return localStorage.getItem(TOKEN_KEY);
}

export function setAuthSession(token, user) {
  localStorage.setItem(TOKEN_KEY, token);
  localStorage.setItem(USER_KEY, JSON.stringify(user));
}

export function getCurrentUser() {
  const data = localStorage.getItem(USER_KEY);
  if (!data) return null;
  try {
    return JSON.parse(data);
  } catch (err) {
    return null;
  }
}

export function getUserRole() {
  const user = getCurrentUser();
  return user ? user.role : null;
}

export function isAuthenticated() {
  return !!getAuthToken();
}

export function clearAuthSession() {
  localStorage.removeItem(TOKEN_KEY);
  localStorage.removeItem(USER_KEY);
}

export function logout() {
  clearAuthSession();
  window.location.href = '/frontend/pages/login.html';
}

export function requireAuth() {
  if (!isAuthenticated()) {
    window.location.href = '/frontend/pages/login.html';
  }
}

export function requireAdmin() {
  if (!isAuthenticated() || getUserRole() !== 'admin') {
    window.location.href = '/frontend/pages/login.html';
  }
}
