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
  const [tab, setTab] = useState<"sources" | "facts" | "ledger">("facts");
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
        setTab(next.overview_facts.length ? "facts" : next.guidance_ledger.length ? "ledger" : "sources");
        window.history.replaceState(null, "", `#/research?symbol=${encodeURIComponent(next.company.symbol)}`);
      }
    } catch (err) {
      if (err instanceof DOMException && err.name === "AbortError") return;
      setError(err instanceof Error ? err.message : "Research is temporarily unavailable.");
    } finally {
      if (!controller.signal.aborted) setLoading(false);
    }
  };

  useEffect(() => {
    const requested = new URLSearchParams(window.location.hash.split("?")[1] || "").get("symbol");
    load(requested || "INFY");
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
        <h1 className="screen-title">Research desk</h1>
        <p className="screen-subtitle">
          Company facts and management guidance, with the primary source behind each claim.
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

        <div className="research-switcher" aria-label="Quick company switcher">
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

            <div className="research-coverage-line">
              {report.source_coverage.length} primary sources · {report.overview_facts.length} verified facts · {report.guidance_ledger.length} guidance statements
            </div>
          </section>

          {/* Bounded free-form research */}
          <section className="panel">
            <div className="panel-header">
              <span className="panel-title">Ask the filings</span>
              <span className="badge badge-routine">Source-backed</span>
            </div>

            <p className="research-help">Ask your own question. FINN searches indexed issuer evidence and shows the exact passage it used.</p>
            <div className="research-suggestions" aria-label="Example questions">
              {[
                "What revenue did the company report?",
                "What guidance did management give?",
                "What did management say about cash conversion?",
              ].map((prompt) => (
                <button className="research-suggestion" key={prompt} onClick={() => triggerPrompt(prompt)} disabled={asking}>
                  {prompt}
                </button>
              ))}
            </div>

            <div className="field">
              <label htmlFor="research-question">Focused question</label>
              <input
                id="research-question"
                value={question}
                onChange={(e) => setQuestion(e.target.value)}
                placeholder="Ask anything about this issuer’s indexed sources"
                onKeyDown={(event) => { if (event.key === "Enter") ask(); }}
              />
            </div>
            <button className="button research-ask" onClick={() => ask()} disabled={asking || !question.trim()}>
              {asking ? "Searching evidence…" : "Find answer"}
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


          {/* Revolut Segmented Tabs */}
          <div className="segmented" style={{ marginBottom: 16 }}>
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
                        ? "Page-level evidence available"
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
                    No management statement has been verified for this issuer. A reported outcome is assessed separately when the target period closes.
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
                        {row.assessment.replaceAll("_", " ")}
                      </span>
                    </div>
                    <h3>{row.stated_summary}</h3>
                    <p>{row.explanation}</p>
                    <div className="event-actions">
                      <span />
                      <button className="button secondary" onClick={() => setEvidenceId(row.stated_evidence_id)}>
                        Inspect statement
                      </button>
                    </div>
                  </article>
                ))
              )}
            </section>
          )}

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
