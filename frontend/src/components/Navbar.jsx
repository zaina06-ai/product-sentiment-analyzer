import { AudioLines } from "lucide-react";

export default function Navbar({ view, onNavigate, hasResults }) {
  return (
    <nav className="navbar">
      <div className="brand">
        <AudioLines size={20} className="brand-icon" strokeWidth={2.4} />
        <span className="brand-bold">Senti</span>
        <span className="brand-light">Scrap</span>
      </div>
      <div className="nav-tabs">
        <button
          className={`nav-tab ${view === "search" ? "active" : ""}`}
          onClick={() => onNavigate("search")}
        >
          Search
        </button>
        <button
          className={`nav-tab ${view === "dashboard" ? "active" : ""}`}
          onClick={() => hasResults && onNavigate("dashboard")}
          disabled={!hasResults}
          title={!hasResults ? "Search a product first" : ""}
        >
          Dashboard
        </button>
      </div>
    </nav>
  );
}
