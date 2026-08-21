"""
Project Atlas
Phase 3 - Synthetic Data Generation

Generates 17 synthetic datasets for Project Atlas.

The raw datasets intentionally contain a small number of
realistic data-quality issues.

Phase 4 will detect and remediate those issues.

Random seed: 42
Date range: 2019-01-01 to 2025-12-31
"""

from pathlib import Path
import random

import numpy as np
import pandas as pd
from faker import Faker


# ============================================================
# SETTINGS
# ============================================================

SEED = 42

START_DATE = "2019-01-01"
END_DATE = "2025-12-31"

ATTRIBUTE_START_DATE = "2016-01-01"
ATTRIBUTE_END_DATE = "2018-12-31"

SCRIPT_DIR = Path(__file__).resolve().parent
OUTPUT_DIR = SCRIPT_DIR / "data" / "raw"

OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

random.seed(SEED)
np.random.seed(SEED)
Faker.seed(SEED)

fake = Faker()
rng = np.random.default_rng(SEED)


# ============================================================
# DATA VOLUMES
# ============================================================

N_ACCOUNT = 1_000
N_CUSTOMER = 50_000
N_PRODUCT = 5_000
N_SUPPLIER = 1_000
N_LOCATION = 100
N_EMPLOYEE = 5_000
N_MACHINE = 2_000

N_SALES = 500_000
N_PRODUCTION = 200_000
N_MAINTENANCE = 50_000
N_FINANCIAL = 300_000
N_BUDGET = 20_000
N_ENERGY = 100_000
N_EMISSIONS = 100_000
N_WASTE = 100_000
N_INVENTORY = 500_000


# ============================================================
# REFERENCE VALUES
# ============================================================

COUNTRIES = [
    "United States",
    "Canada",
    "Germany",
    "Sweden",
    "Mexico"
]

INDUSTRIES = [
    "Manufacturing",
    "Automotive",
    "Retail",
    "Healthcare",
    "Technology"
]

ACCOUNT_TYPES = [
    "Enterprise",
    "Mid-Market",
    "Small Business"
]

CUSTOMER_SEGMENTS = [
    "Enterprise",
    "Mid-Market",
    "SMB"
]

PRODUCT_CATEGORIES = [
    "Industrial Equipment",
    "Components",
    "Electronics",
    "Packaging",
    "Raw Materials"
]

PRODUCT_SUBCATEGORIES = [
    "Standard",
    "Premium",
    "Specialty"
]

SUPPLIER_CATEGORIES = [
    "Manufacturer",
    "Distributor",
    "Service Provider",
    "Raw Material Supplier"
]

LOCATION_TYPES = [
    "Plant",
    "Warehouse",
    "Distribution Center",
    "Office"
]

DEPARTMENTS = [
    "Sales",
    "Operations",
    "Finance",
    "Human Resources",
    "IT",
    "Maintenance",
    "Supply Chain"
]

EMPLOYEE_ROLES = [
    "Analyst",
    "Manager",
    "Supervisor",
    "Operator",
    "Engineer",
    "Coordinator",
    "Specialist"
]

MACHINE_TYPES = [
    "CNC Machine",
    "Assembly Machine",
    "Packaging Machine",
    "Press Machine",
    "Cutting Machine"
]

MAINTENANCE_TYPES = [
    "Preventive",
    "Corrective",
    "Inspection"
]

TRANSACTION_TYPES = [
    "Revenue",
    "Expense",
    "Cost"
]

TRANSACTION_CATEGORIES = [
    "Sales Revenue",
    "Operating Expense",
    "Maintenance",
    "Payroll",
    "Utilities",
    "Materials"
]

BUDGET_CATEGORIES = [
    "Revenue",
    "Operations",
    "Maintenance",
    "Payroll",
    "Utilities"
]

ENERGY_SOURCES = [
    "Electricity",
    "Natural Gas",
    "Diesel"
]

EMISSIONS_CATEGORIES = [
    "Direct Emissions",
    "Purchased Energy",
    "Transportation"
]

WASTE_CATEGORIES = [
    "Metal",
    "Plastic",
    "Paper",
    "Chemical",
    "General"
]

DISPOSAL_METHODS = [
    "Recycling",
    "Landfill",
    "Reuse",
    "Treatment"
]


