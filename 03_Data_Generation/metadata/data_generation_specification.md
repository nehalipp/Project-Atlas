# Project Atlas — Data Generation Specification

## 1. Purpose

This document defines how the synthetic source data for Project Atlas will be generated.

The data supports the approved Phase 2 data model and provides realistic operational data for the Data Quality, ETL, Warehouse, Analytics, Power BI, and Tableau phases.

All data is synthetic and intended for portfolio and demonstration purposes only.

---

## 2. Generation Approach

Data will be generated using:

- Python
- Faker
- Pandas
- NumPy where useful

The generation process will be:

- Reproducible
- Relationship-aware
- Configurable
- Realistic
- Easy to reproduce and explain

A fixed random seed will be used so the same configuration can reproduce the baseline datasets.

The generation workflow is:

```text
Reference Data
      ↓
Clean Business Data
      ↓
Controlled Quality Issues
      ↓
Imperfect Source Data
````

---

## 3. Source Datasets

The generator will create source data for all 16 Atlas domains.

### Reference Data

```text
accounts
customers
products
suppliers
locations
employees
machines
```

### Business Process Data

```text
sales
production
maintenance
financial_transactions
budget
energy
emissions
waste
inventory
```

These datasets represent the operational source layer and will later flow through the Data Quality and ETL phases.

---

## 4. Initial Data Volumes

The approved generation targets are:

| Dataset                | Target Records |
| ---------------------- | -------------: |
| Accounts               |          1,000 |
| Customers              |         50,000 |
| Suppliers              |          1,000 |
| Products               |          5,000 |
| Locations              |            100 |
| Employees              |          5,000 |
| Machines               |          2,000 |
| Sales                  |        500,000 |
| Production             |        200,000 |
| Maintenance            |         50,000 |
| Financial Transactions |        300,000 |
| Budget                 |         20,000 |
| Energy                 |        100,000 |
| Emissions              |        100,000 |
| Waste                  |        100,000 |
| Inventory              |        500,000 |

These are generation targets. Final record counts after controlled quality-issue injection will be measured during the Data Quality phase.

---

## 5. Date Range

The business-process datasets will use:

```text
Start: 2019-01-01
End:   2025-12-31
```

The date range is centralized in:

```text
03_Data_Generation/config/generation_config.py
```

so it can be changed without modifying individual generation scripts.

---

## 6. Business Relationships

Generation follows the dependency structure established in the approved Phase 2 data model.

### Account and Customer

```text
Account
   ↓
Customer
```

Each customer belongs to one account.

### Supplier and Product

```text
Supplier
   ↓
Product
```

Each product has one primary supplier.

### Location, Employee and Machine

```text
Location
   ├── Employee
   └── Machine
