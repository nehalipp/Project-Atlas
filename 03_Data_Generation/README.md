# Phase 3 — Data Generation

## Purpose

This phase generates the clean synthetic baseline dataset for Project Atlas.

The data is generated with Python using:

- Python
- Pandas
- NumPy
- Faker

The generated data follows the approved Phase 2 data model and data dictionary.

All data is synthetic and intended for portfolio, analytics, and BI development purposes.

---

## Files

```text
03_Data_Generation/
├── generate_data.py
├── reference_data.xlsx
├── README.md
└── data/
    └── raw/
````

### generate_data.py

Generates the synthetic Atlas datasets using a fixed random seed of `42`.

### reference_data.xlsx

Contains the controlled reference values used by the data generator, including categories, statuses, departments, product classifications, and other business values.

### data/raw/

Contains the generated CSV datasets.

---

## Generated Datasets

The script generates 17 datasets:

### Dimensions

* `dim_date.csv`
* `dim_account.csv`
* `dim_customer.csv`
* `dim_product.csv`
* `dim_supplier.csv`
* `dim_location.csv`
* `dim_employee.csv`
* `dim_machine.csv`

### Facts

* `fact_sales.csv`
* `fact_production.csv`
* `fact_maintenance.csv`
* `fact_financial_transaction.csv`
* `fact_budget.csv`
* `fact_energy.csv`
* `fact_emissions.csv`
* `fact_waste.csv`
* `fact_inventory.csv`

---

## Data Generation

The generator uses:

* Date range: `2019-01-01` to `2025-12-31`
* Random seed: `42`
* Reproducible synthetic data
* Phase 2 column names and relationships
* Approved fact-table grains

The output is saved automatically to:

```text
03_Data_Generation/data/raw/
```

---

## How to Run

From the Project Atlas repository root:

```bash
python3 03_Data_Generation/generate_data.py
```

The generated CSV files will be saved under:

```text
03_Data_Generation/data/raw/
```

---

## Data Quality

This phase generates the clean synthetic baseline.

Intentional data-quality issues are introduced and analyzed separately in **Phase 4 — Data Quality**.