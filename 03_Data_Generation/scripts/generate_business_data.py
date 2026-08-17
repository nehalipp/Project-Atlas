"""
Project Atlas
Phase 3 — Business Data Generation

Generates the nine approved business datasets:

    sales
    production
    maintenance
    financial_transactions
    budget
    energy
    emissions
    waste
    inventory

All data is synthetic and reproducible.

The generator respects the approved Phase 2 data model,
fact grains, reference relationships and lifecycle dates.
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


# ============================================================
# SETUP
# ============================================================

rng = np.random.default_rng(SEED)

START = pd.Timestamp(START_DATE)
END = pd.Timestamp(END_DATE)

RAW_DATA_DIR.mkdir(
    parents=True,
    exist_ok=True,
)


# ============================================================
# HELPERS
# ============================================================

def load(name):
    return pd.read_csv(
        RAW_DATA_DIR / f"{name}.csv"
    )


def save(df, filename):
    df.to_csv(
        RAW_DATA_DIR / filename,
        index=False,
    )

    print(
        f"      ✓ {filename:<32}"
        f"{len(df):>10,} records"
    )


def random_dates(size):

    days = (END - START).days

    offsets = rng.integers(
        0,
        days + 1,
        size,
    )

    return (
        START
        + pd.to_timedelta(
            offsets,
            unit="D",
        )
    ).strftime("%Y-%m-%d")


def dates_after(start_dates):

    start_dates = pd.to_datetime(
        start_dates
    )

    max_days = (
        END - start_dates
    ).days

    offsets = np.array([
        rng.integers(
            0,
            days + 1,
        )
        for days in max_days
    ])

    return (
        start_dates
        + pd.to_timedelta(
            offsets,
            unit="D",
        )
    ).strftime("%Y-%m-%d")


# ============================================================
# SALES
# ============================================================

def generate_sales(
    accounts,
    customers,
    products,
    locations,
):

    customer_ids = rng.choice(
        customers["customer_id"].to_numpy(),
        N_SALES,
    )

    customer_account = (
        customers
        .set_index("customer_id")["account_id"]
    )

    product_ids = rng.choice(
        products["product_id"].to_numpy(),
        N_SALES,
    )

    product_prices = (
        products
        .set_index("product_id")["unit_price"]
    )

    account_ids = (
        pd.Series(customer_ids)
        .map(customer_account)
        .to_numpy()
    )

    unit_prices = (
        pd.Series(product_ids)
        .map(product_prices)
        .to_numpy()
    )

    quantity = rng.integers(
        1,
        101,
        N_SALES,
    )

    discount_rate = np.round(
        rng.uniform(
            0,
            0.15,
            N_SALES,
        ),
        4,
    )

    revenue = np.round(
        quantity
        * unit_prices
        * (1 - discount_rate),
        2,
    )

    return pd.DataFrame({
        "sales_id": [
            f"SALE-{i:07d}"
            for i in range(1, N_SALES + 1)
        ],
        "date": random_dates(N_SALES),
        "account_id": account_ids,
        "customer_id": customer_ids,
        "product_id": product_ids,
        "location_id": rng.choice(
            locations["location_id"].to_numpy(),
            N_SALES,
        ),
        "quantity": quantity,
        "unit_price": unit_prices,
        "discount_rate": discount_rate,
        "revenue": revenue,
    })


# ============================================================
# PRODUCTION
# ============================================================

def generate_production(
    products,
    locations,
    machines,
    employees,
):

    machine_lookup = machines.set_index(
        "machine_id"
    )

    employee_lookup = employees.set_index(
        "employee_id"
    )

    machine_ids = rng.choice(
        machines["machine_id"].to_numpy(),
        N_PRODUCTION,
    )

    machine_locations = (
        machine_lookup
        .loc[machine_ids, "location_id"]
        .to_numpy()
    )

    employees_by_location = {
        location_id: group["employee_id"].to_numpy()
        for location_id, group
        in employees.groupby("location_id")
    }

    employee_ids = np.array([
        rng.choice(
            employees_by_location[location_id]
        )
        for location_id in machine_locations
    ])

    employee_hire_dates = (
        employee_lookup
        .loc[employee_ids, "hire_date"]
        .to_numpy()
    )

    machine_install_dates = (
        machine_lookup
        .loc[machine_ids, "installation_date"]
        .to_numpy()
    )

    earliest_dates = pd.to_datetime(
        np.maximum(
            pd.to_datetime(
                employee_hire_dates
            ).values.astype("datetime64[D]"),
            pd.to_datetime(
                machine_install_dates
            ).values.astype("datetime64[D]"),
        )
    )

    planned_quantity = rng.integers(
        50,
        501,
        N_PRODUCTION,
    )

    quantity_produced = np.maximum(
        1,
        np.round(
            planned_quantity
            * rng.uniform(
                0.85,
                1.10,
                N_PRODUCTION,
            )
        ).astype(int),
    )

    return pd.DataFrame({
        "production_id": [
            f"PROD-ACT-{i:07d}"
            for i in range(1, N_PRODUCTION + 1)
        ],
        "date": dates_after(earliest_dates),
        "product_id": rng.choice(
            products["product_id"].to_numpy(),
            N_PRODUCTION,
        ),
        "location_id": machine_locations,
        "machine_id": machine_ids,
        "employee_id": employee_ids,
        "planned_quantity": planned_quantity,
        "quantity_produced": quantity_produced,
        "production_hours": np.round(
            rng.uniform(
                1,
                16,
                N_PRODUCTION,
            ),
            2,
        ),
        "production_status": rng.choice(
            [
                "Completed",
                "Partial",
                "Cancelled",
            ],
            N_PRODUCTION,
            p=[0.90, 0.08, 0.02],
        ),
    })


# ============================================================
# MAINTENANCE
# ============================================================

def generate_maintenance(
    machines,
    employees,
):

    machine_lookup = machines.set_index(
        "machine_id"
    )

    employee_lookup = employees.set_index(
        "employee_id"
    )

    machine_ids = rng.choice(
        machines["machine_id"].to_numpy(),
        N_MAINTENANCE,
    )

    machine_locations = (
        machine_lookup
        .loc[machine_ids, "location_id"]
        .to_numpy()
    )

    employees_by_location = {
        location_id: group["employee_id"].to_numpy()
        for location_id, group
        in employees.groupby("location_id")
    }

    employee_ids = np.array([
        rng.choice(
            employees_by_location[location_id]
        )
        for location_id in machine_locations
    ])

    machine_install_dates = (
        machine_lookup
        .loc[machine_ids, "installation_date"]
        .to_numpy()
    )

    employee_hire_dates = (
        employee_lookup
        .loc[employee_ids, "hire_date"]
        .to_numpy()
    )

    earliest_dates = pd.to_datetime(
        np.maximum(
            pd.to_datetime(
                machine_install_dates
            ).values.astype("datetime64[D]"),
            pd.to_datetime(
                employee_hire_dates
            ).values.astype("datetime64[D]"),
        )
    )

    return pd.DataFrame({
        "maintenance_id": [
            f"MAINT-{i:07d}"
            for i in range(1, N_MAINTENANCE + 1)
        ],
        "date": dates_after(earliest_dates),
        "location_id": machine_locations,
        "machine_id": machine_ids,
        "employee_id": employee_ids,
        "maintenance_type": rng.choice(
            [
                "Preventive",
                "Corrective",
                "Inspection",
                "Emergency",
            ],
            N_MAINTENANCE,
            p=[0.45, 0.30, 0.20, 0.05],
        ),
        "downtime_hours": np.round(
            rng.uniform(
                0.5,
                24,
                N_MAINTENANCE,
            ),
            2,
        ),
        "maintenance_cost": np.round(
            rng.lognormal(
                mean=6,
                sigma=0.7,
                size=N_MAINTENANCE,
            ),
            2,
        ),
    })


# ============================================================
# FINANCIAL TRANSACTIONS
# ============================================================

def generate_financial_transactions(locations):

    return pd.DataFrame({
        "financial_transaction_id": [
            f"FIN-{i:07d}"
            for i in range(
                1,
                N_FINANCIAL_TRANSACTIONS + 1,
            )
        ],
        "date": random_dates(
            N_FINANCIAL_TRANSACTIONS
        ),
        "location_id": rng.choice(
            locations["location_id"].to_numpy(),
            N_FINANCIAL_TRANSACTIONS,
        ),
        "transaction_type": rng.choice(
            [
                "Revenue",
                "Expense",
                "Transfer",
                "Adjustment",
            ],
            N_FINANCIAL_TRANSACTIONS,
            p=[0.30, 0.45, 0.15, 0.10],
        ),
        "amount": np.round(
            rng.lognormal(
                mean=7,
                sigma=1,
                size=N_FINANCIAL_TRANSACTIONS,
            ),
            2,
        ),
        "description": rng.choice(
            [
                "Operating transaction",
                "Customer transaction",
                "Supplier transaction",
                "Internal transaction",
                "Period adjustment",
            ],
            N_FINANCIAL_TRANSACTIONS,
        ),
    })


# ============================================================
# BUDGET
# ============================================================

def generate_budget(locations):

    return pd.DataFrame({
        "budget_id": [
            f"BUD-{i:07d}"
            for i in range(1, N_BUDGET + 1)
        ],
        "date": random_dates(N_BUDGET),
        "location_id": rng.choice(
            locations["location_id"].to_numpy(),
            N_BUDGET,
        ),
        "category": rng.choice(
            [
                "Operations",
                "Production",
                "Maintenance",
                "Energy",
                "Supply Chain",
                "Administration",
            ],
            N_BUDGET,
        ),
        "budget_amount": np.round(
            rng.lognormal(
                mean=10,
                sigma=0.8,
                size=N_BUDGET,
            ),
            2,
        ),
    })


# ============================================================
# ENERGY
# ============================================================

def generate_energy(locations):

    return pd.DataFrame({
        "energy_id": [
            f"ENG-{i:07d}"
            for i in range(1, N_ENERGY + 1)
        ],
        "date": random_dates(N_ENERGY),
        "location_id": rng.choice(
            locations["location_id"].to_numpy(),
            N_ENERGY,
        ),
        "energy_type": rng.choice(
            [
                "Electricity",
                "Natural Gas",
                "Diesel",
                "Steam",
            ],
            N_ENERGY,
            p=[0.60, 0.20, 0.10, 0.10],
        ),
        "consumption": np.round(
            rng.lognormal(
                mean=5,
                sigma=1,
                size=N_ENERGY,
            ),
            2,
        ),
        "unit": "kWh",
    })


# ============================================================
# EMISSIONS
# ============================================================

def generate_emissions(locations):

    return pd.DataFrame({
        "emissions_id": [
            f"EMI-{i:07d}"
            for i in range(1, N_EMISSIONS + 1)
        ],
        "date": random_dates(N_EMISSIONS),
        "location_id": rng.choice(
            locations["location_id"].to_numpy(),
            N_EMISSIONS,
        ),
        "source": rng.choice(
            [
                "Electricity",
                "Natural Gas",
                "Fuel",
                "Process",
            ],
            N_EMISSIONS,
        ),
        "co2_kg": np.round(
            rng.lognormal(
                mean=5,
                sigma=1,
                size=N_EMISSIONS,
            ),
            2,
        ),
    })


# ============================================================
# WASTE
# ============================================================

def generate_waste(locations):

    return pd.DataFrame({
        "waste_id": [
            f"WST-{i:07d}"
            for i in range(1, N_WASTE + 1)
        ],
        "date": random_dates(N_WASTE),
        "location_id": rng.choice(
            locations["location_id"].to_numpy(),
            N_WASTE,
        ),
        "waste_type": rng.choice(
            [
                "Metal",
                "Plastic",
                "Paper",
                "Chemical",
                "General",
            ],
            N_WASTE,
        ),
        "quantity": np.round(
            rng.lognormal(
                mean=3,
                sigma=1,
                size=N_WASTE,
            ),
            2,
        ),
        "unit": "kg",
        "disposal_method": rng.choice(
            [
                "Recycling",
                "Landfill",
                "Treatment",
                "Reuse",
            ],
            N_WASTE,
        ),
    })


# ============================================================
# INVENTORY
# ============================================================

def generate_inventory(
    products,
    locations,
):

    dates = pd.date_range(
        START,
        END,
        freq="D",
    )

    total_combinations = (
        len(dates)
        * len(products)
        * len(locations)
    )

    if N_INVENTORY > total_combinations:
        raise ValueError(
            "N_INVENTORY exceeds available "
            "Date + Product + Location combinations."
        )

    combinations = rng.choice(
        total_combinations,
        N_INVENTORY,
        replace=False,
    )

    n_products = len(products)
    n_locations = len(locations)

    date_index = (
        combinations
        // (n_products * n_locations)
    )

    remainder = (
        combinations
        % (n_products * n_locations)
    )

    product_index = (
        remainder
        // n_locations
    )

    location_index = (
        remainder
        % n_locations
    )

    product_ids = (
        products["product_id"]
        .to_numpy()[product_index]
    )

    location_ids = (
        locations["location_id"]
        .to_numpy()[location_index]
    )

    snapshot_dates = (
        dates.to_numpy()[date_index]
    )

    quantity = rng.integers(
        0,
        1001,
        N_INVENTORY,
    )

    reorder_point = rng.integers(
        20,
        201,
        N_INVENTORY,
    )

    unit_costs = (
        products
        .set_index("product_id")["unit_cost"]
    )

    inventory_value = np.round(
        quantity
        * pd.Series(product_ids)
        .map(unit_costs)
        .to_numpy(),
        2,
    )

    return pd.DataFrame({
        "inventory_id": [
            f"INV-{i:07d}"
            for i in range(1, N_INVENTORY + 1)
        ],
        "date": pd.to_datetime(
            snapshot_dates
        ).strftime("%Y-%m-%d"),
        "product_id": product_ids,
        "location_id": location_ids,
        "quantity_on_hand": quantity,
        "reorder_point": reorder_point,
        "inventory_value": inventory_value,
    })


# ============================================================
# BASELINE VALIDATION
# ============================================================

def validate_baseline(
    sales,
    production,
    maintenance,
    inventory,
):

    customers = load("customers")

    customer_accounts = (
        customers
        .set_index("customer_id")["account_id"]
    )

    expected_accounts = (
        sales["customer_id"]
        .map(customer_accounts)
    )

    if not (
        sales["account_id"]
        == expected_accounts
    ).all():
        raise ValueError(
            "Sales account/customer relationship failed."
        )

    machines = load("machines")
    employees = load("employees")

    machine_locations = (
        machines
        .set_index("machine_id")["location_id"]
    )

    employee_locations = (
        employees
        .set_index("employee_id")["location_id"]
    )

    if not (
        production["location_id"]
        == production["machine_id"].map(
            machine_locations
        )
    ).all():
        raise ValueError(
            "Production machine/location relationship failed."
        )

    if not (
        production["location_id"]
        == production["employee_id"].map(
            employee_locations
        )
    ).all():
        raise ValueError(
            "Production employee/location relationship failed."
        )

    if not (
        maintenance["location_id"]
        == maintenance["machine_id"].map(
            machine_locations
        )
    ).all():
        raise ValueError(
            "Maintenance machine/location relationship failed."
        )

    if not (
        maintenance["location_id"]
        == maintenance["employee_id"].map(
            employee_locations
        )
    ).all():
        raise ValueError(
            "Maintenance employee/location relationship failed."
        )

    if inventory.duplicated(
        subset=[
            "date",
            "product_id",
            "location_id",
        ]
    ).any():
        raise ValueError(
            "Inventory Date + Product + Location grain failed."
        )

    print("\nRunning baseline validation...")
    print("      ✓ Sales account/customer relationship")
    print("      ✓ Production machine/location relationship")
    print("      ✓ Production employee/location relationship")
    print("      ✓ Maintenance machine/location relationship")
    print("      ✓ Maintenance employee/location relationship")
    print("      ✓ Inventory Date + Product + Location grain")
    print("\n      CLEAN BASELINE VALIDATION PASSED")


# ============================================================
# MAIN
# ============================================================

def main():

    print("=" * 70)
    print("Project Atlas — Business Data Generation")
    print("=" * 70)

    print("\nGenerating business datasets...")

    accounts = load("accounts")
    customers = load("customers")
    products = load("products")
    locations = load("locations")
    employees = load("employees")
    machines = load("machines")

    sales = generate_sales(
        accounts,
        customers,
        products,
        locations,
    )
    save(sales, "sales.csv")

    production = generate_production(
        products,
        locations,
        machines,
        employees,
    )
    save(production, "production.csv")

    maintenance = generate_maintenance(
        machines,
        employees,
    )
    save(maintenance, "maintenance.csv")

    financial = generate_financial_transactions(
        locations
    )
    save(financial, "financial_transactions.csv")

    budget = generate_budget(locations)
    save(budget, "budget.csv")

    energy = generate_energy(locations)
    save(energy, "energy.csv")

    emissions = generate_emissions(locations)
    save(emissions, "emissions.csv")

    waste = generate_waste(locations)
    save(waste, "waste.csv")

    inventory = generate_inventory(
        products,
        locations,
    )
    save(inventory, "inventory.csv")

    validate_baseline(
        sales,
        production,
        maintenance,
        inventory,
    )

    total_records = sum([
        len(sales),
        len(production),
        len(maintenance),
        len(financial),
        len(budget),
        len(energy),
        len(emissions),
        len(waste),
        len(inventory),
    ])

    print("\n" + "-" * 70)
    print("GENERATION SUMMARY")
    print("-" * 70)
    print(f"Datasets generated                  : 9")
    print(f"Total records                       : {total_records:,.0f}")
    print(f"Output                              : {RAW_DATA_DIR}")

    print("\n" + "=" * 70)
    print("BUSINESS DATA GENERATION COMPLETE")
    print("=" * 70)

    print(
        "\nClean baseline is validated and ready "
        "for controlled quality injection."
    )


if __name__ == "__main__":
    main()