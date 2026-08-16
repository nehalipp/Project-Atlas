"""
Project Atlas
Enterprise Decision Intelligence Platform

Business Data Generation
-------------------------
Generates the nine transactional/business-process datasets:

    sales
    production
    maintenance
    financial_transactions
    budget
    energy
    emissions
    waste
    inventory

Reference datasets must already exist in:

    data/raw/

Reference datasets:
    accounts.csv
    customers.csv
    suppliers.csv
    products.csv
    locations.csv
    employees.csv
    machines.csv

All generated data is synthetic and intended for portfolio
and demonstration purposes only.
"""

from pathlib import Path

import numpy as np
import pandas as pd


# ============================================================
# PROJECT PATHS
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parents[2]

RAW_DIR = PROJECT_ROOT / "data" / "raw"


# ============================================================
# GENERATION CONFIGURATION
# ============================================================

RANDOM_SEED = 42

START_DATE = pd.Timestamp("2019-01-01")
END_DATE = pd.Timestamp("2025-12-31")

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
# RANDOM NUMBER GENERATOR
# ============================================================

rng = np.random.default_rng(RANDOM_SEED)


# ============================================================
# HELPER FUNCTIONS
# ============================================================

def random_dates(size):
    """
    Generate random dates within the approved project date range.
    """
    days = (END_DATE - START_DATE).days

    return START_DATE + pd.to_timedelta(
        rng.integers(0, days + 1, size=size),
        unit="D"
    )


def load_reference_data():
    """
    Load the seven reference datasets required by the
    transactional data generators.
    """

    print("Loading reference datasets...")

    required_files = [
        "accounts.csv",
        "customers.csv",
        "suppliers.csv",
        "products.csv",
        "locations.csv",
        "employees.csv",
        "machines.csv",
    ]

    missing_files = [
        file_name
        for file_name in required_files
        if not (RAW_DIR / file_name).exists()
    ]

    if missing_files:
        raise FileNotFoundError(
            "The following reference datasets are missing:\n"
            + "\n".join(f" - {file}" for file in missing_files)
            + "\n\nRun generate_reference_data.py first."
        )

    references = {
        "accounts": pd.read_csv(RAW_DIR / "accounts.csv"),
        "customers": pd.read_csv(RAW_DIR / "customers.csv"),
        "suppliers": pd.read_csv(RAW_DIR / "suppliers.csv"),
        "products": pd.read_csv(RAW_DIR / "products.csv"),
        "locations": pd.read_csv(RAW_DIR / "locations.csv"),
        "employees": pd.read_csv(RAW_DIR / "employees.csv"),
        "machines": pd.read_csv(RAW_DIR / "machines.csv"),
    }

    print("Reference data loaded successfully.\n")

    return references


# ============================================================
# SALES
# ============================================================

def generate_sales(references):
    """
    Generate sales transaction data.

    Grain:
        One row per sales transaction line.

    Relationships:
        Date
        Account
        Customer
        Product
        Location
    """

    print("Generating sales...")

    customers = references["customers"]
    products = references["products"]
    locations = references["locations"]

    customer_sample = customers.iloc[
        rng.integers(0, len(customers), N_SALES)
    ].reset_index(drop=True)

    product_sample = products.iloc[
        rng.integers(0, len(products), N_SALES)
    ].reset_index(drop=True)

    location_sample = locations.iloc[
        rng.integers(0, len(locations), N_SALES)
    ].reset_index(drop=True)

    quantities = rng.integers(1, 101, N_SALES)

    unit_prices = product_sample["unit_price"].to_numpy()

    revenue = quantities * unit_prices

    sales = pd.DataFrame({
        "transaction_id": [
            f"TXN-{i:08d}"
            for i in range(1, N_SALES + 1)
        ],
        "transaction_date": random_dates(N_SALES),
        "account_id": customer_sample["account_id"].values,
        "customer_id": customer_sample["customer_id"].values,
        "product_id": product_sample["product_id"].values,
        "location_id": location_sample["location_id"].values,
        "quantity": quantities,
        "unit_price": np.round(unit_prices, 2),
        "revenue": np.round(revenue, 2),
    })

    sales.to_csv(RAW_DIR / "sales.csv", index=False)

    print(f"Created sales.csv: {len(sales):,} records")


