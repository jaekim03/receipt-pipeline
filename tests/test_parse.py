from __future__ import annotations
import sys
import os
from datetime import date

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))
from parse import extract_amount, extract_date, extract_vendor


# --- extract_amount ---

def test_extract_amount_total_dollar():
    assert extract_amount("Total $12.34") == 12.34

def test_extract_amount_total_label_only():
    assert extract_amount("TOTAL: 8.00") == 8.00

def test_extract_amount_amount_due():
    assert extract_amount("Amount Due 99.50") == 99.50

def test_extract_amount_subtotal():
    assert extract_amount("Subtotal 5.00\nTotal 6.00") == 5.00

def test_extract_amount_dollar_sign_only():
    assert extract_amount("You owe $3.99") == 3.99

def test_extract_amount_no_match():
    assert extract_amount("no numbers here") is None


# --- extract_date ---

def test_extract_date_iso():
    assert extract_date("Date: 2026-04-22") == date(2026, 4, 22)

def test_extract_date_slash_mdy():
    assert extract_date("04/22/2026") == date(2026, 4, 22)

def test_extract_date_month_name_long():
    assert extract_date("April 22, 2026") == date(2026, 4, 22)

def test_extract_date_month_name_short():
    assert extract_date("Apr 22 2026") == date(2026, 4, 22)

def test_extract_date_no_match():
    assert extract_date("no date here") is None


# --- extract_vendor ---

def test_extract_vendor_first_line():
    assert extract_vendor("Starbucks\n123 Main St\nTotal $5.00") == "Starbucks"

def test_extract_vendor_skips_blank_lines():
    assert extract_vendor("\n\nCostco\nSome Address") == "Costco"

def test_extract_vendor_truncates_long_line():
    long_line = "A" * 300
    result = extract_vendor(long_line)
    assert result == "A" * 255

def test_extract_vendor_empty_text():
    assert extract_vendor("") is None
