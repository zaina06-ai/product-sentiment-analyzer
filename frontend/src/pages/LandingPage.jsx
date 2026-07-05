// pages/LandingPage.jsx
// ─────────────────────────────────────────────────────────────────────────
// The "/" route — the hero landing page with the search bar.
//
// Notice how thin this component is:
//   All stateful logic (query, loading, error, search) lives in useProductSearch.
//   This component is responsible ONLY for rendering UI.
//
// Flow:
//   1. User types in SearchBar → hook's setQuery updates query state
//   2. User clicks Search or presses Enter → hook's search() fires
//   3. While loading → LoadingSpinner replaces the search area
//   4. On success → useNavigate sends user to /dashboard
//   5. On error   → error message appears below the SearchBar
// ─────────────────────────────────────────────────────────────────────────

import React from 'react';
import SearchBar     from '../components/SearchBar';
import LoadingSpinner from '../components/LoadingSpinner';
import useProductSearch from '../hooks/useProductSearch';

function LandingPage() {
  const { query, setQuery, loading, error, search } = useProductSearch();

  return (
    <div style={{
      minHeight: '85vh',
      display: 'flex',
      flexDirection: 'column',
      alignItems: 'center',
      justifyContent: 'center',
      padding: '4rem 2rem',
      width: '100%',
      boxSizing: 'border-box',
    }}>

      {/* ── Hero section ── */}
      <div style={{
        textAlign: 'center',
        marginBottom: '2.5rem',
        display: 'flex',
        flexDirection: 'column',
        alignItems: 'center',
        width: '100%',
      }} className="animate-fade-in-up">
        {/* Headline */}
        <h1
          className="league-gothic"
          style={{
            color: 'var(--text-primary)',
            fontSize: 'clamp(4rem, 8vw, 8rem)',
            lineHeight: 1.05,
            marginBottom: '1rem',
            letterSpacing: '-0.01em',
            whiteSpace: 'nowrap',
          }}
        >
          Understand What Customers Feel
        </h1>

        <p style={{ color: 'var(--text-muted)', fontSize: '1.1rem', maxWidth: '520px', textAlign: 'center', marginTop: '0.5rem' }}>
          Search any product on Amazon and Flipkart and get the sentiment analysis in real time.
        </p>
      </div>

      {/* ── Search area ── */}
      <div style={{ width: '100%', maxWidth: '640px' }} className="animate-fade-in-up">
        {loading ? (
          <LoadingSpinner message="Scraping reviews & running sentiment analysis… this may take 15–30 seconds." />
        ) : (
          <>
            <SearchBar
              value={query}
              onChange={setQuery}
              onSearch={search}
              loading={loading}
            />

            {/* Error message */}
            {error && (
              <div
                style={{ backgroundColor: '#fef2f2', color: '#ef4444', border: '1px solid #fca5a5', marginTop: '1rem', padding: '0.75rem 1rem', borderRadius: '0.75rem', fontSize: '0.875rem', display: 'flex', gap: '0.5rem', alignItems: 'flex-start' }}
                role="alert"
              >
                <span style={{ fontWeight: 600 }}>Error:</span>
                {error}
              </div>
            )}
          </>
        )}
      </div>
    </div>
  );
}

export default LandingPage;
