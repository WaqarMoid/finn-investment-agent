# Accuracy, product quality and release gates

ENAM does not provide numerical scoring weights. The following are proposed internal thresholds to make the submission inspectable. They do not establish universal accuracy, guarantee a hiring outcome, or replace manual review.

## 1. Build the gold set before tuning

Use public primary documents with a manifest of company, source URL/hash, PDF page, source excerpt and labeler decision. Keep synthetic fixtures for edge cases in a separate directory. Never label synthetic data as a real filing.

Suggested feasible set: 60 announcements covering routine and material subtypes; 60 financial cells across at least three companies and two table layouts; 20 guidance statements/outcomes including revisions, qualitative and future targets; 20 questions with both answerable and unanswerable cases. Reuse documents to control cost. Add sector-specific and OCR stress cases if available. Split by document/company where possible so train/dev examples do not leak into held-out tests. Lock test labels before prompt tuning and record changes.

Human verification must inspect the primary page, not merely agree with the model. A second reviewer is helpful if available; if one person labels everything, disclose that limitation. Save disagreements and ambiguous labels instead of forcing certainty.

## 2. Metrics and gates

| Area | How to measure | Proposed release gate |
|---|---|---|
| Critical demo figures | Exact tuple: entity, period, scope, metric, value, unit, source | 100% manually checked for the showcased workflows |
| Extraction accuracy | Correct extracted tuples / extracted tuples, plus supported-gold coverage | >=98% on the labeled subset; report numerator/denominator and missingness |
| Numerical calculations | Deterministic outputs against independent known vectors | 100% relevant test vectors pass |
| Citation validity | Referenced IDs/pages/spans resolve to allowed company source | 100% published demo claims |
| Citation support | Human judgment that each atomic factual claim follows from evidence | Zero unsupported critical demo claims; report all observed defects elsewhere |
| Materiality recall | True material filings surfaced / gold material filings | >=95% on the small labeled set; zero misses for defined critical override cases |
| Precision / noise | True material / all surfaced-as-material; routine reduction | Report alongside recall; never optimize noise by hiding severe events |
| Guidance matching | Correct metric/horizon/basis pairings and verdicts / assessed pairs | 100% demo pairs reviewed; report held-out performance separately |
| Abstention | Correct refusal on unanswerable cases; supported answers on answerable cases | All deliberate no-evidence tests abstain; report answer coverage to prevent empty-answer gaming |
| Generalization | Unprepared companies handled without code edits | Three held-out runs, at least one useful supported new-company report; disclose partial/failure cases |
| Filing coverage | Source pages completed and ingested record counts reconciled | No undisclosed missing interval/page in displayed coverage |
| Idempotency | Repeat ingest/rule evaluation/restart | Zero duplicate source IDs or repeated same-rule event alerts |
| Accessibility | Automated scan + manual keyboard/touch/screen-reader checks | No critical/serious automated findings in core flows; manual checks pass |
| UI reliability | End-to-end critical journeys | 100% selected journeys pass on release build |
| Performance | Cached and uncached measured separately | Cached content target <2s; uncached progress visible promptly and bounded completion/failure |

A 98% result on 60 observations is a coarse estimate, not evidence of production-wide reliability. Report sample sizes, scope and failure examples; avoid claims such as “99.9% accurate.” Include extraction coverage separately from precision: a system returning one perfect cell out of 60 has not succeeded.

## 3. Test layers

**Unit:** financial formulas, unit conversions, fiscal periods, timezone intervals, category/ranking overrides, guidance comparator semantics, source-policy guards, cache-key versions, alert thresholds and dedup keys.

**Contract/integration:** captured exchange responses, pagination, malformed HTML, missing attachment, source URL validation, model invalid JSON, citation-ID checking, persistence migrations, worker leases, restart recovery, document-version invalidation. Fake adapters for deterministic CI; live provider smoke checks are separately labeled and never required for ordinary offline unit tests.

**End-to-end:** user-visible behavior using Playwright role/label locators, controlled clock and fixture data. Wait on expected UI states/requests, not arbitrary sleeps. Polling means global network-idle is often the wrong readiness condition. Test the production build, not only dev server.

**Manual/source:** original PDF versus extracted cells, guidance meaning and horizon, negative/zero denominators, qualitative interpretations, sector mismatches, IR entity identity. A second model cannot prove financial truth.

## 4. Required regression cases

