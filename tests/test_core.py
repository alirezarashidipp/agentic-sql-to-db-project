import os
import sqlite3
import tempfile
import unittest
from contextlib import closing
from pathlib import Path

TEST_DIRECTORY = tempfile.TemporaryDirectory()
TEST_DATABASE = Path(TEST_DIRECTORY.name) / "employees.db"
os.environ.update(
    {
        "OPENAI_MODEL": "test-model",
        "DATABASE_PATH": str(TEST_DATABASE),
        "TABLE_NAME": "employees",
        "MAX_QUESTION_LENGTH": "500",
        "MAX_RESULT_ROWS": "100",
    }
)

from app import database
from app.schema import COLUMN_GUIDE

TEST_ROWS = (
    (1001, "AVA CARTER", "MSW", "CODER", "SOFTWARE ENGINEER"),
    (1002, "LIAM PATEL", "MRM", "NON-CODER", "RECRUITER"),
    (1003, "MIA KIM", "SECURITY", "NON-CODER", "SECURITY ANALYST"),
)


class CoreDatabaseTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        with closing(sqlite3.connect(TEST_DATABASE)) as connection, connection:
            connection.execute("""
                CREATE TABLE employees (
                    EMPLOYEE_ID INTEGER PRIMARY KEY,
                    EMPLOYEE_NAME TEXT NOT NULL,
                    DEPARTMENT TEXT NOT NULL,
                    STATUS TEXT NOT NULL CHECK (STATUS IN ('CODER', 'NON-CODER')),
                    TITLE TEXT NOT NULL
                )
            """)
            connection.executemany(
                "INSERT INTO employees VALUES (?, ?, ?, ?, ?)",
                TEST_ROWS,
            )

    @classmethod
    def tearDownClass(cls):
        database.table_schema.cache_clear()
        database.describe_table.cache_clear()
        TEST_DIRECTORY.cleanup()

    def test_existing_database_is_loaded_without_changes(self):
        rows = database.execute_sql(
            'SELECT COUNT(*) AS total FROM "employees"'
        )
        self.assertEqual(rows[0]["total"], len(TEST_ROWS))
        self.assertEqual(
            [column["name"] for column in database.table_schema()],
            list(COLUMN_GUIDE),
        )

    def test_missing_database_is_not_created(self):
        original_path = database.DB_PATH
        missing_path = Path(TEST_DIRECTORY.name) / "missing.db"
        database.DB_PATH = missing_path
        database.table_schema.cache_clear()
        try:
            with self.assertRaisesRegex(ValueError, "does not exist"):
                database.table_schema()
            self.assertFalse(missing_path.exists())
        finally:
            database.DB_PATH = original_path
            database.table_schema.cache_clear()

    def test_sql_validation_rejects_unsafe_queries(self):
        unsafe_queries = (
            "DELETE FROM employees",
            "SELECT * FROM another_table",
            "SELECT * FROM employees; DELETE FROM employees",
            "SELECT * FROM employees -- ignore safeguards",
        )
        for query in unsafe_queries:
            with self.subTest(query=query), self.assertRaises(ValueError):
                database.validate_sql(query)

    def test_sqlite_authorizer_denies_other_tables(self):
        query = (
            "SELECT EMPLOYEE_ID, EMPLOYEE_NAME, DEPARTMENT, STATUS, TITLE "
            "FROM employees UNION ALL SELECT 0, name, '', '', '' "
            "FROM sqlite_master"
        )
        with self.assertRaises(sqlite3.DatabaseError):
            database.execute_sql(query)

    def test_result_limit_is_enforced(self):
        original_limit = database.MAX_RESULT_ROWS
        database.MAX_RESULT_ROWS = 2
        try:
            rows = database.execute_sql(
                "SELECT * FROM employees ORDER BY EMPLOYEE_ID"
            )
        finally:
            database.MAX_RESULT_ROWS = original_limit
        self.assertEqual(len(rows), 2)


if __name__ == "__main__":
    unittest.main()
