# BRSR ESG Pipeline

An open-source data pipeline that collects Indian listed companies' **BRSR**
(Business Responsibility and Sustainability Reporting) filings from NSE, extracts their
environmental data (energy, emissions, water, waste), and scores the **quality** of
each company's disclosures across six dimensions: accuracy, completeness, consistency,
validity, uniqueness and integrity.

> Status: **Stage 1 of 7**: project skeleton and database. See [docs/ROADMAP.md](docs/ROADMAP.md).

## Why
Since FY 2022-23, India's top 1,000 listed companies must file BRSR reports. The data
is public but scattered across PDFs and XBRL files, uses mixed units, and is sometimes
incomplete or inconsistent. This project turns it into one clean, comparable dataset.

## How it works
Bronze (raw files) → Silver (extracted facts) → Gold (clean metrics) → Quality scorecard → Dashboard.
Details in [ARCHITECTURE.md](ARCHITECTURE.md).

## Quick start
```
python -m venv .venv
.venv\Scripts\activate            # Mac: source .venv/bin/activate
pip install -r requirements.txt
python pipelines/run.py init-db
python pipelines/run.py status
pytest
```
New to Git or Python environments? Start with [docs/SETUP_GUIDE.md](docs/SETUP_GUIDE.md).

## Project structure
```
config/          settings and the metric catalog (the data labels)
src/brsr/        the pipeline code, one folder per stage
pipelines/       run.py, the one command you run
tests/           automated tests + sample XBRL files
docs/            setup guide and roadmap
data/            downloaded files and the database (not in Git)
```

## Tech stack
All free and open source: Python, SQLite, pandas, pdfplumber, pytest, Streamlit, Ollama.
