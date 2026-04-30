"""
Create two demo SQLite databases (source.db + target.db) with an 'employees' table. Plants intentional differences so you can
immediately test data-sentinel comparison logic via the API.

Usage:
    python scripts/seed_demo.py
"""

import os
import sqlite3

SOURCE_DB = "source.db"
TARGET_DB = "target.db"

def setup_db(path: str, rows: list[tuple]) -> None:
    if os.path.exists(path):
        os.remove(path)

    conn = sqlite3.connect(path)
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE employees (
            id INTEGER PRIMARY KEY,
            name TEXT,
            department TEXT,
            salary INTEGER
        )
    """)
    cur.executemany("INSERT INTO employees VALUES (?, ?, ?, ?)", rows)
    conn.commit()
    conn.close()

source_rows = [
    (1, "Alice", "Engineering", 120000),
    (2, "Bob", "Marketing", 90000),
    (3, "Charlie", "HR", 70000),
    (4, "David", "Engineering", 110000),
    (5, "Eve", "Marketing", 95000),
]

target_rows = [
    (1, "Alice", "Engineering", 120000),  # Match
    (2, "Bob", "Marketing", 85000),      # Salary mismatch
    (3, "Charlie", "HR", 70000),         # Match
    # David missing in target
    (5, "Eve", "Marketing", 95000),      # Match
    (6, "Frank", "Sales", 80000),       # Extra row in target
]

setup_db(SOURCE_DB, source_rows)
setup_db(TARGET_DB, target_rows)

print(f"Created {SOURCE_DB} ({len(source_rows)} rows)"
      f"and {TARGET_DB} ({len(target_rows)} rows)")
print()

print("Expected differences when comparing 'employees' table:")
print(" - Missing in target: David (id=4)")
print(" - Salary mismatch: Bob (id=2)")
print(" - Extra in target: Frank (id=6)")