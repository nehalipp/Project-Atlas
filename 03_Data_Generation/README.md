# Project Atlas — Data Generation

## Purpose

Phase 3 creates the synthetic raw data used by Project Atlas.

The data represents a commercial and industrial business covering sales,
customers, products, suppliers, production, maintenance, finance,
inventory, energy, emissions and waste.

All data is synthetic and is intended for portfolio and analytical
demonstration purposes.

## Data Generation

The datasets are generated using:

- Python
- Pandas
- NumPy
- Faker

A fixed random seed (`42`) is used so the data can be reproduced.

Date range:

**2019-01-01 to 2025-12-31**

The generator creates 17 warehouse datasets:

### Dimensions

- dim_date
- dim_account
- dim_customer
- dim_product
- dim_supplier
- dim_location
- dim_employee
- dim_machine

### Facts

- fact_sales
- fact_production
- fact_maintenance
- fact_financial_transaction
- fact_budget
- fact_energy
- fact_emissions
- fact_waste
- fact_inventory

## Data Volumes

The baseline generation contains approximately **1.94 million records**
across the 17 datasets.

The largest datasets include:

- Sales — 500,000 baseline rows
- Inventory — 500,000 rows
- Financial Transactions — 300,000 baseline rows
- Production — 200,000 baseline rows
- Energy — 100,000 rows
- Emissions — 100,000 rows
- Waste — 100,000 rows

## Raw Data Quality

The raw layer intentionally contains controlled data-quality issues.

Examples include:

- Missing values
- Duplicate records
- Invalid references
- Invalid domain values
- Negative quantities or measurements
- Revenue inconsistencies
- Inventory reconciliation issues
- Production rule violations
- Outliers

The issues are intentionally introduced to simulate the type of imperfect
operational data that an analytics team may encounter before data is
validated and prepared for reporting.

The raw datasets are therefore **not trusted data**.

The exact quality issues are intentionally not documented in the generation
output. They are expected to be discovered during Phase 4 through data
profiling and validation.

## Reference Data

`reference_data.xlsx` contains:

- Approved categorical values
- Business rules
- Expected dataset volumes
- Data-quality dimensions

It provides the reference information used during data-quality validation.

## Output

Generated CSV files are saved to:

```text
03_Data_Generation/data/raw/
````

The raw layer is the starting point for the Phase 4 data-quality process.

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