# ============================================================
# PRODUCTION
# ============================================================

def generate_production(references):
    """
    Generate production activity data.

    Grain:
        One row per production activity.

    IMPORTANT LOCATION LOGIC:

        Machine
           ↓
        Machine Location
           ↓
        Employee from same Location
           ↓
        Production Event

    Therefore:

        production.location_id
        =
        machine.location_id
        =
        employee.location_id

    This preserves the approved Phase 2 relationship.
    """

    print("Generating production...")

    products = references["products"]
    machines = references["machines"]
    employees = references["employees"]

    # --------------------------------------------------------
    # Build employee lookup by location
    # --------------------------------------------------------

    employees_by_location = {
        location_id: group["employee_id"].to_numpy()
        for location_id, group in employees.groupby("location_id")
    }

    # --------------------------------------------------------
    # Select products
    # --------------------------------------------------------

    product_sample = products.iloc[
        rng.integers(0, len(products), N_PRODUCTION)
    ].reset_index(drop=True)

    # --------------------------------------------------------
    # Select machines FIRST
    # --------------------------------------------------------

    machine_sample = machines.iloc[
        rng.integers(0, len(machines), N_PRODUCTION)
    ].reset_index(drop=True)

    machine_ids = machine_sample["machine_id"].to_numpy()
    machine_locations = machine_sample["location_id"].to_numpy()

    # --------------------------------------------------------
    # Select employee from the SAME machine location
    # --------------------------------------------------------

    employee_ids = []

    for location_id in machine_locations:

        available_employees = employees_by_location.get(location_id)

        if available_employees is None or len(available_employees) == 0:
            raise ValueError(
                f"No employees found for production location: {location_id}"
            )

        employee_ids.append(
            rng.choice(available_employees)
        )

    employee_ids = np.array(employee_ids)

    # --------------------------------------------------------
    # Generate production quantities
    # --------------------------------------------------------

    planned_quantity = rng.integers(
        50,
        1001,
        N_PRODUCTION
    )

    production_quantity = np.floor(
        planned_quantity * rng.uniform(
            0.85,
            1.05,
            N_PRODUCTION
        )
    ).astype(int)

    production_quantity = np.maximum(
        production_quantity,
        0
    )

    defect_quantity = np.floor(
        production_quantity
        * rng.uniform(
            0.00,
            0.05,
            N_PRODUCTION
        )
    ).astype(int)

    defect_quantity = np.minimum(
        defect_quantity,
        production_quantity
    )

    production = pd.DataFrame({
        "production_id": [
            f"PROD-{i:08d}"
            for i in range(1, N_PRODUCTION + 1)
        ],
        "production_date": random_dates(N_PRODUCTION),
        "product_id": product_sample["product_id"].values,
        "location_id": machine_locations,
        "machine_id": machine_ids,
        "employee_id": employee_ids,
        "planned_quantity": planned_quantity,
        "production_quantity": production_quantity,
        "defect_quantity": defect_quantity,
    })

    production.to_csv(
        RAW_DIR / "production.csv",
        index=False
    )

    print(
        f"Created production.csv: "
        f"{len(production):,} records"
    )


# ============================================================
# MAINTENANCE
# ============================================================

