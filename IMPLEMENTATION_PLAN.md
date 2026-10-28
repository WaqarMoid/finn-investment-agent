# FINN: comprehensive implementation plan

## 1. Product strategy and scope

**Product promise:** In a brief phone session, identify the portfolio developments worth investigating, inspect the underlying filing, and examine whether a company's reported outcomes match its earlier guidance.

Primary user: a time-constrained public-market investor with 15–20 holdings. Three moments: morning catch-up, review of a newly detected material disclosure, and targeted company research. This is an information and evidence product. Do not add trading, target prices, portfolio optimization, invented buy/sell recommendations, or an unexplained AI confidence score.

Build a responsive web app, not native apps. Use three mobile destinations: **Briefing, Research, Watchlist**. Notification rules live in Watchlist; sources open in a reusable evidence drawer. Desktop uses a list/detail arrangement of the same content. A compact question input supplements structured research; it is not the whole interface.

### Delivery tiers

**P0, required for our chosen submission:** 18 mock holdings; EOD prices/volume; one working exchange announcement adapter; annual-report and transcript ingestion; default 24-hour digest with custom window; material-first grouping with all ingested filings recoverable; configurable in-app alert inbox; four result metrics with honest unavailable states; 3–5 prepared research examples; ticker discovery beyond that set; a cited company snapshot and a four-quarter guidance ledger for at least one well-supported company; reliable source inspection; explicit live/replay status; phone deployment; README, build history, covering note.

**P1, add after P0 passes:** management appointment background, guided question answering, annual cash-quality panel, second exchange adapter, manual primary-document upload fallback, stronger retrieval, source-page highlighting, saved research.

**P2, consciously defer:** all eight deep research panels, native notifications, voice, dark mode, multi-user authentication, portfolio position accounting, realtime price data, full market screening, automated investment decisions, Kubernetes, a vector database, elaborate autonomous multi-agent orchestration. An installable app manifest is inexpensive but does not establish offline support or push notifications.

The brief describes most frontend examples as a menu. Our ambitious P0 is a chosen scope, not a claim that ENAM mandates all those screens. If time contracts, use the cut order in section 13.

## 2. Requirement traceability

M = main PDF; R = reference PDF. Page references refer to the original documents, preserved as extracted text under research.

| ID | Source and interpretation | Implementation evidence |
|---|---|---|
| R01 | M1/M4: mobile-first runnable prototype | Phone URL; 390px and real-device walkthrough; no horizontal page overflow |
| R02 | M1: both push and pull interaction | Briefing/alerts generated without a question; on-demand research job |
| R03 | M1: 15–20 mock portfolio names | 18 verified security-master records, sector diversity; watchlist UI |
| R04 | M1: handful of ad-hoc companies, about 3–5 | Four prepared research cases, outside holdings if practical |
| R05 | M2: engine must generalize to unseen NSE tickers where data exists | Security-master resolver and generic discovery; held-out-company test |
| R06 | M2: three data sources | EOD adapter, NSE/BSE filing adapter, company annual report/transcript adapter |
| R07 | M2: digest is an example, adopted here | UTC interval filtering; 24h/7d/custom; routine items expandable |
| R08 | M2: triggered alerts are an example, adopted here | Configurable price/volume/category rules; deterministic deduped events |
| R09 | M2: management enrichment is a favored example | P1 verified bio from company filing/IR; no compulsory LinkedIn scraping |
| R10 | M2: quarterly results favored example | Revenue/EBITDA/PBT/PAT, QoQ/YoY, comparable basis, provenance |
| R11 | M3: eight research outputs are optional menu | Snapshot and guidance ledger deep; additional panels only if supported |
| R12 | M3: promises versus outcomes particularly valued | Time-aligned four-quarter ledger, evidence on both sides, uncertainty explicit |
| R13 | M3: pull uses primary reports/transcripts, no broker/news/model memory | Retrieval allowlist; claims need primary evidence; no secondary fallback |
| R14 | M3: concise, interactive, considered density/design | DESIGN_SPEC plus screenshot and usability gates |
| R15 | M3: efficiency earns bonus; no model restriction | Deterministic calculations; model routing, cache, token/cost logs |
| R16 | M3/M4: creativity, judgment, architecture; thin and working | Explicit cut line, reasoned UI, early deployment, reproducible demo |
| R17 | M4: URL/repository/build history/short writeup | Release checklist and submission draft; links tested in private browser |
| R18 | M4: recipient/subject | Record assessment@enam.com and ENAM - IIT screening - 2027; do not send automatically |
| R19 | R1: 17 suggested filing categories, adaptable | Preserve category mapping; subtype/materiality are separate fields |
| R20 | R2–3: definitions scaffold finance | Finance normalization policy below; explain terms inline when useful |

