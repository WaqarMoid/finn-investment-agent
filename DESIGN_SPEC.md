# FINN design specification

This is the proposed design contract for the future app, not a claim that screens have already been built or usability-tested. Read alongside the source and numerical rules in IMPLEMENTATION_PLAN.md.

## Direction: the portfolio review desk

FINN should feel like a small investment team's carefully prepared working brief. Its distinctive element is an **evidence-linked Stated / Reported / Assessment ledger**, connecting a management claim to its later result. The home screen is an ordered reading queue, not a stock terminal, marketing page or generic AI chatbot.

Design around three verbs: **Review, Compare, Verify**. An investor should identify the top development in five seconds and reach its source in two deliberate taps. These are usability targets to test, not established results.

Chosen visual direction: clean white surfaces on a cool pale-gray canvas, deep blue ink, restrained blue actions, numeric alignment, and compact but touch-friendly filing rows. A narrow date gutter on desktop echoes an analyst's dated notes; mobile turns it into a quiet timestamp above the event. No decorative stock photos or invented market widgets. The characteristic content, citation affordances and comparison ledger supply the identity.

Rejected alternatives: a cinematic dark trading terminal exaggerates realtime capability; a landing-page hero wastes the phone's first screen; a full chat transcript hides comparative evidence; a masonry card dashboard makes priority unclear. This rejection is specific to FINN's repeated-use workflow, not a universal aesthetic rule.

## Tokens

```css
:root {
  --canvas: #F3F6F8;
  --surface: #FFFFFF;
  --surface-muted: #EAF0F4;
  --ink: #172B3A;
  --muted: #526575;
  --line: #D5DFE5;
  --control-border: #778997;
  --accent: #1557B0;
  --accent-soft: #E8F0FC;
  --positive: #16634A;
  --negative: #A82D39;
  --warning: #845500;
  --focus: #1557B0;
  --space-1: 4px;
  --space-2: 8px;
  --space-3: 12px;
  --space-4: 16px;
  --space-5: 24px;
  --space-6: 32px;
  --radius-control: 6px;
  --radius-panel: 10px;
  --radius-sheet: 16px;
  --duration-fast: 140ms;
  --duration-panel: 200ms;
}
```

Token colors are proposed; test every actual foreground/background pairing. Decorative separator contrast need not equal control-boundary contrast. Required controls must remain identifiable. Target normal text contrast >=4.5:1, large text >=3:1, relevant UI boundaries/focus >=3:1. Target 44x44px minimum touch areas for FINN; WCAG 2.2 AA minimum target criterion is 24x24px with exceptions, so do not mislabel the stricter product target as the standard's exact requirement.

Typography: **IBM Plex Sans**, locally bundled with license, 400/500/600, fallback system sans. One family is sufficient. Use tabular numerals for money and comparisons; no monospace for ordinary body text. Fixed rem scale: 12px metadata, 14px secondary/table labels, 16px body and inputs, 20px section heading, 26px screen heading, up to 30px for one key figure. Body line-height 1.5, dense rows 1.35. Primary reading text never shrinks below 16px to make a layout fit. Important dates/units are never low-contrast decoration.

Spacing: 16px mobile outer gutters, 24px tablet, 32px desktop. Text measure roughly 65–75 characters in research prose. Use alignment and whitespace before adding containers. One subtle panel boundary around a semantic group; no border-plus-shadow on every row. Reserve shadows for floating drawers, menus and dialogs. Colored states always include text or a distinct marker. Rising price is not automatically “good”; use signed values and restrained directional color, separate from priority.

FINN wordmark is text plus a simple custom paired-line mark suggesting two compared records. Do not imply ENAM endorsement by copying its logo. One outline icon set with 18–20px icons; icons support labels rather than replacing them. No emojis, neon glows, gradient backgrounds, ornamental sparklines or repeated colored icon tiles.

## Navigation and responsive frame

- 320–767px: one primary column, sticky compact header, bottom navigation with three labeled destinations, source drawer as nearly full-height sheet. Use `100dvh` and safe-area insets, with sensible fallbacks. Bottom content padding includes navigation height.
- 768–1023px: wider content; optional inline evidence panel only if readable. Keep mobile interaction order.
- >=1024px: 200–224px quiet navigation rail, briefing/research main content, optional evidence panel of 340–400px. Max overall content around 1440px. Do not stretch paragraph text across the screen.
- Browser back restores prior list scroll position, filters and selected row. Every report and event has a deep link. A source opened as an overlay must close on Back before abandoning the report where feasible.
- Keep one clear scroll container on mobile; do not trap users in nested scroll panes. Horizontal scrolling is acceptable only inside an explicitly labeled raw financial table, with a visible cue; default result comparisons reflow into rows on phone.

