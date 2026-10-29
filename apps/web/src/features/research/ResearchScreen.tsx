import { FormEvent, useEffect, useRef, useState } from "react";
import EvidenceDrawer from "../../components/evidence/EvidenceDrawer";

interface GuidanceRow {
  target_period: string;
  metric_label: string;
  stated_summary: string;
  stated_evidence_id: string;
  reported_summary: string;
  reported_evidence_id?: string | null;
  assessment: string;
  explanation: string;
}

interface Fact {
  label: string;
  value: string;
  growth: string;
  evidence_id: string;
  citation_num: number;
}

interface Source {
  document_id: string;
  title: string;
  source_type: string;
  publisher: string;
  published_at_utc: string;
  fiscal_period?: string;
  page_count: number;
  source_url?: string;
  status?: string;
}

interface Fundamentals {
  business_snapshot?: {
    summary: string;
    core_offerings?: string[];
    segments: Array<{ name: string; share_pct: number; growth?: string }>;
    geographies?: Array<{ region: string; share_pct: number }>;
  };
  financial_snapshot?: {
    headline_period: string;
    revenue: { value: string; growth_yoy: string; growth_qoq?: string; evidence_id?: string };
    operating_margin: { value: string; delta_yoy: string; target_corridor?: string; evidence_id?: string };
    net_profit: { value: string; growth_yoy: string; growth_qoq?: string; evidence_id?: string };
    free_cash_flow?: { value: string; conversion_rate?: string; evidence_id?: string };
    key_ratios?: Array<{ name: string; value: string }>;
  };
  trajectory?: {
    direction: string;
    growth_drivers: Array<{ vector: string; detail: string }>;
    compression_drags: Array<{ segment: string; detail: string }>;
  };
  balance_sheet?: {
    net_cash_debt: { value: string; status: string; label: string };
    leverage_ratio: { value: string; label: string };
    working_capital_dso: { value: string; label: string };
    capital_allocation: string;
  };
  cash_quality?: {
    verdict: string;
    operating_cash_flow: string;
    free_cash_flow: string;
    conversion_ratio: string;
    working_capital_drag: string;
  };
  narrative_vs_numbers?: Array<{
    quarter: string;
    management_narrative: string;
    actual_reported: string;
    verdict: string;
    analysis: string;
  }>;
  bull_vs_bear?: {
    bull_thesis: Array<{ point: string; detail: string }>;
    bear_thesis: Array<{ point: string; detail: string }>;
  };
}

interface Report {
  status: string;
  company: {
    id: string;
    symbol: string;
    legal_name: string;
    isin: string;
    sector: string;
  };
  as_of_date: string;
  stages: Array<{ label: string; status: string }>;
  overview_facts: Fact[];
  guidance_ledger: GuidanceRow[];
  source_coverage: Source[];
  modules?: Fundamentals;
  limitations: string[];
}

