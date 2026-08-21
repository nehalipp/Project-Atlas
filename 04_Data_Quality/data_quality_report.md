# Project Atlas — Phase 4 Data Quality

## Purpose

Phase 4 evaluates the quality of the synthetic raw datasets generated in Phase 3 and creates trusted datasets for the downstream ETL process.

The assessment focuses on:

- Completeness
- Uniqueness
- Validity
- Consistency
- Referential integrity
- Business rules

The process uses simple Python and Pandas with deterministic remediation rules.

---

## Quality Approach

The raw datasets were intentionally created with a small number of controlled quality issues.

The Phase 4 process:

1. Loads the raw datasets.
2. Applies data-quality rules.
3. Remediates issues where a reliable correction is possible.
4. Removes records that cannot be safely used.
5. Retains unusual but potentially valid outliers for investigation.
6. Validates the trusted datasets.
7. Saves the trusted datasets and quality summary.

The trusted datasets are the input for Phase 5 ETL.

---

## Main Quality Issues

### Completeness

Detected missing values in:

- Customer country
- Product subcategory
- Supplier category
- Maintenance type

**Remediation:** Missing categorical values were replaced with `Unknown`.

---

### Whitespace

Leading and trailing whitespace was intentionally introduced into selected text fields.

Affected dimensions included:

- Account name
- Customer name
- Employee name
- Machine name
- Product name
- Supplier name

**Remediation:** Leading and trailing whitespace was removed.

---

### Uniqueness

Duplicate business records were introduced into:

- Sales
- Production
- Financial transactions

**Remediation:** Duplicate records were removed using the appropriate business identifier.

---

### Referential Integrity

Invalid foreign-key references were introduced into:

- Sales → Customer
- Inventory → Product
- Energy → Machine
- Maintenance → Employee

**Remediation:** Records containing invalid references were removed.

---

### Validity

Invalid categorical values were introduced into:

- Customer segment
- Location type
- Machine status
- Supplier category

Negative numeric values were introduced into:

- Sales quantity
- Inventory issued quantity
- Energy consumption
- Waste quantity

**Remediation:**

- Invalid categorical values were replaced with `Unknown`.
- Records containing negative operational quantities were removed.

---

### Consistency

Two reconciliation rules were applied.

#### Sales Revenue

Revenue was recalculated when it did not agree with the underlying sales quantity, price and discount.

#### Inventory

Closing inventory was recalculated using:

`Opening Quantity + Received Quantity - Issued Quantity`

---

### Production Business Rule

Production defects cannot exceed production output.

Rule:

`Defect Quantity <= Produced Quantity`

Records violating this rule were corrected by capping defect quantity at produced quantity.

---

### Outliers

Some unusually large production quantities and financial transaction amounts were intentionally retained.

These records were not automatically removed because an outlier is not necessarily an error.

**Action:** Retain for investigation.

This distinction prevents potentially valid business events from being removed simply because they are unusual.

---

## Trusted Data Result

| Dataset | Raw Rows | Trusted Rows | Rows Removed | Retained % |
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

## Quality Summary

The majority of the synthetic data was retained after remediation.

The largest reduction occurred in `fact_sales`, where duplicate records, invalid customer references and negative quantities were removed.

The quality process also corrected data that could be safely reconciled rather than unnecessarily deleting it.

Outliers were retained separately for investigation because unusual values require business review rather than automatic deletion.

Detailed issue-level results are available in:

`quality_summary.xlsx`