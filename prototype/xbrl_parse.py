"""
Step 4 - read the official XBRL file (the "answer key").

An XBRL file is XML. Each number ("fact") has a tag name (what it is) and a
context (which period it belongs to, e.g. FY 2025-26 or FY 2024-25).
This module turns every fact into a row of a table, then picks out the
metrics listed in config.XBRL_TAGS for the current and previous year.
"""

import xml.etree.ElementTree as ET

import pandas as pd

import config
from llm_extract import to_number
from units import convert


def _local(tag):
    """'{http://...}TotalScope1Emissions' -> 'TotalScope1Emissions'"""
    return tag.split("}", 1)[-1]


def _contexts(root):
    """Map each context id to its period end date and whether it is a sub-breakdown."""
    contexts = {}
    for ctx in root.iter():
        if _local(ctx.tag) != "context":
            continue
        end = None
        has_dims = False
        for child in ctx.iter():
            name = _local(child.tag)
            if name in ("endDate", "instant") and child.text:
                end = child.text.strip()
            if name in ("segment", "scenario") and len(child):
                has_dims = True
        contexts[ctx.get("id")] = {"end_date": end, "has_dims": has_dims}
    return contexts


def read_facts(xml_path):
    """Every fact in the file as a table: tag, value, end_date, has_dims, unit."""
    root = ET.parse(xml_path).getroot()
    contexts = _contexts(root)
    rows = []
    for el in root.iter():
        ctx_id = el.get("contextRef")
        if not ctx_id:
            continue
        ctx = contexts.get(ctx_id, {})
        rows.append({
            "tag": _local(el.tag),
            "value": (el.text or "").strip(),
            "context": ctx_id,
            "end_date": ctx.get("end_date"),
            "has_dims": ctx.get("has_dims", False),
            "unit": el.get("unitRef", ""),
        })
    return pd.DataFrame(rows, columns=["tag", "value", "context", "end_date", "has_dims", "unit"])


def save_facts(xml_path):
    """Save all facts to data/xbrl_facts/<name>.csv so you can browse them in Excel."""
    config.XBRL_FACTS_DIR.mkdir(parents=True, exist_ok=True)
    out = config.XBRL_FACTS_DIR / f"{xml_path.stem}.csv"
    read_facts(xml_path).to_csv(out, index=False)
    return out


def find_tags(xml_path, keyword):
    """List tag names containing a keyword, e.g. 'energy' or 'scope'."""
    facts = read_facts(xml_path)
    hits = facts[facts["tag"].str.contains(keyword, case=False, na=False)]
    return (hits.groupby("tag")
                .agg(example_value=("value", "first"), times_used=("value", "size"))
                .reset_index())


def metric_values(xml_path):
    """
    Returns two dicts: current-year values and previous-year values,
    for every metric that has a tag filled in config.XBRL_TAGS.
    Only company-wide totals are used (facts without sub-breakdowns).
    """
    facts = read_facts(xml_path)
    totals = facts[~facts["has_dims"]].copy()
    totals["number"] = totals["value"].map(to_number)
    totals = totals.dropna(subset=["number", "end_date"])

    current, previous = {}, {}
    for field, tag in config.XBRL_TAGS.items():
        if not tag:
            continue
        tag = tag.split(":")[-1]
        matches = totals[totals["tag"] == tag]
        by_year = (matches.sort_values("end_date")
                          .drop_duplicates("end_date", keep="last")
                          .sort_values("end_date", ascending=False))
        for position, target in [(0, current), (1, previous)]:
            if len(by_year) > position:
                fact = by_year.iloc[position]
                value, warning = convert(field, float(fact["number"]), fact["unit"])
                if warning:
                    print(f"  XBRL {warning}")
                target[field] = value
    return current, previous