def generate_maintenance(references):
    """
    Generate maintenance events.

    Grain:
        One row per maintenance event.

    Machine and employee are selected so that both belong
    to the same operational location.
    """

    print("Generating maintenance...")

    machines = references["machines"]
    employees = references["employees"]

    employees_by_location = {
        location_id: group["employee_id"].to_numpy()
        for location_id, group in employees.groupby("location_id")
    }

    machine_sample = machines.iloc[
        rng.integers(0, len(machines), N_MAINTENANCE)
    ].reset_index(drop=True)

    machine_ids = machine_sample["machine_id"].to_numpy()
    locations = machine_sample["location_id"].to_numpy()

    employee_ids = []

    for location_id in locations:

        available_employees = employees_by_location.get(location_id)

        if available_employees is None or len(available_employees) == 0:
            raise ValueError(
                f"No employees found for maintenance location: "
                f"{location_id}"
            )

        employee_ids.append(
            rng.choice(available_employees)
        )

    maintenance_types = np.array([
        "Preventive",
        "Corrective",
        "Inspection",
    ])

    maintenance = pd.DataFrame({
        "maintenance_id": [
            f"MAINT-{i:08d}"
            for i in range(1, N_MAINTENANCE + 1)
        ],
        "maintenance_date": random_dates(N_MAINTENANCE),
        "location_id": locations,
        "machine_id": machine_ids,
        "employee_id": employee_ids,
        "maintenance_type": rng.choice(
            maintenance_types,
            N_MAINTENANCE
        ),
        "maintenance_hours": np.round(
            rng.uniform(1, 12, N_MAINTENANCE),
            2
        ),
        "downtime_hours": np.round(
            rng.uniform(0, 24, N_MAINTENANCE),
            2
        ),
        "maintenance_cost": np.round(
            rng.uniform(100, 5000, N_MAINTENANCE),
            2
        ),
    })

    maintenance.to_csv(
        RAW_DIR / "maintenance.csv",
        index=False
    )

    print(
        f"Created maintenance.csv: "
        f"{len(maintenance):,} records"
    )


# ============================================================
# FINANCIAL TRANSACTIONS
# ============================================================

def generate_financial_transactions(references):
    """
    Generate financial transactions.

    Grain:
        One row per financial transaction.
    """

    print("Generating financial transactions...")

    locations = references["locations"]

    location_ids = rng.choice(
        locations["location_id"].to_numpy(),
        N_FINANCIAL
    )

    categories = np.array([
        "Revenue",
        "Payroll",
        "Operations",
        "Maintenance",
        "Utilities",
        "Procurement",
        "Transportation",
    ])

    transaction_types = np.array([
        "Income",
        "Expense",
    ])

    transaction_type = rng.choice(
        transaction_types,
        N_FINANCIAL,
        p=[0.30, 0.70]
    )

    amounts = np.round(
        rng.uniform(100, 100000, N_FINANCIAL),
        2
    )

    financial_transactions = pd.DataFrame({
        "financial_transaction_id": [
            f"FIN-{i:08d}"
            for i in range(1, N_FINANCIAL + 1)
        ],
        "transaction_date": random_dates(N_FINANCIAL),
        "location_id": location_ids,
        "category": rng.choice(
            categories,
            N_FINANCIAL
        ),
        "transaction_type": transaction_type,
        "amount": amounts,
    })

    financial_transactions.to_csv(
        RAW_DIR / "financial_transactions.csv",
        index=False
    )

    print(
        f"Created financial_transactions.csv: "
        f"{len(financial_transactions):,} records"
    )


# ============================================================
# BUDGET
# ============================================================

def generate_budget(references):
    """
    Generate budget records.

    Grain:
        One row per budget record.
    """

    print("Generating budget...")

    locations = references["locations"]

    budget_categories = np.array([
        "Operations",
        "Maintenance",
        "Payroll",
        "Utilities",
        "Procurement",
        "Transportation",
        "Sustainability",
    ])

    budget = pd.DataFrame({
        "budget_id": [
            f"BUD-{i:08d}"
            for i in range(1, N_BUDGET + 1)
        ],
        "budget_date": random_dates(N_BUDGET),
        "location_id": rng.choice(
            locations["location_id"].to_numpy(),
            N_BUDGET
        ),
        "budget_category": rng.choice(
            budget_categories,
            N_BUDGET
        ),
        "budget_amount": np.round(
            rng.uniform(
                10000,
                500000,
                N_BUDGET
            ),
            2
        ),
    })

    budget.to_csv(
        RAW_DIR / "budget.csv",
        index=False
    )

    print(
        f"Created budget.csv: "
        f"{len(budget):,} records"
    )