# ============================================================
# HELPER FUNCTIONS
# ============================================================

def make_ids(prefix, number):
    """Create business IDs."""
    return [f"{prefix}-{i:06d}" for i in range(1, number + 1)]


def random_dates(number):
    """Create random operational dates."""
    dates = pd.date_range(START_DATE, END_DATE)
    return rng.choice(dates, number)


def random_attribute_dates(number):
    """Create dates before the operational period."""
    dates = pd.date_range(
        ATTRIBUTE_START_DATE,
        ATTRIBUTE_END_DATE
    )
    return rng.choice(dates, number)


def random_rows(dataframe, number):
    """Return random row indexes."""
    return rng.choice(
        dataframe.index,
        size=number,
        replace=False
    )


def save_data(dataframe, name):
    """Save dataframe as CSV."""
    dataframe.to_csv(
        OUTPUT_DIR / f"{name}.csv",
        index=False
    )
    print(f"{name}: {len(dataframe):,} rows")


# ============================================================
# DIMENSION TABLES
# ============================================================

print("\nGenerating dimensions...")


# -------------------------
# dim_date
# -------------------------

dates = pd.date_range(
    START_DATE,
    END_DATE
)

dim_date = pd.DataFrame({
    "date_key": dates.strftime("%Y%m%d").astype(int),
    "full_date": dates,
    "day_of_week": dates.dayofweek + 1,
    "day_name": dates.day_name(),
    "week_number": dates.isocalendar().week.astype(int),
    "month": dates.month,
    "month_name": dates.month_name(),
    "quarter": dates.quarter,
    "year": dates.year
})


# -------------------------
# dim_account
# -------------------------

dim_account = pd.DataFrame({
    "account_key": range(1, N_ACCOUNT + 1),
    "account_id": make_ids("ACC", N_ACCOUNT),
    "account_name": [fake.company() for _ in range(N_ACCOUNT)],
    "account_type": rng.choice(ACCOUNT_TYPES, N_ACCOUNT),
    "industry": rng.choice(INDUSTRIES, N_ACCOUNT),
    "country": rng.choice(COUNTRIES, N_ACCOUNT),
    "status": rng.choice(
        ["Active", "Inactive"],
        N_ACCOUNT,
        p=[0.90, 0.10]
    )
})


# -------------------------
# dim_customer
# -------------------------

dim_customer = pd.DataFrame({
    "customer_key": range(1, N_CUSTOMER + 1),
    "customer_id": make_ids("CUS", N_CUSTOMER),
    "account_key": rng.choice(
        dim_account["account_key"],
        N_CUSTOMER
    ),
    "customer_name": [
        fake.company()
        for _ in range(N_CUSTOMER)
    ],
    "customer_segment": rng.choice(
        CUSTOMER_SEGMENTS,
        N_CUSTOMER
    ),
    "industry": rng.choice(
        INDUSTRIES,
        N_CUSTOMER
    ),
    "country": rng.choice(
        COUNTRIES,
        N_CUSTOMER
    ),
    "status": rng.choice(
        ["Active", "Inactive"],
        N_CUSTOMER,
        p=[0.90, 0.10]
    )
})


# -------------------------
# dim_supplier
# -------------------------

dim_supplier = pd.DataFrame({
    "supplier_key": range(1, N_SUPPLIER + 1),
    "supplier_id": make_ids("SUP", N_SUPPLIER),
    "supplier_name": [
        fake.company()
        for _ in range(N_SUPPLIER)
    ],
    "supplier_category": rng.choice(
        SUPPLIER_CATEGORIES,
        N_SUPPLIER
    ),
    "country": rng.choice(
        COUNTRIES,
        N_SUPPLIER
    ),
    "status": rng.choice(
        ["Active", "Inactive"],
        N_SUPPLIER,
        p=[0.90, 0.10]
    )
})


# -------------------------
# dim_product
# -------------------------

unit_cost = np.round(
    rng.uniform(10, 500, N_PRODUCT),
    2
)

unit_price = np.round(
    unit_cost * rng.uniform(1.25, 2.50, N_PRODUCT),
    2
)

