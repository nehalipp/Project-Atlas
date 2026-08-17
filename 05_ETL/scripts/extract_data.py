import csv
import hashlib
import json
import shutil
import sys
from datetime import datetime, timezone
from pathlib import Path


# ============================================================
# Allow imports from 05_ETL
# ============================================================

ETL_ROOT = Path(__file__).resolve().parents[1]

if str(ETL_ROOT) not in sys.path:
    sys.path.insert(0, str(ETL_ROOT))


from config.etl_config import (
    EXPECTED_DATASETS,
    EXPECTED_ROW_COUNTS,
    EXPECTED_TOTAL_ROWS,
    LOG_DIR,
    RAW_DATA_DIR,
    TRUSTED_DATA_DIR,
)


# ============================================================
# Utility Functions
# ============================================================

def count_csv_rows(file_path: Path) -> int:
    """
    Count data rows in a CSV file, excluding the header.
    """
    with file_path.open(
        "r",
        encoding="utf-8",
        newline=""
    ) as file:

        reader = csv.reader(file)

        # Skip header
        next(reader, None)

        return sum(1 for _ in reader)


def calculate_sha256(file_path: Path) -> str:
    """
    Calculate SHA-256 checksum for source-file traceability.
    """
    digest = hashlib.sha256()

    with file_path.open("rb") as file:
        for chunk in iter(
            lambda: file.read(1024 * 1024),
            b""
        ):
            digest.update(chunk)

    return digest.hexdigest()


def write_log(results: list[dict]) -> Path:
    """
    Write extraction results to a timestamped JSON log.
    """

    LOG_DIR.mkdir(
        parents=True,
        exist_ok=True
    )

    timestamp = datetime.now(
        timezone.utc
    ).strftime("%Y%m%dT%H%M%SZ")

    log_file = (
        LOG_DIR
        / f"extract_{timestamp}.json"
    )

    log_file.write_text(
        json.dumps(
            results,
            indent=2
        ),
        encoding="utf-8"
    )

    return log_file


# ============================================================
# Main Extraction Process
# ============================================================

def main() -> None:

    print("=" * 70)
    print("Project Atlas — Phase 5 ETL — Trusted to Raw")
    print("=" * 70)

    # --------------------------------------------------------
    # Validate source directory
    # --------------------------------------------------------

    if not TRUSTED_DATA_DIR.exists():
        raise FileNotFoundError(
            f"Trusted data directory not found:\n"
            f"{TRUSTED_DATA_DIR}"
        )

    # --------------------------------------------------------
    # Create Raw directory
    # --------------------------------------------------------

    RAW_DATA_DIR.mkdir(
        parents=True,
        exist_ok=True
    )

    results = []

    total_source_rows = 0
    total_raw_rows = 0

    # --------------------------------------------------------
    # Extract each Atlas dataset
    # --------------------------------------------------------

    for dataset in EXPECTED_DATASETS:

        source_file = (
            TRUSTED_DATA_DIR
            / f"{dataset}.csv"
        )

        raw_file = (
            RAW_DATA_DIR
            / f"{dataset}.csv"
        )

        print(f"\nProcessing: {dataset}.csv")

        # ----------------------------------------------------
        # Source file existence
        # ----------------------------------------------------

        if not source_file.exists():
            raise FileNotFoundError(
                f"Required trusted dataset not found:\n"
                f"{source_file}"
            )

        # ----------------------------------------------------
        # Count source rows
        # ----------------------------------------------------

        source_rows = count_csv_rows(
            source_file
        )

        expected_rows = EXPECTED_ROW_COUNTS[
            dataset
        ]

        if source_rows != expected_rows:
            raise RuntimeError(
                f"Source row-count mismatch for "
                f"{dataset}.csv\n"
                f"Expected: {expected_rows:,}\n"
                f"Actual:   {source_rows:,}"
            )

        # ----------------------------------------------------
        # Calculate source checksum
        # ----------------------------------------------------

        source_checksum = calculate_sha256(
            source_file
        )

        # ----------------------------------------------------
        # Copy trusted source into Raw
        # ----------------------------------------------------

        shutil.copy2(
            source_file,
            raw_file
        )

        # ----------------------------------------------------
        # Validate Raw copy
        # ----------------------------------------------------

        raw_rows = count_csv_rows(
            raw_file
        )

        if raw_rows != source_rows:
            raise RuntimeError(
                f"Raw row-count mismatch for "
                f"{dataset}.csv\n"
                f"Source rows: {source_rows:,}\n"
                f"Raw rows:    {raw_rows:,}"
            )

        raw_checksum = calculate_sha256(
            raw_file
        )

        if source_checksum != raw_checksum:
            raise RuntimeError(
                f"Checksum mismatch for "
                f"{dataset}.csv"
            )

        # ----------------------------------------------------
        # Record successful extraction
        # ----------------------------------------------------

        result = {
            "dataset": dataset,
            "source_file": str(source_file),
            "raw_file": str(raw_file),
            "expected_rows": expected_rows,
            "source_rows": source_rows,
            "raw_rows": raw_rows,
            "source_sha256": source_checksum,
            "raw_sha256": raw_checksum,
            "status": "PASS",
        }

        results.append(result)

        total_source_rows += source_rows
        total_raw_rows += raw_rows

        print(
            f"Rows: {source_rows:,} | "
            f"Checksum: PASS | "
            f"Extraction: PASS"
        )

    # --------------------------------------------------------
    # Validate total record counts
    # --------------------------------------------------------

    print("\n" + "-" * 70)

    print(
        f"Expected total rows: {EXPECTED_TOTAL_ROWS:,}"
    )

    print(
        f"Source total rows:   {total_source_rows:,}"
    )

    print(
        f"Raw total rows:      {total_raw_rows:,}"
    )

    if total_source_rows != EXPECTED_TOTAL_ROWS:
        raise RuntimeError(
            "Total source row-count validation failed."
        )

    if total_raw_rows != EXPECTED_TOTAL_ROWS:
        raise RuntimeError(
            "Total Raw row-count validation failed."
        )

    # --------------------------------------------------------
    # Write extraction log
    # --------------------------------------------------------

    log_file = write_log(results)

    # --------------------------------------------------------
    # Final status
    # --------------------------------------------------------

    print("\n" + "=" * 70)
    print("ETL EXTRACTION STATUS: SUCCESS")
    print("=" * 70)

    print(
        f"Datasets extracted: {len(results)}"
    )

    print(
        f"Total rows:         {total_raw_rows:,}"
    )

    print(
        f"Raw directory:      {RAW_DATA_DIR}"
    )

    print(
        f"Log file:           {log_file}"
    )

    print("=" * 70)


if __name__ == "__main__":
    main()