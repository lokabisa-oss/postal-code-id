#!/usr/bin/env python3

import csv
import json
import hashlib
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

# ============================================================
# CONFIG — REPRODUCIBLE & EXPLICIT
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parents[1]

# region-id (release artifact)
REGION_ID_RELEASE = "v1.0.1"
REGIONS_ID_FILE = PROJECT_ROOT / "regions_id.csv"

# OpenData Jabar (legacy official reference)
OPENDATA_JABAR_FILE = (
    PROJECT_ROOT
    / "data"
    / "sources"
    / "opendata-jabar"
    / "dispusipda-kode_pos_kab_kota_indonesia_data.csv"
)
OPENDATA_JABAR_YEAR = 2023

# Build metadata
BUILD_YEAR = datetime.now(timezone.utc).year
BUILD_SOURCE = "OPENDATA_JABAR"

# Output (scoped, non-destructive)
OUTPUT_CSV = PROJECT_ROOT / "postal_codes_opendata_jabar.csv"
OUTPUT_JSON = PROJECT_ROOT / "postal_codes_opendata_jabar.json"

# Confidence (per BUILD.md)
CONFIDENCE_OFFICIAL = 0.7

# ============================================================
# UTILITIES
# ============================================================

def die(msg: str):
    print(f"ERROR: {msg}", file=sys.stderr)
    sys.exit(1)


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            h.update(chunk)
    return h.hexdigest()


def normalize_kemendagri_code(value: str) -> str:
    """Normalize Kemendagri code like 11.01.01.2001 → 1101012001"""
    return re.sub(r"\D", "", value or "")

# ============================================================
# LOADERS
# ============================================================

def load_regions_id(path: Path):
    """
    Load village ground truth from regions_id.csv
    Required columns:
      - village_code
      - village_name
      - village_type
    """
    villages = {}

    if not path.exists():
        die(f"Missing regions_id.csv: {path}")

    with path.open(newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        required = {"village_code", "village_name", "village_type"}
        missing = required - set(reader.fieldnames or [])
        if missing:
            die(f"regions_id.csv missing columns: {', '.join(sorted(missing))}")

        for row in reader:
            code = row["village_code"].strip()
            if not code:
                die("Empty village_code found in regions_id.csv")

            villages[code] = {
                "village_name": row["village_name"].strip(),
                "village_type": row["village_type"].strip(),
            }

    if not villages:
        die("No villages loaded from regions_id.csv")

    return villages


def load_opendata_jabar(path: Path):
    """
    Load OpenData Jabar postal codes.
    Required columns:
      - kemendagri_kode_desa_kelurahan
      - kode_pos
    """
    mapping = {}

    if not path.exists():
        die(f"Missing OpenData Jabar file: {path}")

    with path.open(newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        required = {
            "kemendagri_kode_desa_kelurahan",
            "kode_pos",
        }
        missing = required - set(reader.fieldnames or [])
        if missing:
            die(f"OpenData Jabar CSV missing columns: {', '.join(sorted(missing))}")

        for row in reader:
            village_code = normalize_kemendagri_code(
                row["kemendagri_kode_desa_kelurahan"]
            )
            postal_code = (row.get("kode_pos") or "").strip()

            if not village_code:
                continue

            if postal_code and postal_code != "0":
                mapping[village_code] = postal_code

    print(f"Loaded {len(mapping)} postal codes from OpenData Jabar")
    return mapping

# ============================================================
# BUILD LOGIC
# ============================================================

def build_records(villages, official_map):
    """
    Build one record per village.
    OFFICIAL if available in OpenData Jabar, else UNASSIGNED.
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
            "status": "UNASSIGNED",
        }

        if village_code in official_map:
            record.update(
                {
                    "postal_code": official_map[village_code],
                    "source": BUILD_SOURCE,
                    "confidence": CONFIDENCE_OFFICIAL,
                    "year": OPENDATA_JABAR_YEAR,
                    "status": "OFFICIAL",
                }
            )

        records.append(record)

    return records

# ============================================================
# OUTPUT
# ============================================================

def write_csv(path: Path, records):
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(records[0].keys()))
        writer.writeheader()
        writer.writerows(records)


def write_json(path: Path, records):
    with path.open("w", encoding="utf-8") as f:
        json.dump(records, f, ensure_ascii=False, indent=2)

# ============================================================
# MAIN
# ============================================================

def main():
    villages = load_regions_id(REGIONS_ID_FILE)
    official_map = load_opendata_jabar(OPENDATA_JABAR_FILE)

    records = build_records(villages, official_map)
    records.sort(key=lambda r: r["village_code"])

    write_csv(OUTPUT_CSV, records)
    write_json(OUTPUT_JSON, records)

    total = len(records)
    official = sum(1 for r in records if r["status"] == "OFFICIAL")

    print("Build complete — OpenData Jabar (legacy)")
    print(f"Region-ID release : {REGION_ID_RELEASE}")
    print(f"Total villages   : {total}")
    print(f"OFFICIAL         : {official}")
    print(f"Coverage         : {(official / total) * 100:.2f}%")
    print(f"CSV  : {OUTPUT_CSV} (sha256: {sha256(OUTPUT_CSV)})")
    print(f"JSON : {OUTPUT_JSON} (sha256: {sha256(OUTPUT_JSON)})")


if __name__ == "__main__":
    main()
