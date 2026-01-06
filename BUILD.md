# Build Specification – postal-code-id

This document defines how releases of the **postal-code-id** dataset
are produced in a deterministic and reproducible manner.

This repository distributes **dataset releases**, not source code.
Any implementation (scripts, tools) must conform to the rules
defined in this document.

---

## Purpose

- Ensure dataset releases are reproducible
- Make data lineage explicit and auditable
- Separate **methodology** from **distribution**

---

## Input Sources

### 1. Open Data Jawa Barat – Postal Code Dataset (Baseline)

- Repository: https://github.com/lokabisa-oss/id-documents
- Path: `opendata-jabar/postal-code/2023`
- Reference: `opendata-jabar-postal-code-2023`
- Integrity: Verified via `SHA256SUMS`

Role:

- Primary baseline for **OFFICIAL** postal code mappings
- Non-authoritative but publishable open data

---

### 2. region-id (Administrative Reference)

- Repository: https://github.com/lokabisa-oss/region-id
- Reference: pinned release (e.g. `v2025Q1`)

Role:

- Authoritative source for:
  - village identifiers (`village_code`)
  - village names
  - village types (`village`, `urban_village`)
- Defines the full set of villages that must be represented

---

### 3. Pos Indonesia Public Postal Lookup (Augmentation Signal)

- Access method: public web lookup
- Data used: postal code only
- Redistribution: **not allowed**

Role:

- Signal-only source for **AUGMENTED** mappings
- Used solely to improve coverage completeness
- Never treated as authoritative

Reproducibility note:

- Results may change over time
- Augmented mappings must always be explicitly labeled

---

## Build Rules

### 1. Coverage Rule

- Exactly **one output record** MUST exist for every village in `region-id`
- Output coverage MUST be 100% of region-id villages

---

### 2. region-id (Administrative Reference)

- Repository: https://github.com/lokabisa-oss/region-id
- Release: v1.0.0
- URL: https://github.com/lokabisa-oss/region-id/releases/tag/v1.0.0

Artifacts used:

- `regions_id.csv` (GitHub Release asset)

Role:

- Authoritative source for administrative identifiers and attributes
- Provides a flattened snapshot of:
  - province
  - regency
  - district
  - village
- Defines the complete and fixed set of villages used for:
  - coverage calculation
  - village identifiers (`village_code`)
  - village names
  - village types (`village`, `urban_village`)

---

### 3. AUGMENTED Mapping Rule

A village is classified as `AUGMENTED` if:

- It does not have an OFFICIAL mapping
- A postal code is found via Pos Indonesia lookup

Output constraints:

- `status = AUGMENTED`
- `source = POSINDONESIA_SCRAPE`
- `confidence = 0.3 – 0.6`
- `year = build year`
- `village_name` and `village_type` MUST be sourced from `region-id`

Notes:

- Augmented mappings are **non-authoritative**
- Augmented mappings MUST NOT override OFFICIAL mappings

---

### 4. UNASSIGNED Mapping Rule

A village is classified as `UNASSIGNED` if:

- No OFFICIAL or AUGMENTED postal code is available

Output constraints:

- `postal_code = null`
- `status = UNASSIGNED`
- `source = NONE`
- `confidence = 0.0`
- `year = build year`
- `village_name` and `village_type` MUST be sourced from `region-id`

---

## Output Schema

All output records MUST conform to:

- `schema/postal_code.schema.json`

Any record that does not validate against the schema
MUST be rejected.

---

## Output Artifacts

Each release MUST produce:

- `postal_codes.csv`
- `postal_codes.json`
- SHA-256 checksum files for each artifact

---

## Determinism Rules

To ensure reproducibility:

- Input source references MUST be pinned
- Output records MUST be sorted by `village_code` ascending
- No random or non-deterministic operations are allowed
- Confidence values MUST follow defined ranges
- Coverage calculations are based exclusively on
  region-id release v1.0.0 and MUST NOT change
  unless the pinned reference is updated.
- Administrative data MUST be consumed exclusively from the
  `regions_id.csv` release artifact of region-id v1.0.0.
- Repository source trees or branch contents MUST NOT be used
  for administrative references.

---

## Versioning

Dataset releases use time-based versioning:

- `vYYYYQn` (e.g. `v2025Q1`)

Build rules apply identically across versions unless
explicitly revised in this document.

---

## Non-Goals

This build process explicitly does NOT aim to:

- Replace Pos Indonesia as an authoritative source
- Provide real-time postal code resolution
- Infer postal codes without explicit labeling

---

## Auditability

A dataset release is considered valid if:

- All villages in `region-id` are represented
- All records conform to the schema
- All sources and rules used are traceable to this document
