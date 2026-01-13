# Build Specification – postal-code-id

This document defines how releases of the **postal-code-id** dataset
are produced in a deterministic, auditable, and reproducible manner.

This repository distributes **dataset releases**, not source code.
Any implementation (scripts, tools, pipelines) MUST conform to the rules
defined in this document.

---

## Purpose

- Ensure dataset releases are reproducible
- Make data lineage explicit and auditable
- Separate **methodology** from **distribution**
- Clearly distinguish authoritative references from augmentation signals

---

## Release Types

postal-code-id produces **two distinct release types**, each with
explicitly defined inputs and guarantees.

### 1️⃣ Baseline Release (Open Data Jawa Barat)

Characteristics:

- Coverage: < 100%
- Source of postal codes: Open Data Jawa Barat (2023)
- Status values:
  - `OFFICIAL`
  - `UNASSIGNED`

Purpose:

- Provide a conservative, publishable baseline
- Avoid inference or augmentation
- Preserve original data semantics

---

### 2️⃣ Derived Full-Coverage Release (region-id + Pos Indonesia)

Characteristics:

- Coverage: **100% of region-id villages**
- Ground truth: `region-id`
- Postal code signal: Pos Indonesia ingestion output
- Status values:
  - `OFFICIAL`
  - `AUGMENTED`

Purpose:

- Provide a complete, practical reference dataset
- Preserve transparency by explicitly labeling augmentation
- Never replace authoritative sources

---

## Input Sources

### 1. region-id (Administrative Reference)

- Repository: https://github.com/lokabisa-oss/region-id
- Release: **v1.0.1** (pinned)
- Artifact:
  - `regions_id.csv` (GitHub Release asset)

Role:

- **Authoritative source** for administrative data:
  - `province_code`, `province_name`
  - `regency_code`, `regency_name`, `regency_type`
  - `district_code`, `district_name`
  - `village_code`, `village_name`, `village_type`
- Defines the **complete and fixed set of villages**
- Sole reference for:
  - coverage calculation
  - village identifiers
  - village names and types

Constraints:

- Administrative data MUST NOT be sourced from any other repository,
  API, or dataset.
- Repository source trees or branches MUST NOT be used.
- Only the pinned release artifact is allowed.

---

### 2. Open Data Jawa Barat – Postal Code Dataset (Baseline)

- Repository: https://github.com/lokabisa-oss/id-documents
- Path: `opendata-jabar/postal-code/2023`
- Reference: pinned commit or tag
- Integrity: verified via `SHA256SUMS`

Role:

- Primary baseline for **OFFICIAL** postal code mappings
- Non-authoritative but redistributable open data
- Used in both Baseline and Derived releases

---

### 3. Pos Indonesia Public Postal Lookup (Ingestion Signal)

- Access method: public web lookup
- Consumed artifact:
  - JSONL ingestion output (e.g. `village_postal_codes.jsonl`)
- Data used:
  - postal code only
- Redistribution: **NOT allowed** (raw responses)

Role:

- Signal-only source for **AUGMENTED** mappings
- Used exclusively to fill missing postal codes
- Never treated as authoritative
- Never used as an administrative reference

Important constraints:

- Pos Indonesia data MUST be applied **only by `village_code`**
- No name-based, district-based, or city-based inference is allowed
- Administrative attributes MUST always come from `regions_id.csv`

Reproducibility note:

- Ingestion results may change over time
- Derived releases MUST explicitly label augmentation

---

## Build Rules

### 1. Coverage Rule (Global)

- Exactly **one output record** MUST exist for every village in `region-id`
- Output coverage MUST be 100% of region-id villages

---

### 2. OFFICIAL Mapping Rule

A village is classified as `OFFICIAL` if:

- A postal code exists in Open Data Jawa Barat
- The village exists in `regions_id.csv`

Output constraints:

- `status = OFFICIAL`
- `source = OPENDATA_JABAR`
- `confidence = 0.7`
- `year = 2023`
- Administrative fields MUST come from `regions_id.csv`

---

### 3. AUGMENTED Mapping Rule (Derived Release Only)

A village is classified as `AUGMENTED` if:

- It does NOT have an OFFICIAL mapping
- A postal code exists in the Pos Indonesia ingestion output
  for the same `village_code`

Output constraints:

- `status = AUGMENTED`
- `source = POSINDONESIA_SCRAPE`
- `confidence = 0.3 – 0.6`
- `year = build year`
- Administrative fields MUST come from `regions_id.csv`

Notes:

- AUGMENTED mappings are **non-authoritative**
- AUGMENTED mappings MUST NOT override OFFICIAL mappings

---

### 4. UNASSIGNED Mapping Rule (Baseline Release Only)

A village is classified as `UNASSIGNED` if:

- No OFFICIAL postal code is available

Output constraints:

- `postal_code = null`
- `status = UNASSIGNED`
- `source = NONE`
- `confidence = 0.0`
- `year = build year`
- Administrative fields MUST come from `regions_id.csv`

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

- All input references MUST be pinned
- Output records MUST be sorted by `village_code` (ascending)
- No random or non-deterministic operations are allowed
- Confidence values MUST follow defined ranges
- Coverage calculations MUST be based exclusively on
  `region-id` release v1.0.0
- Administrative data MUST be consumed exclusively from
  `regions_id.csv`

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
- Perform probabilistic or ML-based inference

---

## Auditability

A dataset release is considered valid if:

- All villages in `region-id` are represented
- All records conform to the schema
- All mappings are explicitly labeled
- All sources and rules are traceable to this document
