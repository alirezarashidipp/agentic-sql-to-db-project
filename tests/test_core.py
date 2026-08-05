import json
import os
import shutil
import sqlite3
import tempfile
import unittest
from contextlib import closing
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import Mock, patch

ROOT = Path(__file__).resolve().parent.parent
DEFAULT_ENV = {}
for line in (ROOT / ".env.example").read_text(encoding="utf-8").splitlines():
    key, separator, value = line.partition("=")
    if separator and key and not key.lstrip().startswith("#"):
        DEFAULT_ENV[key.strip()] = value.strip()

SOURCE_DATABASE = Path(DEFAULT_ENV["DATABASE_PATH"])
if not SOURCE_DATABASE.is_absolute():
    SOURCE_DATABASE = ROOT / SOURCE_DATABASE

TEST_DIRECTORY = tempfile.TemporaryDirectory()
TEST_DATABASE = Path(TEST_DIRECTORY.name) / SOURCE_DATABASE.name
shutil.copyfile(SOURCE_DATABASE, TEST_DATABASE)
os.environ.update(
    {
        "OPENAI_API_KEY": "test-key",
        "OPENAI_MODEL": "test-model",
        "DATABASE_PATH": str(TEST_DATABASE),
        "TABLE_NAME": DEFAULT_ENV["TABLE_NAME"],
        "MAX_QUESTION_LENGTH": DEFAULT_ENV["MAX_QUESTION_LENGTH"],
        "MAX_RESULT_ROWS": DEFAULT_ENV["MAX_RESULT_ROWS"],
    }
)

from app import api, database, workflow
from app.config import MAX_QUESTION_LENGTH, STATIC_DIR, TABLE_NAME
from app.schema import COLUMN_GUIDE


def tearDownModule():
    database.table_schema.cache_clear()
    database.describe_table.cache_clear()
    TEST_DIRECTORY.cleanup()


def _row_values(row):
    return tuple(
        sorted((type(value).__name__, repr(value)) for value in row.values())
    )


def rows_equal(actual, expected, mode):
    if mode == "scalar":
        return (
            len(actual) == len(expected) == 1
            and len(actual[0]) == len(expected[0]) == 1
            and next(iter(actual[0].values()))
            == next(iter(expected[0].values()))
        )

    if mode == "ordered":
        return list(map(_row_values, actual)) == list(map(_row_values, expected))

    if mode == "unordered":
        return sorted(map(_row_values, actual)) == sorted(map(_row_values, expected))

    if mode == "grouped":
        # ponytail: grouped results assume one text label and one numeric value;
        # add explicit label/value keys if numeric group labels become a real case.
        def grouped(rows):
            result = {}
            for row in rows:
                values = list(row.values())
                numbers = [
                    value
                    for value in values
                    if isinstance(value, (int, float)) and not isinstance(value, bool)
                ]
                labels = [value for value in values if value not in numbers]
                if len(values) != 2 or len(numbers) != 1 or len(labels) != 1:
                    return None
                try:
                    if labels[0] in result:
                        return None
                    result[labels[0]] = numbers[0]
                except TypeError:
                    return None
            return result

        actual_groups = grouped(actual)
        return actual_groups is not None and actual_groups == grouped(expected)

    raise ValueError(f"Unknown comparison mode: {mode}")


