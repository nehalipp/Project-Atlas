# Project Atlas — Data Quality Specification

## 1. Purpose

This document defines the Data Quality framework for Project Atlas.

Phase 4 transforms the intentionally imperfect source datasets created during Phase 3 into trusted datasets suitable for the downstream ETL, PostgreSQL Data Warehouse, Analytics, Power BI, and Tableau phases.

The Phase 4 process must:

- Profile the source data.
- Measure data-quality issues.
- Validate completeness and uniqueness.
- Validate referential integrity.
- Validate business rules.
- Establish trusted reference dimensions.
- Remediate missing and invalid data.
- Propagate deleted reference identifiers to dependent facts.
- Preserve approved fact grains.
- Revalidate the trusted datasets.
- Produce documented remediation results.

All data remains synthetic.

---

## 2. Phase 4 Position in Project Atlas

The approved Atlas pipeline is:

```text
Raw Operational Data
        ↓
Data Profiling & Quality
        ↓
ETL / ELT
        ↓
PostgreSQL Data Warehouse
        ↓
Reusable SQL Analytics
        ↓
Power BI + Tableau
        ↓
Business Insights & Recommendations
````

Phase 4 is therefore the quality-control boundary between intentionally imperfect source data and trusted data used by downstream processing.

The trusted output must not be treated as warehouse data.

---

## 3. Source Data

Phase 4 consumes the quality-issue datasets generated during Phase 3.

Source location:

```text
03_Data_Generation/data/quality_issues/
```

The source layer contains all 16 Atlas datasets.

### Reference datasets

```text
accounts
customers
suppliers
products
locations
employees
machines
```

### Business datasets

```text
sales
production
maintenance
financial_transactions
budget
energy
emissions
waste
inventory
```

The clean Phase 3 baseline remains available under:

```text
03_Data_Generation/data/raw/
```

The quality-issue datasets are intentionally imperfect and are the primary inputs to Phase 4.

---

## 4. Data Quality Dimensions

Phase 4 evaluates the following dimensions.

### 4.1 Completeness

Checks whether required fields contain missing values.

Examples:

* Missing account identifiers
* Missing customer identifiers
* Missing dates
* Missing product identifiers
* Missing quantities
* Missing financial amounts

Required fields must be populated before trusted data is produced.

---

### 4.2 Uniqueness

Checks whether identifiers and approved unique grains are preserved.

Examples:

* Duplicate entity identifiers
* Duplicate source rows
* Duplicate inventory grain

Duplicates introduced during Phase 3 must be detected and remediated where appropriate.

---

### 4.3 Validity

Checks whether values conform to expected business rules and data types.

Examples:

* Invalid categories
* Negative quantities where not permitted
* Invalid financial values
* Invalid dates
* Invalid revenue calculations

---

### 4.4 Consistency

Checks whether related values agree with each other.

Examples:

* Sales account and customer relationships
* Sales revenue calculations
* Production machine and location relationships
* Production employee and location relationships
* Maintenance machine and location relationships
* Inventory quantity rules

---

### 4.5 Referential Integrity

Checks whether foreign-key-like identifiers reference valid records.

Examples:

```text
Customer → Account
Product → Supplier
Employee → Location
Machine → Location

Sales → Account
Sales → Customer
Sales → Product
Sales → Location

Production → Product
Production → Location
Production → Machine
Production → Employee

Maintenance → Location
Maintenance → Machine
Maintenance → Employee

Inventory → Product
Inventory → Location
```

Invalid references must not remain in trusted data.

---

### 4.6 Business Rules

Business rules validate whether records are logically valid for their domain.

Examples include:

* Sales revenue consistency
* Positive or valid production quantities
* Valid inventory quantities
* Valid financial amounts
* Valid operational relationships
* Valid inventory grain

---

## 5. Approved Fact Grains

Phase 4 must preserve the approved Atlas fact grains.

| Dataset                | Approved Grain                        |
| ---------------------- | ------------------------------------- |
| Sales                  | One row per sales transaction line    |
| Production             | One row per production activity       |
| Maintenance            | One row per maintenance event         |
| Financial Transactions | One row per financial transaction     |
| Budget                 | One row per budget record             |
| Energy                 | One row per energy measurement        |
| Emissions              | One row per emissions record          |
| Waste                  | One row per waste record              |
| Inventory              | One row per Product + Location + Date |

Inventory is a periodic snapshot.

```text
Inventory Grain:
Date + Product + Location
```

Remediation must not introduce duplicate rows at an approved fact grain.

Facts must not be joined directly to other facts at incompatible grains during quality processing.

---

## 6. Phase 4 Workflow

The Phase 4 pipeline is:

```text
Profile
   ↓
