import re
import sqlite3
from contextlib import closing
from functools import cache

from .config import DB_PATH, MAX_RESULT_ROWS, TABLE_NAME
from .schema import COLUMN_GUIDE

TABLE_REFERENCE = re.compile(
    rf'(?is)\bFROM\s+(?:"{re.escape(TABLE_NAME)}"|{re.escape(TABLE_NAME)})(?=\s|$)'
)


def _connect_readonly() -> sqlite3.Connection:
    if not DB_PATH.is_file():
        raise ValueError(f"Database file does not exist: {DB_PATH}")
    return sqlite3.connect(f"{DB_PATH.as_uri()}?mode=ro", uri=True)


@cache
def table_schema() -> list[dict]:
    with closing(_connect_readonly()) as connection:
        columns = connection.execute(
            f'PRAGMA table_info("{TABLE_NAME}")'
        ).fetchall()

    if not columns:
        raise ValueError(f"Table {TABLE_NAME!r} does not exist in {DB_PATH.name}.")

    names = {column[1] for column in columns}
    if names != set(COLUMN_GUIDE):
        missing = names - set(COLUMN_GUIDE)
        extra = set(COLUMN_GUIDE) - names
        raise ValueError(
            f"COLUMN_GUIDE does not match {TABLE_NAME!r}. "
            f"Missing guides: {sorted(missing)}; extra guides: {sorted(extra)}."
        )

    schema = []
    for _, name, data_type, required, _, primary_key in columns:
        constraints = (
            f"{' PRIMARY KEY' if primary_key else ''}"
            f"{' NOT NULL' if required else ''}"
        )
        schema.append(
            {
                "name": name,
                "type": f"{data_type}{constraints}",
                **COLUMN_GUIDE[name],
            }
        )
    return schema


@cache
def describe_table() -> str:
    lines = [
        f"- {column['name']} ({column['type']}): {column['description']} "
        f"Possible values: {column['possible_values']}"
        for column in table_schema()
    ]
    return f'Table: "{TABLE_NAME}"\nColumn dictionary:\n' + "\n".join(lines)


def validate_sql(sql: str) -> str:
    sql = sql.strip()
    if (
        not re.match(r"(?is)^SELECT\b", sql)
        or ";" in sql
        or "--" in sql
        or "/*" in sql
        or not TABLE_REFERENCE.search(sql)
    ):
        raise ValueError(f"Only one SELECT query on {TABLE_NAME!r} is allowed.")
    return sql


def execute_sql(sql: str) -> list[dict]:
    sql = validate_sql(sql)
    with closing(_connect_readonly()) as connection:
        connection.row_factory = sqlite3.Row
        connection.execute("PRAGMA query_only = ON")

        def authorize(action, table, _column, _database, _source):
            if action == sqlite3.SQLITE_READ:
                return sqlite3.SQLITE_OK if table == TABLE_NAME else sqlite3.SQLITE_DENY
            if action in (sqlite3.SQLITE_SELECT, sqlite3.SQLITE_FUNCTION):
                return sqlite3.SQLITE_OK
            return sqlite3.SQLITE_DENY

        connection.set_authorizer(authorize)
        return [
            dict(row)
            for row in connection.execute(sql).fetchmany(MAX_RESULT_ROWS)
        ]
