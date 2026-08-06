# Database

## Existing-file contract

`DATABASE_PATH=main_datawarehouse.db` resolves relative to the project root. The tracked
file already contains 100 fictional employees. The application never creates,
migrates, or seeds a database. The exposed table name is fixed as `data` in
`app/schema.py`; it is not an environment setting.

At startup, the application:

1. requires `DATABASE_PATH` to point to an existing file;
2. opens SQLite with URI `mode=ro`;
3. verifies that the `data` table exists;
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

For a flat CSV, the standalone `csv_to_sqlite.py` tool can act as the external
data producer. It uses only Python's standard library and is never imported by
the application:

```powershell
.\.venv\Scripts\python.exe csv_to_sqlite.py `
  .\input.csv `
  .\main_datawarehouse.db `
  --infer-types `
  --replace
```

The tool creates one flat table. It does not infer primary keys, indexes,
relationships, or `NOT NULL` constraints. It refuses an existing output by
default; `--replace` atomically replaces the complete database after a
successful conversion. Stop the app before replacing its configured file.
`main.py --check` validates the database selected in `.env.local`; deterministic
unit tests intentionally continue to use the sample database from `.env.example`
unless the project's default dataset is deliberately changed.

1. Create and populate the file in the external data process.
2. Stop the application.
3. Ensure its table is named `data` and set `DATABASE_PATH` in `.env.local`.
4. Update `COLUMN_GUIDE` to match `data`'s exact columns.
5. Update `EXAMPLE_QUESTIONS` and `EVAL_CASES` when the dataset changes.
6. Restart the application.

No change is required in `app/database.py`, `app/workflow.py`, the prompt
YAML, or the frontend.

## Change data or columns

The external producer owns all `CREATE TABLE`, `ALTER TABLE`, `INSERT`,
`UPDATE`, and migration work. After replacing or migrating the SQLite file:

1. update `COLUMN_GUIDE` and the schema-specific `EVAL_CASES` when columns or
   their meaning changed;
2. keep every guide key identical to its live SQLite column name;
3. restart the application to clear cached schema metadata;
4. run the deterministic tests and `python main.py --check` from the active
   virtual environment;
5. run the opt-in DeepEval suite when an OpenAI key is available.

Never commit real employee or personal data.

## Swap the database engine

The modular boundary supports replacing SQLite files that expose `data`, not
replacing SQLite itself. PostgreSQL or another engine requires a new adapter,
driver, query-validation rules, and tests.
