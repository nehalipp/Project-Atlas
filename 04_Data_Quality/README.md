# Project Atlas — Phase 4: Data Quality

Phase 4 converts the intentionally imperfect synthetic source data created in Phase 3 into trusted datasets for downstream ETL and the PostgreSQL data warehouse.

The phase demonstrates a practical data-quality workflow:

```text
Profile
   ↓
Validate Source
   ↓
Remediate
   ↓
Validate Trusted
   ↓
Trusted Data
````

All data is synthetic and intended only for portfolio and demonstration purposes.

---

## Purpose

Phase 4 demonstrates how an analytics/data engineering workflow handles imperfect operational data before it reaches a warehouse.

The phase covers:

* Data profiling
* Completeness assessment
* Duplicate detection
* Referential-integrity validation
* Business-rule validation
* Data remediation
* Dependency-aware remediation
* Fact-grain preservation
* Trusted-data validation
* Remediation reporting

The objective is to produce a trusted source layer without fabricating business facts.

---

## Input

Phase 4 consumes the intentionally imperfect datasets produced during Phase 3.

Source:

```text
03_Data_Generation/data/quality_issues/
```

There are 16 datasets:

### Reference Data

```text
accounts.csv
customers.csv
suppliers.csv
products.csv
locations.csv
employees.csv
machines.csv
```

### Business Data

```text
sales.csv
production.csv
maintenance.csv
financial_transactions.csv
budget.csv
energy.csv
emissions.csv
waste.csv
inventory.csv
```

---

## Pipeline

The complete Phase 4 pipeline is controlled by:

```text
scripts/run_data_quality.py
```

It executes:

```text
1. profile_data.py
2. validate_source_data.py
3. remediate_data.py
4. validate_trusted_data.py
```

The pipeline stops if a required stage fails.

---

## Step 1 — Profiling

Script:

```text
scripts/profile_data.py
```

The profiling stage inspects all 16 datasets and reports:

* Record counts
* Columns
* Data types
* Missing values
* Duplicate rows

Output:

```text
reports/data_profile_summary.csv
```

The profiling stage does not modify the source data.

---

## Step 2 — Source Validation

Script:

```text
scripts/validate_source_data.py
```

The source validator checks:

* Completeness
* Uniqueness
* Referential integrity
* Business rules
* Account/customer consistency
* Product/supplier relationships
* Location dependencies
* Fact-level rules

The expected result is that quality issues are detected because the Phase 3 source data was intentionally corrupted.

This is an expected outcome, not a pipeline failure.

Output:

```text
reports/source_quality_report.csv
```

---

## Step 3 — Remediation

Script:

```text
scripts/remediate_data.py
```

The remediation process establishes trusted reference dimensions first.

The dependency order is:

```text
Accounts
   ↓
Customers
   ↓
Sales

Suppliers
   ↓
Products
   ↓
Sales / Production / Inventory

Locations
   ├── Employees
   ├── Machines
   └── Operational Facts
```

Reference identifiers removed during remediation are not allowed to remain in dependent business facts.

The process:

* Resolves missing values using dataset-specific rules.
* Removes records with unresolved critical problems.
* Removes invalid references.
* Propagates deleted reference identifiers to dependent datasets.
* Rechecks account/customer/sales consistency.
* Rechecks product/supplier dependencies.
* Rechecks location/employee/machine dependencies.
* Preserves approved fact grains.
* Retains valid outliers for investigation.

Trusted output:

```text
data/trusted/
```

Remediation report:

```text
reports/remediation_summary.csv
```

---

## Outlier Policy

Not every extreme value is an error.

Valid outliers are intentionally retained.

For example, an unusually large operational measurement may represent a legitimate business event.

Therefore:

```text
Valid Outlier
      ↓
Retain
      ↓
