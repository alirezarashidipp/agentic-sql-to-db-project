# Database

## Existing-file contract

`DATABASE_PATH=employees.db` resolves relative to the project root. The tracked
file already contains 100 fictional employees. The application never creates,
migrates, or seeds a database.

At startup, the application:

1. requires `DATABASE_PATH` to point to an existing file;
2. opens SQLite with URI `mode=ro`;
3. verifies that `TABLE_NAME` exists;
4. requires `COLUMN_GUIDE` keys to exactly match the live columns.

Default schema:

| Column | Type | Meaning |
| --- | --- | --- |
| `EMPLOYEE_ID` | `INTEGER PRIMARY KEY` | Unique employee ID |
| `EMPLOYEE_NAME` | `TEXT NOT NULL` | Synthetic employee name |
| `DEPARTMENT` | `TEXT NOT NULL` | `MSW`, `MRM`, or `SECURITY` |
| `STATUS` | `TEXT NOT NULL` | `CODER` or `NON-CODER` |
| `TITLE` | `TEXT NOT NULL` | Official job title |

## Supply another SQLite file

1. Create and populate the file in the external data process.
2. Stop the application.
3. Set `DATABASE_PATH` and `TABLE_NAME` in `.env.local`.
4. Update `COLUMN_GUIDE` to match the selected table's exact columns.
5. Update `EXAMPLE_QUESTIONS` when the dataset changes.
6. Restart the application.

No change is required in `app/database.py`, `app/workflow.py`, the prompt
YAML, or the frontend.

## Change data or columns

The external producer owns all `CREATE TABLE`, `ALTER TABLE`, `INSERT`,
`UPDATE`, and migration work. After replacing or migrating the SQLite file:

1. update `COLUMN_GUIDE` when columns or their meaning changed;
2. keep every guide key identical to its live SQLite column name;
3. restart the application to clear cached schema metadata;
4. run the tests and `python main.py --check` from the active virtual environment.

Never commit real employee or personal data.

## Swap the database engine

The modular boundary supports replacing SQLite files and tables, not replacing
SQLite itself. PostgreSQL or another engine requires a new database adapter,
driver, query-validation rules, and tests.
