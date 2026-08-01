# Contributing

## Setup

```powershell
Copy-Item .env.example .env.local
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
```

Add your own `OPENAI_API_KEY` only to `.env.local`.

## Before opening a pull request

```powershell
python -m unittest discover -s tests -v
python main.py --check
node --check static/app.js
node --test tests/test_chart.cjs
```

Keep changes focused and update the matching document when behavior changes.
Do not add dependencies when the standard library or an existing dependency is
enough.

## Dataset changes

Create or update the SQLite file outside this application. For a column change,
update the external table and make `COLUMN_GUIDE` match its columns exactly.
Verify `employees.db` contains sample data only, update `EXAMPLE_QUESTIONS`
when needed, and restart the application after replacing the file.

## Security changes

Treat model output as untrusted. Changes to SQL validation or execution need a
regression test and must preserve the independent SQLite authorizer layer.
