# Project Atlas — ETL

## Purpose

Phase 5 prepares the trusted datasets from Phase 4 for loading into the PostgreSQL dimensional warehouse.

The ETL pipeline is:

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

The 17 trusted datasets produced by Phase 4 are copied into the ETL raw layer.

The datasets include:

* 8 dimensions
* 9 fact tables

The Phase 4 trusted data contains **1,842,059 records** across the 17 datasets.

### Staging

The raw CSV files are prepared using simple Python/Pandas processing.

Staging focuses on:

* Consistent data types
* Date preparation
* Numeric preparation
* Preserving existing warehouse keys
* Preserving fact-table grain
* Preserving measurement units

Data-quality remediation is not repeated here because it was completed in Phase 4.

### Transform

The staging datasets are prepared for the PostgreSQL warehouse.

Transformations include:

* Standardizing actual date fields
* Validating the expected warehouse column structure
* Preserving dimensional keys and business identifiers
* Preserving fact-table row counts and grain
* Preserving `unit_of_measure` where applicable

Measurement units are carried through the warehouse-ready layer for applicable datasets. Current standardized units include:

* Energy: **kWh**
* CO₂ emissions: **kg**
* Waste: **kg**
* Product-related quantities: units defined by the applicable product or inventory record

No unnecessary aggregation or fact-to-fact transformation is performed.

### Validate

The warehouse-ready layer is validated for:

* Dataset existence
* Expected columns
* Row counts
* Foreign-key relationships

Validation passed successfully for **all 17 datasets**.

All expected foreign-key relationships were validated successfully.

The warehouse-ready validation confirms that the datasets conform to the expected Phase 6 warehouse loading structure.

## Loading

`load_atlas.sql` loads the warehouse-ready CSV files into PostgreSQL.

Dimensions are loaded before facts so that foreign-key relationships can be established correctly.

The PostgreSQL table definitions and constraints are maintained in Phase 6.

## Python and SQL

Python/Pandas supports extraction, staging, transformation and validation.

SQL is used for the PostgreSQL loading process and becomes the primary language for warehouse and analytical processing in later phases.

## Result

Phase 5 produces a validated, warehouse-ready dataset that can be loaded into the PostgreSQL dimensional warehouse without changing the approved data model or fact grains.

The Phase 5 warehouse-ready layer has passed validation across all **17 datasets** and is ready for Phase 6 warehouse loading.
