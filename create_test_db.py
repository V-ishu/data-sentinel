import sqlite3

# ── SOURCE DATABASE ──
source = sqlite3.connect('source.db')
cursor = source.cursor()

cursor.execute('''
    CREATE TABLE IF NOT EXISTS employees (
        id INTEGER PRIMARY KEY,
        name TEXT,
        department TEXT,
        salary INTEGER
    )
''')

cursor.executemany("INSERT INTO employees VALUES (?, ?, ?, ?)", [
    (1, 'Alice',   'Engineering', 50000),
    (2, 'Bob',     'Engineering', 60000),
    (3, 'Charlie', 'HR',          55000),
    (4, 'Diana',   'Finance',     70000),
    (5, 'Eve',     'Engineering', 65000),
])

source.commit()
source.close()
print("✅ Source database created.")

# ── TARGET DATABASE (with intentional differences) ──
target = sqlite3.connect('target.db')
cursor = target.cursor()

cursor.execute('''
    CREATE TABLE IF NOT EXISTS employees (
        id INTEGER PRIMARY KEY,
        name TEXT,
        department TEXT,
        salary INTEGER
    )
''')

cursor.executemany("INSERT INTO employees VALUES (?, ?, ?, ?)", [
    (1, 'Alice',   'Engineering', 55000),  # salary changed
    (2, 'Bob',     'Engineering', 60000),  # identical
    (3, 'Charlie', 'Marketing',   55000),  # department changed
                                           # id 4 Diana is missing
    (5, 'Eve',     'Engineering', 65000),  # identical
    (6, 'Frank',   'Finance',     72000),  # extra row not in source
])

target.commit()
target.close()
print("✅ Target database created with intentional differences.")
print("\nDifferences introduced:")
print("  • id=1 Alice: salary changed 50000 → 55000")
print("  • id=3 Charlie: department changed HR → Marketing")
print("  • id=4 Diana: missing in target")
print("  • id=6 Frank: extra row in target, not in source")