Validate Source Data
   ↓
Remediate
   ↓
Validate Trusted Data
```

The complete workflow is orchestrated by:

```text
04_Data_Quality/scripts/run_data_quality.py
```

---

## 7. Step 1 — Data Profiling

Script:

```text
profile_data.py
```

Purpose:

* Inspect all 16 quality-issue datasets.
* Record row counts.
* Inspect columns and data types.
* Measure missing values.
* Measure duplicate rows.
* Produce a profiling summary.

Output:

```text
04_Data_Quality/reports/data_profile_summary.csv
```

The profiling stage is diagnostic and does not modify source data.

---

## 8. Step 2 — Source Data Quality Validation

Script:

```text
validate_source_data.py
```

Purpose:

* Measure completeness issues.
* Measure duplicate records.
* Check referential integrity.
* Check business rules.
* Quantify the intentionally introduced quality issues.

The expected result is that source data contains controlled quality issues.

This is not a failure of Phase 4.

It demonstrates that the source layer requires data-quality remediation before downstream use.

Output:

```text
04_Data_Quality/reports/source_quality_report.csv
```

---

## 9. Step 3 — Data Remediation

Script:

```text
remediate_data.py
```

The remediation process creates trusted datasets from the quality-issue source data.

Trusted output:

```text
04_Data_Quality/data/trusted/
```

### 9.1 Trusted Reference Dimensions First

Reference dimensions are established before dependent business facts.

The remediation order is:

```text
Accounts
Customers
Suppliers
Products
Locations
Employees
Machines
        ↓
Business Facts
```

This establishes the trusted identifier sets used by dependent datasets.

---

### 9.2 Missing-Value Remediation

Missing values are handled using dataset-specific rules.

The objective is not to blindly fill every missing value with a generic placeholder.

Remediation should preserve business meaning and should prefer:

1. Deterministic reconstruction where possible.
2. Valid values derived from related records where appropriate.
3. Removal of records that cannot be trusted safely.

No unresolved missing values are permitted in the trusted output.

---

### 9.3 Reference-Dependency Remediation

When a corrupted or invalid reference record cannot be trusted and is removed from a reference dimension, dependent records referencing that identifier must also be removed or otherwise remediated.

The dependency hierarchy is:

```text
Account
   ↓
Customer
   ↓
Sales

Supplier
   ↓
Product
   ↓
Sales / Production / Inventory

Location
   ├── Employee
   ├── Machine
   ├── Sales
   ├── Production
   ├── Maintenance
   ├── Financial Transactions
   ├── Budget
   ├── Energy
   ├── Emissions
   ├── Waste
   └── Inventory
```

Trusted facts must never contain references to identifiers absent from the trusted reference dimensions.

---

### 9.4 Account → Customer → Sales Consistency

The trusted relationship must satisfy:

```text
Customer.account_id
    → trusted Accounts.account_id
```

Sales must satisfy:

```text
Sales.customer_id
    → trusted Customers.customer_id
```

and:

```text
Sales.account_id
    =
trusted Customer.account_id
```

Any remaining inconsistency must cause trusted validation to fail.

---

### 9.5 Product → Supplier Dependency

Every trusted product must reference a trusted supplier.

```text
Product.supplier_id
    → Supplier.supplier_id
```

Sales, production, and inventory records referencing removed products must be removed or otherwise remediated.

---

### 9.6 Location → Employee / Machine Dependencies

Employees and machines must reference trusted locations.

```text
Employee.location_id
    → Location.location_id

Machine.location_id
    → Location.location_id
```

Business records referencing removed employees, machines, or locations must be reconciled against the trusted dimensions.

---

### 9.7 Business Fact Remediation

Business datasets are remediated only after the trusted reference dimensions have been established.

The process includes:

* Removing invalid references.
* Removing unresolved missing-key records.
* Correcting deterministic business-rule violations where safely possible.
* Removing records that cannot be trusted.
* Preserving valid records.
* Preserving approved fact grain.

Valid outliers are retained.

---

## 10. Outlier Policy

Outliers are not automatically considered invalid.

A statistically unusual value may represent a legitimate business event.

Therefore:

```text
Valid Outlier
      ↓
Retain
      ↓
