import { useState, useEffect, FormEvent } from "react";
import EvidenceDrawer from "../../components/evidence/EvidenceDrawer";

interface GuidanceRow {
  target_period: string;
  metric_label: string;
  stated_summary: string;
  stated_evidence_id: string;
  reported_summary: string;
  reported_evidence_id?: string | null;
  assessment: "met" | "exceeded" | "missed" | "not_due" | "not_comparable" | "qualitative_supported" | "withdrawn";
  explanation: string;
  is_revised?: boolean;
  original_target?: string | null;
}

interface OverviewFact {
  label: string;
  value: string;
  growth: string;
  evidence_id: string;
  citation_num: number;
  excerpt: string;
}

interface SourceDocument {
  document_id: string;
  title: string;
  source_type: string;
  publisher: string;
  published_at_utc: string;
  fiscal_period?: string;
  page_count: number;
  source_url?: string;
}

interface ResearchReport {
  status: string;
  company: {
    id: string;
    symbol: string;
    legal_name: string;
    isin: string;
    sector: string;
  };
  as_of_date: string;
  stages: Array<{ stage: string; label: string; status: string }>;
  overview_facts: OverviewFact[];
  guidance_ledger: GuidanceRow[];
  source_coverage: SourceDocument[];
  limitations: string[];
}

interface BoundedAnswer {
  question: string;
  answer: string;
  evidence_citations: Array<{ citation_num: number; evidence_id: string; label: string }>;
  limitation: string;
}