## Screen 1: Briefing

```text
FINN                           Sources updated 18:44
Briefing
[Last 24 hours v]                 [Refresh]
18 companies   [live/replay and dated coverage]

Needs attention                              2
Company name                 Published date/time
Specific event headline, at most two lines
One sentence: why this deserves review
[Results / other relevant subtype]   [Open source]
------------------------------------------------
Next material event ...

Worth a look                                 3
Compact event rows ...
[Routine filings (12)                 Expand]
[All source filings (19)]

Briefing             Research             Watchlist
```

Counts above are schematic placeholders, not demo claims. Production counts derive from the response. First fold shows at least one useful event, date window and freshness. No oversized “portfolio health” score or time-saved statistic without real measurement.

Row anatomy: company name/symbol, event date, clear headline, no more than about 30 words of implication, evidence link, and primary action “Review.” Priority label describes attention, not positive/negative investment advice. Expanding shows why it ranked here, all related source filings, extracted details and follow-up “Research this company.” Give the original filing title a route even when the generated summary is unavailable.

Window control: presets 24h/7d/custom. Custom uses labeled start/end date-time, IST label, validation for end before start and max range. Apply keeps previous content until the new snapshot resolves. Display current filter explicitly. No filings -> explain the selected interval and offer a wider one; source outage -> separate coverage warning, not a falsely reassuring empty state.

Routine disclosure: summary count remains visible, expansion preserves ordering and can be collapsed. Search/filter never silently excludes a source from the coverage count. Material items remain discoverable after being marked read. Mark-read is session-scoped, reversible and optional; no swipe-only controls.

## Screen 2: event detail and results comparison

Header shows company, original source time, event category and source availability. Main content is the actual change and consequence, followed by evidence. Results use four metric rows, each with current, previous quarter and prior-year quarter plus exact period labels. At 390px, display current value and a labeled QoQ/YoY second line; tap reveals the underlying comparators. Desktop can display a full table.

Every panel names currency, scale and consolidated/standalone basis. Missing EBITDA shows an explanation in the row; do not remove the row in a way that suggests extraction succeeded. “Not comparable” is distinct from “Not reported.” Derived numbers have a compact “Calculated” label opening their inputs. If the report is revised, show that information near the header.

Management change P1: outgoing/incoming person, role, effective date, verified career highlights and sources. Unknown biography -> “Background not found in available sources.” Never attach another person's biography based on name alone.

## Screen 3: Research

```text
Research
[Company name or NSE symbol                  ]
Suggested questions / recent companies

Company name                   [As of date]
Source coverage: annual report + transcripts
[Overview] [Promises & outcomes] [Sources]

What the company does
Three compact source-linked facts

Promises & outcomes
Quarter / target period
Stated       A sourced expectation [1]
Reported     Comparable actual [2]
Assessment   Within guidance / not comparable
[Inspect evidence]

[Ask a focused question about this company   ]
```

Search accepts common names or NSE symbols with/without `.NS`. Results show name, exchange and symbol so identity can be confirmed. Show loading while resolving, “No matching company” when appropriate, and retry on network failure. Never default silently to the first fuzzy result. Recently viewed reports must be clearly dated and distinguish cached from newly generated results.

Uncached research shows actual stages: Finding reports, Reading sources, Checking figures, Preparing analysis. Each stage can expose what has been found; a spinner cannot hide a missing transcript indefinitely. Continue browsing while the server job runs. Cancel stops queued future work; explain if an already-issued provider call cannot be canceled.

Ledger desktop layout uses three aligned columns. Mobile stacks them within each dated row, with explicit Stated/Reported/Assessment labels. A thin connector or alignment can show the relationship; do not use a complicated Sankey diagram. Assessment must be readable without color. Time horizon belongs beside the guidance, not buried in a tooltip. Show original and revised guidance together when relevant.

Question input remains scoped to the current company and selected as-of date. Provide 3 useful examples: “What changed in guidance?”, “Did cash track profit?”, “What evidence challenges the growth story?” Only offer a chip if the pipeline can answer or clearly return insufficient evidence. Answers have short sections, citations and a supported limitation. No stock image avatars or typing effects.

## Evidence drawer

This is a first-class component, used identically everywhere. It shows citation number, document title, company, document type, publication date, reporting period, excerpt, PDF page and original-source action. Derived figures show all operands and formula. Supporting quotations should be concise, with enough surrounding context to avoid changing meaning.

