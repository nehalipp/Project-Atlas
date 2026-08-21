# Project Atlas — Business Definition

## 1. Project Overview

Project Atlas is an end-to-end **Enterprise Decision Intelligence Platform** built as a portfolio project for Data Analyst, Senior Data Analyst, BI Analyst/Developer, Analytics Engineer, Operations/Supply Chain Analytics, Manufacturing/Industrial Analytics, and Sustainability/Business Analytics roles.

Atlas uses a synthetic commercial/manufacturing business scenario. It transforms imperfect operational data into trusted, reusable, decision-ready business intelligence through data quality, ETL/ELT, dimensional modeling, SQL analytics, and BI.

The platform is designed to support both USA and Sweden job applications without maintaining separate implementations.

---

## 2. Business Problem

Management does not have a consistent, trusted view of commercial, operational, financial, inventory, and sustainability performance because information is distributed across multiple operational datasets and contains data-quality and consistency issues.

This makes it difficult to:

* Monitor revenue, customer, product, account, supplier, and location performance consistently.
* Evaluate production, machine, maintenance, and operational performance together.
* Compare financial actuals with budgets and identify important variances.
* Monitor inventory conditions alongside sales and production.
* Connect energy, emissions, and waste performance to operational activity.
* Perform cross-domain analysis without inconsistent KPI definitions or double counting.

---

## 3. Business Objective

Build a reusable decision-intelligence platform that transforms imperfect operational data into trusted, governed, and decision-ready analytics for commercial, operational, financial, inventory, and sustainability decision-making.

Atlas should help business users:

* Monitor performance and trends.
* Compare business units, entities, and operational areas.
* Identify exceptions and areas requiring investigation.
* Understand potential relationships across business domains.
* Support evidence-based management decisions.

---

## 4. Business Areas

Atlas contains 16 analytical domains that form one integrated enterprise platform.

### Master / Reference Domains

1. Accounts
2. Customers
3. Products
4. Suppliers
5. Locations
6. Employees
7. Machines

### Business Process Domains

8. Sales
9. Production
10. Maintenance
11. Financial Transactions
12. Budget
13. Energy
14. Emissions
15. Waste
16. Inventory

Accounts and Customers remain intentionally separate. An **Account** represents the commercial relationship or organizational grouping, while a **Customer** represents the customer entity participating in business activity and associated with an account.

---

## 5. Key Business Questions

### Commercial

* How is revenue changing over time?
* Which customers generate the most revenue?
* Which products and categories perform best?
* Which locations generate the strongest sales?
* Which accounts represent the largest commercial relationships?

### Supplier

* Which suppliers support the largest share of business activity?
* Which suppliers should management investigate based on available performance indicators?
* Do supplier patterns differ across locations or products?

### Operations

* How much is being produced?
* How does actual production compare with planned production?
* Which locations or machines have the strongest or weakest production performance?
* Where are important operational exceptions occurring?

### Maintenance

* Which machines experience the most maintenance activity?
* Where is maintenance cost concentrated?
* What relationships can be investigated between maintenance activity and production performance?

### Financial

* What are the major revenue and cost trends?
* How does actual financial performance compare with budget?
* Where are the largest budget variances?
* Which areas require financial investigation?

### Inventory

* What inventory is available?
* Where are potential inventory shortages or excesses?
* How do inventory conditions relate to sales and production?

### Sustainability

* How much energy is being consumed?
* How does energy consumption relate to production?
* What are the major emissions patterns?
* How does waste vary across operations?
* Where are energy, emissions, or waste intensity concerns visible?

### Cross-Domain

* Does production performance vary with machine maintenance activity?
* How do production levels relate to energy consumption?
* How do production levels relate to emissions?
* How do sales trends relate to inventory?
* How do revenue, costs, and budget performance interact?

Cross-domain analysis is a core capability of Atlas. Any cross-domain analysis must respect fact-table grain and avoid fan-out or double counting.

---

## 6. Stakeholders

  | Stakeholder                            | Primary Decision Need                              |
  | -------------------------------------- | -------------------------------------------------- |
  | Executive Management                   | Overall enterprise performance                     |
  | Sales / Commercial Management          | Customers, products, accounts, and revenue         |
  | Operations Management                  | Production, locations, and operational performance |
  | Maintenance Management                 | Machine reliability and maintenance activity       |
  | Finance Management                     | Revenue, costs, and budget performance             |
  | Supply Chain / Inventory Management    | Suppliers, inventory, and availability             |
  | Sustainability / Operations Leadership | Energy, emissions, and waste                       |

---

## 7. Scope

### In Scope

* Synthetic enterprise operational data.
* All 16 Atlas business domains.
* Data profiling and quality management.
* ETL/ELT and data transformation.
* PostgreSQL dimensional warehouse.
* Reusable SQL analytical layer.
* Governed KPI definitions.
* Power BI implementation.
* Tableau implementation.
* Cross-domain analysis.
* Data-supported business insights and recommendations.
* Portfolio documentation and interview narrative.

### Out of Scope

The core implementation will not introduce unnecessary engineering or advanced analytics complexity, including:

* Machine learning or deep learning.
* Real-time streaming.
* Airflow.
* dbt.
* Spark.
* Databricks.
* Snowflake.
* Cloud platforms.
* Kafka/streaming.
* Docker/Kubernetes.
* APIs or microservices.
* Terraform.
* Complex CI/CD.
* Additional BI platforms.
* Complex testing frameworks.

Potential production extensions may be discussed later, but they are not part of the core Atlas implementation.

---

## 8. Assumptions

1. All business data is synthetic and is clearly identified as synthetic.
2. The scenario represents a commercial/manufacturing organization.
3. The generated data is designed to resemble realistic operational conditions.
4. Controlled data-quality issues may be intentionally introduced to support the data-quality phase.
5. PostgreSQL is the primary database and analytical warehouse.
6. SQL is the primary language for database-side transformation and analytics where appropriate.
7. Python is primarily a supporting technology for synthetic data generation, basic data preparation, data-quality support, and simple orchestration where necessary.
8. Power BI and Tableau consume the same trusted analytical foundation rather than separate underlying pipelines.
9. Important business metrics have one governed definition across SQL, Power BI, Tableau, documentation, and interviews.
10. Cross-domain analysis will aggregate facts to compatible grains before combining them.
11. Atlas is a portfolio implementation, not a claim of a production enterprise deployment.
12. No real companies, customers, employees, financial results, or business relationships are represented.

---

## 9. Technology Stack

  | Layer                           | Technology                            |
  | ------------------------------- | ------------------------------------- |
  | Data Generation                 | Python, Faker, Pandas                 |
  | Reference / Small Business Data | Excel                                 |
  | Database / Warehouse            | PostgreSQL                            |
  | Transformation / Analytics      | SQL + simple Python where appropriate |
  | BI                              | Power BI + Tableau                    |
  | Documentation                   | Markdown                              |
  | Version Control                 | Git / GitHub                          |

Python is a supporting skill rather than the centerpiece of Atlas. Analytical logic should be implemented in SQL/PostgreSQL where that is the more appropriate and understandable approach.