dim_product = pd.DataFrame({
    "product_key": range(1, N_PRODUCT + 1),
    "product_id": make_ids("PROD", N_PRODUCT),
    "supplier_key": rng.choice(
        dim_supplier["supplier_key"],
        N_PRODUCT
    ),
    "product_name": [
        f"Atlas Product {i}"
        for i in range(1, N_PRODUCT + 1)
    ],
    "category": rng.choice(
        PRODUCT_CATEGORIES,
        N_PRODUCT
    ),
    "subcategory": rng.choice(
        PRODUCT_SUBCATEGORIES,
        N_PRODUCT
    ),
    "unit_of_measure": rng.choice(
        ["Each", "Kg", "Liter", "Meter"],
        N_PRODUCT
    ),
    "unit_cost": unit_cost,
    "unit_price": unit_price,
    "status": rng.choice(
        ["Active", "Inactive"],
        N_PRODUCT,
        p=[0.90, 0.10]
    )
})


# -------------------------
# dim_location
# -------------------------

dim_location = pd.DataFrame({
    "location_key": range(1, N_LOCATION + 1),
    "location_id": make_ids("LOC", N_LOCATION),
    "location_name": [
        f"Atlas Facility {i}"
        for i in range(1, N_LOCATION + 1)
    ],
    "location_type": rng.choice(
        LOCATION_TYPES,
        N_LOCATION
    ),
    "city": [fake.city() for _ in range(N_LOCATION)],
    "state_region": [
        fake.state()
        for _ in range(N_LOCATION)
    ],
    "country": rng.choice(
        COUNTRIES,
        N_LOCATION
    ),
    "status": rng.choice(
        ["Active", "Inactive"],
        N_LOCATION,
        p=[0.95, 0.05]
    )
})


# -------------------------
# dim_employee
# -------------------------

dim_employee = pd.DataFrame({
    "employee_key": range(1, N_EMPLOYEE + 1),
    "employee_id": make_ids("EMP", N_EMPLOYEE),
    "location_key": rng.choice(
        dim_location["location_key"],
        N_EMPLOYEE
    ),
    "employee_name": [
        fake.name()
        for _ in range(N_EMPLOYEE)
    ],
    "department": rng.choice(
        DEPARTMENTS,
        N_EMPLOYEE
    ),
    "role": rng.choice(
        EMPLOYEE_ROLES,
        N_EMPLOYEE
    ),
    "hire_date": random_attribute_dates(N_EMPLOYEE),
    "status": rng.choice(
        ["Active", "Inactive"],
        N_EMPLOYEE,
        p=[0.92, 0.08]
    )
})


# -------------------------
# dim_machine
# -------------------------

dim_machine = pd.DataFrame({
    "machine_key": range(1, N_MACHINE + 1),
    "machine_id": make_ids("MCH", N_MACHINE),
    "location_key": rng.choice(
        dim_location["location_key"],
        N_MACHINE
    ),
    "machine_name": [
        f"Atlas Machine {i}"
        for i in range(1, N_MACHINE + 1)
    ],
    "machine_type": rng.choice(
        MACHINE_TYPES,
        N_MACHINE
    ),
    "installation_date": random_attribute_dates(
        N_MACHINE
    ),
    "status": rng.choice(
        ["Operational", "Maintenance", "Inactive"],
        N_MACHINE,
        p=[0.85, 0.10, 0.05]
    )
})


# ============================================================
# LOOKUPS
# ============================================================

product_prices = dict(
    zip(
        dim_product["product_key"],
        dim_product["unit_price"]
    )
)

machine_locations = dict(
    zip(
        dim_machine["machine_key"],
        dim_machine["location_key"]
    )
)


# ============================================================
# FACT TABLES
# ============================================================

print("\nGenerating facts...")


# -------------------------
# fact_sales
# -------------------------

sales_dates = pd.to_datetime(
    random_dates(N_SALES)
)

sales_quantity = rng.integers(
    1,
    101,
    N_SALES
)

sales_product_keys = rng.choice(
    dim_product["product_key"],
    N_SALES
)

sales_unit_price = np.array([
    product_prices[key]
    for key in sales_product_keys
])

discount = np.round(
    sales_quantity
    * sales_unit_price
    * rng.uniform(0, 0.15, N_SALES),
    2
)

revenue = np.round(
    sales_quantity * sales_unit_price - discount,
    2
)

