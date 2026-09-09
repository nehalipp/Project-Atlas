# Project Atlas — Phase 3 Data Generation

## Purpose

Phase 3 creates realistic synthetic operational data for Project Atlas.

The data represents a commercial and manufacturing environment covering customers, products, suppliers, locations, employees, machines, sales, production, maintenance, finance, inventory and sustainability.

All data is synthetic and created for portfolio and analytical demonstration purposes.

---

## Generation Approach

Data is generated using:

* Python
* Faker
* Pandas
* NumPy

A fixed random seed of `42` is used for reproducibility.

Operational dates range from:

`2019-01-01` to `2025-12-31`

Reference attributes such as employee hire dates and machine installation dates are generated before the operational period.

---

## Datasets

Phase 3 generates 17 datasets:

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

The datasets follow the approved Phase 2 dimensional model.

---

## Raw Data Volumes

| Dataset                      |    Rows |
| ---------------------------- | ------: |
| `dim_date`                   |   2,557 |
| `dim_account`                |   1,000 |
| `dim_customer`               |  50,000 |
| `dim_product`                |   5,000 |
| `dim_supplier`               |   1,000 |
| `dim_location`               |     100 |
| `dim_employee`               |   5,000 |
| `dim_machine`                |   2,000 |
| `fact_sales`                 | 500,500 |
| `fact_production`            | 200,200 |
| `fact_maintenance`           |  50,000 |
| `fact_financial_transaction` | 300,300 |
| `fact_budget`                |  20,000 |
| `fact_energy`                | 100,000 |
| `fact_emissions`             | 100,000 |
| `fact_waste`                 | 100,000 |
| `fact_inventory`             | 500,000 |

**Total raw rows: 1,937,657**

---

## Controlled Data-Quality Issues

The raw datasets intentionally contain controlled quality issues for Phase 4, including:

* Missing values
* Leading/trailing whitespace
* Duplicate records
* Invalid foreign-key references
* Invalid categorical values
* Negative quantities
* Revenue inconsistencies
* Inventory inconsistencies
* Production business-rule violations
* Production outliers
* Financial transaction outliers

These issues simulate imperfect operational data that may require validation and remediation before reporting.

### Measurement Units

* Product-related quantities: `Each`
* Energy: `kWh`
* Emissions: `kg` CO₂-equivalent
* Waste: `kg`

Maintenance and downtime are measured in hours. Financial amounts are monetary values.

---

## Output

Raw CSV files are saved to:

```text
03_Data_Generation/data/raw/
```

Phase 4 uses these raw datasets for profiling, validation and remediation.

---

## Reproducibility

Run:

```bash
python generate_data.py
```

The generator uses seed `42` to produce reproducible synthetic data.

## Phase 3 Deliverables

```text
03_Data_Generation/
├── generate_data.py
├── reference_data.xlsx
└── README.md
```