export default function ResearchScreen() {
  const [tickerQuery, setTickerQuery] = useState("INFY");
  const [activeTab, setActiveTab] = useState<"overview" | "ledger" | "sources">("ledger");
  const [selectedEvidenceId, setSelectedEvidenceId] = useState<string | null>(null);

  const [loading, setLoading] = useState(false);
  const [currentStage, setCurrentStage] = useState<string | null>(null);
  const [report, setReport] = useState<ResearchReport | null>(null);
  const [errorMsg, setErrorMsg] = useState<string | null>(null);

  // Bounded question state
  const [questionInput, setQuestionInput] = useState("");
  const [askingQuestion, setAskingQuestion] = useState(false);
  const [questionResult, setQuestionResult] = useState<BoundedAnswer | null>(null);

  const loadResearch = async (symbol: string) => {
    setLoading(true);
    setErrorMsg(null);
    setQuestionResult(null);

    // Simulate visible progressive pipeline stages for user feedback
    setCurrentStage("Finding primary annual reports & transcripts...");
    try {
      const resp = await fetch(`/api/v1/research/${encodeURIComponent(symbol)}`);
      if (!resp.ok) {
        if (resp.status === 404) {
          setErrorMsg(`Company '${symbol}' not found in candidate master. Please try INFY, HCLTECH, TCS, or RELIANCE.`);
        } else {
          setErrorMsg(`Research error: HTTP ${resp.status}`);
        }
        setReport(null);
        return;
      }
      const data: ResearchReport = await resp.json();
      setReport(data);
    } catch {
      setErrorMsg("Network error connecting to FINN Research API.");
      setReport(null);
    } finally {
      setLoading(false);
      setCurrentStage(null);
    }
  };

  useEffect(() => {
    loadResearch("INFY");
  }, []);

  const handleSearchSubmit = (e: FormEvent) => {
    e.preventDefault();
    if (tickerQuery.trim()) {
      loadResearch(tickerQuery.trim());
    }
  };

  const handleAskQuestion = async (qText: string) => {
    if (!report || !qText.trim()) return;
    setAskingQuestion(true);
    try {
      const resp = await fetch(`/api/v1/research/${encodeURIComponent(report.company.symbol)}/ask`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ question: qText })
      });
      if (resp.ok) {
        const data: BoundedAnswer = await resp.json();
        setQuestionResult(data);
      }
    } catch {
      // Ignored
    } finally {
      setAskingQuestion(false);
    }
  };

  const getAssessmentBadge = (assessment: GuidanceRow["assessment"]) => {
    switch (assessment) {
      case "met":
      case "exceeded":
        return <span className="badge" style={{ background: "#E8F5E9", color: "#2E7D32", border: "1px solid #C8E6C9", fontWeight: 700 }}>MET</span>;
      case "missed":
        return <span className="badge badge-attention" style={{ fontWeight: 700 }}>MISSED</span>;
      case "not_due":
        return <span className="badge" style={{ background: "var(--surface-muted)", color: "var(--muted)", fontWeight: 600 }}>NOT YET DUE</span>;
      case "qualitative_supported":
        return <span className="badge" style={{ background: "#E0F2F1", color: "#00695C", fontWeight: 600 }}>QUALITATIVE</span>;
      case "withdrawn":
        return <span className="badge" style={{ background: "#FFEBEE", color: "#C62828", fontWeight: 600 }}>WITHDRAWN</span>;
      default:
        return <span className="badge badge-routine">{assessment}</span>;
    }
  };

  return (
    <div className="research-screen" style={{ display: "flex", flexDirection: "column", gap: "var(--space-4)" }}>
      {/* Search Header */}
      <div className="panel" style={{ padding: "var(--space-4)" }}>
        <label htmlFor="company-search" style={{ fontSize: "0.75rem", fontWeight: 700, color: "var(--muted)", textTransform: "uppercase", letterSpacing: "0.05em" }}>
          Primary-Source Research Desk
        </label>
        <form onSubmit={handleSearchSubmit} style={{ display: "flex", gap: "var(--space-2)", marginTop: "6px" }}>
          <input
            id="company-search"
            type="text"
            value={tickerQuery}
            onChange={(e) => setTickerQuery(e.target.value)}
            placeholder="Enter NSE Symbol or ISIN (e.g. INFY, HCLTECH, TCS)..."
            style={{
              flex: 1,
              padding: "10px 14px",
              border: "1px solid var(--control-border)",
              borderRadius: "var(--radius-control)",
              fontSize: "0.9375rem",
              background: "var(--surface)",
              minHeight: "44px"
            }}
          />
          <button
            type="submit"
            className="btn btn-primary"
            style={{ minHeight: "44px", padding: "0 18px", fontWeight: 600 }}
            disabled={loading}
          >
            {loading ? "Searching..." : "Research"}
          </button>
        </form>

        {/* Quick Suggestion Chips */}
        <div style={{ display: "flex", gap: "6px", marginTop: "10px", alignItems: "center", flexWrap: "wrap" }}>
          <span style={{ fontSize: "0.75rem", color: "var(--muted)" }}>Quick view:</span>
          {["INFY", "HCLTECH", "TCS", "RELIANCE"].map((sym) => (
            <button
              key={sym}
              type="button"
              onClick={() => {
                setTickerQuery(sym);
                loadResearch(sym);
              }}
              style={{
                background: "var(--surface-muted)",
                border: "1px solid var(--control-border)",
                borderRadius: "12px",
                padding: "2px 10px",
                fontSize: "0.75rem",
                fontWeight: 600,
                cursor: "pointer",
                color: "var(--foreground)"
              }}
            >
              {sym}
            </button>
          ))}
        </div>
      </div>

      {/* Loading Progress State */}
      {loading && (
        <div className="panel" style={{ padding: "var(--space-4)", textAlign: "center" }}>
          <div style={{ fontWeight: 600, color: "var(--primary)", marginBottom: "8px" }}>
            {currentStage || "Analyzing Primary Filings..."}
          </div>
          <div style={{ display: "flex", justifyContent: "center", gap: "12px", fontSize: "0.8125rem", color: "var(--muted)" }}>
            <span>✓ Finding reports</span>
            <span>✓ Reading sources</span>
            <span>• Checking figures</span>
            <span>• Preparing ledger</span>
          </div>
        </div>
      )}

      {/* Error state */}
      {errorMsg && (
        <div className="panel" style={{ padding: "var(--space-4)", background: "#FFEBEE", border: "1px solid #FFCDD2", color: "#C62828" }}>
          <strong>Error: </strong> {errorMsg}
        </div>
      )}

      {/* Main Report View */}
      {report && !loading && (
        <>
          {/* Company Identity & Coverage Summary Card */}
          <div className="panel" style={{ padding: "var(--space-4)" }}>
            <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start", flexWrap: "wrap", gap: "8px" }}>
              <div>
                <h2 style={{ fontSize: "1.25rem", fontWeight: 700, margin: 0, color: "var(--foreground)" }}>
                  {report.company.legal_name}
                </h2>
                <div style={{ fontSize: "0.8125rem", color: "var(--muted)", marginTop: "4px" }}>
                  <span>NSE: <strong>{report.company.symbol}</strong></span> • <span>ISIN: {report.company.isin}</span> • <span>{report.company.sector}</span>
                </div>
              </div>
              <div style={{ textAlign: "right" }}>
                <span className="badge badge-routine" style={{ fontSize: "0.75rem" }}>
                  As of: {report.as_of_date}
                </span>
                <div style={{ fontSize: "0.75rem", color: "var(--muted)", marginTop: "4px" }}>
                  Source: Annual Reports + Transcripts
                </div>
              </div>
            </div>

            {/* Sub-Navigation Tabs */}
            <div style={{ display: "flex", gap: "8px", borderBottom: "1px solid var(--control-border)", marginTop: "16px", paddingBottom: "8px" }}>
              <button
                type="button"
                onClick={() => setActiveTab("ledger")}
                style={{
                  background: activeTab === "ledger" ? "var(--primary)" : "transparent",
                  color: activeTab === "ledger" ? "#fff" : "var(--foreground)",
                  border: "none",
                  padding: "6px 14px",
                  borderRadius: "var(--radius-control)",
                  fontSize: "0.8125rem",
                  fontWeight: 600,
                  cursor: "pointer",
                  minHeight: "36px"
                }}
              >
                Promises & Outcomes (4Q Ledger)
              </button>
              <button
                type="button"
                onClick={() => setActiveTab("overview")}
                style={{
                  background: activeTab === "overview" ? "var(--primary)" : "transparent",
                  color: activeTab === "overview" ? "#fff" : "var(--foreground)",
                  border: "none",
                  padding: "6px 14px",
                  borderRadius: "var(--radius-control)",
                  fontSize: "0.8125rem",
                  fontWeight: 600,
                  cursor: "pointer",
                  minHeight: "36px"
                }}
              >
                Overview Facts
              </button>
              <button
                type="button"
                onClick={() => setActiveTab("sources")}
                style={{
                  background: activeTab === "sources" ? "var(--primary)" : "transparent",
                  color: activeTab === "sources" ? "#fff" : "var(--foreground)",
                  border: "none",
                  padding: "6px 14px",
                  borderRadius: "var(--radius-control)",
                  fontSize: "0.8125rem",
                  fontWeight: 600,
                  cursor: "pointer",
                  minHeight: "36px"
                }}
              >
                Primary Sources ({report.source_coverage.length})
              </button>
            </div>
          </div>

          {/* TAB 1: GUIDANCE LEDGER (SIGNATURE FEATURE) */}
          {activeTab === "ledger" && (
            <div style={{ display: "flex", flexDirection: "column", gap: "var(--space-3)" }}>
              <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
                <h3 style={{ fontSize: "1rem", fontWeight: 700, margin: 0 }}>
                  4-Quarter Management Guidance Ledger
                </h3>
                <span style={{ fontSize: "0.75rem", color: "var(--muted)" }}>
                  Pure primary transcript & results audit
                </span>
              </div>

              {report.guidance_ledger.length === 0 ? (
                <div className="panel" style={{ padding: "var(--space-4)", textAlign: "center", color: "var(--muted)" }}>
                  No guidance ledger records for this company yet. Guidance extraction runs against official earnings call transcripts.
                </div>
              ) : (
                report.guidance_ledger.map((row) => (
                  <div
                    key={row.target_period}
                    className="panel"
                    style={{
                      padding: "var(--space-4)",
                      display: "flex",
                      flexDirection: "column",
                      gap: "var(--space-3)",
                      borderLeft: `4px solid ${
                        row.assessment === "met" || row.assessment === "exceeded"
                          ? "#2E7D32"
                          : row.assessment === "missed"
                          ? "#C62828"
                          : "var(--control-border)"
                      }`
                    }}
                  >
                    {/* Period & Verdict Header */}
                    <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", flexWrap: "wrap", gap: "8px" }}>
                      <div style={{ display: "flex", alignItems: "center", gap: "8px" }}>
                        <span style={{ fontSize: "1rem", fontWeight: 700, color: "var(--foreground)" }}>
                          {row.target_period}
                        </span>
                        <span style={{ fontSize: "0.8125rem", color: "var(--muted)" }}>
                          ({row.metric_label})
                        </span>
                        {row.is_revised && (
                          <span className="badge" style={{ background: "#FFF3E0", color: "#E65100", fontSize: "0.7rem", fontWeight: 600 }}>
                            REVISED TARGET
                          </span>
                        )}
                      </div>
                      <div>{getAssessmentBadge(row.assessment)}</div>
                    </div>

                    {/* Stated vs Reported Comparison */}
                    <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(280px, 1fr))", gap: "12px", background: "var(--surface-muted)", padding: "12px", borderRadius: "var(--radius-control)" }}>
                      <div>
                        <div style={{ fontSize: "0.75rem", fontWeight: 700, color: "var(--muted)", textTransform: "uppercase" }}>
                          Stated Guidance
                        </div>
                        <div style={{ fontSize: "0.875rem", marginTop: "4px", lineHeight: 1.4 }}>
                          {row.stated_summary}
                        </div>
                        {row.is_revised && row.original_target && (
                          <div style={{ fontSize: "0.75rem", color: "#E65100", marginTop: "4px", fontStyle: "italic" }}>
                            {row.original_target}
                          </div>
                        )}
                        <button
                          type="button"
                          className="btn btn-secondary"
                          onClick={() => setSelectedEvidenceId(row.stated_evidence_id)}
                          style={{
                            marginTop: "8px",
                            fontSize: "0.75rem",
                            padding: "4px 10px",
                            minHeight: "36px"
                          }}
                        >
                          Inspect Stated Evidence [1]
                        </button>
                      </div>

                      <div>
                        <div style={{ fontSize: "0.75rem", fontWeight: 700, color: "var(--muted)", textTransform: "uppercase" }}>
                          Reported Outcome
                        </div>
                        <div style={{ fontSize: "0.875rem", marginTop: "4px", lineHeight: 1.4 }}>
                          {row.reported_summary}
                        </div>
                        {row.reported_evidence_id ? (
                          <button
                            type="button"
                            className="btn btn-secondary"
                            onClick={() => setSelectedEvidenceId(row.reported_evidence_id!)}
                            style={{
                              marginTop: "8px",
                              fontSize: "0.75rem",
                              padding: "4px 10px",
                              minHeight: "36px"
                            }}
                          >
                            Inspect Reported Evidence [2]
                          </button>
                        ) : (
                          <div style={{ fontSize: "0.75rem", color: "var(--muted)", marginTop: "12px" }}>
                            <em>Audited outcome pending future board meeting release</em>
                          </div>
                        )}
                      </div>
                    </div>

                    {/* Deterministic Explanation */}
                    <div style={{ fontSize: "0.8125rem", color: "var(--foreground)", borderTop: "1px dashed var(--control-border)", paddingTop: "8px", lineHeight: 1.4 }}>
                      <strong>Assessment verdict:</strong> {row.explanation}
                    </div>
                  </div>
                ))
              )}
            </div>
          )}

          {/* TAB 2: OVERVIEW FACTS */}
          {activeTab === "overview" && (
            <div style={{ display: "flex", flexDirection: "column", gap: "var(--space-3)" }}>
              <h3 style={{ fontSize: "1rem", fontWeight: 700, margin: 0 }}>
                Compact Source-Linked Facts
              </h3>
              <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(260px, 1fr))", gap: "12px" }}>
                {report.overview_facts.map((fact) => (
                  <div key={fact.citation_num} className="panel" style={{ padding: "var(--space-3) var(--space-4)" }}>
                    <div style={{ fontSize: "0.75rem", color: "var(--muted)", fontWeight: 600, textTransform: "uppercase" }}>
                      {fact.label}
                    </div>
                    <div style={{ fontSize: "1.5rem", fontWeight: 700, color: "var(--foreground)", margin: "4px 0" }}>
                      {fact.value}
                    </div>
                    <div style={{ fontSize: "0.8125rem", color: "var(--primary)", fontWeight: 600 }}>
                      {fact.growth}
                    </div>
                    <button
                      type="button"
                      className="btn btn-secondary"
                      onClick={() => setSelectedEvidenceId(fact.evidence_id)}
                      style={{ marginTop: "8px", fontSize: "0.75rem", padding: "4px 8px", minHeight: "34px" }}
                    >
                      Cite Fact [{fact.citation_num}]
                    </button>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* TAB 3: PRIMARY SOURCES */}
          {activeTab === "sources" && (
            <div style={{ display: "flex", flexDirection: "column", gap: "var(--space-3)" }}>
              <h3 style={{ fontSize: "1rem", fontWeight: 700, margin: 0 }}>
                Primary Source Filings & Transcripts ({report.source_coverage.length})
              </h3>
              {report.source_coverage.map((doc) => (
                <div key={doc.document_id} className="panel" style={{ padding: "var(--space-3) var(--space-4)" }}>
                  <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start", gap: "8px" }}>
                    <div>
                      <div style={{ fontWeight: 600, fontSize: "0.875rem" }}>{doc.title}</div>
                      <div style={{ fontSize: "0.75rem", color: "var(--muted)", marginTop: "2px" }}>
                        Publisher: {doc.publisher} • Pages: {doc.page_count} • Date: {doc.published_at_utc ? doc.published_at_utc.substring(0, 10) : "N/A"}
                      </div>
                    </div>
                    <span className="badge badge-routine" style={{ fontSize: "0.7rem" }}>
                      {doc.source_type}
                    </span>
                  </div>
                  {doc.source_url && (
                    <div style={{ marginTop: "6px" }}>
                      <a
                        href={doc.source_url}
                        target="_blank"
                        rel="noreferrer"
                        style={{ fontSize: "0.75rem", color: "var(--primary)", wordBreak: "break-all" }}
                      >
                        View Official Filing Document ↗
                      </a>
                    </div>
                  )}
                </div>
              ))}
            </div>
          )}

          {/* Ask a Focused Question Section (T10 Bounded Questions) */}
          <div className="panel" style={{ padding: "var(--space-4)", display: "flex", flexDirection: "column", gap: "var(--space-3)" }}>
            <h3 style={{ fontSize: "0.9375rem", fontWeight: 700, margin: 0 }}>
              Ask a Focused Question About {report.company.symbol}
            </h3>
            <p style={{ fontSize: "0.8125rem", color: "var(--muted)", margin: 0 }}>
              Answers are strictly grounded in primary annual reports and earnings transcripts. Speculation and ungrounded prose are rejected.
            </p>

            {/* Suggested Question Chips */}
            <div style={{ display: "flex", gap: "6px", flexWrap: "wrap" }}>
              {[
                "What changed in guidance?",
                "Did cash track profit?",
                "What evidence challenges the growth story?"
              ].map((suggestion) => (
                <button
                  key={suggestion}
                  type="button"
                  onClick={() => {
                    setQuestionInput(suggestion);
                    handleAskQuestion(suggestion);
                  }}
                  style={{
                    background: "var(--surface-muted)",
                    border: "1px solid var(--control-border)",
                    borderRadius: "16px",
                    padding: "4px 12px",
                    fontSize: "0.75rem",
                    fontWeight: 500,
                    cursor: "pointer",
                    color: "var(--foreground)"
                  }}
                >
                  💬 {suggestion}
                </button>
              ))}
            </div>

            <div style={{ display: "flex", gap: "8px" }}>
              <input
                type="text"
                value={questionInput}
                onChange={(e) => setQuestionInput(e.target.value)}
                placeholder="Ask about guidance revisions, margins, or cash flows..."
                style={{
                  flex: 1,
                  padding: "8px 12px",
                  borderRadius: "var(--radius-control)",
                  border: "1px solid var(--control-border)",
                  fontSize: "0.875rem",
                  minHeight: "44px"
                }}
              />
              <button
                type="button"
                className="btn btn-primary"
                onClick={() => handleAskQuestion(questionInput)}
                disabled={askingQuestion || !questionInput.trim()}
                style={{ minHeight: "44px", padding: "0 16px" }}
              >
                {askingQuestion ? "Analyzing..." : "Ask"}
              </button>
            </div>

            {/* Bounded Question Result Box */}
            {questionResult && (
              <div style={{ background: "var(--surface-muted)", padding: "14px", borderRadius: "var(--radius-control)", borderLeft: "4px solid var(--primary)", marginTop: "4px" }}>
                <div style={{ fontWeight: 600, fontSize: "0.875rem", marginBottom: "6px" }}>
                  Q: {questionResult.question}
                </div>
                <div style={{ fontSize: "0.875rem", lineHeight: 1.5, color: "var(--foreground)" }}>
                  {questionResult.answer}
                </div>

                {/* Evidence citations */}
                {questionResult.evidence_citations.length > 0 && (
                  <div style={{ display: "flex", gap: "8px", marginTop: "10px", alignItems: "center", flexWrap: "wrap" }}>
                    <span style={{ fontSize: "0.75rem", fontWeight: 700, color: "var(--muted)" }}>Citations:</span>
                    {questionResult.evidence_citations.map((c) => (
                      <button
                        key={c.evidence_id}
                        type="button"
                        className="btn btn-secondary"
                        onClick={() => setSelectedEvidenceId(c.evidence_id)}
                        style={{ fontSize: "0.75rem", padding: "2px 8px", minHeight: "32px" }}
                      >
                        [{c.citation_num}] {c.label}
                      </button>
                    ))}
                  </div>
                )}

                {/* Supported Limitation */}
                <div style={{ fontSize: "0.75rem", color: "var(--muted)", marginTop: "8px", fontStyle: "italic" }}>
                  <strong>Limitation:</strong> {questionResult.limitation}
                </div>
              </div>
            )}
          </div>

          {/* Transparent Source Limitations Banner */}
          <div className="panel" style={{ padding: "var(--space-3) var(--space-4)", background: "#FFFDE7", border: "1px solid #FFF59D" }}>
            <div style={{ fontSize: "0.75rem", fontWeight: 700, color: "#F57F17", textTransform: "uppercase", marginBottom: "4px" }}>
              Verified Source Grounding & Data Boundaries
            </div>
            <ul style={{ margin: 0, paddingLeft: "18px", fontSize: "0.75rem", color: "#5D4037", lineHeight: 1.5 }}>
              {report.limitations.map((lim, idx) => (
                <li key={idx}>{lim}</li>
              ))}
            </ul>
          </div>
        </>
      )}

      {/* Shared Accessible Evidence Drawer */}
      {selectedEvidenceId && (
        <EvidenceDrawer
          evidenceId={selectedEvidenceId}
          onClose={() => setSelectedEvidenceId(null)}
        />
      )}
    </div>
  );
}
