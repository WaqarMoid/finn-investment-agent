# Implementation work packets

Use this as an execution queue. Each packet should fit one focused coding-agent session. Read the listed documents and relevant code, implement, run the specified checks, record evidence and stop at the packet boundary. Do not ask the model to build the entire product in one response.

At every handoff update `docs/BUILD_STATUS.md`: completed packet, changed files, commands/results, unresolved defects, current source coverage, next packet, decisions deviating from the plan. Record actual outcomes, not “should work.” Commit passing checkpoints if working in Git. Preserve unrelated user changes.

## T00 — Source feasibility and runtime spike

Read: START_HERE, IMPLEMENTATION_PLAN sections 2–5, RESEARCH_AND_DECISIONS.

Deliver: `docs/source-feasibility.md`, chosen dependency/runtime versions, one downloaded primary PDF manifest, one exchange metadata fixture, one EOD fixture and a verified company identity. Test official IR and transcript availability for proposed demo companies. Check the intended host supports background worker, persistent volume and HTTPS. Document each source as tested/blocked/unverified with timestamp.

Gate: at least one successful path for each of the three source classes, or an explicit remediation decision before UI scope expands. Downloading a web page without parsing usable records does not pass. Timebox to 90 minutes; do not spend the day reverse-engineering a blocked exchange.

## T01 — Repo, shell and first deployment

Read: IMPLEMENTATION_PLAN architecture; DESIGN_SPEC tokens/navigation; CONTRACTS common types.

Deliver: React/TS frontend, Python API, lockfiles, `.env.example`, Dockerfile/Compose, lint/typecheck/test scripts, health routes, mobile navigation shell, a preview deployment. Pick compatible maintained dependencies and record versions; no invented deployment URLs.

Gate: fresh install/build, API readiness, responsive shell at 390px, direct deep-link reload, HTTPS preview opens on phone. Keep synthetic UI fixtures labeled and separate from final demo data.

## T02 — Database, identity and evidence backbone

Read: CONTRACTS entities/common types; IMPLEMENTATION_PLAN security resolution and provenance.

Deliver: migrations, company/security resolver, 18 validated candidate holdings, raw document storage, source-page/evidence objects, data repository layer, session-scoped watchlist. Test unknown and renamed/aliased identities. Add explicit scope/period/unit fields before numerical features.

Gate: migration on clean DB and rerun; foreign keys; immutable document hash/version; evidence lookup returns correct original page; two browser sessions have isolated watchlists. Never embed the demo answers into the resolver.

## T03 — Price adapter and deterministic calculations

Read: IMPLEMENTATION_PLAN price, alert and numerical sections; CONTRACTS arithmetic vectors.

Deliver: adapter interface plus live adapter and fixture adapter, daily-bar storage, completed-session handling, volume baseline and price delta functions, adjustment policy and source status.

Gate: zero/negative/missing data cases, exactly-2x threshold, prior-20 exclusion, weekends, split day, provider correction, insufficient history. Unit tests offline; one separately marked live integration smoke check. No live network calls in ordinary unit tests.

## T04 — Exchange ingestion and reliable jobs

Read: IMPLEMENTATION_PLAN exchange/operations; CONTRACTS jobs/announcements.

Deliver: one functioning exchange adapter, complete pagination, interval coverage, attachment jobs, source-ID dedup, cross-source event grouping, durable worker leases, retries/circuit breaker, refresh endpoint with quotas.

Gate: failed middle page does not advance full watermark; duplicate poll emits no duplicate event; revised attachment retains previous version; worker restart recovers; source 403/429 becomes visible stale/partial state. A disabled second exchange is documented rather than faked.

## T05 — Materiality and alerts

Read: IMPLEMENTATION_PLAN section 6; classification prompt; DESIGN_SPEC Briefing/Watchlist.

Deliver: taxonomy mapping, subtype classification, deterministic ranking, high-risk overrides, persisted session-scoped rules, alert evaluation/dedup, non-notifying preview. Keep model classifier behind a feature flag until extraction output validates.

Gate: results notice below actual results; auditor distress never hidden by routine category; critical record still surfaced if classifier fails; rule edits and poll retries do not spam; price alert never attributes causation to coincident news.

## T06 — Complete briefing vertical slice

Read: DESIGN_SPEC Briefing/event/evidence/state sections; API table.

Deliver: live/replay-aware briefing, 24h/7d/custom interval, priority groups, routine expansion, source-level filing list, event detail, evidence drawer, alert inbox, settings form.

Gate: user can change date range, find a material filing, inspect source and save a threshold. Counts reconcile to records. Mobile Back restores list. Empty, stale, partial, loading and failure states are exercised, not merely coded as unused branches.

## T07 — Primary document discovery and parsing

