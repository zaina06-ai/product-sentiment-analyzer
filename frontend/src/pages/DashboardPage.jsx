// pages/DashboardPage.jsx
// ─────────────────────────────────────────────────────────────────────────
// The "/dashboard" route — displays all sentiment analysis results.
//
// Data flow:
//   LandingPage → useProductSearch (hook) → navigate('/dashboard', { state: { data } })
//   DashboardPage → useLocation().state → destructure and render
//
// Why route state instead of global state (Redux/Context)?
//   This is a college project with a simple linear flow: search → view results.
//   Route state is the lightest-weight solution — no boilerplate, no extra deps.
//   If the project grows to need persistent state, adding Context is trivial.
//
// Guard:
//   If someone opens /dashboard directly (no state), we redirect to "/" so
//   they aren't shown a broken empty dashboard.
// ─────────────────────────────────────────────────────────────────────────

import React, { useEffect } from 'react';
import { useLocation, useNavigate } from 'react-router-dom';

import SentimentCard  from '../components/SentimentCard';
import PieChart       from '../components/PieChart';
import BarChart       from '../components/BarChart';
import ReviewList     from '../components/ReviewList';

function DashboardPage() {
  const location = useLocation();
  const navigate  = useNavigate();

  // Data passed via router state from useProductSearch hook
  const routeState = location.state;



  // Guard: redirect to home if no data available
  useEffect(() => {
    if (!routeState?.data) {
      navigate('/', { replace: true });
    }
  }, [routeState, navigate]);

  if (!routeState?.data) return null;   // prevent flash before redirect

  const { data, query: searchedQuery } = routeState;
  const { positive, neutral, negative } = data.sentimentSummary;

  return (
    <div style={{
      maxWidth: '1100px',
      width: '100%',
      margin: '0 auto',
      padding: '3rem 2rem 3rem',
      boxSizing: 'border-box',
      display: 'flex',
      flexDirection: 'column',
      gap: '2.5rem',
    }}>

      {/* ── Page header ── */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 animate-fade-in-up">
        <div>
          <p className="text-xs font-semibold uppercase tracking-widest mb-1" style={{ color: 'var(--accent-glow)' }}>
            Sentiment Report
          </p>
          <h1 className="text-3xl font-bold leading-tight" style={{ color: 'var(--text-primary)' }}>
            {data.product}
          </h1>
          <p className="text-sm mt-1" style={{ color: 'var(--text-muted)' }}>
            Based on {data.totalReviews.toLocaleString()} scraped reviews · Search: "
            <span style={{ color: 'var(--accent-glow)' }}>{searchedQuery}</span>"
          </p>
        </div>

      </div>

      {/* ── KPI Sentiment Cards ── */}
      <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
        <SentimentCard
          title="Positive Reviews"
          value={`${positive.percentage}%`}
          count={positive.count}
          delay={0}
        />
        <SentimentCard
          title="Neutral Reviews"
          value={`${neutral.percentage}%`}
          count={neutral.count}
          delay={100}
        />
        <SentimentCard
          title="Negative Reviews"
          value={`${negative.percentage}%`}
          count={negative.count}
          delay={200}
        />
      </div>

      {/* ── Charts row ── */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <PieChart
          positive={positive.percentage}
          neutral={neutral.percentage}
          negative={negative.percentage}
        />
        <BarChart
          positive={positive.count}
          neutral={neutral.count}
          negative={negative.count}
        />
      </div>

      {/* ── Reviews section ── */}
      <ReviewList reviews={data.reviews} />
    </div>
  );
}

export default DashboardPage;
