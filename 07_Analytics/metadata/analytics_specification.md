# Project Atlas — Analytics Specification

## 1. Purpose

The Atlas Analytics Layer is the reusable analytical layer between the PostgreSQL data warehouse and the BI platforms.

Its purpose is to transform trusted warehouse facts into governed, business-oriented analytical views that can be consumed consistently by:

- Power BI
- Tableau
- Documentation
- Business insights
- Interview explanations

The analytics layer must not become a second warehouse.

Its responsibility is to provide reusable analytical logic while preserving the business meaning and grain of the underlying warehouse.

---

# 2. Analytics Architecture

The official Atlas architecture is:

```text
Raw Operational Data
        ↓
Data Profiling & Quality
        ↓
ETL / ELT
        ↓
PostgreSQL Data Warehouse
        ↓
Reusable SQL Analytics Layer
        ↓
Power BI + Tableau
        ↓
Business Insights & Recommendations
````

The Analytics Layer therefore sits downstream of the PostgreSQL warehouse and upstream of both BI platforms.

Power BI and Tableau consume the same trusted analytical foundation.

Separate underlying analytical pipelines are not created for each BI platform.

---

# 3. Analytics Objectives

The Atlas Analytics Layer is designed to:

1. Standardize important business metrics.
2. Provide reusable SQL analytical logic.
3. Support domain-level decision analysis.
4. Enable controlled cross-domain analysis.
5. Prevent fact-to-fact fan-out and double counting.
6. Provide a trusted foundation for Power BI and Tableau.
7. Make analytical results reproducible.
8. Keep KPI definitions consistent across the project.
9. Translate warehouse data into business-oriented measures.
10. Support downstream business insights and recommendations.

---

# 4. Analytics Layers

Atlas Analytics is organized into three analytical layers.

## 4.1 KPI Analytics

KPI views provide standardized daily metrics for major business-process facts.

Current KPI views:

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

These views provide reusable metrics that can be consumed by downstream analytical and BI layers.

---

## 4.2 Domain Analytics

Domain analytics provides more detailed analytical perspectives within individual domains.

Current domain views:

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

These views support domain-specific analysis without requiring Power BI or Tableau to rebuild the same SQL logic independently.

---

## 4.3 Cross-Domain Analytics

Cross-domain analysis is a core differentiator of Atlas.

Current cross-domain views:

```text
analytics.vw_sales_production_inventory_daily
analytics.vw_production_maintenance_daily
analytics.vw_production_energy_emissions_daily
```

These views combine multiple business processes only after each contributing fact has been aggregated to a compatible analytical grain.

---

# 5. Fact Grain Protection

Fact tables operate at different grains.

Directly joining facts at their transaction/event grain can produce many-to-many relationships and fan-out.

Atlas therefore follows this rule:

```text
Fact A
   ↓
Aggregate to target grain

Fact B
   ↓
Aggregate to target grain

Fact C
   ↓
Aggregate to target grain

Compatible analytical grain
   ↓
