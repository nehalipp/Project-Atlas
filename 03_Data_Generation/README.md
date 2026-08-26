# Project Atlas — Phase 3 Data Generation

## Purpose

Phase 3 creates realistic synthetic operational data for Project Atlas.

The data represents a commercial and manufacturing environment covering customers, products, suppliers, locations, employees, machines, sales, production, maintenance, finance, inventory and sustainability.

All data is synthetic and created for portfolio and analytical demonstration purposes.

---

## Generation Approach

Data is generated using:

- Python
- Faker
- Pandas
- NumPy

A fixed random seed of `42` is used so the datasets can be reproduced consistently.

Operational dates range from:

`2019-01-01` to `2025-12-31`

Reference attributes such as employee hire dates and machine installation dates are generated before the operational period.

---

## Datasets

Phase 3 generates 17 datasets.

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

The datasets follow the approved Phase 2 dimensional model.

---

## Data Volumes

| Dataset | Approx. Rows |
|---|---:|
| dim_date | 2,557 |
| dim_account | 1,000 |
| dim_customer | 50,000 |
| dim_product | 5,000 |
| dim_supplier | 1,000 |
| dim_location | 100 |
| dim_employee | 5,000 |
| dim_machine | 2,000 |
| fact_sales | 500,500 |
| fact_production | 200,200 |
| fact_maintenance | 50,000 |
| fact_financial_transaction | 300,300 |
| fact_budget | 20,000 |
| fact_energy | 100,000 |
| fact_emissions | 100,000 |
| fact_waste | 100,000 |
| fact_inventory | 500,000 |

Total raw rows: approximately **1.94 million**.

---

## Business Realism Controls

The generator keeps the existing 17-table schema, keys, date range, approximate row volumes and controlled Phase 4 quality issues. The valid baseline data now includes modest business-driven variation across products, customers, locations and operational measures.

Examples:
- Location names are synthetic but business-readable rather than generic facility labels.
- Sales demand varies by product category, customer segment, location type and month.
- Production is generated from plant-based machines with controlled achievement and defect rates.
- Maintenance cost and downtime vary by maintenance type and facility profile.
- Energy, emissions and waste vary by location/business profile.
- Financial and budget values vary by category and location type.
- Inventory issuance and reorder points vary by product demand profile.

These are distribution improvements, not schema changes. The existing downstream phases remain compatible as long as the same raw-to-warehouse column structure is retained.

## Measurement Units

The `reference_data.xlsx` workbook contains a `Measurement_Units` sheet. Atlas uses USD for financial measures, hours for time measures, kWh for energy consumption, kg CO2e for emissions, kg for waste, and the product-specific `unit_of_measure` for sales, production and inventory quantities.

## Controlled Raw-Data Quality Issues

The raw datasets intentionally contain a small number of realistic quality problems.

These include:

- Missing values
- Leading/trailing whitespace
- Duplicate records
- Invalid foreign-key references
- Invalid categorical values
- Negative operational quantities
- Revenue reconciliation issues
- Inventory reconciliation issues
- Production business-rule violations
- Production outliers
- Financial transaction outliers

Examples include:

- Missing customer country
- Missing product subcategory
- Missing supplier category
- Missing maintenance type
- Invalid customer segments
- Invalid location types
- Invalid machine statuses
- Invalid supplier categories
- Invalid customer, product, machine and employee references
- Negative sales, inventory, energy and waste quantities
- Sales revenue inconsistencies
- Inventory closing-balance inconsistencies
- Production defects greater than produced quantity
- Unusually large production quantities
- Unusually large financial transactions

These issues are intentional and are part of the project design.

They simulate the type of imperfect operational data that a data analyst may encounter before data is prepared for reporting and analytics.

---

## Output

Raw CSV files are saved to:

```text
03_Data_Generation/data/raw/
```

The raw datasets are intentionally imperfect.

Phase 4 uses these datasets to perform data-quality assessment, remediation and trusted-data validation.

---

## Reproducibility

Run:

```bash
python generate_data.py
```

The generator uses a fixed random seed (`42`) to produce reproducible
synthetic data.

## Phase 3 Deliverables

```text
03_Data_Generation/
├── generate_data.py
├── reference_data.xlsx
└── README.md
```

Phase 4 will profile, validate and remediate the raw datasets before they
are used downstream.