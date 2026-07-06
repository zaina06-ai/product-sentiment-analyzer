import { Pie } from "react-chartjs-2";
import {
  Chart as ChartJS,
  ArcElement,
  Tooltip,
  Legend,
} from "chart.js";
import {
  Smile,
  Meh,
  Frown,
  Gauge,
  ExternalLink,
  Inbox,
} from "lucide-react";
import Waveform from "../components/Waveform";

ChartJS.register(ArcElement, Tooltip, Legend);

const CHART_OPTIONS = {
  plugins: {
    legend: {
      position: "bottom",
      labels: {
        color: "#8B93A7",
        font: { family: "Inter", size: 12 },
        padding: 16,
        usePointStyle: true,
        pointStyle: "circle",
      },
    },
    tooltip: {
      backgroundColor: "#12172A",
      borderColor: "#232B45",
      borderWidth: 1,
      titleColor: "#EDEFF5",
      bodyColor: "#EDEFF5",
      padding: 10,
      titleFont: { family: "Space Grotesk" },
      bodyFont: { family: "JetBrains Mono" },
    },
  },
  cutout: "62%",
};

export default function Dashboard({ results }) {
  // Guard against missing data instead of crashing with
  // "Cannot read properties of undefined" like the original bug.
  if (!results) {
    return (
      <section className="dashboard-empty">
        <Inbox size={32} strokeWidth={1.5} />
        <p>No results yet. Go to Search and look up a product first.</p>
      </section>
    );
  }

  const product = results.product ?? {};
  const summary = results.summary ?? {
    positive: 0,
    neutral: 0,
    negative: 0,
    total: 0,
    average_score: 0,
  };
  const reviews = results.reviews ?? [];

  const chartData = {
    labels: ["Positive", "Neutral", "Negative"],
    datasets: [
      {
        data: [summary.positive, summary.neutral, summary.negative],
        backgroundColor: ["#3DD9A4", "#5B6478", "#FB6B7A"],
        borderWidth: 0,
        hoverOffset: 6,
      },
    ],
  };

  return (
    <section className="dashboard">
      <div className="product-card">
        {product.image && (
          <img src={product.image} alt={product.name} className="product-image" />
        )}
        <div>
          <h2 className="product-name">
            {product.name ?? "Unknown product"}
            {results.cached && <span className="cached-badge">cached</span>}
          </h2>
          {product.price && <p className="product-price">{product.price}</p>}
          {product.url && (
            <a href={product.url} target="_blank" rel="noreferrer" className="product-link">
              View on Flipkart <ExternalLink size={12} />
            </a>
          )}
        </div>
      </div>

      <div className="stats-grid">
        <div className="chart-box">
          <Pie data={chartData} options={CHART_OPTIONS} />
        </div>

        <div className="stat-cards">
          <StatCard icon={Smile} label="Positive" value={summary.positive} color="#3DD9A4" />
          <StatCard icon={Meh} label="Neutral" value={summary.neutral} color="#8B93A7" />
          <StatCard icon={Frown} label="Negative" value={summary.negative} color="#FB6B7A" />
          <StatCard
            icon={Gauge}
            label="Avg. score"
            value={summary.average_score}
            color="#FFC857"
          />
        </div>
      </div>

      <Waveform reviews={reviews} />

      <div className="reviews-list">
        <h3>Reviews ({reviews.length})</h3>
        {reviews.length === 0 && <p>No reviews were found for this product.</p>}
        {reviews.map((r, i) => (
          <div
            key={i}
            className={`review-card ${r.label ?? "neutral"}`}
            style={{ animationDelay: `${Math.min(i, 12) * 40}ms` }}
          >
            <p className="review-text">{r.text}</p>
            <span className={`review-label ${r.label ?? "neutral"}`}>
              {r.label ?? "neutral"}
            </span>
          </div>
        ))}
      </div>
    </section>
  );
}

function StatCard({ icon: Icon, label, value, color }) {
  return (
    <div className="stat-card" style={{ "--stat-color": color }}>
      <div className="stat-top">
        <Icon size={16} color={color} strokeWidth={2.2} />
        <span className="stat-label">{label}</span>
      </div>
      <span className="stat-value" style={{ color }}>
        {value}
      </span>
    </div>
  );
}
