
# 5. Create the README

Create:

```text
05_ETL/README.md
````

Use:

````markdown
# Project Atlas — Phase 5: ETL

Phase 5 establishes the reproducible ETL pipeline between the trusted data produced by Phase 4 and the PostgreSQL data warehouse implemented in Phase 6.

## ETL Flow

```text
04_Data_Quality/data/trusted/
            ↓
         Extract
            ↓
     05_ETL/data/raw/
            ↓
         Staging
            ↓
       Transform
            ↓
        Validate
            ↓
       Phase 6 Warehouse
````

## Current Implementation

The first ETL step implements the:

```text
Trusted → Raw
```

boundary.

The extraction process:

* expects all 16 Atlas datasets;
* verifies required source files;
* validates expected row counts;
* copies trusted data into Raw;
* calculates SHA-256 checksums;
* verifies the Raw copy;
* records extraction results in a JSON log.

No business transformation occurs in the Raw layer.

## Source

```text
04_Data_Quality/data/trusted/
```

## Raw Output

```text
05_ETL/data/raw/
```

## Run

From the Project Atlas repository root:

```bash
python3 05_ETL/scripts/extract_data.py
```

## Phase Boundary

Phase 5 prepares and validates data for the warehouse.

It does not yet implement:

* PostgreSQL warehouse tables
* Dimension tables
* Fact tables
* Analytical SQL views
* Power BI
* Tableau

````

---

# 6. Run Step 1

Now execute:

```bash
python3 05_ETL/scripts/extract_data.py
````

You should see approximately:

```text
======================================================================
Project Atlas — Phase 5 ETL — Trusted to Raw
======================================================================

Processing: accounts.csv
Rows: 1,000 | Checksum: PASS | Extraction: PASS

Processing: customers.csv
Rows: 49,509 | Checksum: PASS | Extraction: PASS

...
```

and eventually:

```text
Expected total rows: 1,746,059
Source total rows:   1,746,059
Raw total rows:      1,746,059

======================================================================
ETL EXTRACTION STATUS: SUCCESS
======================================================================
Datasets extracted: 16
Total rows:         1,746,059
...
```

---

# 7. Verify the resulting structure

Run:

```bash
find 05_ETL -maxdepth 3 -type f | sort
```

You should have:

```text
05_ETL/README.md
05_ETL/config/etl_config.py
05_ETL/data/raw/accounts.csv
05_ETL/data/raw/budget.csv
05_ETL/data/raw/customers.csv
05_ETL/data/raw/emissions.csv
05_ETL/data/raw/employees.csv
05_ETL/data/raw/energy.csv
05_ETL/data/raw/financial_transactions.csv
05_ETL/data/raw/inventory.csv
05_ETL/data/raw/locations.csv
05_ETL/data/raw/machines.csv
05_ETL/data/raw/maintenance.csv
05_ETL/data/raw/production.csv
05_ETL/data/raw/products.csv
05_ETL/data/raw/sales.csv
05_ETL/data/raw/suppliers.csv
05_ETL/data/raw/waste.csv
05_ETL/logs/extract_<timestamp>.json
05_ETL/metadata/etl_specification.md
05_ETL/scripts/extract_data.py
```

---
