// components/BarChart.jsx
// ─────────────────────────────────────────────────────────────────────────
// Bar chart comparing raw review counts per sentiment category.
//
// Chart.js v3+ requires manual registration. We register:
//   BarElement, CategoryScale, LinearScale, Tooltip, Legend
//
// Props:
//   positive {number} — count of positive reviews
//   neutral  {number} — count of neutral reviews
//   negative {number} — count of negative reviews
// ─────────────────────────────────────────────────────────────────────────

import React from 'react';
import { Bar } from 'react-chartjs-2';
import {
  Chart as ChartJS,
  BarElement,
  CategoryScale,
  LinearScale,
  Tooltip,
  Legend,
} from 'chart.js';

ChartJS.register(BarElement, CategoryScale, LinearScale, Tooltip, Legend);

function BarChart({ positive = 0, neutral = 0, negative = 0 }) {
  const data = {
    labels: ['Positive', 'Neutral', 'Negative'],
    datasets: [
      {
        label: 'Review Count',
        data: [positive, neutral, negative],
        backgroundColor: [
          'rgba(34,197,94,0.75)',
          'rgba(245,158,11,0.75)',
          'rgba(239,68,68,0.75)',
        ],
        borderColor: ['#22c55e', '#f59e0b', '#ef4444'],
        borderWidth: 2,
        borderRadius: 8,         // rounded bar tops
        borderSkipped: false,    // round all corners, not just top
      },
    ],
  };

  const options = {
    responsive: true,
    plugins: {
      legend: { display: false },   // legend is redundant with labeled x-axis
      tooltip: {
        backgroundColor: '#ffffff',
        titleColor: '#111827',
        bodyColor: '#4b5563',
        borderColor: '#e5e7eb',
        borderWidth: 1,
        callbacks: {
          label: (ctx) => ` ${ctx.parsed.y} reviews`,
        },
      },
    },
    scales: {
      x: {
        ticks:  { color: '#94a3b8', font: { family: 'Inter', size: 13 } },
        grid:   { display: false },
        border: { color: '#e5e7eb' },
      },
      y: {
        beginAtZero: true,
        ticks: {
          color: '#94a3b8',
          font: { family: 'Inter', size: 12 },
          precision: 0,           // no decimal places on y-axis
        },
        grid:   { color: '#e5e7eb' },
        border: { color: 'transparent' },
      },
    },
  };

  return (
    <div
      id="bar-chart-container"
      className="rounded-2xl p-6 flex flex-col gap-4 animate-fade-in-up"
      style={{
        backgroundColor: 'var(--bg-card)',
        border: '1px solid #e5e7eb',
        boxShadow: '0 4px 12px rgba(0,0,0,0.05)',
        animationDelay: '300ms',
      }}
    >
      <h3 className="text-base font-semibold" style={{ color: 'var(--text-primary)' }}>
        Review Count by Sentiment
      </h3>

      <Bar data={data} options={options} />
    </div>
  );
}

export default BarChart;
