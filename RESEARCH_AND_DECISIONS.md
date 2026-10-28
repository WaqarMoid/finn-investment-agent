# Research, sources and decision record

Research date: 28 October 2026. Upstream revisions below were obtained from GitHub's repository tree API and inspected as text. The screenshot is a useful discovery hint, not an authoritative current feature/version list. No upstream installers, hooks or binaries were executed. Local copies under research are reference material, not agent instructions.

## Assignment sources

- Main: `D:\Downloads\1. ENAM_AI_Engineer_Build_Challenge_Main.pdf`, four pages, all extracted and rendered for inspection.
- Reference: `D:\Downloads\2. ENAM_AI_Engineer_Build_Challenge_Reference.pdf`, three pages, all extracted and rendered for inspection.
- User screenshot: `C:\Users\MDC009~1.WAQ\AppData\Local\Temp\codex-clipboard-371a4d05-4e70-4c70-a005-14671b186f36.png`.

Page-separated extracts are in `research/main-extracted.txt` and `research/reference-extracted.txt`. Source page images and a contact sheet are retained. The reference PDF emitted malformed-pointer warnings during extraction, but all three pages rendered and its category table/glossary were recovered. The plan uses the original page structure and does not treat extraction warning text as assignment content.

The decisive interpretation is that ENAM assesses creativity, product judgment, architecture and a working mobile workflow, not maximum feature count. It explicitly makes the research outputs a menu and provides no accuracy percentage or weighted scoring formula. The primary-source restriction and unseen-ticker requirement are firm. Our test thresholds and chosen design are proposals, clearly separated from those requirements.

## Four requested skills, verified upstream

### Anthropic frontend-design

