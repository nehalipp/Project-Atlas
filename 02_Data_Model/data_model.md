# Project Atlas — Data Model

## 1. Modeling Approach

Project Atlas uses a dimensional **star-schema data warehouse** designed for reusable SQL analytics and downstream Power BI and Tableau reporting.

The approved warehouse baseline contains:

- 8 dimensions
- 9 core fact tables
- 17 warehouse tables

The model uses surrogate warehouse keys, retained source/business identifiers, conformed dimensions, and clearly defined fact grains.

Detailed columns, data types, keys, relationships, and business definitions are maintained in `data_dictionary.xlsx`. The visual relationship model is documented in `atlas_erd.png`.

---

## 2. Dimensions

The warehouse contains:

```text
dim_date
dim_account
dim_customer
dim_product
dim_supplier
dim_location
dim_employee
dim_machine
````

Key business relationships:

```text
dim_account
    1 ──── * dim_customer

dim_supplier
    1 ──── * dim_product

dim_location
    1 ──── * dim_employee

dim_location
    1 ──── * dim_machine
```

Account and Customer remain separate domains. An Account represents the commercial relationship or organizational grouping, while a Customer represents the customer entity associated with an Account.

Each Product has one primary Supplier in the synthetic business model. A separate supplier bridge table is therefore not required.

---

## 3. Fact Tables and Grain

| Fact                         | Grain                                                                          |
| ---------------------------- | ------------------------------------------------------------------------------ |
| `fact_sales`                 | One row per sales transaction, customer, product, location and date            |
| `fact_production`            | One row per production activity, product, machine, employee, location and date |
| `fact_maintenance`           | One row per maintenance event, machine, employee, location and date            |
| `fact_financial_transaction` | One row per financial transaction, account, location, category/type and date   |
| `fact_budget`                | One row per budget allocation, account, location, category and date/period     |
| `fact_energy`                | One row per energy record, machine, location and date                          |
| `fact_emissions`             | One row per emissions record, location, category and date                      |
| `fact_waste`                 | One row per waste record, location, category and date                          |
| `fact_inventory`             | One row per inventory position, product, location and date                     |

Inventory is modeled as a **periodic snapshot fact** at:

```text
Date + Product + Location
```

with the expected business reconciliation:

```text
Opening + Received - Issued = Closing
```

---

## 4. Keys and Relationships

Dimensions use surrogate warehouse keys such as:

```text
date_key
account_key
customer_key
product_key
supplier_key
location_key
employee_key
machine_key
```

Facts use their own warehouse row keys and foreign keys to applicable dimensions.

Source/business identifiers are retained separately from warehouse surrogate keys.

There are **no direct fact-to-fact relationships**.

Cross-domain analysis must use conformed dimensions and compatible aggregation grains to prevent fan-out and double counting.

---

## 5. Conformed Dimensions

The primary conformed dimensions are:

* `dim_date`
* `dim_account`
* `dim_product`
* `dim_location`
* `dim_employee`
* `dim_machine`

These dimensions allow consistent analysis across commercial, operational, financial, inventory, and sustainability processes.

For example:

```text
dim_date
   ├── fact_sales
   ├── fact_production
   ├── fact_maintenance
   ├── fact_financial_transaction
   ├── fact_budget
   ├── fact_energy
   ├── fact_emissions
   ├── fact_waste
   └── fact_inventory
```

---

## 6. Major Modeling Decisions

* Use a dimensional/star-schema warehouse.
* Maintain the approved 8-dimension / 9-fact baseline.
* Keep Account and Customer as separate domains.
* Link Customer to Account.
* Link Product to its primary Supplier.
* Do not introduce a supplier bridge table without a genuine many-to-many requirement.
* Model Inventory as a periodic snapshot.
* Keep Budget separate from Financial Transactions.
* Use conformed dimensions for cross-domain analysis.
* Do not directly join facts at incompatible grains.
* SCD Type 2 and incremental loading are outside the core model unless a genuine analytical requirement later justifies them.
