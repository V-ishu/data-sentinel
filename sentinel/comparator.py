from sentinel.utils import hash_row, get_primary_keys, get_composite_keys


class Comparator:
    """
    Compares data from two databases using a three-strategy fallback:
    1. Primary Key comparison
    2. Composite Key comparison
    3. MD5 Row Hash comparison (no key needed)
    """

    def __init__(self, source_data: list[dict], target_data: list[dict], pk_column: str = None, composite_keys: list[str] = None):
        self.source_data = source_data
        self.target_data = target_data
        self.pk_column = pk_column
        self.composite_keys = composite_keys
        self.results = {
            "strategy_used": None,
            "total_source_rows": len(source_data),
            "total_target_rows": len(target_data),
            "missing_in_target": [],
            "missing_in_source": [],
            "mismatched_rows": []
        }

    def compare(self) -> dict:
        """
        Entry point. Decides which strategy to use and runs it.
        """
        if self.pk_column:
            print(f"🔑 Strategy: Primary Key comparison on column '{self.pk_column}'")
            self.results["strategy_used"] = "Primary Key"
            return self._compare_by_key(
                get_primary_keys(self.source_data, self.pk_column),
                get_primary_keys(self.target_data, self.pk_column),
                key_label=self.pk_column
            )

        elif self.composite_keys:
            print(f"🔑 Strategy: Composite Key comparison on columns {self.composite_keys}")
            self.results["strategy_used"] = "Composite Key"
            return self._compare_by_key(
                get_composite_keys(self.source_data, self.composite_keys),
                get_composite_keys(self.target_data, self.composite_keys),
                key_label=str(self.composite_keys)
            )

        else:
            print("🔑 Strategy: MD5 Row Hash comparison (no key found)")
            self.results["strategy_used"] = "MD5 Row Hash"
            return self._compare_by_hash()

    def _compare_by_key(self, source_map: dict, target_map: dict, key_label: str) -> dict:
        """
        Compares two tables using a key (primary or composite).

        source_map and target_map are dicts of: key_value -> full_row
        """
        source_keys = set(source_map.keys())
        target_keys = set(target_map.keys())

        # Find missing rows using set operations
        missing_in_target = source_keys - target_keys
        missing_in_source = target_keys - source_keys
        common_keys = source_keys & target_keys

        # Store missing rows
        for key in missing_in_target:
            self.results["missing_in_target"].append({
                "key": str(key),
                "key_column": key_label,
                "row": source_map[key]
            })

        for key in missing_in_source:
            self.results["missing_in_source"].append({
                "key": str(key),
                "key_column": key_label,
                "row": target_map[key]
            })

        # For common keys, compare every column
        for key in common_keys:
            source_row = source_map[key]
            target_row = target_map[key]
            mismatches = self._find_column_mismatches(source_row, target_row)
            if mismatches:
                self.results["mismatched_rows"].append({
                    "key": str(key),
                    "key_column": key_label,
                    "mismatches": mismatches
                })

        return self.results

    def _compare_by_hash(self) -> dict:
        """
        Compares two tables using MD5 hashing when no key is available.
        Hashes every row and compares fingerprints.
        """
        source_hashes = {hash_row(row): row for row in self.source_data}
        target_hashes = {hash_row(row): row for row in self.target_data}

        source_keys = set(source_hashes.keys())
        target_keys = set(target_hashes.keys())

        # Rows in source but not in target
        for h in source_keys - target_keys:
            self.results["missing_in_target"].append({
                "key": h[:8] + "...",  # show first 8 chars of hash
                "key_column": "MD5 Hash",
                "row": source_hashes[h]
            })

        # Rows in target but not in source
        for h in target_keys - source_keys:
            self.results["missing_in_source"].append({
                "key": h[:8] + "...",
                "key_column": "MD5 Hash",
                "row": target_hashes[h]
            })

        return self.results

    def _find_column_mismatches(self, source_row: dict, target_row: dict) -> list[dict]:
        """
        Compares two rows column by column.
        Returns list of columns that have different values.
        """
        mismatches = []
        for col in source_row:
            if str(source_row[col]) != str(target_row.get(col)):
                mismatches.append({
                    "column": col,
                    "source_value": source_row[col],
                    "target_value": target_row.get(col)
                })
        return mismatches