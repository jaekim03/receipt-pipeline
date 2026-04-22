import sys
from pathlib import Path


import cv2
import numpy as np
from PIL import Image
from pillow_heif import register_heif_opener

register_heif_opener()

SCRIPT_DIR = Path(__file__).resolve().parent
RAW_DIR    = SCRIPT_DIR / ".." / "data" / "raw"
PROC_DIR   = SCRIPT_DIR / ".." / "data" / "processed"

SUPPORTED_RASTER = {".jpg", ".jpeg", ".png"}
SUPPORTED_HEIC   = {".heic"}
UNSUPPORTED      = {".pdf"}
KNOWN_EXTENSIONS = SUPPORTED_RASTER | SUPPORTED_HEIC | UNSUPPORTED


def load_image_as_bgr(raw_path: Path):
    ext = raw_path.suffix.lower()

    if ext in SUPPORTED_RASTER:
        buf = np.fromfile(str(raw_path), dtype=np.uint8)
        img = cv2.imdecode(buf, cv2.IMREAD_COLOR)
        return img  # None if corrupted

    if ext in SUPPORTED_HEIC:
        pil_img = Image.open(raw_path).convert("RGB")
        arr = np.array(pil_img)
        return cv2.cvtColor(arr, cv2.COLOR_RGB2BGR)

    return None


def preprocess_image(img: np.ndarray) -> np.ndarray:
    gray    = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    blurred = cv2.GaussianBlur(gray, (3, 3), 0)
    thresh  = cv2.adaptiveThreshold(
        blurred, 255,
        cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
        cv2.THRESH_BINARY,
        11, 2
    )
    return thresh


def save_processed(processed_img: np.ndarray, out_path: Path) -> bool:
    ext = out_path.suffix.lower()
    encode_ext = ext if ext in {".jpg", ".jpeg", ".png"} else ".png"
    success, buf = cv2.imencode(encode_ext, processed_img)
    if not success:
        return False
    buf.tofile(str(out_path))
    return True


def run_preprocess() -> dict:
    PROC_DIR.mkdir(exist_ok=True)
    counters = {"processed": 0, "skipped": 0, "failed": 0, "unsupported": 0}

    for raw_path in sorted(RAW_DIR.iterdir()):
        if raw_path.suffix.lower() not in KNOWN_EXTENSIONS:
            continue

        ext = raw_path.suffix.lower()

        out_name = (raw_path.stem + ".png") if ext in SUPPORTED_HEIC else raw_path.name
        out_path = PROC_DIR / out_name

        if out_path.exists():
            counters["skipped"] += 1
            continue

        if ext in UNSUPPORTED:
            print(f"[SKIP] Unsupported format (PDF): {raw_path.name}")
            counters["unsupported"] += 1
            continue

        img = load_image_as_bgr(raw_path)
        if img is None:
            print(f"[FAIL] Could not load: {raw_path.name}")
            counters["failed"] += 1
            continue

        try:
            processed = preprocess_image(img)
        except Exception as e:
            print(f"[FAIL] {raw_path.name}: {e}")
            counters["failed"] += 1
            continue

        if save_processed(processed, out_path):
            print(f"[OK]   {raw_path.name}")
            counters["processed"] += 1
        else:
            print(f"[FAIL] Could not save: {raw_path.name}")
            counters["failed"] += 1

    return counters


if __name__ == "__main__":
    results = run_preprocess()
    print()
    print("=" * 40)
    print(f"  Processed  : {results['processed']}")
    print(f"  Skipped    : {results['skipped']}  (already done)")
    print(f"  Failed     : {results['failed']}")
    print(f"  Unsupported: {results['unsupported']}  (PDFs — deferred to Phase 3)")
    print(f"  Total seen : {sum(results.values())}")
    print("=" * 40)
    if results["failed"] > 0:
        sys.exit(1)
