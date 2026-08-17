# Phase 6 — Data Warehouse

## Overview

Phase 6 implements the PostgreSQL data warehouse for Project Atlas.

The warehouse transforms the validated `warehouse_ready` outputs from Phase 5 into a relational dimensional model that can support reusable SQL analytics, Power BI, and Tableau.

The warehouse is implemented and managed using PostgreSQL with DBeaver.

## Purpose

The warehouse provides a trusted analytical foundation for:

- Cross-domain analysis
- Reusable SQL analytics
- KPI calculation
- Power BI reporting
- Tableau reporting
- Executive and domain-level decision intelligence

The warehouse is designed to preserve clear fact grain, conformed dimensions, referential integrity, and consistent business definitions.

## Technology

- PostgreSQL
- DBeaver
- SQL

## Warehouse Structure

Project Atlas contains 17 warehouse tables:

### Dimensions

1. `dim_date`
2. `dim_account`
3. `dim_customer`
4. `dim_product`
5. `dim_supplier`
6. `dim_location`
7. `dim_employee`
8. `dim_machine`

### Facts

1. `fact_sales`
2. `fact_production`
3. `fact_maintenance`
4. `fact_financial_transaction`
5. `fact_budget`
6. `fact_energy`
7. `fact_emissions`
8. `fact_waste`
9. `fact_inventory`

## Data Flow

```text
Phase 5
warehouse_ready CSV files
        |
        v
DBeaver / PostgreSQL
        |
        v
Atlas Warehouse
        |
        v
Phase 7
Reusable SQL Analytics
```

## Loading Approach

The Phase 5 `warehouse_ready` CSV files were loaded into PostgreSQL using DBeaver.

Dimension tables were loaded before fact tables so that foreign-key relationships could be enforced during fact loading.

The implemented warehouse was reconciled against the Phase 5 outputs.

## Fact Grain

Each fact table has a defined analytical grain.

Examples include:

* `fact_sales` — one sales transaction line
* `fact_production` — one production activity record for a product, location, machine, employee, and date
* `fact_maintenance` — one maintenance activity record
* `fact_financial_transaction` — one financial transaction
* `fact_budget` — one budget record for a date, location, and category
* `fact_energy` — one energy consumption record
* `fact_emissions` — one emissions record
* `fact_waste` — one waste record
* `fact_inventory` — one product/location/date inventory snapshot

The inventory grain was specifically validated to ensure there are no duplicate product/location/date combinations.

## Relationships

The warehouse uses conformed dimensions to support cross-domain analysis.

Examples:

```text
Sales → Date
Sales → Account
Sales → Customer
Sales → Product
Sales → Location

Production → Date
Production → Product
Production → Location
Production → Machine
Production → Employee

Maintenance → Date
Maintenance → Location
Maintenance → Machine
Maintenance → Employee

Inventory → Date
Inventory → Product
Inventory → Location
```

Fact-to-fact joins are not used as a default analytical modeling approach because incompatible fact grains can cause fan-out and double counting.

## Constraints

The warehouse uses:

* Primary keys
* Unique constraints
* Foreign keys
* Not-null checks
* Inventory grain uniqueness

Foreign-key relationships were validated after loading.

## Indexing

Indexes were created primarily on fact-table foreign keys used for dimensional joins and common analytical access patterns.

Primary-key and unique-constraint indexes are created automatically by PostgreSQL and are not duplicated.

The warehouse therefore avoids unnecessary redundant indexes.

## Data Validation

The warehouse validation process checks:

* Warehouse table existence
* Row counts
* Primary keys
* Foreign keys
* Referential integrity
* Inventory grain
* Production quantity validity
* Production outliers
* Warehouse indexes

The validation script is:

```text
sql/04_validate_warehouse.sql
```

## Production Data Quality Observation

Production records where `quantity_produced` exceeds `planned_quantity` are not automatically classified as invalid because above-plan production can represent a legitimate operational condition.

Extreme production outliers are monitored separately.

The current warehouse contains records where:

```text
quantity_produced > planned_quantity * 2
```

These records are retained because Atlas uses synthetic data containing controlled quality issues and outliers.

They will be considered during downstream analytics and dashboard development rather than being silently removed from the warehouse.

## SQL Files

```text
sql/
├── 01_create_dimensions.sql
├── 02_create_facts.sql
├── 03_create_indexes.sql
└── 04_validate_warehouse.sql
```

### `01_create_dimensions.sql`

Creates the eight warehouse dimensions and their constraints.

### `02_create_facts.sql`

Creates the nine core fact tables and their relationships to conformed dimensions.

### `03_create_indexes.sql`

Creates justified fact foreign-key indexes for analytical joins and filtering.

### `04_validate_warehouse.sql`

Provides reproducible warehouse validation queries.

## Phase 6 Completion Criteria

Phase 6 is considered complete when:

* All 17 warehouse tables exist
* Phase 5 data is loaded
* Expected warehouse row counts are reconciled
* Primary keys are present
* Foreign keys are present
* Referential integrity is validated
* Inventory grain is validated
* Production hard-validity checks pass
* Justified indexes are implemented
* Validation SQL is stored in the repository
* Warehouse documentation is complete

## Next Phase

After Phase 6 is committed and the warehouse is stable, Project Atlas proceeds to:

**Phase 7 — Analytics**

Phase 7 will build reusable SQL analytics on top of the trusted PostgreSQL warehouse.

The analytics layer will establish governed metrics and reusable analytical logic before BI development begins.

````