class CoreDatabaseTests(unittest.TestCase):
    def test_existing_database_matches_column_guide(self):
        rows = database.execute_sql(
            f'SELECT COUNT(*) AS total FROM "{TABLE_NAME}"'
        )
        self.assertGreaterEqual(rows[0]["total"], 0)
        self.assertEqual(
            {column["name"] for column in database.table_schema()},
            set(COLUMN_GUIDE),
        )

    def test_missing_database_is_not_created(self):
        missing_path = Path(TEST_DIRECTORY.name) / "missing.db"
        database.table_schema.cache_clear()
        self.addCleanup(database.table_schema.cache_clear)
        with patch.object(database, "DB_PATH", missing_path):
            with self.assertRaisesRegex(ValueError, "does not exist"):
                database.table_schema()
            self.assertFalse(missing_path.exists())

    def test_sql_validation_rejects_unsafe_queries(self):
        unsafe_queries = (
            f'DELETE FROM "{TABLE_NAME}"',
            f'SELECT * FROM "{TABLE_NAME}_other"',
            f'SELECT * FROM "{TABLE_NAME}"; DELETE FROM "{TABLE_NAME}"',
            f'SELECT * FROM "{TABLE_NAME}" -- ignore safeguards',
        )
        for query in unsafe_queries:
            with self.subTest(query=query), self.assertRaises(ValueError):
                database.validate_sql(query)

        valid = f'SELECT COUNT(*) FROM "{TABLE_NAME}"'
        self.assertEqual(database.validate_sql(valid), valid)

    def test_query_must_really_read_the_configured_table(self):
        with self.assertRaisesRegex(ValueError, "must read"):
            database.execute_sql(f"SELECT 'FROM {TABLE_NAME} ' AS fake")

    def test_database_file_is_readonly(self):
        with closing(database._connect_readonly()) as connection:
            with self.assertRaises(sqlite3.OperationalError):
                connection.execute(f'DELETE FROM "{TABLE_NAME}"')

    def test_sqlite_authorizer_denies_other_tables(self):
        query = (
            f'SELECT sqlite_master.name FROM "{TABLE_NAME}" '
            "CROSS JOIN sqlite_master"
        )
        with self.assertRaises(sqlite3.DatabaseError):
            database.execute_sql(query)

    def test_result_limit_is_enforced(self):
        total = database.execute_sql(
            f'SELECT COUNT(*) AS total FROM "{TABLE_NAME}"'
        )[0]["total"]
        if total < 2:
            self.skipTest("The configured sample table has fewer than two rows.")

        with patch.object(database, "MAX_RESULT_ROWS", 2):
            rows = database.execute_sql(f'SELECT * FROM "{TABLE_NAME}"')
        self.assertEqual(len(rows), 2)


class ContractTests(unittest.TestCase):
    def test_schema_endpoint_returns_runtime_columns(self):
        columns = [
            {
                "name": "RUNTIME_COLUMN",
                "type": "TEXT",
                "description": "Runtime description.",
                "possible_values": "Any.",
            }
        ]
        with (
            patch.object(api, "TABLE_NAME", "runtime_table"),
            patch.object(api, "table_schema", return_value=columns),
            patch.object(api, "EXAMPLE_QUESTIONS", ("Runtime example?",)),
        ):
            payload = json.loads(json.dumps(api.schema()))

        self.assertEqual(
            payload,
            {
                "table": "runtime_table",
                "columns": columns,
                "examples": ["Runtime example?"],
                "max_question_length": MAX_QUESTION_LENGTH,
            },
        )

    def test_ask_endpoint_keeps_one_json_contract_for_every_status(self):
        cases = (
            (
                {
                    "status": "valid",
                    "normalized_question": "Normalized question",
                    "answer": "One row.",
                    "sql": "SELECT 1",
                    "rows": [{"total": 1}],
                },
                "Normalized question",
                "SELECT 1",
                [{"total": 1}],
            ),
            ({"status": "incomplete", "answer": "Add details."}, "Show data", None, []),
            ({"status": "invalid", "answer": "Out of scope."}, "Show data", None, []),
        )

        for graph_result, normalized, sql, rows in cases:
            with self.subTest(status=graph_result["status"]), patch.object(
                api.question_graph, "invoke", return_value=graph_result
            ):
                payload = json.loads(
                    json.dumps(api.ask(api.QuestionRequest(question="Show data")))
                )

                self.assertEqual(
                    set(payload),
                    {
                        "question",
                        "normalized_question",
                        "status",
                        "answer",
                        "sql",
                        "rows",
                    },
                )
                self.assertEqual(payload["normalized_question"], normalized)
                self.assertEqual(payload["sql"], sql)
                self.assertEqual(payload["rows"], rows)

    def test_frontend_consumes_schema_instead_of_hardcoding_columns(self):
        script = (STATIC_DIR / "app.js").read_text(encoding="utf-8")
        html = (STATIC_DIR / "index.html").read_text(encoding="utf-8")

        for token in (
            'fetch("/schema")',
            "data.columns.forEach",
            "column.name",
            "column.description",
            "column.possible_values",
            "data.table",
            "data.examples",
            "data.max_question_length",
        ):
            self.assertIn(token, script)
        self.assertRegex(
            html,
            r'(?s)<div\s+id=["\']schema-fields["\'][^>]*>\s*</div>',
        )