fact_sales = pd.DataFrame({
    "sales_key": range(1, N_SALES + 1),
    "transaction_id": make_ids("SAL", N_SALES),
    "date_key": sales_dates.strftime("%Y%m%d").astype(int),
    "customer_key": rng.choice(
        dim_customer["customer_key"],
        N_SALES
    ),
    "product_key": sales_product_keys,
    "location_key": rng.choice(
        dim_location["location_key"],
        N_SALES
    ),
    "quantity": sales_quantity,
    "unit_price": sales_unit_price,
    "discount_amount": discount,
    "revenue": revenue
})


# -------------------------
# fact_production
# -------------------------

production_machine_keys = rng.choice(
    dim_machine["machine_key"],
    N_PRODUCTION
)

production_location_keys = [
    machine_locations[machine]
    for machine in production_machine_keys
]

planned_quantity = rng.integers(
    50,
    501,
    N_PRODUCTION
)

# VALID BASELINE:
# Produced quantity cannot exceed planned quantity.

produced_quantity = np.round(
    planned_quantity
    * rng.uniform(0.80, 1.00, N_PRODUCTION)
).astype(int)

# VALID BASELINE:
# Defects cannot exceed produced quantity.

defect_quantity = np.array([
    rng.integers(0, produced + 1)
    for produced in produced_quantity
])

fact_production = pd.DataFrame({
    "production_key": range(1, N_PRODUCTION + 1),
    "production_id": make_ids("PRD", N_PRODUCTION),
    "date_key": pd.to_datetime(
        random_dates(N_PRODUCTION)
    ).strftime("%Y%m%d").astype(int),
    "product_key": rng.choice(
        dim_product["product_key"],
        N_PRODUCTION
    ),
    "location_key": production_location_keys,
    "machine_key": production_machine_keys,
    "employee_key": rng.choice(
        dim_employee["employee_key"],
        N_PRODUCTION
    ),
    "planned_quantity": planned_quantity,
    "produced_quantity": produced_quantity,
    "defect_quantity": defect_quantity,
    "production_hours": np.round(
        rng.uniform(1, 12, N_PRODUCTION),
        2
    )
})


# -------------------------
# fact_maintenance
# -------------------------

maintenance_machine_keys = rng.choice(
    dim_machine["machine_key"],
    N_MAINTENANCE
)

maintenance_location_keys = [
    machine_locations[machine]
    for machine in maintenance_machine_keys
]

fact_maintenance = pd.DataFrame({
    "maintenance_key": range(1, N_MAINTENANCE + 1),
    "maintenance_id": make_ids("MNT", N_MAINTENANCE),
    "date_key": pd.to_datetime(
        random_dates(N_MAINTENANCE)
    ).strftime("%Y%m%d").astype(int),
    "location_key": maintenance_location_keys,
    "machine_key": maintenance_machine_keys,
    "employee_key": rng.choice(
        dim_employee["employee_key"],
        N_MAINTENANCE
    ),
    "maintenance_type": rng.choice(
        MAINTENANCE_TYPES,
        N_MAINTENANCE
    ),
    "maintenance_hours": np.round(
        rng.uniform(0.5, 8, N_MAINTENANCE),
        2
    ),
    "downtime_hours": np.round(
        rng.uniform(0.5, 24, N_MAINTENANCE),
        2
    ),
    "maintenance_cost": np.round(
        rng.uniform(100, 10_000, N_MAINTENANCE),
        2
    )
})


# -------------------------
# fact_financial_transaction
# -------------------------

fact_financial_transaction = pd.DataFrame({
    "financial_transaction_key": range(
        1,
        N_FINANCIAL + 1
    ),
    "transaction_id": make_ids("FIN", N_FINANCIAL),
    "date_key": pd.to_datetime(
        random_dates(N_FINANCIAL)
    ).strftime("%Y%m%d").astype(int),
    "account_key": rng.choice(
        dim_account["account_key"],
        N_FINANCIAL
    ),
    "location_key": rng.choice(
        dim_location["location_key"],
        N_FINANCIAL
    ),
    "transaction_type": rng.choice(
        TRANSACTION_TYPES,
        N_FINANCIAL
    ),
    "transaction_category": rng.choice(
        TRANSACTION_CATEGORIES,
        N_FINANCIAL
    ),
    "transaction_amount": np.round(
        rng.uniform(100, 50_000, N_FINANCIAL),
        2
    )
})


