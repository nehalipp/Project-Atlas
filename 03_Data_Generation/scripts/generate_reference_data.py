"""
Project Atlas
Phase 3 — Reference Data Generation

Generates the seven approved reference datasets:

    accounts
    customers
    suppliers
    products
    locations
    employees
    machines

All data is synthetic and reproducible.

Temporal fields establish lifecycle starting points that
downstream business facts must respect.
"""

from pathlib import Path
import sys

import numpy as np
import pandas as pd
from faker import Faker


# ============================================================
# CONFIGURATION
# ============================================================

SCRIPT_DIR = Path(__file__).resolve().parent
CONFIG_DIR = SCRIPT_DIR.parent / "config"

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


# ============================================================
# SETUP
# ============================================================

fake = Faker()
fake.seed_instance(SEED)

rng = np.random.default_rng(SEED)

RAW_DATA_DIR.mkdir(
    parents=True,
    exist_ok=True,
)


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
# SYNTHETIC LOCATION ANCHORS
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

OPERATIONAL_LOCATIONS = (
    US_LOCATIONS
    + SWEDISH_LOCATIONS
)


# ============================================================
# HELPERS
# ============================================================

def random_dates(size):
    """Generate dates within the approved Atlas period."""

    start = pd.Timestamp(START_DATE)
    end = pd.Timestamp(END_DATE)

    days = (end - start).days

    offsets = rng.integers(
        0,
        days + 1,
        size,
    )

    return (
        start
        + pd.to_timedelta(
            offsets,
            unit="D",
        )
    ).strftime("%Y-%m-%d")


def save(df, filename):
    """Save a generated reference dataset."""

    path = RAW_DATA_DIR / filename

    df.to_csv(
        path,
        index=False,
    )

    print(
        f"      ✓ {filename:<28}"
        f"{len(df):>10,} records"
    )


# ============================================================
# GENERATORS
# ============================================================

def generate_accounts():

    return pd.DataFrame({
        "account_id": [
            f"ACC-{i:06d}"
            for i in range(1, N_ACCOUNTS + 1)
        ],
        "account_name": [
            f"{fake.company()} Account"
            for _ in range(N_ACCOUNTS)
        ],
        "account_type": rng.choice(
            ACCOUNT_TYPES,
            N_ACCOUNTS,
            p=[0.15, 0.35, 0.35, 0.15],
        ),
        "industry": rng.choice(
            INDUSTRIES,
            N_ACCOUNTS,
        ),
        "country": rng.choice(
            COUNTRIES,
            N_ACCOUNTS,
            p=COUNTRY_WEIGHTS,
        ),
        "status": rng.choice(
            ["Active", "Inactive"],
            N_ACCOUNTS,
            p=[0.95, 0.05],
        ),
    })


def generate_customers(accounts):

    account_ids = rng.choice(
        accounts["account_id"].to_numpy(),
        N_CUSTOMERS,
    )

    country_lookup = (
        accounts
        .set_index("account_id")["country"]
    )

    customer_countries = (
        pd.Series(account_ids)
        .map(country_lookup)
        .to_numpy()
    )

    return pd.DataFrame({
        "customer_id": [
            f"CUST-{i:07d}"
            for i in range(1, N_CUSTOMERS + 1)
        ],
        "account_id": account_ids,
        "customer_name": [
            fake.company()
            for _ in range(N_CUSTOMERS)
        ],
        "customer_segment": rng.choice(
            CUSTOMER_SEGMENTS,
            N_CUSTOMERS,
            p=[0.15, 0.45, 0.30, 0.10],
        ),
        "industry": rng.choice(
            INDUSTRIES,
            N_CUSTOMERS,
        ),
        "country": customer_countries,
        "status": rng.choice(
            ["Active", "Inactive"],
            N_CUSTOMERS,
            p=[0.94, 0.06],
        ),
    })


def generate_suppliers():

    return pd.DataFrame({
        "supplier_id": [
            f"SUP-{i:06d}"
            for i in range(1, N_SUPPLIERS + 1)
        ],
        "supplier_name": [
            fake.company()
            for _ in range(N_SUPPLIERS)
        ],
        "supplier_category": rng.choice(
            SUPPLIER_CATEGORIES,
            N_SUPPLIERS,
        ),
        "country": rng.choice(
            COUNTRIES,
            N_SUPPLIERS,
            p=COUNTRY_WEIGHTS,
        ),
        "status": rng.choice(
            ["Active", "Inactive"],
            N_SUPPLIERS,
            p=[0.95, 0.05],
        ),
    })


