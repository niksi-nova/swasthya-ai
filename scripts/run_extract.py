# scripts/run_extract.py
import sys
from app.extractor import extract_tables_from_pdf, parse_simple_lab_table
import json

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python run_extract.py path/to/report.pdf")
        sys.exit(1)
    pdf_path = sys.argv[1]
    out = extract_tables_from_pdf(pdf_path)
    # try parsing any found tables
    parsed = []
    for item in out:
        if "table" in item:
            for t in item["table"]:
                parsed.extend(parse_simple_lab_table(item["table"]))
    print(json.dumps({"raw": out, "parsed_samples": parsed}, indent=2))
