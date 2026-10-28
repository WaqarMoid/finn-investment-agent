import { useState, useEffect } from "react";
import type { FormEvent } from "react";

interface WatchlistCompany {
  company_id: string;
  symbol: string;
  legal_name: string;
  sector: string;
  isin: string;
  price_provider_symbol?: string;
}

interface AlertItem {
  id: string;
  company_name: string;
  symbol: string;
  source_type: string;
  reason: string;
  created_at_utc: string;
  acknowledged: boolean;
}

interface PreviewItem {
  type: string;
  company_name: string;
  symbol: string;
  title: string;
  category: string;
  tier: string;
  match_reason: string;
}

export default function WatchlistScreen() {
  const [companies, setCompanies] = useState<WatchlistCompany[]>([]);
  const [alerts, setAlerts] = useState<AlertItem[]>([]);
  const [priceThreshold, setPriceThreshold] = useState("5.0");
  const [volumeMultiple, setVolumeMultiple] = useState("2.0");
  const [rulesSaved, setRulesSaved] = useState(false);
  const [previewMatches, setPreviewMatches] = useState<PreviewItem[] | null>(null);
  const [previewLoading, setPreviewLoading] = useState(false);

  // Load watchlist, notification rules, and alerts
  useEffect(() => {
    fetch("/api/v1/watchlist")
      .then((res) => res.json())
      .then((json) => setCompanies(json.data || []))
      .catch(() => {});

    fetch("/api/v1/notification-rules")
      .then((res) => res.json())
      .then((json) => {
        if (json.data) {
          setPriceThreshold(String(json.data.price_pct));
          setVolumeMultiple(String(json.data.volume_multiple));
        }
      })
      .catch(() => {});

    fetch("/api/v1/alerts")
      .then((res) => res.json())
      .then((json) => setAlerts(json.data || []))
      .catch(() => {});
  }, []);

  const handleSave = async (e: FormEvent) => {
    e.preventDefault();
    try {
      const res = await fetch("/api/v1/notification-rules", {
        method: "PUT",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          price_pct: parseFloat(priceThreshold),
          volume_multiple: parseFloat(volumeMultiple),
          categories: ["results", "m_and_a", "litigation", "management_change", "dividend"],
          min_materiality: "worth_a_look",
          enabled: true,
        }),
      });
      if (res.ok) {
        setRulesSaved(true);
        setTimeout(() => setRulesSaved(false), 3000);
      }
    } catch {
      // Ignore
    }
  };

  const handlePreview = async () => {
    setPreviewLoading(true);
    setPreviewMatches(null);
    try {
      const res = await fetch("/api/v1/notification-rules/preview", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          price_pct: parseFloat(priceThreshold),
          volume_multiple: parseFloat(volumeMultiple),
        }),
      });
      if (res.ok) {
        const json = await res.json();
        setPreviewMatches(json.data || []);
      }
    } finally {
      setPreviewLoading(false);
    }
  };

  const handleAcknowledge = async (alertId: string) => {
    try {
      const res = await fetch(`/api/v1/alerts/${alertId}`, { method: "PATCH" });
      if (res.ok) {
        setAlerts((prev) =>
          prev.map((a) => (a.id === alertId ? { ...a, acknowledged: true } : a))
        );
      }
    } catch {
      // Ignore
    }
  };

  const unreadAlerts = alerts.filter((a) => !a.acknowledged);

  return (
    <div className="watchlist-screen">
      <div style={{ marginBottom: "var(--space-3)" }}>
        <h1 style={{ fontSize: "1.375rem", fontWeight: 700, color: "var(--ink)" }}>Watchlist & Notification Rules</h1>
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
              <label htmlFor="price-input" style={{ display: "block", fontSize: "0.75rem", fontWeight: 600, color: "var(--muted)", marginBottom: "4px" }}>
                Price Move Threshold (%)
              </label>
              <input
                id="price-input"
                type="number"
                step="0.5"
                min="0.5"
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
              <span style={{ fontSize: "0.6875rem", color: "var(--muted)" }}>Alert if daily move strictly exceeds this</span>
            </div>

            <div>
              <label htmlFor="volume-input" style={{ display: "block", fontSize: "0.75rem", fontWeight: 600, color: "var(--muted)", marginBottom: "4px" }}>
                Volume Multiple (vs 20D)
              </label>
              <input
                id="volume-input"
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

          <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", flexWrap: "wrap", gap: "8px" }}>
            <button
              type="button"
              onClick={handlePreview}
              disabled={previewLoading}
              style={{
                background: "var(--surface-muted)",
                color: "var(--ink)",
                border: "1px solid var(--line)",
                padding: "8px 12px",
                borderRadius: "var(--radius-control)",
                fontSize: "0.8125rem",
                fontWeight: 600,
                cursor: previewLoading ? "not-allowed" : "pointer",
              }}
            >
              {previewLoading ? "Testing..." : "Test on recent data"}
            </button>

            <div style={{ display: "flex", alignItems: "center", gap: "var(--space-3)" }}>
              {rulesSaved && (
                <span style={{ fontSize: "0.8125rem", color: "var(--positive)", fontWeight: 600 }}>
                  Rules saved for this session!
                </span>
              )}
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
          </div>
        </form>

        {/* Non-notifying Preview Results */}
        {previewMatches && (
          <div style={{ marginTop: "var(--space-4)", paddingTop: "var(--space-3)", borderTop: "1px solid var(--line)" }}>
            <h4 style={{ fontSize: "0.875rem", fontWeight: 600, color: "var(--ink)", marginBottom: "4px" }}>
              Preview Matches ({previewMatches.length} recent events match rules)
            </h4>
            <p style={{ fontSize: "0.75rem", color: "var(--muted)", marginBottom: "8px" }}>
              Non-notifying preview: these events match your criteria but were not added to your inbox.
            </p>
            {previewMatches.map((m, idx) => (
              <div key={idx} style={{ fontSize: "0.8125rem", padding: "6px 0", borderBottom: "1px solid var(--line)" }}>
                <strong>{m.symbol}</strong>: {m.title}
                <span className="badge badge-worth-a-look" style={{ marginLeft: "8px", fontSize: "0.6875rem" }}>{m.tier}</span>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Session Alerts Inbox */}
      <div className="panel">
        <div className="panel-header">
          <div style={{ display: "flex", alignItems: "center", gap: "var(--space-2)" }}>
            <h2 className="panel-title" style={{ fontSize: "1rem" }}>Session Alerts Inbox</h2>
            {unreadAlerts.length > 0 && (
              <span className="badge badge-attention">{unreadAlerts.length} Unread</span>
            )}
          </div>
        </div>

        {alerts.length === 0 ? (
          <p style={{ fontSize: "0.8125rem", color: "var(--muted)", fontStyle: "italic" }}>
            No alerts triggered yet for this session.
          </p>
        ) : (
          <div>
            {alerts.map((al) => (
              <div
                key={al.id}
                style={{
                  padding: "8px 0",
                  borderBottom: "1px solid var(--line)",
                  display: "flex",
                  justifyContent: "space-between",
                  alignItems: "center",
                  opacity: al.acknowledged ? 0.6 : 1.0,
                }}
              >
                <div>
                  <div style={{ fontSize: "0.8125rem", fontWeight: 600, color: "var(--ink)" }}>
                    {al.symbol}: {al.source_type.toUpperCase()}
                  </div>
                  <div style={{ fontSize: "0.75rem", color: "var(--muted)" }}>{al.reason}</div>
                </div>
                {!al.acknowledged && (
                  <button
                    onClick={() => handleAcknowledge(al.id)}
                    style={{
                      background: "var(--accent-soft)",
                      color: "var(--accent)",
                      border: "none",
                      padding: "4px 8px",
                      borderRadius: "var(--radius-control)",
                      fontSize: "0.75rem",
                      cursor: "pointer",
                    }}
                  >
                    Acknowledge
                  </button>
                )}
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Monitored Companies List */}
      <div className="panel">
        <div className="panel-header">
          <h2 className="panel-title" style={{ fontSize: "1rem" }}>
            Monitored Portfolio Holdings ({companies.length} Companies)
          </h2>
        </div>

        <div style={{ display: "flex", flexDirection: "column" }}>
          {companies.map((item) => (
            <div
              key={item.company_id}
              style={{
                display: "flex",
                justifyContent: "space-between",
                alignItems: "center",
                padding: "8px 0",
                borderBottom: "1px solid var(--line)",
              }}
            >
              <div>
                <strong style={{ fontSize: "0.875rem", color: "var(--ink)" }}>{item.symbol}</strong>
                <p style={{ fontSize: "0.75rem", color: "var(--muted)" }}>{item.legal_name} &bull; {item.sector}</p>
              </div>
              <span className="badge badge-routine" style={{ fontSize: "0.6875rem" }}>
                Active Monitoring
              </span>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
