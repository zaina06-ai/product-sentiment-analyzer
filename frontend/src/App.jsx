// App.jsx
// ─────────────────────────────────────────────────────────────────────────
// Root component. Sets up React Router with two routes:
//   /            → LandingPage  (search UI)
//   /dashboard   → DashboardPage (charts + reviews)
//
// Navbar and Footer live outside <Routes> so they appear on every page.
// ─────────────────────────────────────────────────────────────────────────

import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';

import Navbar   from './components/Navbar';
import Footer   from './components/Footer';
import LandingPage    from './pages/LandingPage';
import DashboardPage  from './pages/DashboardPage';

function App() {
  return (
    <Router>
      {/* ── Global layout wrapper ── */}
      <div style={{ minHeight: '100vh', display: 'flex', flexDirection: 'column', width: '100%', backgroundColor: 'var(--bg-primary)' }}>

        {/* Persistent top navigation */}
        <Navbar />

        {/* Page content grows to fill remaining height */}
        <main style={{ flex: 1, width: '100%', display: 'flex', flexDirection: 'column' }}>
          <Routes>
            <Route path="/"          element={<LandingPage />} />
            <Route path="/dashboard" element={<DashboardPage />} />
          </Routes>
        </main>

        {/* Persistent footer */}
        <Footer />
      </div>
    </Router>
  );
}

export default App;
