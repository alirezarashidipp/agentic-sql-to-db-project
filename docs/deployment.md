# Deployment

## Local development

```powershell
Copy-Item .env.example .env.local
# Add OPENAI_API_KEY to .env.local
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python main.py
```

When `python` is not on `PATH`, use the full path to `python.exe` to create
`.venv`; commands after activation use the virtual environment automatically.

`main.py` starts Uvicorn on `127.0.0.1:8000` with reload enabled. This entry
point is for local development only.

## Docker Compose

```powershell
docker compose up --build
```

Compose:

- binds the app to `127.0.0.1:8000`;
- reads secrets at runtime from `.env.local`;
- uses the prebuilt fictional `main_datawarehouse.db` included in the image;
- opens SQLite read-only and never creates or seeds it.

Stop the app with:

```powershell
docker compose down
```

## Standalone Docker

```powershell
docker build -t employee-sql-assistant .
docker run --rm --env-file .env.local -p 127.0.0.1:8000:8000 employee-sql-assistant
```

The image already contains `/app/main_datawarehouse.db` for the demo.

The container listens on the `PORT` environment variable supplied by the
hosting platform. When `PORT` is not set, it defaults to `8000` for local
Docker runs.

For another externally produced database containing a table named `data`, mount
the file read-only and point `DATABASE_PATH` at its container location:

```powershell
$database = (Resolve-Path "C:\path\external.db").Path
docker run --rm --env-file .env.local -e DATABASE_PATH=/data/external.db --mount "type=bind,source=$database,target=/data/external.db,readonly" -p 127.0.0.1:8000:8000 employee-sql-assistant
```

## Production boundary

The image runs Uvicorn as a non-root user, but the application is not ready for
an untrusted public network. Add authentication, rate limiting, request
timeouts, safe operational logging, and TLS at the deployment edge first.

Back up the externally managed SQLite file before schema or data migrations.
The application has no migration system and never modifies that file.
