#!/usr/bin/env python3

import argparse
import csv
import json
import re
from datetime import datetime, timezone
from pathlib import Path


# ------------------------------------------------------------
# Utilities
# ------------------------------------------------------------

def normalize_kemendagri_code(value: str) -> str:
    """11.01.01.2001 → 1101012001"""
    return re.sub(r"\D", "", value or "")


# ------------------------------------------------------------
# Loaders
# ------------------------------------------------------------

def load_regions_id(path: Path):
    villages = {}

    with open(path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            code = row["village_code"].strip()
            villages[code] = {
                "village_code": code,
                "village_name": row.get("village_name"),
                "district_code": row.get("district_code"),
                "district_name": row.get("district_name"),
                "regency_code": row.get("regency_code"),
                "regency_name": row.get("regency_name"),
                "province_code": row.get("province_code"),
                "province_name": row.get("province_name"),
            }

    return villages


def load_opendata_jabar_csv(path: Path):
    seen = set()

    with open(path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            raw_code = row.get("kemendagri_kode_desa_kelurahan")
            postal_code = (row.get("kode_pos") or "").strip()

            if not raw_code:
                continue
            if not postal_code or postal_code == "0":
                continue

            village_code = normalize_kemendagri_code(raw_code)
            if village_code:
                seen.add(village_code)

    return seen


# ------------------------------------------------------------
# Main
# ------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(
        description="Coverage report for OpenData Jabar postal codes vs region-id"
    )
    parser.add_argument(
        "--regions",
        required=True,
        help="Path to regions_id.csv",
    )
    parser.add_argument(
        "--output",
        required=True,
        help="Path to OpenData Jabar CSV",
    )
    parser.add_argument(
        "--coverage",
        default="coverage_opendata_jabar.json",
        help="Coverage report output",
    )
    parser.add_argument(
        "--failed",
        default="failed_villages_opendata_jabar.jsonl",
        help="Missing villages output",
    )

    args = parser.parse_args()

    regions = load_regions_id(Path(args.regions))
    seen = load_opendata_jabar_csv(Path(args.opendata))

    total = len(regions)
    matched = sum(1 for code in regions if code in seen)
    missing = total - matched

    # ---- coverage report ----
    coverage = {
        "source": "OPENDATA_JABAR",
        "baseline": "regions_id",
        "total_villages": total,
        "matched": matched,
        "missing": missing,
        "coverage_percent": round((matched / total) * 100, 2) if total else 0.0,
        "generated_at": datetime.now(timezone.utc).isoformat(),
    }

    with open(args.coverage, "w", encoding="utf-8") as f:
        json.dump(coverage, f, indent=2, ensure_ascii=False)

    # ---- failed villages ----
    with open(args.failed, "w", encoding="utf-8") as f:
        for code, v in regions.items():
            if code not in seen:
                f.write(
                    json.dumps(v, ensure_ascii=False) + "\n"
                )

    # ---- summary ----
    print("Coverage OpenData Jabar")
    print(f"- Total villages : {total}")
    print(f"- Matched        : {matched}")
    print(f"- Missing        : {missing}")
    print(f"- Coverage       : {coverage['coverage_percent']}%")
    print(f"→ {args.coverage}")
    print(f"→ {args.failed}")


if __name__ == "__main__":
    main()