Do not interpret “every filing” as a guarantee across a source outage. Reconcile every filing actually received in a requested interval and expose feed coverage, last successful sync, and missing intervals. Routine collapse is a presentation decision, never destructive deletion.

## 3. Candidate companies and source feasibility

Proposed 18-symbol watchlist: RELIANCE, TCS, INFY, HDFCBANK, ICICIBANK, HINDUNILVR, ITC, LT, SUNPHARMA, DRREDDY, MARUTI, TITAN, ULTRACEMCO, NTPC, TATASTEEL, PERSISTENT, KAYNES, CERA. These are **candidate identifiers**, not a certified current exchange master. Resolve and verify each at build time, including renames, mergers, listing status and series. Substitute only after documenting why, keeping 15–20 names and sector/size diversity. Do not assert size classifications without a dated market-cap source.

Four proposed ad-hoc cases: HCLTECH, COFORGE, DIXON, ASTRAL. Select the final set after source feasibility checks. Prefer one guidance-rich company, one capital-intensive business, one company with messy or absent guidance, and one financial-sector case for metric limitations. A portfolio name can also supply the signature ledger; availability is more important than novelty.

Source inventory per prepared company: verified identity/ISIN and official IR domain, latest available annual report, prior annual report if needed for trajectory, last four available transcripts, matching quarterly results, one earlier guidance-bearing transcript if required, filing dates, fiscal periods, download URLs, hashes and access status. Four quarters of YoY comparisons can require **eight quarterly periods**; four guidance outcome pairs can require guidance stated before the four target periods. Do not assume four PDFs are sufficient.

**Early feasibility spike, maximum 90 minutes:** resolve one ticker, fetch 60 trading sessions, obtain exchange filing metadata and attachment, acquire one annual report and transcript from an official company site, extract page text and locate a result/guidance excerpt. Deploy a basic shell the same day. Source access failure discovered late is the largest avoidable delivery risk.

## 4. Architecture and stack

Choose **React + TypeScript + Vite**, **FastAPI/Pydantic**, **SQLite with WAL and FTS5**, and a lightweight Python worker sharing application services. Use plain CSS variables/CSS modules, accessible headless dialogs/tabs if needed, and a single outline icon family. Use TanStack Query for remote state, React Router for deep links, Vitest/Testing Library, pytest and Playwright. Python extraction uses pypdf/pdfplumber; OCR is an isolated fallback. Avoid a new dependency where a small pure function is clearer.

This separates Python data ingestion from frontend craft while retaining one deployable unit: build the frontend and serve its static files from FastAPI; `/api/v1/*` is routed before the SPA fallback. A single container, one API process, one worker process, persistent `/data` volume, and HTTPS are sufficient. Use a provider that actually supports these requirements; free plans and sleeping/ephemeral filesystems must be verified on implementation day. Local Docker Compose is the reliable reproduction path. If persistent hosting is unavailable, explicitly migrate to managed Postgres/object storage, or publish a labeled read-only replay deployment plus a runnable live backend; the latter is a limitation, not full live equivalence.

```text
Public exchange / market / official company sources
  -> source adapters -> raw files + metadata + checksums
  -> parsing -> typed facts / events / citations
  -> validation -> deterministic metrics / priority / alerts
  -> primary-only retrieval -> structured model analysis -> claim validation
  -> API -> mobile Briefing / Research / Watchlist -> evidence drawer

Durable job table -> worker -> bounded retries -> progress polling
SQLite: entities, facts, job state, FTS chunks, derived results, cache
Filesystem: immutable raw documents; no transient-only storage
```

Suggested code structure:

