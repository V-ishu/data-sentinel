# 🛡️ data-sentinel

A Python-based two-database comparison framework for detecting data drift, missing rows, and column-level mismatches across SQL databases.

Built for data migration validation, release pipeline integrity checks, and environment consistency verification.

---

## Why data-sentinel?

When migrating data between environments, how do you know the migration was successful?

Manually checking rows across two databases is error-prone and doesn't scale. data-sentinel automates this — connecting to both databases, comparing every row and column, and producing a clear report of exactly what's different.

---

## How It Works

data-sentinel uses a **three-strategy comparison engine** with automatic fallback:

| Strategy | When Used |
|---|---|
| **Primary Key** | Table has a single primary key — auto-detected |
| **Composite Key** | No single PK — user specifies multiple columns as key |
| **MD5 Row Hash** | No key available — each row is hashed and fingerprints are compared |

For every row that exists in both databases, all columns are compared to detect mismatches.

---

## Installation
```bash
git clone https://github.com/V-ishu/data-sentinel.git
cd data-sentinel
pip install -r requirements.txt
```

---

## Usage

### Basic comparison (primary key auto-detected)
```bash
python -m sentinel.cli compare \
  --source-db "sqlite:///source.db" \
  --target-db "sqlite:///target.db" \
  --table "employees"
```

### With a WHERE clause filter
```bash
python -m sentinel.cli compare \
  --source-db "sqlite:///source.db" \
  --target-db "sqlite:///target.db" \
  --table "employees" \
  --where "department = 'Engineering'"
```

### With composite keys
```bash
python -m sentinel.cli compare \
  --source-db "sqlite:///source.db" \
  --target-db "sqlite:///target.db" \
  --table "orders" \
  --composite-keys "customer_id,product_id"
```

### Save full report to JSON
```bash
python -m sentinel.cli compare \
  --source-db "sqlite:///source.db" \
  --target-db "sqlite:///target.db" \
  --table "employees" \
  --save-report
```

---

## Sample Output
```
✅ Connected to source database.
✅ Connected to target database.
🔍 Auto-detected primary key: 'id'
🔑 Strategy: Primary Key comparison on column 'id'

📊 data-sentinel Report — 2026-02-24 14:31:04
📋 Table: employees
╭──────────────────────┬─────────╮
│ Check                │   Count │
├──────────────────────┼─────────┤
│ Total rows in source │       5 │
│ Total rows in target │       5 │
│ Missing in target    │       1 │
│ Missing in source    │       1 │
│ Mismatched rows      │       2 │
╰──────────────────────┴─────────╯

⚠️  Column Mismatches:
  Key: 1 (column: id)
    • salary: '50000' → '55000'
  Key: 3 (column: id)
    • department: 'HR' → 'Marketing'

❌ Missing in Target:
  Key: 4 → {'id': 4, 'name': 'Diana', 'department': 'Finance', 'salary': 70000}

➕ Missing in Source:
  Key: 6 → {'id': 6, 'name': 'Frank', 'department': 'Finance', 'salary': 72000}

❌ 4 issue(s) found across both databases.
```

---

## Supported Databases

Any SQLAlchemy-compatible database:
- SQLite
- PostgreSQL
- MySQL
- Oracle

---

## Project Structure
```
data-sentinel/
├── sentinel/
│   ├── cli.py          # CLI entry point (Click)
│   ├── connector.py    # Database connection handler
│   ├── comparator.py   # Three-strategy comparison engine
│   ├── reporter.py     # Terminal + JSON report generation
│   └── utils.py        # MD5 hashing and key extraction
├── requirements.txt
└── README.md
```

---

## Tech Stack

- **Python 3.10+**
- **SQLAlchemy** — database-agnostic connections
- **Click** — CLI interface
- **Tabulate** — terminal report formatting
- **hashlib** — MD5 row hashing (built-in)