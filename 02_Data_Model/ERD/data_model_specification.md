# Project Atlas — Data Model Specification

## 1. Purpose

This document defines the approved tables, grain, keys, and relationships for the Project Atlas data warehouse.

The model uses a dimensional/star-schema approach and is finalized before PostgreSQL warehouse implementation.

---

## 2. Dimensions

| Table | Grain | Primary Key |
|---|---|---|
| `dim_date` | One row per calendar date | `date_key` |
| `dim_account` | One row per account | `account_key` |
| `dim_customer` | One row per customer | `customer_key` |
| `dim_product` | One row per product | `product_key` |
| `dim_supplier` | One row per supplier | `supplier_key` |
| `dim_location` | One row per location | `location_key` |
| `dim_employee` | One row per employee | `employee_key` |
| `dim_machine` | One row per machine | `machine_key` |

Source/business identifiers are retained in the dimensions for traceability.

---

## 3. Facts

| Table | Grain | Primary Key |
|---|---|---|
| `fact_sales` | One row per sales transaction line | `sales_key` |
| `fact_production` | One row per production activity | `production_key` |
| `fact_maintenance` | One row per maintenance event | `maintenance_key` |
| `fact_financial_transaction` | One row per financial transaction | `financial_transaction_key` |
| `fact_budget` | One row per budget record | `budget_key` |
| `fact_energy` | One row per energy measurement | `energy_key` |
| `fact_emissions` | One row per emissions record | `emissions_key` |
| `fact_waste` | One row per waste record | `waste_key` |
| `fact_inventory` | One row per product, location, and inventory date | `inventory_key` |

`fact_inventory` is a periodic snapshot fact.

---

## 4. Dimension Relationships

### Account → Customer

```text
dim_account 1 ───────< dim_customer
````

* One account can have many customers.
* Each customer belongs to one account.
* Account represents the commercial relationship or organizational grouping.
* Customer represents the customer entity.

---

### Supplier → Product

```text
dim_supplier 1 ───────< dim_product
```

* One supplier can be the primary supplier for many products.
* Each product has one primary supplier in the baseline model.
* A Product–Supplier bridge table is not required.

---

### Location → Employee

```text
dim_location 1 ───────< dim_employee
```

Each employee has one primary operational location.

---

### Location → Machine

```text
dim_location 1 ───────< dim_machine
```

Each machine has one primary operational location.

---

## 5. Fact-to-Dimension Relationships

### Sales

```text
dim_date      1 ───────< fact_sales
dim_account   1 ───────< fact_sales
dim_customer  1 ───────< fact_sales
dim_product   1 ───────< fact_sales
dim_location  1 ───────< fact_sales
```

Foreign keys:

```text
date_key
account_key
customer_key
product_key
location_key
```

`location_key` represents the selling/sales location.

The `account_key` on a sales record must correspond to the account associated with its customer.

---

### Production

```text
dim_date      1 ───────< fact_production
dim_product   1 ───────< fact_production
dim_location  1 ───────< fact_production
dim_machine   1 ───────< fact_production
dim_employee  1 ───────< fact_production
```

Foreign keys:

```text
date_key
product_key
location_key
machine_key
employee_key
```

Employee participation represents the responsible/assigned employee where recorded.

---

### Maintenance

```text
dim_date      1 ───────< fact_maintenance
dim_location  1 ───────< fact_maintenance
dim_machine   1 ───────< fact_maintenance
dim_employee  1 ───────< fact_maintenance
```

Foreign keys:

```text
date_key
location_key
machine_key
employee_key
```

---

### Financial Transactions

```text
dim_date      1 ───────< fact_financial_transaction
dim_location  1 ───────< fact_financial_transaction
```

Foreign keys:

```text
date_key
location_key
```

The financial transaction model remains intentionally simple. A separate chart-of-accounts hierarchy is not part of the baseline model.

---

### Budget

```text
dim_date      1 ───────< fact_budget
dim_location  1 ───────< fact_budget
```

Foreign keys:

```text
date_key
location_key
```

The date represents the applicable budget period.

---

### Energy

```text
dim_date      1 ───────< fact_energy
dim_location  1 ───────< fact_energy
```

Foreign keys:

```text
date_key
location_key
```

---

### Emissions

```text
dim_date      1 ───────< fact_emissions
dim_location  1 ───────< fact_emissions
```

Foreign keys:

```text
date_key
location_key
```

---

### Waste

```text
dim_date      1 ───────< fact_waste
dim_location  1 ───────< fact_waste
```

Foreign keys:

```text
date_key
location_key
```

---

### Inventory

```text
dim_date      1 ───────< fact_inventory
dim_product   1 ───────< fact_inventory
dim_location  1 ───────< fact_inventory
```

Foreign keys:

```text
date_key
product_key
location_key
```

Inventory grain:

```text
Date + Product + Location
```

---

## 6. Machine Date Relationship

Machines also reference the date dimension for their installation date:

```text
dim_date 1 ───────< dim_machine
```

Foreign key:

```text
installation_date_key → dim_date.date_key
```

---

## 7. Conformed Dimensions

The main conformed dimensions are:

| Dimension      | Used By                                                                                |
| -------------- | -------------------------------------------------------------------------------------- |
| `dim_date`     | All facts                                                                              |
| `dim_location` | Sales, Production, Maintenance, Financial, Budget, Energy, Emissions, Waste, Inventory |
| `dim_product`  | Sales, Production, Inventory                                                           |
| `dim_machine`  | Production, Maintenance                                                                |
| `dim_employee` | Production, Maintenance                                                                |

`dim_customer` and `dim_account` primarily support Sales.

`dim_supplier` supports analysis through its relationship with Product.

---

## 8. Cross-Domain Analysis

Facts represent different business processes and therefore must not be joined directly at incompatible grains.

For example:

```text
fact_sales × fact_production
fact_production × fact_maintenance
fact_financial_transaction × fact_budget
```

should not be joined at detailed fact level.

Instead, each fact should first be aggregated to a compatible business grain.

Examples:

```text
Sales + Production
Date + Product + Location
```

```text
Production + Maintenance
Date + Location
```

```text
Financial Transactions + Budget
Budget Period + Location + Category
```

This prevents fan-out and double counting.

---

## 9. Key Rules

* Dimension surrogate keys are used as warehouse primary keys.
* Facts reference dimension surrogate keys.
* Source/business identifiers are retained for traceability.
* Foreign keys must reference valid dimension records after trusted ETL.
* Every fact must maintain its documented grain.
* Relationships must support the approved Atlas business scope.
* No additional bridge tables or hierarchies are introduced unless a genuine analytical requirement is identified.

---

## 10. Approved Model

### Dimensions

```text
dim_date
dim_account
dim_customer
dim_product
dim_supplier
dim_location
dim_employee
dim_machine
```

### Facts

```text
fact_sales
fact_production
fact_maintenance
fact_financial_transaction
fact_budget
fact_energy
fact_emissions
fact_waste
fact_inventory
```

This is the Phase 2 warehouse baseline.

---

## 11. Status

> **Phase 2 — Data Model**
>
> **Detailed specification: Complete**
>
> **Next step: ERD generation and validation**

---

> **Note:** All data used in Project Atlas is synthetic and intended for portfolio and demonstration purposes only.