# ============================================================
# ENERGY
# ============================================================

def generate_energy(references):
    """
    Generate energy measurements.

    Grain:
        One row per energy measurement.
    """

    print("Generating energy...")

    locations = references["locations"]

    energy_types = np.array([
        "Electricity",
        "Natural Gas",
        "Diesel",
        "Steam",
    ])

    energy = pd.DataFrame({
        "energy_id": [
            f"ENG-{i:08d}"
            for i in range(1, N_ENERGY + 1)
        ],
        "measurement_date": random_dates(N_ENERGY),
        "location_id": rng.choice(
            locations["location_id"].to_numpy(),
            N_ENERGY
        ),
        "energy_type": rng.choice(
            energy_types,
            N_ENERGY
        ),
        "energy_quantity": np.round(
            rng.uniform(
                100,
                10000,
                N_ENERGY
            ),
            2
        ),
        "energy_cost": np.round(
            rng.uniform(
                50,
                5000,
                N_ENERGY
            ),
            2
        ),
    })

    energy.to_csv(
        RAW_DIR / "energy.csv",
        index=False
    )

    print(
        f"Created energy.csv: "
        f"{len(energy):,} records"
    )


# ============================================================
# EMISSIONS
# ============================================================

def generate_emissions(references):
    """
    Generate emissions records.

    Grain:
        One row per emissions record.
    """

    print("Generating emissions...")

    locations = references["locations"]

    emission_sources = np.array([
        "Electricity",
        "Natural Gas",
        "Diesel",
        "Manufacturing Process",
        "Transportation",
    ])

    emissions = pd.DataFrame({
        "emissions_id": [
            f"EMI-{i:08d}"
            for i in range(1, N_EMISSIONS + 1)
        ],
        "emissions_date": random_dates(N_EMISSIONS),
        "location_id": rng.choice(
            locations["location_id"].to_numpy(),
            N_EMISSIONS
        ),
        "emission_source": rng.choice(
            emission_sources,
            N_EMISSIONS
        ),
        "emissions_quantity": np.round(
            rng.uniform(
                10,
                5000,
                N_EMISSIONS
            ),
            2
        ),
    })

    emissions.to_csv(
        RAW_DIR / "emissions.csv",
        index=False
    )

    print(
        f"Created emissions.csv: "
        f"{len(emissions):,} records"
    )


# ============================================================
# WASTE
# ============================================================

def generate_waste(references):
    """
    Generate waste records.

    Grain:
        One row per waste record.
    """

    print("Generating waste...")

    locations = references["locations"]

    waste_types = np.array([
        "Metal",
        "Plastic",
        "Chemical",
        "General",
        "Recyclable",
    ])

    disposal_methods = np.array([
        "Recycled",
        "Landfill",
        "Treatment",
        "Incineration",
    ])

    waste = pd.DataFrame({
        "waste_id": [
            f"WST-{i:08d}"
            for i in range(1, N_WASTE + 1)
        ],
        "waste_date": random_dates(N_WASTE),
        "location_id": rng.choice(
            locations["location_id"].to_numpy(),
            N_WASTE
        ),
        "waste_type": rng.choice(
            waste_types,
            N_WASTE
        ),
        "waste_quantity": np.round(
            rng.uniform(
                1,
                1000,
                N_WASTE
            ),
            2
        ),
        "disposal_method": rng.choice(
            disposal_methods,
            N_WASTE
        ),
    })

    waste.to_csv(
        RAW_DIR / "waste.csv",
        index=False
    )

    print(
        f"Created waste.csv: "
        f"{len(waste):,} records"
    )


