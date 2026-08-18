# Project Atlas — KPI Catalog

## 1. Purpose

This document is the governed KPI reference for Project Atlas.

It defines the business meaning, calculation logic, analytical grain, source data, and interpretation of important metrics used across the Atlas analytics layer.

These definitions are intended to remain consistent across:

- PostgreSQL analytics
- Power BI
- Tableau
- Documentation
- Business insights
- Interview explanations

Project Atlas uses synthetic data. KPI values represent analytical results from the synthetic warehouse and must not be interpreted as real-world business results.

---

# 2. KPI Governance Principles

The following principles govern Atlas metrics:

1. Each important KPI has one governed definition.
2. KPI calculations must be traceable to the PostgreSQL warehouse.
3. Power BI and Tableau must consume the same governed business definitions.
4. Equivalent SQL, Power BI, and Tableau contexts must reconcile.
5. Cross-domain KPIs must respect fact-table grain.
6. Facts must be aggregated to a compatible analytical grain before cross-domain combination.
7. Division-by-zero conditions must return NULL rather than misleading values.
8. Analytical estimates must not be presented as actual financial results.
9. Synthetic results must not be represented as real-world business impact.
10. KPI definitions must remain explainable in business terms.

---

# 3. Analytical Layers

Atlas analytics is organized into three layers.

## 3.1 KPI Analytics

Reusable daily KPI views providing standardized business measures by date and applicable analytical dimensions.

Examples:

- Sales KPIs
- Production KPIs
- Maintenance KPIs
- Financial KPIs
- Budget KPIs
- Energy KPIs
- Emissions KPIs
- Waste KPIs
- Inventory KPIs

## 3.2 Domain Analytics

Reusable analytical views providing domain-specific performance analysis.

Examples:

- Account sales
- Customer sales
- Product sales
- Supplier sales
- Location sales
- Production performance
- Machine production
- Maintenance performance
- Employee operations
- Financial performance
- Budget performance
- Energy performance
- Emissions performance
- Waste performance
- Inventory position

## 3.3 Cross-Domain Analytics

Cross-domain views combine independently aggregated facts at compatible analytical grains.

Current governed cross-domain views:

1. Sales + Production + Inventory
2. Production + Maintenance
3. Production + Energy + Emissions

---

# 4. Commercial KPIs

## 4.1 Total Revenue

**Business definition**

Total recognized sales revenue represented in the synthetic sales fact.

**Calculation**

