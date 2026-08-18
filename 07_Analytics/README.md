# Project Atlas — Phase 7: Analytics

## Purpose

Phase 7 transforms the trusted PostgreSQL warehouse into a reusable analytical SQL layer for downstream Power BI and Tableau consumption.

The objective is to provide:

- Governed KPIs
- Reusable analytical views
- Dimension-aware domain analysis
- Cross-domain analysis
- Reconciliation against warehouse facts
- Grain and fan-out validation

Phase 7 does not modify the warehouse data.

---

## Position in the Atlas Architecture

```text
Raw Operational Data
        ↓
Data Profiling & Quality
        ↓
ETL / ELT
        ↓
PostgreSQL Data Warehouse
        ↓
>>> Phase 7 — Reusable SQL Analytics Layer <<<
        ↓
Power BI + Tableau
        ↓
Business Insights & Recommendations
````

Power BI and Tableau consume the same analytical foundation.

Important business metrics are defined once and must reconcile across both BI platforms.

---

## Analytical Design Principles

### 1. Governed KPIs

Important metrics have a single documented definition.

KPI definitions are maintained in:

```text
07_Analytics/metadata/kpi_definitions.md
```

These definitions govern SQL, Power BI, Tableau and downstream business interpretation.

### 2. Fact Grain Protection

Facts are never blindly joined at transaction/event grain.

For cross-domain analysis:

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

      ↓

Join compatible aggregates
```

This prevents fan-out and double counting.

### 3. Explicit Numeric Ratios

Analytical ratios use explicit numeric division and `NULLIF` to prevent:

* Integer truncation
* Divide-by-zero errors

### 4. Inventory Snapshot Protection

Inventory is a snapshot fact.

Inventory position must be interpreted at a specific date and must not be summed across dates as though it were a transaction flow.

### 5. Synthetic Data Governance

All Atlas data is synthetic.

Analytics results describe the generated dataset and do not represent actual companies, customers, financial performance or operational improvements.

---

# SQL View Structure

```text
07_Analytics/sql/
│
├── 01_create_analytics_schema.sql
├── 02_create_kpi_views.sql
├── 03_create_domain_views.sql
├── 04_create_cross_domain_views.sql
└── 05_validate_all_analytics.sql
```

---

# KPI Views

Daily enterprise KPI views include:

* Sales
* Production
* Maintenance
* Financial Transactions
* Budget
* Energy
* Emissions
* Waste
* Inventory

Example:

```text
vw_sales_kpis_daily
```

Grain:

```text
One row per date
```

---

# Domain Views

Domain views provide reusable dimensional analysis for:

* Accounts
* Customers
* Products
* Suppliers
* Locations
* Production
* Machines
* Maintenance
* Employees
* Financials
* Budget
* Energy
* Emissions
* Waste
* Inventory

These views are designed for downstream BI consumption.

---

# Cross-Domain Views

Phase 7 includes three required cross-domain analytical views.

## Sales + Production + Inventory

```text
vw_sales_production_inventory_daily
```

Grain:

```text
Date + Location + Product
```

Supports analysis of:

* Sales quantity
* Production quantity
* Inventory position
* Production attainment
* Inventory-to-sales relationship
* Reorder-point conditions

---

## Production + Maintenance

```text
vw_production_maintenance_daily
```

Grain:

```text
Date + Location + Machine
```

Supports analysis of:

* Production output
* Production rate
* Maintenance events
* Downtime
* Maintenance cost
* Maintenance cost per produced unit

---

## Production + Energy + Emissions

```text
vw_production_energy_emissions_daily
```

Grain:

```text
Date + Location
```

Supports analysis of:

* Production output
* Energy consumption
* CO₂ emissions
* Energy intensity
* Emissions intensity

Intensity measures are analytical measures and are not causal claims.

---

# Validation

Final analytics validation covers:

1. Required view existence
2. KPI population
3. KPI date coverage against source facts
4. Warehouse-to-KPI reconciliation
5. Domain-view reconciliation
6. Cross-domain reconciliation
7. Domain analytical grain uniqueness
8. Cross-domain grain uniqueness
9. Fan-out protection

The validation script is:

```text
07_Analytics/sql/05_validate_all_analytics.sql
```

---

# Reproduction

Run the SQL files in order:

```text
01_create_analytics_schema.sql
02_create_kpi_views.sql
03_create_domain_views.sql
04_create_cross_domain_views.sql
05_validate_all_analytics.sql
```

Then run the Phase 7 Python validation script:

```bash
python3 07_Analytics/scripts/validate_analytics.py
```

---

# Definition of Done

Phase 7 is complete when:

* Required analytical views exist.
* KPI views are populated.
* KPI definitions are documented.
* KPI totals reconcile to warehouse facts.
* Domain views reconcile to source facts.
* Cross-domain views reconcile to source facts.
* Documented grains are unique.
* Cross-domain fact joins are protected from fan-out.
* SQL is ready for Power BI and Tableau consumption.