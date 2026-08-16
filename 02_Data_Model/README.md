# Project Atlas — Data Model

## 1. Purpose

The Data Model defines the structure used to transform Atlas operational data into a reliable analytical warehouse.

Project Atlas uses a dimensional/star-schema approach designed to support reporting, cross-domain analysis, and consistent business metrics.

The model is defined before warehouse implementation so that entities, relationships, keys, fact grain, and analytical paths are clearly understood.

---

## 2. Modeling Approach

Atlas follows these modeling principles:

- Dimensional / star-schema modeling
- Conformed dimensions where appropriate
- Surrogate keys for warehouse dimensions
- Source/business identifiers retained for traceability
- Clearly documented grain for every fact
- Compatible aggregation grains for cross-domain analysis
- Simple business relationships without unnecessary enterprise complexity
- No direct joins between incompatible fact grains that could cause fan-out or double counting

The model is designed to be practical, understandable, and suitable for analytical reporting.

---

## 3. Dimensions

Atlas contains eight approved initial warehouse dimensions.

| Dimension | Purpose | Grain |
|---|---|---|
| `dim_date` | Shared calendar and time analysis | One row per calendar date |
| `dim_account` | Commercial relationships and organizational groupings | One row per account |
| `dim_customer` | Customer entities participating in business activity | One row per customer |
| `dim_product` | Products and SKUs used across business processes | One row per product |
| `dim_supplier` | Supplier entities and attributes | One row per supplier |
| `dim_location` | Physical and operational locations | One row per location |
| `dim_employee` | Employees participating in relevant operations | One row per employee |
| `dim_machine` | Production and operational assets | One row per machine |

### Account and Customer

Accounts and Customers are intentionally separate.

- **Account** represents a commercial relationship or organizational grouping.
- **Customer** represents the customer entity participating in business activity and associated with an account.

The relationship remains intentionally simple:

```text
Account
   │
   └──< Customer
````

No unnecessary CRM hierarchy is introduced.

---

## 4. Facts

Atlas contains nine approved initial warehouse facts.

| Fact                         | Grain                                                                                                                        |
| ---------------------------- | ---------------------------------------------------------------------------------------------------------------------------- |
| `fact_sales`                 | One row per sales transaction line for one product, customer, transaction date, and sales location                           |
| `fact_production`            | One row per production activity for one product, location, production date, machine, and responsible employee where recorded |
| `fact_maintenance`           | One row per maintenance event for one machine, location, and maintenance date                                                |
| `fact_financial_transaction` | One row per financial transaction recorded on one transaction date for one location and financial category                   |
| `fact_budget`                | One row per budget record for one budget period, location, and budget category                                               |
| `fact_energy`                | One row per energy measurement for one location, measurement date, and energy type                                           |
| `fact_emissions`             | One row per emissions record for one location, measurement date, and emissions source/category                               |
| `fact_waste`                 | One row per waste record for one location, waste date, and waste type                                                        |
| `fact_inventory`             | One row per inventory position for one product, location, and inventory date                                                 |

Fact grain is a core modeling requirement in Atlas and must remain documented and consistent throughout the project.

---

## 5. Key Relationships

The primary business relationships are:

```text
Account
   │
   └──< Customer
             │
             └──< Sales


Supplier
   │
   └──< Product
             │
             ├──< Sales
             ├──< Production
             └──< Inventory


Location
   ├──< Sales
   ├──< Production
   ├──< Maintenance
   ├──< Financial Transactions
   ├──< Budget
   ├──< Energy
   ├──< Emissions
   ├──< Waste
   ├──< Inventory
   ├──< Employees
   └──< Machines


Machine
   ├──< Production
   └──< Maintenance


Employee
   ├──< Production
   └──< Maintenance


Date
   └──< All time-dependent facts
