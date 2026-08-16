"""
Project Atlas
Phase 3 — Data Generation Configuration

Central configuration for the synthetic source-data generation pipeline.
"""

from pathlib import Path


# ============================================================
# Reproducibility
# ============================================================

SEED = 42


# ============================================================
# Date Range
# ============================================================

START_DATE = "2019-01-01"
END_DATE = "2025-12-31"


# ============================================================
# Project Paths
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parents[2]

RAW_DATA_DIR = PROJECT_ROOT / "data" / "raw"


# ============================================================
# Reference Data Volumes
# ============================================================

N_ACCOUNTS = 1_000
N_CUSTOMERS = 50_000
N_SUPPLIERS = 1_000
N_PRODUCTS = 5_000
N_LOCATIONS = 100
N_EMPLOYEES = 5_000
N_MACHINES = 2_000


# ============================================================
# Business Process Data Volumes
# ============================================================

N_SALES = 500_000
N_PRODUCTION = 200_000
N_MAINTENANCE = 50_000
N_FINANCIAL_TRANSACTIONS = 300_000
N_BUDGET = 20_000
N_ENERGY = 100_000
N_EMISSIONS = 100_000
N_WASTE = 100_000
N_INVENTORY = 500_000


# ============================================================
# Controlled Data Quality Issue Rates
#
# These are generation parameters only.
# Phase 4 will measure the actual resulting quality issues.
# ============================================================

MISSING_RATE = 0.05
DUPLICATE_RATE = 0.02
INVALID_REFERENCE_RATE = 0.01
INVALID_VALUE_RATE = 0.01
OUTLIER_RATE = 0.005


# ============================================================
# Dataset Groups
# ============================================================

REFERENCE_DATASETS = (
    "accounts",
    "customers",
    "suppliers",
    "products",
    "locations",
    "employees",
    "machines",
)

BUSINESS_DATASETS = (
    "sales",
    "production",
    "maintenance",
    "financial_transactions",
    "budget",
    "energy",
    "emissions",
    "waste",
    "inventory",
)

ALL_DATASETS = REFERENCE_DATASETS + BUSINESS_DATASETS
