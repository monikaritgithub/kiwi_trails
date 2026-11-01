/* Utility helper functions for New Zealand formatting.
Formats currency into NZD, dates into Pacific/Auckland time, shows status banners, and provides crisp SVG icons.
*/

export function formatMoney(amount) {
  const num = parseFloat(amount) || 0;
  return `NZ$${num.toFixed(2)}`;
}

export function formatDate(dateString) {
  if (!dateString) return '';
  const date = new Date(dateString);
  return date.toLocaleDateString('en-NZ', {
    day: 'numeric',
    month: 'short',
    year: 'numeric'
  });
}

export function formatDateTime(dateString) {
  if (!dateString) return '';
  const date = new Date(dateString);
  return date.toLocaleString('en-NZ', {
    day: 'numeric',
    month: 'short',
    year: 'numeric',
    hour: '2-digit',
    minute: '2-digit'
  });
}

export function showToast(message, type = 'info') {
  let toastContainer = document.getElementById('toast-container');
  if (!toastContainer) {
    toastContainer = document.createElement('div');
    toastContainer.id = 'toast-container';
    toastContainer.className = 'toast-container';
    document.body.appendChild(toastContainer);
  }

  const toast = document.createElement('div');
  toast.className = `toast toast-${type}`;
  toast.textContent = message;
  toastContainer.appendChild(toast);

  setTimeout(() => {
    toast.classList.add('fade-out');
    setTimeout(() => toast.remove(), 400);
  }, 3500);
}

export function getIcon(name, extraClass = '') {
  const icons = {
    leaf: `<svg class="icon icon-stroke ${extraClass}" viewBox="0 0 24 24"><path d="M11 20A7 7 0 0 1 4 13a7 7 0 0 1 7-7c2.5 0 4.8 1.3 6.1 3.3.4.6.9 1 1.6 1.1 2 .4 3.3 2.1 3.3 4.1a4.5 4.5 0 0 1-4.5 4.5c-1.3 0-2.5-.5-3.5-1.4M11 20v-9"/></svg>`,
    star: `<svg class="icon ${extraClass}" viewBox="0 0 24 24"><polygon points="12 2 15.09 8.26 22 9.27 17 14.14 18.18 21.02 12 17.77 5.82 21.02 7 14.14 2 9.27 8.91 8.26 12 2"/></svg>`,
    pin: `<svg class="icon icon-stroke ${extraClass}" viewBox="0 0 24 24"><path d="M21 10c0 7-9 13-9 13s-9-6-9-13a9 9 0 0 1 18 0z"/><circle cx="12" cy="10" r="3"/></svg>`,
    calendar: `<svg class="icon icon-stroke ${extraClass}" viewBox="0 0 24 24"><rect x="3" y="4" width="18" height="18" rx="2" ry="2"/><line x1="16" y1="2" x2="16" y2="6"/><line x1="8" y1="2" x2="8" y2="6"/><line x1="3" y1="10" x2="21" y2="10"/></svg>`,
    document: `<svg class="icon icon-stroke ${extraClass}" viewBox="0 0 24 24"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/><polyline points="14 2 14 8 20 8"/><line x1="16" y1="13" x2="8" y2="13"/><line x1="16" y1="17" x2="8" y2="17"/></svg>`,
    verified: `<svg class="icon icon-stroke ${extraClass}" viewBox="0 0 24 24"><path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/><polyline points="9 12 11 14 15 10"/></svg>`,
    accessibility: `<svg class="icon icon-stroke ${extraClass}" viewBox="0 0 24 24"><circle cx="12" cy="4" r="2"/><path d="M5 9h14M12 9v10M8 19l4-4 4 4"/></svg>`,
    users: `<svg class="icon icon-stroke ${extraClass}" viewBox="0 0 24 24"><path d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2"/><circle cx="9" cy="7" r="4"/><path d="M23 21v-2a4 4 0 0 0-3-3.87"/><path d="M16 3.13a4 4 0 0 1 0 7.75"/></svg>`,
    sun: `<svg class="icon icon-stroke ${extraClass}" viewBox="0 0 24 24"><circle cx="12" cy="12" r="5"/><line x1="12" y1="1" x2="12" y2="3"/><line x1="12" y1="21" x2="12" y2="23"/><line x1="4.22" y1="4.22" x2="5.64" y2="5.64"/><line x1="18.36" y1="18.36" x2="19.78" y2="19.78"/><line x1="1" y1="12" x2="3" y2="12"/><line x1="21" y1="12" x2="23" y2="12"/><line x1="4.22" y1="19.78" x2="5.64" y2="18.36"/><line x1="18.36" y1="5.64" x2="19.78" y2="4.22"/></svg>`,
    spark: `<svg class="icon icon-stroke ${extraClass}" viewBox="0 0 24 24"><polygon points="12 2 15 9 22 12 15 15 12 22 9 15 2 12 9 9 12 2"/></svg>`,
    printer: `<svg class="icon icon-stroke ${extraClass}" viewBox="0 0 24 24"><polyline points="6 9 6 2 18 2 18 9"/><path d="M6 18H4a2 2 0 0 1-2-2v-5a2 2 0 0 1 2-2h16a2 2 0 0 1 2 2v5a2 2 0 0 1-2 2h-2"/><rect x="6" y="14" width="12" height="8"/></svg>`,
    compass: `<svg class="icon icon-stroke ${extraClass}" viewBox="0 0 24 24"><circle cx="12" cy="12" r="10"/><polygon points="16.24 7.76 14.12 14.12 7.76 16.24 9.88 9.88 16.24 7.76"/></svg>`,
    tag: `<svg class="icon icon-stroke ${extraClass}" viewBox="0 0 24 24"><path d="M20.59 13.41l-7.17 7.17a2 2 0 0 1-2.83 0L2 12V2h10l8.59 8.59a2 2 0 0 1 0 2.82z"/><line x1="7" y1="7" x2="7.01" y2="7"/></svg>`,
    mountain: `<svg class="icon icon-stroke ${extraClass}" viewBox="0 0 24 24"><path d="m8 3 4 8 5-5 5 15H2L8 3z"/></svg>`,
    check: `<svg class="icon icon-stroke ${extraClass}" viewBox="0 0 24 24"><polyline points="20 6 9 17 4 12"/></svg>`
  };
  return icons[name] || '';
}
