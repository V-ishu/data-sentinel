import hashlib


def hash_row(row: dict) -> str:
    """
    Takes a row (dictionary of column: value pairs) and returns
    a fixed-length MD5 fingerprint of that row's data.

    Any change in any column value will produce a completely different hash.
    This allows fast row-level comparison without needing a primary key.
    """
    # Step 1: Sort columns alphabetically so order is always consistent
    sorted_values = [str(row[col]) for col in sorted(row.keys())]

    # Step 2: Join all values into one string with a separator
    row_string = "|".join(sorted_values)

    # Step 3: Generate MD5 hash of that string
    return hashlib.md5(row_string.encode()).hexdigest()


def get_primary_keys(data: list[dict], pk_column: str) -> dict:
    """
    Extracts primary key values from a list of rows.
    Returns a dict mapping pk_value -> full row for fast lookup.
    """
    return {row[pk_column]: row for row in data}


def get_composite_keys(data: list[dict], key_columns: list[str]) -> dict:
    """
    Extracts composite key values (multiple columns combined) from rows.
    Returns a dict mapping (col1_val, col2_val, ...) -> full row.
    """
    return {
        tuple(str(row[col]) for col in key_columns): row
        for row in data
    }