```text
apps/web/src/{app,features/briefing,features/research,features/watchlist,
  components/evidence,components/ui,lib,styles}
apps/api/finn/{api,schemas,db,adapters,ingestion,extraction,finance,
  ranking,alerts,retrieval,research,llm,jobs,observability}
tests/{unit,integration,contracts,e2e,fixtures,gold}
scripts/{seed_demo,refresh_sources,evaluate,export_history}
data/manifests/             # safe source metadata, not secrets
docs/{architecture,decisions,eval,build-history,screenshots}
Dockerfile; compose.yaml; .env.example; README.md
```

Pin exact versions after installing a compatible stable set; commit Python and JavaScript lockfiles. Record runtime versions. Do not assert that an untested version combination works. SQLite FTS5 availability is a startup check. Database migrations are versioned, transactional and repeatable; backup before destructive migrations. Never keep business rules duplicated in React and Python.

## 5. Ingestion and provenance

### Security resolution

Refresh a dated official NSE securities master; normalize symbol input, suffixes, aliases and ISIN. Exact symbol match wins; ambiguous name searches show choices. Validate BSE code separately: a BSE numeric scrip code is not derived by appending `.BO` to an NSE ticker. Store exchange-specific price identifiers and historical aliases. Resolve the company before retrieval, preventing similarly named entities from contaminating evidence.

For unseen companies: master lookup -> official domain discovery -> IR/report/transcript link discovery -> bounded download and indexing -> research. Search snippets are discovery only, never evidence. Use a configurable search adapter if permitted and available, otherwise exchange-linked website and generic same-domain IR crawling. Store reusable domain hints as configuration, not per-company narrative or special-case answer code. If discovery fails, explain exactly which document class is missing; allow adding a primary URL or upload in P1. Manual fallback must not be presented as proof of automated generalization.

### Price/volume

Use yfinance or equivalent for EOD data, with explicit adjustment settings, daily interval and provider/timezone metadata. Fetch approximately 90 calendar days to obtain at least 21 completed trading sessions; request more if needed. Save raw close, adjusted close when supplied, raw volume, corporate actions and retrieval time. Keep price provider identity consistent within a series. Do not blend NSE and BSE volumes.

Calculate alerts only on completed sessions, using an exchange calendar and actual returned session dates. An initial operational refresh target of 18:30 IST is a proposal, not a statement of guaranteed publication time; retry after an hour if the day's bar is missing. Announce stale data instead of pretending it is today's. Weekends and holidays do not create missing-day alerts. Preserve revision history when a provider corrects a bar.

### Exchange announcements

Use an official NSE or BSE source, with metadata pagination, date-range filtering and attachments. The public web pages are entry points, not a promise of a stable documented API. Inspect the current permitted interface at build time, retain sample responses, and isolate source-specific parsing in adapters. Handle normal sessions/cookies where required; no bot-block bypass. Honor robots/terms, rate limits and Retry-After. BSE returned 403 during planning; mark its adapter unverified until the coding spike succeeds.

Poll a configurable 15-minute interval for the prototype, using an overlap window for late filings, and a longer backfill on first run. Track published_at, exchange_received_at, fetched_at, attachment availability and covered interval separately. Configured polling is near-periodic detection, not realtime delivery. Fetch all pages before advancing the watermark; failed middle pages leave the interval partial. Use bounded requests and a 48-hour overlap initially. Reconcile counts and retain the source record even if its PDF fails.

Dedup by source ID within an exchange. Across exchanges, group by ISIN, content hash and event timing; preserve both source links. Similar titles alone cannot collapse different announcements. Revised PDFs supersede earlier versions but remain auditable. A results notice, results filing, investor deck and newspaper advertisement are related documents, not four identical material results alerts.

### Fundamentals

Screener may help discover links; download the underlying company/exchange annual report and transcript. Do not use Screener's normalized financial table as primary pull evidence. Official company IR is preferred. Pull core evidence consists of annual reports and transcripts. Primary quarterly result filings can supplement numeric verification and guidance outcomes, explicitly labeled as such; if the assessor interprets the parenthetical annual-reports-plus-transcripts strictly, the research view must still work from those two classes alone. Official investor decks are optional supplementary evidence, not substitutes for required AR/transcript ingestion.

### Document pipeline

