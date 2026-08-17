"""
Project Atlas
Phase 3 — Reference Data Generation

Creates the seven reference datasets:
accounts, customers, suppliers, products,
locations, employees, machines.

All data is synthetic and reproducible.
"""

from pathlib import Path
import sys

import numpy as np
import pandas as pd
from faker import Faker


# ============================================================
# PATHS AND CONFIGURATION
# ============================================================

SCRIPT_DIR = Path(__file__).resolve().parent
DATA_GENERATION_DIR = SCRIPT_DIR.parent
CONFIG_DIR = DATA_GENERATION_DIR / "config"

sys.path.insert(0, str(CONFIG_DIR))

from generation_config import (
    END_DATE,
    N_ACCOUNTS,
    N_CUSTOMERS,
    N_EMPLOYEES,
    N_LOCATIONS,
    N_MACHINES,
    N_PRODUCTS,
    N_SUPPLIERS,
    RAW_DATA_DIR,
    SEED,
    START_DATE,
)


fake = Faker()
fake.seed_instance(SEED)
rng = np.random.default_rng(SEED)

RAW_DATA_DIR.mkdir(parents=True, exist_ok=True)


# ============================================================
# BUSINESS VALUES
# ============================================================

ACCOUNT_TYPES = [
    "Enterprise",
    "Mid-Market",
    "Small Business",
    "Distributor",
]

CUSTOMER_SEGMENTS = [
    "Enterprise",
    "Commercial",
    "SMB",
    "Strategic",
]

INDUSTRIES = [
    "Automotive",
    "Construction",
    "Consumer Goods",
    "Electronics",
    "Food & Beverage",
    "Healthcare",
    "Industrial Equipment",
    "Manufacturing",
    "Retail",
    "Technology",
]

SUPPLIER_CATEGORIES = [
    "Raw Materials",
    "Components",
    "Packaging",
    "Equipment",
    "Maintenance",
]

PRODUCT_CATEGORIES = [
    "Components",
    "Finished Goods",
    "Industrial Parts",
    "Packaging",
    "Raw Materials",
]

LOCATION_TYPES = [
    "Plant",
    "Warehouse",
    "Distribution Center",
    "Office",
    "Store",
]

EMPLOYEE_DEPARTMENTS = [
    "Operations",
    "Production",
    "Maintenance",
    "Supply Chain",
    "Finance",
    "Sales",
    "Human Resources",
    "IT",
]

EMPLOYEE_ROLES = [
    "Operator",
    "Supervisor",
    "Manager",
    "Engineer",
    "Analyst",
    "Coordinator",
    "Technician",
    "Specialist",
]

MACHINE_TYPES = [
    "CNC Machine",
    "Press",
    "Assembly Line",
    "Packaging Machine",
    "Furnace",
    "Conveyor",
    "Robotic Cell",
    "Cutting Machine",
]

MACHINE_STATUSES = [
    "Active",
    "Maintenance",
    "Inactive",
]

COUNTRIES = [
    "United States",
    "Canada",
    "Mexico",
    "Germany",
    "United Kingdom",
    "Sweden",
]

COUNTRY_WEIGHTS = [
    0.55,
    0.08,
    0.08,
    0.10,
    0.09,
    0.10,
]


# ============================================================
# LOCATION REFERENCE
# ============================================================

US_LOCATIONS = [
    ("Pittsburgh", "Pennsylvania"),
    ("Philadelphia", "Pennsylvania"),
    ("Allentown", "Pennsylvania"),
    ("Columbus", "Ohio"),
    ("Cleveland", "Ohio"),
    ("Detroit", "Michigan"),
    ("Chicago", "Illinois"),
    ("Indianapolis", "Indiana"),
    ("New York", "New York"),
    ("Newark", "New Jersey"),
    ("Charlotte", "North Carolina"),
    ("Atlanta", "Georgia"),
    ("Dallas", "Texas"),
    ("Houston", "Texas"),
]

