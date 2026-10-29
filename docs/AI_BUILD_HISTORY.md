# AI Build History & Agent Interaction Record

This document records the full interaction history and progression of the coding agent across the entire challenge.

## 1. Conversation History & Planning Links

The AI build process comprised two phases: upfront architecture/planning and end-to-end coding execution.

1. **Architecture & Planning Conversation (ChatGPT):**
   - **Shared Conversation Link:** [https://chatgpt.com/s/cx_6ae2e567879881919375559c9eedc46e](https://chatgpt.com/s/cx_6ae2e567879881919375559c9eedc46e)
   - Scope: Specification design, data contracts, taxonomy definition, and execution packet planning (`T00`–`T13`).

2. **Implementation & Verification Conversation (Antigravity):**
   - **Full Raw Transcript (JSONL):** [https://github.com/WaqarMoid/finn-investment-agent/blob/master/docs/ai_build_history_transcript.jsonl](https://github.com/WaqarMoid/finn-investment-agent/blob/master/docs/ai_build_history_transcript.jsonl)
   - **Verification & Status Ledger:** [https://github.com/WaqarMoid/finn-investment-agent/blob/master/docs/BUILD_STATUS.md](https://github.com/WaqarMoid/finn-investment-agent/blob/master/docs/BUILD_STATUS.md)
   - Scope: Implementation of all 14 packets, 71 automated tests, and mobile vertical slices.

## 2. Packet Progression Summary

1. **Packet T00 — Feasibility Spike:**
   - Evaluated 3 primary sources: Yahoo Finance EOD, NSE Corporate Announcements API, and Infosys IR annual reports/earnings call transcripts.
   - Live network checks verified HTTP 200 on NSE and Infosys PDF download (284 KB). Documented Cloudflare 403 on BSE.
2. **Packet T01 — Monorepo Architecture & Mobile Shell:**
   - Set up React 18 + Vite 5 + TypeScript SPA frontend and FastAPI Python backend.
   - Built 390px mobile-first responsive layout with bottom navigation (Briefing, Research, Watchlist).
3. **Packet T02 — Database & Identity Backbone:**
   - Created SQLite database schema with WAL mode and foreign key constraints.
   - Implemented `CompanyResolver` handling symbols, ISINs, BSE codes, and aliases without fuzzy hallucination.
   - Built session-isolated watchlist storage.
4. **Packet T03 — Deterministic Financial Price & Volume Math:**
   - Implemented strict >5.0% price move and >2.0x volume spike logic against prior 20 completed sessions.
   - Added split/dividend adjustment policy and non-causal price alert phrasing.
5. **Packet T04 — Exchange Ingestion & Reliable Background Jobs:**
   - Implemented NSE announcement adapter with pagination, attachment downloading, and duplicate filtering.
   - Built durable SQLite job leases (`BEGIN IMMEDIATE`) with automatic crash recovery.
6. **Packet T05 — Materiality Ranking & Alert Engine:**
   - 17-category classification taxonomy with deterministic safety overrides (insolvency, auditor resignation elevated).
   - Session-scoped notification rules with alert deduplication.
7. **Packet T06 — Briefing Vertical Slice:**
   - Built interactive Briefing screen with 24h/7d/custom windows, count reconciliation (all 20 filings accounted for), and live Evidence Drawer.
8. **Packet T09 — 4-Quarter Guidance Ledger (Signature Feature):**
   - Extracted management forward guidance and matched against reported results deterministically.
   - Assigned auditable verdicts (*Met*, *Exceeded*, *Missed*, *Not Due*, *Qualitative Supported*).
   - Provided dual-sided evidence inspector with exact PDF page numbers and verbatim quotes.
9. **Packet T10 — Generalization Across Held-Out Tickers:**
   - Tested pipeline across 3 unseen tickers (`COFORGE`, `DIXON`, `ASTRAL`) from different sectors.
   - Verified that missing documents result in honest policy limitations rather than fabricated data.
10. **Packet T11 — Replay Mode & Resilience:**
    - Added historical replay clock (`FINN_MODE=replay`) with fixed cutoff date (`2024-10-18`).
    - Added rate-limiting (HTTP 429 on rapid refresh) and tested failure injection without database corruption.
11. **Packet T12–T13 — Evaluation, README & Release:**
    - Full regression run (71/71 tests passing).
    - Production build compiled with zero errors.