# -------------------------
# fact_budget
# -------------------------

fact_budget = pd.DataFrame({
    "budget_key": range(1, N_BUDGET + 1),
    "budget_id": make_ids("BUD", N_BUDGET),
    "date_key": pd.to_datetime(
        random_dates(N_BUDGET)
    ).strftime("%Y%m%d").astype(int),
    "account_key": rng.choice(
        dim_account["account_key"],
        N_BUDGET
    ),
    "location_key": rng.choice(
        dim_location["location_key"],
        N_BUDGET
    ),
    "budget_category": rng.choice(
        BUDGET_CATEGORIES,
        N_BUDGET
    ),
    "budget_amount": np.round(
        rng.uniform(10_000, 500_000, N_BUDGET),
        2
    )
})


# -------------------------
# fact_energy
# -------------------------

energy_machine_keys = rng.choice(
    dim_machine["machine_key"],
    N_ENERGY
)

energy_location_keys = [
    machine_locations[machine]
    for machine in energy_machine_keys
]

fact_energy = pd.DataFrame({
    "energy_key": range(1, N_ENERGY + 1),
    "energy_id": make_ids("ENG", N_ENERGY),
    "date_key": pd.to_datetime(
        random_dates(N_ENERGY)
    ).strftime("%Y%m%d").astype(int),
    "location_key": energy_location_keys,
    "machine_key": energy_machine_keys,
    "energy_source": rng.choice(
        ENERGY_SOURCES,
        N_ENERGY
    ),
    "energy_consumption": np.round(
        rng.uniform(100, 10_000, N_ENERGY),
        3
    )
})


# -------------------------
# fact_emissions
# -------------------------

fact_emissions = pd.DataFrame({
    "emissions_key": range(1, N_EMISSIONS + 1),
    "emissions_id": make_ids("EMS", N_EMISSIONS),
    "date_key": pd.to_datetime(
        random_dates(N_EMISSIONS)
    ).strftime("%Y%m%d").astype(int),
    "location_key": rng.choice(
        dim_location["location_key"],
        N_EMISSIONS
    ),
    "emissions_category": rng.choice(
        EMISSIONS_CATEGORIES,
        N_EMISSIONS
    ),
    "co2_emissions": np.round(
        rng.uniform(10, 5_000, N_EMISSIONS),
        3
    )
})


# -------------------------
# fact_waste
# -------------------------

fact_waste = pd.DataFrame({
    "waste_key": range(1, N_WASTE + 1),
    "waste_id": make_ids("WST", N_WASTE),
    "date_key": pd.to_datetime(
        random_dates(N_WASTE)
    ).strftime("%Y%m%d").astype(int),
    "location_key": rng.choice(
        dim_location["location_key"],
        N_WASTE
    ),
    "waste_category": rng.choice(
        WASTE_CATEGORIES,
        N_WASTE
    ),
    "disposal_method": rng.choice(
        DISPOSAL_METHODS,
        N_WASTE
    ),
    "waste_quantity": np.round(
        rng.uniform(1, 1_000, N_WASTE),
        3
    )
})


# -------------------------
# fact_inventory
# -------------------------

inventory_dates = pd.date_range(
    START_DATE,
    END_DATE
)

date_count = len(inventory_dates)

random_numbers = rng.choice(
    date_count * N_PRODUCT * N_LOCATION,
    size=N_INVENTORY,
    replace=False
)

date_index = random_numbers // (
    N_PRODUCT * N_LOCATION
)

remaining = random_numbers % (
    N_PRODUCT * N_LOCATION
)

inventory_product_keys = (
    remaining // N_LOCATION
) + 1

inventory_location_keys = (
    remaining % N_LOCATION
) + 1

opening_quantity = rng.integers(
    0,
    5_000,
    N_INVENTORY
)

received_quantity = rng.integers(
    0,
    2_000,
    N_INVENTORY
)

available_quantity = (
    opening_quantity
    + received_quantity
)

issued_quantity = np.minimum(
    rng.integers(0, 2_000, N_INVENTORY),
    available_quantity
)

closing_quantity = (
    opening_quantity
    + received_quantity
    - issued_quantity
)

