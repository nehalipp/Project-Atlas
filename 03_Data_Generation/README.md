# Project Atlas — Phase 3: Data Generation

Phase 3 creates the synthetic operational source data used by Project Atlas.

The data is generated with Python, Faker, Pandas, and NumPy using the
approved Phase 2 Data Model, controlled relationships, realistic business
behavior, and reproducible randomness.

All data is synthetic and intended for portfolio and demonstration purposes
only.

---

## Purpose

Phase 3 produces:

1. Clean synthetic reference data
2. Clean synthetic business-process data
3. A validated clean baseline
4. Intentionally imperfect copies for Phase 4 Data Quality

The clean baseline is preserved separately from the quality-issue datasets.

---

## Datasets

Phase 3 generates all 16 approved Atlas datasets.

### Reference Data

| Dataset | Records |
|---|---:|
| accounts.csv | 1,000 |
| customers.csv | 50,000 |
| suppliers.csv | 1,000 |
| products.csv | 5,000 |
| locations.csv | 100 |
| employees.csv | 5,000 |
| machines.csv | 2,000 |

### Business Data

| Dataset | Records |
|---|---:|
| sales.csv | 500,000 |
| production.csv | 200,000 |
| maintenance.csv | 50,000 |
| financial_transactions.csv | 300,000 |
| budget.csv | 20,000 |
| energy.csv | 100,000 |
| emissions.csv | 100,000 |
| waste.csv | 100,000 |
| inventory.csv | 500,000 |

Clean baseline:

```text
16 datasets
1,934,100 records
````

---

## Data Generation Flow

The complete Phase 3 workflow is:

```text
Reference Generation
        ↓
Reference Validation
        ↓
Business Generation
        ↓
Business Validation
        ↓
Controlled Quality Injection
        ↓
Phase 3 Complete
```

The clean baseline is validated before any quality issues are introduced.

---

## Scripts

```text
scripts/
├── generate_reference_data.py
├── validate_reference_data.py
├── generate_business_data.py
├── validate_business_data.py
├── inject_quality_issues.py
└── generate_all_data.py
```

### Recommended execution

Run the complete pipeline from the repository root:

```bash
python3 03_Data_Generation/scripts/generate_all_data.py
```

The orchestration script runs all five Phase 3 stages in the correct order
and stops if a required stage fails.

Individual scripts can also be run when troubleshooting or validating a
specific stage.

---

## Output

Phase 3 creates two separate data states:

```text
03_Data_Generation/data/
├── raw/
└── quality_issues/
```

### `data/raw/`

Contains the clean, validated synthetic baseline.

This data is used as the trusted source baseline for downstream development
and reconciliation.

### `data/quality_issues/`

Contains intentionally imperfect copies created by
`inject_quality_issues.py`.

These datasets are the primary input for Phase 4 — Data Quality.

The quality-issue datasets do not replace the clean baseline.

---

## Controlled Quality Issues

The quality-injection process introduces deliberate defects such as:

* Missing values
* Duplicate records
* Invalid references
* Invalid categories
* Invalid numeric values
* Outliers
* Referential-integrity issues
* Business-rule violations
* Structural and consistency issues

The purpose is to provide realistic data-quality challenges for Phase 4.

The defects are controlled and reproducible rather than uncontrolled random
corruption.

---

## Validation

The clean baseline is validated before quality injection.

Reference validation covers:

* Record counts
* Relationship integrity
* Product pricing
* Lifecycle dates

Business validation covers:

* Record counts
* Referential integrity
* Customer/account consistency
* Revenue calculations
* Machine/location consistency
* Employee/location consistency
* Inventory grain

A successful Phase 3 run therefore establishes both:

```text
Validated Clean Baseline
+
Controlled Imperfect Dataset
```

---

## Reproducibility

Generation is controlled through:

```text
03_Data_Generation/config/generation_config.py
```

The project uses:

```text
Random Seed: 42
Date Range: 2019-01-01 to 2025-12-31
```

Running the pipeline with the same configuration and generator version
reproduces the clean baseline.

---

## Technology

* Python
* Faker
* Pandas
* NumPy
* CSV

No additional orchestration framework or data platform is required.

---

## Phase Boundary

Phase 3 is responsible for:

* Synthetic data generation
* Relationship-aware generation
* Clean baseline validation
* Controlled quality-issue injection

Phase 4 is responsible for:

* Data profiling
* Data-quality measurement
* Completeness
* Uniqueness
* Validity
* Consistency
* Referential integrity
* Business-rule validation
* Quality reporting
* Remediation

Phase 3 does not perform final data-quality remediation.

---

## Status

**Phase 3 — Complete**

The 16 synthetic datasets have been generated, the clean baseline has been
validated, and controlled quality issues have been injected.

**Next phase:** Phase 4 — Data Quality

---

> **Note:** All data used in Project Atlas is synthetic and intended for
> portfolio and demonstration purposes only.