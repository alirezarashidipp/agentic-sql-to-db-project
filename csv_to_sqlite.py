"""Convert one CSV file into a standalone SQLite database."""

import argparse
import csv
import math
import os
import re
import sqlite3
import tempfile
from contextlib import closing
from pathlib import Path

TABLE_NAME = re.compile(r"[A-Za-z_][A-Za-z0-9_]*\Z")
INTEGER = re.compile(r"[+-]?(?:0|[1-9][0-9]*)\Z")
NUMBER = re.compile(
    r"[+-]?(?:(?:0|[1-9][0-9]*)(?:\.[0-9]*)?|\.[0-9]+)"
    r"(?:[eE][+-]?[0-9]+)?\Z"
)
SQLITE_INTEGER_MIN = -(2**63)
SQLITE_INTEGER_MAX = 2**63 - 1


def _quote_identifier(value: str) -> str:
    return '"' + value.replace('"', '""') + '"'


def _is_real(value: str) -> bool:
    if not NUMBER.fullmatch(value):
        return False
    try:
        return math.isfinite(float(value))
    except ValueError:
        return False


def _infer_type(values: list[str]) -> str:
    populated = [value.strip() for value in values if value.strip()]
    if not populated:
        return "TEXT"
    if all(INTEGER.fullmatch(value) for value in populated):
        integers = [int(value) for value in populated]
        if all(
            SQLITE_INTEGER_MIN <= value <= SQLITE_INTEGER_MAX
            for value in integers
        ):
            return "INTEGER"
        return "TEXT"
    if all(_is_real(value) for value in populated):
        return "REAL"
    return "TEXT"


def _coerce(value: str, data_type: str):
    stripped = value.strip()
    if not stripped:
        return None
    if data_type == "INTEGER":
        return int(stripped)
    if data_type == "REAL":
        return float(stripped)
    return value


def convert_csv(
    csv_path: Path,
    database_path: Path,
    table: str,
    *,
    delimiter: str = ",",
    encoding: str = "utf-8-sig",
    infer_types: bool = False,
    replace: bool = False,
) -> tuple[int, dict[str, str]]:
    """Create a SQLite file and return its row count and inferred schema."""
    csv_path = Path(csv_path)
    database_path = Path(database_path)

    if not TABLE_NAME.fullmatch(table):
        raise ValueError(
            "Table name must use only letters, numbers, and underscores."
        )
    if len(delimiter) != 1 or delimiter in "\r\n":
        raise ValueError("Delimiter must be one non-newline character.")
    if not csv_path.is_file():
        raise FileNotFoundError(f"CSV file does not exist: {csv_path}")
    if csv_path.resolve() == database_path.resolve():
        raise ValueError("CSV input and SQLite output must be different files.")
    if not database_path.parent.is_dir():
        raise FileNotFoundError(
            f"Output directory does not exist: {database_path.parent}"
        )
    if database_path.is_symlink():
        raise ValueError("Refusing to replace a symbolic-link database path.")
    if database_path.exists() and not database_path.is_file():
        raise ValueError(f"Output path is not a file: {database_path}")
    if database_path.exists() and not replace:
        raise FileExistsError(
            f"Database already exists: {database_path}. "
            "Use --replace to overwrite it."
        )

    with csv_path.open("r", encoding=encoding, newline="") as source:
        reader = csv.reader(source, delimiter=delimiter, strict=True)
        try:
            headers = [name.strip() for name in next(reader)]
        except StopIteration as error:
            raise ValueError("CSV file is empty.") from error

        if not headers or any(not name or "\x00" in name for name in headers):
            raise ValueError("Every CSV column needs a non-empty header.")
        if len({name.casefold() for name in headers}) != len(headers):
            raise ValueError("CSV column names must be unique.")

        # ponytail: one in-memory pass keeps type inference simple; use a two-pass
        # stream only when CSV files become too large to fit comfortably in memory.
        rows = []
        for line_number, row in enumerate(reader, start=2):
            if len(row) != len(headers):
                raise ValueError(
                    f"CSV row {line_number} has {len(row)} values; "
                    f"expected {len(headers)}."
                )
            rows.append(row)

    types = [
        _infer_type([row[index] for row in rows]) if infer_types else "TEXT"
        for index in range(len(headers))
    ]
    converted_rows = [
        tuple(_coerce(value, types[index]) for index, value in enumerate(row))
        for row in rows
    ]

    descriptor, temporary_name = tempfile.mkstemp(
        prefix=f".{database_path.name}.",
        suffix=".tmp",
        dir=database_path.parent,
    )
    os.close(descriptor)
    temporary_path = Path(temporary_name)

    try:
        definitions = ", ".join(
            f"{_quote_identifier(name)} {data_type}"
            for name, data_type in zip(headers, types)
        )
        columns = ", ".join(_quote_identifier(name) for name in headers)
        placeholders = ", ".join("?" for _ in headers)

        with closing(sqlite3.connect(temporary_path)) as connection:
            with connection:
                connection.execute(
                    f"CREATE TABLE {_quote_identifier(table)} ({definitions})"
                )
                if converted_rows:
                    connection.executemany(
                        f"INSERT INTO {_quote_identifier(table)} "
                        f"({columns}) VALUES ({placeholders})",
                        converted_rows,
                    )

        if database_path.exists() and not replace:
            raise FileExistsError(
                f"Database appeared during import: {database_path}"
            )
        os.replace(temporary_path, database_path)
    finally:
        temporary_path.unlink(missing_ok=True)

    return len(rows), dict(zip(headers, types))


def _parse_delimiter(value: str) -> str:
    if value.lower() == "tab":
        return "\t"
    if len(value) != 1 or value in "\r\n":
        raise argparse.ArgumentTypeError("Use one character, or 'tab'.")
    return value


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Convert one CSV file into a SQLite database."
    )
    parser.add_argument("csv_file", type=Path)
    parser.add_argument("database_file", type=Path)
    parser.add_argument("--table", required=True)
    parser.add_argument("--delimiter", type=_parse_delimiter, default=",")
    parser.add_argument("--encoding", default="utf-8-sig")
    parser.add_argument(
        "--infer-types",
        action="store_true",
        help=(
            "Infer clear INTEGER and REAL columns; otherwise keep all "
            "columns as TEXT."
        ),
    )
    parser.add_argument(
        "--replace",
        action="store_true",
        help="Replace the output database only after conversion succeeds.",
    )
    args = parser.parse_args()

    try:
        row_count, schema = convert_csv(
            args.csv_file,
            args.database_file,
            args.table,
            delimiter=args.delimiter,
            encoding=args.encoding,
            infer_types=args.infer_types,
            replace=args.replace,
        )
    except (csv.Error, OSError, sqlite3.Error, UnicodeError, ValueError) as error:
        parser.exit(1, f"error: {error}\n")

    columns = ", ".join(f"{name} {data_type}" for name, data_type in schema.items())
    print(
        f"Wrote {row_count} rows to {args.database_file} "
        f"in table {args.table!r}."
    )
    print(f"Columns: {columns}")


if __name__ == "__main__":
    main()
