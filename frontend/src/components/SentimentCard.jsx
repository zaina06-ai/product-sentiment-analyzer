// components/SentimentCard.jsx
// ─────────────────────────────────────────────────────────────────────────
// KPI statistics card — renders one sentiment metric (Positive / Neutral /
// Negative) with a percentage value and icon.
//
// Props:
//   title   {string}  — label, e.g. "Positive Reviews"
//   value   {string}  — display value, e.g. "72%"
//   color   {string}  — CSS color for the accent bar and icon background
//   icon    {string}  — emoji or symbol displayed in the icon badge
//   count   {number}  — optional raw count shown below percentage
//   delay   {number}  — animation stagger delay in ms (default 0)
// ─────────────────────────────────────────────────────────────────────────

import React from 'react';

function SentimentCard({ title, value, color, icon, count, delay = 0 }) {
  return (
    <div
      className="relative overflow-hidden rounded-2xl flex flex-col gap-3 animate-fade-in-up"
      style={{
        backgroundColor: 'var(--bg-card)',
        border: '1px solid #e5e7eb',
        animationDelay: `${delay}ms`,
        boxShadow: '0 4px 12px rgba(0,0,0,0.05)',
        padding: '1.5rem 1.5rem 1.5rem 1.75rem',
      }}
    >



      {/* ── Header row ── */}
      <div className="flex items-center justify-between">
        <p className="text-sm font-medium" style={{ color: 'var(--text-muted)' }}>
          {title}
        </p>
      </div>

      {/* ── Value ── */}
      <p className="text-4xl font-bold tracking-tight" style={{ color: 'var(--text-primary)' }}>
        {value}
      </p>

      {/* ── Optional raw count ── */}
      {count !== undefined && (
        <p className="text-xs" style={{ color: 'var(--text-muted)' }}>
          {count.toLocaleString()} reviews
        </p>
      )}

      {/* Background glow blob */}
      <div
        className="absolute -bottom-6 -right-6 w-24 h-24 rounded-full blur-2xl opacity-10"
        style={{ backgroundColor: 'var(--text-muted)' }}
        aria-hidden="true"
      />
    </div>
  );
}

export default SentimentCard;
