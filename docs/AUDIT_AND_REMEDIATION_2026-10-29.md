# FINN live audit and remediation report

Date: 2026-10-29 (IST)

## Scope

The deployed Localtunnel build, REST API, SQLite records, mobile viewport, desktop viewport, all three product destinations, NSE upstream behavior, research source integrity, theme behavior, and deployment path were inspected. The audit used read-only browser automation against the public tunnel, direct API requests, database queries, and a post-fix local production build.

## Material faults found

| Area | Fault | User impact | Resolution |
|---|---|---|---|
| Date windows | The NSE adapter ignored `start_date` and `end_date` and always requested the latest feed. | 24h, 7d, and custom windows showed the same two days. | NSE `from_date` and `to_date` parameters are now sent in `DD-MM-YYYY`; records are converted from IST to UTC and bounded again after retrieval. |
| Production refresh | The presence of a test fixture file forced every live refresh to use the fixture. | “Live” refresh never contacted NSE. | Fixtures are now used only when `FINN_EXCHANGE_SOURCE=fixture` or in replay mode. Live mode uses NSE. |
| Custom UI | “Custom” meant a hard-coded 30 days and exposed no date controls. | Users could not choose a range. | Added accessible From/To date inputs, validation, a 32-calendar-day fetch limit, selected-window sync, and accurate interval queries. |
| Portfolio scoping | Briefings grouped every NSE company ingested into the global database. | Unmonitored companies appeared in the portfolio briefing. | Briefing queries now join the anonymous session watchlist. Backfill processing filters the upstream batch to the 18 monitored symbols. |
| Time boundaries | NSE timestamps were interpreted as UTC although `an_dt` is IST. | Filings around midnight could fall in the wrong day. | NSE timestamps are localized to Asia/Kolkata, then normalized to UTC. |
| Default watchlist | `SELECT ... LIMIT 18` selected whichever companies SQLite returned first. | The starter portfolio could change as unmonitored issuers were inserted. | The 18 assignment companies are now seeded from an explicit ordered ID list. |
| Filing categories | Broad “financial results” matching ran before transcript/call matching. | Earnings calls could be mislabeled as results. | Specific call/transcript rules now run before results rules. |
| Briefing evidence | Every event opened the same hard-coded `ev-preview-101`. | Filing buttons could show an unrelated Infosys quotation. | Each event opens its actual NSE attachment URL; no source button is rendered when the filing has no URL. |
| Research integrity | INFY/HCL narratives, figures, and guidance rows were hand-written into seed data; TCS/Reliance fell back to the Infosys demo citation. | Reports could display unsupported or cross-company claims. | Synthetic documents and placeholder NSE paths are removed at startup. Four quick stocks now have first-party issuer links. Facts and ledger rows require persisted page evidence. |
| Research race | Rapid ticker selection left the previous report visible while the next request ran. | TCS or Reliance could show Infosys/HCL content. | The active request is aborted, the previous report is cleared immediately, and controls are disabled during resolution. |
| Evidence drawer | A failed citation request displayed a fixed sample guidance quote. | A 404 looked like verified evidence. | The drawer now shows an explicit unavailable state and never substitutes text. |
| Bounded Q&A | FTS results returned citation IDs that did not exist in the evidence API. | Answers could not be inspected. | A matching parsed page now produces a stable real evidence span; otherwise FINN refuses to answer. |
| Visual system | No theme toggle, external IBM font, dense inline styling, weak hierarchy. | The product looked generic and dark mode did not exist. | Added local Raleway variable font, persisted light/dark theme, system preference default, mobile floating navigation, desktop rail, rounded sheet hierarchy, clearer controls, and reduced-motion/focus support. |
| Tunnel access | Localtunnel required an IP/tunnel-password step. | Mobile reviewers encountered friction before reaching the app. | Added a Render Blueprint and one-click deploy link for a standard HTTPS URL. |

## Verification evidence

- Full automated suite: **71 passed**.
- Frontend production build: TypeScript and Vite completed successfully.
- Live NSE single-day response: **99 records** on 2026-10-29.
- Live NSE 2026-10-22 through 2026-10-29 response: **3,596 records**; **70 watchlist records** processed and **3,526 non-watchlist records** discarded before insertion.
- 24-hour briefing after the live sync: **2 events / 2 source filings**.
- Eight-day custom briefing over the same database: **56 events / 70 source filings**.
- Browser QA at 390×844 and 1440×1000: no console errors, no horizontal mobile overflow, two custom date inputs, both themes, correct TCS-after-INFY state, and at least two official links for every quick research stock.

Screenshots are stored in `docs/audit-after/`. The repeatable browser audit script is `scripts/audit_deployment.py`.

## Product limits retained intentionally

- BSE automated announcements remain unavailable because its anti-bot layer rejects the server flow. The UI and API state that NSE is the active exchange source.
- The official research catalog is complete for the four quick choices, but page-level extraction is intentionally pending. This is a visible coverage state, not a silent fallback.
- The Render free tier has an ephemeral filesystem and can sleep after inactivity. Startup recreates the database and source catalog, but durable cross-deploy watchlists require a persistent disk or managed database.
- The maximum on-demand NSE backfill is 32 calendar days to bound upstream load and response time.