SWEDISH_LOCATIONS = [
    ("Stockholm", "Stockholm County"),
    ("Gothenburg", "Västra Götaland County"),
    ("Malmö", "Skåne County"),
    ("Linköping", "Östergötland County"),
    ("Jönköping", "Jönköping County"),
    ("Västerås", "Västmanland County"),
    ("Örebro", "Örebro County"),
    ("Helsingborg", "Skåne County"),
]

OPERATIONAL_LOCATIONS = US_LOCATIONS + SWEDISH_LOCATIONS


# ============================================================
# HELPERS
# ============================================================

def random_dates(size):
    """Generate dates within the project date range."""

    start = pd.Timestamp(START_DATE)
    end = pd.Timestamp(END_DATE)

    days = (end - start).days

    offsets = rng.integers(
        0,
        days + 1,
        size
    )

    return (
        start
        + pd.to_timedelta(offsets, unit="D")
    ).strftime("%Y-%m-%d")


def save(df, filename):
    """Save a dataframe to the raw data folder."""

    df.to_csv(
        RAW_DATA_DIR / filename,
        index=False
    )

    print(
        f"Created {filename}: "
        f"{len(df):,} records"
    )


# ============================================================
# ACCOUNTS
# ============================================================

def generate_accounts():

    n = N_ACCOUNTS

    return pd.DataFrame({
        "account_id": [
            f"ACC-{i:06d}"
            for i in range(1, n + 1)
        ],

        "account_name": [
            f"{fake.company()} Account"
            for _ in range(n)
        ],

        "account_type": rng.choice(
            ACCOUNT_TYPES,
            n,
            p=[0.15, 0.35, 0.35, 0.15]
        ),

        "industry": rng.choice(
            INDUSTRIES,
            n
        ),

        "country": rng.choice(
            COUNTRIES,
            n,
            p=COUNTRY_WEIGHTS
        ),

        "status": rng.choice(
            ["Active", "Inactive"],
            n,
            p=[0.95, 0.05]
        ),
    })


# ============================================================
# CUSTOMERS
# ============================================================

def generate_customers(accounts):

    n = N_CUSTOMERS

    account_ids = rng.choice(
        accounts["account_id"].to_numpy(),
        n
    )

    country_lookup = accounts.set_index(
        "account_id"
    )["country"]

    return pd.DataFrame({
        "customer_id": [
            f"CUST-{i:07d}"
            for i in range(1, n + 1)
        ],

        "account_id": account_ids,

        "customer_name": [
            fake.company()
            for _ in range(n)
        ],

        "customer_segment": rng.choice(
            CUSTOMER_SEGMENTS,
            n,
            p=[0.15, 0.45, 0.30, 0.10]
        ),

        "industry": rng.choice(
            INDUSTRIES,
            n
        ),

        "country": pd.Series(
            account_ids
        ).map(country_lookup).to_numpy(),

        "status": rng.choice(
            ["Active", "Inactive"],
            n,
            p=[0.94, 0.06]
        ),
    })


# ============================================================
# SUPPLIERS
# ============================================================

def generate_suppliers():

    n = N_SUPPLIERS

    return pd.DataFrame({
        "supplier_id": [
            f"SUP-{i:06d}"
            for i in range(1, n + 1)
        ],

        "supplier_name": [
            fake.company()
            for _ in range(n)
        ],

        "supplier_category": rng.choice(
            SUPPLIER_CATEGORIES,
            n
        ),

        "country": rng.choice(
            COUNTRIES,
            n,
            p=COUNTRY_WEIGHTS
        ),

        "status": rng.choice(
            ["Active", "Inactive"],
            n,
            p=[0.95, 0.05]
        ),
    })


# ============================================================
# PRODUCTS
# ============================================================

def generate_products(suppliers):

    n = N_PRODUCTS

    categories = rng.choice(
        PRODUCT_CATEGORIES,
        n,
        p=[0.25, 0.25, 0.20, 0.10, 0.20]
    )

    unit_cost = np.round(
        rng.lognormal(
            mean=3.5,
            sigma=0.8,
            size=n
        ),
        2
    )

    unit_price = np.round(
        unit_cost * rng.uniform(1.20, 2.50, n),
        2
    )

    return pd.DataFrame({
        "product_id": [
            f"PROD-{i:07d}"
            for i in range(1, n + 1)
        ],

        "supplier_id": rng.choice(
            suppliers["supplier_id"].to_numpy(),
            n
        ),

        "product_name": [
            f"{category} Product {i:05d}"
            for i, category in enumerate(
                categories,
                start=1
            )
        ],

        "category": categories,

        "unit_cost": unit_cost,

        "unit_price": unit_price,

        "status": rng.choice(
            ["Active", "Inactive"],
            n,
            p=[0.96, 0.04]
        ),
    })


