"""
Project Atlas
Phase 3 — Business Data Generation

Generates the nine business-process datasets:
sales, production, maintenance, financial_transactions,
budget, energy, emissions, waste, inventory.
"""

from pathlib import Path
import sys

import numpy as np
import pandas as pd


# ============================================================
# CONFIGURATION
# ============================================================

SCRIPT_DIR = Path(__file__).resolve().parent
CONFIG_DIR = SCRIPT_DIR.parent / "config"

sys.path.insert(0, str(CONFIG_DIR))

from generation_config import (
    END_DATE,
    N_BUDGET,
    N_EMISSIONS,
    N_ENERGY,
    N_FINANCIAL_TRANSACTIONS,
    N_INVENTORY,
    N_MAINTENANCE,
    N_PRODUCTION,
    N_SALES,
    N_WASTE,
    RAW_DATA_DIR,
    SEED,
    START_DATE,
)


rng = np.random.default_rng(SEED)
RAW_DATA_DIR.mkdir(parents=True, exist_ok=True)


# ============================================================
# HELPERS
# ============================================================

def random_dates(size):
    """Generate dates within the approved project period."""

    start = pd.Timestamp(START_DATE)
    end = pd.Timestamp(END_DATE)

    days = (end - start).days

    return (
        start
        + pd.to_timedelta(
            rng.integers(0, days + 1, size),
            unit="D",
        )
    ).strftime("%Y-%m-%d")


def load(name):
    """Load a reference dataset."""

    path = RAW_DATA_DIR / f"{name}.csv"

    if not path.exists():
        raise FileNotFoundError(
            f"Missing reference dataset: {path}\n"
            "Run generate_reference_data.py first."
        )

    return pd.read_csv(path)


def save(df, name):
    """Save a business dataset."""

    path = RAW_DATA_DIR / f"{name}.csv"
    df.to_csv(path, index=False)

    print(
        f"Created {name}.csv: {len(df):,} records"
    )


# ============================================================
# LOAD REFERENCE DATA
# ============================================================

def load_references():

    return {
        "accounts": load("accounts"),
        "customers": load("customers"),
        "suppliers": load("suppliers"),
        "products": load("products"),
        "locations": load("locations"),
        "employees": load("employees"),
        "machines": load("machines"),
    }
  
# ============================================================
# SALES
# ============================================================

def generate_sales(ref):

    customers = ref["customers"]
    products = ref["products"]
    locations = ref["locations"]

    customer = customers.iloc[
        rng.integers(len(customers), size=N_SALES)
    ].reset_index(drop=True)

    product = products.iloc[
        rng.integers(len(products), size=N_SALES)
    ].reset_index(drop=True)

    location = locations.iloc[
        rng.integers(len(locations), size=N_SALES)
    ].reset_index(drop=True)

    quantity = rng.integers(
        1,
        101,
        N_SALES
    )

    unit_price = product["unit_price"].to_numpy()

    gross_amount = quantity * unit_price

    discount_rate = rng.choice(
        [0.00, 0.02, 0.05, 0.10, 0.15],
        N_SALES,
        p=[0.45, 0.20, 0.20, 0.10, 0.05]
    )

    discount_amount = np.round(
        gross_amount * discount_rate,
        2
    )

    revenue = np.round(
        gross_amount - discount_amount,
        2
    )

    return pd.DataFrame({
        "transaction_id": [
            f"TXN-{i:08d}"
            for i in range(1, N_SALES + 1)
        ],

        "transaction_date": random_dates(N_SALES),

        "account_id": customer["account_id"],

        "customer_id": customer["customer_id"],

        "product_id": product["product_id"],

        "location_id": location["location_id"],

        "quantity": quantity,

        "unit_price": np.round(unit_price, 2),

        "discount_amount": discount_amount,

        "revenue": revenue,
    })


# ============================================================
# PRODUCTION
# ============================================================

