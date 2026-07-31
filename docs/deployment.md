# Deployment

## Local development

```powershell
Copy-Item .env.example .env.local
# Add OPENAI_API_KEY to .env.local
uv sync --locked
uv run python main.py
```

`main.py` starts Uvicorn on `127.0.0.1:8000` with reload enabled. This entry
point is for local development only.

## Docker Compose

```powershell
docker compose up --build
```

Compose:

- binds the app to `127.0.0.1:8000`;
- reads secrets at runtime from `.env.local`;
- overrides `DATABASE_PATH` with `/data/employees.db`;
- persists SQLite in the `sqlite_data` volume.

Stop the app with:

```powershell
docker compose down
```

Add `--volumes` only when you intentionally want to delete the container
database.

## Standalone Docker

```powershell
docker build -t employee-sql-assistant .
docker run --rm --env-file .env.local -e DATABASE_PATH=/data/employees.db -p 127.0.0.1:8000:8000 employee-sql-assistant
```

Mount a writable volume at `/data` when data must survive container removal.

## Production boundary

The image runs Uvicorn as a non-root user, but the application is not ready for
an untrusted public network. Add authentication, rate limiting, request
timeouts, safe operational logging, and TLS at the deployment edge first.

Back up the SQLite volume before upgrades that change `app/schema.py`. There is
no migration system.