Investigate Later
```

Only values that violate explicit business rules or cannot be trusted are remediated.

---

## Step 4 — Trusted Validation

Script:

```text
scripts/validate_trusted_data.py
```

This validator is intentionally strict.

The trusted-data quality gate checks:

* Required fields are complete.
* Required identifiers are valid.
* Duplicate records are not present where prohibited.
* Referential integrity is valid.
* Account/customer/sales relationships are consistent.
* Product/supplier relationships are valid.
* Location/employee/machine relationships are valid.
* Business facts reference trusted dimensions.
* Business rules are satisfied.
* Approved fact grains are preserved.
* Inventory grain is unique.

The trusted dataset is accepted only when all critical checks pass.

Expected result:

```text
Validation status : PASSED
```

---

## Trusted Output

The trusted datasets are stored in:

```text
04_Data_Quality/data/trusted/
```

Expected files:

```text
accounts.csv
customers.csv
suppliers.csv
products.csv
locations.csv
employees.csv
machines.csv
sales.csv
production.csv
maintenance.csv
financial_transactions.csv
budget.csv
energy.csv
emissions.csv
waste.csv
inventory.csv
```

These datasets are trusted source data.

They are not yet PostgreSQL warehouse tables.

---

## Current Validated Results

The current Phase 4 run produced:

```text
Source records:
1,972,782

Trusted records:
1,842,059

Records removed:
130,723
```

The strict trusted-data validation completed successfully.

Current trusted dataset counts:

| Dataset                    | Trusted Records |
| -------------------------- | --------------: |
| accounts.csv               |           1,000 |
| customers.csv              |          49,509 |
| suppliers.csv              |           1,000 |
| products.csv               |           4,951 |
| locations.csv              |             100 |
| employees.csv              |           4,913 |
| machines.csv               |           1,959 |
| sales.csv                  |         466,046 |
| production.csv             |         181,438 |
| maintenance.csv            |          46,180 |
| financial_transactions.csv |         293,285 |
| budget.csv                 |          19,445 |
| energy.csv                 |          97,747 |
| emissions.csv              |          97,337 |
| waste.csv                  |          97,982 |
| inventory.csv              |         479,167 |

These are synthetic dataset counts from the current reproducible run. They do not represent real-world business results.

---

## Reports

Phase 4 produces the following reports:

```text
reports/
├── data_profile_summary.csv
├── source_quality_report.csv
└── remediation_summary.csv
```

### `data_profile_summary.csv`

Contains profiling results for the quality-issue datasets.

### `source_quality_report.csv`

Documents quality issues detected in the intentionally imperfect source data.

### `remediation_summary.csv`

Documents source records, trusted records, and records removed during remediation.

---

## Running Phase 4

From the Project Atlas root directory:

```bash
python3 04_Data_Quality/scripts/run_data_quality.py
```

A successful run ends with a trusted-data validation status of:

```text
PASSED
```

Individual scripts can also be executed for development and troubleshooting:

```bash
python3 04_Data_Quality/scripts/profile_data.py

python3 04_Data_Quality/scripts/validate_source_data.py

python3 04_Data_Quality/scripts/remediate_data.py

python3 04_Data_Quality/scripts/validate_trusted_data.py
```

Normal execution should use:

```bash
python3 04_Data_Quality/scripts/run_data_quality.py
```

---

## Technology

Phase 4 uses:

* Python
* Pandas
* NumPy where useful
* CSV
* Markdown

No additional data-platform or orchestration technology is required.

---

## Phase Boundary

Phase 4 ends when trusted source data passes the strict quality gate.

Phase 4 does not build:

* PostgreSQL warehouse tables
* ETL/ELT transformations
* SQL analytics
* Power BI dashboards
* Tableau dashboards
* Business insights

Those activities belong to subsequent Atlas phases.

The resulting trusted datasets become the input to the ETL phase.

---

## Status

**Phase 4 — Complete**

The 16 synthetic datasets have been:

* Profiled
* Assessed for data quality
* Remediated
* Validated
* Passed through the trusted-data quality gate

Trusted data is ready for:

**Phase 5 — ETL**

---

> **Note:** All data used in Project Atlas is synthetic and intended for portfolio and demonstration purposes only.