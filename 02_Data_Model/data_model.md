# Project Atlas — Data Model

## 1. Modeling Approach

Project Atlas uses a **dimensional star-schema data warehouse** designed to support reusable SQL analytics and BI reporting.

The model contains **8 dimension tables and 9 fact tables**, for a total of **17 warehouse tables**. Dimensions provide descriptive business context, while facts capture measurable business processes and events.

The model uses:

* Surrogate warehouse keys for dimensional relationships
* Retained business identifiers for source/business traceability
* Conformed dimensions, especially `dim_date` and `dim_location`
* Explicit fact-table grain
* Separate fact tables for different business processes
* No direct fact-to-fact relationships

Fact tables must be analyzed at compatible grains to prevent fan-out and double counting.

---

## 2. Dimensions

| Dimension      | Purpose                                              | Primary Key    |
| -------------- | ---------------------------------------------------- | -------------- |
| `dim_date`     | Calendar and time analysis                           | `date_key`     |
| `dim_account`  | Commercial accounts and organizational relationships | `account_key`  |
| `dim_customer` | Customer entities and segmentation                   | `customer_key` |
| `dim_product`  | Products, categories, pricing and measurement units  | `product_key`  |
| `dim_supplier` | Supplier information and classification              | `supplier_key` |
| `dim_location` | Facilities, locations and geographic context         | `location_key` |
| `dim_employee` | Workforce and employee attributes                    | `employee_key` |
| `dim_machine`  | Production and operational assets                    | `machine_key`  |

### Key dimensional decisions

* `dim_account` and `dim_customer` remain separate. Customers are associated with commercial accounts through `account_key`.
* `dim_product` contains `unit_of_measure` to identify the measurement basis for product quantities.
* `dim_machine` contains the warehouse surrogate key `machine_key`, business identifier `machine_id`, machine attributes and operating status.
* `dim_location` is shared across commercial, operational and sustainability processes.
* `dim_date` is the conformed calendar dimension used for consistent time analysis.

---

## 3. Fact Tables and Grain

Every fact table has an explicitly defined grain.

| Fact Table                    | Fact Type         | Grain — One Row Represents                                                    |
| ----------------------------- | ----------------- | ----------------------------------------------------------------------------- |
| `fact_sales`                  | Transactional     | One sales transaction for one customer, product, location and date            |
| `fact_production`             | Operational Event | One production activity for one product, machine, employee, location and date |
| `fact_maintenance`            | Operational Event | One maintenance event for one machine, employee, location and date            |
| `fact_financial_transactions` | Transactional     | One financial transaction for one account, location, category/type and date   |
| `fact_budget`                 | Planning          | One budget allocation for one account, location, category and date/period     |
| `fact_energy`                 | Measurement       | One energy consumption record for one machine, location and date              |
| `fact_emissions`              | Measurement       | One emissions record for one location, emissions category and date            |
| `fact_waste`                  | Measurement       | One waste record for one location, waste category and date                    |
| `fact_inventory`              | Periodic Snapshot | One inventory position for one product, location and date                     |

### Measurement-unit design

Measurement units are explicitly documented for quantitative fact tables where the unit is required to interpret the measure.

| Table             | Unit of Measure                                    |
| ----------------- | -------------------------------------------------- |
| `dim_product`     | Product-specific: `Each`, `Kg`, `Liter` or `Meter` |
| `fact_sales`      | Derived from the related product                   |
| `fact_production` | Derived from the related product                   |
| `fact_inventory`  | Derived from the related product                   |
| `fact_energy`     | `kWh`                                              |
| `fact_emissions`  | `kg` CO₂-equivalent                                |
| `fact_waste`      | `kg`                                               |

Financial facts use monetary amounts, while maintenance uses time-based measures such as hours. A generic `unit_of_measure` field is therefore not required for those facts.

---

## 4. Relationships

The warehouse uses one-to-many relationships from dimensions to their related facts.

### Dimension-to-dimension relationships

| Parent         | Child          | Relationship |
| -------------- | -------------- | ------------ |
| `dim_account`  | `dim_customer` | 1:M          |
| `dim_supplier` | `dim_product`  | 1:M          |
| `dim_location` | `dim_employee` | 1:M          |
| `dim_location` | `dim_machine`  | 1:M          |

