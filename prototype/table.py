"""
The master table: one row per report. Columns:
  report_id, company, year,
  ai_<metric>    - what the AI read from the PDF
  xbrl_<metric>  - official value, current year
  prev_<metric>  - official value, previous year
"""

import pandas as pd

import config


def load():
    if config.MASTER_TABLE.exists():
        return pd.read_csv(config.MASTER_TABLE)
    return pd.DataFrame(columns=["report_id", "company", "year"])


def upsert(table, row):
    """Add the row, or replace the old row for the same report."""
    if "report_id" in table.columns:
        table = table[table["report_id"] != row["report_id"]]
    new = pd.DataFrame([row])
    table = new if table.empty else pd.concat([table, new], ignore_index=True)
    return table


def save(table):
    config.DATA_DIR.mkdir(parents=True, exist_ok=True)
    table.to_csv(config.MASTER_TABLE, index=False)


def has_ai_values(table, report_id):
    """True if this report already has at least one AI value (so we can skip the AI)."""
    if table.empty or "report_id" not in table.columns:
        return False
    rows = table[table["report_id"] == report_id]
    ai_cols = [c for c in table.columns if c.startswith("ai_")]
    return not rows.empty and bool(ai_cols) and rows[ai_cols].notna().any(axis=None)
