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

const getAvatarClass = (symbol: string) => {
  const s = symbol.toUpperCase().replace(".NS", "");
  if (s.includes("INFY")) return "avatar-infy";
  if (s.includes("TCS")) return "avatar-tcs";
  if (s.includes("HCL")) return "avatar-hcltech";
  if (s.includes("REL")) return "avatar-reliance";
  if (s.includes("COF")) return "avatar-coforge";
  if (s.includes("DIX")) return "avatar-dixon";
  if (s.includes("AST")) return "avatar-astral";
  return "avatar-generic";
};

export default function WatchlistScreen() {
  const [companies, setCompanies] = useState<WatchlistCompany[]>([]);
  const [alerts, setAlerts] = useState<AlertItem[]>([]);
  const [priceThreshold, setPriceThreshold] = useState("5.0");
  const [volumeMultiple, setVolumeMultiple] = useState("2.0");
  const [rulesSaved, setRulesSaved] = useState(false);
  const [previewMatches, setPreviewMatches] = useState<PreviewItem[] | null>(null);
  const [previewLoading, setPreviewLoading] = useState(false);

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
      <header className="screen-heading">
        <div className="screen-kicker">Portfolio & Trigger Rules</div>
        <h1 className="screen-title">Watchlist & Alerts</h1>
        <p className="screen-subtitle">
          Session-isolated portfolio preferences and automated thresholds for material disclosures, volume spikes, and unusual price swings.
        </p>
      </header>

      {/* Rules Configuration Panel */}
      <section className="panel">
        <div className="panel-header">
          <span className="panel-title">Trigger Thresholds</span>
          <span className="badge badge-routine">Session Scoped</span>
        </div>

        <form onSubmit={handleSave}>
          <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 12, marginBottom: 14 }}>
            <div className="field">
              <label htmlFor="price-input">Price Move Threshold (%)</label>
              <input
                id="price-input"
                type="number"
                step="0.5"
                min="0.5"
                max="25.0"
                value={priceThreshold}
                onChange={(e) => setPriceThreshold(e.target.value)}
              />
              <span style={{ fontSize: 11, color: "var(--muted)", paddingLeft: 4 }}>
                Alert if daily move strictly exceeds ±X%
              </span>
            </div>

            <div className="field">
              <label htmlFor="volume-input">Volume Multiple (vs 20D)</label>
              <input
                id="volume-input"
                type="number"
                step="0.1"
                min="1.0"
                max="10.0"
                value={volumeMultiple}
                onChange={(e) => setVolumeMultiple(e.target.value)}
              />
              <span style={{ fontSize: 11, color: "var(--muted)", paddingLeft: 4 }}>
                Alert if volume &gt; N × 20-day baseline
              </span>
            </div>
          </div>

          <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", flexWrap: "wrap", gap: 10 }}>
            <button
              type="button"
              className="button secondary"
              onClick={handlePreview}
              disabled={previewLoading}
            >
              {previewLoading ? "Testing…" : "Test on recent data"}
            </button>

            <div style={{ display: "flex", alignItems: "center", gap: 12 }}>
              {rulesSaved && (
                <span style={{ fontSize: 13, color: "var(--positive)", fontWeight: 700 }}>
                  ✓ Rules saved for this session!
                </span>
              )}
              <button className="button" type="submit">
                Save Alert Rules
              </button>
            </div>
          </div>
        </form>

        {/* Non-notifying Preview Results */}
        {previewMatches && (
          <div style={{ marginTop: 16, paddingTop: 14, borderTop: "1px solid var(--line)" }}>
            <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between", marginBottom: 6 }}>
              <h4 style={{ fontSize: 14, fontWeight: 750, color: "var(--ink)" }}>
                Rule Test Matches ({previewMatches.length} recent events match criteria)
              </h4>
              <span className="badge badge-routine">Non-Notifying</span>
            </div>
            <p style={{ fontSize: 12, color: "var(--muted)", marginBottom: 10 }}>
              These events match your criteria but do not clutter your alerts inbox.
            </p>
            {previewMatches.map((m, idx) => (
              <div key={idx} style={{ fontSize: 13, padding: "8px 0", borderBottom: "1px solid var(--line)" }}>
                <strong>{m.symbol}</strong>: {m.title}
                <span className="badge badge-worth-a-look" style={{ marginLeft: 8, fontSize: 11 }}>
                  {m.tier}
                </span>
              </div>
            ))}
          </div>
        )}
      </section>

      {/* Session Alerts Inbox */}
      <section className="panel">
        <div className="panel-header">
          <div style={{ display: "flex", alignItems: "center", gap: 8 }}>
            <span className="panel-title">Session Alerts Inbox</span>
            {unreadAlerts.length > 0 && (
              <span className="badge badge-attention">{unreadAlerts.length} Unread</span>
            )}
          </div>
        </div>

        {alerts.length === 0 ? (
          <p style={{ fontSize: 13, color: "var(--muted)", fontStyle: "italic", padding: "10px 0" }}>
            No triggered alerts yet for this session.
          </p>
        ) : (
          <div>
            {alerts.map((al) => (
              <div
                key={al.id}
                style={{
                  padding: "10px 0",
                  borderBottom: "1px solid var(--line)",
                  display: "flex",
                  justifyContent: "space-between",
                  alignItems: "center",
                  opacity: al.acknowledged ? 0.55 : 1.0,
                }}
              >
                <div>
                  <div style={{ fontSize: 13.5, fontWeight: 700, color: "var(--ink)" }}>
                    {al.symbol}: {al.source_type.toUpperCase()}
                  </div>
                  <div style={{ fontSize: 12.5, color: "var(--muted)", marginTop: 2 }}>{al.reason}</div>
                </div>
                {!al.acknowledged && (
                  <button
                    className="button secondary"
                    style={{ minHeight: 32, padding: "0 12px", fontSize: 11.5 }}
                    onClick={() => handleAcknowledge(al.id)}
                  >
                    Acknowledge
                  </button>
                )}
              </div>
            ))}
          </div>
        )}
      </section>

      {/* Monitored Holdings List */}
      <section className="panel">
        <div className="panel-header">
          <span className="panel-title">Monitored Portfolio Holdings</span>
          <span className="badge badge-routine">{companies.length} Companies</span>
        </div>

        <div style={{ display: "flex", flexDirection: "column" }}>
          {companies.map((item) => (
            <div
              key={item.company_id}
              style={{
                display: "flex",
                justifyContent: "space-between",
                alignItems: "center",
                padding: "12px 0",
                borderBottom: "1px solid var(--line)",
              }}
            >
              <div style={{ display: "flex", alignItems: "center", gap: 12 }}>
                <div className={`company-avatar ${getAvatarClass(item.symbol)}`}>
                  {item.symbol.slice(0, 2).toUpperCase()}
                </div>
                <div>
                  <strong style={{ fontSize: 14.5, color: "var(--ink)" }}>{item.symbol}</strong>
                  <p style={{ fontSize: 12.5, color: "var(--muted)", marginTop: 2 }}>
                    {item.legal_name} · {item.sector}
                  </p>
                </div>
              </div>
              <button
                className="button secondary"
                style={{ minHeight: 32, padding: "0 12px", fontSize: 11.5 }}
                onClick={() => {
                  window.location.hash = "#/research";
                }}
              >
                Research
              </button>
            </div>
          ))}
        </div>
      </section>
    </div>
  );
}
