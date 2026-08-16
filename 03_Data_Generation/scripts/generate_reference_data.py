"""
Project Atlas
Phase 3 — Reference Data Generation

Generates the seven reference/master datasets:

    accounts
    customers
    suppliers
    products
    locations
    employees
    machines

The datasets are synthetic and maintain the relationships
defined in the approved Phase 2 data model.

Generation is reproducible through the centralized configuration.
"""

from pathlib import Path

import numpy as np
import pandas as pd
from faker import Faker

import sys

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

# ============================================================
# Setup
# ============================================================

fake = Faker()
fake.seed_instance(SEED)

rng = np.random.default_rng(SEED)

RAW_DATA_DIR.mkdir(parents=True, exist_ok=True)


# ============================================================
# Business Reference Values
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


# ============================================================
# Geographic Reference Values
# ============================================================

COUNTRIES = [
    "United States",
    "Canada",
    "Mexico",
    "Germany",
    "United Kingdom",
    "Sweden",
]

COUNTRY_WEIGHTS = [
    0.55,  # United States
    0.08,  # Canada
    0.08,  # Mexico
    0.10,  # Germany
    0.09,  # United Kingdom
    0.10,  # Sweden
]


# Operational locations are deliberately defined as
# city + state/region pairs so that geographic values
# remain internally consistent.

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
    US_LOCATIONS + SWEDISH_LOCATIONS
)


# ============================================================
# Helper Functions
# ============================================================

def random_dates(size: int) -> pd.Series:
    """
    Generate reproducible random dates within the project period.
    """

    start = pd.Timestamp(START_DATE)
    end = pd.Timestamp(END_DATE)

    days = (end - start).days

    offsets = rng.integers(
        0,
        days + 1,
        size=size,
    )

    return pd.Series(
        start + pd.to_timedelta(
            offsets,
            unit="D",
        )
    ).dt.strftime("%Y-%m-%d")


def save_dataset(
    df: pd.DataFrame,
    filename: str,
) -> None:
    """
    Save a generated dataset to the raw data directory.
    """

    output_path = RAW_DATA_DIR / filename

    df.to_csv(
        output_path,
        index=False,
    )

    print(
        f"Created {filename}: "
        f"{len(df):,} records"
    )


# ============================================================
# Accounts
# ============================================================

def generate_accounts() -> pd.DataFrame:
    """
    Generate commercial account records.

    Account represents the commercial relationship or
    organizational grouping in the Atlas model.
    """

    account_ids = [
        f"ACC-{i:06d}"
        for i in range(
            1,
            N_ACCOUNTS + 1,
        )
    ]

    account_names = [
        f"{fake.company()} Account"
        for _ in range(N_ACCOUNTS)
    ]

    account_types = rng.choice(
        ACCOUNT_TYPES,
        size=N_ACCOUNTS,
        p=[
            0.15,
            0.35,
            0.35,
            0.15,
        ],
    )

    industries = rng.choice(
        INDUSTRIES,
        size=N_ACCOUNTS,
    )

    countries = rng.choice(
        COUNTRIES,
        size=N_ACCOUNTS,
        p=COUNTRY_WEIGHTS,
    )

    statuses = rng.choice(
        ["Active", "Inactive"],
        size=N_ACCOUNTS,
        p=[
            0.95,
            0.05,
        ],
    )

    df = pd.DataFrame(
        {
            "account_id": account_ids,
            "account_name": account_names,
            "account_type": account_types,
            "industry": industries,
            "country": countries,
            "status": statuses,
        }
    )

    return df


# ============================================================
# Customers
# ============================================================

def generate_customers(
    accounts: pd.DataFrame,
) -> pd.DataFrame:
    """
    Generate customer records linked to existing accounts.

    Customer country is inherited from the associated account
    to maintain a consistent commercial relationship.
    """

    customer_ids = [
        f"CUST-{i:07d}"
        for i in range(
            1,
            N_CUSTOMERS + 1,
        )
    ]

    customer_account_ids = rng.choice(
        accounts["account_id"].values,
        size=N_CUSTOMERS,
    )

    account_ids = pd.Series(
        customer_account_ids
    )

    account_country_lookup = (
        accounts
        .set_index("account_id")["country"]
    )

    customer_countries = account_ids.map(
        account_country_lookup
    )

    df = pd.DataFrame(
        {
            "customer_id": customer_ids,
            "account_id": customer_account_ids,
            "customer_name": [
                fake.company()
                for _ in range(N_CUSTOMERS)
            ],
            "customer_segment": rng.choice(
                CUSTOMER_SEGMENTS,
                size=N_CUSTOMERS,
                p=[
                    0.15,
                    0.45,
                    0.30,
                    0.10,
                ],
            ),
            "industry": rng.choice(
                INDUSTRIES,
                size=N_CUSTOMERS,
            ),
            "country": customer_countries.values,
            "status": rng.choice(
                ["Active", "Inactive"],
                size=N_CUSTOMERS,
                p=[
                    0.94,
                    0.06,
                ],
            ),
        }
    )

    return df


