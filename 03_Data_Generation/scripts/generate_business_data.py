"""
Project Atlas
Phase 3 — Business Data Generation

Generates the nine clean business-process datasets using the
validated reference datasets.

This script creates the baseline source data only.
Controlled data-quality issues are introduced separately by
inject_quality_issues.py.
"""

from pathlib import Path

import numpy as np
import pandas as pd


# ============================================================
# Project Paths
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parents[2]

RAW_DATA_DIR = PROJECT_ROOT / "data" / "raw"


# ============================================================
# Configuration
# ============================================================

SEED = 42

START_DATE = "2019-01-01"
END_DATE = "2025-12-31"

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
# Random Generator
# ============================================================

rng = np.random.default_rng(SEED)


# ============================================================
# Utility Functions
# ============================================================

def load_reference_data():
    """Load the seven validated reference datasets."""

    files = {
        "accounts": "accounts.csv",
        "customers": "customers.csv",
        "suppliers": "suppliers.csv",
        "products": "products.csv",
        "locations": "locations.csv",
        "employees": "employees.csv",
        "machines": "machines.csv",
    }

    data = {}

    for name, filename in files.items():

        path = RAW_DATA_DIR / filename

        if not path.exists():
            raise FileNotFoundError(
                f"Required reference dataset not found: {path}"
            )

        data[name] = pd.read_csv(path)

    return data


def random_dates(size):
    """Generate random dates within the approved period."""

    start = pd.Timestamp(START_DATE)
    end = pd.Timestamp(END_DATE)

    days = (end - start).days

    offsets = rng.integers(
        0,
        days + 1,
        size=size,
    )

    return start + pd.to_timedelta(
        offsets,
        unit="D",
    )


def save_dataset(df, filename):
    """Save generated dataset to data/raw."""

    path = RAW_DATA_DIR / filename

    df.to_csv(
        path,
        index=False,
    )

    print(
        f"Created {filename}: "
        f"{len(df):,} records"
    )


def weighted_sample(values, size):
    """
    Sample values with a mild concentration effect.

    This creates different activity levels across entities
    without introducing unnecessarily complex modeling.
    """

    values = np.asarray(values)

    weights = np.linspace(
        1.5,
        0.5,
        len(values),
    )

    weights = weights / weights.sum()

    return rng.choice(
        values,
        size=size,
        replace=True,
        p=weights,
    )


# ============================================================
# Sales
# ============================================================

def generate_sales(data):

    customers = data["customers"]
    accounts = data["accounts"]
    products = data["products"]
    locations = data["locations"]

    customer_sample = weighted_sample(
        customers["customer_id"].values,
        N_SALES,
    )

    customer_lookup = (
        customers
        .set_index("customer_id")
    )

    sampled_customers = (
        customer_lookup
        .loc[customer_sample]
        .reset_index()
    )

    product_sample = weighted_sample(
        products["product_id"].values,
        N_SALES,
    )

    product_lookup = (
        products
        .set_index("product_id")
    )

    sampled_products = (
        product_lookup
        .loc[product_sample]
        .reset_index()
    )

    location_sample = rng.choice(
        locations["location_id"].values,
        size=N_SALES,
        replace=True,
    )

    quantity = rng.integers(
        1,
        101,
        size=N_SALES,
    )

    unit_price = (
        sampled_products["unit_price"]
        .to_numpy()
    )

    discount_rate = rng.uniform(
        0,
        0.15,
        size=N_SALES,
    )

    gross_amount = (
        quantity * unit_price
    )

    discount_amount = (
        gross_amount * discount_rate
    )

    revenue = (
        gross_amount - discount_amount
    )

    df = pd.DataFrame({
        "transaction_id": [
            f"SO-{i:07d}"
            for i in range(1, N_SALES + 1)
        ],
        "transaction_date": random_dates(N_SALES),
        "account_id": sampled_customers["account_id"].values,
        "customer_id": sampled_customers["customer_id"].values,
        "product_id": sampled_products["product_id"].values,
        "location_id": location_sample,
        "quantity": quantity,
        "unit_price": np.round(unit_price, 2),
        "discount_amount": np.round(discount_amount, 2),
        "revenue": np.round(revenue, 2),
    })

    return df


