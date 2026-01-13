#!/usr/bin/env bash
set -e

postal-code-id-ingester run \
  --regions failed_regions.csv \
  --output data/village_postal_codes.jsonl \
  --concurrency 3 \
  --enable-overrides \
  --override-table data/sources/postal_ingest_name_overrides.csv \
  --verbose
