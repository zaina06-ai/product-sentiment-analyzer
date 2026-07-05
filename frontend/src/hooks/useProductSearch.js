// hooks/useProductSearch.js
// ─────────────────────────────────────────────────────────────────────────
// Custom hook that manages the product search lifecycle.
//
// Why a custom hook?
//   It keeps stateful logic (loading, error, data) out of UI components.
//   LandingPage becomes a thin shell that just renders UI; all logic lives here.
//   If we later add caching or debouncing, we do it in ONE place.
//
// Returns:
//   {
//     query   : string         — current input value
//     setQuery: function       — update input value
//     loading : boolean        — true while API call is in flight
//     error   : string|null    — error message or null
//     search  : async function — triggers the API call and navigation
//   }
// ─────────────────────────────────────────────────────────────────────────

import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { searchProduct } from '../services/api';

function useProductSearch() {
  const navigate = useNavigate();

  const [query,   setQuery]   = useState('');
  const [loading, setLoading] = useState(false);
  const [error,   setError]   = useState(null);

  /**
   * Triggers a search for the current `query` value.
   * On success  → navigates to /dashboard, passing API data via route state.
   * On failure  → sets the error message so LandingPage can display it.
   */
  const search = async () => {
    // Guard: don't search if input is empty
    const trimmed = query.trim();
    if (!trimmed) return;

    setLoading(true);
    setError(null);

    try {
      const data = await searchProduct(trimmed);

      // Navigate to dashboard and pass data as router state.
      // This avoids prop-drilling across unrelated components.
      // DashboardPage retrieves it with: const { state } = useLocation()
      navigate('/dashboard', { state: { data, query: trimmed } });

    } catch (err) {
      // err.message is already normalised by the Axios interceptor in api.js
      setError(err.message || 'Product not found. Please try a different search.');
    } finally {
      setLoading(false);
    }
  };

  return { query, setQuery, loading, error, search };
}

export default useProductSearch;
