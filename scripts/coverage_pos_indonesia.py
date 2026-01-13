#!/usr/bin/env python3

import argparse
import json
from datetime import datetime, timezone

from postal_code_id_ingester.ingest.region_id_loader import (
    load_villages_from_region_id
)
from postal_code_id_ingester.export.resume import (
    load_seen_village_codes
)


def main():
    parser = argparse.ArgumentParser(
        description="Coverage report for Pos Indonesia ingestion vs region-id"
    )
    parser.add_argument(
        "--regions",
        required=True,
        help="Path to regions_id.csv (ground truth)",
    )
    parser.add_argument(
        "--output",
        required=True,
        help="Path to ingestion JSONL (Pos Indonesia lookup result)",
    )
    parser.add_argument(
        "--coverage",
        default="coverage_pos_indonesia.json",
        help="Coverage report output JSON",
    )
    parser.add_argument(
        "--failed",
        default="failed_villages_pos_indonesia.jsonl",
        help="Missing villages output (JSONL)",
    )

    args = parser.parse_args()

    # ------------------------------------------------------------
    # Load ground truth (region-id)
    # ------------------------------------------------------------
    villages = load_villages_from_region_id(args.regions)
    total = len(villages)
    print(f"Total villages in region-id: {total}")

    # ------------------------------------------------------------
    # Load ingested village codes
    # ------------------------------------------------------------
    seen = load_seen_village_codes(args.output)
    matched = len(seen)

    # ------------------------------------------------------------
    # Compute missing villages
    # ------------------------------------------------------------
    missing_villages = [
        v for v in villages if v.village_code not in seen
    ]

    # ------------------------------------------------------------
    # Coverage report
    # ------------------------------------------------------------
    coverage = {
        "source": "POSINDONESIA_LOOKUP",
        "baseline": "region-id",
        "total_villages": total,
        "matched": matched,
        "missing": len(missing_villages),
        "coverage_percent": round((matched / total) * 100, 2) if total else 0.0,
        "generated_at": datetime.now(timezone.utc).isoformat(),
    }

    with open(args.coverage, "w", encoding="utf-8") as f:
        json.dump(coverage, f, indent=2, ensure_ascii=False)

    # ------------------------------------------------------------
    # Failed villages (JSONL)
    # ------------------------------------------------------------
    with open(args.failed, "w", encoding="utf-8") as f:
        for v in missing_villages:
            f.write(
                json.dumps(
                    {
                        "village_code": v.village_code,
                        "village_name": v.village,
                        "district_code": v.district_code,
                        "district_name": v.district,
                        "regency_code": v.city_code,
                        "regency_name": v.city,
                        "province_code": v.province_code,
                        "province_name": v.province,
                    },
                    ensure_ascii=False,
                )
                + "\n"
            )

    # ------------------------------------------------------------
    # Console summary
    # ------------------------------------------------------------
    print("Coverage Pos Indonesia")
    print(f"- Total villages : {total}")
    print(f"- Matched        : {matched}")
    print(f"- Missing        : {len(missing_villages)}")
    print(f"- Coverage       : {coverage['coverage_percent']}%")
    print(f"→ {args.coverage}")
    print(f"→ {args.failed}")


if __name__ == "__main__":
    main()
