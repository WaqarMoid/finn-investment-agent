import { useState } from "react";
import type { FormEvent } from "react";

interface WatchlistCompany {
  symbol: string;
  name: string;
  sector: string;
  lastClose: string;
  changePct: string;
}

const SYNTHETIC_WATCHLIST_PREVIEW: WatchlistCompany[] = [
  { symbol: "INFY", name: "Infosys Limited", sector: "IT", lastClose: "1,113.10", changePct: "+0.85%" },
  { symbol: "TCS", name: "Tata Consultancy Services", sector: "IT", lastClose: "3,890.50", changePct: "-0.32%" },
  { symbol: "HCLTECH", name: "HCL Technologies", sector: "IT", lastClose: "1,620.00", changePct: "+1.20%" },
  { symbol: "HDFCBANK", name: "HDFC Bank Limited", sector: "Banking", lastClose: "1,745.20", changePct: "+0.15%" },
  { symbol: "ICICIBANK", name: "ICICI Bank Limited", sector: "Banking", lastClose: "1,260.40", changePct: "+0.45%" },
  { symbol: "RELIANCE", name: "Reliance Industries", sector: "Conglomerate", lastClose: "2,780.00", changePct: "-0.10%" },
];

export default function WatchlistScreen() {
  const [priceThreshold, setPriceThreshold] = useState("5.0");
  const [volumeMultiple, setVolumeMultiple] = useState("2.0");
  const [rulesSaved, setRulesSaved] = useState(false);

  const handleSave = (e: FormEvent) => {
    e.preventDefault();
    setRulesSaved(true);
    setTimeout(() => setRulesSaved(false), 3000);
  };

  return (
    <div className="watchlist-screen">
      {/* Synthetic preview banner */}
      <div style={{
        background: "#FFF8E1",
        border: "1px solid #FFE082",
        padding: "8px 12px",
        borderRadius: "var(--radius-control)",
        fontSize: "0.8125rem",
        color: "#795548",
        marginBottom: "var(--space-4)",
        display: "flex",
        alignItems: "center",
        justifyContent: "space-between"
      }}>
        <span><strong>T01 Shell Preview:</strong> Displaying labeled synthetic watchlist fixture.</span>
        <span className="badge badge-synthetic">SYNTHETIC FIXTURE</span>
      </div>

      <div style={{ marginBottom: "var(--space-3)" }}>
        <h1 style={{ fontSize: "1.375rem", fontWeight: 700, color: "var(--ink)" }}>Watchlist & Alert Rules</h1>
        <p style={{ fontSize: "0.8125rem", color: "var(--muted)" }}>
          Session-isolated preferences &bull; Anonymous reviewer session active
        </p>
      </div>

      {/* Rules Configuration Panel */}
      <div className="panel">
        <h2 className="panel-title" style={{ fontSize: "1rem", marginBottom: "var(--space-3)" }}>
          Notification Trigger Thresholds
        </h2>

        <form onSubmit={handleSave}>
          <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: "var(--space-3)", marginBottom: "var(--space-3)" }}>
            <div>
              <label style={{ display: "block", fontSize: "0.75rem", fontWeight: 600, color: "var(--muted)", marginBottom: "4px" }}>
                Price Move Threshold (%)
              </label>
              <input
                type="number"
                step="0.5"
                min="1.0"
                max="25.0"
                value={priceThreshold}
                onChange={(e) => setPriceThreshold(e.target.value)}
                style={{
                  width: "100%",
                  padding: "8px",
                  borderRadius: "var(--radius-control)",
                  border: "1px solid var(--control-border)",
                  fontSize: "0.875rem",
                }}
              />
              <span style={{ fontSize: "0.6875rem", color: "var(--muted)" }}>Alert if daily move exceeds this</span>
            </div>

            <div>
              <label style={{ display: "block", fontSize: "0.75rem", fontWeight: 600, color: "var(--muted)", marginBottom: "4px" }}>
                Volume Multiple (vs 20D)
              </label>
              <input
                type="number"
                step="0.1"
                min="1.0"
                max="10.0"
                value={volumeMultiple}
                onChange={(e) => setVolumeMultiple(e.target.value)}
                style={{
                  width: "100%",
                  padding: "8px",
                  borderRadius: "var(--radius-control)",
                  border: "1px solid var(--control-border)",
                  fontSize: "0.875rem",
                }}
              />
              <span style={{ fontSize: "0.6875rem", color: "var(--muted)" }}>Alert if volume &gt; N &times; 20-day mean</span>
            </div>
          </div>

          <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
            <span style={{ fontSize: "0.75rem", color: "var(--positive)", fontWeight: 600 }}>
              {rulesSaved ? "Rules saved for this session!" : ""}
            </span>
            <button
              type="submit"
              style={{
                background: "var(--accent)",
                color: "#FFF",
                border: "none",
                padding: "8px 16px",
                borderRadius: "var(--radius-control)",
                fontSize: "0.875rem",
                fontWeight: 600,
                cursor: "pointer",
                minHeight: "var(--min-touch-target)",
              }}
            >
              Save Alert Rules
            </button>
          </div>
        </form>
      </div>

      {/* Monitored Companies List */}
      <div className="panel">
        <div className="panel-header">
          <span className="panel-title" style={{ fontSize: "1rem" }}>
            Monitored Portfolio Holdings (18 Companies)
          </span>
        </div>

        <div style={{ display: "flex", flexDirection: "column" }}>
          {SYNTHETIC_WATCHLIST_PREVIEW.map((item) => (
            <div
              key={item.symbol}
              style={{
                display: "flex",
                justifyContent: "space-between",
                alignItems: "center",
                padding: "10px 0",
                borderBottom: "1px solid var(--line)",
              }}
            >
              <div>
                <strong style={{ fontSize: "0.875rem", color: "var(--ink)" }}>{item.symbol}</strong>
                <p style={{ fontSize: "0.75rem", color: "var(--muted)" }}>{item.name} &bull; {item.sector}</p>
              </div>
              <div style={{ textAlign: "right" }}>
                <span className="tabular-nums" style={{ fontSize: "0.875rem", fontWeight: 600, color: "var(--ink)" }}>
                  &#8377;{item.lastClose}
                </span>
                <p
                  className="tabular-nums"
                  style={{
                    fontSize: "0.75rem",
                    fontWeight: 600,
                    color: item.changePct.startsWith("+") ? "var(--positive)" : "var(--negative)",
                  }}
                >
                  {item.changePct}
                </p>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
