# Project Atlas — ETL Specification

## 1. Purpose

Phase 5 establishes the reproducible ETL pipeline between the Phase 4 trusted data layer and the Phase 6 PostgreSQL data warehouse.

The ETL pipeline follows:

```text
Source
  ↓
Extract
  ↓
Raw
  ↓
Staging
  ↓
Transform
  ↓
Validate
  ↓
Warehouse
````

## 2. Phase 5 Source

The authoritative Phase 5 source is:

```text
04_Data_Quality/data/trusted/
```

These datasets are the trusted outputs produced by Phase 4.

Phase 5 does not reintroduce the data-quality issues generated during Phase 3.

## 3. Raw Layer

The Phase 5 Raw layer is:

```text
05_ETL/data/raw/
```

The Raw layer preserves the trusted source datasets as extracted.

No business transformations are performed in the Raw layer.

## 4. Expected Input Datasets

| Dataset                | Expected Rows |
| ---------------------- | ------------: |
| Accounts               |         1,000 |
| Customers              |        49,509 |
| Products               |         4,951 |
| Suppliers              |         1,000 |
| Locations              |           100 |
| Employees              |         4,913 |
| Machines               |         1,959 |
| Sales                  |       466,046 |
| Production             |       181,438 |
| Maintenance            |        46,180 |
| Financial Transactions |       293,285 |
| Budget                 |        19,445 |
| Energy                 |        97,747 |
| Emissions              |        97,337 |
| Waste                  |        97,982 |
| Inventory              |       479,167 |
| **Total**              | **1,842,059** |

## 5. Extraction Controls

The extraction process must:

1. Verify that all 16 expected datasets exist.
2. Verify expected source row counts.
3. Copy trusted datasets into the Raw layer.
4. Verify Raw row counts against source row counts.
5. Calculate SHA-256 checksums.
6. Confirm that source and Raw checksums match.
7. Record dataset-level results.
8. Record the overall extraction status.

## 6. Approved Warehouse Mapping

### Dimensions

```text
dim_date
dim_account
dim_customer
dim_product
dim_supplier
dim_location
dim_employee
dim_machine
```

### Facts

```text
fact_sales
fact_production
fact_maintenance
fact_financial_transaction
fact_budget
fact_energy
fact_emissions
fact_waste
fact_inventory
```

The PostgreSQL warehouse is implemented during Phase 6.

## 7. Fact Grain

ETL transformations must preserve the approved fact grains.

| Fact                       | Grain                                                                  |
| -------------------------- | ---------------------------------------------------------------------- |
| fact_sales                 | One sales transaction                                                  |
| fact_production            | One production event for product, machine, employee, location and date |
| fact_maintenance           | One maintenance event for machine, employee, location and date         |
| fact_financial_transaction | One financial transaction                                              |
| fact_budget                | One budget record for location, category and date                      |
| fact_energy                | One energy measurement for location, energy type and date              |
| fact_emissions             | One emissions measurement for location, source and date                |
| fact_waste                 | One waste record for location, waste type and date                     |
| fact_inventory             | One inventory snapshot for product, location and date                  |

No fact-to-fact joins should be introduced merely for ETL convenience.

## 8. Phase 5 Scope

### Required

* Extract
* Raw ingestion
* Staging
* Transformation
* Validation
* Record-count reconciliation
* ETL logging

### Out of Scope

* Airflow
* dbt
* Spark
* Cloud orchestration
* Incremental loading
* SCD Type 2
* Complex CI/CD
* Machine learning
* BI development
* Analytics views
* PostgreSQL warehouse implementation

````

---