1. Validate URL against verified company/exchange sources. Enforce HTTP(S), public addresses, redirect revalidation, MIME and size limits; reject internal/metadata/localhost addresses.
2. Stream download with 20-second connection/read budgets, bounded total job time, max 30 MB/document and 500 pages initially. These are implementation defaults, configurable for a legitimate large report. Store content SHA-256, URL, original filename, dates and fetch status.
3. Extract per-page text, layout/table candidates, and page numbers. Retain PDF page index and printed page label separately. Detect encrypted, corrupt, HTML-instead-of-PDF and scanned documents.
4. Run OCR only on relevant low-text pages; never OCR every annual-report page by default. Tag OCR outputs and do not silently publish critical numbers without corroboration or review.
5. Chunk by section/paragraph with page boundaries and table headers attached. Start around 700 tokens, 100-token overlap; split large tables by row with repeated headers. Store offsets and immutable source page IDs.
6. Extract typed facts with evidence spans. Normalize only after validating entity, period, unit, currency and consolidated/standalone basis.
7. Record parser/model/schema versions. Changes invalidate dependent artifacts, not unrelated data.

A document may be downloaded but not readable, readable but not indexed, indexed but insufficient for an answer. Show these distinctions in research progress and source coverage.

## 6. Push: digest, materiality and alerts

### Category taxonomy

Seed the 17 reference labels: results, M&A, fund_raise, management_change, litigation, insider_trading, earnings_call, investor_meetings, credit_rating, dividend, bonus_split, capex, press_release, postal_ballot, agm_egm, pledging, unclassified. Use machine key `m_and_a` with source-label mapping. Add subtype, event stage, role, magnitude, effective date and materiality_reason; these are more informative than category alone.

Respect the reference while improving judgment: auditor appointments may be routine, but auditor resignation/qualification and distress must never be buried simply because they fall under unclassified. A board meeting to consider results is not results. A credit reaffirmation differs from downgrade. Rumor clarification is not completed acquisition. An analyst's question is not management guidance.

Rules handle obvious subjects; a cheap structured model resolves ambiguous categories using title plus relevant filing text. Low certainty becomes review-needed, not an invented categorical conclusion. Failures still show original title, time and filing link.

### Ranking policy, deterministic and inspectable

Assign a tier before sorting: Needs attention, Worth a look, Routine. Safety overrides put insolvency, auditor qualification, serious regulatory action, material restatement and significant leadership departure in Needs attention. The rule cannot be overwritten by a weak model's “routine” label.

Initial scoring proposal (tune with labeled filings): actual results/M&A/distress 60 base; other material leadership/funding/capex/rating downgrade 45; ordinary operational update/dividend 25; notices/meetings/compliance 5. Add 15 for explicit user category interest and up to 15 for verified relative magnitude. Use 55+ for Needs attention, 25–54 for Worth a look, lower for Routine. Unknown magnitude adds zero; do not invent a financial denominator. Recent publication breaks ties after severity; use stable ID as final tie-break. Store rule version and component contributions. User category selection affects notification eligibility and ranking, not whether a filing is retained.

These numbers are product hypotheses, not learned probabilities. Validate on 50–100 varied filings; prioritize recall of material events before reducing noise. No causality claim linking price change and filing without evidence. “Occurred on the same day” is safe; “caused the fall” is not.

Digest interval is `[start_utc, end_utc)`, displayed in IST. Default last 24 hours; presets 7 days and custom date/time. Summaries group related events, but a “View all filings” path accounts for every ingested record. Expose counts as derived values: unique events, source filings, and routine filings are different counts. Use a snapshot ID so refresh cannot move rows under the user's finger.

### Alert rules

- Price movement = `100 * (current_close / previous_close - 1)` using a declared comparable series. Default absolute move strictly greater than 5%, configurable positive threshold. At corporate action discontinuities use an independently supported comparable series or suppress the alert with reason. Do not conflate an adjusted total-return measure with raw market-price movement.
- Volume ratio = `today_volume / mean(previous 20 completed sessions' volumes)`. Today is excluded. Trigger strictly greater than 2.0 by default. Fewer than 20 valid sessions -> insufficient history, no default alert. Missing volume is not zero; zero baseline produces unavailable.
- Material-filing alert = configured categories plus materiality threshold; user sees why it matched. Polling detects new filings regardless of whether the app is open.
- Event uniqueness = tenant/session scope, rule ID and version, company, underlying filing group or trading session. Re-running jobs must not duplicate alerts.
- Rule edits affect future events; an explicitly labeled “Test on recent data” returns a preview without emitting notifications. If recalc is offered, label historical alerts.
- In-app inbox and badges are P0. Optional web push requires separate permission, service worker, delivery setup and testing; do not promise background OS notifications without them.
- First sync establishes a baseline and fills the digest; it must not notify on every old filing. Persist a monitoring-start cutoff, and only emit newly eligible events after it. Historical replay deliberately uses its own fixed cutoff and labeled event clock.