class WorkflowTests(unittest.TestCase):
    @staticmethod
    def _client(*parsed, answer="Answer."):
        responses = Mock()
        responses.parse.side_effect = [
            SimpleNamespace(output_parsed=value) for value in parsed
        ]
        responses.create.return_value = SimpleNamespace(output_text=answer)
        return SimpleNamespace(responses=responses)

    def test_valid_question_routes_through_sql_and_answer(self):
        sql = f'SELECT COUNT(*) AS total FROM "{TABLE_NAME}"'
        client = self._client(
            workflow.QuestionReview(
                status="valid",
                normalized_question="Normalized question",
                message="",
            ),
            workflow.SqlQuery(sql=f" {sql} "),
            answer="One row.",
        )

        with (
            patch.object(workflow, "describe_table", return_value="schema"),
            patch.object(workflow, "get_openai_client", return_value=client),
            patch.object(
                workflow, "execute_sql", return_value=[{"total": 1}]
            ) as execute_sql,
        ):
            result = workflow.question_graph.invoke({"question": "Question"})

        self.assertEqual(result["status"], "valid")
        self.assertEqual(result["sql"], sql)
        self.assertEqual(result["rows"], [{"total": 1}])
        self.assertEqual(result["answer"], "One row.")
        self.assertEqual(client.responses.parse.call_count, 2)
        client.responses.create.assert_called_once()
        execute_sql.assert_called_once_with(sql)

    def test_non_valid_questions_never_execute_sql(self):
        for status in ("incomplete", "invalid"):
            with self.subTest(status=status):
                client = self._client(
                    workflow.QuestionReview(
                        status=status,
                        normalized_question="Normalized question",
                        message="Stop.",
                    )
                )
                with (
                    patch.object(workflow, "describe_table", return_value="schema"),
                    patch.object(
                        workflow, "get_openai_client", return_value=client
                    ),
                    patch.object(workflow, "execute_sql") as execute_sql,
                ):
                    result = workflow.question_graph.invoke(
                        {"question": "Question"}
                    )

                self.assertEqual(result["status"], status)
                self.assertEqual(result["answer"], "Stop.")
                self.assertEqual(client.responses.parse.call_count, 1)
                client.responses.create.assert_not_called()
                execute_sql.assert_not_called()

    def test_generated_sql_executes_through_the_real_guardrails(self):
        sql = f'SELECT COUNT(*) AS total FROM "{TABLE_NAME}"'
        client = self._client(workflow.SqlQuery(sql=sql))
        with patch.object(workflow, "get_openai_client", return_value=client):
            result = workflow.query_database(
                {
                    "schema": database.describe_table(),
                    "normalized_question": "How many rows?",
                }
            )

        expected = database.execute_sql(sql)
        self.assertTrue(rows_equal(result["rows"], expected, "scalar"))

    def test_answer_model_receives_the_question_sql_and_rows(self):
        client = self._client(answer="Seven.")
        state = {
            "normalized_question": "How many rows?",
            "sql": f'SELECT COUNT(*) AS total FROM "{TABLE_NAME}"',
            "rows": [{"total": 7}],
        }
        with patch.object(workflow, "get_openai_client", return_value=client):
            result = workflow.generate_answer(state)

        request = client.responses.create.call_args.kwargs
        self.assertEqual(json.loads(request["input"]), {
            "question": state["normalized_question"],
            "sql": state["sql"],
            "rows": state["rows"],
        })
        self.assertIn("using only the supplied SQLite result", request["instructions"])
        self.assertFalse(request["store"])
        self.assertEqual(result["answer"], "Seven.")


class ResultComparisonTests(unittest.TestCase):
    def test_supported_result_comparison_modes(self):
        self.assertTrue(rows_equal([{"TOTAL": 2}], [{"count": 2}], "scalar"))
        self.assertTrue(
            rows_equal(
                [{"name": "B", "count": 2}, {"name": "A", "count": 1}],
                [{"label": "A", "value": 1}, {"label": "B", "value": 2}],
                "grouped",
            )
        )
        actual = [{"name": "B"}, {"name": "A"}]
        expected = [{"label": "A"}, {"label": "B"}]
        self.assertTrue(rows_equal(actual, expected, "unordered"))
        self.assertFalse(rows_equal(actual, expected, "ordered"))
        self.assertTrue(rows_equal(list(reversed(actual)), expected, "ordered"))

        with self.assertRaises(ValueError):
            rows_equal([], [], "unknown")


if __name__ == "__main__":
    unittest.main()
