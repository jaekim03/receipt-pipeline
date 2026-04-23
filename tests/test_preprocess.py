from pathlib import Path

RAW_DIR  = Path(__file__).resolve().parent / ".." / "data" / "raw"
PROC_DIR = Path(__file__).resolve().parent / ".." / "data" / "processed"

SKIP_EXTENSIONS  = {".pdf"}
HEIC_EXTENSIONS  = {".heic"}
KNOWN_EXTENSIONS = {".jpg", ".jpeg", ".png", ".heic", ".pdf"}


def get_expected_processed_name(raw_path):
    if raw_path.suffix.lower() in HEIC_EXTENSIONS:
        return raw_path.stem + ".png"
    return raw_path.name


def test_all_raw_files_have_processed_counterpart():
    missing = []
    for raw_path in sorted(RAW_DIR.iterdir()):
        if raw_path.suffix.lower() not in KNOWN_EXTENSIONS:
            continue
        if raw_path.suffix.lower() in SKIP_EXTENSIONS:
            continue
        expected = PROC_DIR / get_expected_processed_name(raw_path)
        if not expected.exists():
            missing.append(raw_path.name)
    assert missing == [], f"Missing processed files for: {missing}"


def test_processed_count_matches_raw_minus_pdfs():
    raw_count = sum(
        1 for f in RAW_DIR.iterdir()
        if f.suffix.lower() in KNOWN_EXTENSIONS
        and f.suffix.lower() not in SKIP_EXTENSIONS
    )
    proc_count = sum(
        1 for f in PROC_DIR.iterdir()
        if f.suffix.lower() in {".jpg", ".jpeg", ".png"}
    )
    assert proc_count == raw_count, (
        f"Expected {raw_count} processed files, found {proc_count}"
    )
