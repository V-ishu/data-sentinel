from tabulate import tabulate
import json
from datetime import datetime


class Reporter:
    """
    Takes comparison results and outputs them in readable formats.
    Supports: terminal summary table + detailed JSON report.
    """

    def __init__(self, results: dict, table_name: str):
        self.results = results
        self.table_name = table_name
        self.timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    def print_summary(self):
        """Print a clean summary table in the terminal."""
        print(f"\n📊 data-sentinel Report — {self.timestamp}")
        print(f"📋 Table: {self.table_name}")
        print(f"🔑 Strategy Used: {self.results['strategy_used']}")
        print("-" * 60)

        summary = [
            ["Total rows in source", self.results["total_source_rows"]],
            ["Total rows in target", self.results["total_target_rows"]],
            ["Missing in target", len(self.results["missing_in_target"])],
            ["Missing in source", len(self.results["missing_in_source"])],
            ["Mismatched rows", len(self.results["mismatched_rows"])],
        ]
        print(tabulate(summary, headers=["Check", "Count"], tablefmt="rounded_outline"))
        print("-" * 60)

        # Print mismatch details (capped at 200 like your Amdocs tool)
        if self.results["mismatched_rows"]:
            print(f"\n⚠️  Column Mismatches (showing up to 200):")
            shown = self.results["mismatched_rows"][:200]
            for row in shown:
                print(f"\n  Key: {row['key']} (column: {row['key_column']})")
                for m in row["mismatches"]:
                    print(f"    • {m['column']}: '{m['source_value']}' → '{m['target_value']}'")

        if self.results["missing_in_target"]:
            print(f"\n❌ Missing in Target (showing up to 200):")
            for row in self.results["missing_in_target"][:200]:
                print(f"  Key: {row['key']} → {row['row']}")

        if self.results["missing_in_source"]:
            print(f"\n➕ Missing in Source (showing up to 200):")
            for row in self.results["missing_in_source"][:200]:
                print(f"  Key: {row['key']} → {row['row']}")

        # Final verdict
        total_issues = (
            len(self.results["missing_in_target"]) +
            len(self.results["missing_in_source"]) +
            len(self.results["mismatched_rows"])
        )
        print("\n" + "-" * 60)
        if total_issues == 0:
            print("✅ Tables are identical. No differences found.")
        else:
            print(f"❌ {total_issues} issue(s) found across both databases.")
        print("-" * 60 + "\n")

    def save_json(self, filepath: str = "report.json"):
        """Save full results to a JSON file."""
        output = {
            "generated_at": self.timestamp,
            "table": self.table_name,
            "strategy_used": self.results["strategy_used"],
            "summary": {
                "total_source_rows": self.results["total_source_rows"],
                "total_target_rows": self.results["total_target_rows"],
                "missing_in_target": len(self.results["missing_in_target"]),
                "missing_in_source": len(self.results["missing_in_source"]),
                "mismatched_rows": len(self.results["mismatched_rows"])
            },
            "details": {
                "missing_in_target": self.results["missing_in_target"][:200],
                "missing_in_source": self.results["missing_in_source"][:200],
                "mismatched_rows": self.results["mismatched_rows"][:200]
            }
        }
        with open(filepath, "w") as f:
            json.dump(output, f, indent=4)
        print(f"💾 Report saved to {filepath}")