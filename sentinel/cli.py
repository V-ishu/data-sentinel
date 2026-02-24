import click
from sentinel.connector import DatabaseConnector
from sentinel.comparator import Comparator
from sentinel.reporter import Reporter


@click.group()
def cli():
    """
    🛡️  data-sentinel — Two-database comparison and validation framework.
    Detects missing rows, column mismatches, and data drift across SQL databases.
    """
    pass


@cli.command()
@click.option("--source-db", required=True, help="Source database connection string")
@click.option("--target-db", required=True, help="Target database connection string")
@click.option("--table", required=True, help="Table name to compare")
@click.option("--pk", default=None, help="Primary key column (optional — auto-detected if not provided)")
@click.option("--composite-keys", default=None, help="Comma-separated composite key columns e.g. 'col1,col2'")
@click.option("--where", default=None, help="Optional WHERE clause filter e.g. \"department = 'Engineering'\"")
@click.option("--save-report", is_flag=True, help="Save full results to report.json")
def compare(source_db, target_db, table, pk, composite_keys, where, save_report):
    """Compare a table across two databases and report differences."""

    # Step 1: Connect to both databases
    source_conn = DatabaseConnector(source_db, label="source")
    target_conn = DatabaseConnector(target_db, label="target")

    try:
        source_conn.connect()
        target_conn.connect()
    except ConnectionError as e:
        click.echo(str(e))
        return

    # Step 2: Auto-detect primary key if not provided
    if not pk and not composite_keys:
        pk = source_conn.get_primary_key(table)
        if pk:
            print(f"🔍 Auto-detected primary key: '{pk}'")
        else:
            print("⚠️  No primary key detected. Falling back to MD5 row hash comparison.")

    # Step 3: Fetch data from both databases
    try:
        print(f"\n📥 Fetching data from source...")
        source_data = source_conn.fetch_table(table, where_clause=where)
        print(f"📥 Fetching data from target...")
        target_data = target_conn.fetch_table(table, where_clause=where)
    except RuntimeError as e:
        click.echo(str(e))
        return
    finally:
        source_conn.disconnect()
        target_conn.disconnect()

    print(f"\n✅ Source rows fetched: {len(source_data)}")
    print(f"✅ Target rows fetched: {len(target_data)}")

    # Step 4: Parse composite keys if provided
    composite_key_list = None
    if composite_keys:
        composite_key_list = [k.strip() for k in composite_keys.split(",")]

    # Step 5: Run comparison
    print(f"\n🔄 Running comparison...\n")
    comparator = Comparator(
        source_data=source_data,
        target_data=target_data,
        pk_column=pk,
        composite_keys=composite_key_list
    )
    results = comparator.compare()

    # Step 6: Report
    reporter = Reporter(results, table_name=table)
    reporter.print_summary()

    if save_report:
        reporter.save_json()


if __name__ == "__main__":
    cli()