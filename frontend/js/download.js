/* Binary file download handlers for booking documents.
Fetches binary streams and triggers browser file save for PDF invoices and ICS invites.
*/

import { CONFIG } from './config.js';
import { getAuthToken } from './auth.js';

export async function downloadFile(endpoint, filenameFallback) {
  const url = `${CONFIG.API_BASE_URL}${endpoint}`;
  const token = getAuthToken();
  const headers = {};
  if (token) {
    headers['Authorization'] = `Bearer ${token}`;
  }

  const response = await fetch(url, { headers });
  if (!response.ok) {
    throw new Error(`Failed to download file: ${response.statusText}`);
  }

  const blob = await response.blob();
  const blobUrl = window.URL.createObjectURL(blob);
  const anchor = document.createElement('a');
  anchor.href = blobUrl;

  const disposition = response.headers.get('content-disposition');
  let filename = filenameFallback;
  if (disposition && disposition.includes('filename=')) {
    const match = disposition.match(/filename="?([^"]+)"?/);
    if (match && match[1]) filename = match[1];
  }

  anchor.download = filename;
  document.body.appendChild(anchor);
  anchor.click();
  anchor.remove();
  window.URL.revokeObjectURL(blobUrl);
}

export function downloadInvoice(bookingId) {
  return downloadFile(`/bookings/${bookingId}/invoice`, `kiwi-trails-invoice-${bookingId}.pdf`);
}

export function downloadCalendar(bookingId) {
  return downloadFile(`/bookings/${bookingId}/calendar`, `kiwi-trails-departure-${bookingId}.ics`);
}
