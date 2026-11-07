"""
The one file you run. Each step can be run alone or all together.

  python run.py collect              get report links from NSE -> data/links.csv
  python run.py download             download PDFs + XBRL files -> data/raw/
  python run.py extract              AI reads each PDF, official XBRL values added
  python run.py check                compare + flag -> data/flags.csv
  python run.py all                  download, extract and check in one go
  python run.py find-tags FILE WORD  search an XBRL file for tag names, e.g. 'energy'

Use  --limit 3  with extract or all to try only the first 3 reports.
Use  --redo     with extract to re-run the AI even for reports already done.
"""

import argparse
from pathlib import Path

import config
import table as master
from collect import collect_from_nse, load_links
from download import download_all, report_id
from validate import accuracy_score, build_flags


def step_extract(limit=None, redo=False):
    # imported here so 'collect' and 'download' work even without pdfplumber
    from llm_extract import extract_metrics
    from pdf_extract import principle6_text
    from xbrl_parse import metric_values, save_facts

    links = load_links()
    if limit:
        links = links.head(limit)
    table = master.load()

    for _, link in links.iterrows():
        rid = report_id(link["company"], link["year"])
        pdf_path = config.RAW_DIR / f"{rid}.pdf"
        xml_path = config.RAW_DIR / f"{rid}.xml"
        print(f"\n{rid}")

        old = table[table["report_id"] == rid] if "report_id" in table.columns else table.iloc[0:0]
        row = old.iloc[0].to_dict() if not old.empty else {}
        row.update({"report_id": rid, "company": link["company"], "year": link["year"]})

        # 1) AI reads the PDF (skipped if already done, unless --redo)
        if pdf_path.exists() and (redo or not master.has_ai_values(table, rid)):
            try:
                text = principle6_text(pdf_path)
                if text.strip():
                    for field, value in extract_metrics(text).items():
                        row[f"ai_{field}"] = value
                    print("  AI extraction: done")
                else:
                    print("  AI extraction: no Principle 6 text (scanned PDF?) - skipped")
            except Exception as err:
                print(f"  AI extraction FAILED: {err}")
        elif not pdf_path.exists():
            print("  no PDF downloaded")
        else:
            print("  AI extraction: already done")

        # 2) official numbers from the XBRL file
        if xml_path.exists():
            try:
                save_facts(xml_path)
                current, previous = metric_values(xml_path)
                for field, value in current.items():
                    row[f"xbrl_{field}"] = value
                for field, value in previous.items():
                    row[f"prev_{field}"] = value
                if not current:
                    print("  XBRL: fill XBRL_TAGS in config.py to read official values")
                else:
                    print(f"  XBRL: {len(current)} official values read")
            except Exception as err:
                print(f"  XBRL FAILED: {err}")

        table = master.upsert(table, row)
        master.save(table)  # saved after every report

    print(f"\nMaster table: {config.MASTER_TABLE} ({len(table)} reports)")


def step_check():
    table = master.load()
    if table.empty:
        raise SystemExit("Master table is empty - run 'extract' first.")
    flags = build_flags(table)
    flags.to_csv(config.FLAGS_FILE, index=False)

    score, checked = accuracy_score(table)
    if score is not None:
        print(f"AI accuracy: {score:.0%} of {checked} values matched the official XBRL")
    else:
        print("AI accuracy: no official values yet (fill XBRL_TAGS in config.py)")

    print(f"{len(flags)} flags saved to {config.FLAGS_FILE}")
    if not flags.empty:
        print(flags[["company", "check", "metric", "message"]].to_string(index=False))


def main():
    parser = argparse.ArgumentParser(description="BRSR ESG pipeline")
    parser.add_argument("step", choices=["collect", "download", "extract", "check", "all", "find-tags"])
    parser.add_argument("args", nargs="*")
    parser.add_argument("--limit", type=int)
    parser.add_argument("--redo", action="store_true")
    opts = parser.parse_args()

    if opts.step == "collect":
        collect_from_nse()
    elif opts.step == "download":
        download_all(load_links().head(opts.limit) if opts.limit else load_links())
    elif opts.step == "extract":
        step_extract(opts.limit, opts.redo)
    elif opts.step == "check":
        step_check()
    elif opts.step == "all":
        links = load_links()
        download_all(links.head(opts.limit) if opts.limit else links)
        step_extract(opts.limit, opts.redo)
        step_check()
    elif opts.step == "find-tags":
        if len(opts.args) != 2:
            raise SystemExit("Usage: python run.py find-tags data/raw/FILE.xml energy")
        from xbrl_parse import find_tags
        hits = find_tags(Path(opts.args[0]), opts.args[1])
        print(hits.to_string(index=False) if not hits.empty else "No tags found.")


if __name__ == "__main__":
    main()
