# Contributing

## Setup

```powershell
Copy-Item .env.example .env.local
uv sync --locked
```

Add your own `OPENAI_API_KEY` only to `.env.local`.

## Before opening a pull request

```powershell
uv run python -m unittest discover -s tests -v
uv run python main.py --check
node --check static/app.js
node --test tests/test_chart.cjs
```

Keep changes focused and update the matching document when behavior changes.
Do not add dependencies when the standard library or an existing dependency is
enough.

## Dataset changes

A column change must update these values in `app/schema.py`:

1. `TABLE_DDL`
2. `SEED_SQL`
3. `SEED_ROWS`
4. `COLUMN_GUIDE`

Recreate `employees.db`, verify it contains sample data only, and update
`EXAMPLE_QUESTIONS` when user-facing examples change.

## Security changes

Treat model output as untrusted. Changes to SQL validation or execution need a
regression test and must preserve the independent SQLite authorizer layer.
