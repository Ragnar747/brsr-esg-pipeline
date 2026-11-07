# BRSR ESG pipeline

Reads Indian companies' BRSR sustainability reports, extracts environmental
metrics with an AI model, checks the AI against the official XBRL data, and
flags warning signs.

## Files (one job each)

| File | Job |
|---|---|
| `config.py` | All settings: folders, AI model, metrics, XBRL tags, flag thresholds |
| `collect.py` | Gets the list of reports (from NSE, or your own `links.csv`) |
| `download.py` | Downloads each PDF + XBRL file once into `data/raw/` |
| `pdf_extract.py` | Pulls the Principle 6 (environment) pages out of a PDF |
| `llm_extract.py` | Asks the AI for the metrics and cleans the numbers |
| `units.py` | Converts TJ/GJ/MWh, tonnes, kilolitres to one standard unit |
| `xbrl_parse.py` | Reads official values (current + previous year) from XBRL |
| `table.py` | Loads, updates and saves the master table |
| `validate.py` | Accuracy check (AI vs XBRL) and screening flags |
| `run.py` | The only file you run |

## Setup

```
pip install -r requirements.txt
ollama pull llama3.1:8b
```

## Run

```
python run.py collect                 # needs NSE_API_URL in config.py (see note there)
python run.py all --limit 3           # test on 3 reports first
python run.py all                     # everything
```

Or run steps one at a time: `download`, `extract`, `check`.

## XBRL tags

The tag names in `config.py` are confirmed from real FY 2025-26 SEBI filings
(UltraTech Cement, Rajesh Exports). To look for other metrics:

```
python run.py find-tags data/raw/CYIENT_LIMITED_2026.xml energy
python run.py find-tags data/raw/CYIENT_LIMITED_2026.xml scope
```

Every fact from each
XBRL file is also saved to `data/xbrl_facts/` so you can browse it in Excel.

## Outputs

- `data/master_table.csv`: one row per report (`ai_`, `xbrl_` and `prev_` columns)
- `data/flags.csv`: three kinds of flag: `accuracy` (AI misread the PDF),
  `consistency` (PDF and XBRL disagree), `screening` (warning signs in the data)

Screening flags use thresholds you choose in `config.py`. They point to
companies worth a closer look; they are not proof of a rule being broken.
