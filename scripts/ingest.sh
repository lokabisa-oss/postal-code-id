#!/usr/bin/env bash
set -e

postal-code-id-ingester run \
  --regions regions_id.csv \
  --concurrency 3 \
  --output data/village_postal_codes.jsonl \
  --verbose
