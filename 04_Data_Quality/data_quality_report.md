# Project Atlas — Data Quality Report

## 1. Overview

Phase 4 validates and remediates the synthetic operational data generated in Phase 3.

The objective is to identify data-quality issues before the data enters the PostgreSQL warehouse and downstream analytics.

The validation covers:

- Completeness
- Uniqueness
- Validity
- Consistency
- Referential integrity
- Business-rule compliance

The process converts imperfect raw data into trusted datasets for the ETL and warehouse phases.

---

## 2. Data Quality Process

The Phase 4 process follows:

Raw Data
↓
Profiling
↓
Validation
↓
Remediation
↓
Trusted Data Validation
↓
Trusted Datasets

The remediation rules are implemented in `data_quality.py` and are based on the Atlas data dictionary, approved business rules, and relationships defined in the data model.

---

## 3. Quality Checks

### Completeness

Required fields were checked for missing values.

Blank text values in required fields were converted to NULL before validation. Required fields were then remediated using the defined business rule, such as replacing missing categorical/text values with `Unknown`.

The following fields are intentionally nullable according to the Atlas data dictionary:

- `dim_product.subcategory`
- `fact_waste.disposal_method`

NULL values in these fields are therefore treated as expected rather than as quality failures.

### Uniqueness

Primary keys and business identifiers were checked for duplicate values.

Controlled duplicate records were introduced during data generation and removed during remediation.

### Validity

Categorical values, dates, numeric fields, identifiers, and required text fields were validated against the approved data definitions and business rules.

Invalid categorical values were replaced with `Unknown` where an appropriate replacement was defined.

### Consistency

Business calculations and relationships were checked for internal consistency.

Examples include:

- Sales revenue reconciliation
- Inventory closing quantity reconciliation
- Production quantity relationships
- Financial transaction rules

Where a deterministic calculation could be corrected safely, the trusted value was recalculated.

### Referential Integrity

Foreign-key relationships between dimensions and facts were validated.

Records containing invalid foreign-key references were removed so that trusted datasets contain only valid relationships.

### Business Rules

Operational business rules were applied to quantities and measures.

Examples include:

- Non-negative quantities
- Production defect quantity cannot exceed produced quantity
- Revenue must reconcile with transaction values
- Inventory closing quantity must reconcile with inventory movements

Extreme production and financial transaction values were retained for investigation rather than automatically removed.

---

## 4. Main Issues Detected and Remediated

The generated dataset contained controlled quality issues across several domains.

| Issue | Remediation |
|---|---|
| Leading/trailing whitespace | Trimmed text values |
| Blank required text values | Converted blank values to NULL and filled with `Unknown` |
| Duplicate primary keys | Removed duplicate records |
| Invalid categorical values | Replaced with `Unknown` |
| Negative quantities | Removed invalid records |
| Invalid foreign keys | Removed records with invalid references |
| Revenue reconciliation failures | Recalculated revenue |
| Inventory reconciliation failures | Recalculated closing quantity |
| Defect quantity greater than produced quantity | Capped defect quantity at produced quantity |
| Production outliers | Retained for investigation |
| Financial transaction outliers | Retained for investigation |

Nullable fields were not incorrectly converted into required fields. In particular, NULL values in `dim_product.subcategory` remain valid because the field is explicitly defined as nullable in the Atlas data dictionary.

---

## 5. Trusted Dataset Results

The final trusted datasets contain:

| Dataset | Raw Rows | Trusted Rows | Rows Removed | Retained |
|---|---:|---:|---:|---:|
| dim_account | 1,000 | 1,000 | 0 | 100.0% |
| dim_customer | 50,000 | 50,000 | 0 | 100.0% |
| dim_date | 2,557 | 2,557 | 0 | 100.0% |
| dim_employee | 5,000 | 5,000 | 0 | 100.0% |
| dim_location | 100 | 100 | 0 | 100.0% |
| dim_machine | 2,000 | 2,000 | 0 | 100.0% |
| dim_product | 5,000 | 5,000 | 0 | 100.0% |
| dim_supplier | 1,000 | 1,000 | 0 | 100.0% |
| fact_budget | 20,000 | 20,000 | 0 | 100.0% |
| fact_emissions | 100,000 | 100,000 | 0 | 100.0% |
| fact_energy | 100,000 | 99,800 | 200 | 99.8% |
| fact_financial_transaction | 300,300 | 300,000 | 300 | 99.9% |
| fact_inventory | 500,000 | 499,000 | 1,000 | 99.8% |
| fact_maintenance | 50,000 | 49,950 | 50 | 99.9% |
| fact_production | 200,200 | 200,000 | 200 | 99.9% |
| fact_sales | 500,500 | 499,002 | 1,498 | 99.7% |
| fact_waste | 100,000 | 99,900 | 100 | 99.9% |

---

## 6. Final Validation

The trusted datasets passed the final validation.

Results:

- All expected datasets present
- Unexpected NULL values: 0
- Duplicate rows: 0
- Invalid foreign-key references: 0
- Required fields validated
- Business rules validated
- Expected nullable fields preserved
- Trusted datasets successfully generated

---

## 7. Outcome

Phase 4 produces trusted datasets that can be consumed by the ETL process.

The trusted data is the controlled input for:

```text
Phase 4 Data Quality
        ↓
Phase 5 ETL
        ↓
Phase 6 PostgreSQL Warehouse
        ↓
Phase 7 Analytics
````

All quality decisions are implemented through reusable remediation rules so that the process can also handle similar data-quality issues if they occur in future generated or source data.
