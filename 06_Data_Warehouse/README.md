# Phase 6 — Data Warehouse

## Purpose

Phase 6 implements the Project Atlas PostgreSQL data warehouse using the approved dimensional/star-schema design.

The warehouse receives the validated warehouse-ready datasets produced in Phase 5 and provides the trusted foundation for the Phase 7 SQL analytics layer and downstream Power BI and Tableau analysis.

## Warehouse Structure

Atlas contains 17 warehouse tables:

### Dimensions

- `dim_date`
- `dim_account`
- `dim_customer`
- `dim_product`
- `dim_supplier`
- `dim_location`
- `dim_employee`
- `dim_machine`

### Facts

- `fact_sales`
- `fact_production`
- `fact_maintenance`
- `fact_financial_transaction`
- `fact_budget`
- `fact_energy`
- `fact_emissions`
- `fact_waste`
- `fact_inventory`

The dimensions are conformed where appropriate so that business processes can be analyzed consistently across the warehouse.

## Load

The warehouse is loaded from the Phase 5 warehouse-ready CSV files using:

`05_ETL/load_atlas.sql`

Dimension dependencies are respected during loading. For example, `dim_supplier` must be loaded before `dim_product` because products reference suppliers.

## Validation

The warehouse was validated in DBeaver after loading.

Validation included:

- Row counts
- Primary-key uniqueness
- Dimension referential integrity
- Fact referential integrity
- Required key NULL checks

All Phase 6 validation checks passed.

## Final Warehouse Row Counts

| Table | Rows |
|---|---:|
| `dim_account` | 1,000 |
| `dim_customer` | 50,000 |
| `dim_date` | 2,557 |
| `dim_employee` | 5,000 |
| `dim_location` | 100 |
| `dim_machine` | 2,000 |
| `dim_product` | 5,000 |
| `dim_supplier` | 1,000 |
| `fact_budget` | 20,000 |
| `fact_emissions` | 100,000 |
| `fact_energy` | 99,800 |
| `fact_financial_transaction` | 300,000 |
| `fact_inventory` | 499,000 |
| `fact_maintenance` | 49,950 |
| `fact_production` | 200,000 |
| `fact_sales` | 499,002 |
| `fact_waste` | 99,900 |

## GitHub Deliverables

```text
06_Data_Warehouse/
├── schema.sql
└── README.md
```
