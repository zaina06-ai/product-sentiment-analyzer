// components/LoadingSpinner.jsx
// ─────────────────────────────────────────────────────────────────────────
// Reusable full-page or inline loading indicator.
//
// Props:
//   message {string}  — optional text shown below the spinner
//                        defaults to "Scraping reviews & analyzing sentiment…"
//
// The spinner is pure CSS (no GIF/image), driven by the @keyframes spin
// defined in index.css (animate-spin-slow class).
// ─────────────────────────────────────────────────────────────────────────

import React from 'react';

function LoadingSpinner({ message = 'Scraping reviews & analyzing sentiment…' }) {
  return (
    <div
      id="loading-spinner-container"
      className="flex flex-col items-center justify-center gap-5 py-20 animate-fade-in-up"
      role="status"
      aria-live="polite"
    >
      {/* Outer ring */}
      <div className="relative w-16 h-16">
        <div
          className="absolute inset-0 rounded-full animate-spin-slow"
          style={{
            border: '3px solid transparent',
            borderTopColor: 'var(--accent)',
            borderRightColor: 'var(--accent-glow)',
          }}
        />
        {/* Inner glow dot */}
        <div
          className="absolute inset-3 rounded-full"
          style={{ background: 'radial-gradient(circle, #6366f1 0%, transparent 70%)' }}
        />
      </div>

      {/* Message */}
      <p className="text-sm font-medium text-center max-w-xs" style={{ color: 'var(--text-muted)' }}>
        {message}
      </p>

      {/* Animated dots */}
      <div className="flex gap-1.5">
        {[0, 150, 300].map((delay) => (
          <span
            key={delay}
            className="w-2 h-2 rounded-full"
            style={{
              backgroundColor: 'var(--accent)',
              animation: `pulse 1.2s ease-in-out ${delay}ms infinite`,
            }}
          />
        ))}
      </div>

      <style>{`
        @keyframes pulse {
          0%, 80%, 100% { transform: scale(0.6); opacity: 0.4; }
          40%            { transform: scale(1);   opacity: 1; }
        }
      `}</style>
    </div>
  );
}

export default LoadingSpinner;
