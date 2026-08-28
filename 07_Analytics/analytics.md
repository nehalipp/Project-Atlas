# Phase 7 — Analytics

## Purpose

Phase 7 creates the reusable SQL analytics layer on top of the validated PostgreSQL data warehouse from Phase 6.

The objective is to transform warehouse data into consistent, decision-ready business metrics that can be consumed by Power BI and Tableau.

The analytics layer covers:

* Commercial performance
* Customer performance
* Product performance
* Supplier performance
* Operations
* Finance
* Sustainability
* Inventory
* Executive KPIs

The Phase 7 analytics layer preserves the dimensional model and fact-grain discipline established in the warehouse.

---

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

The SQL layer intentionally uses eight analysis scripts aligned with the primary business domains.

---

# Business Analysis Areas

## Sales

Sales analysis provides:

* Revenue
* Quantity sold
* Transaction count
* Discount amount
* Revenue trends
* Product category performance
* Location performance
* Customer segment performance
* Sales performance by unit of measure

Primary source:

`fact_sales`

Supporting dimensions:

* `dim_date`
* `dim_customer`
* `dim_product`
* `dim_location`

### Unit-of-Measure Governance

Sales quantities are not treated as one universal quantity because Atlas contains multiple measurement units.

The current warehouse supports units including:

* Each
* Kg
* Liter
* Meter

Quantity-based sales metrics are therefore reported by `unit_of_measure`.

Revenue and transaction metrics may be aggregated independently because they are not dependent on the physical measurement unit.

---

## Customer

Customer analysis provides:

* Customer revenue
* Transaction activity
* Quantity purchased
* Average transaction revenue
* Customer segment performance
* Account-level performance
* Customer performance by unit of measure

Primary sources:

`fact_sales`, `dim_customer`, `dim_account`

Customer quantity metrics are reported by unit of measure to avoid combining physically different quantities.

---

## Product

Product analysis provides:

* Product revenue
* Quantity sold
* Average selling price
* Category performance
* Subcategory performance
* Supplier-associated sales
* Product performance by unit of measure

Primary sources:

`fact_sales`, `dim_product`, `dim_supplier`

The product dimension provides the governing unit of measure for product-level quantity interpretation.

---

## Supplier

Supplier analysis provides:

* Products supplied
* Quantity sold through associated products
* Associated sales revenue
* Supplier category performance
* Supplier-associated sales by unit of measure

Primary sources:

`dim_supplier`, `dim_product`, `fact_sales`

Supplier revenue is interpreted as **sales revenue associated with products supplied by the supplier**.

It is not treated as a direct measure of supplier financial performance.

Quantity metrics are reported by unit of measure.

---

# Operations

## Production

Operations analysis provides:

* Planned production
* Produced quantity
* Production variance
* Production achievement percentage
* Defect quantity
* Production hours
* Production by location
* Production by product

Primary sources:

`fact_production`, `dim_product`, `dim_location`, `dim_date`

Production quantities are reported by `unit_of_measure`.

Production achievement is calculated within the same unit:

`Produced Quantity / Planned Quantity`

This prevents quantities measured in different units from being combined into a single production KPI.

---

## Maintenance

Maintenance analysis provides:

* Maintenance events
* Maintenance hours
* Downtime hours
* Maintenance cost
* Monthly maintenance performance
* Machine maintenance performance

Primary sources:

`fact_maintenance`, `dim_machine`, `dim_location`, `dim_date`

Maintenance hours, downtime hours, and maintenance cost are independent of product quantity units and can therefore be aggregated directly.

---

# Financial

Financial analysis provides:

* Revenue transactions
* Expense transactions
* Cost transactions
* Transaction amounts
* Financial trends
* Financial categories
* Budget totals
* Budget category performance

Primary sources:

`fact_financial_transaction`, `fact_budget`, `dim_account`, `dim_location`, `dim_date`

Financial transaction amounts are treated as monetary values and are therefore independent of the physical units used by sales, production, inventory, or waste.

### Budget and Actuals

Budget and actual financial transactions remain separate analytical concepts.

A direct Budget vs Actual category comparison is **not defined** because the available budget and financial transaction categories do not provide a defensible one-to-one mapping.

The analytics layer therefore does not manufacture a Budget vs Actual relationship where the source data does not support one.

---

# Sustainability

Sustainability analysis provides:

* Energy consumption
* Energy source performance
* Energy by location
* CO2 emissions
* Emissions categories
* Waste quantity
* Waste categories
* Disposal methods
* Monthly sustainability trends

Primary sources:

`fact_energy`, `fact_emissions`, `fact_waste`

## Measurement Units

Atlas explicitly records measurement units for sustainability metrics.

Energy consumption is measured in:

`kWh`

