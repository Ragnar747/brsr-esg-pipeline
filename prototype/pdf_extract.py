"""
Step 3a - read a BRSR PDF and return only the Principle 6 (environment) section.

Handles two layouts seen in real reports:
  - normal one-column pages (e.g. Rajesh Exports)
  - two-page spreads / two-column pages (e.g. UltraTech), where reading
    straight across mixes the left and right columns together.
"""

import re

import pdfplumber

import config

P6_START = re.compile(r"PRINCIPLE\s*6\s*[:\-–]?\s*BUSINESSES\s+SHOULD\s+RESPECT", re.I)
P6_START_LOOSE = re.compile(r"PRINCIPLE\s*6\b", re.I)
P7_START = re.compile(r"PRINCIPLE\s*7\b", re.I)


def is_two_column(page):
    """Two columns if almost no words cross the middle of the page."""
    words = page.extract_words()
    if len(words) < 50:
        return False
    mid = page.width / 2
    crossing = sum(1 for w in words if w["x0"] < mid - 5 and w["x1"] > mid + 5)
    lines = len({round(w["top"]) for w in words}) or 1
    return crossing / lines < 0.05


def page_text(page):
    if is_two_column(page):
        mid = page.width / 2
        left = page.crop((0, 0, mid, page.height)).extract_text() or ""
        right = page.crop((mid, 0, page.width, page.height)).extract_text() or ""
        return left + "\n" + right
    return page.extract_text() or ""


def full_text(pdf_path):
    with pdfplumber.open(pdf_path) as pdf:
        return "\n".join(page_text(page) for page in pdf.pages)


def principle6_text(pdf_path):
    text = full_text(pdf_path)
    start = P6_START.search(text) or P6_START_LOOSE.search(text)
    if not start:
        return ""
    end = P7_START.search(text, start.end())
    section = text[start.start(): end.start() if end else None]
    if len(section) > config.MAX_CHARS:
        print(f"  note: Principle 6 is {len(section)} characters; only the first "
              f"{config.MAX_CHARS} go to the AI (raise MAX_CHARS in config.py)")
    return section
