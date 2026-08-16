# Project Atlas — Data Generation Specification

## 1. Purpose

This document defines how the synthetic source data for Project Atlas will be generated.

The data will support the approved Phase 2 data model and provide realistic operational data for the Data Quality, ETL, Warehouse, Analytics, Power BI, and Tableau phases.

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
- Designed with controlled data-quality issues

A fixed random seed will be used so the same configuration can reproduce the dataset.

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
````

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

These source datasets will later flow through the Atlas data-quality and ETL processes.

---

## 4. Initial Data Volumes

The following volumes are the approved generation targets for the initial implementation.

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

These are generation targets rather than final data-quality counts. The final record counts will be measured after generation.

---

## 5. Date Range

The initial datasets will use:

```text
Start: 2019-01-01
End:   2025-12-31
```

The date range is centralized in the generation configuration so it can be changed without modifying individual generation scripts.

---

## 6. Business Relationships

The generator will create data in dependency order so that relationships remain realistic.

### Account and Customer

```text
Account
   ↓
Customer
```

Each customer belongs to an account.

### Supplier and Product

```text
Supplier
   ↓
Product
```

Each product has a primary supplier.

### Location, Employee and Machine

```text
Location
   ├── Employee
   └── Machine
```

Employees and machines are associated with operational locations.

### Sales

Sales will reference:

```text
Date
Account
Customer
Product
Location
```

### Production

Production will reference:

```text
Date
Product
Location
Machine
Employee
```

### Maintenance

Maintenance will reference:

```text
Date
Location
Machine
Employee
```

### Financial and Budget

These datasets will reference:

```text
Date
Location
```

### Energy, Emissions and Waste

These datasets will reference:

```text
Date
Location
```

### Inventory

Inventory will reference:

```text
Date
Product
Location
```

The generation process must preserve the relationships defined in the approved Phase 2 model.

---

## 7. Realistic Data Behavior

Generated data should contain believable:

* Names and business identifiers
* Dates
* Product categories
* Supplier relationships
* Customer attributes
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

Relationships and values should reflect the commercial/manufacturing scenario rather than being generated as completely independent random values.

---

## 8. Controlled Data-Quality Issues

The source data will intentionally contain realistic quality problems so that Phase 4 can demonstrate profiling and remediation.

Issues may include:

* Missing values
* Duplicate records
* Invalid references
* Invalid categories
* Invalid quantities or prices
* Revenue inconsistencies
* Outliers
* Referential-integrity issues
* Business-rule violations

Quality issues will be introduced deliberately and documented.

They should be large enough to be detected during profiling but limited enough that the underlying datasets remain believable.

The generator must not rely on uncontrolled random corruption.

---

## 9. Reproducibility

A centralized configuration will contain:

```text
Random seed
Date range
Dataset record counts
Quality-issue parameters
```

The initial random seed will be:

```text
42
```

The same configuration and generator version should produce reproducible source data.

---

## 10. Generation Order

The generation process will follow the dependency structure:

```text
Reference Data
      ↓
Business Process Data
      ↓
Controlled Quality Issues
      ↓
Generated Source Data
```

Reference data will be generated before dependent business-process data.

This allows downstream records to use valid source identifiers and realistic relationships.

---

## 11. Output

Generated datasets will be stored separately from the generation code.

Expected output:

```text
data/
└── raw/
    ├── accounts.csv
    ├── customers.csv
    ├── products.csv
    ├── suppliers.csv
    ├── locations.csv
    ├── employees.csv
    ├── machines.csv
    ├── sales.csv
    ├── production.csv
    ├── maintenance.csv
    ├── financial_transactions.csv
    ├── budget.csv
    ├── energy.csv
    ├── emissions.csv
    ├── waste.csv
    └── inventory.csv
```

The generated files represent the imperfect source layer and will not be treated as trusted warehouse data.

---

## 12. Generation Rules

The generator must:

* Use the approved Phase 2 model as the structural reference.
* Preserve required business relationships.
* Use reproducible random generation.
* Keep all data synthetic.
* Introduce controlled quality issues.
* Avoid real companies, people, financial results, or business relationships.
* Keep the implementation understandable and maintainable.
* Avoid unnecessary technologies or complexity.

No additional domains or warehouse entities will be introduced during data generation without revisiting the approved Phase 2 model.

---

## 13. Status

> **Phase 3 — Data Generation**
>
> **Generation specification:** Locked
>
> **Next step:** Implement the Python data-generation pipeline

---

> **Note:** All data used in Project Atlas is synthetic and intended for portfolio and demonstration purposes only.