## 7. Numerical correctness

Represent money as Decimal or integer base units, not binary floats. Store source value, source unit, normalized value and conversion. Display INR crore by default where appropriate: 1 crore = 10 million INR; 1 lakh = 100,000 INR; 1 billion INR = 100 crore. No currency conversion without an explicit dated FX source; separate INR, USD and constant-currency guidance.

Every fact key includes company, metric, period start/end, period type, fiscal label, currency, unit, reporting scope and status (reported/derived/restated/unavailable). Compare only compatible keys. Fiscal labels must come from the company's reporting calendar; do not assume every company has an April–March year.

Revenue: distinguish revenue from operations from total income. PAT: distinguish group total from profit attributable to owners. PBT: use the explicitly comparable reported measure. EBITDA: prefer explicitly reported EBITDA with definition. Never rename EBIT/operating profit as EBITDA. A derivation such as PBT + finance costs + D&A may include other income or exceptional effects; label it, preserve components, and publish only when its accounting scope matches the intended measure. Otherwise show “Not disclosed on a comparable basis.” Banks/insurers need sector-aware measures; EBITDA is generally not a useful common operating measure there, so do not force a four-number generic story.

QoQ/YoY = `(current / prior - 1) * 100` only when prior > 0 and periods/scope/currency are comparable. Negative or zero prior -> show absolute change and wording such as “loss narrowed,” with percentage `null` and reason. Margin difference in percentage points is not percent growth. A 15% to 18% margin is +3 percentage points. Ratios with zero/negative inappropriate denominators are unavailable, with explanation.

Distinguish quarter-only results from YTD, six-month and nine-month columns. Derive Q4 = FY minus 9M only when the same basis, accounting definitions and restatement version apply; mark derived and cite both operands. Do not accidentally use annual revenue as Q4. Handle prior-year comparative columns, exceptional items, discontinued operations and acquisition-related changes. Preserve restated values and recalculate downstream deltas with a visible revision note.

Optional cash quality: CFO/PAT with meaningful positive PAT and same period; FCF = CFO minus cash capital expenditures using explicit sign convention and definition. Do not use capex guidance as actual cash capex. Working-capital days, ROCE and ROE need their exact formulas and average-denominator availability; omit rather than assume. Debt means clearly defined gross/net debt, not all liabilities. A profit increase alone does not prove cash quality.

All calculations execute in Python. LLMs locate and explain facts; they do not supply final arithmetic. Render numbers and deltas from the same typed objects, not separate generated prose. Round at display boundaries; explain any displayed rounding differences rather than changing underlying financial totals.

## 8. Pull research and management ledger

Pipeline: resolve -> discover -> ingest -> assess coverage -> retrieve -> extract facts/guidance -> compute -> synthesize -> validate citations -> publish supported sections. Job progress uses real completed stages, not invented percentages. Cache by company, question/template, source hashes, as-of timestamp, prompt/schema/model versions and reporting basis.

Start with SQLite FTS5 plus section/metric keywords, company and date filters. Retrieve table rows with their headers and adjacent explanatory notes. For guidance, select management-speaking turns and forward-looking verbs; include preceding context. Use around 8–12 high-relevance evidence blocks per answer and bounded annual-report sections. Embeddings/reranking are P1 only if measured retrieval misses justify them. A large vector store cannot repair bad period identification.

Research report structure: company/basis/as-of header; coverage summary; three cited business facts; verified headline figures; four-quarter guidance ledger; two or three supported implications and unresolved questions. Optional bull/bear framing uses the same primary facts, distinguishes interpretation, and includes counterevidence. No fabricated certainty, no stock forecast from model memory.

