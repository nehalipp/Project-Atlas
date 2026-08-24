# Phase 7 — Analytics

## Purpose

Phase 7 creates the reusable SQL analytics layer on top of the validated PostgreSQL warehouse from Phase 6.

The objective is to transform warehouse data into consistent, decision-ready business metrics that can be consumed by Power BI and Tableau.

The analytics layer covers commercial performance, customers, products, suppliers, operations, finance, sustainability, inventory, and executive KPIs.

## Analytics Structure

```text
07_Analytics/
├── analytics.md
└── sql/
    ├── sales_analysis.sql
    ├── customer_analysis.sql
    ├── product_analysis.sql
    ├── supplier_analysis.sql
    ├── operations_analysis.sql
    ├── financial_analysis.sql
    ├── sustainability_analysis.sql
    └── executive_kpis.sql
```

## Business Analysis Areas

### Sales

Sales analysis provides:

* Revenue
* Units sold
* Transaction count
* Discount amount
* Revenue trends
* Product category performance
* Location performance
* Customer segment performance

Primary source:

`fact_sales`

### Customer

Customer analysis provides:

* Customer revenue
* Transaction activity
* Units purchased
* Average transaction revenue
* Customer segment performance
* Account-level performance

Primary sources:

`fact_sales`, `dim_customer`, `dim_account`

### Product

Product analysis provides:

* Product revenue
* Units sold
* Average selling price
* Category performance
* Subcategory performance
* Supplier-associated sales

Primary sources:

`fact_sales`, `dim_product`, `dim_supplier`

### Supplier

Supplier analysis provides:

* Products supplied
* Units sold through associated products
* Associated sales revenue
* Supplier category performance

Primary sources:

`dim_supplier`, `dim_product`, `fact_sales`

Supplier revenue is interpreted as sales revenue associated with products supplied by the supplier. It is not treated as a direct measure of supplier financial performance.

### Operations

Operations analysis provides:

* Planned production
* Produced quantity
* Production variance
* Defect quantity
* Production hours
* Maintenance events
* Maintenance hours
* Downtime
* Maintenance cost
* Machine maintenance performance

Primary sources:

`fact_production`, `fact_maintenance`, `dim_machine`, `dim_location`, `dim_date`

### Financial

Financial analysis provides:

* Revenue transactions
* Expense transactions
* Cost transactions
* Transaction amounts
* Financial trends
* Financial categories
* Budget totals

Primary sources:

`fact_financial_transaction`, `fact_budget`, `dim_account`, `dim_location`, `dim_date`

Budget and actual financial transactions are kept as separate analytical concepts. A direct Budget vs Actual category comparison is not defined because the available budget and financial transaction categories do not provide a defensible one-to-one mapping.

### Sustainability

Sustainability analysis provides:

* Energy consumption
* Energy source performance
* Energy by location
* CO2 emissions
* Emissions categories
* Waste quantity
* Waste categories
* Disposal methods

Primary sources:

`fact_energy`, `fact_emissions`, `fact_waste`

The analytics layer also supports cross-domain intensity analysis, such as energy consumption per unit of production.

### Inventory

Inventory analysis provides:

* Opening quantity
* Received quantity
* Issued quantity
* Closing quantity
* Reorder point
* Inventory records at or below reorder point

Primary source:

`fact_inventory`

Inventory is treated as a periodic snapshot. Closing inventory should therefore be interpreted at an appropriate reporting date rather than blindly summed across all historical snapshots.

## KPI Governance

Executive KPIs are centralized in:

`sql/executive_kpis.sql`

The governed KPI groups include:

### Commercial

* Total revenue
* Total units sold
* Total transactions
* Average transaction revenue
* Total discounts

### Operations

* Planned production
* Produced quantity
* Production variance
* Defect quantity
* Production hours
* Maintenance events
* Maintenance hours
* Downtime hours
* Maintenance cost

### Financial

* Financial revenue
* Financial expense
* Financial cost
* Total budget

### Sustainability

* Energy consumption
* CO2 emissions
* Waste quantity

### Inventory

* Closing inventory quantity
* Inventory records at or below reorder point

These definitions are intended to remain consistent when the metrics are consumed in downstream BI tools.

## Fact-Grain Discipline

Atlas contains multiple independent fact tables.

Fact tables are not joined directly to one another at their raw grain when this could create fan-out and double counting.

For cross-domain analysis:

1. Each fact is aggregated independently.
2. The results are brought to a compatible analytical grain.
3. The aggregated datasets are then joined.

For example, monthly production and monthly energy consumption can be combined at the year/month grain to calculate:

`Energy Consumption per Unit Produced`

This approach preserves the original fact grains and prevents inflated measures.

## Data Quality Considerations

The analytics layer does not silently correct unusual business values that were retained through the trusted data process.

For example, production records where produced quantity differs from planned quantity are retained and exposed through production variance metrics.

Financial categories are also preserved as supplied by the warehouse. The analytics layer does not reinterpret ambiguous category combinations without a documented business rule.

## Downstream BI Use

The Phase 7 SQL layer provides the analytical foundation for:

* Power BI
* Tableau

Downstream dashboards should use the governed KPI definitions established in this phase rather than independently redefining core business metrics.

## Validation

All Phase 7 SQL analysis scripts were executed successfully against the PostgreSQL warehouse.

Validated areas include:

* Sales
* Customers
* Products
* Suppliers
* Operations
* Financials
* Sustainability
* Executive KPIs