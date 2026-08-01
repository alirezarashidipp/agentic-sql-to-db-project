# Security

## Trust model

User questions and all model output are untrusted. The application is designed
for local learning with sample data, not for public access or sensitive
employee records.

## Existing controls

1. FastAPI limits question length.
2. Structured model output constrains validation status and SQL shape.
3. `validate_sql()` accepts one comment-free `SELECT` that references the
   configured table.
4. The existing SQLite file is opened with URI `mode=ro` and
   `PRAGMA query_only = ON`.
5. A SQLite authorizer denies reads from other tables and all SQLite write
   actions.
6. `MAX_RESULT_ROWS` caps returned rows.
7. OpenAI requests use `store=False`.
8. `.env.local` and virtual environments are excluded from Git and Docker.
9. Docker runs the application as a non-root user.

Prompt rules are helpful but are not a security boundary. Do not remove the
independent SQL and SQLite controls.

## Secrets

- Store `OPENAI_API_KEY` only in `.env.local` or the deployment secret store.
- Never paste keys into issues, logs, screenshots, prompts, or committed files.
- Revoke a key immediately if it is exposed.
- `.env.example` must contain names and safe defaults only.

## Known gaps

- `/ask` and `/schema` have no authentication.
- There is no rate limiting, usage quota, or cost ceiling.
- OpenAI and SQLite work have no explicit execution timeout.
- There is no request-level audit trail or security monitoring.
- The returned SQL and rows are visible in the frontend debug panel.

Bind to localhost unless a trusted gateway supplies the missing controls.

## Reporting

Do not include secrets or real employee data in a report. For this small
learning repository, open a private report with the repository owner before
publishing a security issue.
