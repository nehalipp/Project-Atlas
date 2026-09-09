"""
Project Atlas
Phase 3 - Synthetic Data Generation

Generates the 17 approved Atlas datasets:
    8 dimensions + 9 facts

Design goals
------------
- Reproducible synthetic data (seed = 42)
- 2019-01-01 through 2025-12-31 operational period
- Realistic multi-year business trends for BI dashboards
- Consistent operational quantity unit: Each
- Energy: kWh
- Emissions: kg
- Waste: kg
- Controlled raw-data quality issues for Phase 4
- Fact grains remain compatible with the Atlas star schema
- No fact-to-fact foreign keys are created

Phase 4 is responsible for profiling, validating and remediating
these intentionally introduced raw-data quality issues.
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
# STANDARD MEASUREMENT UNITS
# ============================================================

# One common unit is used for product-related quantities so that
# sales, production and inventory quantities remain comparable.
PRODUCT_UNIT_OF_MEASURE = "Each"
ENERGY_UNIT_OF_MEASURE = "kWh"
EMISSIONS_UNIT_OF_MEASURE = "kg"
WASTE_UNIT_OF_MEASURE = "kg"


# ============================================================
# REFERENCE VALUES
# ============================================================

COUNTRIES = [
    "United States",
    "Canada",
    "Germany",
    "Sweden",
    "Mexico",
]

INDUSTRIES = [
    "Manufacturing",
    "Automotive",
    "Retail",
    "Healthcare",
    "Technology",
]

ACCOUNT_TYPES = [
    "Enterprise",
    "Mid-Market",
    "Small Business",
]

CUSTOMER_SEGMENTS = [
    "Enterprise",
    "Mid-Market",
    "SMB",
]

PRODUCT_CATEGORIES = [
    "Industrial Equipment",
    "Components",
    "Electronics",
    "Packaging",
    "Raw Materials",
]

PRODUCT_SUBCATEGORIES = [
    "Standard",
    "Premium",
    "Specialty",
]

SUPPLIER_CATEGORIES = [
    "Manufacturer",
    "Distributor",
    "Service Provider",
    "Raw Material Supplier",
]

LOCATION_TYPES = [
    "Plant",
    "Warehouse",
    "Distribution Center",
    "Office",
]

DEPARTMENTS = [
    "Sales",
    "Operations",
    "Finance",
    "Human Resources",
    "IT",
    "Maintenance",
    "Supply Chain",
]

EMPLOYEE_ROLES = [
    "Analyst",
    "Manager",
    "Supervisor",
    "Operator",
    "Engineer",
    "Coordinator",
    "Specialist",
]

MACHINE_TYPES = [
    "CNC Machine",
    "Assembly Machine",
    "Packaging Machine",
    "Press Machine",
    "Cutting Machine",
]

MAINTENANCE_TYPES = [
    "Preventive",
    "Corrective",
    "Inspection",
]

TRANSACTION_TYPES = [
    "Revenue",
    "Expense",
    "Cost",
]

TRANSACTION_CATEGORIES = [
    "Sales Revenue",
    "Operating Expense",
    "Maintenance",
    "Payroll",
    "Utilities",
    "Materials",
]

BUDGET_CATEGORIES = [
    "Revenue",
    "Operations",
    "Maintenance",
    "Payroll",
    "Utilities",
]

ENERGY_SOURCES = [
    "Electricity",
    "Natural Gas",
    "Diesel",
]

EMISSIONS_CATEGORIES = [
    "Direct Emissions",
    "Purchased Energy",
    "Transportation",
]

WASTE_CATEGORIES = [
    "Metal",
    "Plastic",
    "Paper",
    "Chemical",
    "General",
]

DISPOSAL_METHODS = [
    "Recycling",
    "Landfill",
    "Reuse",
    "Treatment",
]


# ============================================================
# NAMING HELPERS
# ============================================================

PRODUCT_NAME_PREFIXES = {
    "Industrial Equipment": [
        "Hydraulic Power Unit",
        "Pneumatic Control Unit",
        "Industrial Drive System",
        "Process Pump Assembly",
        "Material Handling Unit",
        "Thermal Processing Unit",
    ],
    "Components": [
        "Precision Bearing Assembly",
        "Steel Coupling",
        "Aluminum Mounting Bracket",
        "Drive Shaft Assembly",
        "Industrial Valve Assembly",
        "Conveyor Roller Assembly",
    ],
    "Electronics": [
        "Industrial Control Module",
        "Variable Frequency Drive",
        "Proximity Sensor",
        "Power Distribution Module",
        "Motor Control Panel",
        "Industrial Signal Converter",
    ],
    "Packaging": [
        "Corrugated Shipping Carton",
        "Protective Packaging Insert",
        "Industrial Stretch Film",
        "Pallet Wrap Assembly",
        "Heavy-Duty Packaging Sleeve",
        "Reusable Transport Crate",
    ],
    "Raw Materials": [
        "Cold Rolled Steel Coil",
        "Aluminum Sheet Stock",
        "Polymer Resin",
        "Industrial Copper Wire",
        "Stainless Steel Sheet",
        "Engineering Plastic Pellets",
    ],
}

MACHINE_NAME_PREFIXES = {
    "CNC Machine": [
        "CNC Vertical Machining Center",
        "CNC Horizontal Machining Center",
        "CNC Turning Center",
        "CNC Precision Mill",
    ],
    "Assembly Machine": [
        "Automated Assembly Cell",
        "Servo Assembly Station",
        "Robotic Assembly Cell",
        "Precision Assembly Line",
    ],
    "Packaging Machine": [
        "Automated Carton Packer",
        "High-Speed Labeling Machine",
        "Case Sealing System",
        "Flexible Packaging Line",
    ],
    "Press Machine": [
        "Hydraulic Press",
        "Mechanical Stamping Press",
        "Precision Forming Press",
        "Servo Press System",
    ],
    "Cutting Machine": [
        "Laser Cutting System",
        "Precision Slitting Machine",
        "Industrial Sawing Center",
        "CNC Plasma Cutting System",
    ],
}


def make_ids(prefix, number):
    return [f"{prefix}-{i:06d}" for i in range(1, number + 1)]


def random_dates(number):
    dates = pd.date_range(START_DATE, END_DATE)
    return rng.choice(dates, number)


def random_attribute_dates(number):
    dates = pd.date_range(ATTRIBUTE_START_DATE, ATTRIBUTE_END_DATE)
    return rng.choice(dates, number)


def random_rows(dataframe, number):
    return rng.choice(dataframe.index.to_numpy(), size=number, replace=False)


def make_product_names(categories, subcategories):
    names = []
    for i, (category, subcategory) in enumerate(
        zip(categories, subcategories), start=1
    ):
        prefix = PRODUCT_NAME_PREFIXES[category][
            (i - 1) % len(PRODUCT_NAME_PREFIXES[category])
        ]
        names.append(f"{prefix} {subcategory} Series {i:04d}")
    return names


def make_machine_names(machine_types):
    names = []
    type_counts = {}
    for machine_type in machine_types:
        type_counts[machine_type] = type_counts.get(machine_type, 0) + 1
        prefix = MACHINE_NAME_PREFIXES[machine_type][
            (type_counts[machine_type] - 1)
            % len(MACHINE_NAME_PREFIXES[machine_type])
        ]
        names.append(f"{prefix} {type_counts[machine_type]:03d}")
    return names


def save_data(dataframe, name):
    path = OUTPUT_DIR / f"{name}.csv"
    dataframe.to_csv(path, index=False)
    print(f"{name:32} {len(dataframe):>10,} rows")


# ============================================================
# TREND HELPERS
# ============================================================

# These year multipliers create a believable business trajectory:
# growth in commercial activity and production, with gradual
# efficiency improvements in energy, emissions and waste.
YEAR_FACTORS = {
    2019: 0.86,
    2020: 0.82,
    2021: 0.94,
    2022: 1.00,
    2023: 1.08,
    2024: 1.17,
    2025: 1.27,
}


# Month seasonality is deliberately moderate. It should create
# visible monthly patterns without overwhelming the yearly trend.
MONTH_FACTORS = {
    1: 0.94,
    2: 0.96,
    3: 1.02,
    4: 1.00,
    5: 1.04,
    6: 1.06,
    7: 0.98,
    8: 1.00,
    9: 1.05,
    10: 1.08,
    11: 1.03,
    12: 0.93,
}


def year_factor_from_dates(dates):
    years = pd.DatetimeIndex(pd.to_datetime(dates)).year
    return np.array([YEAR_FACTORS[int(year)] for year in years], dtype=float)


def month_factor_from_dates(dates):
    months = pd.DatetimeIndex(pd.to_datetime(dates)).month
    return np.array([MONTH_FACTORS[int(month)] for month in months], dtype=float)


def operational_trend(dates):
    return year_factor_from_dates(dates) * month_factor_from_dates(dates)


def validate_lengths(dataset_name, expected, **arrays):
    for name, values in arrays.items():
        actual = len(values)
        if actual != expected:
            raise ValueError(
                f"{dataset_name}: {name} has {actual:,} values; "
                f"expected {expected:,}."
            )


def validate_single_unit(dataframe, column, expected_unit, dataset_name):
    units = dataframe[column].dropna().astype(str).unique().tolist()
    if units != [expected_unit]:
        raise ValueError(
            f"{dataset_name}: expected only '{expected_unit}' in {column}; "
            f"found {sorted(units)}"
        )
    print(f"{dataset_name}.{column}: PASS - {expected_unit}")


# ============================================================
# DIMENSIONS
# ============================================================

print("\nGenerating dimensions...")


# -------------------------
# dim_date
# -------------------------

dates = pd.date_range(START_DATE, END_DATE)

dim_date = pd.DataFrame({
    "date_key": dates.strftime("%Y%m%d").astype(int),
    "full_date": dates,
    "day_of_week": dates.dayofweek + 1,
    "day_name": dates.day_name(),
    "week_number": dates.isocalendar().week.astype(int),
    "month": dates.month,
    "month_name": dates.month_name(),
    "quarter": dates.quarter,
    "year": dates.year,
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
    "status": rng.choice(["Active", "Inactive"], N_ACCOUNT, p=[0.90, 0.10]),
})


# -------------------------
# dim_customer
# -------------------------

dim_customer = pd.DataFrame({
    "customer_key": range(1, N_CUSTOMER + 1),
    "customer_id": make_ids("CUS", N_CUSTOMER),
    "account_key": rng.choice(dim_account["account_key"], N_CUSTOMER),
    "customer_name": [fake.company() for _ in range(N_CUSTOMER)],
    "customer_segment": rng.choice(CUSTOMER_SEGMENTS, N_CUSTOMER),
    "industry": rng.choice(INDUSTRIES, N_CUSTOMER),
    "country": rng.choice(COUNTRIES, N_CUSTOMER),
    "status": rng.choice(["Active", "Inactive"], N_CUSTOMER, p=[0.90, 0.10]),
})


# -------------------------
# dim_supplier
# -------------------------

dim_supplier = pd.DataFrame({
    "supplier_key": range(1, N_SUPPLIER + 1),
    "supplier_id": make_ids("SUP", N_SUPPLIER),
    "supplier_name": [fake.company() for _ in range(N_SUPPLIER)],
    "supplier_category": rng.choice(SUPPLIER_CATEGORIES, N_SUPPLIER),
    "country": rng.choice(COUNTRIES, N_SUPPLIER),
    "status": rng.choice(["Active", "Inactive"], N_SUPPLIER, p=[0.90, 0.10]),
})


# -------------------------
# dim_product
# -------------------------

unit_cost = np.round(rng.uniform(10, 500, N_PRODUCT), 2)
unit_price = np.round(unit_cost * rng.uniform(1.25, 2.50, N_PRODUCT), 2)
product_categories = rng.choice(PRODUCT_CATEGORIES, N_PRODUCT)
product_subcategories = rng.choice(PRODUCT_SUBCATEGORIES, N_PRODUCT)

# ALL product quantities use one unit: Each.
dim_product = pd.DataFrame({
    "product_key": range(1, N_PRODUCT + 1),
    "product_id": make_ids("PROD", N_PRODUCT),
    "supplier_key": rng.choice(dim_supplier["supplier_key"], N_PRODUCT),
    "product_name": make_product_names(product_categories, product_subcategories),
    "category": product_categories,
    "subcategory": product_subcategories,
    "unit_of_measure": [PRODUCT_UNIT_OF_MEASURE] * N_PRODUCT,
    "unit_cost": unit_cost,
    "unit_price": unit_price,
    "status": rng.choice(["Active", "Inactive"], N_PRODUCT, p=[0.90, 0.10]),
})


# -------------------------
# dim_location
# -------------------------

location_types = rng.choice(LOCATION_TYPES, N_LOCATION)
location_cities = [fake.city() for _ in range(N_LOCATION)]

dim_location = pd.DataFrame({
    "location_key": range(1, N_LOCATION + 1),
    "location_id": make_ids("LOC", N_LOCATION),
    "location_name": [
        f"{city} {location_type} Facility"
        for city, location_type in zip(location_cities, location_types)
    ],
    "location_type": location_types,
    "city": location_cities,
    "state_region": [fake.state() for _ in range(N_LOCATION)],
    "country": rng.choice(COUNTRIES, N_LOCATION),
    "status": rng.choice(["Active", "Inactive"], N_LOCATION, p=[0.90, 0.10]),
})


# -------------------------
# dim_employee
# -------------------------

dim_employee = pd.DataFrame({
    "employee_key": range(1, N_EMPLOYEE + 1),
    "employee_id": make_ids("EMP", N_EMPLOYEE),
    "location_key": rng.choice(dim_location["location_key"], N_EMPLOYEE),
    "employee_name": [fake.name() for _ in range(N_EMPLOYEE)],
    "department": rng.choice(DEPARTMENTS, N_EMPLOYEE),
    "role": rng.choice(EMPLOYEE_ROLES, N_EMPLOYEE),
    "hire_date": random_attribute_dates(N_EMPLOYEE),
    "status": rng.choice(["Active", "Inactive"], N_EMPLOYEE, p=[0.92, 0.08]),
})


# -------------------------
# dim_machine
# -------------------------

machine_types = rng.choice(MACHINE_TYPES, N_MACHINE)

dim_machine = pd.DataFrame({
    "machine_key": range(1, N_MACHINE + 1),
    "machine_id": make_ids("MCH", N_MACHINE),
    "location_key": rng.choice(dim_location["location_key"], N_MACHINE),
    "machine_name": make_machine_names(machine_types),
    "machine_type": machine_types,
    "installation_date": random_attribute_dates(N_MACHINE),
    "status": rng.choice(
        ["Operational", "Maintenance", "Inactive"],
        N_MACHINE,
        p=[0.85, 0.10, 0.05],
    ),
})


# ============================================================
# LOOKUPS
# ============================================================

product_prices = dict(zip(dim_product["product_key"], dim_product["unit_price"]))
product_costs = dict(zip(dim_product["product_key"], dim_product["unit_cost"]))
product_units = dict(zip(dim_product["product_key"], dim_product["unit_of_measure"]))
machine_locations = dict(zip(dim_machine["machine_key"], dim_machine["location_key"]))


# ============================================================
# FACT TABLES
# ============================================================

print("\nGenerating facts...")


# ============================================================
# fact_sales
# ============================================================

sales_dates = pd.to_datetime(random_dates(N_SALES))
sales_trend = operational_trend(sales_dates)

sales_product_keys = rng.choice(dim_product["product_key"].to_numpy(), N_SALES)
sales_quantity = np.maximum(
    1,
    np.round(
        rng.lognormal(mean=3.1, sigma=0.65, size=N_SALES)
        * sales_trend
        / 2.0
    ).astype(int),
)

sales_unit_price = np.array([product_prices[key] for key in sales_product_keys])

discount_rate = np.clip(
    rng.beta(2.0, 18.0, N_SALES),
    0,
    0.20,
)
discount = np.round(sales_quantity * sales_unit_price * discount_rate, 2)

revenue = np.round(
    sales_quantity * sales_unit_price - discount,
    2,
)

validate_lengths(
    "fact_sales",
    N_SALES,
    dates=sales_dates,
    product_keys=sales_product_keys,
    quantity=sales_quantity,
    unit_price=sales_unit_price,
    revenue=revenue,
)

fact_sales = pd.DataFrame({
    "sales_key": range(1, N_SALES + 1),
    "transaction_id": make_ids("SAL", N_SALES),
    "date_key": sales_dates.strftime("%Y%m%d").astype(int),
    "customer_key": rng.choice(dim_customer["customer_key"].to_numpy(), N_SALES),
    "product_key": sales_product_keys,
    "unit_of_measure": [product_units[key] for key in sales_product_keys],
    "location_key": rng.choice(dim_location["location_key"].to_numpy(), N_SALES),
    "quantity": sales_quantity,
    "unit_price": sales_unit_price,
    "discount_amount": discount,
    "revenue": revenue,
})


# ============================================================
# fact_production
# ============================================================

production_dates = pd.to_datetime(random_dates(N_PRODUCTION))
production_trend = operational_trend(production_dates)
production_machine_keys = rng.choice(dim_machine["machine_key"].to_numpy(), N_PRODUCTION)
production_location_keys = np.array(
    [machine_locations[machine] for machine in production_machine_keys]
)

planned_quantity = np.maximum(
    50,
    np.round(
        rng.normal(260, 80, N_PRODUCTION) * production_trend
    ).astype(int),
)

planned_quantity = np.clip(planned_quantity, 50, 650)

achievement = np.clip(
    rng.normal(0.94, 0.045, N_PRODUCTION),
    0.78,
    1.00,
)
produced_quantity = np.round(planned_quantity * achievement).astype(int)

# Valid baseline: defects cannot exceed produced quantity.
defect_rate = np.clip(rng.beta(1.8, 35.0, N_PRODUCTION), 0.001, 0.15)
defect_quantity = np.minimum(
    produced_quantity,
    np.round(produced_quantity * defect_rate).astype(int),
)

production_product_keys = rng.choice(dim_product["product_key"].to_numpy(), N_PRODUCTION)

production_hours = np.round(
    np.clip(
        planned_quantity / rng.uniform(35, 65, N_PRODUCTION),
        1,
        12,
    ),
    2,
)

validate_lengths(
    "fact_production",
    N_PRODUCTION,
    dates=production_dates,
    machine_keys=production_machine_keys,
    product_keys=production_product_keys,
    planned=planned_quantity,
    produced=produced_quantity,
    defects=defect_quantity,
)

fact_production = pd.DataFrame({
    "production_key": range(1, N_PRODUCTION + 1),
    "production_id": make_ids("PRD", N_PRODUCTION),
    "date_key": production_dates.strftime("%Y%m%d").astype(int),
    "product_key": production_product_keys,
    "unit_of_measure": [product_units[key] for key in production_product_keys],
    "location_key": production_location_keys,
    "machine_key": production_machine_keys,
    "employee_key": rng.choice(dim_employee["employee_key"].to_numpy(), N_PRODUCTION),
    "planned_quantity": planned_quantity,
    "produced_quantity": produced_quantity,
    "defect_quantity": defect_quantity,
    "production_hours": production_hours,
})


# ============================================================
# fact_maintenance
# ============================================================

maintenance_dates = pd.to_datetime(random_dates(N_MAINTENANCE))
maintenance_machine_keys = rng.choice(dim_machine["machine_key"].to_numpy(), N_MAINTENANCE)
maintenance_location_keys = np.array(
    [machine_locations[machine] for machine in maintenance_machine_keys]
)

maintenance_type = rng.choice(
    MAINTENANCE_TYPES,
    N_MAINTENANCE,
    p=[0.55, 0.30, 0.15],
)

maintenance_hours = np.round(
    rng.gamma(shape=2.5, scale=1.0, size=N_MAINTENANCE),
    2,
)

# Corrective maintenance tends to create more downtime.
downtime_multiplier = np.where(
    maintenance_type == "Corrective", 2.4,
    np.where(maintenance_type == "Preventive", 0.9, 0.5),
)

downtime_hours = np.round(
    np.clip(
        maintenance_hours * downtime_multiplier * rng.uniform(0.8, 1.5, N_MAINTENANCE),
        0.25,
        24,
    ),
    2,
)

maintenance_cost = np.round(
    np.clip(
        250
        + maintenance_hours * rng.uniform(150, 700, N_MAINTENANCE)
        + downtime_hours * rng.uniform(50, 250, N_MAINTENANCE),
        100,
        25_000,
    ),
    2,
)

fact_maintenance = pd.DataFrame({
    "maintenance_key": range(1, N_MAINTENANCE + 1),
    "maintenance_id": make_ids("MNT", N_MAINTENANCE),
    "date_key": maintenance_dates.strftime("%Y%m%d").astype(int),
    "location_key": maintenance_location_keys,
    "machine_key": maintenance_machine_keys,
    "employee_key": rng.choice(dim_employee["employee_key"].to_numpy(), N_MAINTENANCE),
    "maintenance_type": maintenance_type,
    "maintenance_hours": maintenance_hours,
    "downtime_hours": downtime_hours,
    "maintenance_cost": maintenance_cost,
})


# ============================================================
# fact_financial_transaction
# ============================================================

financial_dates = pd.to_datetime(random_dates(N_FINANCIAL))
financial_trend = operational_trend(financial_dates)

transaction_type = rng.choice(
    TRANSACTION_TYPES,
    N_FINANCIAL,
    p=[0.38, 0.34, 0.28],
)

# Category probabilities are intentionally aligned to transaction types.
category_by_type = {
    "Revenue": ["Sales Revenue"],
    "Expense": ["Operating Expense", "Payroll", "Utilities"],
    "Cost": ["Maintenance", "Materials"],
}
transaction_category = np.array([
    rng.choice(category_by_type[t]) for t in transaction_type
])

base_amount = np.maximum(
    100,
    rng.lognormal(mean=8.0, sigma=0.8, size=N_FINANCIAL) * financial_trend,
)

# Revenue is somewhat larger than operating costs on average,
# which creates a sensible positive net financial result before
# controlled raw-data issues are introduced.
type_multiplier = np.where(
    transaction_type == "Revenue", 1.45,
    np.where(transaction_type == "Expense", 0.70, 0.80),
)

transaction_amount = np.round(
    np.clip(base_amount * type_multiplier, 100, 100_000),
    2,
)

fact_financial_transaction = pd.DataFrame({
    "financial_transaction_key": range(1, N_FINANCIAL + 1),
    "transaction_id": make_ids("FIN", N_FINANCIAL),
    "date_key": financial_dates.strftime("%Y%m%d").astype(int),
    "account_key": rng.choice(dim_account["account_key"].to_numpy(), N_FINANCIAL),
    "location_key": rng.choice(dim_location["location_key"].to_numpy(), N_FINANCIAL),
    "transaction_type": transaction_type,
    "transaction_category": transaction_category,
    "transaction_amount": transaction_amount,
})


# ============================================================
# fact_budget
# ============================================================

budget_dates = pd.to_datetime(random_dates(N_BUDGET))
budget_trend = operational_trend(budget_dates)

budget_category = rng.choice(
    BUDGET_CATEGORIES,
    N_BUDGET,
    p=[0.15, 0.35, 0.18, 0.17, 0.15],
)

budget_base = rng.lognormal(mean=11.0, sigma=0.65, size=N_BUDGET)
budget_amount = np.round(
    np.clip(budget_base * budget_trend, 10_000, 750_000),
    2,
)

fact_budget = pd.DataFrame({
    "budget_key": range(1, N_BUDGET + 1),
    "budget_id": make_ids("BUD", N_BUDGET),
    "date_key": budget_dates.strftime("%Y%m%d").astype(int),
    "account_key": rng.choice(dim_account["account_key"].to_numpy(), N_BUDGET),
    "location_key": rng.choice(dim_location["location_key"].to_numpy(), N_BUDGET),
    "budget_category": budget_category,
    "budget_amount": budget_amount,
})


# ============================================================
# fact_energy
# ============================================================

energy_dates = pd.to_datetime(random_dates(N_ENERGY))
energy_trend = operational_trend(energy_dates)
energy_machine_keys = rng.choice(dim_machine["machine_key"].to_numpy(), N_ENERGY)
energy_location_keys = np.array(
    [machine_locations[machine] for machine in energy_machine_keys]
)
energy_source = rng.choice(
    ENERGY_SOURCES,
    N_ENERGY,
    p=[0.60, 0.25, 0.15],
)

# Energy use grows with operations, but efficiency gradually improves.
energy_efficiency = np.interp(
    pd.DatetimeIndex(energy_dates).year,
    [2019, 2020, 2021, 2022, 2023, 2024, 2025],
    [1.00, 0.99, 0.97, 0.95, 0.93, 0.91, 0.89],
)

source_multiplier = np.where(
    energy_source == "Electricity", 1.00,
    np.where(energy_source == "Natural Gas", 1.25, 1.45),
)

energy_consumption = np.round(
    np.clip(
        rng.lognormal(mean=7.5, sigma=0.65, size=N_ENERGY)
        * energy_trend
        * energy_efficiency
        * source_multiplier,
        25,
        30_000,
    ),
    3,
)

fact_energy = pd.DataFrame({
    "energy_key": range(1, N_ENERGY + 1),
    "energy_id": make_ids("ENG", N_ENERGY),
    "date_key": energy_dates.strftime("%Y%m%d").astype(int),
    "location_key": energy_location_keys,
    "machine_key": energy_machine_keys,
    "energy_source": energy_source,
    "unit_of_measure": [ENERGY_UNIT_OF_MEASURE] * N_ENERGY,
    "energy_consumption": energy_consumption,
})


# ============================================================
# fact_emissions
# ============================================================

# IMPORTANT: fact_emissions has a different grain from fact_energy.
# We therefore do NOT copy machine-level energy rows into this fact.
# Instead, emissions are generated independently at the approved
# location/category/date grain while retaining a sensible relationship
# to operational activity through common trend factors.

emissions_dates = pd.to_datetime(random_dates(N_EMISSIONS))
emissions_trend = operational_trend(emissions_dates)
emissions_years = pd.DatetimeIndex(emissions_dates).year

# Gradual emissions-intensity improvement over the period.
emissions_efficiency = np.interp(
    emissions_years,
    [2019, 2020, 2021, 2022, 2023, 2024, 2025],
    [1.00, 0.99, 0.97, 0.95, 0.92, 0.89, 0.86],
)

emissions_category = rng.choice(
    EMISSIONS_CATEGORIES,
    N_EMISSIONS,
    p=[0.45, 0.40, 0.15],
)

emission_category_multiplier = np.where(
    emissions_category == "Transportation", 1.30,
    np.where(emissions_category == "Direct Emissions", 1.15, 0.95),
)

# Synthetic analytical factors. They are intentionally documented as
# portfolio-generation factors rather than real-world regulatory factors.
emission_base = {
    "Direct Emissions": 0.55,
    "Purchased Energy": 0.42,
    "Transportation": 0.75,
}

emission_factor = np.array([
    emission_base[category] for category in emissions_category
])

co2_emissions = np.round(
    np.clip(
        rng.lognormal(mean=7.2, sigma=0.65, size=N_EMISSIONS)
        * emissions_trend
        * emissions_efficiency
        * emission_factor
        * emission_category_multiplier,
        1,
        25_000,
    ),
    3,
)

fact_emissions = pd.DataFrame({
    "emissions_key": range(1, N_EMISSIONS + 1),
    "emissions_id": make_ids("EMS", N_EMISSIONS),
    "date_key": emissions_dates.strftime("%Y%m%d").astype(int),
    "location_key": rng.choice(dim_location["location_key"].to_numpy(), N_EMISSIONS),
    "emissions_category": emissions_category,
    "unit_of_measure": [EMISSIONS_UNIT_OF_MEASURE] * N_EMISSIONS,
    "co2_emissions": co2_emissions,
})


# ============================================================
# fact_waste
# ============================================================

waste_dates = pd.to_datetime(random_dates(N_WASTE))
waste_trend = operational_trend(waste_dates)
waste_years = pd.DatetimeIndex(waste_dates).year

waste_efficiency = np.interp(
    waste_years,
    [2019, 2020, 2021, 2022, 2023, 2024, 2025],
    [1.00, 0.99, 0.97, 0.95, 0.92, 0.89, 0.86],
)

waste_category = rng.choice(
    WASTE_CATEGORIES,
    N_WASTE,
    p=[0.25, 0.22, 0.18, 0.10, 0.25],
)

disposal_method = rng.choice(
    DISPOSAL_METHODS,
    N_WASTE,
    p=[0.48, 0.28, 0.12, 0.12],
)

waste_category_multiplier = np.where(
    waste_category == "Metal", 1.15,
    np.where(waste_category == "Chemical", 0.75, 1.00),
)

waste_quantity = np.round(
    np.clip(
        rng.lognormal(mean=5.2, sigma=0.75, size=N_WASTE)
        * waste_trend
        * waste_efficiency
        * waste_category_multiplier,
        1,
        10_000,
    ),
    3,
)

fact_waste = pd.DataFrame({
    "waste_key": range(1, N_WASTE + 1),
    "waste_id": make_ids("WST", N_WASTE),
    "date_key": waste_dates.strftime("%Y%m%d").astype(int),
    "location_key": rng.choice(dim_location["location_key"].to_numpy(), N_WASTE),
    "waste_category": waste_category,
    "disposal_method": disposal_method,
    "unit_of_measure": [WASTE_UNIT_OF_MEASURE] * N_WASTE,
    "waste_quantity": waste_quantity,
})


# ============================================================
# fact_inventory
# ============================================================

inventory_dates = pd.date_range(START_DATE, END_DATE)
date_count = len(inventory_dates)

# Select unique date/product/location combinations. This prevents
# accidental duplicate snapshots at the same natural grain.
random_numbers = rng.choice(
    date_count * N_PRODUCT * N_LOCATION,
    size=N_INVENTORY,
    replace=False,
)

date_index = random_numbers // (N_PRODUCT * N_LOCATION)
remaining = random_numbers % (N_PRODUCT * N_LOCATION)

inventory_product_keys = (remaining // N_LOCATION) + 1
inventory_location_keys = (remaining % N_LOCATION) + 1

inventory_dates_selected = inventory_dates[date_index]
inventory_trend = operational_trend(inventory_dates_selected)

opening_quantity = np.maximum(
    0,
    np.round(
        rng.lognormal(mean=7.2, sigma=0.65, size=N_INVENTORY)
        * np.sqrt(inventory_trend)
    ).astype(int),
)

received_quantity = np.maximum(
    0,
    np.round(
        rng.lognormal(mean=6.0, sigma=0.70, size=N_INVENTORY)
        * inventory_trend
    ).astype(int),
)

issued_quantity = np.minimum(
    np.maximum(
        0,
        np.round(
            rng.lognormal(mean=6.1, sigma=0.75, size=N_INVENTORY)
            * inventory_trend
        ).astype(int),
    ),
    opening_quantity + received_quantity,
)

closing_quantity = opening_quantity + received_quantity - issued_quantity

reorder_point = np.maximum(
    100,
    np.round(
        rng.lognormal(mean=6.4, sigma=0.45, size=N_INVENTORY)
    ).astype(int),
)
reorder_point = np.clip(reorder_point, 100, 5_000)

fact_inventory = pd.DataFrame({
    "inventory_key": range(1, N_INVENTORY + 1),
    "inventory_id": make_ids("INV", N_INVENTORY),
    "date_key": pd.DatetimeIndex(inventory_dates_selected).strftime("%Y%m%d").astype(int),
    "product_key": inventory_product_keys,
    "unit_of_measure": [product_units[key] for key in inventory_product_keys],
    "location_key": inventory_location_keys,
    "opening_quantity": opening_quantity,
    "received_quantity": received_quantity,
    "issued_quantity": issued_quantity,
    "closing_quantity": closing_quantity,
    "reorder_point": reorder_point,
})


# ============================================================
# CONTROLLED RAW-DATA QUALITY ISSUES
# ============================================================

print("\nIntroducing controlled raw-data quality issues...")


# ------------------------------------------------------------
# 1. NULL / BLANK VALUES
# ------------------------------------------------------------

dim_customer.loc[random_rows(dim_customer, 100), "country"] = np.nan
dim_product.loc[random_rows(dim_product, 10), "subcategory"] = np.nan
dim_supplier.loc[random_rows(dim_supplier, 5), "supplier_category"] = np.nan
fact_maintenance.loc[random_rows(fact_maintenance, 100), "maintenance_type"] = np.nan

dim_account.loc[random_rows(dim_account, 10), "industry"] = ""
dim_location.loc[random_rows(dim_location, 5), "city"] = ""
fact_budget.loc[random_rows(fact_budget, 20), "budget_category"] = ""
fact_emissions.loc[random_rows(fact_emissions, 20), "emissions_category"] = ""


# ------------------------------------------------------------
# 2. LEADING / TRAILING SPACES
# ------------------------------------------------------------

for dataframe, column, count in [
    (dim_account, "account_name", 20),
    (dim_customer, "customer_name", 20),
    (dim_product, "product_name", 20),
    (dim_supplier, "supplier_name", 20),
    (dim_employee, "employee_name", 20),
    (dim_machine, "machine_name", 20),
]:
    rows = random_rows(dataframe, count)
    dataframe.loc[rows, column] = (
        " " + dataframe.loc[rows, column].astype(str) + " "
    )


# ------------------------------------------------------------
# 3. DUPLICATE ROWS
# ------------------------------------------------------------

# Duplicates are added after valid keys are created so Phase 4 can
# demonstrate uniqueness checks and remediation.
fact_sales = pd.concat(
    [fact_sales, fact_sales.sample(500, random_state=SEED)],
    ignore_index=True,
)

fact_production = pd.concat(
    [fact_production, fact_production.sample(200, random_state=SEED)],
    ignore_index=True,
)

fact_financial_transaction = pd.concat(
    [fact_financial_transaction, fact_financial_transaction.sample(300, random_state=SEED)],
    ignore_index=True,
)


# ------------------------------------------------------------
# 4. INVALID FOREIGN KEYS
# ------------------------------------------------------------

fact_sales.loc[random_rows(fact_sales, 500), "customer_key"] = 999999
fact_inventory.loc[random_rows(fact_inventory, 500), "product_key"] = 999999
fact_energy.loc[random_rows(fact_energy, 100), "machine_key"] = 999999
fact_maintenance.loc[random_rows(fact_maintenance, 50), "employee_key"] = 999999


# ------------------------------------------------------------
# 5. INVALID CATEGORIES / DOMAIN VALUES
# ------------------------------------------------------------

dim_customer.loc[random_rows(dim_customer, 50), "customer_segment"] = "Unknown Segment"
dim_location.loc[random_rows(dim_location, 5), "location_type"] = "Temporary Facility"
dim_machine.loc[random_rows(dim_machine, 20), "status"] = "Unknown"
dim_supplier.loc[random_rows(dim_supplier, 10), "supplier_category"] = "Other Supplier"
fact_maintenance.loc[random_rows(fact_maintenance, 10), "maintenance_type"] = "Emergency Type"


# ------------------------------------------------------------
# 6. INVALID NUMERIC VALUES
# ------------------------------------------------------------

fact_sales.loc[random_rows(fact_sales, 500), "quantity"] = -1
fact_inventory.loc[random_rows(fact_inventory, 500), "issued_quantity"] = -10
fact_energy.loc[random_rows(fact_energy, 100), "energy_consumption"] = -100
fact_waste.loc[random_rows(fact_waste, 100), "waste_quantity"] = -50


# ------------------------------------------------------------
# 7. SALES REVENUE INCONSISTENCY
# ------------------------------------------------------------

sales_issue = random_rows(fact_sales, 500)
fact_sales.loc[sales_issue, "revenue"] = (
    fact_sales.loc[sales_issue, "quantity"]
    * fact_sales.loc[sales_issue, "unit_price"]
    * 1.25
).round(2)


# ------------------------------------------------------------
# 8. INVENTORY RECONCILIATION ISSUES
# ------------------------------------------------------------

inventory_issue = random_rows(fact_inventory, 500)
fact_inventory.loc[inventory_issue, "closing_quantity"] = (
    fact_inventory.loc[inventory_issue, "opening_quantity"]
    + fact_inventory.loc[inventory_issue, "received_quantity"]
    - fact_inventory.loc[inventory_issue, "issued_quantity"]
    + 100
)


# ------------------------------------------------------------
# 9. PRODUCTION DEFECT ISSUES
# ------------------------------------------------------------

production_defect_issue = random_rows(fact_production, 200)
fact_production.loc[production_defect_issue, "defect_quantity"] = (
    fact_production.loc[production_defect_issue, "produced_quantity"] + 10
)


# ------------------------------------------------------------
# 10. PRODUCTION OUTLIERS
# ------------------------------------------------------------

production_outlier = random_rows(fact_production, 100)
fact_production.loc[production_outlier, "produced_quantity"] = (
    fact_production.loc[production_outlier, "planned_quantity"] * 3
).astype(int)


# ------------------------------------------------------------
# 11. FINANCIAL OUTLIERS
# ------------------------------------------------------------

financial_outlier = random_rows(fact_financial_transaction, 150)
fact_financial_transaction.loc[financial_outlier, "transaction_amount"] = (
    fact_financial_transaction.loc[financial_outlier, "transaction_amount"] * 10
).round(2)


# ============================================================
# FINAL VALIDATION
# ============================================================

print("\nValidating measurement units...")

validate_single_unit(
    dim_product,
    "unit_of_measure",
    PRODUCT_UNIT_OF_MEASURE,
    "dim_product",
)
validate_single_unit(
    fact_sales,
    "unit_of_measure",
    PRODUCT_UNIT_OF_MEASURE,
    "fact_sales",
)
validate_single_unit(
    fact_production,
    "unit_of_measure",
    PRODUCT_UNIT_OF_MEASURE,
    "fact_production",
)
validate_single_unit(
    fact_inventory,
    "unit_of_measure",
    PRODUCT_UNIT_OF_MEASURE,
    "fact_inventory",
)
validate_single_unit(
    fact_energy,
    "unit_of_measure",
    ENERGY_UNIT_OF_MEASURE,
    "fact_energy",
)
validate_single_unit(
    fact_emissions,
    "unit_of_measure",
    EMISSIONS_UNIT_OF_MEASURE,
    "fact_emissions",
)
validate_single_unit(
    fact_waste,
    "unit_of_measure",
    WASTE_UNIT_OF_MEASURE,
    "fact_waste",
)


# Ensure controlled issues did not accidentally alter row grain
# beyond the intentional duplicate additions.
expected_minimum_rows = {
    "fact_sales": N_SALES,
    "fact_production": N_PRODUCTION,
    "fact_maintenance": N_MAINTENANCE,
    "fact_financial_transaction": N_FINANCIAL,
    "fact_budget": N_BUDGET,
    "fact_energy": N_ENERGY,
    "fact_emissions": N_EMISSIONS,
    "fact_waste": N_WASTE,
    "fact_inventory": N_INVENTORY,
}

for dataset_name, expected in expected_minimum_rows.items():
    dataframe = locals()[dataset_name]
    if len(dataframe) < expected:
        raise ValueError(
            f"{dataset_name}: generated {len(dataframe):,} rows; "
            f"expected at least {expected:,}."
        )


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
    "fact_inventory": fact_inventory,
}

for name, dataframe in datasets.items():
    save_data(dataframe, name)


# ============================================================
# FINAL SUMMARY
# ============================================================

total_rows = sum(len(dataframe) for dataframe in datasets.values())

print("\n========================================")
print("PROJECT ATLAS DATA GENERATION COMPLETE")
print("========================================")
print("All data is synthetic.")
print(f"Date range: {START_DATE} to {END_DATE}")
print(f"Datasets generated: {len(datasets)}")
print(f"Total raw rows: {total_rows:,}")
print(f"Files saved to: {OUTPUT_DIR}")
print(f"Operational quantity unit: {PRODUCT_UNIT_OF_MEASURE}")
print(f"Energy unit: {ENERGY_UNIT_OF_MEASURE}")
print(f"Emissions unit: {EMISSIONS_UNIT_OF_MEASURE}")
print(f"Waste unit: {WASTE_UNIT_OF_MEASURE}")
print("Controlled data-quality issues: included")
print("========================================")
