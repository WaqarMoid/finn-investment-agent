import { FormEvent, useEffect, useRef, useState } from "react";
import EvidenceDrawer from "../../components/evidence/EvidenceDrawer";

interface GuidanceRow { target_period: string; metric_label: string; stated_summary: string; stated_evidence_id: string; reported_summary: string; reported_evidence_id?: string | null; assessment: string; explanation: string; }
interface Fact { label: string; value: string; growth: string; evidence_id: string; citation_num: number; }
interface Source { document_id: string; title: string; source_type: string; publisher: string; published_at_utc: string; fiscal_period?: string; page_count: number; source_url?: string; status?: string; }
interface Report { status: string; company: { id: string; symbol: string; legal_name: string; isin: string; sector: string }; as_of_date: string; stages: Array<{ label: string; status: string }>; overview_facts: Fact[]; guidance_ledger: GuidanceRow[]; source_coverage: Source[]; limitations: string[]; }
interface Answer { question: string; answer: string; evidence_citations: Array<{ evidence_id: string; label: string }>; limitation: string; }

export default function ResearchScreen() {
  const [query, setQuery] = useState("INFY");
  const [report, setReport] = useState<Report | null>(null);
  const [tab, setTab] = useState<"ledger" | "facts" | "sources">("sources");
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
    setLoading(true); setError(null); setReport(null); setAnswer(null);
    try {
      const response = await fetch(`/api/v1/research/${encodeURIComponent(symbol)}`, { signal: controller.signal });
      if (!response.ok) throw new Error(response.status === 404 ? `No listed company matched “${symbol}”.` : `Research request failed (${response.status}).`);
      const next: Report = await response.json();
      if (!controller.signal.aborted) { setReport(next); setQuery(next.company.symbol); setTab("sources"); }
    } catch (err) {
      if (err instanceof DOMException && err.name === "AbortError") return;
      setError(err instanceof Error ? err.message : "Research is temporarily unavailable.");
    } finally { if (!controller.signal.aborted) setLoading(false); }
  };

  useEffect(() => { load("INFY"); return () => activeRequest.current?.abort(); }, []);
  const submit = (event: FormEvent) => { event.preventDefault(); if (query.trim()) load(query.trim()); };
  const ask = async () => {
    if (!report || !question.trim()) return;
    setAsking(true); setAnswer(null);
    try {
      const response = await fetch(`/api/v1/research/${encodeURIComponent(report.company.symbol)}/ask`, { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ question }) });
      if (!response.ok) throw new Error();
      setAnswer(await response.json());
    } catch { setError("The evidence search could not be completed."); }
    finally { setAsking(false); }
  };

  return <div className="research-screen">
    <header className="screen-heading"><div className="screen-kicker">Primary research</div><h1 className="screen-title">Follow the evidence.</h1><p className="screen-subtitle">Official issuer sources first. Claims appear only when FINN can point to an inspectable page excerpt.</p></header>
    <section className="panel">
      <form onSubmit={submit} style={{ display: "flex", gap: 10 }}>
        <div className="field" style={{ flex: 1 }}><label htmlFor="company-search">Company, NSE symbol or ISIN</label><input id="company-search" value={query} onChange={e => setQuery(e.target.value)} placeholder="INFY" autoCapitalize="characters" /></div>
        <button className="button" type="submit" disabled={loading} style={{ alignSelf: "end" }}>{loading ? "Checking…" : "Research"}</button>
      </form>
      <div style={{ display: "flex", flexWrap: "wrap", gap: 7, marginTop: 12 }}>
        {['INFY','HCLTECH','TCS','RELIANCE'].map(symbol => <button className="button secondary" style={{ minHeight: 36, padding: '0 12px', fontSize: 12 }} disabled={loading} key={symbol} onClick={() => { setQuery(symbol); load(symbol); }}>{symbol}</button>)}
      </div>
    </section>
    {loading && <div className="panel empty-state"><p>Resolving the issuer and checking indexed primary sources…</p></div>}
    {error && <div className="notice error-notice" role="alert">{error}</div>}

    {report && <>
      <section className="panel">
        <div className="event-meta"><span>{report.company.sector}</span><span>As of {report.as_of_date}</span></div>
        <h2 style={{ fontSize: 26, letterSpacing: '-.03em', marginTop: 8 }}>{report.company.legal_name}</h2>
        <p style={{ color: 'var(--muted)', marginTop: 4 }}>{report.company.symbol} · {report.company.isin}</p>
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(4,1fr)', gap: 6, marginTop: 16 }}>
          {report.stages.map(stage => <div key={stage.label} style={{ minHeight: 5, borderRadius: 99, background: stage.status === 'completed' ? 'var(--positive)' : 'var(--surface-muted)' }} title={`${stage.label}: ${stage.status}`} />)}
        </div>
      </section>

      <div className="segmented" style={{ marginBottom: 16 }}>
        <button className={tab === 'sources' ? 'active' : ''} onClick={() => setTab('sources')}>Sources · {report.source_coverage.length}</button>
        <button className={tab === 'facts' ? 'active' : ''} onClick={() => setTab('facts')}>Facts · {report.overview_facts.length}</button>
        <button className={tab === 'ledger' ? 'active' : ''} onClick={() => setTab('ledger')}>Guidance · {report.guidance_ledger.length}</button>
      </div>

      {tab === 'sources' && <section className="panel">
        <div className="panel-header"><span className="panel-title">Official source library</span><span className="badge badge-routine">Issuer domains</span></div>
        {report.source_coverage.length === 0 ? <div className="empty-state"><p>No official source has been registered for this issuer yet.</p></div> : report.source_coverage.map(source => <article className="event-card" key={source.document_id}>
          <div className="event-meta"><strong>{source.publisher}</strong><span>{source.fiscal_period || source.published_at_utc?.slice(0,10)}</span></div>
          <h3>{source.title}</h3><p>{source.page_count ? `${source.page_count} indexed pages` : 'Official link registered · page extraction pending'}</p>
          <div className="event-actions"><span className="badge badge-routine">{source.source_type.replaceAll('_',' ')}</span>{source.source_url && <a className="source-link" href={source.source_url} target="_blank" rel="noreferrer">Open official source ↗</a>}</div>
        </article>)}
      </section>}

      {tab === 'facts' && <section className="panel"><div className="panel-header"><span className="panel-title">Verified financial facts</span></div>
        {report.overview_facts.length === 0 ? <div className="empty-state"><h3>No verified page facts yet</h3><p>FINN found official sources but will not turn link metadata into financial claims. This avoids invented figures and citations.</p></div> : report.overview_facts.map(fact => <article className="event-card" key={fact.evidence_id}><div className="event-meta"><strong>{fact.label}</strong><span>{fact.growth}</span></div><h3 style={{ fontSize: 25 }}>{fact.value}</h3><div className="event-actions"><span /><button className="button secondary" onClick={() => setEvidenceId(fact.evidence_id)}>Inspect evidence</button></div></article>)}
      </section>}

      {tab === 'ledger' && <section className="panel"><div className="panel-header"><span className="panel-title">Management guidance ledger</span></div>
        {report.guidance_ledger.length === 0 ? <div className="empty-state"><h3>No evidence-paired guidance yet</h3><p>A ledger row needs both the management statement and a comparable reported outcome. FINN leaves this empty until both citations are verified.</p></div> : report.guidance_ledger.map(row => <article className="event-card" key={`${row.target_period}-${row.metric_label}`}><div className="event-meta"><strong>{row.target_period} · {row.metric_label}</strong><span className="badge badge-routine">{row.assessment}</span></div><h3>{row.stated_summary}</h3><p>{row.reported_summary}</p><div className="event-actions"><span>{row.explanation}</span><button className="button secondary" onClick={() => setEvidenceId(row.stated_evidence_id)}>Inspect statement</button></div></article>)}
      </section>}

      <section className="panel"><div className="panel-header"><span className="panel-title">Ask the indexed evidence</span></div><div className="field"><label htmlFor="research-question">Focused question</label><input id="research-question" value={question} onChange={e => setQuestion(e.target.value)} placeholder="What changed in management guidance?" /></div><button className="button" style={{ width: '100%', marginTop: 10 }} onClick={ask} disabled={asking || !question.trim()}>{asking ? 'Searching excerpts…' : 'Ask'}</button>
        {answer && <div className="notice" style={{ marginTop: 14, marginBottom: 0 }}><strong>{answer.answer}</strong><p style={{ marginTop: 7, color: 'var(--muted)' }}>{answer.limitation}</p>{answer.evidence_citations.map(c => <button key={c.evidence_id} className="button secondary" style={{ marginTop: 10 }} onClick={() => setEvidenceId(c.evidence_id)}>{c.label}</button>)}</div>}
      </section>
      <section className="panel"><div className="panel-header"><span className="panel-title">Coverage limits</span></div>{report.limitations.map(item => <p key={item} style={{ color: 'var(--muted)', fontSize: 13, marginTop: 8 }}>• {item}</p>)}</section>
    </>}
    {evidenceId && <EvidenceDrawer evidenceId={evidenceId} onClose={() => setEvidenceId(null)} />}
  </div>;
}
