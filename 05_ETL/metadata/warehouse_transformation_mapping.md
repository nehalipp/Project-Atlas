# Project Atlas — Warehouse Transformation Mapping

## Purpose

This document defines how Phase 5 Staging datasets are transformed into the approved warehouse-ready dimensions and facts.

The transformation follows:

```text
Staging
   ↓
Warehouse-Ready Transformation
   ↓
PostgreSQL Warehouse
````

The approved warehouse contains 8 dimensions and 9 facts.

---

## Dimensions

| Source                 | Warehouse    | Business Key | Surrogate Key |
| ---------------------- | ------------ | ------------ | ------------- |
| accounts               | dim_account  | account_id   | account_key   |
| customers              | dim_customer | customer_id  | customer_key  |
| products               | dim_product  | product_id   | product_key   |
| suppliers              | dim_supplier | supplier_id  | supplier_key  |
| locations              | dim_location | location_id  | location_key  |
| employees              | dim_employee | employee_id  | employee_key  |
| machines               | dim_machine  | machine_id   | machine_key   |
| Business-process dates | dim_date     | date         | date_key      |

---

## Fact Mapping

### fact_sales

**Grain:** One row represents one sales transaction.

Conformed dimensions:

* Date
* Account
* Customer
* Product
* Location

Source business identifiers are retained.

---

### fact_production

**Grain:** One row represents one production event for a product, machine, employee, location and production date.

Conformed dimensions:

* Date
* Product
* Location
* Machine
* Employee

---

### fact_maintenance

**Grain:** One row represents one maintenance event for a machine, employee, location and maintenance date.

Conformed dimensions:

* Date
* Location
* Machine
* Employee

---

### fact_financial_transaction

**Grain:** One row represents one financial transaction.

Conformed dimensions:

* Date
* Location

---

### fact_budget

**Grain:** One row represents one budget record for a location, category and budget date.

Conformed dimensions:

* Date
* Location

---

### fact_energy

**Grain:** One row represents one energy measurement for a location, energy type and measurement date.

Conformed dimensions:

* Date
* Location

---

### fact_emissions

**Grain:** One row represents one emissions measurement for a location, source and emissions date.

Conformed dimensions:

* Date
* Location

---

### fact_waste

**Grain:** One row represents one waste record for a location, waste type and waste date.

Conformed dimensions:

* Date
* Location

---

### fact_inventory

**Grain:** One row represents one inventory snapshot for a product, location and inventory date.

Conformed dimensions:

* Date
* Product
* Location

---

## Key Principles

1. Source/business identifiers are retained.
2. Warehouse surrogate keys are introduced.
3. Dimension keys are resolved through many-to-one mappings.
4. Fact row counts must remain unchanged.
5. No business fact is joined to another business fact.
6. Conformed dimensions provide cross-domain integration.
7. Fact grain must remain unchanged during transformation.
8. Inventory remains at Date + Product + Location grain.
9. The warehouse-ready layer is prepared for PostgreSQL loading in Phase 6.

---

## Phase Boundary

This transformation does not create PostgreSQL tables.

PostgreSQL implementation belongs to Phase 6 — Warehouse.

````

---

# 11. Run Step 3

Now run:

```bash
python3 05_ETL/scripts/transform_to_warehouse.py
````

The output should start with:

```text
================================================================================
Project Atlas — Phase 5 ETL — Staging to Warehouse-Ready
================================================================================
```

and eventually show:

```text
Dimensions created: 8
Facts created:      9
Warehouse objects:  17
```

---

# 12. Then verify the output

Run:

```bash
find 05_ETL/data/warehouse_ready -type f | sort
```

You should get:

```text
05_ETL/data/warehouse_ready/dim_account.csv
05_ETL/data/warehouse_ready/dim_customer.csv
05_ETL/data/warehouse_ready/dim_date.csv
05_ETL/data/warehouse_ready/dim_employee.csv
05_ETL/data/warehouse_ready/dim_location.csv
05_ETL/data/warehouse_ready/dim_machine.csv
05_ETL/data/warehouse_ready/dim_product.csv
05_ETL/data/warehouse_ready/dim_supplier.csv
05_ETL/data/warehouse_ready/fact_budget.csv
05_ETL/data/warehouse_ready/fact_emissions.csv
05_ETL/data/warehouse_ready/fact_energy.csv
05_ETL/data/warehouse_ready/fact_financial_transaction.csv
05_ETL/data/warehouse_ready/fact_inventory.csv
05_ETL/data/warehouse_ready/fact_maintenance.csv
05_ETL/data/warehouse_ready/fact_production.csv
05_ETL/data/warehouse_ready/fact_sales.csv
05_ETL/data/warehouse_ready/fact_waste.csv
```

---

# 13. One important expectation

The **dimension row counts** should be:

```text
dim_account       1,000
dim_customer     49,509
dim_product       4,951
dim_supplier      1,000
dim_location        100
dim_employee       4,913
dim_machine        1,959
```

`dim_date` will contain every calendar date between the minimum and maximum dates represented in the business facts.

The **fact row counts must remain exactly**:

```text
fact_sales                    466,046
fact_production               181,438
fact_maintenance               46,180
fact_financial_transaction    293,285
fact_budget                    19,445
fact_energy                    97,747
fact_emissions                 97,337
fact_waste                     97,982
fact_inventory                479,167
```

The total business-fact records should therefore remain:

```text
1,745,? 
```

---