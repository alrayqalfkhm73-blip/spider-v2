"""Database Package"""
from database.connection import get_db, Database
from database.schema import create_all, create_tables, create_indexes, table_exists, column_exists, reset_for_test
from database.migrations import apply_all, add_missing_columns

db = get_db()
__all__ = ["get_db", "Database", "db", "create_all", "create_tables",
           "create_indexes", "apply_all", "add_missing_columns",
           "table_exists", "column_exists", "reset_for_test"]
