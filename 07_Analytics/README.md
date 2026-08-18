# Project Atlas — Phase 7: Analytics

## Purpose

Phase 7 establishes the governed SQL analytics layer for Project Atlas.

The purpose of this phase is to transform the PostgreSQL data warehouse into a reusable, decision-oriented analytical foundation that can be consumed consistently by both Power BI and Tableau.

The analytics layer separates business KPI and analytical logic from individual BI reports. This ensures that important metrics are defined once, validated against the warehouse, and reused consistently across both BI platforms.

---

## Position in the Atlas Architecture

Project Atlas follows the architecture:

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

Phase 7 represents the **Reusable SQL Analytics Layer**.

---

## Objectives

The Analytics phase is responsible for:

* Establishing governed KPI calculations.
* Creating reusable SQL analytical views.
* Providing domain-level analytical perspectives.
* Enabling cross-domain analysis.
* Preventing inconsistent KPI definitions across BI platforms.
* Reusing conformed warehouse dimensions.
* Respecting documented fact grain.
* Preventing fact-to-fact fan-out and double counting.
* Reconciling analytical results against warehouse facts.
* Providing a stable analytical foundation for Power BI and Tableau.

---

## Analytics Scope

The analytics layer contains three levels of analytical views.

### 1. Core KPI Analytics

Daily KPI views provide standardized measures for the major operational and financial facts:

* Sales
* Production
* Maintenance
* Financial Transactions
* Budget
* Energy
* Emissions
* Waste
* Inventory

These views provide the governed KPI foundation for downstream reporting.

---

### 2. Domain Analytics

Domain analytical views provide reusable perspectives for individual business areas.

Current domain views include:

* Account Sales
* Customer Sales
* Product Sales
* Supplier Sales
* Location Sales
* Production Performance
* Machine Production
* Maintenance Performance
* Employee Operations
* Financial Performance
* Budget Performance
* Energy Performance
* Emissions Performance
* Waste Performance
* Inventory Position

These views support domain-specific decision analysis and provide the analytical foundation for the corresponding BI dashboards.

---

### 3. Cross-Domain Analytics

Cross-domain views combine compatible analytical grains to support enterprise-level analysis.

Current cross-domain views include:

* Sales + Production + Inventory
* Production + Maintenance
* Production + Energy + Emissions

Cross-domain analysis is designed around compatible aggregation grains to avoid double counting and fact-to-fact fan-out.

---

## Analytical Governance

Important business metrics are defined consistently across:

```text
Business Definition
        ↓
Warehouse
        ↓
SQL Analytics
        ↓
Power BI
        ↓
Tableau
        ↓
Documentation
```

The SQL analytics layer is therefore treated as a governed analytical foundation rather than a collection of ad hoc queries.

Equivalent analytical contexts must reconcile to the underlying warehouse facts.

---

## Validation

Phase 7 includes automated validation through:

```text
07_Analytics/scripts/validate_analytics.py
```

Validation covers:

1. Database connectivity
2. Required analytics views
3. KPI view population
4. KPI date coverage
5. Core KPI reconciliation
6. Domain analytics reconciliation
7. Cross-domain reconciliation
8. Cross-domain grain uniqueness
9. Cross-domain view population

The validation process compares analytical aggregates against the underlying warehouse facts to detect missing records, inconsistent calculations, and potential double counting.

---

## Current Validation Status

Phase 7 has successfully passed automated analytics validation.

Latest validation result:

```text
PASS checks : 75
FAIL checks : 0
CHECK items : 2
```

Core warehouse-to-analytics reconciliations produced zero differences for:

* Sales revenue
* Production quantity
* Maintenance cost
* Energy consumption
* CO2 emissions
* Waste quantity
* Domain-level analytical measures
* Cross-domain analytical measures

Cross-domain grain validation also confirmed that no duplicate analytical grain groups were present in the validated views.

The two date-coverage checks for Production and Maintenance reflect the actual availability of records in the underlying warehouse facts and are not validation failures.

---

## Key Analytical Principle

The analytics layer must preserve the grain of the underlying facts.

For example:

```text
fact_sales
    ↓
Daily / Account / Customer / Product / Location
```

and:

```text
fact_production
    ↓
Daily / Product / Location / Machine / Employee
```

Cross-domain analysis must first aggregate each fact to a compatible analytical grain before combining measures.

This prevents:

```text
Fact A × Fact B
      ↓
Fan-out
      ↓
Double Counting
```

Instead:

```text
Fact A → Compatible Grain
                     ↓
                  Combine
                     ↑
Fact B → Compatible Grain
```

---

## Repository Structure

```text
07_Analytics/
│
├── README.md
│
├── metadata/
│   ├── analytics_specification.md
│   └── kpi_catalog.md
│
├── sql/
│   ├── 01_create_kpi_views.sql
│   ├── 02_create_domain_views.sql
│   ├── 03_create_cross_domain_views.sql
│   ├── 04_validate_analytics.sql
│   └── 05_validate_all_analytics.sql
│
└── scripts/
    └── validate_analytics.py
```

---

## Deliverables

Phase 7 produces:

* Governed KPI SQL views
* Domain analytical SQL views
* Cross-domain analytical SQL views
* KPI definitions and metadata
* Analytics specifications
* Automated SQL validation
* Automated Python validation
* Warehouse-to-analytics reconciliation
* Cross-domain grain validation

---

## Downstream Use

The completed analytics layer becomes the trusted analytical source for:

### Phase 8 — Power BI

Power BI will consume the governed warehouse and analytics layer to create:

* Executive Command Center
* Accounts Intelligence
* Customer Intelligence
* Product Intelligence
* Supplier Intelligence
* Location Intelligence
* Employee Intelligence
* Machine Intelligence
* Sales Intelligence
* Production Intelligence
* Maintenance Intelligence
* Financial Intelligence
* Budget Intelligence
* Energy Intelligence
* Emissions Intelligence
* Waste Intelligence
* Inventory Intelligence

### Phase 9 — Tableau

Tableau will use the same governed analytical foundation to provide equivalent decision-oriented perspectives.

Power BI and Tableau may use different layouts and visualization techniques, but governed KPI definitions and analytical results must remain consistent.

---

## Phase Completion Criteria

Phase 7 is considered complete when:

* Required KPI views exist.
* Required domain analytical views exist.
* Required cross-domain views exist.
* Analytical views are populated.
* KPI calculations reconcile with warehouse facts.
* Domain analytical calculations reconcile with warehouse facts.
* Cross-domain calculations reconcile with warehouse facts.
* Cross-domain grains contain no duplicate grain groups.
* Analytics documentation is complete.
* Automated validation passes with zero failures.

### Status

**Phase 7 — Analytics: COMPLETE / VALIDATED**

The validated analytics layer is now ready to support the BI implementation phases.