def generate_production(ref):

    products = ref["products"]
    machines = ref["machines"]
    employees = ref["employees"]

    # Employees available at each location.
    employees_by_location = (
        employees
        .groupby("location_id")["employee_id"]
        .apply(np.array)
        .to_dict()
    )

    product = products.iloc[
        rng.integers(len(products), size=N_PRODUCTION)
    ].reset_index(drop=True)

    # 1. Select Machine.
    machine = machines.iloc[
        rng.integers(len(machines), size=N_PRODUCTION)
    ].reset_index(drop=True)

    machine_id = machine["machine_id"].to_numpy()

    # 2. Get Machine Location.
    location_id = machine["location_id"].to_numpy()

    # 3. Select Employee from the same Location.
    employee_id = [
        rng.choice(employees_by_location[location])
        for location in location_id
    ]

    planned_quantity = rng.integers(
        50,
        1001,
        N_PRODUCTION
    )

    produced_quantity = np.floor(
        planned_quantity
        * rng.uniform(0.85, 1.05, N_PRODUCTION)
    ).astype(int)

    defect_quantity = np.floor(
        produced_quantity
        * rng.uniform(0.00, 0.05, N_PRODUCTION)
    ).astype(int)

    return pd.DataFrame({
        "production_id": [
            f"PROD-{i:08d}"
            for i in range(1, N_PRODUCTION + 1)
        ],

        "production_date":
            random_dates(N_PRODUCTION),

        "product_id":
            product["product_id"],

        "location_id":
            location_id,

        "machine_id":
            machine_id,

        "employee_id":
            employee_id,

        "planned_quantity":
            planned_quantity,

        "produced_quantity":
            produced_quantity,

        "defect_quantity":
            defect_quantity,

        "production_hours":
            np.round(
                rng.uniform(1, 24, N_PRODUCTION),
                2
            ),
    })


# ============================================================
# MAINTENANCE
# ============================================================

def generate_maintenance(ref):

    machines = ref["machines"]
    employees = ref["employees"]

    employees_by_location = (
        employees
        .groupby("location_id")["employee_id"]
        .apply(np.array)
        .to_dict()
    )

    machine = machines.iloc[
        rng.integers(len(machines), size=N_MAINTENANCE)
    ].reset_index(drop=True)

    location_id = machine["location_id"].to_numpy()

    employee_id = [
        rng.choice(employees_by_location[location])
        for location in location_id
    ]

    return pd.DataFrame({
        "maintenance_id": [
            f"MAINT-{i:08d}"
            for i in range(1, N_MAINTENANCE + 1)
        ],

        "maintenance_date":
            random_dates(N_MAINTENANCE),

        "location_id":
            location_id,

        "machine_id":
            machine["machine_id"],

        "employee_id":
            employee_id,

        "maintenance_type":
            rng.choice(
                [
                    "Preventive",
                    "Corrective",
                    "Inspection",
                ],
                N_MAINTENANCE
            ),

        "maintenance_hours":
            np.round(
                rng.uniform(1, 12, N_MAINTENANCE),
                2
            ),

        "downtime_hours":
            np.round(
                rng.uniform(0, 24, N_MAINTENANCE),
                2
            ),

        "maintenance_cost":
            np.round(
                rng.uniform(100, 5000, N_MAINTENANCE),
                2
            ),
    })


# ============================================================
# FINANCIAL TRANSACTIONS
# ============================================================

def generate_financial_transactions(ref):

    locations = ref["locations"]

    return pd.DataFrame({
        "financial_transaction_id": [
            f"FIN-{i:08d}"
            for i in range(1, N_FINANCIAL + 1)
        ],

        "transaction_date":
            random_dates(N_FINANCIAL),

        "location_id":
            rng.choice(
                locations["location_id"],
                N_FINANCIAL
            ),

        "category":
            rng.choice(
                [
                    "Revenue",
                    "Payroll",
                    "Operations",
                    "Maintenance",
                    "Utilities",
                    "Procurement",
                    "Transportation",
                ],
                N_FINANCIAL
            ),

        "transaction_type":
            rng.choice(
                ["Income", "Expense"],
                N_FINANCIAL,
                p=[0.30, 0.70]
            ),

        "amount":
            np.round(
                rng.uniform(
                    100,
                    100000,
                    N_FINANCIAL
                ),
                2
            ),
    })


# ============================================================
# BUDGET
# ============================================================

def generate_budget(ref):

    locations = ref["locations"]

    return pd.DataFrame({
        "budget_id": [
            f"BUD-{i:08d}"
            for i in range(1, N_BUDGET + 1)
        ],

        "budget_date":
            random_dates(N_BUDGET),

        "location_id":
            rng.choice(
                locations["location_id"],
                N_BUDGET
            ),

        "budget_category":
            rng.choice(
                [
                    "Operations",
                    "Maintenance",
                    "Payroll",
                    "Utilities",
                    "Procurement",
                    "Transportation",
                    "Sustainability",
                ],
                N_BUDGET
            ),

        "budget_amount":
            np.round(
                rng.uniform(
                    10000,
                    500000,
                    N_BUDGET
                ),
                2
            ),
    })


# ============================================================
# ENERGY
# ============================================================

