"""
Unit conversion, so every company lands in the master table in the same units:
  energy -> GJ, emissions -> tonnes CO2e, water -> kilolitres, waste -> tonnes

Real reports mix units: UltraTech reports energy in TJ, Rajesh Exports in GJ.

TRAP: in the SEBI XBRL files, emissions use the unit label "MtCO2e". Here it
means METRIC tonnes, not megatonnes (UltraTech's PDF says "Metric tonnes of
CO2e" for the same number). So it is treated as tonnes.
"""

import re

ENERGY_TO_GJ = {
    "terajoule": 1000, "tj": 1000,
    "gigajoule": 1, "gj": 1,
    "megajoule": 0.001, "mj": 0.001,
    "kilojoule": 1e-6, "kj": 1e-6,
    "megawatthour": 3.6, "mwh": 3.6,
    "kilowatthour": 0.0036, "kwh": 0.0036,
}
TONNES = {"mtco2e": 1, "tco2e": 1, "tonne": 1, "tonnes": 1, "metrictonnes": 1,
          "metrictonne": 1, "t": 1, "mt": 1}
KILOLITRES = {"kiloliters": 1, "kilolitres": 1, "kl": 1, "kiloliter": 1,
              "kilolitre": 1, "m3": 1, "cubicmetres": 1, "cubicmeters": 1,
              "litres": 0.001, "liters": 0.001, "megalitres": 1000, "megaliters": 1000}

TABLE_FOR_FIELD = {
    "total_energy_gj": ENERGY_TO_GJ,
    "renewable_energy_gj": ENERGY_TO_GJ,
    "scope1_tco2e": TONNES,
    "scope2_tco2e": TONNES,
    "water_withdrawal_kl": KILOLITRES,
    "water_consumption_kl": KILOLITRES,
    "total_waste_t": TONNES,
}


def _clean(unit):
    return re.sub(r"[^a-z0-9]", "", (unit or "").lower())


def _factor(table, key):
    """Exact match first, then common long spellings like 'Metric tonnes of CO2e'."""
    if key in table:
        return table[key]
    scale = 1e6 if "million" in key else 1e5 if "lakh" in key else 1
    if table is TONNES and ("tonne" in key or key.startswith(("tco2", "mtco2"))):
        return scale
    if table is KILOLITRES and "kilolit" in key:
        return scale
    if table is ENERGY_TO_GJ:
        for name, factor in sorted(ENERGY_TO_GJ.items(), key=lambda kv: -len(kv[0])):
            if len(name) > 3 and name in key:
                return factor * scale
    return None


def convert(field, value, unit):
    """
    Returns (converted value, warning or None).
    An empty unit is assumed to already be the standard unit.
    """
    if value is None:
        return None, None
    table = TABLE_FOR_FIELD.get(field)
    key = _clean(unit)
    if table is None or key == "":
        return value, None
    factor = _factor(table, key)
    if factor is not None:
        return value * factor, None
    return value, f"unknown unit '{unit}' for {field} - value kept as is"