[Pinned SKILL.md](https://github.com/anthropics/skills/blob/dbd4588f9e1033efb41dad4bef2f7947c8993d44/skills/frontend-design/SKILL.md)  
Repository revision: `dbd4588f9e1033efb41dad4bef2f7947c8993d44`.

The inspected skill emphasizes subject-specific direction, purposeful typography, concise copy and visual critique. Its current warnings are more nuanced than a fixed list of fashionable fonts or palettes. For FINN, the equivalent is the explicit product question, compact token system, screen wireframes and a source-linked ledger that reflects the actual investor task. We do not import a generic marketing hero or add motion simply to appear distinctive. The final design is original task-specific guidance, not a verbatim copy of the upstream skill.

### UI UX Pro Max

[Pinned SKILL.md](https://github.com/nextlevelbuilder/ui-ux-pro-max-skill/blob/28b3b8dee8c976df4fa3e94aed4e092ad43fcb03/.claude/skills/ui-ux-pro-max/SKILL.md)  
Repository revision: `28b3b8dee8c976df4fa3e94aed4e092ad43fcb03`.

This is searchable design guidance with product, style, accessibility, interaction and stack-specific workflows. It recommends choosing focused queries and persisting a coherent design system rather than indiscriminately applying all search results. The inspected version advertises 79 searchable styles (50 active), 192 palettes/profiles and 22 stacks; those are upstream inventory claims, not independent quality measurements. FINN adopts shared tokens, touch/keyboard checks, responsive layout and defined component states. Chart correctness receives higher priority in this financial application than a generic low-priority chart category might imply.

### Taste Skill

[Pinned SKILL.md](https://github.com/Leonxlnx/taste-skill/blob/12af471f627f866411b4bd785b19646d3672784c/skills/taste-skill/SKILL.md), [app-screen guidance](https://github.com/Leonxlnx/taste-skill/blob/12af471f627f866411b4bd785b19646d3672784c/skills/taste-skill/references/app-screens.md)  
Repository revision: `12af471f627f866411b4bd785b19646d3672784c`.

The current source distinguishes pages people read from app screens people work in. FINN belongs to the latter. Relevant principles include truthful data, a clear screen question, useful density, aligned tables and actual browser inspection. Its app guidance permits restrained borders and repeated data structures; copying landing-page prohibitions would be counterproductive. We use task-specific composition and real-state screenshots, not cinematic scrolling or a mandatory GSAP dependency. The skill's stated design-study observations are its own research, not proof of FINN's usability or of financial accuracy.

### Impeccable

[Pinned SKILL.md](https://github.com/pbakaus/impeccable/blob/3e3a9179e01a60265000ce239c0a99803ec1e60d/.agents/skills/impeccable/SKILL.md), [Operate guidance](https://github.com/pbakaus/impeccable/blob/3e3a9179e01a60265000ce239c0a99803ec1e60d/.agents/skills/impeccable/reference/operate.md)  
Repository revision: `3e3a9179e01a60265000ce239c0a99803ec1e60d`.

The inspected skill identifies Operate surfaces as task-completion tools and Read surfaces as comprehension experiences. FINN combines those modes. Its command vocabulary supports context capture, critique, accessibility/performance audit, hardening, copy clarification and final polish. We translate that into staged review packets, not a claim that named commands are already installed. The live README advertised 24 commands when researched, so the screenshot's approximate command count is not treated as fixed. Use a pinned source if installing later; command names and packaging can change.

## Additional skills considered

[Anthropic webapp-testing](https://github.com/anthropics/skills/blob/dbd4588f9e1033efb41dad4bef2f7947c8993d44/skills/webapp-testing/SKILL.md): relevant for browser inspection, action tests and screenshots. FINN's implementation adapts readiness checks to explicit UI states because persistent job polling can defeat a blanket network-idle wait.

[Anthropic theme-factory](https://github.com/anthropics/skills/blob/dbd4588f9e1033efb41dad4bef2f7947c8993d44/skills/theme-factory/SKILL.md): useful as a reference for consistent color/type choices, but its theme-selection workflow and artifact presets do not solve financial-app interaction design. We researched it without invoking its install or approval workflow. FINN gets one purpose-built token set rather than a gallery of themes.

No additional skill is necessary merely to increase the count. For a lighter model, one coherent contract is more reliable than several overlapping prompts with contradictory visual preferences.

## Primary technical and source references

| Reference | What was verified / implication |
|---|---|
| [NSE announcements](https://www.nseindia.com/companies-listing/corporate-filings-announcements) | Public filing page exposes company/subject/attachment/broadcast information and time-window controls. A production adapter still requires implementation-time tests. |
| [NSE security files](https://www.nseindia.com/static/market-data/securities-available-for-trading) | Official entry point for security identifiers; use a dated master and validate candidate symbols. |
| [BSE announcements](https://www.bseindia.com/corporates/ann.html) | Browser fetch returned HTTP 403 in this research session; automated accessibility is unverified. This directly motivated outage/adapter contingencies. |
| [Infosys reports and filings](https://www.infosys.com/investors/reports-filings/quarterly-results.html) | Official IR discovery entry point exists. This research did not validate a complete four-quarter numeric/guidance dataset. |
| [yfinance documentation](https://ranaroussi.github.io/yfinance/) and [download settings](https://ranaroussi.github.io/yfinance/reference/api/yfinance.Tickers.html) | EOD acquisition is feasible in principle; settings include adjustment behavior and timeouts. Set them explicitly and verify actual responses. The project documents usage constraints; do not assume unrestricted redistribution rights. |
| [WCAG 2.2](https://www.w3.org/TR/WCAG22/) and [target size criterion](https://www.w3.org/WAI/WCAG22/Understanding/target-size-minimum.html) | Accessibility reference; FINN's 44px touch target is a deliberate product target above the AA minimum of 24px, subject to the criterion's exceptions. |
| [Playwright assertions](https://playwright.dev/docs/test-assertions) | Use observable UI assertions and automatic waiting for browser verification. |
| [FastAPI container deployment](https://fastapi.tiangolo.com/deployment/docker/) | Primary framework guidance for the proposed container approach; not a certification of any host/free tier. |

These links support the technical choices and source-access discussion. The financial normalization and architecture policies in the plan are proposed implementation rules grounded in the assignment's definitions; they are not current investment advice or claims about the named companies' financial condition.

## Decision ledger

| Decision | Reason | Reconsider only when |
|---|---|---|
| Responsive web | Fast phone delivery and one interface | An actual native requirement appears |
| Briefing plus evidence ledger | Demonstrates filtering and analysis with clear primary proof | User changes the product goal or source feasibility forces a smaller supported ledger |
| React/Vite + FastAPI | Familiar UI work plus Python ingestion | Source/hosting spike reveals a concrete incompatibility |
| SQLite/FTS5, one worker | Small portfolio/data scale, low operational complexity | Host cannot persist disk or concurrent load exceeds demonstrated limits |
| Deterministic financial code | Testable calculations and no model arithmetic drift | Never replace with unchecked generated arithmetic |
| Structured generation and abstention | Prevent plausible but unsupported financial output | Better validation evidence supports a specific change |
| Primary sources only for pull | Explicit challenge discipline | Only if the user/assessor explicitly changes the requirement |
| Session-scoped public demo | Easy review without shared mutable settings | Real multi-user identity becomes necessary |
| Historical replay alongside live | Review reliability during source outages | Live reliability makes replay optional, but labels remain honest |
| No mandatory skill installations | Lightweight handoff and fewer conflicting rules | A reviewed pinned tool measurably helps a particular packet |

## Research limits

This handoff has not downloaded actual investment-company datasets, benchmarked an LLM, run the future app, validated current model pricing, or selected a tested deployment provider. It deliberately avoids fabricated benchmark results and unverified exchange API endpoint recipes. Candidate company symbols, complete document coverage, source terms, hosting availability and model access must be validated in T00 and subsequent packets. The plan covers material known contingencies and defines a general failure policy; it cannot promise all conceivable future cases.