fact_inventory = pd.DataFrame({
    "inventory_key": range(1, N_INVENTORY + 1),
    "inventory_id": make_ids("INV", N_INVENTORY),
    "date_key": inventory_dates[
        date_index
    ].strftime("%Y%m%d").astype(int),
    "product_key": inventory_product_keys,
    "location_key": inventory_location_keys,
    "opening_quantity": opening_quantity,
    "received_quantity": received_quantity,
    "issued_quantity": issued_quantity,
    "closing_quantity": closing_quantity,
    "reorder_point": rng.integers(
        100,
        1_500,
        N_INVENTORY
    )
})


# ============================================================
# CONTROLLED DATA QUALITY ISSUES
# ============================================================

# ============================================================
# 1. NULL / BLANK VALUES
# ============================================================

dim_customer.loc[
    random_rows(dim_customer, 100),
    "country"
] = np.nan

dim_product.loc[
    random_rows(dim_product, 10),
    "subcategory"
] = np.nan

dim_supplier.loc[
    random_rows(dim_supplier, 5),
    "supplier_category"
] = np.nan

fact_maintenance.loc[
    random_rows(fact_maintenance, 100),
    "maintenance_type"
] = np.nan

# Additional blank values
dim_account.loc[
    random_rows(dim_account, 10),
    "industry"
] = ""

dim_location.loc[
    random_rows(dim_location, 5),
    "city"
] = ""

fact_budget.loc[
    random_rows(fact_budget, 20),
    "budget_category"
] = ""

fact_emissions.loc[
    random_rows(fact_emissions, 20),
    "emissions_category"
] = ""


# ============================================================
# 2. LEADING / TRAILING SPACES
# ============================================================

rows = random_rows(dim_account, 20)
dim_account.loc[rows, "account_name"] = (
    " " + dim_account.loc[rows, "account_name"].astype(str) + " "
)

rows = random_rows(dim_customer, 20)
dim_customer.loc[rows, "customer_name"] = (
    "  " + dim_customer.loc[rows, "customer_name"].astype(str) + "  "
)

rows = random_rows(dim_product, 20)
dim_product.loc[rows, "product_name"] = (
    " " + dim_product.loc[rows, "product_name"].astype(str) + " "
)

rows = random_rows(dim_supplier, 20)
dim_supplier.loc[rows, "supplier_name"] = (
    " " + dim_supplier.loc[rows, "supplier_name"].astype(str) + " "
)

rows = random_rows(dim_employee, 20)
dim_employee.loc[rows, "employee_name"] = (
    " " + dim_employee.loc[rows, "employee_name"].astype(str) + " "
)

rows = random_rows(dim_machine, 20)
dim_machine.loc[rows, "machine_name"] = (
    " " + dim_machine.loc[rows, "machine_name"].astype(str) + " "
)


# ============================================================
# 3. DUPLICATES
# ============================================================

fact_sales = pd.concat(
    [
        fact_sales,
        fact_sales.sample(
            500,
            random_state=SEED
        )
    ],
    ignore_index=True
)

fact_production = pd.concat(
    [
        fact_production,
        fact_production.sample(
            200,
            random_state=SEED
        )
    ],
    ignore_index=True
)

fact_financial_transaction = pd.concat(
    [
        fact_financial_transaction,
        fact_financial_transaction.sample(
            300,
            random_state=SEED
        )
    ],
    ignore_index=True
)


# ============================================================
# 4. INVALID FOREIGN KEYS
# ============================================================

fact_sales.loc[
    random_rows(fact_sales, 500),
    "customer_key"
] = 999999

fact_inventory.loc[
    random_rows(fact_inventory, 500),
    "product_key"
] = 999999

fact_energy.loc[
    random_rows(fact_energy, 100),
    "machine_key"
] = 999999

fact_maintenance.loc[
    random_rows(fact_maintenance, 50),
    "employee_key"
] = 999999


# ============================================================
# 5. INVALID CATEGORIES
# ============================================================

dim_customer.loc[
    random_rows(dim_customer, 50),
    "customer_segment"
] = "Unknown Segment"

dim_location.loc[
    random_rows(dim_location, 5),
    "location_type"
] = "Temporary Facility"

dim_machine.loc[
    random_rows(dim_machine, 20),
    "status"
] = "Unknown"