def generate_energy(ref):

    locations = ref["locations"]

    energy_types = np.array([
        "Electricity",
        "Natural Gas",
        "Diesel",
        "Steam",
    ])

    units = {
        "Electricity": "kWh",
        "Natural Gas": "therm",
        "Diesel": "liter",
        "Steam": "kg",
    }

    energy_type = rng.choice(
        energy_types,
        N_ENERGY
    )

    return pd.DataFrame({
        "energy_id": [
            f"ENG-{i:08d}"
            for i in range(1, N_ENERGY + 1)
        ],

        "measurement_date":
            random_dates(N_ENERGY),

        "location_id":
            rng.choice(
                locations["location_id"],
                N_ENERGY
            ),

        "energy_type":
            energy_type,

        "consumption":
            np.round(
                rng.uniform(100, 10000, N_ENERGY),
                2
            ),

        "unit": [
            units[value]
            for value in energy_type
        ],

        "energy_cost":
            np.round(
                rng.uniform(50, 5000, N_ENERGY),
                2
            ),
    })


# ============================================================
# EMISSIONS
# ============================================================

def generate_emissions(ref):

    locations = ref["locations"]

    return pd.DataFrame({
        "emissions_id": [
            f"EMI-{i:08d}"
            for i in range(1, N_EMISSIONS + 1)
        ],

        "emissions_date":
            random_dates(N_EMISSIONS),

        "location_id":
            rng.choice(
                locations["location_id"],
                N_EMISSIONS
            ),

        "emission_source":
            rng.choice(
                [
                    "Electricity",
                    "Natural Gas",
                    "Diesel",
                    "Manufacturing Process",
                    "Transportation",
                ],
                N_EMISSIONS
            ),

        "co2e_amount":
            np.round(
                rng.uniform(10, 5000, N_EMISSIONS),
                2
            ),

        "unit":
            "kg CO2e",
    })


# ============================================================
# WASTE
# ============================================================

def generate_waste(ref):

    locations = ref["locations"]

    return pd.DataFrame({
        "waste_id": [
            f"WST-{i:08d}"
            for i in range(1, N_WASTE + 1)
        ],

        "waste_date":
            random_dates(N_WASTE),

        "location_id":
            rng.choice(
                locations["location_id"],
                N_WASTE
            ),

        "waste_type":
            rng.choice(
                [
                    "Metal",
                    "Plastic",
                    "Chemical",
                    "General",
                    "Recyclable",
                ],
                N_WASTE
            ),

        "waste_quantity":
            np.round(
                rng.uniform(1, 1000, N_WASTE),
                2
            ),

        "unit":
            "kg",

        "disposal_method":
            rng.choice(
                [
                    "Recycled",
                    "Landfill",
                    "Treatment",
                    "Incineration",
                ],
                N_WASTE
            ),
    })


# ============================================================
# INVENTORY
# ============================================================

def generate_inventory(ref):

    products = ref["products"]
    locations = ref["locations"]

    # Create unique Date + Product + Location combinations.
    records = set()

    while len(records) < N_INVENTORY:

        batch_size = max(
            10000,
            int((N_INVENTORY - len(records)) * 1.25)
        )

        dates = random_dates(batch_size)

        product_ids = rng.choice(
            products["product_id"],
            batch_size
        )

        location_ids = rng.choice(
            locations["location_id"],
            batch_size
        )

        records.update(
            zip(
                dates,
                product_ids,
                location_ids
            )
        )

    records = list(records)[:N_INVENTORY]

    inventory = pd.DataFrame(
        records,
        columns=[
            "inventory_date",
            "product_id",
            "location_id",
        ]
    )

    opening = rng.integers(
        0,
        5000,
        N_INVENTORY
    )

    received = rng.integers(
        0,
        2000,
        N_INVENTORY
    )

    available = opening + received

    issued = np.array([
        rng.integers(0, value + 1)
        for value in available
    ])

    inventory["inventory_id"] = [
        f"INV-{i:08d}"
        for i in range(1, N_INVENTORY + 1)
    ]

    inventory["opening_quantity"] = opening
    inventory["received_quantity"] = received
    inventory["issued_quantity"] = issued

    inventory["closing_quantity"] = (
        opening
        + received
        - issued
    )

    inventory["reorder_point"] = rng.integers(
        100,
        1500,
        N_INVENTORY
    )

    return inventory[
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


def main():

    print("=" * 60)
    print("Project Atlas — Business Data Generation")
    print("=" * 60)

    references = load_references()

    generate_sales(references)
    generate_production(references)
    generate_maintenance(references)
    generate_financial_transactions(references)
    generate_budget(references)
    generate_energy(references)
    generate_emissions(references)
    generate_waste(references)
    generate_inventory(references)

    print("\nBusiness data generation complete.")


if __name__ == "__main__":
    main()
