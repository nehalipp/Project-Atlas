# Phase 6 — Data Warehouse

## Purpose

Phase 6 implements the Project Atlas PostgreSQL data warehouse using the approved dimensional/star-schema design.

The warehouse receives the validated warehouse-ready datasets from Phase 5 and provides the foundation for the Phase 7 SQL analytics layer and downstream Power BI and Tableau analysis.

---

## Warehouse Structure

Atlas contains **17 warehouse tables**:

### Dimensions

* `dim_date`
* `dim_account`
* `dim_customer`
* `dim_product`
* `dim_supplier`
* `dim_location`
* `dim_employee`
* `dim_machine`

### Facts

* `fact_sales`
* `fact_production`
* `fact_maintenance`
* `fact_financial_transaction`
* `fact_budget`
* `fact_energy`
* `fact_emissions`
* `fact_waste`
* `fact_inventory`

The warehouse uses conformed dimensions, including Date and Location, to support consistent analysis across business processes.

Surrogate warehouse keys and retained business identifiers provide relational integrity and source traceability.

Fact tables preserve their defined business grains and are not directly joined to other fact tables. Cross-domain analysis is performed through compatible dimensions and aggregated measures.

---

## Load

The warehouse is loaded from the Phase 5 warehouse-ready CSV files using:

`05_ETL/load_atlas.sql`

The load process truncates existing warehouse data and reloads the validated datasets in dependency order. Dimensions are loaded before facts so that foreign-key relationships can be enforced.

---

## Constraints and Relationships

The PostgreSQL schema enforces:

* Primary-key constraints on all 17 tables
* Unique constraints on business identifiers
* Foreign-key relationships between dimensions and facts
* Required `NOT NULL` constraints
* Appropriate nullable fields defined by the data dictionary

The warehouse structure follows the approved Atlas data model.

---

## Validation

The loaded warehouse was validated for:

* Table and row counts
* Primary-key uniqueness
* Business-identifier uniqueness
* Foreign-key referential integrity
* Required key NULLs
* Date coverage
* Measurement units
* Negative operational values
* Schema constraints

All Phase 6 validation checks passed.

### Validation Results

| Check                          | Result                   |
| ------------------------------ | ------------------------ |
| Warehouse tables               | 17                       |
| Primary-key duplicates         | 0                        |
| Business-identifier duplicates | 0                        |
| Invalid foreign-key references | 0                        |
| Required foreign-key NULLs     | 0                        |
| Date range                     | 2019-01-01 to 2025-12-31 |
| Negative operational values    | 0                        |
| Total warehouse rows           | 1,934,309                |

---

## Final Warehouse Row Counts

| Table                        |    Rows |
| ---------------------------- | ------: |
| `dim_account`                |   1,000 |
| `dim_customer`               |  50,000 |
| `dim_date`                   |   2,557 |
| `dim_employee`               |   5,000 |
| `dim_location`               |     100 |
| `dim_machine`                |   2,000 |
| `dim_product`                |   5,000 |
| `dim_supplier`               |   1,000 |
| `fact_budget`                |  20,000 |
| `fact_emissions`             | 100,000 |
| `fact_energy`                |  99,801 |
| `fact_financial_transaction` | 300,000 |
| `fact_inventory`             | 499,001 |
| `fact_maintenance`           |  49,950 |
| `fact_production`            | 200,000 |
| `fact_sales`                 | 499,000 |
| `fact_waste`                 |  99,900 |

**Total warehouse rows: 1,934,309**

---

## GitHub Deliverables

```text
06_Data_Warehouse/
├── README.md
└── schema.sql
```