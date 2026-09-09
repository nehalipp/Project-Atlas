# Project Atlas — ETL

## Purpose

Phase 5 prepares the trusted Phase 4 datasets for loading into the PostgreSQL dimensional warehouse.

The ETL flow is:

```text
Phase 4 Trusted Data
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
Warehouse-Ready Data
        ↓
 PostgreSQL Warehouse
```

## ETL Process

### Extract

The 17 trusted datasets from Phase 4 are copied into the ETL raw layer.

The current trusted input contains **1,934,309 records** across:

* 8 dimensions
* 9 fact tables

### Staging

Python/Pandas is used for straightforward staging preparation, including:

* Data-type handling
* Date preparation
* Numeric preparation
* Preserving warehouse keys
* Preserving business identifiers
* Preserving fact-table grain
* Preserving measurement units

Data-quality remediation is not repeated because it was completed in Phase 4.

### Transform

The staging datasets are prepared for PostgreSQL loading.

Transformations focus on:

* Standardizing date fields
* Validating the expected warehouse structure
* Preserving dimensional keys and business identifiers
* Preserving fact-table grain
* Preserving applicable measurement units

No unnecessary aggregation or fact-to-fact transformation is performed.

### Validate

The warehouse-ready datasets were validated for:

* Dataset existence
* Expected structure
* Row counts
* Foreign-key relationships

All 17 datasets passed the Phase 5 validation and were prepared for warehouse loading.

## Warehouse-Ready Results

| Dataset                      | Warehouse-Ready Rows |
| ---------------------------- | -------------------: |
| `dim_account`                |                1,000 |
| `dim_customer`               |               50,000 |
| `dim_date`                   |                2,557 |
| `dim_employee`               |                5,000 |
| `dim_location`               |                  100 |
| `dim_machine`                |                2,000 |
| `dim_product`                |                5,000 |
| `dim_supplier`               |                1,000 |
| `fact_budget`                |               20,000 |
| `fact_emissions`             |              100,000 |
| `fact_energy`                |               99,801 |
| `fact_financial_transaction` |              300,000 |
| `fact_inventory`             |              499,001 |
| `fact_maintenance`           |               49,950 |
| `fact_production`            |              200,000 |
| `fact_sales`                 |              499,000 |
| `fact_waste`                 |               99,900 |

**Total warehouse-ready rows: 1,934,309**

## Loading

`load_atlas.sql` loads the warehouse-ready CSV files into PostgreSQL.

Dimensions are loaded before facts so that the approved dimensional relationships can be established.

The PostgreSQL schema and constraints are maintained in Phase 6.

## Python and SQL

Python/Pandas supports the preparation and validation steps of the ETL process.

SQL is used for PostgreSQL loading and becomes the primary language for warehouse and analytical processing in later phases.

## Result

Phase 5 produces validated warehouse-ready datasets without changing the approved Atlas data model or fact grains.

The current Phase 5 output contains **1,934,309 records across all 17 datasets** and has been successfully loaded into the PostgreSQL warehouse.