# ============================================================
# Production
# ============================================================

def generate_production(data):

    products = data["products"]
    machines = data["machines"]
    employees = data["employees"]

    machine_sample = rng.choice(
        machines["machine_id"].values,
        size=N_PRODUCTION,
        replace=True,
    )

    machine_lookup = (
        machines
        .set_index("machine_id")
    )

    sampled_machines = (
        machine_lookup
        .loc[machine_sample]
        .reset_index()
    )

    employee_sample = rng.choice(
        employees["employee_id"].values,
        size=N_PRODUCTION,
        replace=True,
    )

    product_sample = rng.choice(
        products["product_id"].values,
        size=N_PRODUCTION,
        replace=True,
    )

    production_hours = np.round(
        rng.uniform(
            2,
            16,
            size=N_PRODUCTION,
        ),
        2,
    )

    planned_quantity = (
        production_hours
        * rng.uniform(
            40,
            100,
            size=N_PRODUCTION,
        )
    ).astype(int)

    defect_rate = rng.uniform(
        0.005,
        0.05,
        size=N_PRODUCTION,
    )

    produced_quantity = (
        planned_quantity
        * rng.uniform(
            0.90,
            1.05,
            size=N_PRODUCTION,
        )
    ).astype(int)

    defect_quantity = (
        produced_quantity
        * defect_rate
    ).astype(int)

    df = pd.DataFrame({
        "production_id": [
            f"PR-{i:07d}"
            for i in range(1, N_PRODUCTION + 1)
        ],
        "production_date": random_dates(
            N_PRODUCTION
        ),
        "product_id": product_sample,
        "location_id": sampled_machines["location_id"].values,
        "machine_id": sampled_machines["machine_id"].values,
        "employee_id": employee_sample,
        "planned_quantity": planned_quantity,
        "produced_quantity": produced_quantity,
        "defect_quantity": defect_quantity,
        "production_hours": production_hours,
    })

    return df


# ============================================================
# Maintenance
# ============================================================

def generate_maintenance(data):

    machines = data["machines"]
    employees = data["employees"]

    machine_sample = rng.choice(
        machines["machine_id"].values,
        size=N_MAINTENANCE,
        replace=True,
    )

    machine_lookup = (
        machines
        .set_index("machine_id")
    )

    sampled_machines = (
        machine_lookup
        .loc[machine_sample]
        .reset_index()
    )

    employee_sample = rng.choice(
        employees["employee_id"].values,
        size=N_MAINTENANCE,
        replace=True,
    )

    maintenance_types = rng.choice(
        [
            "Preventive",
            "Corrective",
            "Inspection",
            "Emergency",
        ],
        size=N_MAINTENANCE,
        p=[
            0.45,
            0.30,
            0.15,
            0.10,
        ],
    )

    maintenance_hours = np.round(
        rng.uniform(
            1,
            12,
            size=N_MAINTENANCE,
        ),
        2,
    )

    downtime_hours = np.round(
        maintenance_hours
        * rng.uniform(
            0.50,
            1.50,
            size=N_MAINTENANCE,
        ),
        2,
    )

    maintenance_cost = np.round(
        maintenance_hours
        * rng.uniform(
            75,
            350,
            size=N_MAINTENANCE,
        ),
        2,
    )

    df = pd.DataFrame({
        "maintenance_id": [
            f"MT-{i:07d}"
            for i in range(1, N_MAINTENANCE + 1)
        ],
        "maintenance_date": random_dates(
            N_MAINTENANCE
        ),
        "location_id": sampled_machines["location_id"].values,
        "machine_id": sampled_machines["machine_id"].values,
        "employee_id": employee_sample,
        "maintenance_type": maintenance_types,
        "maintenance_hours": maintenance_hours,
        "downtime_hours": downtime_hours,
        "maintenance_cost": maintenance_cost,
    })

    return df


