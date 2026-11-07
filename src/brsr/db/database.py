"""
Database helpers: open a connection, create the tables, load the metric catalog.
"""

import csv
import sqlite3
from pathlib import Path

from config import settings

SCHEMA_FILE = Path(__file__).with_name("schema.sql")


def connect(db_path=None):
    """Open the SQLite database (the file is created if it doesn't exist)."""
    path = Path(db_path or settings.DB_PATH)
    path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(path)
    conn.row_factory = sqlite3.Row          # rows behave like dictionaries
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def create_tables(conn):
    conn.executescript(SCHEMA_FILE.read_text(encoding="utf-8"))
    conn.commit()


def load_metric_catalog(conn, csv_path=None):
    """Copy config/metric_catalog.csv into the metric_catalog table."""
    path = Path(csv_path or settings.METRIC_CATALOG)
    with open(path, newline="", encoding="utf-8") as f:
        rows = list(csv.DictReader(f))
    conn.executemany(
        """INSERT OR REPLACE INTO metric_catalog
           (metric, xbrl_tag, standard_unit, category, brsr_core, description)
           VALUES (:metric, :xbrl_tag, :standard_unit, :category, :brsr_core, :description)""",
        rows,
    )
    conn.commit()
    return len(rows)


def table_counts(conn):
    """How many rows each table has - handy for checking progress."""
    tables = [r["name"] for r in conn.execute(
        "SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%' ORDER BY name")]
    return {t: conn.execute(f"SELECT COUNT(*) FROM {t}").fetchone()[0] for t in tables}