# ============================================================
# LOCATIONS
# ============================================================

def generate_locations():

    n = N_LOCATIONS

    location_types = rng.choice(
        LOCATION_TYPES,
        n,
        p=[0.30, 0.20, 0.15, 0.15, 0.20]
    )

    indices = rng.integers(
        0,
        len(OPERATIONAL_LOCATIONS),
        n
    )

    cities = [
        OPERATIONAL_LOCATIONS[i][0]
        for i in indices
    ]

    regions = [
        OPERATIONAL_LOCATIONS[i][1]
        for i in indices
    ]

    us_count = len(US_LOCATIONS)

    countries = [
        "United States" if i < us_count else "Sweden"
        for i in indices
    ]

    return pd.DataFrame({
        "location_id": [
            f"LOC-{i:04d}"
            for i in range(1, n + 1)
        ],

        "location_name": [
            f"{location_type} {i:03d}"
            for i, location_type in enumerate(
                location_types,
                start=1
            )
        ],

        "location_type": location_types,

        "city": cities,

        "state_region": regions,

        "country": countries,

        "status": rng.choice(
            ["Active", "Inactive"],
            n,
            p=[0.97, 0.03]
        ),
    })


# ============================================================
# EMPLOYEES
# ============================================================

def generate_employees(locations):

    n = N_EMPLOYEES

    return pd.DataFrame({
        "employee_id": [
            f"EMP-{i:06d}"
            for i in range(1, n + 1)
        ],

        "location_id": rng.choice(
            locations["location_id"].to_numpy(),
            n
        ),

        "employee_name": [
            fake.name()
            for _ in range(n)
        ],

        "department": rng.choice(
            EMPLOYEE_DEPARTMENTS,
            n,
            p=[0.25, 0.20, 0.10, 0.12,
               0.08, 0.08, 0.07, 0.10]
        ),

        "role": rng.choice(
            EMPLOYEE_ROLES,
            n
        ),

        "hire_date": random_dates(n),

        "status": rng.choice(
            ["Active", "Inactive"],
            n,
            p=[0.93, 0.07]
        ),
    })


# ============================================================
# MACHINES
# ============================================================

def generate_machines(locations):

    n = N_MACHINES

    machine_types = rng.choice(
        MACHINE_TYPES,
        n
    )

    return pd.DataFrame({
        "machine_id": [
            f"MCH-{i:06d}"
            for i in range(1, n + 1)
        ],

        "location_id": rng.choice(
            locations["location_id"].to_numpy(),
            n
        ),

        "machine_name": [
            f"{machine_type} {i:05d}"
            for i, machine_type in enumerate(
                machine_types,
                start=1
            )
        ],

        "machine_type": machine_types,

        "installation_date": random_dates(n),

        "status": rng.choice(
            MACHINE_STATUSES,
            n,
            p=[0.85, 0.10, 0.05]
        ),
    })


# ============================================================
# MAIN
# ============================================================

def main():

    print("=" * 60)
    print("Project Atlas — Reference Data Generation")
    print("=" * 60)

    accounts = generate_accounts()
    save(accounts, "accounts.csv")

    customers = generate_customers(accounts)
    save(customers, "customers.csv")

    suppliers = generate_suppliers()
    save(suppliers, "suppliers.csv")

    products = generate_products(suppliers)
    save(products, "products.csv")

    locations = generate_locations()
    save(locations, "locations.csv")

    employees = generate_employees(locations)
    save(employees, "employees.csv")

    machines = generate_machines(locations)
    save(machines, "machines.csv")

    print("\nReference data generation complete.")


if __name__ == "__main__":
    main()
