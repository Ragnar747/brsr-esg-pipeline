"""
The one command you run. Each stage adds a new command here.

  python pipelines/run.py init-db      stage 1: create the database and tables
  python pipelines/run.py status       show how many rows each table has

Coming later (see docs/ROADMAP.md):
  ingest       stage 2: download PDF + XBRL files
  extract      stage 3: XBRL facts -> silver
  standardise  stage 4: silver -> gold metrics
  check        stage 5: data-quality checks + scorecard
  llm          stage 6: PDF cross-check with a local LLM (optional)
"""

import argparse
import sys
from pathlib import Path

# Let Python find our code: the project root (for config/) and src/ (for brsr/)
ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "src"))

from config import settings  # noqa: E402
from brsr.db import database  # noqa: E402


def init_db():
    conn = database.connect()
    database.create_tables(conn)
    n = database.load_metric_catalog(conn)
    print(f"Database ready: {settings.DB_PATH}")
    print(f"Metric catalog loaded: {n} metrics")
    conn.close()


def status():
    if not settings.DB_PATH.exists():
        print("No database yet. Run:  python pipelines/run.py init-db")
        return
    conn = database.connect()
    for table, count in database.table_counts(conn).items():
        print(f"  {table:<16} {count:>8} rows")
    conn.close()


COMMANDS = {"init-db": init_db, "status": status}


def main():
    parser = argparse.ArgumentParser(description="BRSR ESG pipeline")
    parser.add_argument("command", choices=sorted(COMMANDS))
    args = parser.parse_args()
    COMMANDS[args.command]()


if __name__ == "__main__":
    main()
