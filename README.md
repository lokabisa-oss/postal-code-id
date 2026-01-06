# postal-code-id

Indonesian Postal Code Dataset  
Linked to Indonesian administrative regions (region-id)

## Latest Release

- Version: v2025Q1
- Coverage:
  - 100% of region-id villages are represented
  - 84.21% have official postal codes (Open Data Jawa Barat, 2023)
  - 15.79% are marked as UNASSIGNED
- Downloads:
  - postal_codes.csv
  - postal_codes.json

➡️ Download from the GitHub Releases page.

## Data Schema

See `schema/postal_code.schema.json`

## Data Sources

- Open Data Jawa Barat – Postal Code Dataset (2023)  
  (archived in `lokabisa-oss/id-documents`)
- Pos Indonesia public postal lookup  
  (used for confidence-based augmentation only, not redistributed)

## Notes

- Village identifiers, names, and types are aligned with `region-id`.
- Augmented records are explicitly marked and include confidence scores.
- Some villages may not have official postal codes and are marked accordingly.

## Disclaimer

Postal codes are operational data managed by Pos Indonesia.
This dataset is non-authoritative and provided for reference purposes only.

---

## Reproducibility

This dataset is designed to be **fully reproducible and auditable**.

The build process consumes **only pinned, immutable inputs** and produces
deterministic outputs.

### Requirements

- Python 3.9+
- `jsonschema` (required for schema validation; may already be available)

### Steps

1. Clone this repository:
   ```bash
   git clone https://github.com/lokabisa-oss/postal-code-id.git
   cd postal-code-id
   ```
2. Fetch input datasets (pinned references):

   Administrative reference (region-id v1.0.0):

   ```bash
    curl -L \
    https://github.com/lokabisa-oss/region-id/releases/download/v1.0.0/regions_id.csv \
    -o regions_id.csv
   ```

   Official postal code baseline (Open Data Jawa Barat, 2023):

   ```bash
    # Replace <REF> with the pinned commit SHA or tag used in BUILD.md
    curl -L \
    https://raw.githubusercontent.com/lokabisa-oss/id-documents/<REF>/opendata-jabar/postal-code/2023/dispusipda-kode_pos_kab_kota_indonesia_data.csv \
    -o dispusipda-kode_pos_kab_kota_indonesia_data.csv
   ```

   **Example (non-reproducible, for convenience only):**

   The following command fetches the dataset from the current `main` branch.
   This is useful for quick experiments, but **not suitable for reproducible builds**.

   ```bash
   curl -L \
   https://raw.githubusercontent.com/lokabisa-oss/id-documents/refs/heads/main/opendata-jabar/postal-code/2023/dispusipda-kode_pos_kab_kota_indonesia_data.csv \
   -o dispusipda-kode_pos_kab_kota_indonesia_data.csv
   ```

   For reproducible builds and official releases, always use a **pinned commit
   SHA or tag** as documented in `BUILD.md`.

3. (Recommended) Verify input integrity (CSV only):

   Fetch the checksum file from the same pinned reference:

   ```bash
   curl -L \
   https://raw.githubusercontent.com/lokabisa-oss/id-documents/<REF>/opendata-jabar/postal-code/2023/SHA256SUMS \
   -o SHA256SUMS
   ```

   The checksum file may list multiple artifacts.
   If you only fetched the CSV file, you can verify it selectively:

   ```bash
   grep dispusipda-kode_pos_kab_kota_indonesia_data.csv SHA256SUMS | sha256sum -c -
   ```

4. Run the deterministic build:
   ```bash
   python3 scripts/build.py
   ```
5. Validate the output schema:
   ```bash
   python3 scripts/validate_schema.py
   ```
