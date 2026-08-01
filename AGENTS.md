# Agent Instructions

Keep this project small, understandable, and safe for learning.

## Read first

- `README.md` for setup and scope.
- `PROJECT_STATE.md` for current capabilities and known limits.
- `docs/architecture.md` for the request flow.
- `docs/security.md` before changing SQL execution.

## Invariants

- Prompts belong in `prompts/*.yml`, not Python strings.
- Dataset-specific column meaning and examples belong in `app/schema.py`.
- `COLUMN_GUIDE` keys must exactly match the configured SQLite columns.
- The SQLite file is provisioned outside this application; never create,
  migrate, or seed it from runtime code.
- A column change must update the external database and `COLUMN_GUIDE`, then
  restart the application.
- Do not weaken `validate_sql`, `PRAGMA query_only`, or the SQLite authorizer.
- Keep SQL limited to the configured table and cap returned rows.
- Keep the frontend dependency-free unless a real requirement demands more.
- Never commit `.env.local`, API keys, virtual environments, or real employee
  data. `employees.db` is intentionally tracked as a prebuilt sample asset.
- Do not add empty directories or abstractions for future work.

## Commands

```powershell
python -m pip install -r requirements.txt
python main.py
python -m unittest discover -s tests -v
python main.py --check
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
