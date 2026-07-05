// components/SearchBar.jsx
// ─────────────────────────────────────────────────────────────────────────
// Controlled search input component.
//
// Why "controlled"?
//   The parent page (LandingPage) owns the query state via useState.
//   SearchBar receives { value, onChange, onSearch, loading } as props.
//   This keeps the component dumb/reusable — it only handles UI, not state.
//
// Props:
//   value    {string}   — current input value (controlled)
//   onChange {function} — called on every keystroke → updates parent state
//   onSearch {function} — called when user submits (button click or Enter)
//   loading  {boolean}  — disables input+button while API call is in flight
// ─────────────────────────────────────────────────────────────────────────

import React from 'react';

function SearchBar({ value, onChange, onSearch, loading }) {

  // Allow submitting by pressing Enter inside the input field
  const handleKeyDown = (e) => {
    if (e.key === 'Enter' && !loading) {
      onSearch();
    }
  };

  return (
    <div className="flex w-full max-w-2xl mx-auto gap-3">

      {/* ── Text input ── */}
      <div className="relative flex-1">
        <input
          id="product-search-input"
          type="text"
          placeholder="Search for a product (e.g. iPhone 15 Pro)…"
          value={value}
          onChange={(e) => onChange(e.target.value)}
          onKeyDown={handleKeyDown}
          disabled={loading}
          className="w-full rounded-xl text-sm font-medium outline-none transition-all duration-200 disabled:opacity-50"
          style={{
            backgroundColor: 'var(--bg-card)',
            color: 'var(--text-primary)',
            border: '1px solid #d1d5db',
            padding: '1rem 1.25rem',
          }}
          onFocus={(e)  => (e.target.style.borderColor = 'var(--accent)')}
          onBlur={(e)   => (e.target.style.borderColor = '#d1d5db')}
          aria-label="Product search"
        />
      </div>

      {/* ── Search button ── */}
      <button
        id="product-search-btn"
        onClick={onSearch}
        disabled={loading || value.trim() === ''}
        className="px-6 py-4 rounded-xl font-semibold text-sm text-white transition-all duration-200 disabled:opacity-50 disabled:cursor-not-allowed"
        style={{
          backgroundColor: loading ? '#9ca3af' : 'var(--accent)',
          minWidth: '110px',
        }}
        onMouseEnter={(e) => { if (!loading) e.currentTarget.style.opacity = '0.88'; }}
        onMouseLeave={(e) => { e.currentTarget.style.opacity = '1'; }}
      >
        {loading ? 'Searching…' : 'Search'}
      </button>
    </div>
  );
}

export default SearchBar;
