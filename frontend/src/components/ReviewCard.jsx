// components/ReviewCard.jsx
// ─────────────────────────────────────────────────────────────────────────
// Renders a single customer review with sentiment badge, star rating, and date.
//
// Design decisions:
//  • Badge color is looked up from a config object (SENTIMENT_CONFIG) instead
//    of if/else chains — easier to extend if a new sentiment type is added.
//  • Rating and date use optional chaining / conditional rendering:
//    they appear ONLY if the backend provides them, avoiding undefined errors.
//  • Long reviews are clamped to 4 lines with CSS line-clamp.
//
// Props:
//   review   {object}  — a single review object from the API:
//     .text      {string}  — review body text
//     .sentiment {string}  — "positive" | "neutral" | "negative"
//     .rating    {number?} — star rating 1–5 (optional)
//     .date      {string?} — ISO date string (optional)
//     .author    {string?} — reviewer name (optional)
// ─────────────────────────────────────────────────────────────────────────

import React from 'react';

const SENTIMENT_CONFIG = {
  positive: {
    label: 'Positive',
    color: '#111827',
    bg:    '#f3f4f6',
  },
  neutral: {
    label: 'Neutral',
    color: '#4b5563',
    bg:    '#f3f4f6',
  },
  negative: {
    label: 'Negative',
    color: '#9ca3af',
    bg:    '#f3f4f6',
  },
};

// Renders filled/empty stars
function StarRating({ rating }) {
  return (
    <div className="flex gap-0.5" aria-label={`Rating: ${rating} out of 5`}>
      {[1, 2, 3, 4, 5].map((star) => (
        <svg
          key={star}
          className="w-4 h-4"
          fill={star <= rating ? '#4b5563' : 'none'}
          stroke="#4b5563"
          strokeWidth="1.5"
          viewBox="0 0 24 24"
          aria-hidden="true"
        >
          <polygon points="12 2 15.09 8.26 22 9.27 17 14.14 18.18 21.02 12 17.77 5.82 21.02 7 14.14 2 9.27 8.91 8.26 12 2" />
        </svg>
      ))}
    </div>
  );
}

function ReviewCard({ review }) {
  const sentiment = review.sentiment?.toLowerCase() ?? 'neutral';
  const config = SENTIMENT_CONFIG[sentiment] ?? SENTIMENT_CONFIG.neutral;

  // Format ISO date → "Jun 28, 2025"
  const formattedDate = review.date
    ? new Date(review.date).toLocaleDateString('en-US', {
        year: 'numeric', month: 'short', day: 'numeric',
      })
    : null;

  return (
    <article
      className="rounded-2xl p-5 flex flex-col gap-3 animate-fade-in-up transition-transform duration-200 hover:-translate-y-0.5"
      style={{
        backgroundColor: 'var(--bg-card-2)',
        border: '1px solid #e5e7eb',
        boxShadow: '0 2px 12px rgba(0,0,0,0.05)',
      }}
    >
      {/* ── Top row: badge + rating ── */}
      <div className="flex items-center justify-between flex-wrap gap-2">
        {/* Sentiment badge */}
        <span
          className="inline-flex items-center px-3 py-1 rounded-full text-xs font-semibold"
          style={{ color: config.color, backgroundColor: config.bg }}
        >
          {config.label}
        </span>

        {/* Star rating — only if API provides it */}
        {review.rating != null && <StarRating rating={review.rating} />}
      </div>

      {/* ── Review text — clamped to 4 lines ── */}
      <p
        className="text-sm leading-relaxed"
        style={{
          color: 'var(--text-primary)',
          display: '-webkit-box',
          WebkitLineClamp: 4,
          WebkitBoxOrient: 'vertical',
          overflow: 'hidden',
        }}
      >
        {review.text || 'No review text available.'}
      </p>

      {/* ── Footer: author + date ── */}
      <div className="flex items-center justify-between mt-auto pt-2" style={{ borderTop: '1px solid #e5e7eb' }}>
        <span className="text-xs font-medium" style={{ color: 'var(--text-muted)' }}>
          {review.author ?? 'Anonymous'}
        </span>

        {formattedDate && (
          <span className="text-xs" style={{ color: 'var(--text-muted)' }}>
            {formattedDate}
          </span>
        )}
      </div>
    </article>
  );
}

export default ReviewCard;
