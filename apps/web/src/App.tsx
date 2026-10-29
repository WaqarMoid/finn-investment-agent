import { useEffect, useState } from "react";
import BriefingScreen from "./features/briefing/BriefingScreen";
import ResearchScreen from "./features/research/ResearchScreen";
import WatchlistScreen from "./features/watchlist/WatchlistScreen";
import "./styles/tokens.css";
import "./styles/layout.css";

type TabDestination = "briefing" | "research" | "watchlist";
type Theme = "light" | "dark";

const icons = {
  briefing: <path d="M4 6h16M4 12h16M4 18h10" />,
  research: <><circle cx="10.5" cy="10.5" r="6.5" /><path d="m16 16 4 4" /></>,
  watchlist: <path d="M6 4h12v16l-6-4-6 4V4Z" />,
};

export default function App() {
  const [currentTab, setCurrentTab] = useState<TabDestination>(() => {
    const hash = window.location.hash.replace("#/", "").replace("#", "");
    return hash === "research" || hash === "watchlist" ? hash : "briefing";
  });
  const [apiReady, setApiReady] = useState<boolean | null>(null);
  const [theme, setTheme] = useState<Theme>(() => {
    const saved = localStorage.getItem("finn-theme") as Theme | null;
    return saved || (window.matchMedia("(prefers-color-scheme: dark)").matches ? "dark" : "light");
  });

  useEffect(() => {
    document.documentElement.dataset.theme = theme;
    localStorage.setItem("finn-theme", theme);
    document.querySelector('meta[name="theme-color"]')?.setAttribute("content", theme === "dark" ? "#000000" : "#f8f9fa");
  }, [theme]);

  useEffect(() => {
    const handleHash = () => {
      const hash = window.location.hash.replace("#/", "").replace("#", "");
      if (["briefing", "research", "watchlist"].includes(hash)) setCurrentTab(hash as TabDestination);
    };
    window.addEventListener("hashchange", handleHash);
    fetch("/api/v1/health/ready").then(r => setApiReady(r.ok)).catch(() => setApiReady(false));
    return () => window.removeEventListener("hashchange", handleHash);
  }, []);

  const switchTab = (tab: TabDestination) => {
    setCurrentTab(tab);
    window.location.hash = `#/${tab}`;
  };

  return (
    <div className="app-shell">
      <aside className="app-rail">
        <div className="rail-brand" aria-label="FINN home">
          <span className="brand-mark">F</span>
          <span className="brand-word">FINN</span>
        </div>
        <nav className="bottom-nav" aria-label="Main navigation">
          {(["briefing", "research", "watchlist"] as TabDestination[]).map(tab => (
            <button key={tab} className={`nav-item ${currentTab === tab ? "active" : ""}`} onClick={() => switchTab(tab)} aria-current={currentTab === tab ? "page" : undefined}>
              <svg className="nav-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8">{icons[tab]}</svg>
              <span>{tab[0].toUpperCase() + tab.slice(1)}</span>
            </button>
          ))}
        </nav>
      </aside>

      <div className="app-stage">
        <header className="app-header">
          <div className="mobile-brand"><span className="brand-mark">F</span><span>FINN</span></div>
          <div className={`connection-pill ${apiReady === false ? "offline" : ""}`}>
            <span className="status-dot" />
            {apiReady === null ? "Connecting" : apiReady ? "Live" : "Offline"}
          </div>
          <button className="icon-button" onClick={() => setTheme(theme === "dark" ? "light" : "dark")} aria-label={`Use ${theme === "dark" ? "light" : "dark"} theme`} title="Change theme">
            {theme === "dark" ? (
              <svg viewBox="0 0 24 24"><circle cx="12" cy="12" r="4"/><path d="M12 2v2M12 20v2M4.9 4.9l1.4 1.4M17.7 17.7l1.4 1.4M2 12h2M20 12h2M4.9 19.1l1.4-1.4M17.7 6.3l1.4-1.4"/></svg>
            ) : (
              <svg viewBox="0 0 24 24"><path d="M20 15.5A8.5 8.5 0 0 1 8.5 4 8.5 8.5 0 1 0 20 15.5Z"/></svg>
            )}
          </button>
        </header>
        <main className="main-content">
          {currentTab === "briefing" && <BriefingScreen />}
          {currentTab === "research" && <ResearchScreen />}
          {currentTab === "watchlist" && <WatchlistScreen />}
        </main>
      </div>
    </div>
  );
}