def generate_products(suppliers):

    categories = rng.choice(
        PRODUCT_CATEGORIES,
        N_PRODUCTS,
        p=[0.25, 0.25, 0.20, 0.10, 0.20],
    )

    unit_cost = np.round(
        rng.lognormal(
            mean=3.5,
            sigma=0.8,
            size=N_PRODUCTS,
        ),
        2,
    )

    unit_price = np.round(
        unit_cost
        * rng.uniform(1.20, 2.50, N_PRODUCTS),
        2,
    )

    return pd.DataFrame({
        "product_id": [
            f"PROD-{i:07d}"
            for i in range(1, N_PRODUCTS + 1)
        ],
        "supplier_id": rng.choice(
            suppliers["supplier_id"].to_numpy(),
            N_PRODUCTS,
        ),
        "product_name": [
            f"{category} Product {i:05d}"
            for i, category in enumerate(categories, 1)
        ],
        "category": categories,
        "unit_cost": unit_cost,
        "unit_price": unit_price,
        "status": rng.choice(
            ["Active", "Inactive"],
            N_PRODUCTS,
            p=[0.96, 0.04],
        ),
    })


def generate_locations():

    selected_indexes = rng.choice(
        len(OPERATIONAL_LOCATIONS),
        N_LOCATIONS,
        replace=True,
    )

    location_types = rng.choice(
        LOCATION_TYPES,
        N_LOCATIONS,
        p=[0.30, 0.20, 0.15, 0.15, 0.20],
    )

    rows = [
        OPERATIONAL_LOCATIONS[index]
        for index in selected_indexes
    ]

    countries = [
        (
            "United States"
            if index < len(US_LOCATIONS)
            else "Sweden"
        )
        for index in selected_indexes
    ]

    return pd.DataFrame({
        "location_id": [
            f"LOC-{i:04d}"
            for i in range(1, N_LOCATIONS + 1)
        ],
        "location_name": [
            f"{location_types[i]} "
            f"{rows[i][0]} {i + 1:03d}"
            for i in range(N_LOCATIONS)
        ],
        "location_type": location_types,
        "city": [
            row[0]
            for row in rows
        ],
        "state_region": [
            row[1]
            for row in rows
        ],
        "country": countries,
        "status": rng.choice(
            ["Active", "Inactive"],
            N_LOCATIONS,
            p=[0.97, 0.03],
        ),
    })


def generate_employees(locations):

    location_ids = locations["location_id"].to_numpy()

    employee_locations = np.concatenate([
        location_ids,
        rng.choice(
            location_ids,
            N_EMPLOYEES - N_LOCATIONS,
        ),
    ])

    rng.shuffle(employee_locations)

    return pd.DataFrame({
        "employee_id": [
            f"EMP-{i:06d}"
            for i in range(1, N_EMPLOYEES + 1)
        ],
        "location_id": employee_locations,
        "employee_name": [
            fake.name()
            for _ in range(N_EMPLOYEES)
        ],
        "department": rng.choice(
            EMPLOYEE_DEPARTMENTS,
            N_EMPLOYEES,
            p=[0.25, 0.20, 0.10, 0.12,
               0.08, 0.08, 0.07, 0.10],
        ),
        "role": rng.choice(
            EMPLOYEE_ROLES,
            N_EMPLOYEES,
        ),
        "hire_date": random_dates(N_EMPLOYEES),
        "status": rng.choice(
            ["Active", "Inactive"],
            N_EMPLOYEES,
            p=[0.93, 0.07],
        ),
    })


def generate_machines(locations):

    location_ids = locations["location_id"].to_numpy()

    machine_locations = np.concatenate([
        location_ids,
        rng.choice(
            location_ids,
            N_MACHINES - N_LOCATIONS,
        ),
    ])

    rng.shuffle(machine_locations)

    machine_types = rng.choice(
        MACHINE_TYPES,
        N_MACHINES,
    )

    return pd.DataFrame({
        "machine_id": [
            f"MCH-{i:06d}"
            for i in range(1, N_MACHINES + 1)
        ],
        "location_id": machine_locations,
        "machine_name": [
            f"{machine_type} {i:05d}"
            for i, machine_type in enumerate(
                machine_types,
                1,
            )
        ],
        "machine_type": machine_types,
        "installation_date": random_dates(N_MACHINES),
        "status": rng.choice(
            ["Active", "Maintenance", "Inactive"],
            N_MACHINES,
            p=[0.85, 0.10, 0.05],
        ),
    })


# ============================================================
# MAIN
# ============================================================

def main():

    print("=" * 70)
    print("Project Atlas — Reference Data Generation")
    print("=" * 70)

    print("\nGenerating reference datasets...")

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

    total_records = sum([
        len(accounts),
        len(customers),
        len(suppliers),
        len(products),
        len(locations),
        len(employees),
        len(machines),
    ])

    print("\n" + "-" * 70)
    print("GENERATION SUMMARY")
    print("-" * 70)
    print(f"Datasets generated                  : 7")
    print(f"Total records                       : {total_records:,.0f}")
    print(f"Output                              : {RAW_DATA_DIR}")

    print("\n" + "=" * 70)
    print("REFERENCE DATA GENERATION COMPLETE")
    print("=" * 70)


if __name__ == "__main__":
    main()