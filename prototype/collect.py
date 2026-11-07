"""
Step 1 - collect the list of reports (company + PDF link + XBRL link).

Two ways:
  a) fetch it from NSE automatically (needs NSE_API_URL in config.py), or
  b) fill data/links.csv yourself with the columns:
         company, year, pdf_url, xbrl_url
Either way the result is data/links.csv, which every later step reads.
"""

import time

import pandas as pd
import requests

import config

LINK_COLUMNS = ["company", "year", "pdf_url", "xbrl_url"]
NAME_KEYS = ["companyName", "company", "companyname", "comName", "symbol"]
YEAR_KEYS = ["toYear", "toyr", "to_year", "fyTo", "year"]

BROWSER_HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                  "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Safari/537.36",
    "Accept": "application/json, text/plain, */*",
    "Accept-Language": "en-US,en;q=0.9",
    "Referer": config.NSE_BRSR_PAGE,
}


def nse_session():
    """NSE only answers data requests from a session that visited the site first."""
    session = requests.Session()
    session.headers.update(BROWSER_HEADERS)
    session.get(config.NSE_HOME_URL, timeout=30)
    time.sleep(config.REQUEST_DELAY_SECONDS)
    session.get(config.NSE_BRSR_PAGE, timeout=30)
    time.sleep(config.REQUEST_DELAY_SECONDS)
    return session


def _records(payload):
    """The API may return a list, or a dict holding the list. Find the list."""
    if isinstance(payload, list):
        return payload
    if isinstance(payload, dict):
        for value in payload.values():
            if isinstance(value, list) and value and isinstance(value[0], dict):
                return value
    return []


def _first(record, keys):
    for key in keys:
        if record.get(key):
            return str(record[key]).strip()
    return ""


def _find_url(record, ending):
    """Find any text in the record that looks like a link ending in .pdf / .xml."""
    for value in record.values():
        if isinstance(value, str) and value.lower().split("?")[0].endswith(ending):
            return value.strip()
    return ""


def records_to_links(records):
    rows = []
    for record in records:
        rows.append({
            "company": _first(record, NAME_KEYS),
            "year": _first(record, YEAR_KEYS),
            "pdf_url": _find_url(record, ".pdf"),
            "xbrl_url": _find_url(record, ".xml"),
        })
    links = pd.DataFrame(rows, columns=LINK_COLUMNS)
    return links[(links["pdf_url"] != "") | (links["xbrl_url"] != "")]


def collect_from_nse():
    if not config.NSE_API_URL:
        raise SystemExit(
            "NSE_API_URL is empty in config.py. Find it in Chrome's Network tab "
            "(see the note in config.py), or fill data/links.csv by hand."
        )
    session = nse_session()
    response = session.get(config.NSE_API_URL, timeout=60)
    response.raise_for_status()
    links = records_to_links(_records(response.json()))
    if links.empty:
        raise SystemExit(
            "Got a reply from NSE but found no PDF/XML links in it. "
            "Open the reply in the Network tab and check the field names."
        )
    config.DATA_DIR.mkdir(parents=True, exist_ok=True)
    links.to_csv(config.LINKS_FILE, index=False)
    print(f"Saved {len(links)} reports to {config.LINKS_FILE}")
    return links


def load_links():
    if not config.LINKS_FILE.exists():
        raise SystemExit(f"{config.LINKS_FILE} not found. Run 'collect' first or create it.")
    links = pd.read_csv(config.LINKS_FILE, dtype=str).fillna("")
    missing = set(LINK_COLUMNS) - set(links.columns)
    if missing:
        raise SystemExit(f"links.csv is missing columns: {', '.join(sorted(missing))}")
    return links
