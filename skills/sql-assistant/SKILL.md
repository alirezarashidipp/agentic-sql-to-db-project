---
name: sql-assistant-maintenance
description: Safely maintain this FastAPI, LangGraph, and SQLite schema-guided SQL application.
---

# SQL Assistant Maintenance

Use this skill when changing the dataset, prompt behavior, workflow, API, or SQL
guardrails.

1. Read `AGENTS.md`, `PROJECT_STATE.md`, and the relevant document in `docs/`.
2. Trace the affected request path before editing.
3. Keep prompt text in `prompts/*.yml` and column meaning in `app/schema.py`.
4. Preserve SQL validation, query-only mode, and the SQLite authorizer.
5. Treat SQLite as externally provisioned. For a column change, update the
   database and `COLUMN_GUIDE`; never create, migrate, or seed it in the app.
6. Add or update the smallest deterministic regression test.
7. Run:

   ```powershell
   python -m unittest discover -s tests -v
   python main.py --check
   node --check static/app.js
   ```

8. Update `PROJECT_STATE.md` and the relevant documentation when behavior or
   limits change.

Never include secrets or real employee data.