Read: IMPLEMENTATION_PLAN fundamentals/document pipeline/retrieval; CONTRACTS evidence models.

Deliver: generic NSE company -> IR discovery -> annual report/transcript acquisition, page extraction and FTS indexing, quality/coverage manifest, bounded source URL validation. Build source fixtures across at least two different PDF layouts.

Gate: a company outside the watchlist can reach real primary documents through the generic path; scanned/corrupt input becomes a clear limitation; citations point to exact stored pages. Search snippets and secondary content never become pull evidence. Use candidate URL hints only as discovery aids, not hard-coded research answers.

## T08 — Structured extraction and financial facts

Read: IMPLEMENTATION_PLAN numerical rules; CONTRACTS extraction/system prompts and tests.

Deliver: model adapter with schema validation, extraction cache, financial-fact normalization, deterministic QoQ/YoY and result panel, token/cost instrumentation. Manually label a small gold set before changing prompts.

Gate: human checks verify company, period, scope, metric, unit and value together. Bank EBITDA stays unavailable when inappropriate. YTD does not become quarter data. Derived Q4 references both inputs. Missing data does not become zero. No unvalidated numeric prose bypasses the facts renderer.

## T09 — Guidance ledger and first research report

Read: IMPLEMENTATION_PLAN research/ledger; CONTRACTS guidance/matching/synthesis; DESIGN_SPEC Research.

Deliver: guidance extraction with speaker/target/conditions, deterministic match/assessment, four-quarter ledger for a verified company, source-backed snapshot, research job progress, citations and coverage.

Gate: original/revised guidance retained, analyst question excluded, future full-year target not marked missed, qualitative guidance not converted into invented numbers, dual-sided evidence inspectable. All demo ledger verdicts manually verified. Model failure yields partial source-backed content.

## T10 — Generalization and bounded questions

Read: IMPLEMENTATION_PLAN discovery/retrieval/demo; evaluation methodology.

Deliver: 3–5 prepared research cases, held-out evaluation on three unprepared tickers, focused question input with retrieval and citations if time allows. Add embeddings only if measured retrieval misses justify them.

Gate: no ticker-specific narrative code; no code edits during held-out run; record success/partial/failure and reasons. A new ticker with available documents must produce at least a supported useful section via the generic pipeline. Unavailable documents must not become a fabricated completed report.

## T11 — Replay and resilience

Read: IMPLEMENTATION_PLAN contingencies/replay; EVALUATION_AND_RELEASE.

Deliver: source-backed snapshot manifest, fixed replay clock, visible historical labels, no-key read-only demo if useful, failure injection tests, rate limits, session isolation and restart tests. Live and replay share domain contracts.

Gate: turning off external services leaves historical content usable and labeled; no synthetic news leaks into real demo; partial source windows are obvious; cache keys prevent cross-company or cross-as-of contamination; document injection has no authority.

## T12 — Design refinement

Read: DESIGN_SPEC in full. Inspect current screens first.

Deliver: phone/desktop screenshots, three highest-impact critique findings and fixes, touch/focus/reflow checks, final copy, loaded font and license, consistent tokens. Use the bounded design-skill-equivalent workflow; no wholesale style replacement after the vertical slices work.

Gate: all critical interactions work at 390px and keyboard; 320px and 200% zoom do not break core use; long content and missing figures do not clip; visual evidence included. Fix correctness before decorative micro-adjustments.

## T13 — Evaluation, release and history

Read: EVALUATION_AND_RELEASE and SUBMISSION_DRAFT.

Deliver: reproducible evaluation report with counts/errors, tested clean-clone README, production smoke test, truthful demo script, covering-note draft, build-history index and redacted actual conversation exports/share links. Mark every outstanding limitation.

Gate: no critical accuracy/security/usability defects in selected workflows, live link accessible without developer credentials, repo permissions verified, links work on phone, no secrets committed, user can review the final submission. Do not send the email without explicit user authorization.

## Short-context continuation prompt

```text
Continue FINN packet Txx. Read START_HERE.md, docs/BUILD_STATUS.md, the Txx
entry in IMPLEMENTATION_TASKS.md, and only its referenced sections. Inspect
existing code and tests. Preserve passed behavior. Implement the smallest
complete packet, including failure states. Run its gates and report actual
results, affected files, limitations and next packet. Do not broaden scope,
invent financial data, bypass citations or mark unrun tests as passed.
```

## Failure escalation for the coding model

After two failed fixes for the same issue, stop speculative rewrites. Capture the exact error, minimal reproduction, affected contract, attempted fixes and expected behavior in `docs/blockers/`. Continue only independent packets. Request help for genuinely blocking credentials, ambiguous requirements or infrastructure access. Routine naming, styling and implementation choices are already specified; do not ask the user to re-decide them.
