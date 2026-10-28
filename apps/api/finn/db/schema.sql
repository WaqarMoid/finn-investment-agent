-- FINN Core Database Schema
-- Target: SQLite 3.38+ with WAL mode and FTS5 support

PRAGMA foreign_keys = ON;
PRAGMA journal_mode = WAL;
PRAGMA synchronous = NORMAL;

-- Schema migration tracking
CREATE TABLE IF NOT EXISTS schema_migrations (
    version INTEGER PRIMARY KEY,
    applied_at_utc TEXT NOT NULL,
    description TEXT NOT NULL
);

-- Companies master table
CREATE TABLE IF NOT EXISTS companies (
    id TEXT PRIMARY KEY,                       -- UUID
    legal_name TEXT NOT NULL,
    isin TEXT UNIQUE NOT NULL,                 -- e.g. INE009A01021
    sector TEXT,                               -- e.g. IT, Banking, FMCG
    fiscal_calendar TEXT NOT NULL DEFAULT 'APR_MAR', -- APR_MAR or JAN_DEC
    verified_ir_domains TEXT NOT NULL,         -- JSON array of verified domains
    identity_verified_at TEXT NOT NULL         -- ISO-8601 UTC
);

CREATE INDEX IF NOT EXISTS idx_companies_isin ON companies(isin);

-- Securities (Exchange listings & scrip mappings)
CREATE TABLE IF NOT EXISTS securities (
    id TEXT PRIMARY KEY,                       -- UUID
    company_id TEXT NOT NULL REFERENCES companies(id) ON DELETE RESTRICT,
    exchange TEXT NOT NULL,                    -- NSE or BSE
    symbol TEXT NOT NULL,                      -- e.g. INFY, 500209
    series TEXT NOT NULL DEFAULT 'EQ',
    price_provider_symbol TEXT NOT NULL,       -- e.g. INFY.NS, INFY.BO
    valid_from TEXT NOT NULL,                  -- ISO date YYYY-MM-DD
    valid_to TEXT,                             -- NULL if currently active
    UNIQUE(exchange, symbol, valid_from)
);

CREATE INDEX IF NOT EXISTS idx_securities_company ON securities(company_id);
CREATE INDEX IF NOT EXISTS idx_securities_sym_exch ON securities(exchange, symbol);

-- Company Aliases for search and resolution
CREATE TABLE IF NOT EXISTS company_aliases (
    id TEXT PRIMARY KEY,
    company_id TEXT NOT NULL REFERENCES companies(id) ON DELETE CASCADE,
    alias TEXT NOT NULL,
    alias_type TEXT NOT NULL DEFAULT 'common_name' -- common_name, previous_name, trade_name
);

CREATE INDEX IF NOT EXISTS idx_aliases_alias ON company_aliases(alias);

-- Anonymous browser sessions (for scoped watchlist & alert settings)
CREATE TABLE IF NOT EXISTS sessions (
    id TEXT PRIMARY KEY,                       -- UUID or token hash
    created_at_utc TEXT NOT NULL,
    expires_at_utc TEXT NOT NULL
);

-- Watchlist members (strictly session-isolated)
CREATE TABLE IF NOT EXISTS watchlist_members (
    session_id TEXT NOT NULL REFERENCES sessions(id) ON DELETE CASCADE,
    company_id TEXT NOT NULL REFERENCES companies(id) ON DELETE CASCADE,
    added_at_utc TEXT NOT NULL,
    PRIMARY KEY (session_id, company_id)
);

CREATE INDEX IF NOT EXISTS idx_watchlist_session ON watchlist_members(session_id);

-- Raw Source Documents (Immutable provenance)
CREATE TABLE IF NOT EXISTS source_documents (
    id TEXT PRIMARY KEY,                       -- UUID
    company_id TEXT NOT NULL REFERENCES companies(id) ON DELETE RESTRICT,
    source_type TEXT NOT NULL,                 -- exchange_filing, annual_report, earnings_transcript, etc.
    publisher TEXT NOT NULL,                   -- NSE, BSE, Infosys IR, etc.
    source_url TEXT NOT NULL,
    content_hash TEXT NOT NULL,                -- SHA-256
    file_size_bytes INTEGER NOT NULL,
    page_count INTEGER,
    published_at_utc TEXT NOT NULL,
    fiscal_period TEXT,                        -- e.g. Q4_FY24, FY2024
    local_path TEXT NOT NULL,
    fetched_at_utc TEXT NOT NULL,
    parser_version TEXT NOT NULL,
    status TEXT NOT NULL DEFAULT 'verified',   -- verified, needs_review, unavailable
    supersedes_id TEXT REFERENCES source_documents(id) ON DELETE SET NULL,
    UNIQUE(content_hash, company_id)
);