# ============================================================
# Financial Transactions
# ============================================================

def generate_financial_transactions(data):

    locations = data["locations"]

    location_sample = rng.choice(
        locations["location_id"].values,
        size=N_FINANCIAL,
        replace=True,
    )

    categories = np.array([
        "Revenue",
        "Materials",
        "Labor",
        "Maintenance",
        "Utilities",
        "Transportation",
        "Operating Expense",
        "Other Expense",
    ])

    category = rng.choice(
        categories,
        size=N_FINANCIAL,
        p=[
            0.20,
            0.18,
            0.15,
            0.10,
            0.10,
            0.10,
            0.12,
            0.05,
        ],
    )

    amount = np.round(
        rng.lognormal(
            mean=7.0,
            sigma=1.0,
            size=N_FINANCIAL,
        ),
        2,
    )

    df = pd.DataFrame({
        "financial_transaction_id": [
            f"FT-{i:07d}"
            for i in range(1, N_FINANCIAL + 1)
        ],
        "transaction_date": random_dates(
            N_FINANCIAL
        ),
        "location_id": location_sample,
        "transaction_type": np.where(
            category == "Revenue",
            "Revenue",
            "Expense",
        ),
        "category": category,
        "amount": amount,
    })

    return df


# ============================================================
# Budget
# ============================================================

def generate_budget(data):

    locations = data["locations"]

    budget_categories = [
        "Revenue",
        "Materials",
        "Labor",
        "Maintenance",
        "Utilities",
        "Transportation",
        "Operating Expense",
    ]

    location_sample = rng.choice(
        locations["location_id"].values,
        size=N_BUDGET,
        replace=True,
    )

    periods = pd.date_range(
        START_DATE,
        END_DATE,
        freq="MS",
    )

    budget_dates = rng.choice(
        periods,
        size=N_BUDGET,
        replace=True,
    )

    categories = rng.choice(
        budget_categories,
        size=N_BUDGET,
        replace=True,
    )

    budget_amount = np.round(
        rng.lognormal(
            mean=10.0,
            sigma=0.75,
            size=N_BUDGET,
        ),
        2,
    )

    df = pd.DataFrame({
        "budget_id": [
            f"BG-{i:07d}"
            for i in range(1, N_BUDGET + 1)
        ],
        "budget_date": budget_dates,
        "location_id": location_sample,
        "budget_category": categories,
        "budget_amount": budget_amount,
    })

    return df


# ============================================================
# Energy
# ============================================================

def generate_energy(data):

    locations = data["locations"]

    location_sample = rng.choice(
        locations["location_id"].values,
        size=N_ENERGY,
        replace=True,
    )

    energy_types = rng.choice(
        [
            "Electricity",
            "Natural Gas",
            "Fuel",
            "Steam",
        ],
        size=N_ENERGY,
        p=[
            0.55,
            0.20,
            0.15,
            0.10,
        ],
    )

    consumption = np.round(
        rng.lognormal(
            mean=5.5,
            sigma=0.7,
            size=N_ENERGY,
        ),
        2,
    )

    units = np.where(
        energy_types == "Electricity",
        "kWh",
        np.where(
            energy_types == "Natural Gas",
            "m3",
            np.where(
                energy_types == "Fuel",
                "L",
                "kg",
            ),
        ),
    )

    df = pd.DataFrame({
        "energy_id": [
            f"EN-{i:07d}"
            for i in range(1, N_ENERGY + 1)
        ],
        "measurement_date": random_dates(
            N_ENERGY
        ),
        "location_id": location_sample,
        "energy_type": energy_types,
        "consumption": consumption,
        "unit": units,
    })

    return df


# ============================================================
# Emissions
# ============================================================

