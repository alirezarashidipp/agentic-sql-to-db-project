import os
import sqlite3
import tempfile
import unittest
from pathlib import Path

TEST_DIRECTORY = tempfile.TemporaryDirectory()
os.environ.update(
    {
        "OPENAI_MODEL": "test-model",
        "DATABASE_PATH": str(Path(TEST_DIRECTORY.name) / "employees.db"),
        "TABLE_NAME": "employees",
        "MAX_QUESTION_LENGTH": "500",
        "MAX_RESULT_ROWS": "100",
    }
)

from app import database
from app.schema import COLUMN_GUIDE, SEED_ROWS


class CoreDatabaseTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        database.initialize_database()

    @classmethod
    def tearDownClass(cls):
        database.table_schema.cache_clear()
        database.describe_table.cache_clear()
        TEST_DIRECTORY.cleanup()

    def test_database_setup_is_idempotent(self):
        database.initialize_database()
        rows = database.execute_sql(
            'SELECT COUNT(*) AS total FROM "employees"'
        )
        self.assertEqual(rows[0]["total"], len(SEED_ROWS))
        self.assertEqual(
            [column["name"] for column in database.table_schema()],
            list(COLUMN_GUIDE),
        )

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
            "SELECT EMPLOYEE_ID, DEPARTMENT, STATUS, TITLE FROM employees "
            "UNION ALL SELECT 0, name, '', '' FROM sqlite_master"
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
