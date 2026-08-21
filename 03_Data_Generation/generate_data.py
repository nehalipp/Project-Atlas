"""
Project Atlas
Phase 3 - Synthetic Data Generation

Generates the synthetic raw operational data for the
17 approved Atlas warehouse datasets.

All data is synthetic.
Random seed = 42.
Date range = 2019-01-01 to 2025-12-31.

Phase 3 intentionally introduces a small, controlled number
of realistic data-quality issues into the raw datasets.

Phase 4 will profile, validate, remediate and validate the
trusted datasets.

Approved datasets:

Dimensions:
    dim_date
    dim_account
    dim_customer
    dim_product
    dim_supplier
    dim_location
    dim_employee
    dim_machine

Facts:
    fact_sales
    fact_production
    fact_maintenance
    fact_financial_transaction
    fact_budget
    fact_energy
    fact_emissions
    fact_waste
    fact_inventory
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

# Attribute dates are generated before the operational period.
# This prevents normal operational activity from occurring
# before an employee hire date or machine installation date.
ATTRIBUTE_START_DATE = "2016-01-01"
ATTRIBUTE_END_DATE = "2018-12-31"

# Always save inside:
# 03_Data_Generation/data/raw/
SCRIPT_DIR = Path(__file__).resolve().parent
OUTPUT_DIR = SCRIPT_DIR / "data" / "raw"

OUTPUT_DIR.mkdir(
    parents=True,
    exist_ok=True
)

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
    """Create business identifiers."""

    return [
        f"{prefix}-{i:06d}"
        for i in range(1, number + 1)
    ]


def random_dates(number):
    """Create random operational dates."""

    dates = pd.date_range(
        START_DATE,
        END_DATE
    )

    return rng.choice(
        dates,
        size=number
    )


def random_attribute_dates(number):
    """Create dates before the operational period."""

    dates = pd.date_range(
        ATTRIBUTE_START_DATE,
        ATTRIBUTE_END_DATE
    )

    return rng.choice(
        dates,
        size=number
    )


def random_indices(dataframe, percentage):
    """
    Return deterministic random row indexes.

    The percentage is intentionally small because the raw data
    should remain mostly realistic.
    """

    count = max(
        1,
        int(len(dataframe) * percentage)
    )

    return rng.choice(
        dataframe.index,
        size=count,
        replace=False
    )


def save_data(dataframe, table_name):
    """Save a dataframe as a CSV file."""

    dataframe.to_csv(
        OUTPUT_DIR / f"{table_name}.csv",
        index=False
    )

    print(
        f"{table_name}: "
        f"{len(dataframe):,} rows"
    )


# ============================================================
# DIM_DATE
# ============================================================

print("\nGenerating dimensions...")

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


# ============================================================
# DIM_ACCOUNT
# ============================================================

dim_account = pd.DataFrame({
    "account_key": range(
        1,
        N_ACCOUNT + 1
    ),
    "account_id": make_ids(
        "ACC",
        N_ACCOUNT
    ),
    "account_name": [
        fake.company()
        for _ in range(N_ACCOUNT)
    ],
    "account_type": rng.choice(
        ACCOUNT_TYPES,
        N_ACCOUNT
    ),
    "industry": rng.choice(
        INDUSTRIES,
        N_ACCOUNT
    ),
    "country": rng.choice(
        COUNTRIES,
        N_ACCOUNT
    ),
    "status": rng.choice(
        ["Active", "Inactive"],
        N_ACCOUNT,
        p=[0.90, 0.10]
    )
})


# ============================================================
# DIM_CUSTOMER
# ============================================================

dim_customer = pd.DataFrame({
    "customer_key": range(
        1,
        N_CUSTOMER + 1
    ),
    "customer_id": make_ids(
        "CUS",
        N_CUSTOMER
    ),
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


# ============================================================
# DIM_SUPPLIER
# ============================================================

dim_supplier = pd.DataFrame({
    "supplier_key": range(
        1,
        N_SUPPLIER + 1
    ),
    "supplier_id": make_ids(
        "SUP",
        N_SUPPLIER
    ),
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


# ============================================================
# DIM_PRODUCT
# ============================================================

unit_cost = np.round(
    rng.uniform(
        10,
        500,
        N_PRODUCT
    ),
    2
)

unit_price = np.round(
    unit_cost * rng.uniform(
        1.25,
        2.50,
        N_PRODUCT
    ),
    2
)

dim_product = pd.DataFrame({
    "product_key": range(
        1,
        N_PRODUCT + 1
    ),
    "product_id": make_ids(
        "PROD",
        N_PRODUCT
    ),
    "supplier_key": rng.choice(
        dim_supplier["supplier_key"],
        N_PRODUCT
    ),
    "product_name": [
        f"Atlas Product {i}"
        for i in range(
            1,
            N_PRODUCT + 1
        )
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
        [
            "Each",
            "Kg",
            "Liter",
            "Meter"
        ],
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


# ============================================================
# DIM_LOCATION
# ============================================================

dim_location = pd.DataFrame({
    "location_key": range(
        1,
        N_LOCATION + 1
    ),
    "location_id": make_ids(
        "LOC",
        N_LOCATION
    ),
    "location_name": [
        f"Atlas Facility {i}"
        for i in range(
            1,
            N_LOCATION + 1
        )
    ],
    "location_type": rng.choice(
        LOCATION_TYPES,
        N_LOCATION
    ),
    "city": [
        fake.city()
        for _ in range(N_LOCATION)
    ],
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


# ============================================================
# DIM_EMPLOYEE
# ============================================================

dim_employee = pd.DataFrame({
    "employee_key": range(
        1,
        N_EMPLOYEE + 1
    ),
    "employee_id": make_ids(
        "EMP",
        N_EMPLOYEE
    ),
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
    "hire_date": random_attribute_dates(
        N_EMPLOYEE
    ),
    "status": rng.choice(
        ["Active", "Inactive"],
        N_EMPLOYEE,
        p=[0.92, 0.08]
    )
})


# ============================================================
# DIM_MACHINE
# ============================================================

dim_machine = pd.DataFrame({
    "machine_key": range(
        1,
        N_MACHINE + 1
    ),
    "machine_id": make_ids(
        "MCH",
        N_MACHINE
    ),
    "location_key": rng.choice(
        dim_location["location_key"],
        N_MACHINE
    ),
    "machine_name": [
        f"Atlas Machine {i}"
        for i in range(
            1,
            N_MACHINE + 1
        )
    ],
    "machine_type": rng.choice(
        MACHINE_TYPES,
        N_MACHINE
    ),
    "installation_date": random_attribute_dates(
        N_MACHINE
    ),
    "status": rng.choice(
        [
            "Operational",
            "Maintenance",
            "Inactive"
        ],
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
# FACT_SALES
# ============================================================

print("\nGenerating facts...")

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

sales_discount = np.round(
    sales_quantity
    * sales_unit_price
    * rng.uniform(
        0,
        0.15,
        N_SALES
    ),
    2
)

sales_revenue = np.round(
    sales_quantity
    * sales_unit_price
    - sales_discount,
    2
)

fact_sales = pd.DataFrame({
    "sales_key": range(
        1,
        N_SALES + 1
    ),
    "transaction_id": make_ids(
        "SAL",
        N_SALES
    ),
    "date_key": sales_dates.strftime(
        "%Y%m%d"
    ).astype(int),
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
    "discount_amount": sales_discount,
    "revenue": sales_revenue
})


# ============================================================
# FACT_PRODUCTION
# ============================================================

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

produced_quantity = np.round(
    planned_quantity
    * rng.uniform(
        0.80,
        1.10,
        N_PRODUCTION
    )
).astype(int)

fact_production = pd.DataFrame({
    "production_key": range(
        1,
        N_PRODUCTION + 1
    ),
    "production_id": make_ids(
        "PRD",
        N_PRODUCTION
    ),
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
    "defect_quantity": rng.integers(
        0,
        21,
        N_PRODUCTION
    ),
    "production_hours": np.round(
        rng.uniform(
            1,
            12,
            N_PRODUCTION
        ),
        2
    )
})


# ============================================================
# FACT_MAINTENANCE
# ============================================================

maintenance_machine_keys = rng.choice(
    dim_machine["machine_key"],
    N_MAINTENANCE
)

maintenance_location_keys = [
    machine_locations[machine]
    for machine in maintenance_machine_keys
]

fact_maintenance = pd.DataFrame({
    "maintenance_key": range(
        1,
        N_MAINTENANCE + 1
    ),
    "maintenance_id": make_ids(
        "MNT",
        N_MAINTENANCE
    ),
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
        rng.uniform(
            0.5,
            8,
            N_MAINTENANCE
        ),
        2
    ),
    "downtime_hours": np.round(
        rng.uniform(
            0.5,
            24,
            N_MAINTENANCE
        ),
        2
    ),
    "maintenance_cost": np.round(
        rng.uniform(
            100,
            10_000,
            N_MAINTENANCE
        ),
        2
    )
})


# ============================================================
# FACT_FINANCIAL_TRANSACTION
# ============================================================

fact_financial_transaction = pd.DataFrame({
    "financial_transaction_key": range(
        1,
        N_FINANCIAL + 1
    ),
    "transaction_id": make_ids(
        "FIN",
        N_FINANCIAL
    ),
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
        rng.uniform(
            100,
            50_000,
            N_FINANCIAL
        ),
        2
    )
})


# ============================================================
# FACT_BUDGET
# ============================================================

fact_budget = pd.DataFrame({
    "budget_key": range(
        1,
        N_BUDGET + 1
    ),
    "budget_id": make_ids(
        "BUD",
        N_BUDGET
    ),
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
        rng.uniform(
            10_000,
            500_000,
            N_BUDGET
        ),
        2
    )
})


# ============================================================
# FACT_ENERGY
# ============================================================

energy_machine_keys = rng.choice(
    dim_machine["machine_key"],
    N_ENERGY
)

energy_location_keys = [
    machine_locations[machine]
    for machine in energy_machine_keys
]

fact_energy = pd.DataFrame({
    "energy_key": range(
        1,
        N_ENERGY + 1
    ),
    "energy_id": make_ids(
        "ENG",
        N_ENERGY
    ),
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
        rng.uniform(
            100,
            10_000,
            N_ENERGY
        ),
        3
    )
})


# ============================================================
# FACT_EMISSIONS
# ============================================================

fact_emissions = pd.DataFrame({
    "emissions_key": range(
        1,
        N_EMISSIONS + 1
    ),
    "emissions_id": make_ids(
        "EMS",
        N_EMISSIONS
    ),
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
        rng.uniform(
            10,
            5_000,
            N_EMISSIONS
        ),
        3
    )
})


# ============================================================
# FACT_WASTE
# ============================================================

fact_waste = pd.DataFrame({
    "waste_key": range(
        1,
        N_WASTE + 1
    ),
    "waste_id": make_ids(
        "WST",
        N_WASTE
    ),
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
        rng.uniform(
            1,
            1_000,
            N_WASTE
        ),
        3
    )
})


# ============================================================
# FACT_INVENTORY
# ============================================================

# Inventory grain:
# One inventory position for one product,
# location and date.

inventory_dates = pd.date_range(
    START_DATE,
    END_DATE
)

inventory_date_count = len(
    inventory_dates
)

inventory_numbers = rng.choice(
    inventory_date_count
    * N_PRODUCT
    * N_LOCATION,
    size=N_INVENTORY,
    replace=False
)

date_index = (
    inventory_numbers
    // (N_PRODUCT * N_LOCATION)
)

remaining = (
    inventory_numbers
    % (N_PRODUCT * N_LOCATION)
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
    rng.integers(
        0,
        2_000,
        N_INVENTORY
    ),
    available_quantity
)

closing_quantity = (
    opening_quantity
    + received_quantity
    - issued_quantity
)

fact_inventory = pd.DataFrame({
    "inventory_key": range(
        1,
        N_INVENTORY + 1
    ),
    "inventory_id": make_ids(
        "INV",
        N_INVENTORY
    ),
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
# CONTROLLED RAW DATA QUALITY ISSUES
# ============================================================

print(
    "\nIntroducing controlled raw-data "
    "quality issues..."
)


# ============================================================
# 1. MISSING VALUES
# ============================================================

missing_customer = random_indices(
    dim_customer,
    0.002
)

dim_customer.loc[
    missing_customer,
    "country"
] = np.nan


missing_product = random_indices(
    dim_product,
    0.002
)

dim_product.loc[
    missing_product,
    "subcategory"
] = np.nan


missing_supplier = random_indices(
    dim_supplier,
    0.002
)

dim_supplier.loc[
    missing_supplier,
    "supplier_category"
] = np.nan


missing_maintenance = random_indices(
    fact_maintenance,
    0.002
)

fact_maintenance.loc[
    missing_maintenance,
    "maintenance_type"
] = np.nan


# ============================================================
# 2. DUPLICATE RECORDS
# ============================================================

sales_duplicates = fact_sales.sample(
    n=500,
    random_state=SEED
)

fact_sales = pd.concat(
    [
        fact_sales,
        sales_duplicates
    ],
    ignore_index=True
)


production_duplicates = fact_production.sample(
    n=200,
    random_state=SEED
)

fact_production = pd.concat(
    [
        fact_production,
        production_duplicates
    ],
    ignore_index=True
)


financial_duplicates = fact_financial_transaction.sample(
    n=300,
    random_state=SEED
)

fact_financial_transaction = pd.concat(
    [
        fact_financial_transaction,
        financial_duplicates
    ],
    ignore_index=True
)


# ============================================================
# 3. INVALID FOREIGN-KEY REFERENCES
# ============================================================

invalid_customer_fk = random_indices(
    fact_sales,
    0.001
)

fact_sales.loc[
    invalid_customer_fk,
    "customer_key"
] = 999999


invalid_product_fk = random_indices(
    fact_inventory,
    0.001
)

fact_inventory.loc[
    invalid_product_fk,
    "product_key"
] = 999999


invalid_machine_fk = random_indices(
    fact_energy,
    0.001
)

fact_energy.loc[
    invalid_machine_fk,
    "machine_key"
] = 999999


invalid_employee_fk = random_indices(
    fact_maintenance,
    0.001
)

fact_maintenance.loc[
    invalid_employee_fk,
    "employee_key"
] = 999999


# ============================================================
# 4. INVALID CATEGORICAL VALUES
# ============================================================

invalid_customer_segment = random_indices(
    dim_customer,
    0.001
)

dim_customer.loc[
    invalid_customer_segment,
    "customer_segment"
] = "Unknown Segment"


invalid_location_type = random_indices(
    dim_location,
    0.01
)

dim_location.loc[
    invalid_location_type,
    "location_type"
] = "Temporary Facility"


invalid_machine_status = random_indices(
    dim_machine,
    0.01
)

dim_machine.loc[
    invalid_machine_status,
    "status"
] = "Unknown"


invalid_supplier_category = random_indices(
    dim_supplier,
    0.01
)

dim_supplier.loc[
    invalid_supplier_category,
    "supplier_category"
] = "Other Supplier"


# ============================================================
# 5. INVALID NUMERIC VALUES
# ============================================================

negative_sales_quantity = random_indices(
    fact_sales,
    0.001
)

fact_sales.loc[
    negative_sales_quantity,
    "quantity"
] = -1


negative_inventory_quantity = random_indices(
    fact_inventory,
    0.001
)

fact_inventory.loc[
    negative_inventory_quantity,
    "issued_quantity"
] = -10


negative_energy = random_indices(
    fact_energy,
    0.001
)

fact_energy.loc[
    negative_energy,
    "energy_consumption"
] = -100


negative_waste = random_indices(
    fact_waste,
    0.001
)

fact_waste.loc[
    negative_waste,
    "waste_quantity"
] = -50


# ============================================================
# 6. SALES REVENUE INCONSISTENCIES
# ============================================================

revenue_issue_indices = random_indices(
    fact_sales,
    0.001
)

fact_sales.loc[
    revenue_issue_indices,
    "revenue"
] = (
    fact_sales.loc[
        revenue_issue_indices,
        "revenue"
    ]
    * 1.10
).round(2)


# ============================================================
# 7. INVENTORY RECONCILIATION ISSUES
# ============================================================

inventory_issue_indices = random_indices(
    fact_inventory,
    0.001
)

fact_inventory.loc[
    inventory_issue_indices,
    "closing_quantity"
] = (
    fact_inventory.loc[
        inventory_issue_indices,
        "closing_quantity"
    ]
    + 100
)


# ============================================================
# 8. PRODUCTION QUALITY ISSUES
# ============================================================

production_issue_indices = random_indices(
    fact_production,
    0.001
)

fact_production.loc[
    production_issue_indices,
    "defect_quantity"
] = (
    fact_production.loc[
        production_issue_indices,
        "produced_quantity"
    ]
    + 10
)


# ============================================================
# 9. PRODUCTION OUTLIERS
# ============================================================

production_outlier_indices = random_indices(
    fact_production,
    0.0005
)

fact_production.loc[
    production_outlier_indices,
    "produced_quantity"
] = (
    fact_production.loc[
        production_outlier_indices,
        "planned_quantity"
    ]
    * 3
).astype(int)


# ============================================================
# 10. FINANCIAL TRANSACTION OUTLIERS
# ============================================================

financial_outlier_indices = random_indices(
    fact_financial_transaction,
    0.0005
)

fact_financial_transaction.loc[
    financial_outlier_indices,
    "transaction_amount"
] = (
    fact_financial_transaction.loc[
        financial_outlier_indices,
        "transaction_amount"
    ]
    * 10
).round(2)

# ============================================================
# SAVE DATASETS
# ============================================================

print(
    "\nSaving datasets..."
)

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
    save_data(
        dataframe,
        name
    )


# ============================================================
# FINAL SUMMARY
# ============================================================

total_rows = sum(
    len(dataframe)
    for dataframe in datasets.values()
)

print(
    "\n========================================"
)

print(
    "PROJECT ATLAS DATA GENERATION COMPLETE"
)

print(
    "========================================"
)

print(
    "All data is synthetic."
)

print(
    f"Date range: {START_DATE} to {END_DATE}"
)

print(
    f"Datasets generated: {len(datasets)}"
)

print(
    f"Total raw rows: {total_rows:,}"
)

print(
    f"Files saved to: {OUTPUT_DIR}"
)

print(
    "========================================"
)