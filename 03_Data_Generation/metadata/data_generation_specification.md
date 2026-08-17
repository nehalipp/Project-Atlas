# Project Atlas — Data Generation Specification

## 1. Purpose

This document defines how the synthetic source data for Project Atlas is
generated.

The data supports the approved Phase 2 Data Model and provides realistic
operational data for the Data Quality, ETL, Warehouse, Analytics, Power BI,
and Tableau phases.

All data is synthetic and intended for portfolio and demonstration purposes
only.

---

## 2. Generation Approach

Data is generated using:

- Python
- Faker
- Pandas
- NumPy where useful

The generation process is:

- Reproducible
- Relationship-aware
- Configurable
- Realistic
- Maintainable
- Easy to reproduce and explain

A fixed random seed is used so that the clean baseline can be reproduced
using the same configuration and generator version.

The Phase 3 workflow is:

```text
Reference Data Generation
        ↓
Reference Data Validation
        ↓
Business Data Generation
        ↓
Business Data Validation
        ↓
Controlled Quality Issue Injection
````

The clean baseline is validated before quality issues are introduced.

---

## 3. Source Datasets

Phase 3 creates source data for all 16 approved Atlas domains.

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

These datasets represent the synthetic operational source layer.

---

## 4. Approved Data Volumes

The clean baseline generation targets are:

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

The clean baseline therefore contains:

```text
64,100 reference records
+
1,870,000 business records
=
1,934,100 clean baseline records
```

These are generation targets for the clean baseline.

Final record counts in the quality-issue datasets may differ because
controlled duplicate injection and other quality issues are intentionally
introduced.

---

## 5. Date Range

The approved Atlas generation period is:

```text
Start: 2019-01-01
End:   2025-12-31
```

The date range is centralized in:

```text
03_Data_Generation/config/generation_config.py
```

---

## 6. Reproducibility

The centralized configuration contains:

```text
Random seed
Date range
Dataset record counts
Quality-issue rates
Project paths
```

The project seed is:

```text
42
```

The same configuration and generator version should reproduce the same clean
baseline.

---

## 7. Business Relationships

Generation follows the dependency structure defined by the approved Phase 2
Data Model.

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

Each employee and machine has one primary operational location.

### Sales

Sales reference:

```text
Date
Account
Customer
Product
Location
```

The account associated with a sales record must correspond to the account
associated with its customer in the clean baseline.

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

### Financial Transactions

Financial transactions reference:

```text
Date
Location
```

### Budget

Budget records reference:

```text
Date
Location
```

The date represents the applicable budget period.

### Energy

Energy records reference:

```text
Date
Location
```

### Emissions

Emissions records reference:

```text
Date
Location
```

### Waste

Waste records reference:

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

The generation process follows the relationships established in the approved
Phase 2 Data Model.

---

## 8. Fact Grain

The generated business datasets respect the approved Phase 2 fact grains.

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

Inventory is a periodic snapshot fact.

```text
Inventory Grain:
Date + Product + Location
```

No Phase 3 dataset introduces a new fact grain outside the approved Phase 2
Data Model.

---

## 9. Lifecycle and Baseline Integrity

Reference data establishes valid business relationships and lifecycle
constraints used by the business-process generators.

The clean baseline must maintain valid relationships such as:

* Customer → Account
* Product → Supplier
* Employee → Location
* Machine → Location
* Sales → Account
* Sales → Customer
* Sales → Product
* Sales → Location
* Production → Product
* Production → Machine
* Production → Employee
* Production → Location
* Maintenance → Machine
* Maintenance → Employee
* Maintenance → Location
* Inventory → Product
* Inventory → Location

The business-data validation scripts verify these relationships before quality
issues are injected.

---

## 10. Realistic Data Behavior

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

Values should vary by entity and business activity rather than being
uniformly random.

Examples include:

* Different levels of customer sales activity
* Different product demand
* Different operational activity by location
* Different machine production and maintenance activity
* Variation in energy, emissions, waste, and inventory over time

The generated data is synthetic and does not represent real companies,
customers, employees, financial results, or operational performance.

---

## 11. Business-Process Generation Rules

### Sales

Sales use valid customers, accounts, products, and locations.

Revenue is mathematically consistent with quantity, unit price, and discount
in the clean baseline.

### Production

Production uses valid products, machines, employees, and locations.

Production activity varies by product, machine, location, and date.

### Maintenance

Maintenance is associated with valid machines and their operational
locations.

Maintenance activity includes a mixture of preventive, corrective,
inspection, and emergency events.

### Financial Transactions

Financial activity includes realistic revenue and expense categories.

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

Budget records support budget-versus-actual analysis.

Budget categories align with relevant financial categories.

### Energy

Energy records represent consumption by location and energy type.

Examples include:

```text
Electricity
Natural Gas
Fuel
Steam
```

### Emissions

Emissions represent operational emission sources.

Examples include:

```text
Electricity
Natural Gas
Fuel
Transportation
Process
```

### Waste

Waste represents operational waste types and disposal methods.

Examples include:

```text
Metal
Plastic
Paper
Chemical
General
Organic
```

### Inventory

Inventory represents product stock at locations over time.

The clean baseline maintains:

```text
Closing Quantity
=
Opening Quantity
+ Received Quantity
- Issued Quantity
```

---

## 12. Cross-Domain Consistency

The generated datasets support meaningful cross-domain analysis.

Examples include:

```text
Sales + Production + Inventory
Production + Machine + Maintenance
Production + Energy + Emissions
Financial Transactions + Budget
```

Facts must not be joined directly at incompatible detailed grains.

Cross-domain analysis must aggregate each fact to a compatible business grain
before comparison.

Examples include:

```text
Date + Product + Location
```

and:

```text
Date + Location
```

This prevents fan-out and double counting.

---

## 13. Clean Baseline Validation

Before quality issues are introduced, the generated datasets are validated.

Reference validation checks include:

* Record counts
* Customer → Account relationships
* Product → Supplier relationships
* Employee → Location relationships
* Machine → Location relationships
* Product pricing
* Lifecycle dates

Business validation checks include:

* Record counts
* Referential integrity
* Sales customer/account consistency
* Sales revenue calculation
* Production machine/location consistency
* Production employee/location consistency
* Maintenance machine/location consistency
* Maintenance employee/location consistency
* Inventory Date + Product + Location grain

A clean baseline validation failure indicates a generation problem and must
be resolved before quality injection.

---

## 14. Controlled Data-Quality Issues

The clean baseline is generated first and remains preserved under:

```text
03_Data_Generation/data/raw/
```

Controlled quality issues are then introduced by:

```text
inject_quality_issues.py
```

The intentionally imperfect copies are written to:

```text
03_Data_Generation/data/quality_issues/
```

Potential quality issues include:

* Missing values
* Duplicate records
* Invalid references
* Invalid categories
* Invalid numeric values
* Revenue inconsistencies
* Outliers
* Referential-integrity issues
* Business-rule violations
* Other controlled structural or consistency defects

Quality issues are deliberately introduced using the centralized quality
parameters.

They are not intended to represent random uncontrolled corruption.

The quality-issue dataset exists specifically to provide the input for
Phase 4 — Data Quality.

---

## 15. Output Structure

Phase 3 produces two distinct data states:

```text
03_Data_Generation/
└── data/
    ├── raw/
    │   ├── accounts.csv
    │   ├── customers.csv
    │   ├── products.csv
    │   ├── suppliers.csv
    │   ├── locations.csv
    │   ├── employees.csv
    │   ├── machines.csv
    │   ├── sales.csv
    │   ├── production.csv
    │   ├── maintenance.csv
    │   ├── financial_transactions.csv
    │   ├── budget.csv
    │   ├── energy.csv
    │   ├── emissions.csv
    │   ├── waste.csv
    │   └── inventory.csv
    │
    └── quality_issues/
        └── intentionally imperfect copies