```

The exact foreign-key relationships and cardinalities are documented separately in the ERD/table relationship specification.

---

## 6. Conformed Dimensions

The primary conformed dimensions are:

| Dimension      | Used Across                                                                                         |
| -------------- | --------------------------------------------------------------------------------------------------- |
| `dim_date`     | All time-dependent facts                                                                            |
| `dim_location` | Sales, Production, Maintenance, Financial Transactions, Budget, Energy, Emissions, Waste, Inventory |
| `dim_product`  | Sales, Production, Inventory                                                                        |
| `dim_machine`  | Production, Maintenance                                                                             |
| `dim_employee` | Production, Maintenance                                                                             |

`dim_customer` and `dim_account` primarily support commercial analysis.

`dim_supplier` supports product and supply-chain analysis through the product relationship.

---

## 7. Key Design Decisions

### Sales Location

`fact_sales.location_key` represents the **selling/sales location**.

A separate fulfillment or shipping location is not included in the baseline model.

### Employee Participation

Employees are included in Production and Maintenance where the operational record identifies the responsible or assigned employee.

### Machine Participation

Production records include `machine_key` because machine-level production analysis is an important part of Atlas.

### Supplier Relationship

Each product has one **primary supplier** in the baseline model.

The relationship is:

```text
Supplier 1 ───────< Product
```

A many-to-many supplier/product bridge is not included because it is not currently required by the analytical scope.

### Financial Transactions

Financial Transactions remain intentionally simple.

The baseline captures:

* Transaction date
* Location
* Transaction type
* Financial category
* Description
* Amount

A separate chart-of-accounts hierarchy is not introduced.

### Inventory

`fact_inventory` is modeled as a **periodic snapshot fact**.

Its grain is the inventory position of a product at a location on a specific inventory date.

---

## 8. Keys

Warehouse dimensions use surrogate keys as their primary warehouse identifiers.

Business/source identifiers are retained for source traceability.

The general pattern is:

```text
Dimension
   │
   ├── Surrogate Key
   └── Business / Source Identifier
```

Fact tables reference the appropriate dimension surrogate keys.

The exact column names, data types, constraints, and foreign-key definitions are maintained in the detailed data-model specification.

---

## 9. Cross-Domain Analysis

Cross-domain analysis is a core capability of Atlas.

The model supports analytical paths such as:

### Commercial

```text
Account
   ↓
Customer
   ↓
Sales
   ↓
Product
   ↓
Location
```

### Production and Maintenance

```text
Location
   ↓
Machine
   ├── Production
   └── Maintenance
```

### Production and Sustainability

```text
Location
   ├── Production
   ├── Energy
   └── Emissions
```

### Sales and Inventory

```text
Product
   ├── Sales
   └── Inventory
```

### Financial and Budget

```text
Location
   ├── Financial Transactions
   └── Budget
```

Cross-domain analysis must respect the grain of each fact.

---

## 10. Grain and Fan-Out Control

Atlas facts represent different business processes and therefore do not necessarily share the same grain.

The following principles apply:

1. Every fact has one clearly defined grain.
2. Incompatible fact tables are not directly joined at detailed grain.
3. Facts are aggregated to a compatible analytical grain before comparison.
4. Conformed dimensions are used to connect business processes where appropriate.
5. Measures are aggregated only at a level that preserves their business meaning.

For example, detailed Sales and Production records should not be directly joined and then summed.

Instead:

```text
Sales
   ↓
Aggregate to compatible grain
   ↓
Compare
   ↑
Aggregate to compatible grain
   ↑
Production
```

This prevents fan-out and double counting.

---

## 11. Approved Warehouse Baseline

### Dimensions

1. `dim_date`
2. `dim_account`
3. `dim_customer`
4. `dim_product`
5. `dim_supplier`
6. `dim_location`
7. `dim_employee`
8. `dim_machine`

### Facts

1. `fact_sales`
2. `fact_production`
3. `fact_maintenance`
4. `fact_financial_transaction`
5. `fact_budget`
6. `fact_energy`
7. `fact_emissions`
8. `fact_waste`
9. `fact_inventory`

This baseline represents the approved initial warehouse model for Project Atlas.

Additional dimensions or facts will not be introduced unless a genuine analytical requirement justifies the change.

---

## 12. Phase 2 Artifacts

The Data Model phase will produce:

* Data model documentation
* Detailed dimension and fact specifications
* Fact-to-dimension relationships
* Cardinality definitions
* Fact grain definitions
* ERD/table relationship specification
* Final Entity Relationship Diagram

The ERD will be created only after the detailed relationship specification has been validated.

---

## 13. Phase 2 Status

> **Phase 2 — Data Model**
> **Status:** In Progress

The conceptual model, dimensions, facts, grain, key strategy, and major relationship decisions have been established.

The next step is to create and validate the detailed **ERD/table relationship specification**, including:

* Exact table relationships
* Primary keys
* Foreign keys
* Cardinalities
* Dimension-to-fact mappings
* Dimension-to-dimension relationships
* Relationship assumptions and business rules

The ERD will then be generated from the specification.

---

> **Note:** All data used in Project Atlas is synthetic and intended for portfolio and demonstration purposes only.
