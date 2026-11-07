"""
Step 3b - ask the AI model to pull the metrics out of the Principle 6 text.
"""

import json
import re

import requests

import config
from units import convert


def to_number(value):
    """Turn '1,23,456.7 GJ' or 1234 into a float; anything else into None."""
    if value is None or isinstance(value, bool):
        return None
    if isinstance(value, (int, float)):
        return float(value)
    cleaned = re.sub(r"[^0-9.\-]", "", str(value))
    try:
        return float(cleaned) if cleaned not in ("", ".", "-") else None
    except ValueError:
        return None


def build_prompt(text):
    field_list = "\n".join(f'- "{key}": {meaning}' for key, meaning in config.FIELDS.items())
    return f"""You are extracting data from an Indian BRSR (Business Responsibility
and Sustainability) report. From the text below, return ONLY a JSON object
with exactly these keys:
{field_list}

Each key's value must be an object: {{"value": <number>, "unit": "<unit exactly as written in the report>"}}
Example: {{"total_energy_gj": {{"value": 388359.58, "unit": "TJ"}}}}

Rules:
- Use the CURRENT financial year column (the first number column), not the previous year.
- Numbers may use Indian commas like 3,15,29,832 - write them without commas.
- Do NOT convert units yourself; copy the unit the report uses (TJ, GJ, kilolitres, ...).
- Use company-wide totals. Ignore "areas of water stress" tables and
  "Total Scope 1 and Scope 2" combined lines.
- If a value is not in the text, use null. Never guess.

REPORT TEXT:
{text[:config.MAX_CHARS]}"""


def parse_reply(data):
    """Turn the model's JSON into {field: value in standard units}."""
    results = {}
    for key in config.FIELDS:
        item = data.get(key)
        if isinstance(item, dict):
            value, unit = to_number(item.get("value")), item.get("unit", "")
        else:  # model ignored the format and gave a bare number
            value, unit = to_number(item), ""
        converted, warning = convert(key, value, unit)
        if warning:
            print(f"  AI {warning}")
        results[key] = converted
    return results


def extract_metrics(text):
    headers = {"Content-Type": "application/json"}
    if config.LLM_API_KEY:
        headers["Authorization"] = f"Bearer {config.LLM_API_KEY}"
    body = {
        "model": config.LLM_MODEL,
        "messages": [{"role": "user", "content": build_prompt(text)}],
        "temperature": 0,
    }
    response = requests.post(config.LLM_URL, headers=headers, json=body, timeout=300)
    response.raise_for_status()
    reply = response.json()["choices"][0]["message"]["content"]

    match = re.search(r"\{.*\}", reply, re.DOTALL)
    if not match:
        raise ValueError("the model did not return JSON")
    return parse_reply(json.loads(match.group(0)))