```

The `raw/` directory contains the validated clean baseline.

The `quality_issues/` directory contains the intentionally imperfect source
copies used by Phase 4.

The quality-issue datasets do not replace the clean baseline.

---

## 16. Phase 3 Scripts

Phase 3 contains six operational scripts.

### `generate_reference_data.py`

Generates the seven reference datasets.

### `validate_reference_data.py`

Validates the generated reference datasets and their approved relationships.

### `generate_business_data.py`

Generates the nine clean business-process datasets using the reference data.

### `validate_business_data.py`

Validates the clean business-process datasets, referential integrity,
business rules, and approved fact grain.

### `inject_quality_issues.py`

Creates intentionally imperfect copies of all 16 datasets for Phase 4.

### `generate_all_data.py`

Orchestrates the complete Phase 3 workflow in the approved order.

---

## 17. Phase 3 Execution

The recommended execution method is:

```bash
python3 03_Data_Generation/scripts/generate_all_data.py
```

The orchestration performs:

```text
1. Reference Data Generation
2. Reference Data Validation
3. Business Data Generation
4. Business Data Validation
5. Controlled Quality Issue Injection
```

The pipeline stops if a required generation or validation step fails.

Individual scripts remain available for targeted execution and troubleshooting.

---

## 18. Technology

Phase 3 uses:

* Python
* Faker
* Pandas
* NumPy
* CSV files

No additional orchestration framework or data platform is required.

---

## 19. Implementation Rules

The generation implementation must:

* Follow the approved Phase 2 Data Model.
* Preserve approved business relationships.
* Respect documented fact grain.
* Use centralized configuration.
* Use reproducible random generation.
* Keep all data synthetic.
* Avoid real companies, people, customers, employees, or financial results.
* Remain understandable and maintainable.
* Avoid unnecessary technologies or complexity.

No additional domains, facts, dimensions, bridges, or relationships are
introduced during Phase 3 without revisiting the approved Phase 2 Data Model.

---

## 20. Status

> **Phase 3 — Data Generation**
>
> **Specification:** Complete
>
> **Reference generation:** Complete
>
> **Reference validation:** Passed
>
> **Business generation:** Complete
>
> **Business validation:** Passed
>
> **Quality issue injection:** Complete
>
> **Phase status:** COMPLETE
>
> **Next phase:** Phase 4 — Data Quality

---

> **Note:** All data used in Project Atlas is synthetic and intended for
> portfolio and demonstration purposes only.