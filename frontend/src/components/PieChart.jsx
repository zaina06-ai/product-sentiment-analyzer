// components/PieChart.jsx
// ─────────────────────────────────────────────────────────────────────────
// Doughnut chart showing the Positive / Neutral / Negative split.
//
// Why Doughnut (not Pie)?
//   More modern look; the hollow center can display a label.
//
// Chart.js v3+ requires explicit registration of modules — we only register
// what we use (ArcElement, Tooltip, Legend, DoughnutController) to keep the
// bundle lean.
//
// Props:
//   positive {number} — percentage of positive reviews (0-100)
//   neutral  {number} — percentage of neutral reviews
//   negative {number} — percentage of negative reviews
// ─────────────────────────────────────────────────────────────────────────

import React from 'react';
import { Doughnut } from 'react-chartjs-2';
import {
  Chart as ChartJS,
  ArcElement,
  Tooltip,
  Legend,
} from 'chart.js';

// Register only what we use
ChartJS.register(ArcElement, Tooltip, Legend);

function PieChart({ positive = 0, neutral = 0, negative = 0 }) {
  const data = {
    labels: ['Positive', 'Neutral', 'Negative'],
    datasets: [
      {
        data: [positive, neutral, negative],
        backgroundColor: [
          'rgba(34,197,94,0.85)',   // green  — positive
          'rgba(245,158,11,0.85)',  // amber  — neutral
          'rgba(239,68,68,0.85)',   // red    — negative
        ],
        borderColor: [
          '#22c55e',
          '#f59e0b',
          '#ef4444',
        ],
        borderWidth: 2,
        hoverOffset: 8,
      },
    ],
  };

  const options = {
    responsive: true,
    cutout: '68%',           // creates the doughnut hole
    plugins: {
      legend: {
        position: 'bottom',
        labels: {
          color: '#94a3b8',       // var(--text-muted)
          padding: 16,
          font: { size: 13, family: 'Inter' },
          usePointStyle: true,
          pointStyleWidth: 10,
        },
      },
      tooltip: {
        callbacks: {
          label: (ctx) => ` ${ctx.label}: ${ctx.parsed}%`,
        },
        backgroundColor: '#ffffff',
        titleColor: '#111827',
        bodyColor: '#4b5563',
        borderColor: '#e5e7eb',
        borderWidth: 1,
      },
    },
  };

  return (
    <div
      id="pie-chart-container"
      className="rounded-2xl p-6 flex flex-col gap-4 animate-fade-in-up"
      style={{
        backgroundColor: 'var(--bg-card)',
        border: '1px solid #e5e7eb',
        boxShadow: '0 4px 12px rgba(0,0,0,0.05)',
        animationDelay: '200ms',
      }}
    >
      <h3 className="text-base font-semibold" style={{ color: 'var(--text-primary)' }}>
        Sentiment Distribution
      </h3>

      <div className="max-w-[280px] mx-auto w-full">
        <Doughnut data={data} options={options} />
      </div>
    </div>
  );
}

export default PieChart;