### Fact relationships

**Sales**

* `dim_date` → `fact_sales`
* `dim_customer` → `fact_sales`
* `dim_product` → `fact_sales`
* `dim_location` → `fact_sales`

**Production**

* `dim_date` → `fact_production`
* `dim_product` → `fact_production`
* `dim_location` → `fact_production`
* `dim_machine` → `fact_production`
* `dim_employee` → `fact_production`

**Maintenance**

* `dim_date` → `fact_maintenance`
* `dim_location` → `fact_maintenance`
* `dim_machine` → `fact_maintenance`
* `dim_employee` → `fact_maintenance`

**Financial Transactions**

* `dim_date` → `fact_financial_transactions`
* `dim_account` → `fact_financial_transactions`
* `dim_location` → `fact_financial_transactions`

**Budget**

* `dim_date` → `fact_budget`
* `dim_account` → `fact_budget`
* `dim_location` → `fact_budget`

**Energy**

* `dim_date` → `fact_energy`
* `dim_location` → `fact_energy`
* `dim_machine` → `fact_energy`

**Emissions**

* `dim_date` → `fact_emissions`
* `dim_location` → `fact_emissions`

**Waste**

* `dim_date` → `fact_waste`
* `dim_location` → `fact_waste`

**Inventory**

* `dim_date` → `fact_inventory`
* `dim_product` → `fact_inventory`
* `dim_location` → `fact_inventory`

There are **no direct fact-to-fact relationships**.

---

## 5. Key and Traceability Strategy

Surrogate keys are used as warehouse relationship keys, while business identifiers are retained for source and business traceability.

Examples include:

* `customer_key` / `customer_id`
* `product_key` / `product_id`
* `supplier_key` / `supplier_id`
* `location_key` / `location_id`
* `employee_key` / `employee_id`
* `machine_key` / `machine_id`
* `sales_key` / `transaction_id`
* `production_key` / `production_id`
* `maintenance_key` / `maintenance_id`

This separates warehouse relationship management from source/business identification.

---

## 6. Major Modeling Decisions

| Decision               | Final Design                           | Rationale                                                                                   |
| ---------------------- | -------------------------------------- | ------------------------------------------------------------------------------------------- |
| Warehouse architecture | Dimensional star schema                | Supports reusable SQL analytics and BI reporting                                            |
| Dimensions             | 8                                      | Covers the required business context without unnecessary complexity                         |
| Facts                  | 9                                      | Covers commercial, operational, financial, planning, inventory and sustainability processes |
| Warehouse tables       | 17                                     | Approved Atlas warehouse baseline                                                           |
| Account → Customer     | 1:M                                    | Customers belong to commercial accounts                                                     |
| Supplier → Product     | 1:M                                    | Products have a primary supplier in the synthetic business model                            |
| Supplier bridge        | Not used                               | No genuine many-to-many requirement                                                         |
| Sales → Account        | Through Customer                       | Avoids redundant account/customer relationships in the sales fact                           |
| Inventory              | Periodic snapshot                      | Represents inventory position over time                                                     |
| Budget                 | Separate fact                          | Keeps planning values separate from financial actuals                                       |
| Date                   | Conformed dimension                    | Enables consistent time analysis                                                            |
| Location               | Conformed dimension                    | Enables consistent operational and sustainability analysis                                  |
| Surrogate keys         | Used                                   | Separates warehouse relationships from business identifiers                                 |
| Business identifiers   | Retained                               | Preserves source/business traceability                                                      |
| Fact-to-fact joins     | Not permitted                          | Prevents fan-out and double counting                                                        |
| SCD Type 2             | Out of core scope                      | Not required for the portfolio scenario                                                     |
| Incremental loading    | Out of core scope                      | Not required for the portfolio implementation                                               |
| Measurement units      | Explicit where analytically meaningful | Keeps quantitative measures interpretable and prevents ambiguity in BI reporting            |

---

## 7. Reference Artifacts

The detailed column-level definitions, data types, key types, nullability and references are maintained in:

`data_dictionary.xlsx`

The visual warehouse structure is maintained in:

`atlas_erd.png`

The data dictionary serves as the detailed column-level reference, while this document explains the model structure, fact grain, relationships and major modeling decisions.