# Architecture

## Goal
Check the **quality** of Indian companies' BRSR sustainability disclosures:
are they complete, consistent, valid and believable, and how do companies compare?

BRSR is a **disclosure** framework set by SEBI: it says what listed companies must
report, not how much they may pollute. So this project measures disclosure quality,
not legal breaches.

## Data flow

```
NSE website
   │
   ▼
[Ingest] ──────────► BRONZE   raw PDF + XBRL files, `filings` table
   │
   ├─► [XBRL parser] ─┐
   │                  ├──► SILVER   `xbrl_facts`, `pdf_extractions` (unchanged)
   └─► [PDF + LLM] ───┘     (optional cross-check)
                      │
                      ▼
               [Standardise] ──► GOLD   `metrics` (standard units + status)
                      │
                      ▼
               [Quality checks] ──► `quality_checks`, `quality_scores`
                      │
                      ▼
               [Analysis] ──► dashboard, write-up
```

## Layers

| Layer | Holds | Rule |
|---|---|---|
| Bronze | Downloaded files + a log of each filing | Never edited. Everything can be rebuilt from here |
| Silver | Every extracted value, exactly as written | No cleaning, so we can always trace back |
| Gold | Standard units, labels, status | The only layer analysis reads |

## Key decisions

1. **XBRL is the main source.** It is structured and exact. PDFs + an LLM are an
   optional cross-check, and the pipeline works fully without AI.
2. **Long `metrics` table, not 60 columns.** One row per company + year + metric + period.
   Adding a label means adding a row to `config/metric_catalog.csv`, with no code change.
3. **Every value has a status:** `reported`, `zero`, `not_applicable` or `missing`.
   A 0 and a blank mean very different things.
4. **Units are converted on the way to gold.** Real filings mix TJ and GJ.
5. **SQLite** database: one file, free, built into Python. Can move to PostgreSQL later.
6. **Every stage can re-run safely.** The `filings.status` column records progress,
   and finished work is skipped.

## Traps found in real filings (FY 2025-26)

| Trap | Example | Handled in |
|---|---|---|
| Different energy units | UltraTech TJ, Rajesh Exports GJ | Stage 4 (units) |
| "MtCO2e" means metric tonnes, not megatonnes | UltraTech emissions | Stage 4 (units) |
| Same "INR" label, different scale | UltraTech revenue in rupees, turnover in crores | Stage 5 (validity) |
| XBRL incomplete vs PDF | Rajesh Exports: 940 GJ energy in PDF, "not applicable" in XBRL | Stage 6 (accuracy) |
| Energy used but no emissions reported | Rajesh Exports | Stage 5 (integrity) |
| Two-page spreads in PDFs | UltraTech | Stage 6 (PDF reader) |
| Duplicate water tables (company-wide vs water-stress areas) | UltraTech | Stage 6 (LLM prompt) |

## Tech stack (all free and open source)

Python · SQLite · pandas · requests · pdfplumber · pytest · Streamlit · Ollama (open LLMs) · Git
