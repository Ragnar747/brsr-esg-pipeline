"""
Stage 1 tests: the database can be created and the metric catalog loads.
Run with:  pytest
Each test uses a temporary database, so your real data is never touched.
"""

from brsr.db import database

EXPECTED_TABLES = {
    "companies", "metric_catalog", "filings", "xbrl_facts",
    "pdf_extractions", "metrics", "quality_checks", "quality_scores",
}


def make_db(tmp_path):
    conn = database.connect(tmp_path / "test.db")
    database.create_tables(conn)
    return conn


def test_all_tables_created(tmp_path):
    conn = make_db(tmp_path)
    assert set(database.table_counts(conn)) == EXPECTED_TABLES


def test_creating_tables_twice_is_safe(tmp_path):
    conn = make_db(tmp_path)
    database.create_tables(conn)          # must not crash or duplicate anything
    assert set(database.table_counts(conn)) == EXPECTED_TABLES


def test_metric_catalog_loads(tmp_path):
    conn = make_db(tmp_path)
    n = database.load_metric_catalog(conn)
    assert n >= 7
    row = conn.execute(
        "SELECT xbrl_tag, standard_unit FROM metric_catalog WHERE metric = 'scope1_emissions'"
    ).fetchone()
    assert row["xbrl_tag"] == "TotalScope1Emissions"
    assert row["standard_unit"] == "tCO2e"


def test_same_filing_cannot_be_added_twice(tmp_path):
    conn = make_db(tmp_path)
    sql = "INSERT INTO filings (company_name, fy_end) VALUES ('UltraTech Cement Limited', '2026-03-31')"
    conn.execute(sql)
    try:
        conn.execute(sql)
        duplicated = True
    except Exception:
        duplicated = False
    assert not duplicated, "uniqueness rule should block a second identical filing"