def generate_emissions(data):

    locations = data["locations"]

    location_sample = rng.choice(
        locations["location_id"].values,
        size=N_EMISSIONS,
        replace=True,
    )

    sources = rng.choice(
        [
            "Electricity",
            "Natural Gas",
            "Fuel",
            "Transportation",
            "Process",
        ],
        size=N_EMISSIONS,
        p=[
            0.30,
            0.25,
            0.20,
            0.15,
            0.10,
        ],
    )

    co2e_amount = np.round(
        rng.lognormal(
            mean=5.0,
            sigma=0.8,
            size=N_EMISSIONS,
        ),
        2,
    )

    df = pd.DataFrame({
        "emissions_id": [
            f"EM-{i:07d}"
            for i in range(1, N_EMISSIONS + 1)
        ],
        "emissions_date": random_dates(
            N_EMISSIONS
        ),
        "location_id": location_sample,
        "emission_source": sources,
        "co2e_amount": co2e_amount,
        "unit": "kg CO2e",
    })

    return df


# ============================================================
# Waste
# ============================================================

def generate_waste(data):

    locations = data["locations"]

    location_sample = rng.choice(
        locations["location_id"].values,
        size=N_WASTE,
        replace=True,
    )

    waste_types = rng.choice(
        [
            "Metal",
            "Plastic",
            "Paper",
            "Chemical",
            "General",
            "Organic",
        ],
        size=N_WASTE,
        p=[
            0.25,
            0.20,
            0.15,
            0.10,
            0.20,
            0.10,
        ],
    )

    disposal_methods = rng.choice(
        [
            "Recycling",
            "Landfill",
            "Treatment",
            "Reuse",
        ],
        size=N_WASTE,
        p=[
            0.40,
            0.30,
            0.20,
            0.10,
        ],
    )

    waste_quantity = np.round(
        rng.lognormal(
            mean=3.5,
            sigma=0.8,
            size=N_WASTE,
        ),
        2,
    )

    df = pd.DataFrame({
        "waste_id": [
            f"WA-{i:07d}"
            for i in range(1, N_WASTE + 1)
        ],
        "waste_date": random_dates(
            N_WASTE
        ),
        "location_id": location_sample,
        "waste_type": waste_types,
        "disposal_method": disposal_methods,
        "waste_quantity": waste_quantity,
        "unit": "kg",
    })

    return df


# ============================================================
# Inventory
# ============================================================

