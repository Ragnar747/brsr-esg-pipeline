"""
All settings in one place. Change things here, not inside the other files.
"""

from pathlib import Path

# ---------------- folders and files ----------------
BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"
RAW_DIR = DATA_DIR / "raw"                # downloaded PDFs and XBRL files
LINKS_FILE = DATA_DIR / "links.csv"       # list of reports to process
MASTER_TABLE = DATA_DIR / "master_table.csv"
FLAGS_FILE = DATA_DIR / "flags.csv"
XBRL_FACTS_DIR = DATA_DIR / "xbrl_facts"  # every fact from each XBRL, for inspection

# ---------------- collecting links from NSE ----------------
# The BRSR page on NSE loads its table from a hidden data (API) address.
# To find it: open the BRSR page in Chrome -> right-click -> Inspect ->
# Network tab -> "Fetch/XHR" -> reload the page -> click the request that
# returns the table -> copy its "Request URL" and paste it below.
NSE_HOME_URL = "https://www.nseindia.com"
NSE_BRSR_PAGE = "https://www.nseindia.com/companies-listing/corporate-filings-bussiness-sustainabilitiy-reports"
NSE_API_URL = ""            # paste the Request URL here
REQUEST_DELAY_SECONDS = 2   # pause between requests, to be polite to the site

# ---------------- the AI model ----------------
# Default: Ollama on your own laptop (free). Any OpenAI-compatible endpoint works.
LLM_URL = "http://localhost:11434/v1/chat/completions"
LLM_MODEL = "llama3.1:8b"
LLM_API_KEY = ""
MAX_PAGES = 15
MAX_CHARS = 30000

# ---------------- the metrics we track ----------------
# name -> description given to the AI
FIELDS = {
    "total_energy_gj": "total energy consumption, in gigajoules",
    "renewable_energy_gj": "total energy consumed from renewable sources, in gigajoules",
    "water_withdrawal_kl": "total volume of water withdrawal, in kilolitres",
    "water_consumption_kl": "total volume of water consumption, in kilolitres",
    "scope1_tco2e": "total Scope 1 emissions, in tonnes of CO2 equivalent",
    "scope2_tco2e": "total Scope 2 emissions, in tonnes of CO2 equivalent",
    "total_waste_t": "total waste generated, in metric tonnes",
}

# Which XBRL tag holds each metric. All confirmed from real SEBI BRSR files
# (Rajesh Exports and UltraTech Cement, FY 2025-26). Units are converted
# automatically (see units.py). To look for other tags:
#   python run.py find-tags data/raw/<company>.xml <word>
XBRL_TAGS = {
    "total_energy_gj": "TotalEnergyConsumedFromRenewableAndNonRenewableSources",
    "renewable_energy_gj": "TotalEnergyConsumedFromRenewableSources",
    "water_withdrawal_kl": "TotalVolumeOfWaterWithdrawal",
    "water_consumption_kl": "TotalVolumeOfWaterConsumption",
    "scope1_tco2e": "TotalScope1Emissions",
    "scope2_tco2e": "TotalScope2Emissions",
    "total_waste_t": "TotalWasteGenerated",
}

# ---------------- checks and flags ----------------
# These are screening rules YOU choose, not legal limits. Adjust them freely.
MATCH_TOLERANCE = 0.02           # AI value within 2% of XBRL value = match
MAX_YOY_INCREASE = 0.20          # flag if a metric rose more than 20% in a year
YOY_FIELDS = ["total_energy_gj", "water_withdrawal_kl",
              "scope1_tco2e", "scope2_tco2e", "total_waste_t"]
MIN_RENEWABLE_SHARE = 0.10       # flag if under 10% of energy is renewable
