# Project Atlas — Business Definition

## 1. Project Overview

Project Atlas is an end-to-end Enterprise Decision Intelligence Platform built around a realistic commercial and manufacturing business scenario.

The goal is to transform imperfect operational data into trusted, decision-ready business intelligence through data quality, ETL/ELT, PostgreSQL, SQL analytics, Power BI, and Tableau.

Atlas is one integrated enterprise platform covering 16 business domains.

## 2. Business Domains

1. Accounts
2. Customers
3. Products
4. Suppliers
5. Locations
6. Employees
7. Machines
8. Sales
9. Production
10. Maintenance
11. Financial Transactions
12. Budget
13. Energy
14. Emissions
15. Waste
16. Inventory

Accounts and Customers are intentionally separate:

- **Account** — represents a commercial relationship or organizational grouping.
- **Customer** — represents the customer entity participating in business activity and associated with an account.

The relationship is intentionally kept simple and does not introduce unnecessary CRM complexity.

## 3. Business Areas

Atlas provides analysis across five main areas:

### Commercial

- Sales and revenue
- Customers and accounts
- Products and categories
- Location performance

### Operations

- Production
- Machine activity
- Downtime
- Maintenance

### Financial

- Revenue and costs
- Financial transactions
- Budget vs. actual
- Variance analysis

### Inventory & Supply Chain

- Inventory levels
- Stock movements
- Shortages
- Supplier performance

### Sustainability

- Energy consumption
- Energy intensity
- Emissions
- Waste

Cross-domain analysis connects these areas where the business grain allows reliable comparison.

## 4. Key Business Questions

Atlas is designed to answer questions such as:

- How is revenue changing over time?
- Which customers, products, accounts, and locations perform best?
- Where are production and machine performance issues occurring?
- How do maintenance and downtime relate to operations?
- How does actual financial performance compare with budget?
- Where are inventory shortages or stock issues occurring?
- Which locations have higher energy, emissions, or waste levels?
- How do sales, production, inventory, financial, and sustainability measures relate?

## 5. Analytical Principles

The project follows a few important principles:

- Data is synthetic and generated for the project.
- Data quality is evaluated before trusted reporting.
- Business metrics have governed definitions.
- Facts are analyzed according to their documented grain.
- Incompatible fact-to-fact joins that can cause double counting are avoided.
- Power BI and Tableau use the same trusted analytical foundation.
- Project findings must be traceable to the synthetic data.

## 6. Architecture

```text
Raw Operational Data
        ↓
Data Profiling & Quality
        ↓
ETL / ELT
        ↓
PostgreSQL Data Warehouse
        ↓
Reusable SQL Analytics
        ↓
Power BI + Tableau
        ↓
Business Insights & Recommendations
```

## 7. Technology

- Python
- Faker
- Pandas
- NumPy
- PostgreSQL
- SQL
- Power BI / DAX
- Tableau
- Git / GitHub
- Markdown

## 8. Development Phases

1. Business Definition
2. Data Model
3. Data Generation
4. Data Quality
5. ETL
6. Data Warehouse
7. Analytics
8. Power BI
9. Tableau
10. Insights & Portfolio

Each phase is completed before moving to the next when important decisions remain unresolved.

## 9. Phase 1 Status

> **Phase 1 — Business Definition**  
> **Status:** ✅ Complete

Phase 1 established the:

- Business scenario and project scope
- 16 business domains
- Stakeholder needs
- Key business questions
- Analytical principles
- Project boundaries

---

### Next Phase

> **Phase 2 — Data Model**

The next phase will define:

- Entities and relationships
- Dimensions and facts
- Primary and surrogate keys
- Foreign-key relationships
- Conformed dimensions
- Exact grain of each fact

The data model will be finalized **before warehouse implementation begins**.

---

> **Note:** All data and resulting findings in Project Atlas are synthetic and are intended for portfolio and demonstration purposes only.