```text
SUM(fact_sales.revenue)
````

**Primary source**

```text
fact_sales.revenue
```

**Primary analytics view**

```text
analytics.vw_sales_kpis_daily
```

**Cross-domain availability**

```text
analytics.vw_sales_production_inventory_daily
```

**Unit**

Currency units.

**Interpretation**

Measures the total sales revenue represented by the selected analytical context.

---

## 4.2 Sales Quantity

**Business definition**

Total quantity sold in the selected analytical context.

**Calculation**

```text
SUM(fact_sales.quantity)
```

**Primary source**

```text
fact_sales.quantity
```

**Primary analytics view**

```text
analytics.vw_sales_kpis_daily
```

**Cross-domain availability**

```text
analytics.vw_sales_production_inventory_daily
```

**Unit**

Product units.

---

## 4.3 Sales Transaction Count

**Business definition**

Number of distinct sales transactions.

**Calculation**

```text
COUNT(DISTINCT fact_sales.sales_id)
```

**Primary source**

```text
fact_sales.sales_id
```

**Interpretation**

Measures transaction activity rather than revenue value.

---

## 4.4 Average Discount Rate

**Business definition**

Average transaction discount rate within the selected analytical context.

**Calculation**

```text
AVG(fact_sales.discount_rate)
```

**Primary source**

```text
fact_sales.discount_rate
```

**Interpretation**

Provides an indication of the discount level applied across sales transactions.

---

## 4.5 Revenue per Unit

**Business definition**

Average revenue generated per unit sold.

**Calculation**

```text
Total Revenue / Sales Quantity
```

or:

```text
SUM(fact_sales.revenue)
/
NULLIF(SUM(fact_sales.quantity), 0)
```

**Interpretation**

Provides a normalized revenue measure that can support product, customer, account, and location analysis.

---

# 5. Production KPIs

## 5.1 Planned Production Quantity

**Business definition**

Total production quantity planned in the selected analytical context.

**Calculation**

```text
SUM(fact_production.planned_quantity)
```

---

## 5.2 Production Quantity

**Business definition**

Total quantity actually produced.

**Calculation**

```text
SUM(fact_production.quantity_produced)
```

**Primary source**

```text
fact_production.quantity_produced
```

**Primary analytics view**

```text
analytics.vw_production_kpis_daily
```

**Cross-domain views**

```text
analytics.vw_sales_production_inventory_daily
analytics.vw_production_maintenance_daily
analytics.vw_production_energy_emissions_daily
```

---

## 5.3 Production Attainment Rate

**Business definition**

Percentage of planned production quantity that was actually produced.

**Calculation**

```text
Production Quantity / Planned Production Quantity
```

or:

```text
SUM(quantity_produced)
/
NULLIF(SUM(planned_quantity), 0)
```

**Interpretation**

A value of `1.00` represents 100% attainment.

Values below `1.00` indicate production below the planned quantity.

Values above `1.00` indicate production above the planned quantity.

This is a descriptive operational KPI.

---

## 5.4 Production Hours

**Business definition**

Total production hours recorded in the selected analytical context.

**Calculation**

```text
SUM(fact_production.production_hours)
```

---

## 5.5 Production Rate

**Business definition**

Production quantity produced per production hour.

**Calculation**

```text
Production Quantity / Production Hours
```

or:

```text
SUM(quantity_produced)
/
NULLIF(SUM(production_hours), 0)
```

**Unit**

Production units per production hour.

---

## 5.6 Production Record Count

**Business definition**

Number of distinct production records.

**Calculation**

```text
COUNT(DISTINCT fact_production.production_id)
```

---

# 6. Maintenance KPIs

## 6.1 Maintenance Cost

**Business definition**

Total maintenance cost recorded in the selected analytical context.

**Calculation**

```text
SUM(fact_maintenance.maintenance_cost)
```

**Primary source**

```text
fact_maintenance.maintenance_cost
```

**Primary analytics view**

```text
analytics.vw_maintenance_kpis_daily
```

**Cross-domain view**

```text
analytics.vw_production_maintenance_daily
```

---

## 6.2 Maintenance Event Count

**Business definition**

Number of distinct maintenance events.

**Calculation**

```text
COUNT(DISTINCT fact_maintenance.maintenance_id)
```

---

## 6.3 Downtime Hours

**Business definition**

Total machine downtime associated with maintenance records.

**Calculation**

```text
SUM(fact_maintenance.downtime_hours)
```

---

## 6.4 Average Maintenance Cost per Event

**Business definition**

Average maintenance cost associated with each maintenance event.

**Calculation**

```text
Maintenance Cost / Maintenance Event Count
```

or:

```text
SUM(maintenance_cost)
/
NULLIF(COUNT(DISTINCT maintenance_id), 0)
```

---

## 6.5 Maintenance Cost per Produced Unit

**Business definition**

Maintenance cost normalized by production quantity at a compatible analytical context.

**Calculation**

```text
Maintenance Cost / Production Quantity
```

**Important**

This KPI is primarily used in the Production + Maintenance cross-domain analysis.

It must not be calculated by joining raw production and maintenance records at event level.

The two facts are independently aggregated to:

```text
Date + Location + Machine
```

before combination.

---

## 6.6 Downtime-to-Production-Hours Ratio

**Business definition**

Maintenance downtime relative to production hours.

**Calculation**

```text
Downtime Hours / Production Hours
```

**Interpretation**

This is a descriptive operational ratio.

It should not be interpreted as a causal measure of production loss.

---

# 7. Financial KPIs

## 7.1 Financial Transaction Amount

**Business definition**

Total financial transaction amount recorded in the financial transaction fact.

**Calculation**

```text
SUM(fact_financial_transaction.amount)
```

---

## 7.2 Revenue Transaction Amount

**Business definition**

Financial transaction amount where transaction type is `Revenue`.

**Calculation**

```text
SUM(amount)
WHERE transaction_type = 'Revenue'
```

---

## 7.3 Expense Transaction Amount

**Business definition**

Financial transaction amount where transaction type is `Expense`.

**Calculation**

```text
SUM(amount)
WHERE transaction_type = 'Expense'
```

---

## 7.4 Transfer Amount

**Business definition**

Financial transaction amount where transaction type is `Transfer`.

**Calculation**

```text
SUM(amount)
WHERE transaction_type = 'Transfer'
```

---

## 7.5 Adjustment Amount

**Business definition**

Financial transaction amount where transaction type is `Adjustment`.

**Calculation**

```text
SUM(amount)
WHERE transaction_type = 'Adjustment'
```

---

# 8. Budget KPIs

## 8.1 Budget Amount

**Business definition**

Total budget amount recorded in the budget fact.

**Calculation**

```text
SUM(fact_budget.budget_amount)
```

---

## 8.2 Budget by Category

**Business definition**

Budget amount grouped by the budget category.

**Calculation**

```text
SUM(budget_amount)
GROUP BY category
```

Current categories include:

* Maintenance
* Energy
* Production
* Administration
* Supply Chain
* Operations

---

## 8.3 Budget-to-Actual Limitation

Atlas currently does **not** define a governed Budget vs Actual KPI.

The reason is that:

* `fact_budget` contains budget categories.
* `fact_financial_transaction` contains transaction types.
* The current warehouse does not establish a governed category mapping between the two.

Therefore, Atlas must not claim a direct Budget vs Actual variance unless a defensible mapping is explicitly introduced in a future approved project decision.

This is a deliberate analytical governance decision.

---

# 9. Energy KPIs

## 9.1 Energy Consumption

**Business definition**

Total energy consumption represented in the selected analytical context.

For the current Atlas dataset, energy consumption is reconciled using records where:

```text
unit = 'kWh'
```

**Calculation**

```text
SUM(fact_energy.consumption)
WHERE unit = 'kWh'
```

**Primary analytics view**

```text
analytics.vw_energy_kpis_daily
```

---

## 9.2 Energy Consumption by Energy Type

**Business definition**

Energy consumption grouped by energy type.

Current energy types include:

* Electricity
* Natural Gas
* Diesel
* Steam

**Calculation**

```text
SUM(consumption)
GROUP BY energy_type
```

---

## 9.3 Energy Intensity

**Business definition**

Energy consumption normalized by production quantity.

**Calculation**

```text
Energy Consumption (kWh)
/
Production Quantity
```

**Unit**

kWh per production unit.

**Primary cross-domain view**

```text
analytics.vw_production_energy_emissions_daily
```

**Important**

Energy intensity is a descriptive analytical measure.

It does not establish that energy consumption caused changes in production output.

---

# 10. Emissions KPIs

## 10.1 CO2 Emissions

**Business definition**

Total CO₂ emissions recorded in the emissions fact.

**Calculation**

```text
SUM(fact_emissions.co2_kg)
```

**Unit**

kg CO₂.

---

## 10.2 CO2 Emissions by Source

**Business definition**

CO₂ emissions grouped by emissions source.

Current sources include:

* Electricity
* Process
* Fuel
* Natural Gas

**Calculation**

```text
SUM(co2_kg)
GROUP BY source
```

---

## 10.3 Emissions Intensity

**Business definition**

CO₂ emissions normalized by production quantity.

**Calculation**

```text
CO2 Emissions (kg)
/
Production Quantity
```

**Unit**

kg CO₂ per production unit.

**Primary cross-domain view**

```text
analytics.vw_production_energy_emissions_daily
```

**Important**

Emissions intensity is a descriptive analytical measure and does not establish causality.

---

# 11. Waste KPIs

## 11.1 Waste Quantity

**Business definition**

Total waste quantity in the selected analytical context.

For the current Atlas dataset, the reconciled warehouse measure uses:

```text
unit = 'kg'
```

**Calculation**

```text
SUM(fact_waste.quantity)
WHERE unit = 'kg'
```

**Unit**

kg.

---

## 11.2 Waste by Type

**Business definition**

Waste quantity grouped by waste type.

Current waste types include:

* Chemical
* Metal
* Paper
* Plastic
* General

---

## 11.3 Waste by Disposal Method

**Business definition**

Waste quantity grouped by disposal method.

Current disposal methods include:

* Recycling
* Reuse
* Treatment
* Landfill

---

# 12. Inventory KPIs

## 12.1 Quantity on Hand

**Business definition**

Inventory quantity available at the selected inventory snapshot.

**Calculation**

```text
SUM(fact_inventory.quantity_on_hand)
```

**Primary analytics view**

```text
analytics.vw_inventory_kpis_daily
```

**Cross-domain view**

```text
analytics.vw_sales_production_inventory_daily
```

---

## 12.2 Inventory Value

**Business definition**

Total inventory value represented by inventory records.

**Calculation**

```text
SUM(fact_inventory.inventory_value)
```

---

## 12.3 Reorder Point

**Business definition**

Inventory reorder threshold recorded for the selected analytical context.

**Calculation**

```text
MAX(reorder_point)
```

when evaluated at the governed product/location/date grain.

---

## 12.4 Below Reorder Point

**Business definition**

Boolean indicator showing whether quantity on hand is below the applicable reorder point.

**Calculation**

```text
quantity_on_hand < reorder_point
```

---

## 12.5 Inventory-to-Daily-Sales Ratio

**Business definition**

Inventory quantity relative to sales quantity at the same date/location/product analytical grain.

**Calculation**

```text
Quantity on Hand / Sales Quantity
```

**Important**

This metric is not defined as "days of inventory."

No days-of-supply claim should be made because the metric does not use a governed multi-day demand window.

---

# 13. Cross-Domain KPIs

## 13.1 Production Minus Sales Quantity

**Domains**

Sales + Production + Inventory

**Analytical grain**

```text
Date + Location + Product
```

**Calculation**

```text
Production Quantity - Sales Quantity
```

**Interpretation**

Shows the difference between production output and sales quantity at the same analytical grain.

---

## 13.2 Production Attainment Rate

**Domains**

Sales + Production + Inventory

**Analytical grain**

```text
Date + Location + Product
```

**Calculation**

```text
Production Quantity / Planned Production Quantity
```

---

## 13.3 Inventory-to-Daily-Sales Ratio

**Domains**

Sales + Production + Inventory

**Analytical grain**

```text
Date + Location + Product
```

**Calculation**

```text
Quantity on Hand / Sales Quantity
```

---

## 13.4 Below Reorder Point

**Domains**

Sales + Production + Inventory

**Analytical grain**

```text
Date + Location + Product
```

**Calculation**

```text
Quantity on Hand < Reorder Point
```

---

## 13.5 Production Rate

**Domains**

Production + Maintenance

**Analytical grain**

```text
Date + Location + Machine
```

**Calculation**

```text
Production Quantity / Production Hours
```

---

## 13.6 Downtime-to-Production-Hours Ratio

**Domains**

Production + Maintenance

**Analytical grain**

```text
Date + Location + Machine
```

**Calculation**

```text
Downtime Hours / Production Hours
```

---

## 13.7 Maintenance Cost per Produced Unit

**Domains**

Production + Maintenance

**Analytical grain**

```text
Date + Location + Machine
```

**Calculation**

```text
Maintenance Cost / Production Quantity
```

---

## 13.8 Energy Intensity

**Domains**

Production + Energy + Emissions

**Analytical grain**

```text
Date + Location
```

**Calculation**

```text
Energy Consumption (kWh) / Production Quantity
```

---

## 13.9 Emissions Intensity

**Domains**

Production + Energy + Emissions

**Analytical grain**

```text
Date + Location
```

**Calculation**

```text
CO2 Emissions (kg) / Production Quantity
```

---

# 14. Analytical Grain Governance

Cross-domain facts must never be joined directly at incompatible transaction/event grains.

Atlas currently uses the following compatible analytical grains:

| Cross-Domain Analysis           | Grain                     |
| ------------------------------- | ------------------------- |
| Sales + Production + Inventory  | Date + Location + Product |
| Production + Maintenance        | Date + Location + Machine |
| Production + Energy + Emissions | Date + Location           |

Each contributing fact is independently aggregated to the target grain before the facts are combined.

This protects Atlas against:

* Fan-out
* Double counting
* Inflated revenue
* Inflated production
* Inflated maintenance cost
* Inflated energy consumption
* Inflated emissions

---

# 15. Financial Metric Limitations

Atlas must distinguish between actual financial measures and analytical estimates.

The current warehouse contains:

```text
dim_product.unit_cost
fact_sales.revenue
```

A product-cost estimate may therefore be analytically derived as:

```text
Sales Quantity × Product Unit Cost
```

However, this does not represent transaction-level realized COGS.

Therefore the following terminology is permitted only when explicitly labeled as an estimate:

* Estimated Product Cost
* Estimated Gross Margin

The following must not be represented as actual realized measures without additional supporting data:

* Actual COGS
* Actual Gross Margin
* Actual Profit

---

# 16. Synthetic Data Limitation

All Atlas data is synthetic.

Therefore:

* KPI values are illustrative.
* Trends are analytical outputs from generated data.
* Findings are not real-world business results.
* Recommendations are scenario-based.
* No real savings, revenue improvement, cost reduction, production improvement, or environmental impact may be claimed.

---

# 17. BI Consistency Requirement

Power BI and Tableau must use the same governed KPI definitions.

Where equivalent filter contexts are applied:

```text
PostgreSQL Analytics
        =
