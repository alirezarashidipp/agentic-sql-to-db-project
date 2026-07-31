---
name: sql-assistant-maintenance
description: Safely maintain this schema-guided FastAPI, LangGraph, and SQLite learning project.
---

# SQL Assistant Maintenance

Use this skill when changing the dataset, prompt behavior, workflow, API, or SQL
guardrails.

1. Read `AGENTS.md`, `PROJECT_STATE.md`, and the relevant document in `docs/`.
2. Trace the affected request path before editing.
3. Keep prompt text in `prompts/*.yml` and dataset knowledge in `app/schema.py`.
4. Preserve SQL validation, query-only mode, and the SQLite authorizer.
5. For a column change, update `TABLE_DDL`, `SEED_SQL`, `SEED_ROWS`, and
   `COLUMN_GUIDE`, then recreate the sample database.
6. Add or update the smallest deterministic regression test.
7. Run:

   ```powershell
   uv run python -m unittest discover -s tests -v
   uv run python main.py --check
   node --check static/app.js
   ```

8. Update `PROJECT_STATE.md` and the relevant documentation when behavior or
   limits change.

Never include secrets or real employee data.