interface Answer {
  question: string;
  answer: string;
  evidence_citations: Array<{ evidence_id: string; label: string }>;
  limitation: string;
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

export default function ResearchScreen() {
  const [query, setQuery] = useState("INFY");
  const [report, setReport] = useState<Report | null>(null);
  const [tab, setTab] = useState<"sources" | "facts" | "ledger" | "analysis">("sources");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [evidenceId, setEvidenceId] = useState<string | null>(null);
  const [question, setQuestion] = useState("");
  const [answer, setAnswer] = useState<Answer | null>(null);
  const [asking, setAsking] = useState(false);
  const activeRequest = useRef<AbortController | null>(null);

  const load = async (symbol: string) => {
    activeRequest.current?.abort();
    const controller = new AbortController();
    activeRequest.current = controller;
    setLoading(true);
    setError(null);
    setReport(null);
    setAnswer(null);
    try {
      const response = await fetch(`/api/v1/research/${encodeURIComponent(symbol)}`, {
        signal: controller.signal,
      });
      if (!response.ok) {
        throw new Error(
          response.status === 404
            ? `No listed company matched “${symbol}”.`
            : `Research request failed (${response.status}).`
        );
      }
      const next: Report = await response.json();
      if (!controller.signal.aborted) {
        setReport(next);
        setQuery(next.company.symbol);
        setTab("sources");
      }
    } catch (err) {
      if (err instanceof DOMException && err.name === "AbortError") return;
      setError(err instanceof Error ? err.message : "Research is temporarily unavailable.");
    } finally {
      if (!controller.signal.aborted) setLoading(false);
    }
  };

  useEffect(() => {
    load("INFY");
    return () => activeRequest.current?.abort();
  }, []);

  const submit = (event: FormEvent) => {
    event.preventDefault();
    if (query.trim()) load(query.trim());
  };

  const ask = async (customQuestion?: string) => {
    const q = customQuestion || question;
    if (!report || !q.trim()) return;
    setAsking(true);
    setAnswer(null);
    try {
      const response = await fetch(
        `/api/v1/research/${encodeURIComponent(report.company.symbol)}/ask`,
        {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ question: q }),
        }
      );
      if (!response.ok) throw new Error();
      setAnswer(await response.json());
    } catch {
      setError("The evidence search could not be completed.");
    } finally {
      setAsking(false);
    }
  };

  const triggerPrompt = (promptText: string) => {
    setQuestion(promptText);
    ask(promptText);
  };

  return (
    <div className="research-screen">
      <header className="screen-heading">
        <div className="screen-kicker">Primary research</div>
        <h1 className="screen-title">Follow the evidence.</h1>
        <p className="screen-subtitle">
          Official issuer sources first. Claims appear only when FINN can point to an inspectable page excerpt.
        </p>
      </header>

      {/* Search & Fast Switcher */}
      <section className="panel">
        <form onSubmit={submit} style={{ display: "flex", gap: 10 }}>
          <div className="field" style={{ flex: 1 }}>
            <label htmlFor="company-search">Company, NSE symbol or ISIN</label>
            <input
              id="company-search"
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              placeholder="e.g. INFY, TCS, RELIANCE, COFORGE"
              autoCapitalize="characters"
            />
          </div>
          <button className="button" type="submit" disabled={loading} style={{ alignSelf: "end" }}>
            {loading ? "Checking…" : "Research"}
          </button>
        </form>

        <div style={{ display: "flex", flexWrap: "wrap", gap: 7, marginTop: 12 }}>
          {["INFY", "TCS", "HCLTECH", "RELIANCE", "COFORGE", "DIXON", "ASTRAL"].map((symbol) => (
            <button
              className={`button secondary ${report?.company.symbol === symbol ? "active" : ""}`}
              style={{
                minHeight: 34,
                padding: "0 14px",
                fontSize: 12,
                borderRadius: "var(--radius-pill)",
              }}
              disabled={loading}
              key={symbol}
              onClick={() => {
                setQuery(symbol);
                load(symbol);
              }}
            >
              {symbol}
            </button>
          ))}
        </div>
      </section>

      {loading && (
        <div className="panel empty-state">
          <p>Resolving issuer identity and analyzing primary source disclosures…</p>
        </div>
      )}
      {error && <div className="notice error-notice" role="alert">{error}</div>}

      {report && (
        <>
          {/* Company Profile Header */}
          <section className="panel">
            <div style={{ display: "flex", gap: 14, alignItems: "center" }}>
              <div className={`company-avatar ${getAvatarClass(report.company.symbol)}`} style={{ width: 48, height: 48, fontSize: 16 }}>
                {report.company.symbol.slice(0, 2).toUpperCase()}
              </div>
              <div style={{ flex: 1, minWidth: 0 }}>
                <div className="event-meta">
                  <span className="badge badge-routine">{report.company.sector}</span>
                  <span>As of {report.as_of_date}</span>
                </div>
                <h2 style={{ fontSize: 24, letterSpacing: "-0.03em", marginTop: 4 }}>
                  {report.company.legal_name}
                </h2>
                <p style={{ color: "var(--muted)", fontSize: 13, marginTop: 2 }}>
                  {report.company.symbol} · {report.company.isin}
                </p>
              </div>
            </div>

            {/* Pipeline Stages Progress Bar */}
            <div style={{ display: "grid", gridTemplateColumns: "repeat(4, 1fr)", gap: 6, marginTop: 16 }}>
              {report.stages.map((stage) => (
                <div
                  key={stage.label}
                  style={{
                    minHeight: 5,
                    borderRadius: 99,
                    background: stage.status === "completed" ? "var(--positive)" : "var(--surface-muted)",
                  }}
                  title={`${stage.label}: ${stage.status}`}
                />
              ))}
            </div>
          </section>

          {/* Revolut Segmented Tabs */}
          <div className="segmented" style={{ marginBottom: 16 }}>
            {report.modules && (
              <button
                className={tab === "analysis" ? "active" : ""}
                onClick={() => setTab("analysis")}
              >
                Analysis · 8 Modules
              </button>
            )}
            <button
              className={tab === "sources" ? "active" : ""}
              onClick={() => setTab("sources")}
            >
              Sources · {report.source_coverage.length}
            </button>
            <button
              className={tab === "facts" ? "active" : ""}
              onClick={() => setTab("facts")}
            >
              Facts · {report.overview_facts.length}
            </button>
            <button
              className={tab === "ledger" ? "active" : ""}
              onClick={() => setTab("ledger")}
            >
              Guidance · {report.guidance_ledger.length}
            </button>
          </div>

          {/* TAB: 8-Module Fundamental Analysis Suite */}
          {tab === "analysis" && report.modules && (
            <div>
              {/* 1. Business Snapshot */}
              {report.modules.business_snapshot && (
                <section className="panel">
                  <div className="panel-header">
                    <span className="panel-title">1. Business Snapshot & Revenue Mix</span>
                    <span className="badge badge-routine">Segments</span>
                  </div>
                  <p style={{ color: "var(--ink)", fontSize: 14, lineHeight: 1.5, marginBottom: 12 }}>
                    {report.modules.business_snapshot.summary}
                  </p>
                  <div className="module-grid">
                    <div className="module-card">
                      <div className="module-card-title">Operating Segments (% Revenue)</div>
                      <div className="chip-row">
                        {report.modules.business_snapshot.segments.map((seg) => (
                          <span className="chip" key={seg.name}>
                            {seg.name}: <strong>{seg.share_pct}%</strong>
                            {seg.growth && <span style={{ color: seg.growth.startsWith("+") ? "var(--positive)" : "var(--negative)", marginLeft: 4 }}>{seg.growth}</span>}
                          </span>
                        ))}
                      </div>
                    </div>
                    {report.modules.business_snapshot.geographies && (
                      <div className="module-card">
                        <div className="module-card-title">Geographic Distribution</div>
                        <div className="chip-row">
                          {report.modules.business_snapshot.geographies.map((geo) => (
                            <span className="chip" key={geo.region}>
                              {geo.region}: <strong>{geo.share_pct}%</strong>
                            </span>
                          ))}
                        </div>
                      </div>
                    )}
                  </div>
                </section>
              )}

              {/* 2. Financial Snapshot */}
              {report.modules.financial_snapshot && (
                <section className="panel">
                  <div className="panel-header">
                    <span className="panel-title">2. Financial Snapshot ({report.modules.financial_snapshot.headline_period})</span>
                    <span className="badge badge-positive">Audited Numbers</span>
                  </div>
                  <div className="summary-strip">
                    <div className="summary-stat">
                      <span>Revenue</span>
                      <strong>{report.modules.financial_snapshot.revenue.value}</strong>
                      <span style={{ color: "var(--positive)" }}>{report.modules.financial_snapshot.revenue.growth_yoy} YoY</span>
                    </div>
                    <div className="summary-stat">
                      <span>Operating Margin</span>
                      <strong>{report.modules.financial_snapshot.operating_margin.value}</strong>
                      <span>{report.modules.financial_snapshot.operating_margin.delta_yoy} YoY</span>
                    </div>
                    <div className="summary-stat">
                      <span>Net Profit (PAT)</span>
                      <strong>{report.modules.financial_snapshot.net_profit.value}</strong>
                      <span style={{ color: "var(--positive)" }}>{report.modules.financial_snapshot.net_profit.growth_yoy} YoY</span>
                    </div>
                  </div>
                  {report.modules.financial_snapshot.key_ratios && (
                    <div className="chip-row" style={{ marginTop: 10 }}>
                      {report.modules.financial_snapshot.key_ratios.map((kr) => (
                        <span className="chip" key={kr.name}>
                          {kr.name}: <strong>{kr.value}</strong>
                        </span>
                      ))}
                    </div>
                  )}
                </section>
              )}

              {/* 3. Trajectory */}
              {report.modules.trajectory && (
                <section className="panel">
                  <div className="panel-header">
                    <span className="panel-title">3. Trajectory: Growth vs. Compression</span>
                    <span className="badge badge-routine">Multi-Year Direction</span>
                  </div>
                  <p style={{ fontSize: 13.5, color: "var(--muted)", marginBottom: 12 }}>
                    {report.modules.trajectory.direction}
                  </p>
                  <div className="module-grid">
                    <div className="module-card">
                      <div className="module-card-title" style={{ color: "var(--positive)" }}>
                        <span>▲ Secular Growth Vectors</span>
                      </div>
                      {report.modules.trajectory.growth_drivers.map((gd) => (
                        <div key={gd.vector} style={{ marginBottom: 8, fontSize: 13 }}>
                          <strong>{gd.vector}:</strong> {gd.detail}
                        </div>
                      ))}
                    </div>
                    <div className="module-card">
                      <div className="module-card-title" style={{ color: "var(--negative)" }}>
                        <span>▼ Compression Drags</span>
                      </div>
                      {report.modules.trajectory.compression_drags.map((cd) => (
                        <div key={cd.segment} style={{ marginBottom: 8, fontSize: 13 }}>
                          <strong>{cd.segment}:</strong> {cd.detail}
                        </div>
                      ))}
                    </div>
                  </div>
                </section>
              )}

              {/* 4. Balance Sheet & 5. Cash Quality */}
              <div className="module-grid" style={{ marginBottom: 14 }}>
                {report.modules.balance_sheet && (
                  <section className="panel" style={{ marginBottom: 0 }}>
                    <div className="panel-header">
                      <span className="panel-title">4. Balance Sheet & Leverage</span>
                      <span className="badge badge-positive">{report.modules.balance_sheet.net_cash_debt.status}</span>
                    </div>
                    <h3 style={{ fontSize: 24, fontWeight: 800 }}>{report.modules.balance_sheet.net_cash_debt.value}</h3>
                    <p style={{ color: "var(--muted)", fontSize: 12.5, margin: "4px 0 10px" }}>
                      {report.modules.balance_sheet.net_cash_debt.label}
                    </p>
                    <div className="chip-row">
                      <span className="chip">DSO: <strong>{report.modules.balance_sheet.working_capital_dso.value}</strong></span>
                      <span className="chip">Leverage: <strong>{report.modules.balance_sheet.leverage_ratio.value}</strong></span>
                    </div>
                    <p style={{ fontSize: 12, color: "var(--muted)", marginTop: 10 }}>
                      <strong>Capital Allocation:</strong> {report.modules.balance_sheet.capital_allocation}
                    </p>
                  </section>
                )}

                {report.modules.cash_quality && (
                  <section className="panel" style={{ marginBottom: 0 }}>
                    <div className="panel-header">
                      <span className="panel-title">5. Cash Quality</span>
                      <span className="badge badge-positive">Cash Conversion</span>
                    </div>
                    <div style={{ fontSize: 15, fontWeight: 700, color: "var(--positive)", marginBottom: 8 }}>
                      {report.modules.cash_quality.verdict}
                    </div>
                    <div style={{ fontSize: 13, lineHeight: 1.6 }}>
                      <div>• <strong>Operating Cash Flow:</strong> {report.modules.cash_quality.operating_cash_flow}</div>
                      <div>• <strong>Free Cash Flow:</strong> {report.modules.cash_quality.free_cash_flow}</div>
                      <div>• <strong>Conversion Metric:</strong> {report.modules.cash_quality.conversion_ratio}</div>
                      <div>• <strong>Working Capital:</strong> {report.modules.cash_quality.working_capital_drag}</div>
                    </div>
                  </section>
                )}
              </div>

              {/* 6. Narrative vs. Numbers Worked Example */}
              {report.modules.narrative_vs_numbers && (
                <section className="panel">
                  <div className="panel-header">
                    <span className="panel-title">6. Narrative vs. Numbers (Worked Example)</span>
                    <span className="badge badge-routine">4-Quarter Audit</span>
                  </div>
                  <p style={{ fontSize: 13, color: "var(--muted)", marginBottom: 14 }}>
                    Comparing management promises from earnings call transcripts against reported statutory financial numbers.
                  </p>
                  {report.modules.narrative_vs_numbers.map((row) => (
                    <article className="event-card" key={row.quarter}>
                      <div className="event-meta">
                        <strong>{row.quarter}</strong>
                        <span
                          className={`badge ${
                            row.verdict === "met" || row.verdict === "exceeded"
                              ? "badge-positive"
                              : row.verdict === "missed"
                              ? "badge-attention"
                              : "badge-routine"
                          }`}
                        >
                          {row.verdict.toUpperCase()}
                        </span>
                      </div>
                      <h3 style={{ fontSize: 14.5 }}>Promised: {row.management_narrative}</h3>
                      <p style={{ color: "var(--ink)" }}><strong>Delivered:</strong> {row.actual_reported}</p>
                      <div className="event-actions">
                        <span style={{ fontSize: 12, color: "var(--muted)" }}>{row.analysis}</span>
                      </div>
                    </article>
                  ))}
                </section>
              )}

              {/* 8. Bull vs. Bear Case */}
              {report.modules.bull_vs_bear && (
                <section className="panel">
                  <div className="panel-header">
                    <span className="panel-title">8. Bull vs. Bear Case</span>
                    <span className="badge badge-routine">High Conviction</span>
                  </div>
                  <div className="module-grid">
                    <div className="module-card">
                      <div className="module-card-title" style={{ color: "var(--positive)" }}>
                        <span>🐂 The Bull Thesis</span>
                      </div>
                      {report.modules.bull_vs_bear.bull_thesis.map((b) => (
                        <div key={b.point} style={{ marginBottom: 10, fontSize: 13 }}>
                          <strong>{b.point}:</strong> {b.detail}
                        </div>
                      ))}
                    </div>
                    <div className="module-card">
                      <div className="module-card-title" style={{ color: "var(--negative)" }}>
                        <span>🐻 The Bear Thesis</span>
                      </div>
                      {report.modules.bull_vs_bear.bear_thesis.map((b) => (
                        <div key={b.point} style={{ marginBottom: 10, fontSize: 13 }}>
                          <strong>{b.point}:</strong> {b.detail}
                        </div>
                      ))}
                    </div>
                  </div>
                </section>
              )}
            </div>
          )}

          {/* TAB: Sources */}
          {tab === "sources" && (
            <section className="panel">
              <div className="panel-header">
                <span className="panel-title">Official source library</span>
                <span className="badge badge-routine">Issuer domains</span>
              </div>
              {report.source_coverage.length === 0 ? (
                <div className="empty-state">
                  <p>No official source has been registered for this issuer yet.</p>
                </div>
              ) : (
                report.source_coverage.map((source) => (
                  <article className="event-card" key={source.document_id}>
                    <div className="event-meta">
                      <strong>{source.publisher}</strong>
                      <span>{source.fiscal_period || source.published_at_utc?.slice(0, 10)}</span>
                    </div>
                    <h3>{source.title}</h3>
                    <p>
                      {source.page_count
                        ? `${source.page_count} indexed pages`
                        : "Official link registered · page extraction pending"}
                    </p>
                    <div className="event-actions">
                      <span className="badge badge-routine">{source.source_type.replaceAll("_", " ")}</span>
                      {source.source_url && (
                        <a className="source-link" href={source.source_url} target="_blank" rel="noreferrer">
                          Open official source ↗
                        </a>
                      )}
                    </div>
                  </article>
                ))
              )}
            </section>
          )}

          {/* TAB: Facts */}
          {tab === "facts" && (
            <section className="panel">
              <div className="panel-header">
                <span className="panel-title">Verified financial facts</span>
              </div>
              {report.overview_facts.length === 0 ? (
                <div className="empty-state">
                  <h3>No verified page facts yet</h3>
                  <p>
                    FINN found official sources but will not turn link metadata into financial claims. This avoids invented figures and citations.
                  </p>
                </div>
              ) : (
                report.overview_facts.map((fact) => (
                  <article className="event-card" key={fact.evidence_id}>
                    <div className="event-meta">
                      <strong>{fact.label}</strong>
                      <span>{fact.growth}</span>
                    </div>
                    <h3 style={{ fontSize: 24, fontVariantNumeric: "tabular-nums" }}>{fact.value}</h3>
                    <div className="event-actions">
                      <span />
                      <button className="button secondary" onClick={() => setEvidenceId(fact.evidence_id)}>
                        Inspect evidence
                      </button>
                    </div>
                  </article>
                ))
              )}
            </section>
          )}

          {/* TAB: Guidance Ledger */}
          {tab === "ledger" && (
            <section className="panel">
              <div className="panel-header">
                <span className="panel-title">Management guidance ledger</span>
              </div>
              {report.guidance_ledger.length === 0 ? (
                <div className="empty-state">
                  <h3>No evidence-paired guidance yet</h3>
                  <p>
                    A ledger row needs both the management statement and a comparable reported outcome. FINN leaves this empty until both citations are verified.
                  </p>
                </div>
              ) : (
                report.guidance_ledger.map((row) => (
                  <article className="event-card" key={`${row.target_period}-${row.metric_label}`}>
                    <div className="event-meta">
                      <strong>{row.target_period} · {row.metric_label}</strong>
                      <span
                        className={`badge ${
                          row.assessment === "met" || row.assessment === "exceeded"
                            ? "badge-positive"
                            : row.assessment === "missed"
                            ? "badge-attention"
                            : "badge-routine"
                        }`}
                      >
                        {row.assessment}
                      </span>
                    </div>
                    <h3>{row.stated_summary}</h3>
                    <p>{row.reported_summary}</p>
                    <div className="event-actions">
                      <span>{row.explanation}</span>
                      <button className="button secondary" onClick={() => setEvidenceId(row.stated_evidence_id)}>
                        Inspect statement
                      </button>
                    </div>
                  </article>
                ))
              )}
            </section>
          )}

          {/* Revolut Ask on Demand / Quick Dig-In */}
          <section className="panel">
            <div className="panel-header">
              <span className="panel-title">Ask on Demand / Dig In</span>
              <span className="badge badge-routine">Evidence Gated</span>
            </div>

            {/* Quick Prompt Suggestion Pills */}
            <div className="chip-row" style={{ marginBottom: 12 }}>
              <button
                className="chip"
                style={{ cursor: "pointer", background: "var(--surface-muted)" }}
                onClick={() => triggerPrompt("What is the narrative vs numbers delivery across quarters?")}
              >
                📊 Narrative vs Numbers
              </button>
              <button
                className="chip"
                style={{ cursor: "pointer", background: "var(--surface-muted)" }}
                onClick={() => triggerPrompt("What is the cash quality and FCF conversion?")}
              >
                💰 Cash Quality
              </button>
              <button
                className="chip"
                style={{ cursor: "pointer", background: "var(--surface-muted)" }}
                onClick={() => triggerPrompt("What is the multi-year trajectory and compression?")}
              >
                📈 Trajectory
              </button>
              <button
                className="chip"
                style={{ cursor: "pointer", background: "var(--surface-muted)" }}
                onClick={() => triggerPrompt("What is the balance sheet leverage and working capital DSO?")}
              >
                ⚖️ Balance Sheet
              </button>
              <button
                className="chip"
                style={{ cursor: "pointer", background: "var(--surface-muted)" }}
                onClick={() => triggerPrompt("What is the bull vs bear thesis?")}
              >
                🐂 Bull vs Bear
              </button>
            </div>

            <div className="field">
              <label htmlFor="research-question">Focused question</label>
              <input
                id="research-question"
                value={question}
                onChange={(e) => setQuestion(e.target.value)}
                placeholder="What changed in management guidance?"
              />
            </div>
            <button
              className="button"
              style={{ width: "100%", marginTop: 10 }}
              onClick={() => ask()}
              disabled={asking || !question.trim()}
            >
              {asking ? "Searching excerpts…" : "Ask"}
            </button>

            {answer && (
              <div className="notice" style={{ marginTop: 14, marginBottom: 0 }}>
                <strong>{answer.answer}</strong>
                <p style={{ marginTop: 7, color: "var(--muted)", fontSize: 12.5 }}>
                  {answer.limitation}
                </p>
                {answer.evidence_citations.map((c) => (
                  <button
                    key={c.evidence_id}
                    className="button secondary"
                    style={{ marginTop: 10, fontSize: 12, minHeight: 34 }}
                    onClick={() => setEvidenceId(c.evidence_id)}
                  >
                    {c.label}
                  </button>
                ))}
              </div>
            )}
          </section>

          {/* Coverage Limits */}
          <section className="panel">
            <div className="panel-header">
              <span className="panel-title">Coverage limits</span>
            </div>
            {report.limitations.map((item) => (
              <p key={item} style={{ color: "var(--muted)", fontSize: 13, marginTop: 8 }}>
                • {item}
              </p>
            ))}
          </section>
        </>
      )}

      {evidenceId && (
        <EvidenceDrawer evidenceId={evidenceId} onClose={() => setEvidenceId(null)} />
      )}
    </div>
  );
}
