/* Client controller for discount voucher administration.
Fetches coupon catalog from /admin/coupons and submits new voucher definitions.
*/

import { apiFetch } from '../../api.js';
import { requireAdmin } from '../../auth.js';
import { formatDate, showToast } from '../../helpers.js';

document.addEventListener('DOMContentLoaded', async () => {
  requireAdmin();

  await loadCoupons();

  document.getElementById('create-coupon-form').addEventListener('submit', handleCreateCoupon);
});

async function loadCoupons() {
  const tbody = document.getElementById('coupons-table-body');
  tbody.innerHTML = '';

  try {
    const data = await apiFetch('/admin/coupons');
    const items = data.items || [];

    if (items.length === 0) {
      renderEmptyCoupons('No promotional coupons found. Create your first coupon using the form above.');
      return;
    }

    items.forEach(c => renderRow(c, tbody));
  } catch (err) {
    renderEmptyCoupons('No promotional coupons found or unable to load vouchers.');
  }
}

function renderEmptyCoupons(message) {
  const tbody = document.getElementById('coupons-table-body');
  tbody.innerHTML = `<tr><td colspan="5" style="padding: 2.5rem; text-align: center; color: var(--color-text-muted);">${message}</td></tr>`;
}

function renderRow(c, tbody) {
  const tr = document.createElement('tr');
  tr.style.borderBottom = '1px solid var(--color-border)';

  const discountText = c.discount_type === 'percent'
    ? `${parseFloat(c.discount_value)}% Off`
    : `NZ$${parseFloat(c.discount_value).toFixed(2)} Off`;

  const statusPill = c.is_active
    ? '<span class="pill-status pill-approved">Active</span>'
    : '<span class="pill-status pill-cancelled">Expired</span>';

  tr.innerHTML = `
    <td style="padding: 1rem 1.25rem; font-family:monospace; font-weight:700; color:var(--color-primary);">${c.code}</td>
    <td style="padding: 1rem 1.25rem; font-weight:600;">${discountText}</td>
    <td style="padding: 1rem 1.25rem;">${c.uses_count || 0} / ${c.max_uses || '∞'}</td>
    <td style="padding: 1rem 1.25rem;">${formatDate(c.expires_at)}</td>
    <td style="padding: 1rem 1.25rem;">${statusPill}</td>
  `;
  tbody.appendChild(tr);
}

async function handleCreateCoupon(e) {
  e.preventDefault();
  const btn = document.getElementById('btn-create-coupon');
  btn.disabled = true;
  btn.textContent = 'Creating...';

  const code = document.getElementById('coupon-code').value.trim().toUpperCase();
  const discount_type = document.getElementById('discount-type').value;
  const discount_value = parseFloat(document.getElementById('discount-value').value);
  const max_uses = parseInt(document.getElementById('max-uses').value) || 100;
  const expires_at = new Date(document.getElementById('expires-at').value).toISOString();

  try {
    await apiFetch('/admin/coupons', {
      method: 'POST',
      body: { code, discount_type, discount_value, max_uses, expires_at }
    });
    showToast(`Voucher ${code} created successfully!`, 'success');
    document.getElementById('create-coupon-form').reset();
    await loadCoupons();
  } catch (err) {
    alert(err.message || 'Failed to create coupon.');
  } finally {
    btn.disabled = false;
    btn.textContent = 'Create Promo Voucher';
  }
}
