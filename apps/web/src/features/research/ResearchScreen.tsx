import { useState } from "react";
import EvidenceDrawer from "../../components/evidence/EvidenceDrawer";

interface GuidanceRow {
  targetPeriod: string;
  stated: string;
  reported: string;
  assessment: "met" | "exceeded" | "missed" | "not_due" | "not_comparable";
  evidenceId: string;
}

const SYNTHETIC_LEDGER_FIXTURES: GuidanceRow[] = [
  {
    targetPeriod: "Q1 FY25",
    stated: "CC revenue growth 1.0% to 3.0% YoY; operating margin 20% to 22% (stated Apr 2024)",
    reported: "CC revenue growth +2.5% YoY; operating margin 21.1%",
    assessment: "met",
    evidenceId: "ev-preview-101",
  },
  {
    targetPeriod: "Q2 FY25",
    stated: "FY25 CC revenue guidance revised upward to 3.0%–4.0% YoY (stated Jul 2024)",
    reported: "CC revenue growth +3.8% YoY; operating margin 21.3%",
    assessment: "met",
    evidenceId: "ev-preview-104",
  },
  {
    targetPeriod: "Q3 FY25",
    stated: "FY25 CC revenue guidance maintained at 3.75%–4.50% (stated Oct 2024)",
    reported: "CC revenue growth +4.2% YoY; operating margin 21.0%",
    assessment: "met",
    evidenceId: "ev-preview-105",
  },
  {
    targetPeriod: "Q4 FY25",
    stated: "Full-year CC revenue target 4.5%–5.0% YoY; margin target 21.0% (stated Jan 2025)",
    reported: "Pending final audited filings / due Apr 2025",
    assessment: "not_due",
    evidenceId: "ev-preview-106",
  },
];

export default function ResearchScreen() {
  const [tickerQuery, setTickerQuery] = useState("INFY");
  const [selectedEvidenceId, setSelectedEvidenceId] = useState<string | null>(null);

  const getAssessmentBadge = (assessment: GuidanceRow["assessment"]) => {
    switch (assessment) {
      case "met":
      case "exceeded":
        return <span className="badge" style={{ background: "#E8F5E9", color: "var(--positive)", border: "1px solid #C8E6C9" }}>MET</span>;
      case "missed":
        return <span className="badge badge-attention">MISSED</span>;
      case "not_due":
        return <span className="badge" style={{ background: "var(--surface-muted)", color: "var(--muted)" }}>NOT YET DUE</span>;
      default:
        return <span className="badge badge-routine">{assessment}</span>;
    }
  };

  return (
    <div className="research-screen">
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
        <span><strong>T01 Shell Preview:</strong> Displaying labeled synthetic guidance ledger fixture.</span>
        <span className="badge badge-synthetic">SYNTHETIC FIXTURE</span>
      </div>

      {/* Search Header */}
      <div className="panel" style={{ padding: "var(--space-3) var(--space-4)" }}>
        <label htmlFor="company-search" style={{ fontSize: "0.75rem", fontWeight: 600, color: "var(--muted)", textTransform: "uppercase" }}>
          Primary-Source Research Desk
        </label>
        <div style={{ display: "flex", gap: "var(--space-2)", marginTop: "4px" }}>
          <input
            id="company-search"
            type="text"
            value={tickerQuery}
            onChange={(e) => setTickerQuery(e.target.value)}
            placeholder="Enter NSE Symbol (e.g. INFY, TCS, HCLTECH)..."
            style={{
              flex: 1,
              padding: "10px 12px",
              border: "1px solid var(--control-border)",
              borderRadius: "var(--radius-control)",
              fontSize: "0.9375rem",
              background: "var(--surface)",
            }}
          />
          <button
            style={{
              background: "var(--accent)",
              color: "#FFF",
              border: "none",
              padding: "0 16px",
              borderRadius: "var(--radius-control)",
              fontWeight: 600,
              fontSize: "0.875rem",
              cursor: "pointer",
              minHeight: "var(--min-touch-target)",
            }}
          >
            Research
          </button>
        </div>
      </div>

      {/* Company Header & Source Coverage */}
      <div className="panel" style={{ background: "var(--surface)" }}>
        <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start", marginBottom: "var(--space-2)" }}>
          <div>
            <h2 style={{ fontSize: "1.25rem", fontWeight: 700, color: "var(--ink)" }}>Infosys Limited (INFY)</h2>
            <p style={{ fontSize: "0.8125rem", color: "var(--muted)" }}>
              NSE: INFY &bull; BSE: 500209 &bull; ISIN: INE009A01021
            </p>
          </div>
          <span className="badge" style={{ background: "var(--accent-soft)", color: "var(--accent)" }}>
            As-of: Q3 FY25
          </span>
        </div>

        <div style={{ display: "flex", gap: "var(--space-2)", flexWrap: "wrap", fontSize: "0.75rem", color: "var(--muted)", paddingTop: "var(--space-2)", borderTop: "1px solid var(--line)" }}>
          <span>Primary Corpus: <strong>Annual Report FY24 + 4 Earnings Transcripts</strong></span>
          <span>&bull;</span>
          <span>Dual Citations: <strong>Active</strong></span>
        </div>
      </div>

      {/* Signature Feature: Promises & Outcomes Guidance Ledger */}
      <div className="panel">
        <div className="panel-header">
          <div>
            <h3 className="panel-title" style={{ fontSize: "1.0625rem" }}>
              Management Guidance Ledger (4 Quarters)
            </h3>
            <p style={{ fontSize: "0.8125rem", color: "var(--muted)" }}>
              Evaluating stated targets against audited results in deterministic code.
            </p>
          </div>
        </div>

        <div style={{ display: "flex", flexDirection: "column", gap: "var(--space-3)" }}>
          {SYNTHETIC_LEDGER_FIXTURES.map((row) => (
            <div
              key={row.targetPeriod}
              style={{
                border: "1px solid var(--line)",
                borderRadius: "var(--radius-control)",
                padding: "var(--space-3)",
                background: "var(--surface)",
              }}
            >
              <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "6px" }}>
                <strong style={{ fontSize: "0.875rem", color: "var(--ink)" }}>{row.targetPeriod}</strong>
                {getAssessmentBadge(row.assessment)}
              </div>

              {/* Stated */}
              <div style={{ fontSize: "0.8125rem", marginBottom: "6px" }}>
                <span style={{ color: "var(--muted)", fontWeight: 600, display: "inline-block", width: "70px" }}>Stated:</span>
                <span style={{ color: "var(--ink)" }}>{row.stated}</span>
              </div>

              {/* Reported */}
              <div style={{ fontSize: "0.8125rem", marginBottom: "8px" }}>
                <span style={{ color: "var(--muted)", fontWeight: 600, display: "inline-block", width: "70px" }}>Reported:</span>
                <span style={{ color: "var(--ink)", fontWeight: 500 }}>{row.reported}</span>
              </div>

              <div style={{ display: "flex", justifyContent: "flex-end" }}>
                <button
                  onClick={() => setSelectedEvidenceId(row.evidenceId)}
                  style={{
                    background: "none",
                    border: "none",
                    color: "var(--accent)",
                    fontSize: "0.8125rem",
                    fontWeight: 600,
                    cursor: "pointer",
                    padding: "4px 0",
                  }}
                >
                  Inspect Dual Evidence &rarr;
                </button>
              </div>
            </div>
          ))}
        </div>
      </div>

      {selectedEvidenceId && (
        <EvidenceDrawer
          evidenceId={selectedEvidenceId}
          onClose={() => setSelectedEvidenceId(null)}
        />
      )}
    </div>
  );
}
