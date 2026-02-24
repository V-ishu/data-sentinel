from sqlalchemy import create_engine, text, inspect
from sqlalchemy.exc import SQLAlchemyError


class DatabaseConnector:
    """
    Handles connection to a single database.
    Create two instances for source and target comparison.
    """

    def __init__(self, connection_string: str, label: str = "DB"):
        self.connection_string = connection_string
        self.label = label  # "source" or "target" — for clear error messages
        self.engine = None

    def connect(self):
        """Establish and verify database connection."""
        try:
            self.engine = create_engine(self.connection_string)
            with self.engine.connect() as conn:
                conn.execute(text("SELECT 1"))
            print(f"✅ Connected to {self.label} database.")
        except SQLAlchemyError as e:
            raise ConnectionError(f"❌ Failed to connect to {self.label}: {str(e)}")

    def fetch_table(self, table: str, where_clause: str = None) -> list[dict]:
        """
        Fetch all rows from a table.
        Optionally filter with a WHERE clause like: "department = 'Engineering'"
        """
        query = f"SELECT * FROM {table}"
        if where_clause:
            query += f" WHERE {where_clause}"

        try:
            with self.engine.connect() as conn:
                result = conn.execute(text(query))
                columns = list(result.keys())
                rows = result.fetchall()
                return [dict(zip(columns, row)) for row in rows]
        except SQLAlchemyError as e:
            raise RuntimeError(f"❌ Failed to fetch {table} from {self.label}: {str(e)}")

    def get_primary_key(self, table: str):
        """
        Auto-detect the primary key column of a table.
        Returns the PK column name, or None if not found.
        """
        try:
            inspector = inspect(self.engine)
            pk_info = inspector.get_pk_constraint(table)
            pk_columns = pk_info.get("constrained_columns", [])
            return pk_columns[0] if len(pk_columns) == 1 else None
        except Exception:
            return None

    def disconnect(self):
        """Close the database connection."""
        if self.engine:
            self.engine.dispose()
            print(f"🔌 Disconnected from {self.label} database.")