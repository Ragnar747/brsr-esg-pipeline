"""
Step 2 - download each report's PDF and XBRL file into data/raw/.

Files are saved (not just read in memory) so you never download the same
report twice, and you can always open the PDF to check a number by hand.
"""

import re
import time

import requests

import config
from collect import BROWSER_HEADERS


def report_id(company, year):
    """A safe file name like CYIENT_LIMITED_2026."""
    name = re.sub(r"[^A-Za-z0-9]+", "_", f"{company}_{year}").strip("_")
    return name or "unknown_report"


def _download(session, url, path):
    if path.exists() and path.stat().st_size > 0:
        return "already there"
    response = session.get(url, timeout=120)
    response.raise_for_status()
    path.write_bytes(response.content)
    time.sleep(config.REQUEST_DELAY_SECONDS)
    return "downloaded"


def download_all(links):
    config.RAW_DIR.mkdir(parents=True, exist_ok=True)
    session = requests.Session()
    session.headers.update(BROWSER_HEADERS)

    for _, row in links.iterrows():
        rid = report_id(row["company"], row["year"])
        for url, ending in [(row["pdf_url"], ".pdf"), (row["xbrl_url"], ".xml")]:
            if not url:
                continue
            path = config.RAW_DIR / f"{rid}{ending}"
            try:
                status = _download(session, url, path)
                print(f"{path.name}: {status}")
            except Exception as err:
                print(f"{path.name}: FAILED ({err})")
