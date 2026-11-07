-- BRSR ESG pipeline: database schema (SQLite)
-- Layers: reference -> bronze -> silver -> gold
-- Safe to run many times: every table uses IF NOT EXISTS.

PRAGMA foreign_keys = ON;

-- ============ REFERENCE ============

-- One row per company. ISIN is the unique ID found in every XBRL file.
CREATE TABLE IF NOT EXISTS companies (
    isin            TEXT PRIMARY KEY,          -- e.g. INE481G01011
    name            TEXT NOT NULL,
    sector          TEXT,                      -- we add this ourselves, e.g. 'Cement'
    cin             TEXT,                      -- company registration number
    website         TEXT
);

-- One row per metric we track. Loaded from config/metric_catalog.csv.
-- Adding a new label = adding a row here. No code changes needed.
CREATE TABLE IF NOT EXISTS metric_catalog (
    metric          TEXT PRIMARY KEY,          -- e.g. scope1_emissions
    xbrl_tag        TEXT NOT NULL,             -- e.g. TotalScope1Emissions
    standard_unit   TEXT NOT NULL,             -- e.g. tCO2e
    category        TEXT NOT NULL,             -- energy / emissions / water / waste
    brsr_core       TEXT,                      -- BRSR Core attribute, if any
    description     TEXT
);

-- ============ BRONZE: raw files ============

-- One row per company per financial year: what we downloaded and where.
CREATE TABLE IF NOT EXISTS filings (
    filing_id       INTEGER PRIMARY KEY AUTOINCREMENT,
    isin            TEXT,                      -- filled once the XBRL is read
    company_name    TEXT NOT NULL,
    fy_end          TEXT NOT NULL,             -- e.g. 2026-03-31
    pdf_url         TEXT,
    xbrl_url        TEXT,
    pdf_path        TEXT,
    xbrl_path       TEXT,
    downloaded_at   TEXT,
    status          TEXT NOT NULL DEFAULT 'listed',
                    -- listed -> downloaded -> extracted -> standardised -> checked
    error           TEXT,
    UNIQUE (company_name, fy_end)
);

-- ============ SILVER: extracted, unchanged ============

-- Every fact from every XBRL file, exactly as the company wrote it.
CREATE TABLE IF NOT EXISTS xbrl_facts (
    fact_id         INTEGER PRIMARY KEY AUTOINCREMENT,
    filing_id       INTEGER NOT NULL REFERENCES filings(filing_id),
    tag             TEXT NOT NULL,
    value           TEXT,
    context         TEXT,                      -- e.g. DCYMain (current year)
    period_end      TEXT,                      -- e.g. 2026-03-31
    has_dimensions  INTEGER NOT NULL DEFAULT 0, -- 1 = a breakdown, 0 = company total
    unit            TEXT
);
CREATE INDEX IF NOT EXISTS idx_facts_filing_tag ON xbrl_facts (filing_id, tag);

-- Every value the LLM read from a PDF.
CREATE TABLE IF NOT EXISTS pdf_extractions (
    extraction_id   INTEGER PRIMARY KEY AUTOINCREMENT,
    filing_id       INTEGER NOT NULL REFERENCES filings(filing_id),
    metric          TEXT NOT NULL,
    value           REAL,
    unit_as_written TEXT,
    model           TEXT,                      -- e.g. llama3.1:8b
    extracted_at    TEXT
);

-- ============ GOLD: clean, ready for analysis ============

-- One row per company + year + metric + period. Long format on purpose.
CREATE TABLE IF NOT EXISTS metrics (
    filing_id       INTEGER NOT NULL REFERENCES filings(filing_id),
    metric          TEXT NOT NULL REFERENCES metric_catalog(metric),
    period          TEXT NOT NULL,             -- 'current' or 'previous'
    source          TEXT NOT NULL,             -- 'xbrl' or 'pdf'
    value           REAL,                      -- in the standard unit
    status          TEXT NOT NULL,             -- reported / zero / not_applicable / missing
    PRIMARY KEY (filing_id, metric, period, source)
);

-- One row per quality rule checked.
CREATE TABLE IF NOT EXISTS quality_checks (
    check_id        INTEGER PRIMARY KEY AUTOINCREMENT,
    filing_id       INTEGER NOT NULL REFERENCES filings(filing_id),
    dimension       TEXT NOT NULL,             -- accuracy / completeness / consistency /
                                               -- validity / uniqueness / integrity
    rule            TEXT NOT NULL,             -- e.g. renewable_le_total_energy
    passed          INTEGER NOT NULL,          -- 1 = pass, 0 = fail
    details         TEXT,
    checked_at      TEXT
);

-- One row per company + year + dimension: the scorecard.
CREATE TABLE IF NOT EXISTS quality_scores (
    filing_id       INTEGER NOT NULL REFERENCES filings(filing_id),
    dimension       TEXT NOT NULL,
    score           REAL NOT NULL,             -- 0 to 1
    PRIMARY KEY (filing_id, dimension)
);
