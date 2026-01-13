import argparse
import json
from datetime import datetime, timezone
datetime.now(timezone.utc).isoformat()

from postal_code_id_ingester.ingest.region_id_loader import (
    load_villages_from_region_id
)
from postal_code_id_ingester.export.resume import load_seen_village_codes


def main():
    parser = argparse.ArgumentParser(
        description="Generate coverage report for postal-code-id dataset"
    )
    parser.add_argument(
        "--regions",
        required=True,
        help="Path to regions_id.csv",
    )
    parser.add_argument(
        "--output",
        required=True,
        help="Path to output JSONL (ingestion result)",
    )
    parser.add_argument(
        "--coverage",
        default="coverage.json",
        help="Coverage report output (default: coverage.json)",
    )
    parser.add_argument(
        "--failed",
        default="failed_villages.jsonl",
        help="Failed villages JSONL output",
    )

    args = parser.parse_args()

    # Load ground truth
    villages = load_villages_from_region_id(args.regions)
    total = len(villages)
    print(f"Total villages in ground truth: {total}")

    # Load processed village_codes
    seen = load_seen_village_codes(args.output)
    matched = len(seen)

    # Compute missing
    missing_villages = [
        v for v in villages if v.village_code not in seen
    ]

    # ---- Write coverage report ----
    coverage = {
        "total_villages": total,
        "matched": matched,
        "missing": len(missing_villages),
        "coverage_percent": round((matched / total) * 100, 2) if total else 0.0,
        "generated_at": datetime.utcnow().isoformat() + "Z",
    }

    with open(args.coverage, "w", encoding="utf-8") as f:
        json.dump(coverage, f, indent=2)

    # ---- Write failed villages ----
    with open(args.failed, "w", encoding="utf-8") as f:
        for v in missing_villages:
            f.write(
                json.dumps(
                    {
                        "village_code": v.village_code,
                        "village": v.village,
                        "district_code": v.district_code,
                        "district": v.district,
                        "city": v.city,
                        "province": v.province,
                    },
                    ensure_ascii=False,
                )
                + "\n"
            )

    # ---- Console summary ----
    print("Coverage report generated")
    print(f"  Total villages : {total}")
    print(f"  Matched        : {matched}")
    print(f"  Missing        : {len(missing_villages)}")
    print(f"  Coverage       : {coverage['coverage_percent']}%")
    print(f"  → {args.coverage}")
    print(f"  → {args.failed}")


if __name__ == "__main__":
    main()
