# Phase 8 — Power BI

## Purpose

Phase 8 implements the Project Atlas business intelligence layer in Microsoft Power BI.

Power BI connects to the trusted PostgreSQL warehouse created in Phase 6 and uses the governed analytical definitions established in Phase 7 to provide interactive, decision-oriented reporting across commercial, operational, financial, inventory, and sustainability areas.

Power BI is a downstream consumer of the same trusted analytical foundation used by the Atlas analytics layer.

---

## Data Source

Power BI connects directly to the Project Atlas PostgreSQL data warehouse.

The model contains the approved dimensional/star-schema structure:

### Dimensions

* `dim_date`
* `dim_account`
* `dim_customer`
* `dim_product`
* `dim_supplier`
* `dim_location`
* `dim_employee`
* `dim_machine`

### Facts

* `fact_sales`
* `fact_production`
* `fact_maintenance`
* `fact_financial_transaction`
* `fact_budget`
* `fact_energy`
* `fact_emissions`
* `fact_waste`
* `fact_inventory`

The `dim_date` table is configured as the Power BI date table and supports time-intelligence analysis.

---

## Semantic Model

The Power BI model follows the PostgreSQL star-schema design.

* Dimension tables filter related fact tables.
* Relationships use surrogate warehouse keys.
* Fact tables are not directly joined to one another.
* Conformed dimensions such as Date and Location support analysis across business processes.
* Active relationships use single-direction filtering from dimensions to facts.
* Inactive relationships are retained where required by the warehouse model.

This approach preserves the fact-grain discipline established in the warehouse and analytics layers.

---

## DAX and KPI Layer

Core business measures are implemented in DAX and aligned with the governed Phase 7 definitions.

Key measures include:

### Commercial

* Total Revenue
* Revenue YoY Change
* Revenue PY
* Revenue YoY %
* Total Sales
* Sales Lines
* Average Order Value
* Total Customers
* Purchasing Customers

### Product and Supplier

* Total Products
* Active/Selling Products
* Revenue per Selling Product
* Total Suppliers
* Active Suppliers
* Revenue per Active Supplier

### Operations

* Planned Production
* Produced Quantity
* Production Variance
* Production Achievement %
* Defect Rate %
* Downtime Hours
* Inventory Positions Below Reorder Point

### Financial

* Total Financial Revenue
* Total Financial Costs
* Total Financial Expenses
* Net Financial Result

### Sustainability

* Total Energy Consumption
* Total CO2 Emissions
* Total Waste
* Energy Intensity

Inventory measures use the latest available inventory reporting date rather than summing historical inventory snapshots.

---

## KPI Governance

Atlas uses consistent business definitions across SQL, Power BI, Tableau, documentation, and downstream analysis.

Quantity-based metrics retain their `unit_of_measure`. Physical quantities measured in different units are not combined into universal quantity KPIs.

Production achievement and production variance are evaluated within compatible production units.

Inventory is treated as a periodic snapshot.

Energy and emissions retain their defined measurement units:

* Energy — kWh
* CO2 emissions — kg

Financial metrics are treated independently from physical quantity units.

Conditional formatting is used where it improves business interpretation. For example, negative production variance is shown as unfavorable, while defect-rate and financial-result indicators use business-oriented status colors.

---

## Dashboard Approach

The Power BI implementation uses concise, interactive dashboard perspectives designed around business questions rather than individual tables.

Current dashboard perspectives include:

1. Executive Command Center
2. Sales Intelligence
3. Customer Intelligence
4. Product Intelligence
5. Supplier Intelligence
6. Operations Intelligence
7. Financial Intelligence
8. Sustainability Intelligence

Dashboards use KPI cards, trend analysis, categorical comparisons, geographic/location analysis, slicers, and interactive filtering where appropriate.

The Executive Command Center provides a high-level view of commercial, operational, financial, inventory, and sustainability performance.

---

## Analytical Capabilities

The Power BI implementation supports analysis of:

* Revenue and sales performance
* Customer activity and purchasing behavior
* Product and category performance
* Supplier-associated sales performance
* Production achievement and variance
* Defect rates and operational output
* Maintenance activity and downtime
* Financial revenue, costs, expenses, and net result
* Inventory positions and reorder-point issues
* Energy consumption
* CO2 emissions
* Waste
* Energy intensity
* Year-over-year performance

The dashboards are designed to support questions such as:

* What happened?
* Where did it happen?
* How is performance changing over time?
* Which products, customers, suppliers, or locations are driving results?
* Where are operational or financial issues requiring investigation?

---

## Power BI Deliverable

```text
08_Power_BI/

├── README.md
├── Project_Atlas.pbix
└── screenshots/
```

`Project_Atlas.pbix` contains the Power BI semantic model, DAX measures, relationships, report pages, filters, and visualizations.

Selected final dashboard screenshots are maintained in the `screenshots/` directory.