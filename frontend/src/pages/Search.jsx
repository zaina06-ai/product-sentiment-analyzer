import { useState } from "react";
import { SearchIcon, Loader2, AlertCircle, AudioLines } from "lucide-react";
import { searchProduct } from "../api";

export default function Search({ onResults }) {
  const [query, setQuery] = useState("iphone 15");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  async function handleSearch(e) {
    e.preventDefault();
    if (!query.trim()) {
      setError("Please enter a product to search for.");
      return;
    }

    setLoading(true);
    setError(null);

    const { data, error: apiError } = await searchProduct(query.trim());

    setLoading(false);

    if (apiError) {
      setError(apiError);
      return;
    }

    onResults(data);
  }

  return (
    <section className="hero">
      <div className="hero-icon">
        <AudioLines size={22} strokeWidth={2} />
      </div>

      <span className="eyebrow">live scrape</span>
      <h1 className="headline">Hear what customers actually feel</h1>
      <p className="subhead">
        Pull real reviews for any product and turn them into a signal —
        positive, neutral, negative — scored by TextBlob and VADER.
      </p>

      <form className="search-form" onSubmit={handleSearch}>
        <span className="prompt-prefix">product ›</span>
        <input
          type="text"
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          placeholder="e.g. iphone 15, boat airdopes…"
          className="search-input"
        />
        <button type="submit" className="search-button" disabled={loading}>
          {loading ? (
            <>
              <Loader2 size={16} className="spin" /> Listening…
            </>
          ) : (
            <>
              <SearchIcon size={16} /> Analyze
            </>
          )}
        </button>
      </form>

      {error && (
        <p className="error-text">
          <AlertCircle size={14} /> {error}
        </p>
      )}
    </section>
  );
}