CREATE INDEX IF NOT EXISTS idx_source_docs_company ON source_documents(company_id);
CREATE INDEX IF NOT EXISTS idx_source_docs_hash ON source_documents(content_hash);

-- Source Pages (Exact 1-based PDF pages for audit and citation)
CREATE TABLE IF NOT EXISTS source_pages (
    id TEXT PRIMARY KEY,                       -- UUID
    document_id TEXT NOT NULL REFERENCES source_documents(id) ON DELETE CASCADE,
    pdf_page_1based INTEGER NOT NULL,
    printed_label TEXT,
    text_content TEXT NOT NULL,
    ocr_flag INTEGER NOT NULL DEFAULT 0,
    text_hash TEXT NOT NULL,                   -- SHA-256 of normalized text
    UNIQUE(document_id, pdf_page_1based)
);

CREATE INDEX IF NOT EXISTS idx_source_pages_doc ON source_pages(document_id);

-- Evidence Spans (Precise ground-truth quotes)
CREATE TABLE IF NOT EXISTS evidence_spans (
    id TEXT PRIMARY KEY,                       -- UUID
    page_id TEXT NOT NULL REFERENCES source_pages(id) ON DELETE CASCADE,
    start_offset INTEGER NOT NULL,
    end_offset INTEGER NOT NULL,
    excerpt TEXT NOT NULL,
    bbox_json TEXT,                            -- Optional coordinate bounding box
    verification_state TEXT NOT NULL DEFAULT 'verified' -- verified, unreviewed
);

CREATE INDEX IF NOT EXISTS idx_evidence_page ON evidence_spans(page_id);

