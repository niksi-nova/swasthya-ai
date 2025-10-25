# app/extractor.py
import pdfplumber
import pytesseract
from PIL import Image
import io
import re

def extract_tables_from_pdf(pdf_path):
    results = []
    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            # try table extraction
            tables = page.extract_tables()
            if tables:
                for table in tables:
                    results.append({"page": page.page_number, "table": table})
            else:
                # fallback: OCR whole page as text
                pil_img = page.to_image(resolution=300).original
                txt = pytesseract.image_to_string(pil_img)
                results.append({"page": page.page_number, "ocr_text": txt})
    return results

def parse_simple_lab_table(table):
    """
    table: list of rows (list of cells) from pdfplumber
    This is a simple heuristic parser for the CBC-like table.
    """
    parsed = []
    for row in table:
        # join cells, then use simple regex to find numeric result + reference range
        line = " | ".join([c if c else "" for c in row])
        # try to capture: TestName  Result  Unit  Range
        m = re.search(r'([A-Za-z\.\s/:-]+)\s+([\d\.]+)\s*([a-zA-Z%\/]+)?\s+([\d\.]+)\s*-\s*([\d\.]+)', line)
        if m:
            parsed.append({
                "test_name": m.group(1).strip(),
                "result": float(m.group(2)),
                "unit": m.group(3) or "",
                "ref_low": float(m.group(4)),
                "ref_high": float(m.group(5)),
            })
    return parsed
