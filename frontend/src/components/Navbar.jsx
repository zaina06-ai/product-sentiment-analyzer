// components/Navbar.jsx
// ─────────────────────────────────────────────────────────────────────────
// Persistent top navigation bar rendered on every page (see App.jsx).
//
// Key design decisions:
//  • sticky + backdrop-blur → glassmorphism effect; page content scrolls under it.
//  • Clicking the logo navigates to "/" using React Router's useNavigate.
//  • No props needed — this is a pure layout/branding component.
// ─────────────────────────────────────────────────────────────────────────

import React from 'react';
import { useNavigate } from 'react-router-dom';

function Navbar() {
  const navigate = useNavigate();

  return (
    <header
      className="sticky top-0 z-50 w-full border-b"
      style={{
        backgroundColor: 'rgba(255,255,255,0.8)',
        backdropFilter: 'blur(12px)',
        borderColor: '#e5e7eb',
      }}
    >
      <div style={{
        width: '100%',
        padding: '0.85rem 2.5rem',
        display: 'flex',
        alignItems: 'center',
        boxSizing: 'border-box',
      }}>

        {/* ── Logo / Brand ── */}
        <button
          id="navbar-logo-btn"
          onClick={() => navigate('/')}
          style={{ background: 'none', border: 'none', cursor: 'pointer', padding: 0 }}
          aria-label="Go to home"
        >
          <span style={{ fontSize: '1.25rem', fontWeight: 700, letterSpacing: '-0.02em', color: 'var(--text-primary)' }}>
            Senti<span style={{ color: 'var(--accent-glow)' }}>Scrap</span>
          </span>
        </button>

      </div>
    </header>
  );
}

export default Navbar;
