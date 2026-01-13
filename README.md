<p align="center">
  <img
    src="https://raw.githubusercontent.com/lokabisa-oss/postal-code-id/main/metadata/og-postal-code-id.png"
    alt="postal-code-id — Indonesian Postal Code Dataset"
    width="100%"
  />
</p>

<p align="center">
  <a href="https://github.com/lokabisa-oss/postal-code-id/releases">
    <img src="https://img.shields.io/github/v/release/lokabisa-oss/postal-code-id?style=flat-square" />
  </a>
  <a href="https://github.com/lokabisa-oss/postal-code-id">
    <img src="https://img.shields.io/github/repo-size/lokabisa-oss/postal-code-id?style=flat-square" />
  </a>
  <a href="https://github.com/lokabisa-oss/postal-code-id/blob/main/LICENSE">
    <img src="https://img.shields.io/github/license/lokabisa-oss/postal-code-id?style=flat-square" />
  </a>
</p>

# postal-code-id

Indonesian Postal Code Dataset  
Linked to Indonesian administrative regions (`region-id`)

This repository provides **versioned, auditable postal code datasets**
mapped to Indonesian administrative villages.

Postal code coverage is published in **two clearly differentiated release types**
to preserve data provenance and correctness.

---

## 📦 Release Types

### 1️⃣ Official Baseline Release (Open Data Jawa Barat)

This release represents **officially published postal code data**
sourced from Open Data Jawa Barat (2023).

- Coverage:
  - 100% of `region-id` villages are represented
  - ~84% have official postal codes
  - Remaining villages are marked as `UNASSIGNED`
- Source:
  - Open Data Jawa Barat (2023)
- Characteristics:
  - Conservative
  - Source-authoritative
  - Suitable as a baseline reference

**Example release:**

- Version: `v2025Q1`
- Assets:
  - `postal_codes.csv`
  - `postal_codes.json`

🔗 Release page:  
https://github.com/lokabisa-oss/postal-code-id/releases/tag/v2025Q1

---

### 2️⃣ Derived Full-Coverage Release (Pos Indonesia + region-id)

This release provides **100% postal code coverage** by augmenting
the official baseline with results derived from
**Pos Indonesia public postal lookup**, aligned strictly to `region-id`.

- Coverage:
  - 100% of `region-id` villages have postal codes
- Source composition:
  - Open Data Jawa Barat (official baseline)
  - Pos Indonesia public lookup (derived signal)
- Characteristics:
  - Fully complete
  - Explicitly marked as `AUGMENTED`
  - Includes confidence scores per record
  - Traceable and auditable

This release is intended for:

- Data engineering
- Search, validation, and enrichment pipelines
- Practical applications requiring full coverage

⚠️ This release is **non-authoritative** and must not be treated
as an official postal code registry.

(Release tag and documentation will explicitly indicate this status.)

---

## 📄 Spreadsheet Preview

For quick inspection and human-friendly browsing, a public Google Spreadsheet
preview of the dataset is available:

👉 **Spreadsheet preview:**  
https://docs.google.com/spreadsheets/d/1WA137b3k7NmQngzcb0QL8WG-gvMUFT3K92KGipl3T7A

**Notes:**

- Read-only preview
- May contain derived or merged views
- The authoritative artifacts are always the GitHub Releases

---

## Data Schema

See `schema/postal_code.schema.json`

The schema is **shared across release types**, with the following guarantees:

- Source attribution per record
- Explicit status (`OFFICIAL`, `AUGMENTED`, `UNASSIGNED`)
- Confidence scoring for non-official mappings

---

## Data Sources

- **Open Data Jawa Barat** – Postal Code Dataset (2023)  
  (archived in `lokabisa-oss/id-documents`)
- **Pos Indonesia public postal lookup**  
  (used for augmentation only, not redistributed)

---

## Notes

- Village identifiers, names, and types are aligned with `region-id`.
- Augmented records are explicitly marked and never mixed with official data.
- No postal code is inferred without an explicit source signal.

---

## Disclaimer

Postal codes are operational data managed by Pos Indonesia.

This repository provides a **reference dataset** for engineering and research
purposes only and does not claim to be an official postal authority.

---

## Reproducibility

This dataset is designed to be **fully reproducible and auditable**.

Each release:

- Uses pinned, immutable inputs
- Documents its source composition
- Produces deterministic outputs