Join
```

The cross-domain layer must never bypass this process.

---

# 6. Cross-Domain Analytical Grains

## 6.1 Sales + Production + Inventory

View:

```text
analytics.vw_sales_production_inventory_daily
```

Governed grain:

```text
One row represents one date + one location + one product.
```

Contributing facts:

```text
fact_sales
fact_production
fact_inventory
```

Primary analytical questions:

* Are production and sales aligned?
* What is the production-versus-sales quantity difference?
* What inventory position exists relative to sales?
* Which products are below reorder point?
* Where are production, sales and inventory patterns diverging?

Key metrics:

```text
sales_quantity
sales_revenue
production_quantity
planned_production_quantity
quantity_on_hand
inventory_value
reorder_point
production_minus_sales_quantity
production_attainment_rate
inventory_to_daily_sales_ratio
below_reorder_point
```

---

## 6.2 Production + Maintenance

View:

```text
analytics.vw_production_maintenance_daily
```

Governed grain:

```text
One row represents one date + one location + one machine.
```

Contributing facts:

```text
fact_production
fact_maintenance
```

Primary analytical questions:

* How much production activity occurred on each machine?
* How much maintenance activity occurred?
* How much downtime was recorded?
* How does maintenance cost compare with production activity?
* Which machines warrant further operational investigation?

Key metrics:

```text
production_quantity
planned_production_quantity
production_hours
maintenance_event_count
downtime_hours
maintenance_cost
production_attainment_rate
production_rate
downtime_to_production_hours_ratio
average_maintenance_cost_per_event
maintenance_cost_per_produced_unit
```

These metrics are descriptive.

They do not establish that maintenance caused production changes.

---

## 6.3 Production + Energy + Emissions

View:

```text
analytics.vw_production_energy_emissions_daily
```

Governed grain:

```text
One row represents one date + one location.
```

Contributing facts:

```text
fact_production
fact_energy
fact_emissions
```

Primary analytical questions:

* How much production occurred?
* How much energy was consumed?
* What were the associated emissions?
* How does energy consumption normalize against production?
* How do emissions normalize against production?
* Which locations warrant sustainability investigation?

Key metrics:

```text
production_quantity
production_hours
energy_consumption_kwh
co2_kg
energy_intensity_kwh_per_unit
emissions_intensity_kg_per_unit
```

---

# 7. KPI Governance

Important metrics must have one governed definition.

The KPI catalog is maintained in:

```text
07_Analytics/metadata/kpi_catalog.md
```

The KPI catalog is the business-definition reference for:

* SQL
* Power BI
* Tableau
* Documentation
* Interview explanations

If a KPI definition changes, all downstream implementations must be reviewed and updated consistently.

---

# 8. Core KPI Definitions

## Sales

```text
Total Revenue
= SUM(fact_sales.revenue)
```

```text
Sales Quantity
= SUM(fact_sales.quantity)
```

```text
Sales Transaction Count
= COUNT(DISTINCT fact_sales.sales_id)
```

---

## Production

```text
Production Quantity
= SUM(fact_production.quantity_produced)
```

```text
Planned Production Quantity
= SUM(fact_production.planned_quantity)
```

```text
Production Attainment Rate
= Production Quantity / Planned Production Quantity
```

```text
Production Rate
= Production Quantity / Production Hours
```

---

## Maintenance

```text
Maintenance Cost
= SUM(fact_maintenance.maintenance_cost)
```

```text
Maintenance Event Count
= COUNT(DISTINCT fact_maintenance.maintenance_id)
```

```text
Downtime Hours
= SUM(fact_maintenance.downtime_hours)
```

---

## Financial

```text
Financial Transaction Amount
= SUM(fact_financial_transaction.amount)
```

Transaction-specific metrics are filtered by:

```text
transaction_type
```

including:

```text
Revenue
Expense
Transfer
Adjustment
```

---

## Budget

```text
Budget Amount
= SUM(fact_budget.budget_amount)
```

Budget can be analyzed by:

```text
category
location
date
```

A governed Budget vs Actual KPI is not currently implemented because the current warehouse does not define a defensible mapping between budget categories and financial transaction categories.

---

## Energy

```text
Energy Consumption
= SUM(fact_energy.consumption)
WHERE unit = 'kWh'
```

---

## Emissions

```text
CO2 Emissions
= SUM(fact_emissions.co2_kg)
```

---

## Waste

```text
Waste Quantity
= SUM(fact_waste.quantity)
WHERE unit = 'kg'
```

---

## Inventory

```text
Quantity on Hand
= SUM(fact_inventory.quantity_on_hand)
```

```text
Inventory Value
= SUM(fact_inventory.inventory_value)
```

---

# 9. Intensity Metrics

## Energy Intensity

```text
Energy Consumption (kWh)
/
Production Quantity
```

Unit:

```text
kWh per production unit
```

---

## Emissions Intensity

```text
CO2 Emissions (kg)
/
Production Quantity
```

Unit:

```text
kg CO2 per production unit
```

---

## Waste Intensity

Waste intensity is not currently treated as a governed cross-domain KPI unless an appropriate compatible production/waste analytical context is explicitly implemented.

No unsupported cross-domain relationship should be inferred.

---

# 10. Analytical Estimates and Financial Limitations

The warehouse contains product unit cost in:

```text
dim_product.unit_cost
```

and sales revenue in:

```text
fact_sales.revenue
```

An estimated product cost can therefore be derived analytically as:

```text
Sales Quantity × Product Unit Cost
```

However, this is not equivalent to transaction-level realized COGS.

Therefore:

### Permitted terminology

```text
Estimated Product Cost
Estimated Gross Margin
```

### Not permitted without additional supporting data

```text
Actual COGS
Actual Gross Margin
Actual Profit
```

This distinction is required to maintain analytical credibility.

---

# 11. Budget-to-Actual Limitation

Atlas contains:

```text
fact_budget.category
fact_budget.budget_amount
```

and:

```text
fact_financial_transaction.transaction_type
fact_financial_transaction.amount
```

The current warehouse does not provide a governed mapping between budget categories and financial transaction classifications.

Therefore:

```text
Budget vs Actual
Budget Variance
```

are not currently treated as governed metrics.

This prevents an unsupported analytical relationship from being presented as a business fact.

---

# 12. Null and Zero-Denominator Handling

Ratio metrics must protect against division by zero.

Use:

```sql
NULLIF(denominator, 0)
```

rather than returning misleading infinite or zero values.

Examples:

```sql
production_quantity
/
NULLIF(planned_production_quantity, 0)
```

```sql
energy_consumption_kwh
/
NULLIF(production_quantity, 0)
```

```sql
co2_kg
/
NULLIF(production_quantity, 0)
```

A NULL ratio means the metric cannot be meaningfully calculated for that analytical context.

It does not automatically mean zero performance.

---

# 13. Reconciliation Methodology

Analytics are validated against the warehouse using aggregate reconciliation.

For a governed measure:

```text
Warehouse Aggregate
        =
