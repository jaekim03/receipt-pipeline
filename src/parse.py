from __future__ import annotations
import re
import sys
import os
from datetime import date

sys.path.insert(0, os.path.dirname(__file__))
from db import get_connection

MONTH_NAMES = {
    "january": 1, "february": 2, "march": 3, "april": 4,
    "may": 5, "june": 6, "july": 7, "august": 8,
    "september": 9, "october": 10, "november": 11, "december": 12,
    "jan": 1, "feb": 2, "mar": 3, "apr": 4, "jun": 6,
    "jul": 7, "aug": 8, "sep": 9, "oct": 10, "nov": 11, "dec": 12,
}


def extract_amount(text: str) -> float | None:
    patterns = [
        r'(?:total|amount due|subtotal)[^\d]*(\d+\.\d{2})',
        r'\$\s*(\d+\.\d{2})',
    ]
    for p in patterns:
        m = re.search(p, text, re.IGNORECASE)
        if m:
            return float(m.group(1))
    return None


def extract_date(text: str) -> date | None:
    # ISO: 2026-04-22
    m = re.search(r'(\d{4})-(\d{2})-(\d{2})', text)
    if m:
        try:
            return date(int(m.group(1)), int(m.group(2)), int(m.group(3)))
        except ValueError:
            pass

    # Slash: 04/22/2026
    m = re.search(r'(\d{1,2})/(\d{1,2})/(\d{4})', text)
    if m:
        try:
            return date(int(m.group(3)), int(m.group(1)), int(m.group(2)))
        except ValueError:
            pass

    # Month name: April 22, 2026 / Apr 22 2026
    m = re.search(r'([A-Za-z]{3,9})\s+(\d{1,2}),?\s+(\d{4})', text)
    if m:
        month_num = MONTH_NAMES.get(m.group(1).lower())
        if month_num:
            try:
                return date(int(m.group(3)), month_num, int(m.group(2)))
            except ValueError:
                pass

    return None


def extract_vendor(text: str) -> str | None:
    for line in text.splitlines():
        line = line.strip()
        if line:
            return line[:255]
    return None


def run_parse_pipeline() -> dict:
    counters = {"parsed": 0, "skipped": 0, "failed": 0}

    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        SELECT id, raw_text FROM receipt
        WHERE raw_text IS NOT NULL AND vendor IS NULL
    """)
    rows = cur.fetchall()

    for receipt_id, raw_text in rows:
        try:
            vendor = extract_vendor(raw_text)
            amount = extract_amount(raw_text)
            receipt_date = extract_date(raw_text)

            cur.execute(
                "UPDATE receipt SET vendor=%s, amount=%s, receipt_date=%s WHERE id=%s",
                (vendor, amount, receipt_date, receipt_id)
            )
            conn.commit()

            status = f"vendor={vendor!r} amount={amount} date={receipt_date}"
            print(f"[OK]   id={receipt_id} {status}")
            counters["parsed"] += 1
        except Exception as e:
            conn.rollback()
            print(f"[FAIL] id={receipt_id}: {e}")
            counters["failed"] += 1

    cur.close()
    conn.close()
    return counters


if __name__ == "__main__":
    import sys as _sys
    results = run_parse_pipeline()
    print()
    print("=" * 40)
    print(f"  Parsed  : {results['parsed']}")
    print(f"  Skipped : {results['skipped']}")
    print(f"  Failed  : {results['failed']}")
    print(f"  Total   : {sum(results.values())}")
    print("=" * 40)
    if results["failed"] > 0:
        _sys.exit(1)
