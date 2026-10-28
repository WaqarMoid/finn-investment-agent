import { useState, useEffect } from "react";
import EvidenceDrawer from "../../components/evidence/EvidenceDrawer";

interface BriefingEvent {
  id: string;
  company_id: string;
  company_name: string;
  symbol: string;
  event_date: string;
  kind: string;
  headline: string;
  implication: string;
  tier: "needs_attention" | "worth_a_look" | "routine";
  score: number;
  reasons: string[];
  filings_count: number;
  attachment_url?: string;
  created_at_utc: string;
}

interface BriefingData {
  tiers: {
    needs_attention: BriefingEvent[];
    worth_a_look: BriefingEvent[];
    routine: BriefingEvent[];
  };
  summary: {
    needs_attention_count: number;
    worth_a_look_count: number;
    routine_count: number;
    total_events: number;
    total_source_filings: number;
  };
}

export default function BriefingScreen() {
  const [windowPreset, setWindowPreset] = useState<"24h" | "7d" | "custom">("24h");
  const [data, setData] = useState<BriefingData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [selectedEvidenceId, setSelectedEvidenceId] = useState<string | null>(null);
  const [expandRoutine, setExpandRoutine] = useState(false);
  const [refreshing, setRefreshing] = useState(false);

  const fetchBriefing = (preset: "24h" | "7d" | "custom") => {
    setLoading(true);
    setError(null);

    const now = new Date();
    const end = now.toISOString();
    let start = new Date(now.getTime() - 24 * 3600 * 1000).toISOString();

    if (preset === "7d") {
      start = new Date(now.getTime() - 7 * 24 * 3600 * 1000).toISOString();
    } else if (preset === "custom") {
      // 30 days default for custom test
      start = new Date(now.getTime() - 30 * 24 * 3600 * 1000).toISOString();
    }

    fetch(`/api/v1/briefing?start=${encodeURIComponent(start)}&end=${encodeURIComponent(end)}`)
      .then((res) => {
        if (!res.ok) throw new Error(`Briefing request failed: ${res.status}`);
        return res.json();
      })
      .then((json) => {
        setData(json.data);
        setLoading(false);
      })
      .catch((err) => {
        setError(err.message);
        setLoading(false);
      });
  };

  useEffect(() => {
    fetchBriefing(windowPreset);
  }, [windowPreset]);

  const handleRefresh = async () => {
    setRefreshing(true);
    try {
      const res = await fetch("/api/v1/refresh", { method: "POST" });
      if (res.status === 429) {
        alert("Refresh rate limit exceeded. Please wait a few seconds before refreshing again.");
      } else {
        fetchBriefing(windowPreset);
      }
    } catch {
      // Ignore
    } finally {
      setRefreshing(false);
    }
  };

  const attentionEvents = data?.tiers.needs_attention || [];
  const lookEvents = data?.tiers.worth_a_look || [];
  const routineEvents = data?.tiers.routine || [];
  const summary = data?.summary;

  return (
    <div className="briefing-screen">
      {/* Header & Controls */}
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "baseline", marginBottom: "var(--space-3)", flexWrap: "wrap", gap: "8px" }}>
        <div>
          <h1 style={{ fontSize: "1.375rem", fontWeight: 700, color: "var(--ink)" }}>Portfolio Briefing</h1>
          <p style={{ fontSize: "0.8125rem", color: "var(--muted)" }}>
            18 monitored companies &bull; Mode: <strong>Live / IST</strong>
          </p>
        </div>

        <div style={{ display: "flex", gap: "var(--space-2)", alignItems: "center" }}>
          {/* Window Presets */}
          <div style={{ display: "flex", gap: "2px", background: "var(--surface-muted)", padding: "2px", borderRadius: "var(--radius-control)" }}>
            {(["24h", "7d", "custom"] as const).map((preset) => (
              <button
                key={preset}
                onClick={() => setWindowPreset(preset)}
                style={{
                  border: "none",
                  background: windowPreset === preset ? "var(--surface)" : "transparent",
                  color: windowPreset === preset ? "var(--ink)" : "var(--muted)",
                  fontWeight: windowPreset === preset ? 600 : 400,
                  fontSize: "0.75rem",
                  padding: "4px 8px",
                  borderRadius: "4px",
                  cursor: "pointer",
                }}
              >
                {preset === "24h" ? "Last 24h" : preset === "7d" ? "7 Days" : "Custom"}
              </button>
            ))}
          </div>

          {/* Refresh Action */}
          <button
            onClick={handleRefresh}
            disabled={refreshing}
            style={{
              background: "var(--surface)",
              border: "1px solid var(--line)",
              padding: "4px 10px",
              borderRadius: "var(--radius-control)",
              fontSize: "0.75rem",
              fontWeight: 600,
              cursor: refreshing ? "not-allowed" : "pointer",
              color: "var(--ink)",
            }}
          >
            {refreshing ? "Polling..." : "Refresh"}
          </button>
        </div>
      </div>

      {/* Summary Counts Bar (reconciling records) */}
      {summary && (
        <div style={{
          display: "flex",
          justifyContent: "space-between",
          background: "var(--surface)",
          padding: "8px 12px",
          borderRadius: "var(--radius-panel)",
          border: "1px solid var(--line)",
          marginBottom: "var(--space-4)",
          fontSize: "0.8125rem",
          color: "var(--muted)"
        }}>
          <span>Total Events: <strong>{summary.total_events}</strong></span>
          <span>Source Filings: <strong>{summary.total_source_filings}</strong></span>
          <span>Interval: <strong>{windowPreset === "24h" ? "Past 24 Hours" : windowPreset === "7d" ? "Past 7 Days" : "Custom Window"}</strong></span>
        </div>
      )}

      {loading && (
        <div style={{ padding: "var(--space-6) 0", textAlign: "center", color: "var(--muted)" }}>
          Loading live portfolio events...
        </div>
      )}

      {error && (
        <div style={{ padding: "var(--space-4)", background: "#FDF2F2", border: "1px solid #F8D7DA", borderRadius: "var(--radius-panel)", color: "var(--negative)", marginBottom: "var(--space-4)" }}>
          Failed to load briefing: {error}
        </div>
      )}

      {/* Empty State */}
      {!loading && !error && attentionEvents.length === 0 && lookEvents.length === 0 && routineEvents.length === 0 && (
        <div className="panel" style={{ textAlign: "center", padding: "var(--space-6) var(--space-4)" }}>
          <h3 style={{ fontSize: "1rem", fontWeight: 600, marginBottom: "4px" }}>No Material Events in Selected Window</h3>
          <p style={{ fontSize: "0.875rem", color: "var(--muted)", marginBottom: "var(--space-3)" }}>
            No corporate filings or price/volume threshold breaks occurred during this period.
          </p>
          <button
            onClick={() => setWindowPreset("7d")}
            style={{
              background: "var(--accent-soft)",
              color: "var(--accent)",
              border: "none",
              padding: "6px 14px",
              borderRadius: "var(--radius-control)",
              fontSize: "0.8125rem",
              fontWeight: 600,
              cursor: "pointer",
            }}
          >
            Expand to 7 Days
          </button>
        </div>
      )}

      {/* Tier 1: Needs Attention */}
      {attentionEvents.length > 0 && (
        <div className="panel" style={{ borderLeft: "4px solid var(--negative)" }}>
          <div className="panel-header">
            <div style={{ display: "flex", alignItems: "center", gap: "var(--space-2)" }}>
              <span className="panel-title">Needs Attention</span>
              <span className="badge badge-attention">{attentionEvents.length}</span>
            </div>
            <span style={{ fontSize: "0.75rem", color: "var(--muted)" }}>Prioritized by severity</span>
          </div>

          {attentionEvents.map((evt) => (
            <div key={evt.id} style={{ paddingBottom: "var(--space-3)", borderBottom: "1px solid var(--line)", marginBottom: "var(--space-3)" }}>
              <div style={{ display: "flex", justifyContent: "space-between", fontSize: "0.8125rem", color: "var(--muted)", marginBottom: "4px" }}>
                <strong>{evt.company_name} ({evt.symbol})</strong>
                <span>{evt.event_date}</span>
              </div>
              <h3 style={{ fontSize: "0.9375rem", fontWeight: 600, color: "var(--ink)", marginBottom: "4px" }}>
                {evt.headline}
              </h3>
              <p style={{ fontSize: "0.875rem", color: "var(--muted)", marginBottom: "8px" }}>
                {evt.implication}
              </p>
              <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
                <span className="badge badge-attention" style={{ fontSize: "0.6875rem" }}>{evt.kind.toUpperCase()}</span>
                <button
                  onClick={() => setSelectedEvidenceId("ev-preview-101")}
                  style={{
                    background: "var(--accent-soft)",
                    color: "var(--accent)",
                    border: "none",
                    padding: "6px 12px",
                    borderRadius: "var(--radius-control)",
                    fontSize: "0.8125rem",
                    fontWeight: 600,
                    cursor: "pointer",
                    minHeight: "36px",
                  }}
                >
                  Inspect Source &rarr;
                </button>
              </div>
            </div>
          ))}
        </div>
      )}

      {/* Tier 2: Worth a Look */}
      {lookEvents.length > 0 && (
        <div className="panel" style={{ borderLeft: "4px solid var(--warning)" }}>
          <div className="panel-header">
            <div style={{ display: "flex", alignItems: "center", gap: "var(--space-2)" }}>
              <span className="panel-title">Worth a Look</span>
              <span className="badge badge-worth-a-look">{lookEvents.length}</span>
            </div>
          </div>

          {lookEvents.map((evt) => (
            <div key={evt.id} style={{ paddingBottom: "var(--space-3)", borderBottom: "1px solid var(--line)", marginBottom: "var(--space-3)" }}>
              <div style={{ display: "flex", justifyContent: "space-between", fontSize: "0.8125rem", color: "var(--muted)", marginBottom: "4px" }}>
                <strong>{evt.company_name} ({evt.symbol})</strong>
                <span>{evt.event_date}</span>
              </div>
              <h3 style={{ fontSize: "0.9375rem", fontWeight: 600, color: "var(--ink)", marginBottom: "4px" }}>
                {evt.headline}
              </h3>
              <p style={{ fontSize: "0.875rem", color: "var(--muted)", marginBottom: "8px" }}>
                {evt.implication}
              </p>
              <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
                <span className="badge badge-worth-a-look" style={{ fontSize: "0.6875rem" }}>{evt.kind.toUpperCase()}</span>
                <button
                  onClick={() => setSelectedEvidenceId("ev-preview-101")}
                  style={{
                    background: "none",
                    color: "var(--accent)",
                    border: "1px solid var(--line)",
                    padding: "4px 10px",
                    borderRadius: "var(--radius-control)",
                    fontSize: "0.75rem",
                    fontWeight: 500,
                    cursor: "pointer",
                  }}
                >
                  View Filing
                </button>
              </div>
            </div>
          ))}
        </div>
      )}

      {/* Tier 3: Routine Filings */}
      {routineEvents.length > 0 && (
        <div className="panel">
          <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
            <div>
              <span className="panel-title" style={{ fontSize: "0.9375rem" }}>Routine Disclosures</span>
              <span className="badge badge-routine" style={{ marginLeft: "8px" }}>{routineEvents.length}</span>
            </div>
            <button
              onClick={() => setExpandRoutine(!expandRoutine)}
              style={{
                background: "none",
                border: "none",
                color: "var(--accent)",
                fontSize: "0.8125rem",
                fontWeight: 600,
                cursor: "pointer",
                padding: "4px 8px",
              }}
            >
              {expandRoutine ? "Collapse" : "Expand All"}
            </button>
          </div>

          {expandRoutine && (
            <div style={{ marginTop: "var(--space-3)", borderTop: "1px solid var(--line)", paddingTop: "var(--space-3)" }}>
              {routineEvents.map((evt) => (
                <div key={evt.id} style={{ display: "flex", justifyContent: "space-between", fontSize: "0.8125rem", padding: "6px 0", borderBottom: "1px solid var(--line)" }}>
                  <span>{evt.company_name} &mdash; {evt.headline}</span>
                  <span style={{ color: "var(--muted)" }}>{evt.event_date}</span>
                </div>
              ))}
            </div>
          )}
        </div>
      )}

      {selectedEvidenceId && (
        <EvidenceDrawer
          evidenceId={selectedEvidenceId}
          onClose={() => setSelectedEvidenceId(null)}
        />
      )}
    </div>
  );
}
