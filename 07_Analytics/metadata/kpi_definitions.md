# Project Atlas — Phase 7 KPI Definitions

## Purpose

This document is the governed reference for analytical KPIs used by Project Atlas.

KPI definitions established here must remain consistent across:

- PostgreSQL analytics views
- Power BI
- Tableau
- Documentation
- Business insights
- Interview explanations

Atlas uses synthetic enterprise data. Metrics describe the generated analytical dataset and do not represent real-world business results.

---

# 1. Sales KPIs

## Total Revenue

**Definition:** Net sales revenue after discounts.

**Formula:**

```text
Total Revenue = SUM(revenue)
````

**Source:** `fact_sales`

**Analytical grain:** Date or compatible dimensional aggregation.

**Unit:** Currency.

---

## Sales Quantity

**Definition:** Total quantity sold.

**Formula:**

```text
Sales Quantity = SUM(quantity)
```

**Source:** `fact_sales`

**Unit:** Units.

---

## Sales Transaction Count

**Definition:** Number of distinct sales transactions.

**Formula:**

```text
Sales Transaction Count = COUNT(DISTINCT sales_id)
```

---

## Average Selling Price

**Definition:** Quantity-weighted average realized selling price.

**Formula:**

```text
Average Selling Price =
    SUM(revenue) / SUM(quantity)
```

Revenue is net revenue after discount.

---

## Average Discount Rate

**Definition:** Arithmetic average of transaction-level discount rates within the selected analytical context.

**Formula:**

```text
Average Discount Rate = AVG(discount_rate)
```

---

## Estimated Discount Amount

**Definition:** Reconstructed discount amount because `revenue` represents net revenue after discount and gross revenue is not stored directly in the analytics layer.

**Formula:**

```text
Gross Amount = Revenue / (1 - Discount Rate)

Estimated Discount Amount =
    Revenue × Discount Rate / (1 - Discount Rate)
```

The metric is explicitly labeled **estimated** because it is reconstructed from net revenue and discount rate.

---

# 2. Production KPIs

## Production Quantity

**Definition:** Total quantity produced.

**Formula:**

```text
Production Quantity = SUM(quantity_produced)
```

---

## Planned Production Quantity

**Definition:** Total planned production quantity.

**Formula:**

```text
Planned Production Quantity = SUM(planned_quantity)
```

---

## Production Variance

**Definition:** Difference between actual production output and planned production.

**Formula:**

```text
Production Variance =
    Production Quantity - Planned Production Quantity
```

Positive values indicate production above plan.

Negative values indicate production below plan.

---

## Production Attainment Rate

**Definition:** Actual production as a proportion of planned production.

**Formula:**

```text
Production Attainment Rate =
    Production Quantity / Planned Production Quantity
```

Zero planned quantity returns NULL.

---

## Production Rate

**Definition:** Production output per production hour.

**Formula:**

```text
Production Rate =
    Production Quantity / Production Hours
```

Zero production hours returns NULL.

---

# 3. Maintenance KPIs

## Maintenance Event Count

**Definition:** Number of distinct maintenance events.

**Formula:**

```text
COUNT(DISTINCT maintenance_id)
```

---

## Downtime Hours

**Definition:** Total recorded machine downtime hours.

**Formula:**

```text
SUM(downtime_hours)
```

---

## Maintenance Cost

**Definition:** Total recorded maintenance cost.

**Formula:**

```text
SUM(maintenance_cost)
```

---

## Average Maintenance Cost Per Event

**Formula:**

```text
Maintenance Cost / Maintenance Event Count
```

---

## Average Downtime Hours Per Event

**Formula:**

```text
Downtime Hours / Maintenance Event Count
```

---

# 4. Financial KPIs

## Revenue Amount

**Definition:** Sum of financial transactions classified as Revenue.

---

## Expense Amount

**Definition:** Sum of financial transactions classified as Expense.

---

## Transfer Amount

**Definition:** Sum of financial transactions classified as Transfer.

---

## Adjustment Amount

**Definition:** Sum of financial transactions classified as Adjustment.

---

# 5. Budget KPIs

## Total Budget Amount

**Definition:** Total budget amount recorded in `fact_budget`.

**Formula:**

```text
SUM(budget_amount)
```

Budget remains analytically separate from financial actuals because Atlas does not assume an unsupported common budget/actual category mapping.

---

# 6. Energy KPIs

## Energy Consumption

**Definition:** Total energy consumption recorded in kWh.

**Formula:**

```text
SUM(consumption)
WHERE unit = 'kWh'
```

**Unit:** kWh.

---

## Energy Intensity

**Definition:** Energy consumption per unit of production.

**Formula:**

```text
Energy Intensity =
    Energy Consumption kWh / Production Quantity
```

**Unit:** kWh per production unit.

This is an analytical intensity measure and not a causal claim.

---

# 7. Emissions KPIs

## Total CO2

**Definition:** Total recorded CO₂ emissions.

**Formula:**

```text
SUM(co2_kg)
```

**Unit:** kg CO₂.

---

## Emissions Intensity

**Definition:** CO₂ emissions per unit of production.

**Formula:**

```text
Emissions Intensity =
    CO2 kg / Production Quantity
```

**Unit:** kg CO₂ per production unit.

This is an analytical intensity measure and not a causal claim.

---

# 8. Waste KPIs

## Total Waste

**Definition:** Total waste quantity recorded in kilograms.

**Formula:**

```text
SUM(quantity)
WHERE unit = 'kg'
```

**Unit:** kg.

---

# 9. Inventory KPIs

## Quantity On Hand

**Definition:** Inventory quantity available at a specific snapshot date.

**Formula:**

```text
SUM(quantity_on_hand)
```

Inventory is a snapshot measure.

It must not be summed across dates to represent a period flow.

---

## Inventory Value

**Definition:** Inventory value at a specific snapshot date.

**Formula:**

```text
SUM(inventory_value)
```

Inventory value must be interpreted at the selected snapshot date.

---

## Items Below Reorder Point

**Definition:** Count of inventory records where quantity on hand is below the reorder point.

---

## Inventory-to-Daily-Sales Ratio

**Definition:** Inventory quantity available relative to same-day sales quantity.

**Formula:**

```text
Quantity On Hand / Sales Quantity
```

This is a simple analytical ratio and should not be interpreted as a formal days-of-inventory calculation.

---

# 10. Cross-Domain KPIs

## Production Minus Sales Quantity

**Formula:**

```text
Production Quantity - Sales Quantity
```

Used to compare production output and sales activity at the common date/location/product grain.

---

## Downtime-to-Production-Hours Ratio

**Formula:**

```text
Downtime Hours / Production Hours
```

Used as an operational comparison metric.

---

## Maintenance Cost Per Produced Unit

**Formula:**

```text
Maintenance Cost / Production Quantity
```

Used to compare maintenance spending relative to production output.

---

# 11. Analytical Governance Rules

1. Ratios use explicit numeric division.
2. Division by zero returns NULL.
3. Revenue is net revenue after discount.
4. Inventory is treated as a snapshot fact.
5. Cross-domain facts must be aggregated independently before joining.
6. KPI definitions must not be independently redefined in Power BI or Tableau.
7. Synthetic analytical results must not be presented as real-world business impact.
8. Intensity measures are analytical measures and do not establish causality.