```

Employees and machines are associated with operational locations.

### Sales

Sales reference:

```text
Date
Account
Customer
Product
Location
```

### Production

Production references:

```text
Date
Product
Location
Machine
Employee
```

### Maintenance

Maintenance references:

```text
Date
Location
Machine
Employee
```

### Financial Transactions and Budget

These reference:

```text
Date
Location
```

### Energy, Emissions and Waste

These reference:

```text
Date
Location
```

### Inventory

Inventory references:

```text
Date
Product
Location
```

The generation process must preserve the relationships defined in the approved Phase 2 model.

---

## 7. Fact Grain

The generated business data must respect the approved fact grains.

| Dataset                | Grain                                 |
| ---------------------- | ------------------------------------- |
| Sales                  | One row per sales transaction line    |
| Production             | One row per production activity       |
| Maintenance            | One row per maintenance event         |
| Financial Transactions | One row per financial transaction     |
| Budget                 | One row per budget record             |
| Energy                 | One row per energy measurement        |
| Emissions              | One row per emissions record          |
| Waste                  | One row per waste record              |
| Inventory              | One row per Product + Location + Date |

Inventory is a periodic snapshot dataset.

```text
Inventory Grain:
Date + Product + Location
```

No generated dataset should create a new fact grain that differs from the approved Phase 2 model.

---

## 8. Realistic Data Behavior

Generated data should contain believable:

* Names and business identifiers
* Dates
* Product categories
* Supplier relationships
* Customer activity
* Locations
* Employee assignments
* Machine assignments
* Quantities
* Prices
* Costs
* Revenue
* Production activity
* Maintenance activity
* Inventory levels
* Energy consumption
* Emissions
* Waste

Values should vary by entity and business activity rather than being uniformly random.

For example:

* Some customers should generate more sales activity than others.
* Some products should have higher demand.
* Some locations should have higher operational activity.
* Machines should have different levels of production and maintenance activity.
* Energy, emissions, waste, and inventory should vary by location and time.

---

## 9. Business-Process Generation Rules

### Sales

Sales should use valid customers, accounts, products, and locations.

Revenue should be mathematically consistent with quantity, unit price, and discount in the clean baseline.

### Production

Production should use valid products, machines, employees, and locations.

Production activity should vary by product, machine, location, and date.

### Maintenance

Maintenance should be associated with valid machines and their operational locations.

Maintenance types should include a realistic mixture of preventive, corrective, inspection, and emergency activity.

### Financial Transactions

Financial activity should include realistic revenue and expense categories.

Examples include:

```text
Revenue
Materials
Labor
Maintenance
Utilities
Transportation
Operating Expense
Other Expense
```

### Budget

Budget records should support budget-versus-actual analysis.

Budget categories should align with relevant financial categories.

### Energy

Energy records should represent realistic consumption by location and energy type.

Examples:

```text
Electricity
Natural Gas
Fuel
Steam
```

### Emissions

Emissions should represent realistic operational sources.

Examples:

```text
Electricity
Natural Gas
Fuel
Transportation
Process
```

### Waste

Waste should represent realistic waste types and disposal methods.

Examples:

```text
Metal
Plastic
Paper
Chemical
General
Organic
```

### Inventory

Inventory should represent product stock at each location over time.

The clean baseline should maintain:

```text
Closing Quantity
=
Opening Quantity
+ Received Quantity
- Issued Quantity
```

---

## 10. Cross-Domain Consistency

The generated datasets should support meaningful cross-domain analysis.

Examples include:

```text
Sales + Production + Inventory
Production + Machine + Maintenance
Production + Energy + Emissions
Revenue + Financial Transactions + Budget
```

Facts must not be directly joined at incompatible grains.

Cross-domain comparisons will be performed by aggregating facts to compatible business grains.

This prevents fan-out and double counting.

---

## 11. Controlled Data-Quality Issues

The clean baseline generated by:

```text
generate_reference_data.py
generate_business_data.py
```

should remain internally consistent.

Controlled quality issues will then be introduced by:

```text
inject_quality_issues.py
```

Potential issues include:

* Missing values
* Duplicate records
* Invalid references
* Invalid categories
* Invalid quantities or prices
* Revenue inconsistencies
* Outliers
* Referential-integrity issues
* Business-rule violations

Quality issues must be deliberate, documented, and limited enough to keep the source data believable.

The quality-injection process must not introduce uncontrolled random corruption.

---

## 12. Reproducibility

The centralized configuration contains:

```text
Random seed
Date range
Dataset record counts
Generation parameters
Quality-issue parameters
```

The initial random seed is:

```text
42
```

The same configuration and generator version should produce the same baseline data.

---

## 13. Generation Order

The complete generation workflow follows:

```text
1. Reference Data
2. Business Process Data
3. Controlled Quality Issues
4. Final Raw Source Data
```

Reference data must exist before dependent business-process data is generated.

Business-process datasets must use valid identifiers from the reference datasets.

Quality issues are applied only after the clean baseline has been generated.

---

## 14. Output

Generated datasets are stored under:

```text
data/
└── raw/
```

Expected files:

```text
accounts.csv
customers.csv
products.csv
suppliers.csv
locations.csv
employees.csv
machines.csv
sales.csv
production.csv
maintenance.csv
financial_transactions.csv
budget.csv
energy.csv
emissions.csv
waste.csv
inventory.csv
```

The generated files represent the operational source layer.

They are not trusted warehouse data.

---

## 15. Implementation Rules

The generation code must:

* Follow the approved Phase 2 model.
* Preserve business relationships.
* Respect fact grain.
* Use the centralized configuration.
* Use reproducible random generation.
* Keep all data synthetic.
* Avoid real companies, people, customers, employees, or financial results.
* Remain understandable and maintainable.
* Avoid unnecessary technologies or complexity.

No additional domains, facts, dimensions, or relationships will be introduced during Phase 3 without revisiting the approved Phase 2 model.

---

## 16. Phase 3 Scripts

The Phase 3 implementation uses four scripts:

```text
generate_reference_data.py
    ↓
generate_business_data.py
    ↓
inject_quality_issues.py
    ↓
generate_all_data.py
```

### `generate_reference_data.py`

Creates the seven reference datasets.

### `generate_business_data.py`

Creates the nine clean business-process datasets using the reference data.

### `inject_quality_issues.py`

Introduces the controlled data-quality issues required for Phase 4.

### `generate_all_data.py`

Runs the complete generation workflow in the correct order.

---

## 17. Status

> **Phase 3 — Data Generation**
>
> **Generation specification:** Locked
>
> **Reference data:** Generated and validated
>
> **Next step:** Implement `generate_business_data.py`

---

> **Note:** All data used in Project Atlas is synthetic and intended for portfolio and demonstration purposes only.