Investigate in later analysis
```

Only values that violate explicit business rules or cannot be trusted are remediated.

The current Phase 4 design intentionally retains valid outliers for investigation.

---

## 11. Remediation Principles

The remediation process follows these principles:

### Principle 1 — Do not fabricate business facts

The process must not invent customers, products, transactions, revenue, production, or other business activity.

### Principle 2 — Prefer deterministic remediation

If a value can be safely derived from existing trusted relationships, deterministic remediation is preferred.

### Principle 3 — Remove records that cannot be trusted

When a record contains an unresolved critical problem, removal is preferable to silently fabricating a value.

### Principle 4 — Preserve valid information

Valid records should remain in the trusted dataset.

### Principle 5 — Preserve fact grain

Remediation must not create duplicate fact records.

### Principle 6 — Maintain referential integrity

Every trusted foreign-key-like identifier must reference an existing trusted dimension record.

### Principle 7 — Keep valid outliers

Valid extreme observations are retained for later investigation.

---

## 12. Step 4 — Trusted Data Validation

Script:

```text
validate_trusted_data.py
```

This validator is intentionally strict.

The trusted-data quality gate checks:

* Required fields are complete.
* Required identifiers are unique.
* Referential integrity is valid.
* Account/customer/sales relationships are consistent.
* Product/supplier dependencies are valid.
* Location/employee/machine dependencies are valid.
* Business facts reference trusted dimensions.
* Business rules are satisfied.
* Approved fact grains are preserved.
* Inventory grain is unique.
* No unresolved critical quality issues remain.

The expected successful result is:

```text
Validation status : PASSED
```

If any critical rule fails, the trusted data is not ready for downstream ETL.

---

## 13. Trusted Data Output

Trusted datasets are written to:

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

These files represent trusted source data.

They are not yet PostgreSQL warehouse tables.

---

## 14. Remediation Reporting

The remediation process produces:

```text
04_Data_Quality/reports/remediation_summary.csv
```

The report documents:

* Dataset
* Source record count
* Trusted record count
* Records removed

The purpose is to provide traceability between the intentionally imperfect source layer and the trusted output.

The total number of records removed is expected to vary if the generation configuration or quality-injection logic changes.

---

## 15. Current Phase 4 Results

The current validated Phase 4 run produced:

```text
Source records:
1,972,782

Trusted records:
1,842,059

Records removed:
130,723
```

All 16 datasets passed the strict trusted-data validation gate.

The trusted data currently contains:

```text
Accounts                    1,000
Customers                  49,509
Suppliers                   1,000
Products                    4,951
Locations                    100
Employees                  4,913
Machines                   1,959
Sales                    466,046
Production               181,438
Maintenance               46,180
Financial Transactions   293,285
Budget                    19,445
Energy                    97,747
Emissions                 97,337
Waste                     97,982
Inventory                479,167
```

These counts describe the current synthetic run and are not business-performance claims.

---

## 16. Phase 4 Scripts

The Phase 4 implementation contains:

```text
profile_data.py
validate_source_data.py
remediate_data.py
validate_trusted_data.py
run_data_quality.py
```

### `profile_data.py`

Profiles the intentionally imperfect source datasets.

### `validate_source_data.py`

Measures and reports source-data quality issues.

### `remediate_data.py`

Creates trusted datasets using the approved remediation rules.

### `validate_trusted_data.py`

Performs the strict trusted-data quality gate.

### `run_data_quality.py`

Runs the complete Phase 4 workflow in the correct order.

---

## 17. Phase Boundary

Phase 4 is responsible for:

```text
Source Data
    ↓
Profile
    ↓
Measure Quality
    ↓
Remediate
    ↓
Validate
    ↓
Trusted Data
```

Phase 4 does not:

* Build PostgreSQL warehouse tables.
* Perform final ETL/ELT.
* Create analytics models.
* Create Power BI dashboards.
* Create Tableau dashboards.
* Calculate final business insights.

Those activities belong to later Atlas phases.

---

## 18. Technology

Phase 4 uses:

* Python
* Pandas
* NumPy where useful
* CSV source files
* Markdown documentation

No additional orchestration or data-platform technology is required.

---

## 19. Status

> **Phase 4 — Data Quality**
>
> **Specification:** Locked
>
> **Source profiling:** Complete
>
> **Source quality validation:** Complete
>
> **Data remediation:** Complete
>
> **Trusted data validation:** PASSED
>
> **Trusted dataset:** Ready for downstream ETL
>
> **Next phase:** Phase 5 — ETL

---

> **Note:** All data used in Project Atlas is synthetic and intended for portfolio and demonstration purposes only.