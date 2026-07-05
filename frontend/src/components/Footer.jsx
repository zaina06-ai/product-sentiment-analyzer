// components/Footer.jsx
// ─────────────────────────────────────────────────────────────────────────
// Simple persistent footer rendered on every page (via App.jsx).
// No props — pure presentational component.
// ─────────────────────────────────────────────────────────────────────────

import React from 'react';

function Footer() {
  const year = new Date().getFullYear();

  return (
    <footer
      className="w-full py-5 px-6 mt-auto"
      style={{
        backgroundColor: 'var(--bg-card)',
        borderTop: '1px solid #e5e7eb',
      }}
    >
      <div className="max-w-7xl mx-auto flex flex-col sm:flex-row items-center justify-between gap-2">

        <p className="text-xs" style={{ color: 'var(--text-muted)' }}>
          © {year} <span style={{ color: 'var(--accent-glow)' }}>SentiScrap</span> — Product Sentiment Analyzer
        </p>

        <p className="text-xs" style={{ color: 'var(--text-muted)' }}>
          Built with React · Chart.js · TextBlob · VADER
        </p>
      </div>
    </footer>
  );
}

export default Footer;