CO2 emissions are measured in:

`kg`

Waste quantity is analyzed using its explicit `unit_of_measure`.

Sustainability quantity metrics are therefore not combined across incompatible units.

---

# Inventory

Inventory analysis provides:

* Opening quantity
* Received quantity
* Issued quantity
* Closing quantity
* Reorder point
* Inventory records at or below reorder point
* Closing inventory by unit of measure

Primary source:

`fact_inventory`

## Inventory Grain

Inventory is treated as a **periodic snapshot fact**.

Closing inventory represents the inventory position recorded for a reporting date.

Historical inventory snapshots must therefore **not be blindly summed across all dates**.

For executive reporting, closing inventory is evaluated using the latest available reporting date and is grouped by unit of measure.

This preserves the meaning of inventory as a point-in-time business measure.

---

# KPI Governance

Executive KPIs are centralized in:

`sql/executive_kpis.sql`

The governed KPI groups include the following.

## Commercial

* Total revenue
* Total transactions
* Average transaction revenue
* Total discounts
* Quantity sold by unit of measure

A universal `Total Units Sold` KPI is intentionally not defined because the warehouse contains multiple physical measurement units.

---

## Operations

* Planned production by unit
* Produced quantity by unit
* Production variance by unit
* Production achievement percentage by unit
* Defect quantity by unit
* Production hours
* Maintenance events
* Maintenance hours
* Downtime hours
* Maintenance cost

Production achievement is calculated within the same measurement unit.

---

## Financial

* Financial revenue
* Financial expense
* Financial cost
* Total budget

---

## Sustainability

* Energy consumption in kWh
* CO2 emissions in kg
* Waste quantity by unit of measure

---

## Inventory

* Latest closing inventory quantity by unit
* Inventory records at or below reorder point by unit

Inventory KPIs use the latest available inventory snapshot rather than summing historical snapshots.

---

# Fact-Grain Discipline

Atlas contains multiple independent fact tables.

Fact tables are not joined directly to one another at their raw grain when doing so could create fan-out and double counting.

For cross-domain analysis:

1. Each fact is aggregated independently.
2. The results are brought to a compatible analytical grain.
3. The aggregated datasets are then joined where appropriate.

For example, monthly energy consumption can be analyzed alongside monthly production by first aggregating each fact independently at the year/month grain.

Where production quantities are involved, the `unit_of_measure` must also remain part of the compatible analytical grain.

This approach preserves the original fact grains and prevents inflated measures.

---

# Data Quality Considerations

The analytics layer does not silently correct unusual business values that were retained through the trusted data process.

For example, production records where produced quantity differs from planned quantity are retained and exposed through production variance and production achievement metrics.

The analytics layer does not remove unusual operational observations merely because they differ from expectations.

Financial categories are preserved as supplied by the warehouse.

The analytics layer does not reinterpret ambiguous category combinations without a documented business rule.

---

# Unit-of-Measure Governance

Unit of measure is an explicit analytical consideration in Atlas.

The following principles apply:

1. Quantity measures must retain their associated unit.
2. Quantities with different physical units must not be summed into a single KPI.
3. Quantity-based comparisons should occur within the same unit.
4. Revenue and transaction counts may be aggregated independently of physical quantity units.
5. Inventory quantities must retain their unit and reporting date.
6. Sustainability metrics must retain their defined measurement units.
7. Cross-domain ratios involving quantity must only be calculated when the numerator and denominator have compatible units.

This governance prevents dimensionally invalid KPIs from entering downstream BI dashboards.

---

# Downstream BI Use

The Phase 7 SQL layer provides the analytical foundation for:

* Power BI
* Tableau

Downstream dashboards should use the governed KPI definitions established in this phase rather than independently redefining core business metrics.

Where a KPI is quantity-based, the corresponding `unit_of_measure` should remain available in the semantic model.

This ensures that dashboard metrics remain consistent with the warehouse and analytics layer.

---

# Validation

All Phase 7 SQL analysis scripts were executed successfully against the PostgreSQL warehouse.

Validated analysis areas include:

* Sales
* Customers
* Products
* Suppliers
* Operations
* Financials
* Sustainability
* Executive KPIs

Validation confirmed that:

* The SQL scripts execute successfully.
* The updated warehouse columns are referenced correctly.
* Quantity metrics respect unit-of-measure boundaries.
* Production achievement is calculated within compatible units.
* Inventory is treated as a periodic snapshot.
* Sustainability metrics retain their defined measurement units.
* Financial analysis remains independent of physical quantity units.
* Cross-domain analysis avoids direct raw-grain fact-to-fact joins.

---

# Final Phase 7 Deliverables

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

Phase 7 establishes the governed SQL analytics layer used by the downstream BI applications.