# ============================================================
# Suppliers
# ============================================================

def generate_suppliers() -> pd.DataFrame:
    """
    Generate supplier records.
    """

    supplier_ids = [
        f"SUP-{i:06d}"
        for i in range(
            1,
            N_SUPPLIERS + 1,
        )
    ]

    df = pd.DataFrame(
        {
            "supplier_id": supplier_ids,
            "supplier_name": [
                fake.company()
                for _ in range(N_SUPPLIERS)
            ],
            "supplier_category": rng.choice(
                SUPPLIER_CATEGORIES,
                size=N_SUPPLIERS,
            ),
            "country": rng.choice(
                COUNTRIES,
                size=N_SUPPLIERS,
                p=COUNTRY_WEIGHTS,
            ),
            "status": rng.choice(
                ["Active", "Inactive"],
                size=N_SUPPLIERS,
                p=[
                    0.95,
                    0.05,
                ],
            ),
        }
    )

    return df


# ============================================================
# Products
# ============================================================

def generate_products(
    suppliers: pd.DataFrame,
) -> pd.DataFrame:
    """
    Generate products linked to existing suppliers.

    Each product has one primary supplier in the
    approved Atlas baseline model.
    """

    product_ids = [
        f"PROD-{i:07d}"
        for i in range(
            1,
            N_PRODUCTS + 1,
        )
    ]

    product_supplier_ids = rng.choice(
        suppliers["supplier_id"].values,
        size=N_PRODUCTS,
    )

    categories = rng.choice(
        PRODUCT_CATEGORIES,
        size=N_PRODUCTS,
        p=[
            0.25,
            0.25,
            0.20,
            0.10,
            0.20,
        ],
    )

    unit_cost = np.round(
        rng.lognormal(
            mean=3.5,
            sigma=0.8,
            size=N_PRODUCTS,
        ),
        2,
    )

    markup = rng.uniform(
        1.20,
        2.50,
        size=N_PRODUCTS,
    )

    unit_price = np.round(
        unit_cost * markup,
        2,
    )

    df = pd.DataFrame(
        {
            "product_id": product_ids,
            "supplier_id": product_supplier_ids,
            "product_name": [
                f"{category} Product {i:05d}"
                for i, category in enumerate(
                    categories,
                    start=1,
                )
            ],
            "category": categories,
            "unit_cost": unit_cost,
            "unit_price": unit_price,
            "status": rng.choice(
                ["Active", "Inactive"],
                size=N_PRODUCTS,
                p=[
                    0.96,
                    0.04,
                ],
            ),
        }
    )

    return df


# ============================================================
# Locations
# ============================================================

def generate_locations() -> pd.DataFrame:
    """
    Generate geographically coherent operational locations.

    Operational locations are currently represented in the
    United States and Sweden using valid city/state-region pairs.
    """

    location_ids = [
        f"LOC-{i:04d}"
        for i in range(
            1,
            N_LOCATIONS + 1,
        )
    ]

    location_types = rng.choice(
        LOCATION_TYPES,
        size=N_LOCATIONS,
        p=[
            0.30,
            0.20,
            0.15,
            0.15,
            0.20,
        ],
    )

    selected_indices = rng.integers(
        0,
        len(OPERATIONAL_LOCATIONS),
        size=N_LOCATIONS,
    )

    cities = [
        OPERATIONAL_LOCATIONS[index][0]
        for index in selected_indices
    ]

    state_regions = [
        OPERATIONAL_LOCATIONS[index][1]
        for index in selected_indices
    ]

    us_location_count = len(
        US_LOCATIONS
    )

    countries = [
        (
            "United States"
            if index < us_location_count
            else "Sweden"
        )
        for index in selected_indices
    ]

    df = pd.DataFrame(
        {
            "location_id": location_ids,
            "location_name": [
                f"{location_type} {i:03d}"
                for i, location_type in enumerate(
                    location_types,
                    start=1,
                )
            ],
            "location_type": location_types,
            "city": cities,
            "state_region": state_regions,
            "country": countries,
            "status": rng.choice(
                ["Active", "Inactive"],
                size=N_LOCATIONS,
                p=[
                    0.97,
                    0.03,
                ],
            ),
        }
    )

    return df