dim_supplier.loc[
    random_rows(dim_supplier, 10),
    "supplier_category"
] = "Other Supplier"

fact_maintenance.loc[
    random_rows(fact_maintenance, 10),
    "maintenance_type"
] = "Emergency Type"


# ============================================================
# 6. INVALID NUMERIC VALUES
# ============================================================

fact_sales.loc[
    random_rows(fact_sales, 500),
    "quantity"
] = -1

fact_inventory.loc[
    random_rows(fact_inventory, 500),
    "issued_quantity"
] = -10

fact_energy.loc[
    random_rows(fact_energy, 100),
    "energy_consumption"
] = -100

fact_waste.loc[
    random_rows(fact_waste, 100),
    "waste_quantity"
] = -50


# ============================================================
# 7. SALES REVENUE INCONSISTENCY
# ============================================================

sales_issue = random_rows(
    fact_sales,
    500
)

fact_sales.loc[
    sales_issue,
    "revenue"
] = (
    fact_sales.loc[
        sales_issue,
        "quantity"
    ]
    * fact_sales.loc[
        sales_issue,
        "unit_price"
    ]
    * 1.25
).round(2)


# ============================================================
# 8. INVENTORY RECONCILIATION ISSUES
# ============================================================

inventory_issue = random_rows(
    fact_inventory,
    500
)

fact_inventory.loc[
    inventory_issue,
    "closing_quantity"
] = (
    fact_inventory.loc[
        inventory_issue,
        "opening_quantity"
    ]
    + fact_inventory.loc[
        inventory_issue,
        "received_quantity"
    ]
    - fact_inventory.loc[
        inventory_issue,
        "issued_quantity"
    ]
    + 100
)


# ============================================================
# 9. PRODUCTION DEFECT ISSUES
# ============================================================

production_defect_issue = random_rows(
    fact_production,
    200
)

# INVALID:
# Defects are intentionally greater than production.

fact_production.loc[
    production_defect_issue,
    "defect_quantity"
] = (
    fact_production.loc[
        production_defect_issue,
        "produced_quantity"
    ]
    + 10
)


# ============================================================
# 10. PRODUCTION OUTLIERS
# ============================================================

production_outlier = random_rows(
    fact_production,
    100
)

# INVALID OUTLIER:
# Production is intentionally much higher than planned.

fact_production.loc[
    production_outlier,
    "produced_quantity"
] = (
    fact_production.loc[
        production_outlier,
        "planned_quantity"
    ]
    * 3
).astype(int)


# ============================================================
# 11. FINANCIAL OUTLIERS
# ============================================================

financial_outlier = random_rows(
    fact_financial_transaction,
    150
)

fact_financial_transaction.loc[
    financial_outlier,
    "transaction_amount"
] = (
    fact_financial_transaction.loc[
        financial_outlier,
        "transaction_amount"
    ]
    * 10
).round(2)


# ============================================================
# SAVE DATASETS
# ============================================================

print("\nSaving datasets...")

datasets = {
    "dim_date": dim_date,
    "dim_account": dim_account,
    "dim_customer": dim_customer,
    "dim_product": dim_product,
    "dim_supplier": dim_supplier,
    "dim_location": dim_location,
    "dim_employee": dim_employee,
    "dim_machine": dim_machine,
    "fact_sales": fact_sales,
    "fact_production": fact_production,
    "fact_maintenance": fact_maintenance,
    "fact_financial_transaction": fact_financial_transaction,
    "fact_budget": fact_budget,
    "fact_energy": fact_energy,
    "fact_emissions": fact_emissions,
    "fact_waste": fact_waste,
    "fact_inventory": fact_inventory
}

for name, dataframe in datasets.items():
    save_data(dataframe, name)


# ============================================================
# FINAL SUMMARY
# ============================================================

total_rows = sum(
    len(dataframe)
    for dataframe in datasets.values()
)

print("\n========================================")
print("PROJECT ATLAS DATA GENERATION COMPLETE")
print("========================================")
print("All data is synthetic.")
print(f"Date range: {START_DATE} to {END_DATE}")
print(f"Datasets generated: {len(datasets)}")
print(f"Total raw rows: {total_rows:,}")
print(f"Files saved to: {OUTPUT_DIR}")
print("========================================")