"""
Project Atlas
Phase 4 — Source Data Quality Validation

Measures known quality problems in the intentionally imperfect
Phase 3 source datasets.

This script does not modify source data.
"""

from pathlib import Path
import pandas as pd


# ============================================================
# PATHS
# ============================================================

SCRIPT_DIR = Path(__file__).resolve().parent
PHASE_DIR = SCRIPT_DIR.parent

SOURCE_DIR = (
    PHASE_DIR.parent
    / "03_Data_Generation"
    / "data"
    / "quality_issues"
)

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
# HELPERS
# ============================================================

def load(name):
    return pd.read_csv(
        SOURCE_DIR / f"{name}.csv"
    )


def check_references(df, column, valid_values):
    if column not in df.columns:
        return 0

    return int(
        (~df[column].isin(valid_values))
        .sum()
    )


def add_result(results, dataset, issue, count):
    results.append({
        "dataset": dataset,
        "issue_type": issue,
        "issue_count": int(count),
    })


# ============================================================
# MAIN
# ============================================================

def main():

    print("=" * 70)
    print("Project Atlas — Phase 4 Source Data Quality Validation")
    print("=" * 70)

    datasets = {
        name: load(name)
        for name in DATASETS
    }

    results = []

    print("\nRunning completeness and uniqueness checks...")

    for name, df in datasets.items():

        missing = int(df.isna().sum().sum())

        duplicate_rows = int(
            df.duplicated().sum()
        )

        pk = PRIMARY_KEYS[name]

        duplicate_keys = int(
            df[pk].duplicated().sum()
        )

        add_result(
            results,
            name,
            "Missing values",
            missing,
        )

        add_result(
            results,
            name,
            "Duplicate rows",
            duplicate_rows,
        )

        add_result(
            results,
            name,
            "Duplicate primary keys",
            duplicate_keys,
        )

        print(
            f"      ✓ {name + '.csv':<32}"
            f"missing={missing:,} "
            f"duplicates={duplicate_rows:,}"
        )

    # --------------------------------------------------------
    # Referential integrity
    # --------------------------------------------------------

    print("\nRunning referential-integrity checks...")

    references = {
        name: set(
            datasets[name][PRIMARY_KEYS[name]]
            .dropna()
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

        invalid = check_references(
            datasets[dataset],
            column,
            references[parent],
        )

        add_result(
            results,
            dataset,
            f"Invalid reference: {column}",
            invalid,
        )

        print(
            f"      ✓ {dataset} → {parent}"
            f" ({invalid:,} invalid)"
        )

    # --------------------------------------------------------
    # Business rules
    # --------------------------------------------------------

    print("\nRunning business-rule checks...")

    sales = datasets["sales"]

    expected_revenue = (
        sales["quantity"]
        * sales["unit_price"]
        * (1 - sales["discount_rate"])
    )

    revenue_errors = int(
        (
            (sales["revenue"] - expected_revenue)
            .abs()
            > 0.01
        ).sum()
    )

    add_result(
        results,
        "sales",
        "Revenue calculation inconsistency",
        revenue_errors,
    )

    production = datasets["production"]

    production_errors = int(
        (
            production["quantity_produced"] < 0
        ).sum()
    )

    add_result(
        results,
        "production",
        "Negative production quantity",
        production_errors,
    )

    inventory = datasets["inventory"]

    inventory_errors = int(
        (
            inventory["quantity_on_hand"] < 0
        ).sum()
    )

    add_result(
        results,
        "inventory",
        "Negative inventory quantity",
        inventory_errors,
    )

    print(
        f"      ✓ Sales revenue consistency "
        f"({revenue_errors:,} issues)"
    )

    print(
        f"      ✓ Production quantity "
        f"({production_errors:,} issues)"
    )

    print(
        f"      ✓ Inventory quantity "
        f"({inventory_errors:,} issues)"
    )

    # --------------------------------------------------------
    # Save report
    # --------------------------------------------------------

    report = pd.DataFrame(results)

    report.to_csv(
        REPORT_DIR / "source_quality_report.csv",
        index=False,
    )

    issue_count = int(
        report["issue_count"].sum()
    )

    print("\n" + "-" * 70)
    print("QUALITY ASSESSMENT SUMMARY")
    print("-" * 70)

    print(
        f"Datasets assessed                   : {len(DATASETS)}"
    )

    print(
        f"Quality issues detected             : "
        f"{issue_count:,}"
    )

    print(
        f"Report                              : "
        f"{REPORT_DIR / 'source_quality_report.csv'}"
    )

    print("\nExpected result: source data contains controlled quality issues.")

    print("\n" + "=" * 70)
    print("SOURCE DATA QUALITY ASSESSMENT COMPLETE")
    print("=" * 70)


if __name__ == "__main__":
    main()