### Ledger, the signature feature

Each guidance statement records: who said it, date, exact evidence excerpt, metric, quantitative range or qualitative claim, target period, currency/basis, conditions, original/revised/withdrawn status, and source page. Link to an actual only if metric definition, scope, target period and units match.

Display **Stated / Reported / Assessment** per quarter. Assessments: met, exceeded, missed, not yet due, not comparable, no explicit guidance found, insufficient evidence, withdrawn. A fiscal-year target is not missed by one weak quarter. Show “progress toward full-year target” only if the calculation is meaningful; do not grade it early. Qualitative statements get a supported narrative assessment rather than an invented numeric target.

For a higher-is-better bounded range, actual below lower bound is missed, within range met, above upper exceeded. Lower-is-better targets need reversed semantics. Capex and ranges whose direction is not inherently beneficial use “below/within/above guidance,” not “beat/miss.” Apply stated rounding tolerance, not an arbitrary broad tolerance hiding misses.

Revised guidance: preserve chronology, original target and latest target separately. Show the revision and evaluate the target applicable to the outcome; do not erase the original commitment. Do not classify a post-results recap as prior guidance. Facts used in a historical as-of view must have been published by that cutoff. Compare reported-currency growth with reported-currency guidance and constant-currency growth only with compatible actuals.

If a quarter has no explicit guidance, retain its row and show that state. Four honest rows with missingness are preferable to four invented verdicts. At least one demo company should have enough evidence for a meaningful ledger; the general engine must still handle companies that do not guide.

### Citation integrity

Each company-specific factual claim links to a stored citation ID, not a URL fabricated by the model. A claim may require multiple citations. Evidence drawer displays document title, issuer, publication date, PDF page/printed label, excerpt and original link. Verify excerpt existence after whitespace normalization; OCR excerpts carry OCR status. Validate that cited document belongs to the company and allowed source class. Citation existence is necessary but not sufficient: evaluate whether the excerpt actually supports the claim and whether important counterevidence was omitted.

Quote only short evidence spans; do not republish entire third-party reports in a public repository without checking redistribution rights. Raw documents can be fetched at runtime or stored privately with manifests and links. Do not copy broker commentary into the retrieval corpus.

### Full research-menu extension map

The following covers every research option in the brief without requiring all eight at release. Add an optional panel only after its source and validation gate passes; an empty ornamental tab is not implementation.

| Menu item | Data and computation | Useful presentation and gate |
|---|---|---|
| Business snapshot | Annual-report business/segment notes; dated segment revenue and explicit denominator | Three facts and optional segment mix; parts reconcile or scope differences explained; no company facts from memory |
| Financial snapshot | Latest primary reported revenue/profit/margins; dates, unit and scope | Compact metric rows with source and comparison; every current metric carries its period rather than implying all are equally recent |
| Trajectory | Three to five annual periods on a consistent basis, or available comparable quarters | Simple line/table with missing gaps; CAGR only with positive meaningful endpoints and correct interval count; acquisitions/restatements annotated |
| Balance sheet | Debt components, cash, maturity notes, equity and working-capital inputs from AR | Debt/cash summary and one supported funding observation; do not equate all liabilities with debt or calculate days from missing inputs |
| Cash quality | CFO, PAT and cash capex across matching annual periods | CFO/PAT and FCF trend with definitions; negative/zero PAT caveat; no claim that one year's weak conversion proves accounting abuse |
| Narrative versus numbers | Cited management statements matched to typed outcomes and dated counterevidence | Stated/Reported/Assessment ledger; distinguish contradiction from a different horizon, scope or qualified statement |
| Guidance | Explicit forward statements, revisions, conditions and target horizons | Chronological targets with due/not-due state; analyst questions and aspirations identified separately |
| Bull versus bear | Supported strengths, risks and uncertainties derived from the same primary corpus | Two or three concise points each, each with evidence and what would change the view; no fabricated symmetry, price target or buy/sell call |

For optional ratios, a formula registry specifies required metrics, scope, time averaging, valid denominators, units and interpretation caveats. A panel returns insufficient evidence if prerequisites fail. Never broaden source policy merely to populate every menu item.

## 9. Models, cost and reliability

