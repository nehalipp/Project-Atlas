"""
Project Atlas
Phase 3 - Synthetic Data Generation

Generates 17 synthetic datasets for Project Atlas.

The raw datasets intentionally contain a small number of
realistic data-quality issues.

Phase 4 will detect and remediate those issues.

Random seed: 42
Date range: 2019-01-01 to 2025-12-31
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

ATTRIBUTE_START_DATE = "2016-01-01"
ATTRIBUTE_END_DATE = "2018-12-31"

SCRIPT_DIR = Path(__file__).resolve().parent
OUTPUT_DIR = SCRIPT_DIR / "data" / "raw"

OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

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

# ------------------------------------------------------------
# Business realism controls
# ------------------------------------------------------------
# These controls change distributions without changing the Atlas
# schema, keys, row counts, or downstream table structure.
LOCATION_PROFILES = {
    "Plant": {"activity": 1.35, "energy": 1.35, "emissions": 1.30, "waste": 1.20},
    "Warehouse": {"activity": 0.85, "energy": 0.75, "emissions": 0.75, "waste": 0.75},
    "Distribution Center": {"activity": 1.00, "energy": 0.90, "emissions": 0.90, "waste": 0.85},
    "Office": {"activity": 0.45, "energy": 0.55, "emissions": 0.55, "waste": 0.45},
}

PRODUCT_CATEGORY_PROFILE = {
    "Industrial Equipment": {"demand": 1.15, "complexity": 1.20, "energy": 1.25, "waste": 1.10},
    "Components": {"demand": 1.30, "complexity": 0.95, "energy": 0.95, "waste": 0.90},
    "Electronics": {"demand": 1.05, "complexity": 1.10, "energy": 1.15, "waste": 0.80},
    "Packaging": {"demand": 1.25, "complexity": 0.80, "energy": 0.75, "waste": 1.25},
    "Raw Materials": {"demand": 0.80, "complexity": 0.70, "energy": 0.90, "waste": 1.20},
}


# ============================================================
# HELPER FUNCTIONS
# ============================================================

def make_ids(prefix, number):
    """Create business IDs."""
    return [f"{prefix}-{i:06d}" for i in range(1, number + 1)]


def random_dates(number):
    """Create random operational dates."""
    dates = pd.date_range(START_DATE, END_DATE)
    return rng.choice(dates, number)


def random_attribute_dates(number):
    """Create dates before the operational period."""
    dates = pd.date_range(
        ATTRIBUTE_START_DATE,
        ATTRIBUTE_END_DATE
    )
    return rng.choice(dates, number)


def random_rows(dataframe, number):
    """Return random row indexes."""
    return rng.choice(
        dataframe.index,
        size=number,
        replace=False
    )


def save_data(dataframe, name):
    """Save dataframe as CSV."""
    dataframe.to_csv(
        OUTPUT_DIR / f"{name}.csv",
        index=False
    )
    print(f"{name}: {len(dataframe):,} rows")


# ============================================================
# DIMENSION TABLES
# ============================================================

print("\nGenerating dimensions...")


# -------------------------
# dim_date
# -------------------------

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


# -------------------------
# dim_account
# -------------------------

dim_account = pd.DataFrame({
    "account_key": range(1, N_ACCOUNT + 1),
    "account_id": make_ids("ACC", N_ACCOUNT),
    "account_name": [fake.company() for _ in range(N_ACCOUNT)],
    "account_type": rng.choice(ACCOUNT_TYPES, N_ACCOUNT),
    "industry": rng.choice(INDUSTRIES, N_ACCOUNT),
    "country": rng.choice(COUNTRIES, N_ACCOUNT),
    "status": rng.choice(
        ["Active", "Inactive"],
        N_ACCOUNT,
        p=[0.90, 0.10]
    )
})


# -------------------------
# dim_customer
# -------------------------

dim_customer = pd.DataFrame({
    "customer_key": range(1, N_CUSTOMER + 1),
    "customer_id": make_ids("CUS", N_CUSTOMER),
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


# -------------------------
# dim_supplier
# -------------------------

dim_supplier = pd.DataFrame({
    "supplier_key": range(1, N_SUPPLIER + 1),
    "supplier_id": make_ids("SUP", N_SUPPLIER),
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


# -------------------------
# dim_product
# -------------------------

unit_cost = np.round(
    rng.uniform(10, 500, N_PRODUCT),
    2
)

unit_price = np.round(
    unit_cost * rng.uniform(1.25, 2.50, N_PRODUCT),
    2
)

dim_product = pd.DataFrame({
    "product_key": range(1, N_PRODUCT + 1),
    "product_id": make_ids("PROD", N_PRODUCT),
    "supplier_key": rng.choice(
        dim_supplier["supplier_key"],
        N_PRODUCT
    ),
    "product_name": [
        f"Atlas Product {i}"
        for i in range(1, N_PRODUCT + 1)
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
        ["Each", "Kg", "Liter", "Meter"],
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


# -------------------------
# dim_location
# -------------------------
# Synthetic, business-readable locations. We preserve the original
# distribution of location types/countries so downstream dashboard
# behavior does not change structurally.
CITY_CATALOG = [
    ("Harrisburg", "Pennsylvania", "United States"), ("York", "Pennsylvania", "United States"),
    ("Pittsburgh", "Pennsylvania", "United States"), ("Columbus", "Ohio", "United States"),
    ("Cleveland", "Ohio", "United States"), ("Detroit", "Michigan", "United States"),
    ("Charlotte", "North Carolina", "United States"), ("Atlanta", "Georgia", "United States"),
    ("Dallas", "Texas", "United States"), ("Denver", "Colorado", "United States"),
    ("Toronto", "Ontario", "Canada"), ("Montreal", "Quebec", "Canada"),
    ("Vancouver", "British Columbia", "Canada"), ("Calgary", "Alberta", "Canada"),
    ("Ottawa", "Ontario", "Canada"), ("Berlin", "Berlin", "Germany"),
    ("Hamburg", "Hamburg", "Germany"), ("Munich", "Bavaria", "Germany"),
    ("Frankfurt", "Hesse", "Germany"), ("Stuttgart", "Baden-Württemberg", "Germany"),
    ("Cologne", "North Rhine-Westphalia", "Germany"), ("Stockholm", "Stockholm", "Sweden"),
    ("Gothenburg", "Västra Götaland", "Sweden"), ("Malmo", "Skane", "Sweden"),
    ("Uppsala", "Uppsala", "Sweden"), ("Monterrey", "Nuevo Leon", "Mexico"),
    ("Mexico City", "Mexico City", "Mexico"), ("Guadalajara", "Jalisco", "Mexico"),
    ("Tijuana", "Baja California", "Mexico"), ("Queretaro", "Queretaro", "Mexico")
]

country_targets = {
    "United States": 27,
    "Canada": 15,
    "Germany": 15,
    "Sweden": 28,
    "Mexico": 15
}

type_targets = {
    "Plant": 21,
    "Warehouse": 28,
    "Distribution Center": 22,
    "Office": 29
}

location_rows = []
for country, count in country_targets.items():
    candidates = [c for c in CITY_CATALOG if c[2] == country]
    for i in range(count):
        city, region, _ = candidates[i % len(candidates)]
        location_rows.append((city, region, country))

# Assign types deterministically after the city/country list is built.
location_types = []
for ltype, count in type_targets.items():
    location_types.extend([ltype] * count)

# Shuffle only the type assignment so location types are not aligned to countries.
location_types = list(rng.permutation(location_types))

location_names = []
for i, ((city, region, country), ltype) in enumerate(zip(location_rows, location_types), start=1):
    name_by_type = {
        "Plant": "Manufacturing Plant",
        "Warehouse": "Warehouse",
        "Distribution Center": "Distribution Center",
        "Office": "Regional Office"
    }
    location_names.append(f"{city} {name_by_type[ltype]} {i:02d}")

dim_location = pd.DataFrame({
    "location_key": range(1, N_LOCATION + 1),
    "location_id": make_ids("LOC", N_LOCATION),
    "location_name": location_names,
    "location_type": location_types,
    "city": [r[0] for r in location_rows],
    "state_region": [r[1] for r in location_rows],
    "country": [r[2] for r in location_rows],
    "status": rng.choice(
        ["Active", "Inactive"],
        N_LOCATION,
        p=[0.95, 0.05]
    )
})


# -------------------------
# dim_employee
# -------------------------

dim_employee = pd.DataFrame({
    "employee_key": range(1, N_EMPLOYEE + 1),
    "employee_id": make_ids("EMP", N_EMPLOYEE),
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
    "hire_date": random_attribute_dates(N_EMPLOYEE),
    "status": rng.choice(
        ["Active", "Inactive"],
        N_EMPLOYEE,
        p=[0.92, 0.08]
    )
})


# -------------------------
# dim_machine
# -------------------------

machine_location_candidates = dim_location.loc[
    dim_location["location_type"].isin(["Plant", "Warehouse", "Distribution Center"]),
    "location_key"
].to_numpy()

dim_machine = pd.DataFrame({
    "machine_key": range(1, N_MACHINE + 1),
    "machine_id": make_ids("MCH", N_MACHINE),
    "location_key": rng.choice(
        machine_location_candidates,
        N_MACHINE
    ),
    "machine_name": [
        f"Atlas Machine {i}"
        for i in range(1, N_MACHINE + 1)
    ],
    "machine_type": rng.choice(
        MACHINE_TYPES,
        N_MACHINE
    ),
    "installation_date": random_attribute_dates(
        N_MACHINE
    ),
    "status": rng.choice(
        ["Operational", "Maintenance", "Inactive"],
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
# FACT TABLES
# ============================================================

print("\nGenerating facts...")


# -------------------------
# fact_sales
# -------------------------

sales_dates = pd.to_datetime(
    random_dates(N_SALES)
)

# Product demand weights create meaningful differences in product performance.
product_demand_weights = dim_product["category"].map(
    {k: v["demand"] for k, v in PRODUCT_CATEGORY_PROFILE.items()}
).to_numpy()
product_demand_weights = product_demand_weights / product_demand_weights.sum()

sales_product_keys = rng.choice(
    dim_product["product_key"],
    N_SALES,
    p=product_demand_weights
)

# Active customers and enterprise customers have greater transaction probability.
customer_weights = np.ones(N_CUSTOMER)
customer_weights *= np.where(dim_customer["status"].eq("Active"), 1.15, 0.35)
customer_weights *= dim_customer["customer_segment"].map({"Enterprise": 1.35, "Mid-Market": 1.00, "SMB": 0.70}).to_numpy()
customer_weights /= customer_weights.sum()

sales_customer_keys = rng.choice(
    dim_customer["customer_key"],
    N_SALES,
    p=customer_weights
)

# Locations participate at different commercial activity levels.
location_activity_weights = dim_location["location_type"].map(
    {k: v["activity"] for k, v in LOCATION_PROFILES.items()}
).to_numpy()
location_activity_weights /= location_activity_weights.sum()

sales_location_keys = rng.choice(
    dim_location["location_key"],
    N_SALES,
    p=location_activity_weights
)

product_price_map = product_prices
sales_unit_price = np.array([product_price_map[key] for key in sales_product_keys])

# Quantity varies by product category and season.
month_factor = pd.Series(sales_dates.month).map({1:0.95,2:0.97,3:1.00,4:1.02,5:1.04,6:1.00,7:0.96,8:0.98,9:1.01,10:1.05,11:1.10,12:1.18}).to_numpy()
category_factor = dim_product.set_index("product_key")["category"].map(
    {k: v["demand"] for k, v in PRODUCT_CATEGORY_PROFILE.items()}
).loc[sales_product_keys].to_numpy()
sales_quantity = np.maximum(1, np.round(rng.gamma(shape=2.5, scale=18, size=N_SALES) * month_factor * category_factor / 1.35).astype(int))
sales_quantity = np.clip(sales_quantity, 1, 150)

discount_rate = rng.beta(2, 18, N_SALES) * 0.20
discount = np.round(sales_quantity * sales_unit_price * discount_rate, 2)

revenue = np.round(
    sales_quantity * sales_unit_price - discount,
    2
)

fact_sales = pd.DataFrame({
    "sales_key": range(1, N_SALES + 1),
    "transaction_id": make_ids("SAL", N_SALES),
    "date_key": sales_dates.strftime("%Y%m%d").astype(int),
    "customer_key": sales_customer_keys,
    "product_key": sales_product_keys,
    "location_key": sales_location_keys,
    "quantity": sales_quantity,
    "unit_price": sales_unit_price,
    "discount_amount": discount,
    "revenue": revenue
})


# -------------------------
# fact_production
# -------------------------

production_machine_candidates = dim_machine.loc[
    dim_machine["location_key"].isin(
        dim_location.loc[dim_location["location_type"] == "Plant", "location_key"]
    ),
    "machine_key"
].to_numpy()

production_machine_keys = rng.choice(
    production_machine_candidates,
    N_PRODUCTION
)

production_location_keys = np.array([
    machine_locations[machine]
    for machine in production_machine_keys
])

production_dates = pd.to_datetime(random_dates(N_PRODUCTION))
production_product_keys = rng.choice(
    dim_product["product_key"],
    N_PRODUCTION,
    p=product_demand_weights
)

planned_quantity = rng.integers(50, 501, N_PRODUCTION)

location_type_map = dim_location.set_index("location_key")["location_type"]
plant_factor = location_type_map.map({"Plant": 1.00, "Warehouse": 0.98, "Distribution Center": 0.96, "Office": 0.25}).loc[production_location_keys].to_numpy()
category_complexity = dim_product.set_index("product_key")["category"].map(
    {k: v["complexity"] for k, v in PRODUCT_CATEGORY_PROFILE.items()}
).loc[production_product_keys].to_numpy()
category_adjustment = 1 + (category_complexity - 1) * 0.35

# Production performance varies modestly by facility and product complexity.
achievement_ratio = np.clip(
    rng.normal(0.93, 0.05, N_PRODUCTION) * plant_factor / category_adjustment,
    0.82,
    1.02
)
produced_quantity = np.minimum(
    np.round(planned_quantity * achievement_ratio).astype(int),
    planned_quantity
)
produced_quantity = np.maximum(produced_quantity, 1)

# Realistic baseline defect rates are low single-digit percentages;
# intentional Phase 4 violations are added later.
defect_rate = np.clip(
    rng.beta(2.5, 70, N_PRODUCTION)
    * dim_product.set_index("product_key")["category"].map(
        {k: v["waste"] for k, v in PRODUCT_CATEGORY_PROFILE.items()}
    ).loc[production_product_keys].to_numpy(),
    0.002,
    0.12
)
defect_quantity = np.floor(produced_quantity * defect_rate).astype(int)

# Production hours increase with output and product complexity.
production_hours = np.round(
    np.maximum(1, produced_quantity / rng.uniform(35, 65, N_PRODUCTION) * category_complexity),
    2
)
production_hours = np.clip(production_hours, 1, 18)

fact_production = pd.DataFrame({
    "production_key": range(1, N_PRODUCTION + 1),
    "production_id": make_ids("PRD", N_PRODUCTION),
    "date_key": production_dates.strftime("%Y%m%d").astype(int),
    "product_key": production_product_keys,
    "location_key": production_location_keys,
    "machine_key": production_machine_keys,
    "employee_key": rng.choice(dim_employee["employee_key"], N_PRODUCTION),
    "planned_quantity": planned_quantity,
    "produced_quantity": produced_quantity,
    "defect_quantity": defect_quantity,
    "production_hours": production_hours
})


# -------------------------
# fact_maintenance
# -------------------------

maintenance_machine_keys = rng.choice(
    dim_machine["machine_key"],
    N_MAINTENANCE
)

maintenance_location_keys = [
    machine_locations[machine]
    for machine in maintenance_machine_keys
]

maintenance_type_values = rng.choice(MAINTENANCE_TYPES, N_MAINTENANCE, p=[0.55, 0.30, 0.15])
maintenance_location_factor = location_type_map.map({"Plant": 1.30, "Warehouse": 0.85, "Distribution Center": 0.95, "Office": 0.40}).loc[maintenance_location_keys].to_numpy()
maintenance_type_factor = pd.Series(maintenance_type_values).map({"Preventive": 0.75, "Corrective": 1.60, "Inspection": 0.55}).to_numpy()
maintenance_hours = np.clip(rng.gamma(2.5, 1.5, N_MAINTENANCE), 0.5, 10)
downtime_hours = np.clip(maintenance_hours * rng.uniform(0.8, 3.5, N_MAINTENANCE) * np.where(maintenance_type_values == "Corrective", 1.35, 0.75), 0.5, 24)
maintenance_cost = np.clip(
    rng.gamma(2.2, 1200, N_MAINTENANCE) * maintenance_location_factor * maintenance_type_factor,
    100,
    20000
)

fact_maintenance = pd.DataFrame({
    "maintenance_key": range(1, N_MAINTENANCE + 1),
    "maintenance_id": make_ids("MNT", N_MAINTENANCE),
    "date_key": pd.to_datetime(random_dates(N_MAINTENANCE)).strftime("%Y%m%d").astype(int),
    "location_key": maintenance_location_keys,
    "machine_key": maintenance_machine_keys,
    "employee_key": rng.choice(dim_employee["employee_key"], N_MAINTENANCE),
    "maintenance_type": maintenance_type_values,
    "maintenance_hours": np.round(maintenance_hours, 2),
    "downtime_hours": np.round(downtime_hours, 2),
    "maintenance_cost": np.round(maintenance_cost, 2)
})


# -------------------------
# fact_financial_transaction
# -------------------------

financial_location_keys = rng.choice(dim_location["location_key"], N_FINANCIAL, p=location_activity_weights)
financial_categories = rng.choice(TRANSACTION_CATEGORIES, N_FINANCIAL)
financial_location_factor = location_type_map.map({"Plant": 1.35, "Warehouse": 0.85, "Distribution Center": 1.00, "Office": 0.55}).loc[financial_location_keys].to_numpy()
financial_category_factor = pd.Series(financial_categories).map({"Sales Revenue": 1.50, "Operating Expense": 0.80, "Maintenance": 1.10, "Payroll": 0.90, "Utilities": 0.70, "Materials": 1.25}).to_numpy()
financial_amount = np.clip(rng.gamma(2.2, 8500, N_FINANCIAL) * financial_location_factor * financial_category_factor, 100, 250000)

fact_financial_transaction = pd.DataFrame({
    "financial_transaction_key": range(1, N_FINANCIAL + 1),
    "transaction_id": make_ids("FIN", N_FINANCIAL),
    "date_key": pd.to_datetime(random_dates(N_FINANCIAL)).strftime("%Y%m%d").astype(int),
    "account_key": rng.choice(dim_account["account_key"], N_FINANCIAL),
    "location_key": financial_location_keys,
    "transaction_type": rng.choice(TRANSACTION_TYPES, N_FINANCIAL),
    "transaction_category": financial_categories,
    "transaction_amount": np.round(financial_amount, 2)
})


# -------------------------
# fact_budget
# -------------------------

budget_location_keys = rng.choice(dim_location["location_key"], N_BUDGET, p=location_activity_weights)
budget_categories = rng.choice(BUDGET_CATEGORIES, N_BUDGET)
budget_location_factor = location_type_map.map({"Plant": 1.40, "Warehouse": 0.80, "Distribution Center": 1.00, "Office": 0.55}).loc[budget_location_keys].to_numpy()
budget_category_factor = pd.Series(budget_categories).map({"Revenue": 1.45, "Operations": 1.15, "Maintenance": 0.80, "Payroll": 0.95, "Utilities": 0.70}).to_numpy()
budget_amount = np.clip(rng.gamma(2.5, 70000, N_BUDGET) * budget_location_factor * budget_category_factor, 10000, 1000000)

fact_budget = pd.DataFrame({
    "budget_key": range(1, N_BUDGET + 1),
    "budget_id": make_ids("BUD", N_BUDGET),
    "date_key": pd.to_datetime(random_dates(N_BUDGET)).strftime("%Y%m%d").astype(int),
    "account_key": rng.choice(dim_account["account_key"], N_BUDGET),
    "location_key": budget_location_keys,
    "budget_category": budget_categories,
    "budget_amount": np.round(budget_amount, 2)
})


# -------------------------
# fact_energy
# -------------------------

energy_machine_keys = rng.choice(dim_machine["machine_key"], N_ENERGY)
energy_location_keys = np.array([machine_locations[machine] for machine in energy_machine_keys])
energy_dates = pd.to_datetime(random_dates(N_ENERGY))

# Baseline consumption remains in the same general magnitude, but is driven
# by machine/location characteristics rather than being purely uniform random.
energy_location_factor = location_type_map.map(
    {"Plant": 1.35, "Warehouse": 0.75, "Distribution Center": 0.90, "Office": 0.55}
).loc[energy_location_keys].to_numpy()
energy_source_factor = rng.choice([0.90, 1.00, 1.15], N_ENERGY, p=[0.55, 0.30, 0.15])
energy_consumption = np.round(
    rng.gamma(shape=4.5, scale=900, size=N_ENERGY) * energy_location_factor * energy_source_factor,
    3
)
energy_consumption = np.clip(energy_consumption, 50, 15000)

fact_energy = pd.DataFrame({
    "energy_key": range(1, N_ENERGY + 1),
    "energy_id": make_ids("ENG", N_ENERGY),
    "date_key": energy_dates.strftime("%Y%m%d").astype(int),
    "location_key": energy_location_keys,
    "machine_key": energy_machine_keys,
    "energy_source": rng.choice(ENERGY_SOURCES, N_ENERGY),
    "energy_consumption": energy_consumption
})


# -------------------------
# fact_emissions
# -------------------------

emissions_dates = pd.to_datetime(random_dates(N_EMISSIONS))
emissions_location_keys = rng.choice(dim_location["location_key"], N_EMISSIONS, p=location_activity_weights)
emission_factor = rng.choice([0.28, 0.45, 0.65], N_EMISSIONS, p=[0.45, 0.35, 0.20])
emissions_location_factor = location_type_map.map(
    {"Plant": 1.30, "Warehouse": 0.75, "Distribution Center": 0.90, "Office": 0.55}
).loc[emissions_location_keys].to_numpy()
co2_emissions = np.round(
    rng.gamma(shape=4.0, scale=120, size=N_EMISSIONS) * emissions_location_factor * emission_factor * 4.0,
    3
)
co2_emissions = np.clip(co2_emissions, 5, 7500)

fact_emissions = pd.DataFrame({
    "emissions_key": range(1, N_EMISSIONS + 1),
    "emissions_id": make_ids("EMS", N_EMISSIONS),
    "date_key": emissions_dates.strftime("%Y%m%d").astype(int),
    "location_key": emissions_location_keys,
    "emissions_category": rng.choice(EMISSIONS_CATEGORIES, N_EMISSIONS),
    "co2_emissions": co2_emissions
})


# -------------------------
# fact_waste
# -------------------------

waste_dates = pd.to_datetime(random_dates(N_WASTE))
waste_location_keys = rng.choice(dim_location["location_key"], N_WASTE, p=location_activity_weights)
waste_location_factor = location_type_map.map(
    {"Plant": 1.25, "Warehouse": 0.70, "Distribution Center": 0.85, "Office": 0.45}
).loc[waste_location_keys].to_numpy()
waste_category_factor = rng.choice([0.75, 1.0, 1.25], N_WASTE, p=[0.35, 0.45, 0.20])
waste_quantity = np.round(
    rng.gamma(shape=2.5, scale=55, size=N_WASTE) * waste_location_factor * waste_category_factor,
    3
)
waste_quantity = np.clip(waste_quantity, 0.5, 3000)

fact_waste = pd.DataFrame({
    "waste_key": range(1, N_WASTE + 1),
    "waste_id": make_ids("WST", N_WASTE),
    "date_key": waste_dates.strftime("%Y%m%d").astype(int),
    "location_key": waste_location_keys,
    "waste_category": rng.choice(WASTE_CATEGORIES, N_WASTE),
    "disposal_method": rng.choice(DISPOSAL_METHODS, N_WASTE),
    "waste_quantity": waste_quantity
})


# -------------------------
# fact_inventory
# -------------------------

inventory_dates = pd.date_range(START_DATE, END_DATE)
date_count = len(inventory_dates)

random_numbers = rng.choice(
    date_count * N_PRODUCT * N_LOCATION,
    size=N_INVENTORY,
    replace=False
)

date_index = random_numbers // (N_PRODUCT * N_LOCATION)
remaining = random_numbers % (N_PRODUCT * N_LOCATION)
inventory_product_keys = (remaining // N_LOCATION) + 1
inventory_location_keys = (remaining % N_LOCATION) + 1

product_category_factor = dim_product.set_index("product_key")["category"].map(
    {k: v["demand"] for k, v in PRODUCT_CATEGORY_PROFILE.items()}
).loc[inventory_product_keys].to_numpy()
location_factor = location_type_map.map(
    {"Plant": 1.15, "Warehouse": 1.35, "Distribution Center": 1.10, "Office": 0.35}
).loc[inventory_location_keys].to_numpy()

opening_quantity = np.maximum(0, np.round(rng.gamma(3.0, 550, N_INVENTORY) * product_category_factor * location_factor)).astype(int)
received_quantity = np.maximum(0, np.round(rng.gamma(2.2, 250, N_INVENTORY) * product_category_factor * location_factor)).astype(int)

# Issuance is related to demand and available stock, producing meaningful
# low-stock and excess-stock cases while preserving the accounting identity.
available_quantity = opening_quantity + received_quantity
issue_rate = np.clip(rng.beta(2.5, 3.0, N_INVENTORY) * product_category_factor, 0.02, 0.95)
issued_quantity = np.minimum(np.round(available_quantity * issue_rate).astype(int), available_quantity)
closing_quantity = available_quantity - issued_quantity

reorder_point = np.maximum(50, np.round(
    rng.gamma(2.2, 180, N_INVENTORY) * product_category_factor
).astype(int))

fact_inventory = pd.DataFrame({
    "inventory_key": range(1, N_INVENTORY + 1),
    "inventory_id": make_ids("INV", N_INVENTORY),
    "date_key": inventory_dates[date_index].strftime("%Y%m%d").astype(int),
    "product_key": inventory_product_keys,
    "location_key": inventory_location_keys,
    "opening_quantity": opening_quantity,
    "received_quantity": received_quantity,
    "issued_quantity": issued_quantity,
    "closing_quantity": closing_quantity,
    "reorder_point": reorder_point
})


# ============================================================
# CONTROLLED DATA QUALITY ISSUES
# ============================================================

# ============================================================
# 1. NULL / BLANK VALUES
# ============================================================

dim_customer.loc[
    random_rows(dim_customer, 100),
    "country"
] = np.nan

dim_product.loc[
    random_rows(dim_product, 10),
    "subcategory"
] = np.nan

dim_supplier.loc[
    random_rows(dim_supplier, 5),
    "supplier_category"
] = np.nan

fact_maintenance.loc[
    random_rows(fact_maintenance, 100),
    "maintenance_type"
] = np.nan

# Additional blank values
dim_account.loc[
    random_rows(dim_account, 10),
    "industry"
] = ""

dim_location.loc[
    random_rows(dim_location, 5),
    "city"
] = ""

fact_budget.loc[
    random_rows(fact_budget, 20),
    "budget_category"
] = ""

fact_emissions.loc[
    random_rows(fact_emissions, 20),
    "emissions_category"
] = ""


# ============================================================
# 2. LEADING / TRAILING SPACES
# ============================================================

rows = random_rows(dim_account, 20)
dim_account.loc[rows, "account_name"] = (
    " " + dim_account.loc[rows, "account_name"].astype(str) + " "
)

rows = random_rows(dim_customer, 20)
dim_customer.loc[rows, "customer_name"] = (
    "  " + dim_customer.loc[rows, "customer_name"].astype(str) + "  "
)

rows = random_rows(dim_product, 20)
dim_product.loc[rows, "product_name"] = (
    " " + dim_product.loc[rows, "product_name"].astype(str) + " "
)

rows = random_rows(dim_supplier, 20)
dim_supplier.loc[rows, "supplier_name"] = (
    " " + dim_supplier.loc[rows, "supplier_name"].astype(str) + " "
)

rows = random_rows(dim_employee, 20)
dim_employee.loc[rows, "employee_name"] = (
    " " + dim_employee.loc[rows, "employee_name"].astype(str) + " "
)

rows = random_rows(dim_machine, 20)
dim_machine.loc[rows, "machine_name"] = (
    " " + dim_machine.loc[rows, "machine_name"].astype(str) + " "
)


# ============================================================
# 3. DUPLICATES
# ============================================================

fact_sales = pd.concat(
    [
        fact_sales,
        fact_sales.sample(
            500,
            random_state=SEED
        )
    ],
    ignore_index=True
)

fact_production = pd.concat(
    [
        fact_production,
        fact_production.sample(
            200,
            random_state=SEED
        )
    ],
    ignore_index=True
)

fact_financial_transaction = pd.concat(
    [
        fact_financial_transaction,
        fact_financial_transaction.sample(
            300,
            random_state=SEED
        )
    ],
    ignore_index=True
)


# ============================================================
# 4. INVALID FOREIGN KEYS
# ============================================================

fact_sales.loc[
    random_rows(fact_sales, 500),
    "customer_key"
] = 999999

fact_inventory.loc[
    random_rows(fact_inventory, 500),
    "product_key"
] = 999999

fact_energy.loc[
    random_rows(fact_energy, 100),
    "machine_key"
] = 999999

fact_maintenance.loc[
    random_rows(fact_maintenance, 50),
    "employee_key"
] = 999999


# ============================================================
# 5. INVALID CATEGORIES
# ============================================================

dim_customer.loc[
    random_rows(dim_customer, 50),
    "customer_segment"
] = "Unknown Segment"

# Keep the intentional invalid location-type issue, but avoid changing a
# location that currently hosts a machine so operational relationships
# remain realistic before Phase 4 remediation.
locations_without_machines = dim_location.loc[
    ~dim_location["location_key"].isin(dim_machine["location_key"]),
    "location_key"
].to_numpy()
dim_location.loc[
    rng.choice(locations_without_machines, 5, replace=False) - 1,
    "location_type"
] = "Temporary Facility"

dim_machine.loc[
    random_rows(dim_machine, 20),
    "status"
] = "Unknown"

dim_supplier.loc[
    random_rows(dim_supplier, 10),
    "supplier_category"
] = "Other Supplier"

fact_maintenance.loc[
    random_rows(fact_maintenance, 10),
    "maintenance_type"
] = "Emergency Type"


# ============================================================
# 6. INVALID NUMERIC VALUES
# ============================================================

fact_sales.loc[
    random_rows(fact_sales, 500),
    "quantity"
] = -1

fact_inventory.loc[
    random_rows(fact_inventory, 500),
    "issued_quantity"
] = -10

fact_energy.loc[
    random_rows(fact_energy, 100),
    "energy_consumption"
] = -100

fact_waste.loc[
    random_rows(fact_waste, 100),
    "waste_quantity"
] = -50


# ============================================================
# 7. SALES REVENUE INCONSISTENCY
# ============================================================

sales_issue = random_rows(
    fact_sales,
    500
)

fact_sales.loc[
    sales_issue,
    "revenue"
] = (
    fact_sales.loc[
        sales_issue,
        "quantity"
    ]
    * fact_sales.loc[
        sales_issue,
        "unit_price"
    ]
    * 1.25
).round(2)


# ============================================================
# 8. INVENTORY RECONCILIATION ISSUES
# ============================================================

inventory_issue = random_rows(
    fact_inventory,
    500
)

fact_inventory.loc[
    inventory_issue,
    "closing_quantity"
] = (
    fact_inventory.loc[
        inventory_issue,
        "opening_quantity"
    ]
    + fact_inventory.loc[
        inventory_issue,
        "received_quantity"
    ]
    - fact_inventory.loc[
        inventory_issue,
        "issued_quantity"
    ]
    + 100
)


# ============================================================
# 9. PRODUCTION DEFECT ISSUES
# ============================================================

production_defect_issue = random_rows(
    fact_production,
    200
)

# INVALID:
# Defects are intentionally greater than production.

fact_production.loc[
    production_defect_issue,
    "defect_quantity"
] = (
    fact_production.loc[
        production_defect_issue,
        "produced_quantity"
    ]
    + 10
)


# ============================================================
# 10. PRODUCTION OUTLIERS
# ============================================================

production_outlier = random_rows(
    fact_production,
    100
)

# INVALID OUTLIER:
# Production is intentionally much higher than planned.

fact_production.loc[
    production_outlier,
    "produced_quantity"
] = (
    fact_production.loc[
        production_outlier,
        "planned_quantity"
    ]
    * 3
).astype(int)


# ============================================================
# 11. FINANCIAL OUTLIERS
# ============================================================

financial_outlier = random_rows(
    fact_financial_transaction,
    150
)

fact_financial_transaction.loc[
    financial_outlier,
    "transaction_amount"
] = (
    fact_financial_transaction.loc[
        financial_outlier,
        "transaction_amount"
    ]
    * 10
).round(2)


# ============================================================
# SAVE DATASETS
# ============================================================

print("\nSaving datasets...")

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
    save_data(dataframe, name)


# ============================================================
# FINAL SUMMARY
# ============================================================

total_rows = sum(
    len(dataframe)
    for dataframe in datasets.values()
)

print("\n========================================")
print("PROJECT ATLAS DATA GENERATION COMPLETE")
print("========================================")
print("All data is synthetic.")
print(f"Date range: {START_DATE} to {END_DATE}")
print(f"Datasets generated: {len(datasets)}")
print(f"Total raw rows: {total_rows:,}")
print(f"Files saved to: {OUTPUT_DIR}")
print("========================================")