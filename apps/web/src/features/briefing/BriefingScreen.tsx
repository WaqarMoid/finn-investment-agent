import { useEffect, useMemo, useState } from "react";

type Preset = "24h" | "7d" | "custom";
interface BriefingEvent {
  id: string;
  company_name: string;
  symbol: string;
  event_date: string;
  kind: string;
  headline: string;
  implication: string;
  tier: string;
  filings_count: number;
  attachment_url?: string;
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
interface Meta {
  is_replay?: boolean;
  last_updated_utc?: string;
  requested_window?: { start_utc: string; end_utc: string };
  is_partial?: boolean;
}

const localDate = (date: Date) => {
  const offset = date.getTimezoneOffset();
  return new Date(date.getTime() - offset * 60_000).toISOString().slice(0, 10);
};

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

export default function BriefingScreen() {
  const today = useMemo(() => localDate(new Date()), []);
  const weekAgo = useMemo(() => localDate(new Date(Date.now() - 6 * 86_400_000)), []);
  const [preset, setPreset] = useState<Preset>("24h");
  const [customStart, setCustomStart] = useState(weekAgo);
  const [customEnd, setCustomEnd] = useState(today);
  const [data, setData] = useState<BriefingData | null>(null);
  const [meta, setMeta] = useState<Meta | null>(null);
  const [loading, setLoading] = useState(true);
  const [syncing, setSyncing] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [expandRoutine, setExpandRoutine] = useState(false);

  const getWindow = (selected: Preset) => {
    const now = new Date();
    if (selected === "24h") {
      return {
        start: new Date(now.getTime() - 86_400_000).toISOString(),
        end: now.toISOString(),
        startDate: localDate(new Date(now.getTime() - 86_400_000)),
        endDate: localDate(now),
      };
    }
    if (selected === "7d") {
      return {
        start: `${weekAgo}T00:00:00+05:30`,
        end: `${today}T23:59:59+05:30`,
        startDate: weekAgo,
        endDate: today,
      };
    }
    return {
      start: `${customStart}T00:00:00+05:30`,
      end: `${customEnd}T23:59:59+05:30`,
      startDate: customStart,
      endDate: customEnd,
    };
  };

  const loadBriefing = async (selected: Preset, sync = false) => {
    const window = getWindow(selected);
    if (window.startDate > window.endDate) {
      setError("Start date must be on or before end date.");
      return;
    }
    setError(null);
    setLoading(true);
    try {
      if (sync) {
        setSyncing(true);
        const syncResponse = await fetch(`/api/v1/refresh?start_date=${window.startDate}&end_date=${window.endDate}`, { method: "POST" });
        if (!syncResponse.ok && syncResponse.status !== 429) {
          const detail = await syncResponse.json().catch(() => ({}));
          throw new Error(detail.detail || `Exchange sync failed (${syncResponse.status})`);
        }
      }
      const response = await fetch(`/api/v1/briefing?start=${encodeURIComponent(window.start)}&end=${encodeURIComponent(window.end)}`);
      if (!response.ok) throw new Error(`Briefing request failed (${response.status})`);
      const json = await response.json();
      setData(json.data);
      setMeta(json.meta);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Unable to load this briefing window.");
    } finally {
      setLoading(false);
      setSyncing(false);
    }
  };

  useEffect(() => { loadBriefing("24h"); }, []);
  const choosePreset = (next: Preset) => {
    setPreset(next);
    if (next !== "custom") loadBriefing(next, true);
  };
  const summary = data?.summary;

  const EventGroup = ({ title, events, tone }: { title: string; events: BriefingEvent[]; tone: "attention" | "look" | "routine" }) => (
    <section className="panel">
      <div className="panel-header">
        <span className="panel-title">{title}</span>
        <span className={`badge badge-${tone === "attention" ? "attention" : tone === "look" ? "worth-a-look" : "routine"}`}>
          {events.length}
        </span>
      </div>
      {events.map((event) => (
        <article className="event-card" key={event.id}>
          <div style={{ display: "flex", gap: 12, alignItems: "flex-start" }}>
            <div className={`company-avatar ${getAvatarClass(event.symbol)}`}>
              {event.symbol.slice(0, 2).toUpperCase()}
            </div>
            <div style={{ flex: 1, minWidth: 0 }}>
              <div className="event-meta">
                <strong>{event.symbol} · {event.company_name}</strong>
                <span>{event.event_date}</span>
              </div>
              <h3>{event.headline}</h3>
              <p>{event.implication}</p>
              <div className="event-actions">
                <span className={`badge badge-${tone === "attention" ? "attention" : tone === "look" ? "worth-a-look" : "routine"}`}>
                  {event.kind.replaceAll("_", " ")}
                </span>
                {event.attachment_url ? (
                  <a className="source-link" href={event.attachment_url} target="_blank" rel="noreferrer">
                    Open NSE filing ↗
                  </a>
                ) : (
                  <span className="badge badge-routine">Source unavailable</span>
                )}
              </div>
            </div>
          </div>
        </article>
      ))}
    </section>
  );

  return (
    <div className="briefing-screen">
      <header className="screen-heading">
        <div className="screen-kicker">Portfolio Push Digest</div>
        <h1 className="screen-title">Portfolio pulse</h1>
        <p className="screen-subtitle">
          The filings and price moves that matter across your watchlist, ranked by priority.
        </p>
      </header>

      {meta?.is_replay && (
        <div className="notice">
          <strong>Historical replay</strong> · clock fixed at {meta.last_updated_utc?.slice(0, 10)}.
        </div>
      )}
      {meta?.is_partial && (
        <div className="notice">
          NSE returned partial coverage. Results below show the records received; retry refresh for complete coverage.
        </div>
      )}

      {/* Time Window Selector Panel */}
      <section className="panel">
        <div className="segmented" aria-label="Briefing period">
          {(["24h", "7d", "custom"] as Preset[]).map((item) => (
            <button
              key={item}
              className={preset === item ? "active" : ""}
              onClick={() => choosePreset(item)}
            >
              {item === "24h" ? "Last 24h" : item === "7d" ? "7 days" : "Custom"}
            </button>
          ))}
        </div>
        {preset === "custom" && (
          <div className="custom-window">
            <div className="field">
              <label htmlFor="briefing-start">From</label>
              <input
                id="briefing-start"
                type="date"
                value={customStart}
                max={customEnd}
                onChange={(e) => setCustomStart(e.target.value)}
              />
            </div>
            <div className="field">
              <label htmlFor="briefing-end">To</label>
              <input
                id="briefing-end"
                type="date"
                value={customEnd}
                min={customStart}
                max={today}
                onChange={(e) => setCustomEnd(e.target.value)}
              />
            </div>
            <button className="button" disabled={syncing} onClick={() => loadBriefing("custom", true)}>
              {syncing ? "Syncing NSE…" : "Apply window"}
            </button>
          </div>
        )}
        {preset !== "custom" && (
          <button
            className="button secondary"
            style={{ width: "100%", marginTop: 12 }}
            disabled={syncing}
            onClick={() => loadBriefing(preset, true)}
          >
            {syncing ? "Syncing NSE…" : "Refresh this period"}
          </button>
        )}
      </section>

      {/* Revolut Insight Numbers */}
      {summary && (
        <div className="summary-strip">
          <div className="summary-stat">
            <strong>{summary.total_events}</strong>
            <span>total events</span>
          </div>
          <div className="summary-stat">
            <strong>{summary.total_source_filings}</strong>
            <span>source filings</span>
          </div>
          <div className="summary-stat">
            <strong style={{ color: summary.needs_attention_count > 0 ? "var(--negative)" : "inherit" }}>
              {summary.needs_attention_count}
            </strong>
            <span>need attention</span>
          </div>
        </div>
      )}

      {error && <div className="notice error-notice" role="alert">{error}</div>}
      {loading && (
        <div className="panel empty-state">
          <p>{syncing ? "Fetching the selected window from NSE…" : "Preparing your briefing…"}</p>
        </div>
      )}

      {!loading && data && data.tiers.needs_attention.length === 0 && data.tiers.worth_a_look.length === 0 && data.tiers.routine.length === 0 && (
        <div className="panel empty-state">
          <h3>No filings in this window</h3>
          <p>This is a valid empty result for your current watchlist. Try seven days or choose a custom interval.</p>
          <button className="button" onClick={() => choosePreset("7d")}>Check seven days</button>
        </div>
      )}

      {!loading && data && (
        <>
          {data.tiers.needs_attention.length > 0 && (
            <EventGroup title="Needs attention" events={data.tiers.needs_attention} tone="attention" />
          )}
          {data.tiers.worth_a_look.length > 0 && (
            <EventGroup title="Worth a look" events={data.tiers.worth_a_look} tone="look" />
          )}
          {data.tiers.routine.length > 0 && (
            <section className="panel">
              <div className="panel-header">
                <span className="panel-title">Routine disclosures</span>
                <button
                  className="button secondary"
                  style={{ minHeight: 34, padding: "0 14px", fontSize: 12.5 }}
                  onClick={() => setExpandRoutine(!expandRoutine)}
                >
                  {expandRoutine ? "Collapse" : `View ${data.tiers.routine.length}`}
                </button>
              </div>
              {expandRoutine && (
                <div>
                  {data.tiers.routine.map((event) => (
                    <article className="event-card" key={event.id}>
                      <div className="event-meta">
                        <strong>{event.symbol}</strong>
                        <span>{event.event_date}</span>
                      </div>
                      <h3>{event.headline}</h3>
                      {event.attachment_url && (
                        <div className="event-actions">
                          <span />
                          <a className="source-link" href={event.attachment_url} target="_blank" rel="noreferrer">
                            Open filing ↗
                          </a>
                        </div>
                      )}
                    </article>
                  ))}
                </div>
              )}
            </section>
          )}
        </>
      )}
    </div>
  );
}
