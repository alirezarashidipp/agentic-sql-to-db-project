# Employee SQL Assistant

A learning-focused FastAPI project that uses LangGraph to validate an employee
question, complete safe shorthand, query SQLite, and generate a grounded answer.

## Run

```powershell
Copy-Item .env.example .env.local
# Add your OPENAI_API_KEY to .env.local
uv sync
uv run python main.py
```

Open <http://127.0.0.1:8000>.

The app reads `OPENAI_API_KEY` from `.env.local` and creates `employees.db`
with sample employees on first run.

## Configuration

Runtime settings live in `.env.local`:

```dotenv
OPENAI_MODEL=gpt-5.6-sol
DATABASE_PATH=employees.db
TABLE_NAME=employees
MAX_QUESTION_LENGTH=500
MAX_RESULT_ROWS=100
```

`DATABASE_PATH` may be workspace-relative or absolute. `TABLE_NAME` must be a
simple SQLite identifier containing letters, numbers, or underscores.

## Workflow

```text
START
  -> load_schema
  -> review_question
       | valid
       v
     generate_sql -> run_sql -> generate_answer -> END
       |
       + incomplete or invalid ---------------------> END
```

The review node combines the real SQLite types with the `COLUMN_GUIDE` data
dictionary in `app/schema.py`. That dictionary explains every column and its
possible values, so validation can fix unambiguous spelling or shorthand, ask a
clarification for incomplete questions, and reject unsupported requests.

## Structure

```text
.
|-- app/
|   |-- api.py        # FastAPI routes
|   |-- config.py     # environment-driven runtime settings
|   |-- database.py   # generic SQLite access and safe queries
|   |-- prompts.py    # cached YAML prompt loader
|   |-- schema.py     # DDL, seed rows, data dictionary, examples
|   `-- workflow.py   # LangGraph state, nodes, and edges
|-- prompts/
|   |-- question_review.yml
|   |-- sql_generation.yml
|   `-- answer.yml
|-- static/
|   |-- index.html
|   |-- style.css
|   `-- app.js
|-- main.py           # local entry point and self-check
|-- employees.db
`-- .env.local
```

## Import or update employee data

This learning version does not automatically import CSV or JSON files. Demo
rows are defined by `SEED_ROWS` in `app/schema.py`.

### Add new employees

1. Add one tuple per employee to `SEED_ROWS` in `app/schema.py`:

   ```python
   (1011, "MSW", "CODER", "SOFTWARE ENGINEER"),
   ```

2. If the row introduces a new department, status, or title, update its
   `possible_values` in `app/schema.py`.
3. Restart the application. `INSERT OR IGNORE` adds rows with new
   `EMPLOYEE_ID` values without duplicating existing employees.

`EMPLOYEE_ID` is the primary key. Changing a tuple that uses an ID already in
`employees.db` will not update that row because `INSERT OR IGNORE` preserves the
existing record.

### Replace or correct existing data

For a clean replacement:

1. Stop the application.
2. Rename the configured SQLite file to keep it as a backup.
3. Replace `SEED_ROWS` in `app/schema.py`.
4. Update `COLUMN_GUIDE` in the same file.
5. Start the application. A new database will be created and seeded.

### Use another SQLite data asset

To point the application at an existing SQLite file:

1. Set `DATABASE_PATH` and `TABLE_NAME` in `.env.local`.
2. In `app/schema.py`, update `COLUMN_GUIDE` so its keys exactly match the
   selected table's columns.
3. Update `EXAMPLE_QUESTIONS`.
4. Set `SEED_ROWS = ()` when the external database should not receive demo
   rows. `TABLE_DDL` may be empty when the table already exists.
5. Restart the application.

No changes are required in `database.py`, `workflow.py`, the YAML prompts, or
the frontend. The `/schema` endpoint introspects the configured SQLite table,
and the frontend renders its columns automatically.

### Add or change a column

Update all of these:

| Change | File |
| --- | --- |
| SQLite column and constraints | `TABLE_DDL` in `app/schema.py` |
| Seed insert columns | `SEED_SQL` in `app/schema.py` |
| Value in every seed row | `SEED_ROWS` in `app/schema.py` |
| Meaning and possible values | `COLUMN_GUIDE` in `app/schema.py` |

Then recreate the configured SQLite file, because this project intentionally
does not include a migration system.

The YAML prompts normally need no data-value changes: the live column
dictionary replaces `{{schema}}` at runtime. Edit files in `prompts/` only when
the validation, SQL-generation, or answer behavior itself should change.

This modularity swaps SQLite files and tables. Replacing SQLite with another
database engine such as PostgreSQL still requires a new database adapter and
driver.

Run the local check without calling OpenAI:

```powershell
uv run python main.py --check
```
