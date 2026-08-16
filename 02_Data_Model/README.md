# Project Atlas — Data Model

## 1. Purpose

The Data Model defines the structure used to transform Atlas operational data into a reliable analytical warehouse.

Project Atlas uses a dimensional/star-schema approach designed to support reporting, cross-domain analysis, and consistent business metrics.

The model is designed before warehouse implementation so that entity relationships, fact grain, keys, and analytical paths are clearly understood.

---

## 2. Modeling Approach

Atlas uses:

- Dimensional / star-schema modeling
- Conformed dimensions where appropriate
- Surrogate keys for warehouse entities
- Source/business identifiers retained for traceability
- Clearly documented fact grain
- Compatible aggregation grains for cross-domain analysis

The model is designed to support analytical queries without creating unnecessary complexity.

A key principle is to avoid directly joining fact tables at incompatible grains, which can result in fan-out and double counting.

---

## 3. Dimensions

The approved initial warehouse dimensions are:

| Dimension | Purpose |
|---|---|
| `dim_date` | Shared calendar and time analysis |
| `dim_account` | Commercial relationships and organizational groupings |
| `dim_customer` | Customer entities and customer attributes |
| `dim_product` | Products, SKUs, and product categories |
| `dim_supplier` | Supplier entities and supplier attributes |
| `dim_location` | Plants, warehouses, stores, offices, and facilities |
| `dim_employee` | Employees participating in business operations |
| `dim_machine` | Production and operational assets |

### Dimension Roles

#### `dim_date`

Provides a common time dimension for time-based analysis across business processes.

#### `dim_account`

Represents the commercial relationship or organizational grouping.

An account is intentionally separate from a customer.

#### `dim_customer`

Represents the customer entity participating in business activity and associated with an account.

The Account → Customer relationship is intentionally kept simple.

#### `dim_product`

Represents products or SKUs used across relevant business processes such as sales, production, and inventory.

#### `dim_supplier`

Represents suppliers and their business attributes.

#### `dim_location`

Represents the physical or operational location where relevant business activity occurs.

#### `dim_employee`

Represents employees who participate in relevant operational activities.

#### `dim_machine`

Represents production or operational assets used in relevant business processes.

---

## 4. Fact Tables

The approved initial warehouse facts are:

| Fact | Grain |
|---|---|
| `fact_sales` | One row represents one sales transaction line for one product on one transaction date. |
| `fact_production` | One row represents one production activity for one product at one location on one production date. |
| `fact_maintenance` | One row represents one maintenance event for one machine at one location on one maintenance date. |
| `fact_financial_transaction` | One row represents one financial transaction recorded on one transaction date. |
| `fact_budget` | One row represents one budget record for one budget period, location, and budget category. |
| `fact_energy` | One row represents one energy measurement for one location on one measurement date and energy type. |
| `fact_emissions` | One row represents one emissions record for one location on one measurement date and emissions source/category. |
| `fact_waste` | One row represents one waste record for one location on one waste date and waste type/disposal category. |
| `fact_inventory` | One row represents the inventory position of one product at one location on one inventory date. |

> **Fact grain is a hard modeling requirement in Atlas. The grain must be understood and documented before implementing the corresponding warehouse table.**

---

## 5. Key Relationships

The model is designed around the following major business relationships:

```text
Account
   │
   └── Customer

Supplier
   │
   └── Product

Location
   ├── Production
   ├── Maintenance
   ├── Inventory
   ├── Financial Transactions
   ├── Budget
   ├── Energy
   ├── Emissions
   └── Waste

Product
   ├── Sales
   ├── Production
   └── Inventory

Machine
   ├── Production
   └── Maintenance

Employee
   ├── Production
   └── Maintenance

Date
   └── Time-dependent business facts
````

These relationships represent the intended analytical structure. Exact foreign-key implementation will be finalized with the physical warehouse design.

---

## 6. Conformed Dimensions

The following dimensions are expected to be shared across multiple business processes:

| Dimension      | Primary Analytical Use                                         |
| -------------- | -------------------------------------------------------------- |
| `dim_date`     | Time-based analysis across the platform                        |
| `dim_location` | Location-level operational and financial analysis              |
| `dim_product`  | Product-level analysis across sales, production, and inventory |
| `dim_machine`  | Machine-level production and maintenance analysis              |
| `dim_employee` | Employee-level operational analysis                            |

Customer and account dimensions primarily support commercial analysis, while supplier primarily supports supply-chain-related analysis.

The final usage of each dimension will follow the actual grain and business meaning of the associated facts.

---

## 7. Cross-Domain Analysis

Cross-domain analysis is a core capability of Atlas.

Examples include:

### Production + Maintenance

Analyze production performance alongside machine maintenance activity and downtime.

### Production + Energy

Compare production output with energy consumption at a compatible aggregation grain.

### Production + Emissions

Analyze operational output alongside emissions.

### Sales + Production + Inventory

Compare demand, production activity, and inventory position.

### Revenue + Costs + Budget

Compare actual financial activity with planned budget performance.

Cross-domain analysis must be performed at a compatible aggregation grain.

For example, detailed sales transactions should not be directly joined to detailed production records and then aggregated, because this can multiply rows and produce incorrect results.

---

## 8. Grain and Fan-Out Control

Fact tables represent different business processes and therefore do not necessarily have the same grain.

Atlas follows these rules:

1. Each fact has one clearly defined grain.
2. Facts are not directly joined when their grains are incompatible.
3. Facts are aggregated to a compatible grain before cross-domain comparison.
4. Shared dimensions are used to connect business processes where appropriate.
5. Measures must be aggregated only at a level that preserves their business meaning.

This approach prevents fan-out and double counting in SQL analytics and BI models.

---

## 9. Keys

Warehouse dimensions will use surrogate keys where appropriate.

Business/source identifiers will also be retained to provide traceability back to the source data.

The general pattern is:

```text
Dimension
    │
    ├── Surrogate Key
    └── Business / Source Identifier
```

Fact tables will reference the appropriate dimension surrogate keys.

Exact column names, data types, constraints, and indexes will be finalized during the warehouse implementation phase.

---

## 10. Data Model Scope

The approved baseline contains:

**8 Dimensions**

* `dim_date`
* `dim_account`
* `dim_customer`
* `dim_product`
* `dim_supplier`
* `dim_location`
* `dim_employee`
* `dim_machine`

**9 Core Facts**

* `fact_sales`
* `fact_production`
* `fact_maintenance`
* `fact_financial_transaction`
* `fact_budget`
* `fact_energy`
* `fact_emissions`
* `fact_waste`
* `fact_inventory`

No additional dimension or fact table will be added unless a genuine analytical requirement justifies it.

---

## 11. ERD

The Entity Relationship Diagram for the approved data model is maintained in:

```text
02_Data_Model/erd/project_atlas_erd.png
```

The ERD and this document must remain consistent with the approved data model.

---

## 12. Phase 2 Status

> **Phase 2 — Data Model**
> **Status:** In Progress

This phase establishes the dimensions, facts, relationships, keys, conformed dimensions, and fact grain required for the Atlas warehouse.

The next step after the data model is finalized is:

> **Phase 3 — Data Generation**

Synthetic source datasets will be generated only after the data model and its important relationships have been finalized.

---

> **Note:** All data used in Project Atlas is synthetic and intended for portfolio and demonstration purposes only.
