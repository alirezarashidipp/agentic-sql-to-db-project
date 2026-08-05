# Employee SQL Assistant

Ask a question in plain English, turn it into guarded SQLite, and return an
answer grounded in the query result.

This learning project keeps the full path visible: FastAPI receives the
question, LangGraph validates and completes it, OpenAI produces structured
output, SQLite runs a read-only query, and a small HTML/CSS/JavaScript frontend
shows the result.

## What it does

1. Checks whether a question is valid, incomplete, or outside the table scope.
2. Normalizes clear spelling mistakes and shorthand using the live schema.
3. Generates one SQLite `SELECT` query.
4. Applies application and SQLite-level read-only guardrails.
5. Answers from the returned rows only.
6. Offers Bar or Pie views only when the returned rows have a compatible shape.

Try questions such as:

- `How many coders?`
- `How many employees are in each department?`
- `Data engineers in MRM`
- `How many?` — asks for the missing detail instead of guessing.

## Quick start

Requirements:

- Python 3.14 with `pip`
- An OpenAI API key

```powershell
# Use Python available on that computer:
& "D:\path\to\python.exe" -m venv .venv

.\.venv\Scripts\python.exe -m pip install -r requirements.txt
Copy-Item .env.example .env.local
# Add the API key to .env.local
.\.venv\Scripts\python.exe main.py
```

Open <http://127.0.0.1:8000>. Interactive API documentation is available at
<http://127.0.0.1:8000/docs>.

## Docker

Create `.env.local` as shown above, then run:

```powershell
docker compose up --build
```

Open <http://127.0.0.1:8000>. The image includes the existing fictional
`employees.db` asset and opens it read-only. `.env.local` is supplied only at
runtime.

## Configuration

All runtime settings are required and live in `.env.local`:

| Setting | Purpose | Example |
| --- | --- | --- |
| `OPENAI_API_KEY` | OpenAI authentication | Keep secret |
| `OPENAI_MODEL` | Model used by OpenAI-backed workflow nodes | `gpt-5.6-sol` |
| `DATABASE_PATH` | SQLite file, relative to the project or absolute | `employees.db` |
| `TABLE_NAME` | Single table exposed to the assistant | `employees` |
| `MAX_QUESTION_LENGTH` | API input limit | `500` |
| `MAX_RESULT_ROWS` | Maximum rows returned from SQLite | `100` |

## Request flow

```text
question
  -> load live schema and COLUMN_GUIDE
  -> validate / normalize question
       -> incomplete or invalid: return a short explanation
       -> valid: generate SELECT
  -> validate SQL
  -> run read-only SQLite query
  -> generate grounded answer
  -> inspect returned rows in the browser
       -> compatible two-column result: offer valid Bar / Pie views
```

Prompts live in `prompts/*.yml`; table-specific column descriptions live in
`app/schema.py`. The frontend discovers the configured table through
`GET /schema`, so it does not hardcode employee columns.

## Safety boundary

Generated SQL is untrusted. The backend accepts a single `SELECT` against the
configured table, enables `PRAGMA query_only`, and installs a SQLite authorizer
that denies other tables and write operations. These layers must remain in
place even when prompts improve.

This is still a learning/local application: `/ask` has no authentication, rate
limiting, or query timeout. Do not expose it directly to the public internet.
See [docs/security.md](docs/security.md) for the threat model.

## Project map

```text
.
|-- app/                    # FastAPI, LangGraph, config, and SQLite code
|-- prompts/                # Versioned prompt templates
|-- evals/                  # Opt-in live LLM evaluations
|-- static/                 # HTML, CSS, and JavaScript frontend
|-- tests/                  # Standard-library regression tests
|-- docs/                   # Architecture, API, database, deployment, security
|   `-- adr/                # Architecture decision records
|-- skills/                 # Project-local AI maintenance skill
|-- workflows/              # Human-readable AI workflow contract
|-- .github/workflows/      # Continuous integration
|-- AGENTS.md               # Rules for coding agents
|-- PROJECT_STATE.md        # Current capabilities and limits
|-- Dockerfile
|-- docker-compose.yml
|-- Makefile
|-- main.py
|-- requirements.txt       # Pinned direct Python dependencies
|-- requirements-eval.txt  # Optional DeepEval dependencies
`-- employees.db            # Tracked prebuilt sample data asset
```

Directories for migrations, benchmarks, memory, or scripts are intentionally
absent until the project has real code that belongs in them.

## Change the data

To use another SQLite asset:

1. Create and populate the SQLite file in your separate data process.
2. Set `DATABASE_PATH` and `TABLE_NAME` in `.env.local`.
3. Update `COLUMN_GUIDE`, `EXAMPLE_QUESTIONS`, and `EVAL_CASES` in
   `app/schema.py`.
4. Make every `COLUMN_GUIDE` key exactly match a live table column.
5. Restart the app.

The application never creates, migrates, or seeds the database. See
[docs/database.md](docs/database.md) for the existing-file contract.

## Verify changes

```powershell
.\.venv\Scripts\python.exe -m unittest discover -s tests -v
.\.venv\Scripts\python.exe main.py --check
node --check static/app.js
node --test tests/test_chart.cjs
```

## Run the live LLM evaluations

The eval suite calls OpenAI and is intentionally separate from the deterministic
tests and CI. It reuses `OPENAI_API_KEY` and `OPENAI_MODEL` from `.env.local`;
DeepEval uses `OPENAI_MODEL_NAME` when set, or `gpt-4.1` as the judge model.

```powershell
.\.venv\Scripts\python.exe -m pip install -r requirements-eval.txt
$env:PYTHONUTF8 = "1"
.\.venv\Scripts\deepeval.exe test run evals\test_llm.py -v
```

`EVAL_CASES` contains four SQL-result cases, four rejected-question cases, and
two final-answer cases. Update these goldens whenever the configured table or
column meanings change. SQL and routing use exact assertions; DeepEval judges
answer correctness, relevance, and grounding.

## Documentation

- [Architecture](docs/architecture.md)
- [API](docs/api.md)
- [Database and data imports](docs/database.md)
- [Deployment](docs/deployment.md)
- [Security](docs/security.md)
- [Architecture decisions](docs/adr/0001-schema-guided-read-only-sql.md)
- [Contributing](CONTRIBUTING.md)
- [Current project state](PROJECT_STATE.md)