Power BI
        =
Tableau
```

Any discrepancy must be investigated before a KPI is considered production-ready for the Atlas BI layer.

---

# 18. KPI Change Control

A KPI definition must not be changed independently in:

* SQL
* Power BI
* Tableau
* Documentation

If a KPI definition changes, the change must be reflected consistently across all downstream consumers.

---

# 19. Current Analytics Views

## KPI Views

```text
analytics.vw_sales_kpis_daily
analytics.vw_production_kpis_daily
analytics.vw_maintenance_kpis_daily
analytics.vw_financial_kpis_daily
analytics.vw_budget_kpis_daily
analytics.vw_energy_kpis_daily
analytics.vw_emissions_kpis_daily
analytics.vw_waste_kpis_daily
analytics.vw_inventory_kpis_daily
```

## Domain Views

```text
analytics.vw_account_sales_daily
analytics.vw_customer_sales_daily
analytics.vw_product_sales_daily
analytics.vw_supplier_sales_daily
analytics.vw_location_sales_daily
analytics.vw_production_performance_daily
analytics.vw_machine_production_daily
analytics.vw_maintenance_performance_daily
analytics.vw_employee_operations_daily
analytics.vw_financial_performance_daily
analytics.vw_budget_performance_daily
analytics.vw_energy_performance_daily
analytics.vw_emissions_performance_daily
analytics.vw_waste_performance_daily
analytics.vw_inventory_position_daily
```

## Cross-Domain Views

```text
analytics.vw_sales_production_inventory_daily
analytics.vw_production_maintenance_daily
analytics.vw_production_energy_emissions_daily
```

---

# 20. Governance Status

Phase 7 analytics has been validated through:

* View existence checks
* Row-count checks
* Date-range checks
* Warehouse-to-analytics reconciliation
* Domain-level reconciliation
* Cross-domain reconciliation
* Fact-grain validation
* Fan-out protection

Phase 7 is complete when the final automated validation script passes and the analytics documentation is committed to the repository.