-- Text Chunks for Full-Text Search
CREATE TABLE IF NOT EXISTS document_chunks (
    id TEXT PRIMARY KEY,                       -- UUID
    document_id TEXT NOT NULL REFERENCES source_documents(id) ON DELETE CASCADE,
    company_id TEXT NOT NULL REFERENCES companies(id) ON DELETE CASCADE,
    page_start INTEGER NOT NULL,
    page_end INTEGER NOT NULL,
    section TEXT,
    text_content TEXT NOT NULL,
    token_estimate INTEGER NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_chunks_company ON document_chunks(company_id);

-- Virtual FTS5 table for document chunk search
CREATE VIRTUAL TABLE IF NOT EXISTS chunks_fts USING fts5(
    chunk_id UNINDEXED,
    company_id UNINDEXED,
    section,
    text_content,
    tokenize = 'porter unicode61'
);

-- Exchange Announcements
CREATE TABLE IF NOT EXISTS announcements (
    id TEXT PRIMARY KEY,                       -- UUID
    company_id TEXT NOT NULL REFERENCES companies(id) ON DELETE RESTRICT,
    exchange TEXT NOT NULL,                    -- NSE or BSE
    source_id TEXT NOT NULL,                   -- seq_id from exchange API
    published_at_utc TEXT NOT NULL,
    fetched_at_utc TEXT NOT NULL,
    original_title TEXT NOT NULL,
    attachment_url TEXT,
    category TEXT NOT NULL DEFAULT 'unclassified',
    subtype TEXT,
    stage TEXT,                                -- notice, proposed, approved, completed, revised
    document_id TEXT REFERENCES source_documents(id) ON DELETE SET NULL,
    event_group_id TEXT,
    parse_status TEXT NOT NULL DEFAULT 'parsed',
    UNIQUE(exchange, source_id)
);

CREATE INDEX IF NOT EXISTS idx_announcements_company ON announcements(company_id);
CREATE INDEX IF NOT EXISTS idx_announcements_pub_dt ON announcements(published_at_utc);

-- Priority Event Groups (Canonical grouped events)
CREATE TABLE IF NOT EXISTS event_groups (
    id TEXT PRIMARY KEY,                       -- UUID
    company_id TEXT NOT NULL REFERENCES companies(id) ON DELETE RESTRICT,
    kind TEXT NOT NULL,                        -- results, m_and_a, distress, dividend, etc.
    event_date TEXT NOT NULL,                  -- Canonical date YYYY-MM-DD
    headline TEXT NOT NULL,
    implication TEXT NOT NULL,
    ranked_tier TEXT NOT NULL,                 -- needs_attention, worth_a_look, routine
    score REAL NOT NULL,
    reasons_json TEXT NOT NULL,                -- Breakdown of scoring components
    rule_version TEXT NOT NULL,
    created_at_utc TEXT NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_event_groups_tier ON event_groups(ranked_tier, event_date);

-- Daily EOD Price & Volume Bars
CREATE TABLE IF NOT EXISTS price_bars (
    id TEXT PRIMARY KEY,                       -- UUID
    security_id TEXT NOT NULL REFERENCES securities(id) ON DELETE CASCADE,
    provider TEXT NOT NULL,                    -- yfinance, official_exchange
    session_date TEXT NOT NULL,                -- YYYY-MM-DD
    open_price TEXT NOT NULL,                  -- Decimal string
    high_price TEXT NOT NULL,
    low_price TEXT NOT NULL,
    close_price TEXT NOT NULL,
    adjusted_close TEXT,
    volume INTEGER NOT NULL,
    action_flags TEXT,                         -- dividend, split, etc.
    fetched_at_utc TEXT NOT NULL,
    revision INTEGER NOT NULL DEFAULT 1,
    UNIQUE(provider, security_id, session_date, revision)
);

CREATE INDEX IF NOT EXISTS idx_price_bars_sec_date ON price_bars(security_id, session_date);

-- Normalized Financial Facts (Deterministic operands)
CREATE TABLE IF NOT EXISTS financial_facts (
    id TEXT PRIMARY KEY,                       -- UUID
    company_id TEXT NOT NULL REFERENCES companies(id) ON DELETE RESTRICT,
    metric_key TEXT NOT NULL,                  -- revenue_from_operations, pat, ebitda, pbt
    source_label TEXT NOT NULL,
    value_decimal TEXT,                        -- Decimal string (NULL if unavailable)
    original_unit TEXT NOT NULL,               -- crore, lakh, million, percentage
    original_value TEXT NOT NULL,
    currency TEXT NOT NULL DEFAULT 'INR',
    normalized_unit TEXT NOT NULL DEFAULT 'crore',
    period_start TEXT NOT NULL,                -- YYYY-MM-DD
    period_end TEXT NOT NULL,                  -- YYYY-MM-DD
    period_type TEXT NOT NULL,                 -- quarter, half_year, nine_months, annual
    fiscal_label TEXT NOT NULL,                -- e.g. Q4_FY24, FY24
    scope TEXT NOT NULL,                       -- consolidated, standalone
    status TEXT NOT NULL,                      -- reported, derived, restated, unavailable
    missing_reason TEXT,
    evidence_ids_json TEXT NOT NULL,           -- JSON array of evidence_span IDs
    derivation_id TEXT,
    created_at_utc TEXT NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_facts_lookup ON financial_facts(company_id, metric_key, fiscal_label, scope);

-- Financial Derivations (Audit trail for calculated QoQ/YoY/EBITDA)
CREATE TABLE IF NOT EXISTS derivations (
    id TEXT PRIMARY KEY,                       -- UUID
    formula_key TEXT NOT NULL,                 -- qoq_growth, yoy_growth, ebitda_calc
    formula_version TEXT NOT NULL DEFAULT '1.0',
    operand_fact_ids_json TEXT NOT NULL,       -- JSON array of financial_fact IDs
    result_decimal TEXT NOT NULL,
    comparability_result TEXT NOT NULL,        -- valid, scope_mismatch, restated_warning
    rounding_policy TEXT NOT NULL DEFAULT 'round_2_decimals'
);

-- Management Guidance Statements
CREATE TABLE IF NOT EXISTS guidance_statements (
    id TEXT PRIMARY KEY,                       -- UUID
    company_id TEXT NOT NULL REFERENCES companies(id) ON DELETE RESTRICT,
    metric TEXT NOT NULL,                      -- revenue_growth, operating_margin, capex
    speaker_role TEXT NOT NULL,                -- CEO, CFO
    speaker_name TEXT,
    stated_at_utc TEXT NOT NULL,
    target_period TEXT NOT NULL,               -- e.g. FY25, Q1_FY25
    low_decimal TEXT,
    high_decimal TEXT,
    unit TEXT NOT NULL,                        -- percentage, crore
    currency TEXT NOT NULL DEFAULT 'INR',
    basis TEXT NOT NULL,                       -- constant_currency, reported
    qualitative_text TEXT,
    conditions TEXT,
    evidence_ids_json TEXT NOT NULL,
    status TEXT NOT NULL DEFAULT 'original',   -- original, revised, withdrawn
    revises_id TEXT REFERENCES guidance_statements(id) ON DELETE SET NULL,
    created_at_utc TEXT NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_guidance_company ON guidance_statements(company_id, target_period);

-- Guidance Assessments (Met / Exceeded / Missed Ledger)
CREATE TABLE IF NOT EXISTS guidance_assessments (
    id TEXT PRIMARY KEY,                       -- UUID
    guidance_id TEXT NOT NULL REFERENCES guidance_statements(id) ON DELETE CASCADE,
    outcome_fact_ids_json TEXT NOT NULL,       -- Operand financial_facts
    assessment TEXT NOT NULL,                  -- met, exceeded, missed, not_due, not_comparable, withdrawn
    explanation TEXT NOT NULL,
    evidence_ids_json TEXT NOT NULL,
    rule_version TEXT NOT NULL,
    as_of_date TEXT NOT NULL,
    created_at_utc TEXT NOT NULL
);

-- Session-Scoped Notification Rules
CREATE TABLE IF NOT EXISTS notification_rules (
    session_id TEXT NOT NULL REFERENCES sessions(id) ON DELETE CASCADE,
    rule_id TEXT NOT NULL,
    version INTEGER NOT NULL DEFAULT 1,
    enabled INTEGER NOT NULL DEFAULT 1,
    price_pct REAL NOT NULL DEFAULT 5.0,
    volume_multiple REAL NOT NULL DEFAULT 2.0,
    lookback_sessions INTEGER NOT NULL DEFAULT 20,
    categories_json TEXT NOT NULL,             -- JSON array of tracked categories
    min_materiality TEXT NOT NULL DEFAULT 'worth_a_look',
    updated_at_utc TEXT NOT NULL,
    PRIMARY KEY(session_id, rule_id)
);

-- Generated Alerts (Scoped to session inbox)
CREATE TABLE IF NOT EXISTS alerts (
    id TEXT PRIMARY KEY,                       -- UUID
    session_id TEXT NOT NULL REFERENCES sessions(id) ON DELETE CASCADE,
    rule_id TEXT NOT NULL,
    rule_version INTEGER NOT NULL,
    company_id TEXT NOT NULL REFERENCES companies(id) ON DELETE CASCADE,
    source_event_id TEXT,
    source_type TEXT NOT NULL,                 -- filing, price_move, volume_spike
    reason TEXT NOT NULL,
    created_at_utc TEXT NOT NULL,
    acknowledged_at_utc TEXT,
    dedup_key TEXT UNIQUE NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_alerts_session ON alerts(session_id, acknowledged_at_utc);

-- Durable Background Jobs
CREATE TABLE IF NOT EXISTS jobs (
    id TEXT PRIMARY KEY,                       -- UUID
    job_type TEXT NOT NULL,                    -- nse_poll, eod_sync, research_task
    dedup_key TEXT UNIQUE NOT NULL,
    session_id TEXT REFERENCES sessions(id) ON DELETE SET NULL,
    company_id TEXT REFERENCES companies(id) ON DELETE SET NULL,
    status TEXT NOT NULL DEFAULT 'queued',     -- queued, running, partial, succeeded, failed, canceled
    stage TEXT NOT NULL DEFAULT 'initialized',
    attempt_count INTEGER NOT NULL DEFAULT 0,
    lease_until_utc TEXT,
    heartbeat_utc TEXT,
    progress_detail_json TEXT,
    output_id TEXT,
    error_message TEXT,
    created_at_utc TEXT NOT NULL,
    updated_at_utc TEXT NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_jobs_status_lease ON jobs(status, lease_until_utc);

-- Ingestion Sync History
CREATE TABLE IF NOT EXISTS sync_runs (
    id TEXT PRIMARY KEY,                       -- UUID
    adapter TEXT NOT NULL,                     -- nse_announcements, yahoo_eod
    requested_start TEXT NOT NULL,
    requested_end TEXT NOT NULL,
    status TEXT NOT NULL,                      -- completed, partial, failed
    counts_json TEXT NOT NULL,
    error_message TEXT,
    fetched_at_utc TEXT NOT NULL
);
