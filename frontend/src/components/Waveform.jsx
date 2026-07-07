/**
 * Renders the review set as a waveform: one bar per review, in scrape
 * order, height = sentiment intensity, color = polarity. This is the
 * literal shape of "customer voice" for the product, not a decoration.
 */
export default function Waveform({ reviews }) {
  if (!reviews || reviews.length === 0) return null;

  const colorFor = (label) =>
    label === "positive" ? "#3DD9A4" : label === "negative" ? "#FB6B7A" : "#5B6478";

  return (
    <div className="waveform">
      <div className="waveform-label">
        <span>Voice signal</span>
        <span className="waveform-sub">{reviews.length} reviews, in scrape order</span>
      </div>
      <div className="waveform-track">
        {reviews.map((r, i) => {
          const intensity = Math.min(Math.abs(r.combined_score ?? 0), 1);
          const height = 12 + intensity * 48; // px, 12 min so silence is still visible
          return (
            <div
              key={i}
              className="waveform-bar"
              style={{
                height: `${height}px`,
                background: colorFor(r.label),
              }}
              title={`${r.label ?? "neutral"} · ${r.combined_score ?? 0}`}
            />
          );
        })}
      </div>
    </div>
  );
}