Implement a provider-neutral `generate_structured` adapter with model IDs configured through environment variables. Select from the builder's available models by a small gold-set experiment; do not assume the cheapest or largest wins. Use a low-cost model for classification and extraction, stronger reasoning only for ambiguous guidance comparison/contradiction synthesis. Run temperature low where supported, strict schemas, bounded output and explicit missing-value rules.

Validation failure -> one schema repair attempt -> one stronger-model attempt only when budget permits -> abstain with source link. API timeout/429 -> bounded exponential backoff with jitter; respect Retry-After. Circuit-break repeated failures. No recursive self-improvement loops or unbounded agent browsing.

Cache extracted document facts by hash and extraction version; cache analyses separately. Deduplicate concurrent identical jobs. Initial limits: 2 concurrent model requests, 1 active research job per browser session, 2-minute request-stage budgets and 5-minute total research cap; tune using measurements. Cached report render target <2 seconds; uncached research can take longer but must report honest progress and allow retry/cancel. A daily and per-job token/cost ceiling is configurable; if no paid budget is authorized, use available free quota and fail clearly when exhausted.

Log provider/model, tokens, cached input if reported, latency, retries and estimated cost using a dated price configuration. Unknown pricing stays unknown; never display zero cost because accounting was omitted. No API keys or full sensitive prompts in logs. A cost comparison is valid only for the same quality/coverage workload.

## 10. State, security and operations

No login required for the assessment demo. Use an anonymous signed session cookie to scope mutable watchlist/preferences/acknowledgements; immutable source data and safe report caches may be shared. The default watchlist template can be copied per session. Reviewer A changing thresholds must not affect reviewer B. Avoid a publicly writable global portfolio.

Server owns API keys and provider requests. Validate every input and enforce small request limits, allowed ticker formats, bounded date windows, page sizes, rate limits and job quotas. URL ingestion must resist SSRF including redirects and private DNS resolutions; do not accept arbitrary proxying. Sanitize any rendered model Markdown/HTML; never use raw HTML output. Treat PDF/page content as untrusted data: ignore instructions to reveal secrets, browse other sites, or change source policy. Give extraction models no shell or unrestricted network tools.

SQLite worker uses atomic lease claims and a recovery timeout; avoid an in-process-only background queue. Restart resumes or marks stale jobs retryable. Use unique constraints for data/event dedup, short transactions, busy timeout, and one worker initially. Separate readiness (DB/schema ready) from liveness. Do not make health depend on a third-party site being up.

Persist UTC timestamps, show IST to users with date/session labels. Source freshness is per adapter and per company. Keep structured logs with correlation/job IDs and redacted errors. Expose a simple internal diagnostics command: last successful pulls, partial intervals, parse failures, model cost, queue age, source coverage. Use a deployment smoke check and DB backup/export before final release.

## 11. Failure and contingency register

