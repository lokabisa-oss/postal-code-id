#!/usr/bin/env python3

import json
import sys
from pathlib import Path
from jsonschema import Draft202012Validator


SCHEMA_PATH = Path("schema/postal_code.schema.json")
DATA_PATH = Path("postal_codes.json")


def die(msg):
    print(f"SCHEMA VALIDATION FAILED: {msg}", file=sys.stderr)
    sys.exit(1)


def main():
    if not SCHEMA_PATH.exists():
        die(f"Missing schema file: {SCHEMA_PATH}")

    if not DATA_PATH.exists():
        die(f"Missing data file: {DATA_PATH}")

    with open(SCHEMA_PATH, "r", encoding="utf-8") as f:
        record_schema = json.load(f)

    with open(DATA_PATH, "r", encoding="utf-8") as f:
        data = json.load(f)

    if not isinstance(data, list):
        die("postal_codes.json must be an array of records")

    validator = Draft202012Validator(record_schema)

    error_count = 0
    for idx, record in enumerate(data):
        for err in validator.iter_errors(record):
            if error_count == 0:
                print("Schema violations found:", file=sys.stderr)
            print(f"- Record #{idx} ({record.get('village_code')}): {err.message}", file=sys.stderr)
            error_count += 1
            if error_count >= 10:
                print("... more errors omitted", file=sys.stderr)
                sys.exit(1)

    if error_count > 0:
        sys.exit(1)

    print("Schema validation passed ✔")
    print(f"- Records validated: {len(data)}")


if __name__ == "__main__":
    main()