def generate_inventory(data):

    products = data["products"]
    locations = data["locations"]

    # Generate unique Product + Location + Date combinations.
    #
    # There are enough possible combinations across the
    # seven-year period to support the approved 500,000 rows.

    dates = pd.date_range(
        START_DATE,
        END_DATE,
        freq="D",
    )

    total_possible = (
        len(products)
        * len(locations)
        * len(dates)
    )

    if N_INVENTORY > total_possible:
        raise ValueError(
            "Requested inventory volume exceeds "
            "the number of available Product + Location + Date "
            "combinations."
        )

    product_indices = rng.integers(
        0,
        len(products),
        size=N_INVENTORY,
    )

    location_indices = rng.integers(
        0,
        len(locations),
        size=N_INVENTORY,
    )

    date_indices = rng.integers(
        0,
        len(dates),
        size=N_INVENTORY,
    )

    combinations = pd.DataFrame({
        "product_id": products.iloc[
            product_indices
        ]["product_id"].values,

        "location_id": locations.iloc[
            location_indices
        ]["location_id"].values,

        "inventory_date": dates[
            date_indices
        ],
    })

    combinations = (
        combinations
        .drop_duplicates(
            subset=[
                "product_id",
                "location_id",
                "inventory_date",
            ]
        )
        .reset_index(drop=True)
    )

    # If duplicate sampling reduced the dataset below target,
    # generate additional combinations until the target is met.

    while len(combinations) < N_INVENTORY:

        additional = pd.DataFrame({
            "product_id": rng.choice(
                products["product_id"].values,
                size=N_INVENTORY - len(combinations),
                replace=True,
            ),
            "location_id": rng.choice(
                locations["location_id"].values,
                size=N_INVENTORY - len(combinations),
                replace=True,
            ),
            "inventory_date": rng.choice(
                dates,
                size=N_INVENTORY - len(combinations),
                replace=True,
            ),
        })

        combinations = pd.concat(
            [
                combinations,
                additional,
            ],
            ignore_index=True,
        )

        combinations = (
            combinations
            .drop_duplicates(
                subset=[
                    "product_id",
                    "location_id",
                    "inventory_date",
                ]
            )
            .reset_index(drop=True)
        )

    combinations = combinations.iloc[
        :N_INVENTORY
    ].copy()

    opening_quantity = rng.integers(
        0,
        1000,
        size=N_INVENTORY,
    )

    received_quantity = rng.integers(
        0,
        500,
        size=N_INVENTORY,
    )

    issued_quantity = rng.integers(
        0,
        400,
        size=N_INVENTORY,
    )

    closing_quantity = (
        opening_quantity
        + received_quantity
        - issued_quantity
    )

    # Prevent negative stock in the clean baseline.
    negative_mask = closing_quantity < 0

    issued_quantity[negative_mask] = (
        opening_quantity[negative_mask]
        + received_quantity[negative_mask]
    )

    closing_quantity = (
        opening_quantity
        + received_quantity
        - issued_quantity
    )

    reorder_point = rng.integers(
        50,
        300,
        size=N_INVENTORY,
    )

    combinations["inventory_id"] = [
        f"IN-{i:07d}"
        for i in range(1, N_INVENTORY + 1)
    ]

    combinations["opening_quantity"] = (
        opening_quantity
    )

    combinations["received_quantity"] = (
        received_quantity
    )

    combinations["issued_quantity"] = (
        issued_quantity
    )

    combinations["closing_quantity"] = (
        closing_quantity
    )

    combinations["reorder_point"] = (
        reorder_point
    )

    return combinations[
        [
            "inventory_id",
            "inventory_date",
            "product_id",
            "location_id",
            "opening_quantity",
            "received_quantity",
            "issued_quantity",
            "closing_quantity",
            "reorder_point",
        ]
    ]


# ============================================================
# Main
# ============================================================

def main():

    print("=" * 60)
    print("Project Atlas — Business Data Generation")
    print("=" * 60)

    print("\nLoading reference datasets...")

    data = load_reference_data()

    print("Reference data loaded successfully.")

    print("\nGenerating sales...")
    sales = generate_sales(data)
    save_dataset(
        sales,
        "sales.csv",
    )

    print("\nGenerating production...")
    production = generate_production(data)
    save_dataset(
        production,
        "production.csv",
    )

    print("\nGenerating maintenance...")
    maintenance = generate_maintenance(data)
    save_dataset(
        maintenance,
        "maintenance.csv",
    )

    print("\nGenerating financial transactions...")
    financial = generate_financial_transactions(data)
    save_dataset(
        financial,
        "financial_transactions.csv",
    )

    print("\nGenerating budget...")
    budget = generate_budget(data)
    save_dataset(
        budget,
        "budget.csv",
    )

    print("\nGenerating energy...")
    energy = generate_energy(data)
    save_dataset(
        energy,
        "energy.csv",
    )

    print("\nGenerating emissions...")
    emissions = generate_emissions(data)
    save_dataset(
        emissions,
        "emissions.csv",
    )

    print("\nGenerating waste...")
    waste = generate_waste(data)
    save_dataset(
        waste,
        "waste.csv",
    )

    print("\nGenerating inventory...")
    inventory = generate_inventory(data)
    save_dataset(
        inventory,
        "inventory.csv",
    )

    print("\n" + "=" * 60)
    print("Business data generation complete.")
    print(f"Output directory: {RAW_DATA_DIR}")
    print("=" * 60)


if __name__ == "__main__":
    main()
