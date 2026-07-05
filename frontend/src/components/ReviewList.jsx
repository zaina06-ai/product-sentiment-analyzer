// components/ReviewList.jsx
// ─────────────────────────────────────────────────────────────────────────
// Renders the complete list of review cards with a sentiment filter bar.
//
// Why useMemo here?
//   Filtering a potentially large array on every render would be wasteful.
//   useMemo caches the filtered result and only recalculates when `reviews`
//   or `activeFilter` changes.
//
// Props:
//   reviews {Array} — array of review objects from the API
//     Each item shape: { text, sentiment, rating?, date?, author? }
// ─────────────────────────────────────────────────────────────────────────

import React, { useState, useMemo } from 'react';
import ReviewCard from './ReviewCard';

const FILTERS = ['All', 'Positive', 'Neutral', 'Negative'];

function ReviewList({ reviews = [] }) {
  const [activeFilter, setActiveFilter] = useState('All');

  // Memoised filtered list — recalculates only when deps change
  const filteredReviews = useMemo(() => {
    if (activeFilter === 'All') return reviews;
    return reviews.filter(
      (r) => r.sentiment?.toLowerCase() === activeFilter.toLowerCase()
    );
  }, [reviews, activeFilter]);

  return (
    <section id="reviews-section" className="flex flex-col gap-6 mt-8 animate-fade-in-up" style={{ animationDelay: '400ms' }}>

      {/* ── Section header ── */}
      <div className="flex items-center justify-between flex-wrap gap-4">
        <div>
          <h2 className="text-xl font-bold" style={{ color: 'var(--text-primary)' }}>
            Customer Reviews
          </h2>
          <p className="text-sm mt-0.5" style={{ color: 'var(--text-muted)' }}>
            {filteredReviews.length} of {reviews.length} reviews shown
          </p>
        </div>

        {/* ── Filter pills ── */}
        <div className="flex gap-2 flex-wrap">
          {FILTERS.map((filter) => (
            <button
              key={filter}
              id={`filter-btn-${filter.toLowerCase()}`}
              onClick={() => setActiveFilter(filter)}
              className="px-4 py-1.5 rounded-full text-sm font-medium transition-all duration-200"
              style={{
                backgroundColor: activeFilter === filter ? 'var(--accent)' : 'var(--bg-card)',
                color: activeFilter === filter ? '#fff' : 'var(--text-muted)',
                border: `1px solid ${activeFilter === filter ? 'var(--accent)' : '#e5e7eb'}`,
              }}
            >
              {filter}
            </button>
          ))}
        </div>
      </div>

      {/* ── Review grid ── */}
      {filteredReviews.length > 0 ? (
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
          {filteredReviews.map((review, index) => (
            <ReviewCard key={review.id ?? index} review={review} />
          ))}
        </div>
      ) : (
        <div
          className="rounded-2xl p-10 text-center"
          style={{ backgroundColor: 'var(--bg-card)', border: '1px solid #e5e7eb' }}
        >
          <p className="font-semibold" style={{ color: 'var(--text-primary)' }}>
            No {activeFilter !== 'All' ? activeFilter.toLowerCase() : ''} reviews found
          </p>
          <p className="text-sm mt-1" style={{ color: 'var(--text-muted)' }}>
            Try selecting a different filter
          </p>
        </div>
      )}
    </section>
  );
}

export default ReviewList;
