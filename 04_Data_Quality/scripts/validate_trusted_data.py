"""
Project Atlas
Phase 4 — Trusted Data Validation

Final quality gate for the remediated trusted datasets.
"""

from pathlib import Path
import sys
import pandas as pd


# ============================================================
# PATHS
# ============================================================

SCRIPT_DIR = Path(__file__).resolve().parent
PHASE_DIR = SCRIPT_DIR.parent

TRUSTED_DIR = PHASE_DIR / "data" / "trusted"
REPORT_DIR = PHASE_DIR / "reports"

REPORT_DIR.mkdir(parents=True, exist_ok=True)


DATASETS = [
    "accounts",
    "customers",
    "suppliers",
    "products",
    "locations",
    "employees",
    "machines",
    "sales",
    "production",
    "maintenance",
    "financial_transactions",
    "budget",
    "energy",
    "emissions",
    "waste",
    "inventory",
]


PRIMARY_KEYS = {
    "accounts": "account_id",
    "customers": "customer_id",
    "suppliers": "supplier_id",
    "products": "product_id",
    "locations": "location_id",
    "employees": "employee_id",
    "machines": "machine_id",
    "sales": "sales_id",
    "production": "production_id",
    "maintenance": "maintenance_id",
    "financial_transactions": "financial_transaction_id",
    "budget": "budget_id",
    "energy": "energy_id",
    "emissions": "emissions_id",
    "waste": "waste_id",
    "inventory": "inventory_id",
}


# ============================================================
# MAIN
# ============================================================

def main():

    print("=" * 70)
    print("Project Atlas — Trusted Data Validation")
    print("=" * 70)

    datasets = {}

    print("\nLoading trusted datasets...")

    for name in DATASETS:

        path = TRUSTED_DIR / f"{name}.csv"

        if not path.exists():
            raise FileNotFoundError(
                f"Missing trusted dataset: {path}"
            )

        datasets[name] = pd.read_csv(path)

        print(
            f"      ✓ {name + '.csv':<32}"
            f"{len(datasets[name]):>12,} records"
        )

    failures = []

    # --------------------------------------------------------
    # Completeness and uniqueness
    # --------------------------------------------------------

    print("\nRunning completeness and uniqueness checks...")

    for name, df in datasets.items():

        if df.isna().sum().sum() > 0:
            failures.append(
                f"{name}: missing values remain"
            )

        key = PRIMARY_KEYS[name]

        if df[key].isna().any():
            failures.append(
                f"{name}: null primary key"
            )

        if df[key].duplicated().any():
            failures.append(
                f"{name}: duplicate primary key"
            )

        if df.duplicated().any():
            failures.append(
                f"{name}: duplicate rows"
            )

    # --------------------------------------------------------
    # Referential integrity
    # --------------------------------------------------------

    print("\nRunning referential-integrity checks...")

    references = {
        name: set(
            datasets[name][PRIMARY_KEYS[name]]
        )
        for name in [
            "accounts",
            "customers",
            "suppliers",
            "products",
            "locations",
            "employees",
            "machines",
        ]
    }

    relationships = [
        ("customers", "account_id", "accounts"),
        ("products", "supplier_id", "suppliers"),
        ("employees", "location_id", "locations"),
        ("machines", "location_id", "locations"),
        ("sales", "account_id", "accounts"),
        ("sales", "customer_id", "customers"),
        ("sales", "product_id", "products"),
        ("sales", "location_id", "locations"),
        ("production", "product_id", "products"),
        ("production", "location_id", "locations"),
        ("production", "machine_id", "machines"),
        ("production", "employee_id", "employees"),
        ("maintenance", "location_id", "locations"),
        ("maintenance", "machine_id", "machines"),
        ("maintenance", "employee_id", "employees"),
        ("financial_transactions", "location_id", "locations"),
        ("budget", "location_id", "locations"),
        ("energy", "location_id", "locations"),
        ("emissions", "location_id", "locations"),
        ("waste", "location_id", "locations"),
        ("inventory", "product_id", "products"),
        ("inventory", "location_id", "locations"),
    ]

    for dataset, column, parent in relationships:

        invalid = (
            ~datasets[dataset][column]
            .isin(references[parent])
        )

        count = int(invalid.sum())

        if count:
            failures.append(
                f"{dataset}: {column} has "
                f"{count:,} invalid references"
            )

    # --------------------------------------------------------
    # Sales consistency
    # --------------------------------------------------------

    print("\nRunning business-rule checks...")

    sales = datasets["sales"]

    expected_revenue = (
        sales["quantity"]
        * sales["unit_price"]
        * (1 - sales["discount_rate"])
    ).round(2)

    revenue_errors = (
        (sales["revenue"] - expected_revenue)
        .abs()
        > 0.01
    )

    if revenue_errors.any():
        failures.append(
            "sales: revenue calculation inconsistency"
        )

    # --------------------------------------------------------
    # Sales account/customer consistency
    # --------------------------------------------------------

    customer_accounts = (
        datasets["customers"]
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

        failures.append(
            "sales: account/customer inconsistency"
        )

    # --------------------------------------------------------
    # Operational location consistency
    # --------------------------------------------------------

    machine_locations = (
        datasets["machines"]
        .set_index("machine_id")["location_id"]
    )

    employee_locations = (
        datasets["employees"]
        .set_index("employee_id")["location_id"]
    )

    production = datasets["production"]

    if not (
        production["location_id"]
        == production["machine_id"].map(
            machine_locations
        )
    ).all():

        failures.append(
            "production: machine/location inconsistency"
        )

    if not (
        production["location_id"]
        == production["employee_id"].map(
            employee_locations
        )
    ).all():

        failures.append(
            "production: employee/location inconsistency"
        )

    maintenance = datasets["maintenance"]

    if not (
        maintenance["location_id"]
        == maintenance["machine_id"].map(
            machine_locations
        )
    ).all():

        failures.append(
            "maintenance: machine/location inconsistency"
        )

    if not (
        maintenance["location_id"]
        == maintenance["employee_id"].map(
            employee_locations
        )
    ).all():

        failures.append(
            "maintenance: employee/location inconsistency"
        )

    # --------------------------------------------------------
    # Inventory grain
    # --------------------------------------------------------

    inventory = datasets["inventory"]

    duplicate_grain = inventory.duplicated(
        subset=[
            "date",
            "product_id",
            "location_id",
        ]
    )

    if duplicate_grain.any():

        failures.append(
            "inventory: Date + Product + Location "
            "grain is not unique"
        )

    # --------------------------------------------------------
    # Result
    # --------------------------------------------------------

    print("\n" + "-" * 70)
    print("TRUSTED DATA QUALITY GATE")
    print("-" * 70)

    print(
        f"Datasets validated                  : "
        f"{len(DATASETS)}"
    )

    print(
        f"Records validated                   : "
        f"{sum(len(df) for df in datasets.values()):,}"
    )

    if failures:

        print(
            f"Validation status                   : FAILED"
        )

        print("\nRemaining issues:")

        for failure in failures:
            print(f"      ✗ {failure}")

        print("\n" + "=" * 70)
        print("TRUSTED DATA VALIDATION FAILED")
        print("=" * 70)

        sys.exit(1)

    print(
        "Validation status                   : PASSED"
    )

    print(
        f"Trusted output                      : "
        f"{TRUSTED_DIR}"
    )

    print("\nAll critical quality rules passed.")

    print("\n" + "=" * 70)
    print("TRUSTED DATA VALIDATION COMPLETE")
    print("=" * 70)


if __name__ == "__main__":
    main()