Analytics Aggregate
```

within an appropriate numeric tolerance.

Primary reconciliation measures include:

* Sales revenue
* Production quantity
* Maintenance cost
* Maintenance downtime
* Energy consumption
* CO₂ emissions
* Waste quantity
* Inventory quantity

Cross-domain measures are also reconciled against their originating facts.

---

# 14. Current Validated Reconciliation Results

The following values have been validated in the current Atlas implementation:

| Metric              |  Warehouse Result |  Analytics Result |
| ------------------- | ----------------: | ----------------: |
| Sales Revenue       |  3,525,201,270.71 |  3,525,201,270.71 |
| Production Quantity |     72,068,666.00 |     72,068,666.00 |
| Maintenance Cost    |     32,443,072.23 |     32,443,072.23 |
| Energy Consumption  | 30,738,263.75 kWh | 30,738,263.75 kWh |
| CO₂ Emissions       |  30,466,499.55 kg |  30,466,499.55 kg |
| Waste Quantity      |   4,151,914.77 kg |   4,151,914.77 kg |

These are results from synthetic Atlas data.

They are validation evidence, not real-world business outcomes.

---

# 15. Cross-Domain Reconciliation

Cross-domain analytics must preserve the originating fact totals.

For example:

```text
fact_sales.revenue
        =
SUM(vw_sales_production_inventory_daily.sales_revenue)
```

and:

```text
fact_production.quantity_produced
        =
SUM(vw_production_maintenance_daily.production_quantity)
```

and:

```text
fact_maintenance.maintenance_cost
        =
SUM(vw_production_maintenance_daily.maintenance_cost)
```

and:

```text
fact_energy.consumption
        =
