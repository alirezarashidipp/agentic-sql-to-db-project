# Database

## Default asset

`DATABASE_PATH=employees.db` resolves relative to the project root. The tracked
file contains sample data only. On startup, `initialize_database()` creates the
configured table when needed and inserts missing seed IDs with
`INSERT OR IGNORE`.

Default schema:

| Column | Type | Meaning |
| --- | --- | --- |
| `EMPLOYEE_ID` | `INTEGER PRIMARY KEY` | Unique employee ID |
| `DEPARTMENT` | `TEXT NOT NULL` | `MSW`, `MRM`, or `SECURITY` in demo data |
| `STATUS` | `TEXT NOT NULL` | `CODER` or `NON-CODER` |
| `TITLE` | `TEXT NOT NULL` | Official job title |

`COLUMN_GUIDE` supplies descriptions and possible values to both validation and
the frontend. Its keys must exactly match the live SQLite columns or startup
fails.

## Add sample rows

Add tuples to `SEED_ROWS` in `app/schema.py`. New `EMPLOYEE_ID` values are
inserted on the next startup. Editing an existing ID does not update its row
because `INSERT OR IGNORE` preserves the current record.

## Replace existing sample data

1. Stop the application.
2. Back up `employees.db`.
3. Update `SEED_ROWS` and `COLUMN_GUIDE`.
4. Remove or rename the old database.
5. Restart to create and seed a new database.
6. Run the tests and inspect the new database before committing it.

Never commit real employee or personal data.

## Use another SQLite file

1. Set `DATABASE_PATH` and `TABLE_NAME` in `.env.local`.
2. Set `COLUMN_GUIDE` keys to the selected table's exact columns.
3. Update `EXAMPLE_QUESTIONS`.
4. Set `SEED_ROWS = ()` if the external database must not receive demo data.
5. Leave `TABLE_DDL` empty if the table is externally managed.
6. Restart the application.

No change is required in `app/database.py`, `app/workflow.py`, the prompt YAML,
or the frontend.

## Change columns

Update all four schema assets:

| Change | Location in `app/schema.py` |
| --- | --- |
| SQLite columns and constraints | `TABLE_DDL` |
| Insert columns | `SEED_SQL` |
| Values in every sample row | `SEED_ROWS` |
| Descriptions and allowed values | `COLUMN_GUIDE` |

Then recreate or externally migrate the SQLite file. This project intentionally
has no migration framework.

## Swap the database engine

The modular boundary supports replacing SQLite files and tables, not replacing
SQLite itself. PostgreSQL or another engine requires a new database adapter,
driver, query validation rules, and tests.