# ============================================================
# Employees
# ============================================================

def generate_employees(
    locations: pd.DataFrame,
) -> pd.DataFrame:
    """
    Generate employees linked to existing locations.
    """

    employee_ids = [
        f"EMP-{i:06d}"
        for i in range(
            1,
            N_EMPLOYEES + 1,
        )
    ]

    employee_location_ids = rng.choice(
        locations["location_id"].values,
        size=N_EMPLOYEES,
    )

    departments = rng.choice(
        EMPLOYEE_DEPARTMENTS,
        size=N_EMPLOYEES,
        p=[
            0.25,
            0.20,
            0.10,
            0.12,
            0.08,
            0.08,
            0.07,
            0.10,
        ],
    )

    roles = rng.choice(
        EMPLOYEE_ROLES,
        size=N_EMPLOYEES,
    )

    hire_dates = random_dates(
        N_EMPLOYEES
    )

    df = pd.DataFrame(
        {
            "employee_id": employee_ids,
            "location_id": employee_location_ids,
            "employee_name": [
                fake.name()
                for _ in range(N_EMPLOYEES)
            ],
            "department": departments,
            "role": roles,
            "hire_date": hire_dates,
            "status": rng.choice(
                ["Active", "Inactive"],
                size=N_EMPLOYEES,
                p=[
                    0.93,
                    0.07,
                ],
            ),
        }
    )

    return df


# ============================================================
# Machines
# ============================================================

def generate_machines(
    locations: pd.DataFrame,
) -> pd.DataFrame:
    """
    Generate machines linked to existing locations.
    """

    machine_ids = [
        f"MCH-{i:06d}"
        for i in range(
            1,
            N_MACHINES + 1,
        )
    ]

    machine_location_ids = rng.choice(
        locations["location_id"].values,
        size=N_MACHINES,
    )

    machine_types = rng.choice(
        MACHINE_TYPES,
        size=N_MACHINES,
    )

    installation_dates = random_dates(
        N_MACHINES
    )

    df = pd.DataFrame(
        {
            "machine_id": machine_ids,
            "location_id": machine_location_ids,
            "machine_name": [
                f"{machine_type} {i:05d}"
                for i, machine_type in enumerate(
                    machine_types,
                    start=1,
                )
            ],
            "machine_type": machine_types,
            "installation_date": installation_dates,
            "status": rng.choice(
                MACHINE_STATUSES,
                size=N_MACHINES,
                p=[
                    0.85,
                    0.10,
                    0.05,
                ],
            ),
        }
    )

    return df


# ============================================================
# Main
# ============================================================

def main() -> None:
    """
    Generate all seven reference datasets.
    """

    print("=" * 60)
    print("Project Atlas — Reference Data Generation")
    print("=" * 60)

    print("\nGenerating accounts...")
    accounts = generate_accounts()
    save_dataset(
        accounts,
        "accounts.csv",
    )

    print("\nGenerating customers...")
    customers = generate_customers(
        accounts
    )
    save_dataset(
        customers,
        "customers.csv",
    )

    print("\nGenerating suppliers...")
    suppliers = generate_suppliers()
    save_dataset(
        suppliers,
        "suppliers.csv",
    )

    print("\nGenerating products...")
    products = generate_products(
        suppliers
    )
    save_dataset(
        products,
        "products.csv",
    )

    print("\nGenerating locations...")
    locations = generate_locations()
    save_dataset(
        locations,
        "locations.csv",
    )

    print("\nGenerating employees...")
    employees = generate_employees(
        locations
    )
    save_dataset(
        employees,
        "employees.csv",
    )

    print("\nGenerating machines...")
    machines = generate_machines(
        locations
    )
    save_dataset(
        machines,
        "machines.csv",
    )

    print("\n" + "=" * 60)
    print("Reference data generation complete.")
    print(f"Output directory: {RAW_DATA_DIR}")
    print("=" * 60)


if __name__ == "__main__":
    main()
