import { useState } from "react";
import EvidenceDrawer from "../../components/evidence/EvidenceDrawer";

interface BriefingEvent {
  id: string;
  companyName: string;
  symbol: string;
  publishedAt: string;
  headline: string;
  implication: string;
  tier: "needs_attention" | "worth_a_look" | "routine";
  category: string;
  evidenceId: string;
}

// Explicitly labeled synthetic UI fixtures for T01 shell preview
const SYNTHETIC_BRIEFING_FIXTURES: BriefingEvent[] = [
  {
    id: "evt-preview-1",
    companyName: "Infosys Limited",
    symbol: "INFY",
    publishedAt: "Today, 14:44 IST",
    headline: "FY25 Guidance Reiterated at 1%–3% CC Revenue Growth",
    implication: "Operating margin guidance held at 20%–22%; constant currency guidance intact despite discretionary headwinds.",
    tier: "needs_attention",
    category: "Guidance & Results",
    evidenceId: "ev-preview-101",
  },
  {
    id: "evt-preview-2",
    companyName: "HCL Technologies Limited",
    symbol: "HCLTECH",
    publishedAt: "Today, 12:15 IST",
    headline: "Services Revenue Up 1.6% QoQ; Full-Year Forecast Maintained",
    implication: "CC revenue growth tracking within guided range; software division seasonal softness offset by engineering services.",
    tier: "worth_a_look",
    category: "Results / Press Release",
    evidenceId: "ev-preview-102",
  },
  {
    id: "evt-preview-3",
    companyName: "Tata Consultancy Services",
    symbol: "TCS",
    publishedAt: "Yesterday, 18:30 IST",
    headline: "Outcome of Board Meeting: Interim Dividend Declared",
    implication: "Statutory declaration of dividend payable November 2026; record date fixed.",
    tier: "routine",
    category: "Dividend / AGM",
    evidenceId: "ev-preview-103",
  },
];

export default function BriefingScreen() {
  const [windowPreset, setWindowPreset] = useState<"24h" | "7d" | "custom">("24h");
  const [selectedEvidenceId, setSelectedEvidenceId] = useState<string | null>(null);
  const [expandRoutine, setExpandRoutine] = useState(false);

  const attentionEvents = SYNTHETIC_BRIEFING_FIXTURES.filter((e) => e.tier === "needs_attention");
  const lookEvents = SYNTHETIC_BRIEFING_FIXTURES.filter((e) => e.tier === "worth_a_look");
  const routineEvents = SYNTHETIC_BRIEFING_FIXTURES.filter((e) => e.tier === "routine");

  return (
    <div className="briefing-screen">
      {/* Synthetic fixture banner */}
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
        <span><strong>T01 Shell Preview:</strong> Displaying labeled synthetic fixtures.</span>
        <span className="badge badge-synthetic">SYNTHETIC FIXTURE</span>
      </div>

      {/* Briefing Header & Window Filter */}
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "baseline", marginBottom: "var(--space-3)" }}>
        <div>
          <h1 style={{ fontSize: "1.375rem", fontWeight: 700, color: "var(--ink)" }}>Portfolio Briefing</h1>
          <p style={{ fontSize: "0.8125rem", color: "var(--muted)" }}>
            18 monitored companies &bull; Mode: <strong>Live / IST</strong>
          </p>
        </div>

        {/* Window Presets */}
        <div style={{ display: "flex", gap: "4px", background: "var(--surface-muted)", padding: "2px", borderRadius: "var(--radius-control)" }}>
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
      </div>

      {/* Section: Needs Attention */}
      <div className="panel" style={{ borderLeft: "4px solid var(--negative)" }}>
        <div className="panel-header">
          <div style={{ display: "flex", alignItems: "center", gap: "var(--space-2)" }}>
            <span className="panel-title">Needs Attention</span>
            <span className="badge badge-attention">{attentionEvents.length}</span>
          </div>
          <span style={{ fontSize: "0.75rem", color: "var(--muted)" }}>Prioritized by severity</span>
        </div>

        {attentionEvents.map((evt) => (
          <div key={evt.id} style={{ paddingBottom: "var(--space-3)", borderBottom: "1px solid var(--line)" }}>
            <div style={{ display: "flex", justifyContent: "space-between", fontSize: "0.8125rem", color: "var(--muted)", marginBottom: "4px" }}>
              <strong>{evt.companyName} ({evt.symbol})</strong>
              <span>{evt.publishedAt}</span>
            </div>
            <h3 style={{ fontSize: "0.9375rem", fontWeight: 600, color: "var(--ink)", marginBottom: "4px" }}>
              {evt.headline}
            </h3>
            <p style={{ fontSize: "0.875rem", color: "var(--muted)", marginBottom: "8px" }}>
              {evt.implication}
            </p>
            <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
              <span className="badge badge-attention" style={{ fontSize: "0.6875rem" }}>{evt.category}</span>
              <button
                onClick={() => setSelectedEvidenceId(evt.evidenceId)}
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

      {/* Section: Worth a Look */}
      <div className="panel" style={{ borderLeft: "4px solid var(--warning)" }}>
        <div className="panel-header">
          <div style={{ display: "flex", alignItems: "center", gap: "var(--space-2)" }}>
            <span className="panel-title">Worth a Look</span>
            <span className="badge badge-worth-a-look">{lookEvents.length}</span>
          </div>
        </div>

        {lookEvents.map((evt) => (
          <div key={evt.id} style={{ paddingBottom: "var(--space-3)" }}>
            <div style={{ display: "flex", justifyContent: "space-between", fontSize: "0.8125rem", color: "var(--muted)", marginBottom: "4px" }}>
              <strong>{evt.companyName} ({evt.symbol})</strong>
              <span>{evt.publishedAt}</span>
            </div>
            <h3 style={{ fontSize: "0.9375rem", fontWeight: 600, color: "var(--ink)", marginBottom: "4px" }}>
              {evt.headline}
            </h3>
            <p style={{ fontSize: "0.875rem", color: "var(--muted)", marginBottom: "8px" }}>
              {evt.implication}
            </p>
            <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
              <span className="badge badge-worth-a-look" style={{ fontSize: "0.6875rem" }}>{evt.category}</span>
              <button
                onClick={() => setSelectedEvidenceId(evt.evidenceId)}
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

      {/* Section: Routine Filings */}
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
              <div key={evt.id} style={{ display: "flex", justifyContent: "space-between", fontSize: "0.8125rem", padding: "6px 0" }}>
                <span>{evt.companyName} &mdash; {evt.headline}</span>
                <span style={{ color: "var(--muted)" }}>{evt.publishedAt}</span>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Shared Evidence Drawer Modal / Sheet */}
      {selectedEvidenceId && (
        <EvidenceDrawer
          evidenceId={selectedEvidenceId}
          onClose={() => setSelectedEvidenceId(null)}
        />
      )}
    </div>
  );
}
