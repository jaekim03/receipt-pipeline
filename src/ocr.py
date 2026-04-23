from __future__ import annotations
import sys
import os
from pathlib import Path

import cv2
import numpy as np
from PIL import Image
import pytesseract

sys.path.insert(0, os.path.dirname(__file__))
from db import get_connection

SCRIPT_DIR = Path(__file__).resolve().parent
PROC_DIR   = SCRIPT_DIR / ".." / "data" / "processed"

HEIC_EXTENSIONS = {".heic"}


def get_processed_path(file_name: str) -> Path | None:
    raw_path = Path(file_name)
    if raw_path.suffix.lower() in HEIC_EXTENSIONS:
        processed_path = PROC_DIR / (raw_path.stem + ".png")
    else:
        processed_path = PROC_DIR / raw_path.name

    return processed_path if processed_path.exists() else None


def run_ocr(processed_path: Path) -> str:
    buf = np.fromfile(str(processed_path), dtype=np.uint8)
    img_bgr = cv2.imdecode(buf, cv2.IMREAD_COLOR)
    img_rgb = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2RGB)
    pil_img = Image.fromarray(img_rgb)
    return pytesseract.image_to_string(pil_img)


def run_ocr_pipeline() -> dict:
    counters = {"processed": 0, "skipped": 0, "failed": 0}

    conn = get_connection()
    cur = conn.cursor()

    cur.execute("SELECT id, file_name FROM receipt WHERE raw_text IS NULL")
    rows = cur.fetchall()

    for receipt_id, file_name in rows:
        processed_path = get_processed_path(file_name)

        if processed_path is None:
            print(f"[SKIP] No processed file for: {file_name}")
            counters["skipped"] += 1
            continue

        try:
            raw_text = run_ocr(processed_path)
            cur.execute(
                "UPDATE receipt SET raw_text = %s WHERE id = %s",
                (raw_text, receipt_id)
            )
            conn.commit()
            print(f"[OK]   {file_name}")
            counters["processed"] += 1
        except Exception as e:
            conn.rollback()
            print(f"[FAIL] {file_name}: {e}")
            counters["failed"] += 1

    cur.close()
    conn.close()
    return counters


if __name__ == "__main__":
    results = run_ocr_pipeline()
    print()
    print("=" * 40)
    print(f"  Processed : {results['processed']}")
    print(f"  Skipped   : {results['skipped']}  (no processed file — PDFs etc.)")
    print(f"  Failed    : {results['failed']}")
    print(f"  Total     : {sum(results.values())}")
    print("=" * 40)
    if results["failed"] > 0:
        sys.exit(1)