1. Last-24h interval across IST midnight and exact inclusive start/exclusive end.
2. Weekend/holiday displays last completed EOD session without a false freshness claim.
3. Default 18 names validated, and a non-demo NSE ticker resolves without a new code branch.
4. Ambiguous company name requires identity choice; an invalid ticker never maps silently.
5. Results meeting notice is routine while actual results are prioritized.
6. Routine bucket expands to original source filings; counts reconcile despite event grouping.
7. Serious auditor/regulatory event survives low model confidence and unclassified category.
8. Duplicate NSE/BSE announcement groups retain both links; a revision retains earlier version.
9. Failed pagination exposes partial coverage and leaves watermark recoverable.
10. Exactly-threshold price/volume does not trigger when policy is strict greater-than.
11. Volume baseline excludes today; zero baseline and missing days are handled explicitly.
12. Split/bonus day does not generate an unexplained abnormal-price alert.
13. Rule save persists after reload and remains isolated from another session.
14. Preview creates no alerts; retries emit no duplicate notifications.
15. Consolidated/standalone/YTD/current-quarter columns cannot cross-match.
16. INR lakh/crore and USD/constant-currency figures remain distinguishable.
17. Negative prior PAT yields loss wording, not a misleading growth percentage.
18. No reported EBITDA leads to unavailable or explicitly supported derivation.
19. Bank/insurer research does not reuse an unsuitable industrial-company EBITDA template.
20. Q4 subtraction requires matching FY/9M basis and carries both citations.
21. A scanned or encrypted PDF does not produce invented facts.
22. Analyst's suggested number is not management guidance.
23. Full-year guidance is not scored against one quarter; future targets stay not due.
24. Revised guidance shows original and revision; post-outcome recap is not prior guidance.
25. A capex underspend/overspend is not automatically good/bad.
26. A valid citation to a wrong company, period or unsupported claim is rejected.
27. Historical as-of research excludes sources published later than the cutoff.
28. A malicious PDF instruction to ignore rules/reveal keys has no effect.
29. Private-network URL/redirect and oversized file ingestion are rejected.
30. No provider key/quota/timeout produces labeled partial/replay behavior, not fake live answers.
31. Worker restart recovers leased work without duplicate artifacts.
32. A newly ingested revision invalidates affected latest caches but preserves old as-of provenance.
33. Live and replay modes show different dates honestly; synthetic fixtures cannot appear in production replay.
34. Research drawer opens, closes with Escape/Back and restores focus/scroll.
35. Small phone, long company name, huge number, negative result and 200% text zoom remain usable.
36. No document supports the answer -> explicit missing evidence, not confident model memory.

## 5. Five critical journeys

**Morning review:** open phone URL -> understand selected interval and coverage -> inspect top event -> open original source -> return with position preserved -> expand routine filings.

**Alert tuning:** open rules -> change volume multiple -> reject invalid input -> save -> preview matches without notifications -> refresh data -> inspect one deduped alert.

**Company research:** search a company -> confirm identity -> observe real job stages -> read snapshot -> inspect both sides of a guidance comparison -> see missing evidence honestly.

**New ticker:** choose an unprepared security -> discover primary material -> produce useful supported analysis or a precise coverage limitation -> no per-company code edit.

**Failure/recovery:** disconnect provider -> stale banner plus available evidence -> no infinite spinner -> retry or replay -> restored live data has a new timestamp without losing preferences.

## 6. Usability and visual review

Ask a tester to identify the most important event, explain why it matters, find its evidence and describe a guidance outcome. Record time and errors rather than asking only “Does it look good?” Proposed targets: top change identifiable within 5 seconds, source within 2 taps, core briefing review within roughly 60–90 seconds. Failure suggests hierarchy or wording fixes, not automatically more features.

Inspect screenshots at all DESIGN_SPEC widths, plus keyboard focus and reduced motion. Check actual loaded fonts, table alignment, units, wrapping, nav safe areas and dialog scroll. Run an accessibility scanner, then manually test keyboard, VoiceOver/TalkBack where available and one real phone. A perfect automated score does not establish accessibility.

Performance: capture device/network conditions, cold versus warm start, request latencies, parse time, model time, cache hit rate and cost per complete research report. Proposed lab targets: LCP <=2.5s for cached first screen under stated test conditions, CLS <=0.1, responsive interactions around <=200ms. Do not report lab measurements as field Core Web Vitals. Cold free-tier boot delays must be disclosed or eliminated for review.

## 7. Release runbook

1. Freeze features; resolve critical source/number/interaction defects before visual polish.
2. Run formatting/lint, frontend typecheck/build, backend unit/integration tests, contract checks, end-to-end journeys and gold evaluation.
3. Export a dated evaluation report with sample sizes and observed limitations; review every number in the three-minute demo.
4. Build from a clean clone using README alone. Install from lockfiles; migrate/seed; verify no secrets or host-specific paths are required.
5. Deploy release artifact to a host with verified persistence/worker support. Restart once and verify DB/raw documents/jobs survive. Test direct deep links and readiness.
6. Open phone URL in private browsing without developer cookies. Confirm normal reader needs no private API credentials. Verify source links and replay labels.
7. Run secret scan and inspect Git history/exports for credentials and private data. Redact secrets while preserving authentic build history; record redactions.
8. Verify repository access for assessors, complete README, source manifests, limitations, screenshots, demo script, exact setup commands and dependency licenses.
9. Review the covering note: replace all placeholders, state actual tradeoffs, separate implemented behavior from future work. Never claim external connectors or accuracy levels that were not tested.
10. User reviews and authorizes final email. Recipient and subject come from the brief. Deadline time is unspecified; do not invent a midnight cutoff.

No critical failure may be hidden behind a prerecorded demo. A short recording is a fallback aid alongside the working link and reproducible repository, not a replacement for them.
