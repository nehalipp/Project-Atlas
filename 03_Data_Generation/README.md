# Project Atlas — Phase 3: Data Generation

Phase 3 creates the synthetic operational data used by Project Atlas.

The datasets are generated with Python, Faker, and Pandas using controlled
relationships, realistic business behavior, and reproducible randomness.

Phase 3 also intentionally introduces controlled data-quality issues so that
Phase 4 can demonstrate data profiling, validation, and remediation.

---

## Purpose

Phase 3 produces:

1. Clean synthetic reference data
2. Clean synthetic business-process data
3. A validated clean baseline
4. Controlled data-quality issues across all 16 datasets

All data is synthetic and exists only for Project Atlas.

---

## Datasets

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

Total: **16 synthetic datasets**

Output location:

```text
data/raw/
````

---

## Data Generation Flow

Phase 3 follows this sequence:

```text
Generate Reference Data
        ↓
Generate Business Data
        ↓
Validate Clean Baseline
        ↓
Inject Controlled Quality Issues
        ↓
Phase 3 Complete
```

The clean baseline is validated before quality issues are introduced. This
ensures that intentionally defective data can be distinguished from accidental
generation errors.

---

## Controlled Quality Injection

The `inject_quality_issues.py` script introduces realistic and controlled
defects across all 16 datasets.

Quality issues include:

* Missing values (`NaN`)
* Hidden missing-value placeholders
* Exact duplicate rows
* Partial duplicates
* Invalid foreign-key references
* Structural inconsistencies
* Incorrect data types
* Mixed date formats
* Leading/trailing whitespace
* Invalid categories
* Negative or impossible numeric values
* Outliers and anomalies
* Business-rule violations
* Referential-integrity issues
* Reconciliation inconsistencies

The purpose is not to make the data unusable. The defects are intentionally
controlled so Phase 4 can identify, measure, validate, and remediate them.

---

## Phase 3 Orchestration

The complete Phase 3 workflow is controlled by:

```text
scripts/generate_all_data.py
```

This is the **primary script for normal Phase 3 execution**.

It automatically runs:

```text
generate_reference_data.py
generate_business_data.py
validate_reference_data.py
validate_business_data.py
inject_quality_issues.py
```

Successful execution produces a concise progress summary and stops
automatically if any stage fails.

---

## Running Phase 3

From the `03_Data_Generation` directory:

```bash
python3 scripts/generate_all_data.py
```

A successful run ends with:

```text
Phase 3 complete.

Output:
data/raw/

Next phase:
Phase 4 — Data Quality

Run:
cd ../04_Data_Quality
```

The underlying scripts do not normally need to be executed manually.

---

## Reproducibility

Data generation uses a controlled project seed so that the synthetic
datasets and injected quality issues can be reproduced consistently.

Run the Phase 3 orchestration script again whenever the complete raw dataset
needs to be regenerated.

---

## Phase Boundary

Phase 3 is responsible for **creating intentionally imperfect synthetic
datasets**.

Phase 4 is responsible for:

* Data profiling
* Data-quality measurement
* Validation
* Business-rule checks
* Referential-integrity checks
* Quality reporting
* Identifying and documenting remediation requirements

Phase 3 does not perform the final data-quality remediation.

---

## Technology

* Python
* Faker
* Pandas
* NumPy where useful

---

## Status

**Phase 3 — Complete**

The 16 synthetic datasets have been generated, the clean baseline has been
validated, and controlled quality issues have been injected.

**Next phase:** Phase 4 — Data Quality

---

> **Note:** All data used in Project Atlas is synthetic and intended for portfolio and demonstration purposes only.
