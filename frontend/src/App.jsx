import { useState } from "react";
import Navbar from "./components/Navbar";
import Search from "./pages/Search";
import Dashboard from "./pages/Dashboard";

export default function App() {
  const [view, setView] = useState("search");
  const [results, setResults] = useState(null);

  function handleResults(data) {
    setResults(data);
    setView("dashboard");
  }

  return (
    <div className="app">
      <Navbar view={view} onNavigate={setView} hasResults={!!results} />

      <main>
        {view === "search" && <Search onResults={handleResults} />}
        {view === "dashboard" && <Dashboard results={results} />}
      </main>

      <footer className="footer">
        <span>© 2026 SentiScrap — Product Sentiment Analyzer</span>
        <span>Built with React · Chart.js · TextBlob · VADER</span>
      </footer>
    </div>
  );
}