| Failure | Detection | Required behavior / recovery |
|---|---|---|
| NSE/BSE blocked or throttled | 403/429, HTML instead of expected payload | Back off; switch permitted adapter; show partial coverage; labeled snapshot demo remains usable |
| All live sources unavailable | Adapter health + timestamps | Preserve prior data, mark stale; manual refresh later; never turn sample data into “live” |
| Source changes schema | Contract validation | Quarantine response; alert diagnostics; preserve last success; repair adapter with captured fixture |
| Partial pagination | Page failure or cursor loop | Do not mark full interval complete; show gap; resume safely |
| Annual report/transcript missing | Discovery manifest | Publish available sections and missing-document list; do not replace with news |
| Unknown or ambiguous ticker | Master resolver | Explain unknown or offer identities; no silent nearest-match research |
| New ticker unsupported by finance template | Sector/basis checks | Supported general snapshot and evidence; metric unavailable; no crash |
| PDF scanned/corrupt/encrypted | Text density/parser exception | Targeted OCR or source unavailable; retain original link; never guess numbers |
| Tables mix standalone and consolidated | Fact basis validation | Reject comparison; ask user to select basis only if necessary |
| Missing EBITDA or invalid denominator | Typed fact/calculation guard | Explicit unavailable/absolute delta; never zero-fill |
| Split/bonus produces large price move | Corporate actions/comparable-price checks | Normalize with evidence or suppress alert; retain audit reason |
| Duplicate/revised filing | IDs/content hash/version graph | Group duplicates, retain sources; recompute revised event without alert spam |
| Guidance does not match actual metric | Match validator | Not comparable; both pieces of evidence accessible |
| No guidance or outcome not due | Target timeline | Honest state; do not invent hit/miss |
| Model invalid JSON/timeout/quota | Schema/adapter error | Bounded repair/fallback, then cited extract or unavailable analysis |
| Citation supports different company/period | Citation/entity validation | Reject claim and regenerate once or omit |
| Prompt injection in a PDF | Adversarial test + system boundaries | Treat text as evidence only; no tool action from source instructions |
| Worker/server restarts | Expired leases | Resume idempotently; keep last published report |
| Host sleeps or loses disk | Deployment restart probe | Persistent hosting or explicit alternate architecture; replay is labeled |
| Browser offline | Failed fetch/network state | Previously loaded content with stale marker; do not imply a fully offline app |
| Multiple users edit rules | Session tests | Isolate settings and alert acknowledgements |
| Mobile keyboard/long title/large text | Device/visual tests | Reflow, scroll focused field, no hidden primary action |
| Date-boundary or holiday confusion | Calendar/time tests | Use actual sessions and UTC intervals; label EOD date |
| Demo period has no news | Legitimate empty digest | Keep live empty state; offer user-selected historical replay with dates |
| Credentials absent | Startup/config check | Source-backed read-only replay; live research clearly disabled |
| Time runs out | Milestone schedule | Cut P2/P1, protect vertical slices, ship verified limits |

Unanticipated failures use the same rule: retain source evidence and last known good state, fail one section rather than the whole app, expose a plain-language reason, and never make unsupported output look complete.

## 12. Demo, deployment and proof of generalization

Live mode and replay mode use the same domain services and UI contracts. Replay has a fixed clock and a manifest of real historical source records, not fictional company news. All replay screens show the historical interval and snapshot date. Synthetic fixtures are for automated tests and must be marked synthetic; keep them out of the reviewer-facing real-data demo.

Prepare three brief stories: a material filing with a primary evidence trail, a correctly calculated unusual EOD alert, and a promise-versus-outcome comparison including at least one uncertainty case. Management bio is a fourth only if verified. Do not cherry-pick only successful model answers; document failure coverage.

Freeze the demo set, then test three previously unprepared NSE names representing different sectors and document layouts. No code changes or per-ticker facts during the test. Record discovery success, document coverage, supported answer rate, timing and failures. If a held-out company lacks a transcript, that is a legitimate missing-data result, not a successful full research answer. If every held-out fails discovery, the generalization gate has not passed.

README must contain tested quickstart, runtime requirements, environment example, seed/replay/live commands, adapter limitations, model setup, architecture diagram, test/eval commands, source provenance, public deployment details and known gaps. Build history should capture actual prompts, decisions, commits and evaluations; export/share the actual conversations with user review for secrets. Do not fabricate a neat historical transcript after the fact.

## 13. Timeline and decision gates

Assuming start 28 October, target completion 31 October IST:

1. **28 October:** read contract, source spike, deployed shell, schema and raw provenance, one end-to-end briefing row.
2. **29 October:** portfolio ingestion, ranking/alert calculations, complete briefing interactions, source-backed financial extraction and one research report.
3. **30 October:** guidance ledger, unseen ticker pipeline, model/citation validation, realistic replay and failure tests.
4. **31 October:** feature freeze, mobile visual refinements, numerical/source audit, held-out tests, clean-clone deploy, history and writeup.
5. **1 November:** buffer, final URL check and user-authorized submission before the confirmed cutoff.

This is a sequencing proposal, not a promise of person-hours. With a weak coding model, repeatedly use small tasks and contract tests. Stop adding features when fewer than one full verification block remains.

Cut order: native push/voice/dark mode -> extra charts and optional research panels -> management bio -> sophisticated reranker -> second exchange adapter -> four polished research companies reduced to three. Preserve 15–20 holdings, both push and pull, a working primary-source pipeline, unseen-ticker support, mobile UI, reliable demo, and honest state. If the ledger cannot be deeply populated for every example, keep one excellent ledger and partial coverage elsewhere. Never rescue scope by hard-coding final company narratives.
