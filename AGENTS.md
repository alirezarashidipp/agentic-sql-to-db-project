# Agent Instructions

Keep this project small, understandable, and safe for learning.

## Read first

- `README.md` for setup and scope.
- `PROJECT_STATE.md` for current capabilities and known limits.
- `docs/architecture.md` for the request flow.
- `docs/security.md` before changing SQL execution.

## Invariants

- Prompts belong in `prompts/*.yml`, not Python strings.
- Dataset-specific definitions belong in `app/schema.py`.
- `COLUMN_GUIDE` keys must exactly match the configured SQLite columns.
- A column change must update `TABLE_DDL`, `SEED_SQL`, `SEED_ROWS`, and
  `COLUMN_GUIDE`; recreate the database when its schema changes.
- Do not weaken `validate_sql`, `PRAGMA query_only`, or the SQLite authorizer.
- Keep SQL limited to the configured table and cap returned rows.
- Keep the frontend dependency-free unless a real requirement demands more.
- Never commit `.env.local`, API keys, virtual environments, or real employee
  data. `employees.db` is intentionally tracked as sample-only data.
- Do not add empty directories or abstractions for future work.

## Commands

```powershell
uv sync --locked
uv run python main.py
uv run python -m unittest discover -s tests -v
uv run python main.py --check
node --check static/app.js
node --test tests/test_chart.cjs
docker compose config --quiet
```

## Definition of done

- The smallest relevant tests and self-check pass.
- Prompt behavior changes include a prompt version update.
- API, database, deployment, or security changes update the matching document.
- `PROJECT_STATE.md` reflects any new capability or limitation.
- No secret or unrelated user file is staged.
