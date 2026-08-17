# Project Atlas — Data_Generation

## 1. Purpose

This phase generates the synthetic source data used throughout Project Atlas.

All datasets are created using the centralized configuration in:

```text
03_Data_Generation/config/generation_config.py
```

The generated CSV files are stored in:

```text
data/raw/
```

## 2. Generation Workflow

```text
generate_all_data.py
        ↓
Clean Reference Data
        ↓
Clean Business Data
        ↓
validate_reference_data.py
        ↓
validate_business_data.py
        ↓
Clean Baseline Passed
        ↓
inject_quality_issues.py
        ↓
Controlled Data Quality Defects
```

## 3. Main Scripts

| Script                       | Purpose                                         |
| ---------------------------- | ----------------------------------------------- |
| `generate_all_data.py`       | Runs the complete clean-data generation process |
| `generate_reference_data.py` | Generates the 7 reference/master datasets       |
| `generate_business_data.py`  | Generates the 9 business-process datasets       |
| `validate_reference_data.py` | Validates the clean reference datasets          |
| `validate_business_data.py`  | Validates the clean business datasets           |
| `inject_quality_issues.py`   | Injects controlled data-quality defects         |

## 4. Datasets Generated

**Reference datasets:**

* Accounts
* Customers
* Suppliers
* Products
* Locations
* Employees
* Machines

**Business datasets:**

* Sales
* Production
* Maintenance
* Financial Transactions
* Budget
* Energy
* Emissions
* Waste
* Inventory

## 5. Execution

From the Project Atlas root directory:

```bash
python3 03_Data_Generation/scripts/generate_all_data.py
```

Then validate the clean baseline:

```bash
python3 03_Data_Generation/scripts/validate_reference_data.py
python3 03_Data_Generation/scripts/validate_business_data.py
```

After both validations pass, inject the controlled quality issues:

```bash
python3 03_Data_Generation/scripts/inject_quality_issues.py
```

The resulting defective datasets are then used by **Phase 4 — Data Quality** for profiling, validation, measurement, and documentation.


## 6. Phase 3 Status
Phase 3 — Data Generation Status: Completed
```
Note: All data used in Project Atlas is synthetic and intended for portfolio and demonstration purposes only.
```
