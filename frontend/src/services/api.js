// services/api.js
// ─────────────────────────────────────────────────────────────────────────
// Centralised Axios service — the ONLY place in the frontend that knows
// the backend URL or how to make HTTP requests.
//
// Why a separate service file?
//   Separation of Concerns: UI components stay clean and testable.
//   If the backend URL or auth token changes, we update ONE file, not every component.
//
// Usage in a component:
//   import { searchProduct } from '../services/api';
//   const data = await searchProduct('iPhone 15 Pro');
// ─────────────────────────────────────────────────────────────────────────

import axios from 'axios';

// ── Axios instance ────────────────────────────────────────────────────────
// baseURL reads from an environment variable so you can change it per
// environment (dev / staging / prod) without touching source code.
// In Vite, env variables must be prefixed with VITE_.
// Create a .env file in the project root:
//   VITE_API_BASE_URL=http://localhost:5000
const apiClient = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || 'http://localhost:5000',
  timeout: 30000,           // 30 s — scraping can be slow
  headers: {
    'Content-Type': 'application/json',
  },
});

// ── Response interceptor: uniform error shape ─────────────────────────────
// Catches Axios errors and re-throws a plain Error with a human-readable
// message so components don't need to inspect err.response.data themselves.
apiClient.interceptors.response.use(
  (response) => response,
  (error) => {
    const message =
      error.response?.data?.message ||
      error.response?.data?.error  ||
      error.message                ||
      'Something went wrong. Please try again.';
    return Promise.reject(new Error(message));
  }
);

// ── Mock data (fallback for local UI development) ─────────────────────────
// Remove or gate this behind an env flag once your backend is ready.
const MOCK_DATA = {
  product: 'iPhone 15 Pro (Demo Data)',
  totalReviews: 120,
  sentimentSummary: {
    positive: { count: 78, percentage: 65 },
    neutral:  { count: 24, percentage: 20 },
    negative: { count: 18, percentage: 15 },
  },
  reviews: [
    { id: 1, text: 'Absolutely love this phone! The camera quality is outstanding and the titanium build feels premium.', sentiment: 'positive', rating: 5, date: '2024-11-10', author: 'Riya S.' },
    { id: 2, text: 'Good phone overall but the price is a bit steep for what you get compared to Android flagships.', sentiment: 'neutral',  rating: 3, date: '2024-10-22', author: 'Arjun M.' },
    { id: 3, text: 'Battery life is disappointing. Expected much better performance at this price point.', sentiment: 'negative', rating: 2, date: '2024-09-15', author: 'Priya K.' },
    { id: 4, text: 'The ProRes video recording is a game changer for content creators. 10/10 would recommend.', sentiment: 'positive', rating: 5, date: '2024-11-01', author: 'Dev R.' },
    { id: 5, text: 'Smooth performance and great display. However, I miss the USB-A compatibility.', sentiment: 'neutral',  rating: 4, date: '2024-10-05', author: 'Sneha P.' },
    { id: 6, text: 'Overheating issue during heavy gaming sessions. Apple needs to address this ASAP.', sentiment: 'negative', rating: 2, date: '2024-08-30', author: 'Karan T.' },
  ],
};

// ── API functions ─────────────────────────────────────────────────────────

/**
 * Search for a product and return sentiment analysis data.
 *
 * @param {string} productName — the search query entered by the user
 * @returns {Promise<object>}  — structured data matching the schema in MOCK_DATA
 *
 * Expected backend endpoint:
 *   GET /api/search?product={productName}
 *
 * Expected response shape from backend:
 * {
 *   product: string,
 *   totalReviews: number,
 *   sentimentSummary: {
 *     positive: { count: number, percentage: number },
 *     neutral:  { count: number, percentage: number },
 *     negative: { count: number, percentage: number },
 *   },
 *   reviews: Array<{
 *     id: string|number,
 *     text: string,
 *     sentiment: "positive" | "neutral" | "negative",
 *     rating?: number,     // 1-5
 *     date?: string,       // ISO 8601
 *     author?: string,
 *   }>
 * }
 */
export async function searchProduct(productName) {
  // ── DEVELOPMENT FALLBACK ──────────────────────────────────────────────
  // Comment out the next 3 lines once your backend is running.
  if (import.meta.env.DEV && !import.meta.env.VITE_API_BASE_URL) {
    console.warn('[api.js] No VITE_API_BASE_URL set — returning mock data.');
    return MOCK_DATA;
  }
  // ─────────────────────────────────────────────────────────────────────

  const response = await apiClient.get('/api/search', {
    params: { product: productName },
  });

  return response.data;
}
