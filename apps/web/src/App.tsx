import { useState, useEffect } from "react";
import BriefingScreen from "./features/briefing/BriefingScreen";
import ResearchScreen from "./features/research/ResearchScreen";
import WatchlistScreen from "./features/watchlist/WatchlistScreen";
import "./styles/tokens.css";
import "./styles/layout.css";

type TabDestination = "briefing" | "research" | "watchlist";

export default function App() {
  const [currentTab, setCurrentTab] = useState<TabDestination>(() => {
    const hash = window.location.hash.replace("#/", "").replace("#", "");
    if (hash === "research" || hash === "watchlist") return hash;
    return "briefing";
  });

  const [apiReady, setApiReady] = useState<boolean | null>(null);

  // Sync hash with browser navigation (Back/Forward buttons)
  useEffect(() => {
    const handleHashChange = () => {
      const hash = window.location.hash.replace("#/", "").replace("#", "");
      if (hash === "briefing" || hash === "research" || hash === "watchlist") {
        setCurrentTab(hash);
      }
    };
    window.addEventListener("hashchange", handleHashChange);
    return () => window.removeEventListener("hashchange", handleHashChange);
  }, []);

  // Check backend API readiness
  useEffect(() => {
    fetch("/api/v1/health/ready")
      .then((res) => {
        if (res.ok) setApiReady(true);
        else setApiReady(false);
      })
      .catch(() => setApiReady(false));
  }, []);

  const switchTab = (tab: TabDestination) => {
    setCurrentTab(tab);
    window.location.hash = `#/${tab}`;
  };

  return (
    <div className="app-shell">
      {/* Top Header */}
      <header className="app-header">
        <div className="brand-container">
          <div className="brand-logo" aria-hidden="true">
            <div className="brand-logo-line"></div>
            <div className="brand-logo-line"></div>
          </div>
          <span className="brand-title">FINN</span>
          <span className="brand-badge">Briefing</span>
        </div>

        <div className="header-status">
          <span
            className="status-dot"
            style={{ backgroundColor: apiReady === true ? "var(--positive)" : apiReady === false ? "var(--warning)" : "var(--muted)" }}
            title={apiReady === true ? "API Connected & Ready" : apiReady === false ? "API Offline / Standalone Mode" : "Checking API..."}
          ></span>
          <span>{apiReady === true ? "Live" : "Replay"}</span>
        </div>
      </header>

      {/* Main Content Area */}
      <main className="main-content">
        {currentTab === "briefing" && <BriefingScreen />}
        {currentTab === "research" && <ResearchScreen />}
        {currentTab === "watchlist" && <WatchlistScreen />}
      </main>

      {/* Mobile Bottom / Desktop Side Navigation */}
      <nav className="bottom-nav" aria-label="Main Navigation">
        <button
          className={`nav-item ${currentTab === "briefing" ? "active" : ""}`}
          onClick={() => switchTab("briefing")}
          aria-label="Portfolio Briefing"
        >
          {/* Briefing Icon */}
          <svg className="nav-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
            <path d="M4 6h16M4 12h16M4 18h7" />
          </svg>
          <span>Briefing</span>
        </button>

        <button
          className={`nav-item ${currentTab === "research" ? "active" : ""}`}
          onClick={() => switchTab("research")}
          aria-label="Primary Research"
        >
          {/* Research Icon */}
          <svg className="nav-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
            <circle cx="11" cy="11" r="8" />
            <line x1="21" y1="21" x2="16.65" y2="16.65" />
          </svg>
          <span>Research</span>
        </button>

        <button
          className={`nav-item ${currentTab === "watchlist" ? "active" : ""}`}
          onClick={() => switchTab("watchlist")}
          aria-label="Watchlist & Rules"
        >
          {/* Watchlist Icon */}
          <svg className="nav-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
            <path d="M19 21l-7-5-7 5V5a2 2 0 0 1 2-2h10a2 2 0 0 1 2 2z" />
          </svg>
          <span>Watchlist</span>
        </button>
      </nav>
    </div>
  );
}
