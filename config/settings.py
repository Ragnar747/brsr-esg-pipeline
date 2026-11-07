"""
All settings in one place. Change things here, not inside the other files.
"""

from pathlib import Path

# ---------------- folders and files ----------------
PROJECT_ROOT = Path(__file__).resolve().parent.parent
CONFIG_DIR = PROJECT_ROOT / "config"
DATA_DIR = PROJECT_ROOT / "data"
RAW_DIR = DATA_DIR / "raw"                     # bronze: downloaded files
DB_PATH = DATA_DIR / "brsr.db"                 # the SQLite database
METRIC_CATALOG = CONFIG_DIR / "metric_catalog.csv"
LINKS_FILE = CONFIG_DIR / "links.csv"          # list of filings to download

# ---------------- NSE (stage 2) ----------------
NSE_HOME_URL = "https://www.nseindia.com"
NSE_BRSR_PAGE = "https://www.nseindia.com/companies-listing/corporate-filings-bussiness-sustainabilitiy-reports"
NSE_API_URL = ""                 # found later with Chrome's Network tab
REQUEST_DELAY_SECONDS = 2        # be polite: pause between downloads

# ---------------- LLM (stage 6, optional) ----------------
# Ollama runs open models on your own laptop for free.
LLM_URL = "http://localhost:11434/v1/chat/completions"
LLM_MODEL = "llama3.1:8b"

# ---------------- quality thresholds (stage 5) ----------------
MATCH_TOLERANCE = 0.02           # PDF vs XBRL within 2% = match
MAX_YOY_INCREASE = 0.20          # flag a rise of more than 20% in a year
