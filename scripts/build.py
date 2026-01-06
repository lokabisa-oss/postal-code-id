#!/usr/bin/env python3

import csv
import json
import hashlib
import re
from datetime import datetime, timezone
from pathlib import Path
import sys

# ============================================================
# CONFIG — PINNED & EXPLICIT (per BUILD.md)
# ============================================================

# region-id (release artifact)
REGION_ID_RELEASE = "v1.0.0"
REGION_ID_FILE = "regions_id.csv"   # from region-id GitHub Release asset

# Open Data Jawa Barat (baseline)
OPENDATA_JABAR_FILE = "dispusipda-kode_pos_kab_kota_indonesia_data.csv"
OPENDATA_JABAR_YEAR = 2023

# Build
BUILD_YEAR = datetime.now(timezone.utc).year

# Output
OUTPUT_CSV = "postal_codes.csv"
OUTPUT_JSON = "postal_codes.json"

# Confidence (per BUILD.md)
CONFIDENCE_OFFICIAL = 0.7

# ============================================================
# UTILITIES
# ============================================================

def die(msg):
    print(f"ERROR: {msg}", file=sys.stderr)
    sys.exit(1)


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            h.update(chunk)
    return h.hexdigest()


def normalize_kemendagri_code(value: str) -> str:
    """
    Normalize Kemendagri codes like:
    11.01.01.2001 -> 1101012001
    """
    return re.sub(r"\D", "", value or "")

# ============================================================
# LOADERS
# ============================================================

def load_region_id_regions(path: Path):
    """
    Load flattened administrative snapshot from regions_id.csv
    Expected columns (minimum):
      - village_code
      - village_name
      - village_type (village | urban_village)
    """
    villages = {}

    with open(path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        required_cols = {"village_code", "village_name", "village_type"}
        missing = required_cols - set(reader.fieldnames or [])
        if missing:
            die(f"regions_id.csv missing columns: {', '.join(sorted(missing))}")

        for row in reader:
            code = row["village_code"].strip()
            if not code:
                die("Empty village_code found in regions_id.csv")

            villages[code] = {
                "village_name": row["village_name"].strip(),
                "village_type": row["village_type"].strip()
            }

    if not villages:
        die("No villages loaded from regions_id.csv")

    return villages


def load_opendata_jabar(path: Path):
    """
    Load Open Data Jawa Barat baseline.
    Uses ONLY:
      - kemendagri_kode_desa_kelurahan
      - kode_pos
    """
    mapping = {}

    with open(path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        required_cols = {
            "kemendagri_kode_desa_kelurahan",
            "kode_pos"
        }
        missing = required_cols - set(reader.fieldnames or [])
        if missing:
            die(f"Open Data Jabar CSV missing columns: {', '.join(sorted(missing))}")

        for row in reader:
            raw_code = row["kemendagri_kode_desa_kelurahan"]
            village_code = normalize_kemendagri_code(raw_code)
            postal_code = (row.get("kode_pos") or "").strip()

            if not village_code:
                continue

            # Ignore empty / zero postal codes
            if postal_code and postal_code != "0":
                mapping[village_code] = postal_code

    print(f"Loaded {len(mapping)} OFFICIAL postal codes from Open Data Jabar")
    return mapping

# ============================================================
# BUILD LOGIC (per BUILD.md)
# ============================================================

def build_records(villages, official_map):
    """
    Build exactly one record per village (100% coverage).
    OFFICIAL if present in Open Data Jabar, else UNASSIGNED.
    """
    records = []

    for village_code, meta in villages.items():
        record = {
            "postal_code": None,
            "village_code": village_code,
            "village_name": meta["village_name"],
            "village_type": meta["village_type"],
            "source": "NONE",
            "confidence": 0.0,
            "year": BUILD_YEAR,
            "status": "UNASSIGNED"
        }

        if village_code in official_map:
            record.update({
                "postal_code": official_map[village_code],
                "source": "OPENDATA_JABAR",
                "confidence": CONFIDENCE_OFFICIAL,
                "year": OPENDATA_JABAR_YEAR,
                "status": "OFFICIAL"
            })

        records.append(record)

    return records

# ============================================================
# OUTPUT
# ============================================================

def write_csv(path: Path, records):
    with open(path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(
            f,
            fieldnames=list(records[0].keys())
        )
        writer.writeheader()
        writer.writerows(records)


def write_json(path: Path, records):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(records, f, ensure_ascii=False, indent=2)

# ============================================================
# MAIN
# ============================================================

def main():
    region_id_path = Path(REGION_ID_FILE)
    opendata_path = Path(OPENDATA_JABAR_FILE)

    if not region_id_path.exists():
        die(f"Missing region-id artifact: {REGION_ID_FILE}")

    if not opendata_path.exists():
        die(f"Missing Open Data Jabar file: {OPENDATA_JABAR_FILE}")

    villages = load_region_id_regions(region_id_path)
    official_map = load_opendata_jabar(opendata_path)

    records = build_records(villages, official_map)

    # Deterministic ordering
    records.sort(key=lambda r: r["village_code"])

    # Write outputs
    out_csv = Path(OUTPUT_CSV)
    out_json = Path(OUTPUT_JSON)

    write_csv(out_csv, records)
    write_json(out_json, records)

    print("Build complete")
    print(f"Input  region-id ({REGION_ID_RELEASE}) : {REGION_ID_FILE}")
    print(f"Input  Open Data Jabar                : {OPENDATA_JABAR_FILE}")
    print(f"Output CSV  {OUTPUT_CSV}  sha256:{sha256(out_csv)}")
    print(f"Output JSON {OUTPUT_JSON} sha256:{sha256(out_json)}")

    # ------------------------------------------------------------
    # Coverage Report (observability only; does not affect outputs)
    # ------------------------------------------------------------
    total = len(records)
    official = sum(1 for r in records if r["status"] == "OFFICIAL")
    unassigned = total - official
    coverage_pct = (official / total) * 100 if total else 0.0

    print("\nCoverage Report")
    print(f"- Total villages   : {total}")
    print(f"- OFFICIAL         : {official}")
    print(f"- UNASSIGNED       : {unassigned}")
    print(f"- Official coverage: {coverage_pct:.2f}%")


if __name__ == "__main__":
    main()
