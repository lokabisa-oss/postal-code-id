#!/usr/bin/env python3

import csv
import json
import hashlib
from datetime import datetime, timezone
from pathlib import Path
import sys

# ============================================================
# CONFIG — PINNED & REPRODUCIBLE
# ============================================================

# Inputs (repo-relative)
REGIONS_ID_FILE = Path("regions_id.csv")
POS_JSONL_FILE = Path(
    "data/sources/kodepos-posindonesia-co-id/village_postal_codes.jsonl"
)

# Build metadata
BUILD_YEAR = datetime.now(timezone.utc).year
SOURCE_NAME = "POSINDONESIA_LOOKUP"
CONFIDENCE_POS = 1.0

# Outputs
OUTPUT_CORE_CSV = Path("postal_codes_pos_indonesia.csv")
OUTPUT_CORE_JSON = Path("postal_codes_pos_indonesia.json")
OUTPUT_ENRICHED_CSV = Path("postal_codes_pos_indonesia_enriched.csv")

# ============================================================
# UTILITIES
# ============================================================

def die(msg):
    print(f"ERROR: {msg}", file=sys.stderr)
    sys.exit(1)


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            h.update(chunk)
    return h.hexdigest()

# ============================================================
# LOADERS
# ============================================================

def load_regions_id(path: Path):
    """
    Load flattened regions_id.csv
    REQUIRED columns:
      village_code, village_name, village_type,
      district_code, district_name,
      regency_code, regency_name,
      province_code, province_name
    """
    villages = {}

    with path.open(newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)

        required = {
            "village_code",
            "village_name",
            "village_type",
            "district_code",
            "district_name",
            "regency_code",
            "regency_name",
            "province_code",
            "province_name",
        }

        missing = required - set(reader.fieldnames or [])
        if missing:
            die(f"regions_id.csv missing columns: {', '.join(sorted(missing))}")

        for row in reader:
            code = row["village_code"].strip()
            if not code:
                die("Empty village_code in regions_id.csv")

            villages[code] = {
                "village_name": row["village_name"].strip(),
                "village_type": row["village_type"].strip(),
                "district_code": row["district_code"].strip(),
                "district_name": row["district_name"].strip(),
                "regency_code": row["regency_code"].strip(),
                "regency_name": row["regency_name"].strip(),
                "province_code": row["province_code"].strip(),
                "province_name": row["province_name"].strip(),
            }

    if not villages:
        die("No villages loaded from regions_id.csv")

    return villages


def load_pos_indonesia_jsonl(path: Path):
    """
    Load POS Indonesia scrape JSONL.
    Expected keys per line:
      village_code, postal_code
    """
    mapping = {}

    with path.open(encoding="utf-8") as f:
        for line in f:
            if not line.strip():
                continue
            obj = json.loads(line)
            village_code = obj.get("village_code")
            postal_code = obj.get("postal_code")

            if not village_code or not postal_code:
                continue

            mapping[village_code] = postal_code

    if not mapping:
        die("No postal codes loaded from POS Indonesia JSONL")

    return mapping

# ============================================================
# BUILD LOGIC
# ============================================================

def build_records(villages, pos_map):
    core_records = []
    enriched_records = []

    for village_code, meta in villages.items():
        if village_code not in pos_map:
            # POS Indonesia ingestion is expected to be 100%
            continue

        postal_code = pos_map[village_code]

        core = {
            "postal_code": postal_code,
            "village_code": village_code,
            "village_name": meta["village_name"],
            "village_type": meta["village_type"],
            "source": SOURCE_NAME,
            "confidence": CONFIDENCE_POS,
            "year": BUILD_YEAR,
            "status": "AUGMENTED",
        }

        enriched = {
            **core,
            "district_code": meta["district_code"],
            "district_name": meta["district_name"],
            "regency_code": meta["regency_code"],
            "regency_name": meta["regency_name"],
            "province_code": meta["province_code"],
            "province_name": meta["province_name"],
        }

        core_records.append(core)
        enriched_records.append(enriched)

    return core_records, enriched_records

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
    if not REGIONS_ID_FILE.exists():
        die(f"Missing regions_id.csv: {REGIONS_ID_FILE}")

    if not POS_JSONL_FILE.exists():
        die(f"Missing POS Indonesia JSONL: {POS_JSONL_FILE}")

    villages = load_regions_id(REGIONS_ID_FILE)
    pos_map = load_pos_indonesia_jsonl(POS_JSONL_FILE)

    core, enriched = build_records(villages, pos_map)

    # Deterministic ordering
    core.sort(key=lambda r: r["village_code"])
    enriched.sort(key=lambda r: r["village_code"])

    write_csv(OUTPUT_CORE_CSV, core)
    write_json(OUTPUT_CORE_JSON, core)
    write_csv(OUTPUT_ENRICHED_CSV, enriched)

    print("Build complete (POS Indonesia)")
    print(f"- Core CSV      : {OUTPUT_CORE_CSV}  sha256:{sha256(OUTPUT_CORE_CSV)}")
    print(f"- Core JSON     : {OUTPUT_CORE_JSON} sha256:{sha256(OUTPUT_CORE_JSON)}")
    print(f"- Enriched CSV  : {OUTPUT_ENRICHED_CSV} sha256:{sha256(OUTPUT_ENRICHED_CSV)}")
    print(f"- Records       : {len(core)} villages")


if __name__ == "__main__":
    main()
