# FINN research and mobile UI audit — 29 October 2026

## Brief and design decisions

The ENAM main brief evaluates product judgment and a thin working mobile-first prototype more than feature breadth. Pull research must use primary annual reports and concall transcripts, expose source-backed claims, and disclose gaps. Its eight suggested research outputs are a menu, not a requirement to populate every screen with unsupported prose. The reference PDF defines financial terms and comparison conventions; it does not authorize inventing data.

I reviewed the official Emil Kowalski design-engineering skill, Taste skill, and Impeccable. Their useful principles here are: clear task focus and interaction states (Emil); mobile app density, restrained palette, and screenshot review at multiple widths (Taste); and targeted critique and cleanup of component hierarchy (Impeccable). FINN therefore uses a quieter mobile navigation bar, fewer decorative controls, flat issuer monograms, compact research hierarchy, and source-backed microcopy. Figma MCP was not connected, so Playwright screenshots and direct CSS inspection were the equivalent visual QA path.

Sources: [Emil design engineering](https://github.com/emilkowalski/skills/blob/main/skills/emil-design-eng/SKILL.md), [Taste](https://github.com/Leonxlnx/taste-skill/blob/main/skills/taste-skill/SKILL.md), [Impeccable](https://github.com/pbakaus/impeccable).

## Faults found and changes made

- The former eight-module report came from a ticker-specific in-code catalog. Its answers could cite IDs that did not exist. The API now omits that uncited analysis and free-form questions return exact indexed excerpts with an evidence drawer link, or a clear coverage gap. It does not synthesize unsupported conclusions.
- Coforge and Dixon previously showed zero guidance. Exact statements from issuer-hosted Q4 FY26 earnings-call PDFs are indexed with physical PDF page numbers (Coforge p. 8; Dixon p. 14). Guidance remains **not due** until a comparable reported outcome is verified. Astral now has an official annual-report source link but no claimed guidance or financial figures.
- The research composer now precedes the source/fact/guidance tabs. Example questions are optional; users can enter any focused question. The briefing title is “Portfolio pulse.” Legacy Google Fonts loading was removed; the locally bundled Inter font remains.
- The UI shows actual coverage counts rather than a decorative four-stage completion bar. The mobile navigation no longer floats over the page, and buttons, hierarchy, and issuer marks were simplified.
- Briefing now opens routine items by default and shows the underlying filing summary; previously a nonzero event count could lead to a screen with no visible event. Watchlist-to-Research links now carry the selected ticker and survive reload. Alert labels and Watchlist copy were simplified.

## Verified source material

- [Coforge Q4 FY26 earnings-call transcript](https://investors.coforge.com/hubfs/Coforge-Limited-Earnings-Call-Transcript-Q4FY26%20_AJ.pdf?hsLang=en): PDF page 8 states FY27 FCF/PAT of 100% versus earlier 70–80%, and consolidated EBITDA margin of 20.5–21% including Encora.
- [Dixon Q4 FY26 earnings-call transcript](https://dixon-website.s3.ap-south-1.amazonaws.com/uploads/17eb4df3-5044-40f5-b3c4-3def219cbd19-EarningTranscriptQ4FY26.pdf): PDF page 14 states an approximate FY27 revenue target of INR 56,000 crore excluding Vivo, with flat mobile volume assumed.
- [Astral official annual reports](https://www.astralltd.com/investors/report-accounts/): source discovery only; no page-level excerpt is currently indexed.

## Validation

- `python -m unittest discover -s tests`: 72 passing, including mobile Playwright tests and issuer evidence/citation checks.
- `npm run build` in `apps/web`: successful TypeScript and production Vite build.
- Local Playwright visual check: 320, 390, 768, and 1440 px, light and dark; zero horizontal overflow. On 390 px, custom Coforge cash-conversion question returned an excerpt, its citation opened the evidence drawer, and the PDF page was 8. Final screenshots are in `docs/ui-review`.
- The 390 px Watchlist-to-Research browser flow opens TCS rather than resetting to INFY. Briefing and Watchlist were also screenshot-reviewed in light and dark.

## Remaining scope and truthful limitations

This is an evidence-safe vertical slice, not a full automated analyst. For many NSE symbols there is issuer identity but no automatically parsed annual report/transcript; free-form questions may correctly return “cannot answer.” Coforge and Dixon have guidance statements but no verified FY27 outcome assessment. BSE automated retrieval is unavailable. The old ticker-specific module catalog was removed. A future generic analyzer could restore additional modules when source coverage supports them. The live Render service must redeploy this commit before these changes appear remotely.
