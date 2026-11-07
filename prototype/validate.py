"""
Step 5 - checks and flags.

Two different kinds of check, kept separate on purpose:

1. ACCURACY  - did the AI read the PDF correctly? (AI value vs official XBRL value)
2. SCREENING - does the company's own data show warning signs?
              (big jump since last year, low renewable share)

Screening flags are prompts for a closer look, not proof that a company is
breaking a rule: they are based on the thresholds you set in config.py.
"""

import pandas as pd

import config


def _num(row, col):
    value = row.get(col)
    return None if value is None or pd.isna(value) else float(value)


def _gap(ai, official):
    """Relative difference; when the official value is 0, any non-zero AI value is a miss."""
    if official == 0:
        return 0.0 if ai == 0 else 1.0
    return abs(ai - official) / abs(official)


def accuracy_flags(row):
    """
    Compares the PDF (read by AI) with the XBRL. Real filings showed that the
    XBRL itself can be incomplete (Rajesh Exports: 940 GJ of energy in the PDF,
    energy marked 'not applicable' in the XBRL), so gaps are flagged as
    'consistency' problems in the filing, separate from AI 'accuracy' errors.
    """
    flags = []
    for field in config.FIELDS:
        ai, official = _num(row, f"ai_{field}"), _num(row, f"xbrl_{field}")
        if official is None and ai is None:
            continue
        if official is None:
            flags.append(("consistency", field, "value in PDF but missing from XBRL", ai, None))
            continue
        if ai is None:
            if official == 0:
                flags.append(("consistency", field, "XBRL says 0 but PDF gives no number", None, 0))
            else:
                flags.append(("accuracy", field, "AI found no value", None, official))
            continue
        gap = _gap(ai, official)
        if gap > config.MATCH_TOLERANCE:
            flags.append(("accuracy", field, f"AI value off by {gap:.0%}", ai, official))
    return flags


def screening_flags(row):
    flags = []
    # The official numbers are preferred; the AI's are used only if there is no XBRL value.
    def best(field):
        return _num(row, f"xbrl_{field}") if _num(row, f"xbrl_{field}") is not None \
            else _num(row, f"ai_{field}")

    for field in config.YOY_FIELDS:
        now, before = best(field), _num(row, f"prev_{field}")
        if now is None or not before:
            continue
        change = (now - before) / abs(before)
        if change > config.MAX_YOY_INCREASE:
            flags.append(("screening", field, f"up {change:.0%} on last year", now, before))

    # Using energy (grid power or fuel) creates Scope 1 or Scope 2 emissions,
    # unless it is all renewable. Zero/missing emissions with real energy use is a red flag.
    energy, renewable_e = best("total_energy_gj"), best("renewable_energy_gj") or 0
    scope1, scope2 = best("scope1_tco2e"), best("scope2_tco2e")
    if energy and energy - renewable_e > 0 and not scope1 and not scope2:
        flags.append(("screening", "emissions",
                      "uses non-renewable energy but reports no emissions", None, energy))

    total, renewable = best("total_energy_gj"), best("renewable_energy_gj")
    if total and renewable is not None:
        share = renewable / total
        if share < config.MIN_RENEWABLE_SHARE:
            flags.append(("screening", "renewable_share",
                          f"only {share:.0%} renewable energy", share, config.MIN_RENEWABLE_SHARE))
    return flags


def build_flags(table):
    rows = []
    for _, row in table.iterrows():
        for kind, metric, message, value, reference in accuracy_flags(row) + screening_flags(row):
            rows.append({
                "report_id": row.get("report_id"), "company": row.get("company"),
                "year": row.get("year"), "check": kind, "metric": metric,
                "message": message, "value": value, "reference": reference,
            })
    return pd.DataFrame(rows, columns=["report_id", "company", "year", "check",
                                       "metric", "message", "value", "reference"])


def accuracy_score(table):
    """Share of metrics where the AI matched the official value (only where both exist)."""
    checked = matched = 0
    for _, row in table.iterrows():
        for field in config.FIELDS:
            ai, official = _num(row, f"ai_{field}"), _num(row, f"xbrl_{field}")
            if official is None or (ai is None and official == 0):
                continue  # nothing to grade the AI against
            checked += 1
            if ai is not None and _gap(ai, official) <= config.MATCH_TOLERANCE:
                matched += 1
    return (matched / checked if checked else None), checked
