from pathlib import Path


# ============================================================
# Project Atlas — Phase 5 ETL Configuration
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parents[2]

# Phase 4 trusted data — authoritative Phase 5 source
TRUSTED_DATA_DIR = (
    PROJECT_ROOT
    / "04_Data_Quality"
    / "data"
    / "trusted"
)

# Phase 5 Raw layer
RAW_DATA_DIR = (
    PROJECT_ROOT
    / "05_ETL"
    / "data"
    / "raw"
)

# Phase 5 logs
LOG_DIR = (
    PROJECT_ROOT
    / "05_ETL"
    / "logs"
)


# ============================================================
# Expected Atlas datasets
# ============================================================

EXPECTED_DATASETS = [
    "accounts",
    "customers",
    "products",
    "suppliers",
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


# ============================================================
# Phase 4 trusted-data row-count contract
#
# These values were established during the Phase 5
# input schema audit.
# ============================================================

EXPECTED_ROW_COUNTS = {
    "accounts": 1_000,
    "customers": 49_509,
    "products": 4_951,
    "suppliers": 1_000,
    "locations": 100,
    "employees": 4_913,
    "machines": 1_959,
    "sales": 466_046,
    "production": 181_438,
    "maintenance": 46_180,
    "financial_transactions": 293_285,
    "budget": 19_445,
    "energy": 97_747,
    "emissions": 97_337,
    "waste": 97_982,
    "inventory": 479_167,
}


EXPECTED_TOTAL_ROWS = sum(EXPECTED_ROW_COUNTS.values())