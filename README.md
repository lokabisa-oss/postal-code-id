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