SUM(vw_production_energy_emissions_daily.energy_consumption_kwh)
```

and:

```text
fact_emissions.co2_kg
        =
SUM(vw_production_energy_emissions_daily.co2_kg)
```

These reconciliations protect against fan-out and double counting.

---

# 16. Cross-Domain Fan-Out Protection

Atlas specifically avoids patterns such as:

```text
fact_sales
JOIN fact_production
JOIN fact_inventory
```

at raw transaction grain.

Instead:

```text
fact_sales
    ↓
aggregate

fact_production
    ↓
aggregate

fact_inventory
    ↓
aggregate

date + location + product
    ↓
join
```

The same principle applies to:

```text
Production + Maintenance
```

and:

```text
Production + Energy + Emissions
```

---

# 17. Analytics Validation

The final validation script is:

```text
07_Analytics/sql/05_validate_all_analytics.sql
```

The validation checks:

1. Required analytics views exist.
2. KPI views are populated.
3. KPI views cover the expected date range.
4. Core KPI totals reconcile with the warehouse.
5. Domain analytics reconcile with the warehouse.
6. Cross-domain analytics reconcile with the warehouse.
7. Cross-domain grains contain no duplicate grain groups.
8. Major cross-domain measures do not exhibit fan-out.

---

# 18. Python Validation

The automated Python validation entry point is:

```text
07_Analytics/scripts/validate_analytics.py
```

The script should execute the SQL validation checks and fail clearly when a required validation does not pass.

It should provide:

* Database connectivity status
* Required view status
* KPI validation results
* Domain validation results
* Cross-domain validation results
* Final PASS/FAIL status

---

# 19. BI Consumption

Power BI and Tableau are downstream consumers of this analytics layer.

They should not independently recreate important business logic when a governed SQL metric already exists.

The intended flow is:

```text
PostgreSQL Warehouse
        ↓
Analytics SQL Views
        ↓
Power BI
        +
Tableau
```

Equivalent filter contexts should produce equivalent KPI results.

---

# 20. Analytical Limitations

Atlas is intentionally transparent about its limitations.

### Synthetic data

All data is generated for portfolio and analytical demonstration purposes.

### No causal inference

Cross-domain relationships are descriptive.

For example:

```text
Maintenance + Production
```

does not establish that maintenance caused production changes.

### No unsupported financial claims

Actual COGS, actual gross margin, and actual profit are not claimed without appropriate transaction-level financial support.

### No unsupported budget mapping

Budget vs Actual is not treated as a governed KPI without a defensible category mapping.

### No unsupported product-level sustainability attribution

Energy and emissions are available at location/date grain, not product or machine grain.

Therefore product-level energy or emissions attribution should not be inferred.

---

# 21. Reproducibility

The analytics layer should be reproducible from the PostgreSQL warehouse.

Required SQL artifacts:

```text
07_Analytics/sql/01_create_kpi_views.sql
07_Analytics/sql/02_validate_kpi_views.sql
07_Analytics/sql/03_create_domain_views.sql
07_Analytics/sql/04_create_cross_domain_views.sql
07_Analytics/sql/05_validate_all_analytics.sql
```

Metadata artifacts:

```text
07_Analytics/metadata/kpi_catalog.md
07_Analytics/metadata/analytics_specification.md
```

Validation script:

```text
07_Analytics/scripts/validate_analytics.py
```

---

# 22. Definition of Done

Phase 7 Analytics is considered complete when:

* KPI views exist.
* Domain analytics views exist.
* Cross-domain views exist.
* KPI definitions are documented.
* Analytical grains are documented.
* Warehouse-to-analytics reconciliation passes.
* Domain reconciliation passes.
* Cross-domain reconciliation passes.
* Grain uniqueness checks pass.
* Fan-out protection has been validated.
* Python validation passes.
* Analytics documentation is committed.
* Power BI and Tableau can consume the same governed analytical foundation.