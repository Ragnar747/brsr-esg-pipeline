# Roadmap

Seven stages, about 2–3 hours a day, finishing around **22 November 2026**.
Each stage ends with working code, a passing test and one Git commit.
If a day slips, just move the dates. The order matters more than the dates.

| Day | Date | Stage | You'll have at the end |
|---|---|---|---|
| 1 | Sun 8 Nov | 0. Setup | Tools installed, first push to GitHub |
| 2 | Mon 9 Nov | 1. Skeleton + database | Understand every table; database created |
| 3–4 | 10–11 Nov | 2. Ingest → bronze | PDF + XBRL for 5 cement companies downloaded and logged |
| 5–6 | 12–13 Nov | 3. XBRL → silver | ~2,000 facts per company in `xbrl_facts` |
| 7–8 | 14–15 Nov | 4. Standardise → gold | Clean `metrics` table, all units converted |
| 9–10 | 16–17 Nov | 5. Quality checks | Six-dimension scorecard for every company |
| 11–12 | 18–19 Nov | 6. PDF + LLM (optional) | AI reads PDFs; accuracy score vs XBRL |
| 13–14 | 20–21 Nov | 7. Dashboard | Streamlit dashboard comparing companies |
| 15 | Sun 22 Nov | Finish | Polished README, findings write-up, LinkedIn post |

---

## Stage 0: Setup (Day 1)
Follow `docs/SETUP_GUIDE.md` from start to finish.
**Done when:** `pytest` shows `4 passed` and your code is on GitHub.

## Stage 1: Skeleton + database (Day 2) ✅ code already written
- Read `ARCHITECTURE.md`.
- Open `src/brsr/db/schema.sql` and read the comment above each table.
- Open `data/brsr.db` with SQLite Viewer and look at `metric_catalog`.
- Try one SQL query in the viewer: `SELECT metric, standard_unit FROM metric_catalog WHERE category = 'water';`

**Done when:** you can explain bronze, silver and gold in your own words.
**Commit:** already done in stage 0.

## Stage 2: Ingest → bronze (Days 3–4)
- Fill `config/links.csv` with 5 cement companies (UltraTech, Ambuja, ACC, Shree Cement, Dalmia Bharat): company, year, PDF link, XBRL link.
- Build `src/brsr/ingest/downloader.py`: download each file once, add a row to `filings`.
- Optional: find the NSE data address with Chrome's Network tab, to collect links automatically.

**Done when:** `filings` has 5 rows with status `downloaded`.
**Commit:** `Stage 2: download filings into bronze layer`

## Stage 3: XBRL → silver (Days 5–6)
- Build `src/brsr/extract/xbrl_parser.py` (the parser already works in the prototype; we move it here).
- Save every fact into `xbrl_facts`; fill `companies` with ISIN and name.

**Done when:** each filing has ~1,500–2,000 facts; status `extracted`.
**Commit:** `Stage 3: parse XBRL facts into silver layer`

## Stage 4: Standardise → gold (Days 7–8)
- Build `src/brsr/transform/units.py` (TJ→GJ etc.) and `standardise.py`.
- For each metric in the catalog: current + previous year, standard unit, status
  (`reported` / `zero` / `not_applicable` / `missing`).

**Done when:** UltraTech's total energy shows 388,359,580 GJ in `metrics`.
**Commit:** `Stage 4: standardised gold metrics table`

## Stage 5: Quality checks (Days 9–10)
One rule set per dimension, in `src/brsr/quality/`:
- **Completeness:** share of catalog metrics reported
- **Validity:** no negatives, known units, sensible ranges
- **Uniqueness:** one filing per company per year (by ISIN)
- **Integrity:** parts add up to totals; renewable ≤ total; consumption ≤ withdrawal
- **Consistency:** this year's "previous year" matches last year's report
- **Accuracy:** PDF vs XBRL (needs stage 6; scored as "not checked" until then)

**Done when:** `quality_scores` has a score per company per dimension.
**Commit:** `Stage 5: six-dimension data quality checks`

## Stage 6: PDF + LLM cross-check (Days 11–12, optional)
- Install Ollama (setup guide, part 8).
- Move the prototype's PDF reader and LLM extractor into `src/brsr/extract/`.
- Store readings in `pdf_extractions`; compare with XBRL.

**Done when:** you have an accuracy score, e.g. "AI matched 90% of XBRL values".
**Commit:** `Stage 6: LLM extraction from PDFs with accuracy scoring`

## Stage 7: Dashboard (Days 13–14)
- Streamlit app: pick a company, see its metrics, trends and quality scorecard;
  compare cement companies side by side.

**Done when:** `streamlit run` opens the dashboard in your browser.
**Commit:** `Stage 7: Streamlit dashboard`

## Finish (Day 15)
- README: screenshots, what you found, how to run it.
- Write-up: *"What 5 cement companies' BRSR filings reveal about data quality."*
- LinkedIn post with the GitHub link.

---

## After this: ideas for ML / AI (later)
All open source (scikit-learn, statsmodels):
- **Anomaly detection:** find unusual filings automatically (e.g. Isolation Forest)
- **Forecasting:** predict next year's emissions or water use from past filings
- **Peer clustering:** group companies by environmental profile
These need several years and many companies of data, which the pipeline will collect.