# ============================================================
# INVENTORY
# ============================================================

def generate_inventory(references):
    """
    Generate inventory snapshot data.

    Grain:
        One row per product, location, and inventory date.

    This is a periodic snapshot fact.
    """

    print("Generating inventory...")

    products = references["products"]
    locations = references["locations"]

    # --------------------------------------------------------
    # Create a unique Date + Product + Location grain
    # --------------------------------------------------------

    total_combinations = N_INVENTORY

    product_ids = rng.choice(
        products["product_id"].to_numpy(),
        total_combinations
    )

    location_ids = rng.choice(
        locations["location_id"].to_numpy(),
        total_combinations
    )

    dates = random_dates(total_combinations)

    inventory = pd.DataFrame({
        "inventory_id": [
            f"INV-{i:08d}"
            for i in range(1, total_combinations + 1)
        ],
        "inventory_date": dates,
        "product_id": product_ids,
        "location_id": location_ids,
    })

    # Remove any accidental duplicate grain combinations
    # and continue generating until the target count is reached.

    inventory = inventory.drop_duplicates(
        subset=[
            "inventory_date",
            "product_id",
            "location_id",
        ]
    )

    while len(inventory) < N_INVENTORY:

        needed = N_INVENTORY - len(inventory)

        additional = pd.DataFrame({
            "inventory_id": [
                f"INV-TEMP-{i}"
                for i in range(needed)
            ],
            "inventory_date": random_dates(needed),
            "product_id": rng.choice(
                products["product_id"].to_numpy(),
                needed
            ),
            "location_id": rng.choice(
                locations["location_id"].to_numpy(),
                needed
            ),
        })

        inventory = pd.concat(
            [inventory, additional],
            ignore_index=True
        )

        inventory = inventory.drop_duplicates(
            subset=[
                "inventory_date",
                "product_id",
                "location_id",
            ]
        )

    inventory = inventory.head(N_INVENTORY).copy()

    # Recreate sequential inventory IDs after deduplication.
    inventory["inventory_id"] = [
        f"INV-{i:08d}"
        for i in range(1, len(inventory) + 1)
    ]

    opening_quantity = rng.integers(
        0,
        5000,
        len(inventory)
    )

    receipts = rng.integers(
        0,
        2000,
        len(inventory)
    )

    issues = rng.integers(
        0,
        1500,
        len(inventory)
    )

    closing_quantity = (
        opening_quantity
        + receipts
        - issues
    )

    # Prevent negative closing inventory in the clean baseline.
    issues = np.minimum(
        issues,
        opening_quantity + receipts
    )

    closing_quantity = (
        opening_quantity
        + receipts
        - issues
    )

    inventory["opening_quantity"] = opening_quantity
    inventory["receipts_quantity"] = receipts
    inventory["issues_quantity"] = issues
    inventory["closing_quantity"] = closing_quantity

    inventory.to_csv(
        RAW_DIR / "inventory.csv",
        index=False
    )

    print(
        f"Created inventory.csv: "
        f"{len(inventory):,} records"
    )


# ============================================================
# MAIN
# ============================================================

def main():

    print("=" * 60)
    print("Project Atlas — Business Data Generation")
    print("=" * 60)
    print()

    RAW_DIR.mkdir(
        parents=True,
        exist_ok=True
    )

    references = load_reference_data()

    generate_sales(references)

    generate_production(references)

    generate_maintenance(references)

    generate_financial_transactions(references)

    generate_budget(references)

    generate_energy(references)

    generate_emissions(references)

    generate_waste(references)

    generate_inventory(references)

    print()
    print("=" * 60)
    print("Business data generation complete.")
    print(f"Output directory: {RAW_DIR}")
    print("=" * 60)


if __name__ == "__main__":
    main()