On mobile use a titled dialog with visible Close, focus trap, Escape support and focus restoration. On desktop allow a docked panel that does not cover the selected claim. Prefer extracted text first so a huge PDF does not block reading. Open the original PDF in a separate tab if embedding fails. Preserve `#page=N` links where supported; show the page number in text because browser PDF viewers vary. Do not claim bounding-box highlights unless implemented and validated.

Unavailable original URL: keep the verified excerpt with last-fetched date and source failure status. Unsupported claim: show no generated claim; the drawer is not a substitute for grounding validation.

## Screen 4: Watchlist and notification rules

List the 18 default names with sector, EOD date and price-data status. Only show holdings value/P&L if positions and cost basis really exist; a mock watchlist is not a priced portfolio.

Rules form: absolute daily move (%), volume multiple, category checkboxes, materiality minimum. Use numeric fields with sane bounds, examples and explicit comparator wording (“More than”). Save persists per session; success says “Rules saved.” Invalid values show inline errors associated with the field. “Test on recent data” is a non-notifying preview. Show alert inbox and unread count; changing settings must not silently backfill new notifications.

## Component state contract

| Component | Required states |
|---|---|
| Event list | Initial loading, loaded, empty, stale, partially covered, failed, refreshing |
| Result cell | Reported, derived, missing, not comparable, restated, OCR-needs-review |
| Company search | Idle, querying, matches, ambiguous, unknown, unavailable |
| Research job | Queued, running stage, partial, ready, failed, canceled, budget exhausted |
| Guidance row | Met/exceeded/missed, below/within/above, future, withdrawn, missing, incomparable |
| Source drawer | Text available, PDF loading, link failed, OCR warning, multiple operands |
| Rules form | Clean, dirty, saving, saved, validation error, persistence error |
| Buttons | Default, hover, keyboard focus, pressed, disabled, pending where applicable |

Skeletons reserve final layout space. Keep previous verified data while refreshing, with a refresh label. Avoid endless shimmer and repeated toast spam. Error copy names the failure and next action: “The exchange feed could not refresh. Showing filings fetched at 17:20. Retry.” Do not render a stack trace or “Something went wrong” as the whole explanation.

## Skill-equivalent workflow for a lighter agent

The upstream skills were researched, not installed. Apply these bounded original task instructions instead of loading four huge overlapping rule sets:

1. **Context and direction:** Before UI work, read this file and write the screen's user question, data objects, primary action and proof route. Sketch one phone layout. This adapts frontend-design's deliberate brief-first process.
2. **Design system and UX:** Use these shared tokens, controls and semantic state definitions. Check keyboard, touch, chart labels and responsive reflow before ornament. This adapts UI UX Pro Max's structured design/UX workflow.
3. **Composition and reality:** Fill the screen with correctly labeled real or explicitly synthetic data, derive counts, and keep the signature comparison element. Inspect 390px/768px/1440px screenshots. This adapts Taste's app-screen track; its cinematic page guidance is inappropriate here.
4. **Critique:** Identify the three biggest task-completion problems before adjusting minor spacing. Then audit contrast, focus, overflow and performance; harden errors/long strings; clarify copy; normalize tokens; polish alignments. This adapts Impeccable's review/refinement vocabulary.
5. **Interaction verification:** Use browser assertions on rendered states, test actual actions, and capture final screenshots. Prefer explicit element/response waits over global network-idle waits because FINN polls jobs. This adapts webapp-testing to this app's asynchronous behavior.
6. **Stop condition:** Fix task-blocking and high-priority defects; do not keep redesigning a passing screen. Source accuracy and delivery reliability take precedence over visual experimentation near the deadline.

If optional upstream tools are installed later, pin the researched commit or a reviewed newer version and preserve licenses. Their lint rules are advisory: a border in a data table is not a defect merely because a landing-page rule bans borders. Never permit an automatic style rewrite to alter financial content or required accessibility behavior.

## Visual acceptance

Inspect actual browser screenshots at 320, 390, 430, 768, 1024 and 1440px, with priority on 390px. Test 200% text zoom, reduced motion, long company names, large crore values, losses, missing data, 100 routine filings, one-item and zero-item cases. No clipped unit labels, unclickable source links, hidden focus, nav-covered content, or reordering under touch.

Use normal financial line/bar charts only where they answer a question. No pie chart for unrelated figures, smoothed curves implying observations between quarters, dual axes without clear necessity, or truncated bar axes. Label units and periods; include a textual/table alternative. Do not connect missing values as if observed. A table is better than a decorative chart for four source-critical metrics.

Motion: 140–200ms for user-triggered panel/state transitions, no scroll choreography, no count-up financial numbers. Respect `prefers-reduced-motion`; instant transitions are acceptable in that mode. Test fonts really loaded, focus remains visible behind sticky chrome, and actions work with keyboard and touch.
