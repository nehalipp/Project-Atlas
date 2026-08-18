# Project Atlas — KPI Definitions

## Purpose

This document defines the governed analytical metrics used by
Project Atlas. KPI definitions are implemented in the PostgreSQL
analytics layer and serve as the reference for Power BI, Tableau,
documentation, and interview explanations.

---

## Sales KPIs

### Total Revenue

Definition:

Sum of `fact_sales.revenue`.

Source:
`fact_sales`

### Sales Quantity

Definition:

Sum of `fact_sales.quantity`.

### Sales Transactions

Definition:

Distinct count of `fact_sales.sales_id`.

### Average Selling Price

Definition:

Total sales revenue divided by total sales quantity.

Formula:

Total Revenue / Sales Quantity

This is preferred over a simple average of transaction-level
unit prices because transaction quantities may differ.

---

## Production KPIs

### Planned Quantity

Sum of `fact_production.planned_quantity`.

### Quantity Produced

Sum of `fact_production.quantity_produced`.

### Production Variance

Quantity Produced minus Planned Quantity.

### Production Attainment Rate

Quantity Produced divided by Planned Quantity.

### Production Rate

Quantity Produced divided by Production Hours.

### Production Status Counts

Production records are classified using the warehouse values:

- Completed
- Partial
- Cancelled

---

## Maintenance KPIs

### Maintenance Events

Distinct count of `fact_maintenance.maintenance_id`.

### Downtime Hours

Sum of `fact_maintenance.downtime_hours`.

### Maintenance Cost

Sum of `fact_maintenance.maintenance_cost`.

### Average Maintenance Cost per Event

Maintenance Cost divided by Maintenance Events.

### Average Downtime per Event

Downtime Hours divided by Maintenance Events.

---

## Financial KPIs

### Revenue Amount

Sum of financial transaction amounts where
`transaction_type = 'Revenue'`.

### Expense Amount

Sum of financial transaction amounts where
`transaction_type = 'Expense'`.

### Transfer Amount

Sum of financial transaction amounts where
`transaction_type = 'Transfer'`.

### Adjustment Amount

Sum of financial transaction amounts where
`transaction_type = 'Adjustment'`.

Transfers and adjustments are not classified as operating revenue
or operating expense.

---

## Budget KPIs

### Budget Amount

Sum of `fact_budget.budget_amount`.

Budget categories currently include:

- Maintenance
- Energy
- Production
- Administration
- Supply Chain
- Operations

Budget categories must not be artificially mapped to financial
transaction types without a documented business rule.

---

## Energy KPIs

### Energy Consumption

Sum of `fact_energy.consumption` where unit = `kWh`.

The current warehouse contains energy observations in kWh.

---

## Emissions KPIs

### CO2 Emissions

Sum of `fact_emissions.co2_kg`.

Emissions sources currently include:

- Electricity
- Process
- Fuel
- Natural Gas

---

## Waste KPIs

### Waste Quantity

Sum of `fact_waste.quantity` where unit = `kg`.

Waste types currently include:

- Chemical
- Metal
- Paper
- Plastic
- General

Disposal methods currently include:

- Recycling
- Reuse
- Treatment
- Landfill

---

## Inventory KPIs

### Inventory Quantity

Sum of `quantity_on_hand` within a specific inventory snapshot.

### Inventory Value

Sum of `inventory_value` within a specific inventory snapshot.

### Items Below Reorder Point

Count of inventory records where:

`quantity_on_hand < reorder_point`

Inventory is a snapshot fact. Inventory quantities and values must
not be blindly summed across multiple snapshot dates.

---

## Cross-Domain KPI Principles

Facts must be aggregated to compatible grains before being combined.

Examples:

Production + Energy:

Energy Consumption / Quantity Produced

Production + Emissions:

CO2 kg / Quantity Produced

Production + Maintenance:

Production output compared with maintenance cost and downtime.

Sales + Inventory:

Sales quantity compared with inventory position at a compatible
date/product/location grain.

No raw fact-to-fact joins should be used when they can create
fan-out or double counting.