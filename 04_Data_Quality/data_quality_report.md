# Project Atlas — Data Quality Report

## 1. Overview

Phase 4 validates and remediates the synthetic operational data generated in Phase 3.

The objective is to identify data-quality issues before the data enters the PostgreSQL warehouse and downstream analytics.

Validation covers:

* Completeness
* Uniqueness
* Validity
* Consistency
* Referential integrity
* Business rules

The process converts imperfect raw data into trusted datasets for Phase 5 ETL.

---

## 2. Data Quality Process

```text
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
Trusted Data
```

Remediation rules are based on the Atlas data dictionary, approved business rules and relationships defined in the data model.

---

## 3. Quality Checks

### Completeness

Required fields were checked for missing and blank values.

Blank text values were converted to NULL before validation. Where an approved replacement existed, missing categorical/text values were replaced with `Unknown`.

The following fields remain intentionally nullable:

* `dim_product.subcategory`
* `fact_waste.disposal_method`

These NULL values are therefore treated as valid.

### Uniqueness

Primary keys and business identifiers were checked for duplicates.

Controlled duplicate records were removed during remediation.

### Validity

Categorical values, dates, numeric values and identifiers were checked against the approved data definitions and business rules.

Invalid categorical values were replaced with `Unknown` where appropriate.

### Consistency

Business calculations and relationships were checked for internal consistency, including:

* Sales revenue reconciliation
* Inventory closing quantity reconciliation
* Production quantity relationships
* Financial transaction rules

Where a deterministic correction was possible, the trusted value was recalculated.

### Referential Integrity

Foreign-key relationships between dimensions and facts were validated.

Records containing invalid references were removed so that trusted datasets contain valid relationships.

### Business Rules

Operational rules were applied to quantitative measures, including:

* Non-negative quantities
* Defect quantity cannot exceed produced quantity
* Revenue reconciliation
* Inventory closing-balance reconciliation

Extreme production and financial transaction values were retained for investigation rather than automatically removed.

---

## 4. Main Issues and Remediation

| Issue                           | Remediation                                 |
| ------------------------------- | ------------------------------------------- |
| Leading/trailing whitespace     | Trimmed text values                         |
| Blank required text values      | Converted to NULL and filled with `Unknown` |
| Duplicate records               | Removed                                     |
| Invalid categorical values      | Replaced with `Unknown`                     |
| Negative quantities             | Removed                                     |
| Invalid foreign keys            | Removed                                     |
| Revenue inconsistencies         | Recalculated revenue                        |
| Inventory inconsistencies       | Recalculated closing quantity               |
| Defects greater than production | Capped defects at produced quantity         |
| Production outliers             | Retained for investigation                  |
| Financial outliers              | Retained for investigation                  |

Nullable fields were preserved according to the Atlas data dictionary.

---

## 5. Trusted Dataset Results

| Dataset                      | Raw Rows | Trusted Rows | Rows Removed |
| ---------------------------- | -------: | -----------: | -----------: |
| `dim_account`                |    1,000 |        1,000 |            0 |
| `dim_customer`               |   50,000 |       50,000 |            0 |
| `dim_date`                   |    2,557 |        2,557 |            0 |
| `dim_employee`               |    5,000 |        5,000 |            0 |
| `dim_location`               |      100 |          100 |            0 |
| `dim_machine`                |    2,000 |        2,000 |            0 |
| `dim_product`                |    5,000 |        5,000 |            0 |
| `dim_supplier`               |    1,000 |        1,000 |            0 |
| `fact_budget`                |   20,000 |       20,000 |            0 |
| `fact_emissions`             |  100,000 |      100,000 |            0 |
| `fact_energy`                |  100,000 |       99,801 |          199 |
| `fact_financial_transaction` |  300,300 |      300,000 |          300 |
| `fact_inventory`             |  500,000 |      499,001 |          999 |
| `fact_maintenance`           |   50,000 |       49,950 |           50 |
| `fact_production`            |  200,200 |      200,000 |          200 |
| `fact_sales`                 |  500,500 |      499,000 |        1,500 |
| `fact_waste`                 |  100,000 |       99,900 |          100 |

**Total raw rows: 1,937,657**

**Total trusted rows: 1,934,309**

**Total rows removed: 3,348**

---

## 6. Final Validation

The trusted datasets were validated before entering the ETL process.

The current trusted baseline contains:

* All 17 expected datasets
* 1,934,309 trusted records
* No duplicate records in the trusted output
* Validated foreign-key relationships
* Required fields validated
* Approved nullable fields preserved
* Business-rule remediation applied

---

## 7. Outcome

Phase 4 produces the trusted datasets consumed by Phase 5.

```text
Phase 3 Raw Data
       ↓
Phase 4 Data Quality
       ↓
Trusted Data
       ↓
Phase 5 ETL
       ↓
Phase 6 PostgreSQL Warehouse
```

The trusted data provides the controlled foundation for downstream warehouse, analytics and BI development.