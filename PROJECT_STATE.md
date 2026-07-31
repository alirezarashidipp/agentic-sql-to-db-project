# Project State

Last updated: 2026-07-31

## Status

The learning-focused MVP is runnable locally and through Docker. A user can ask
about one configured SQLite table, receive validation or clarification, inspect
the generated SQL, and get an answer grounded in the database result.

## Working capabilities

- FastAPI serves the web UI and JSON API.
- LangGraph routes valid, incomplete, and invalid questions.
- OpenAI structured output validates questions and generates SQL.
- YAML files hold all LLM prompt text.
- SQLite schema introspection is combined with `COLUMN_GUIDE`.
- SQL has application validation, query-only mode, and table-scoped
  authorization.
- The frontend renders columns and examples from `GET /schema`.
- The frontend offers native Bar/Pie views after compatible two-column results.
- Standard-library tests cover database guardrails and chart eligibility.
- Docker Compose runs the app with a persistent SQLite volume.
- GitHub Actions is configured to run deterministic checks without calling
  OpenAI.

## Current data contract

- Database asset: `employees.db`
- Table: `employees`
- Columns: `EMPLOYEE_ID`, `DEPARTMENT`, `STATUS`, `TITLE`
- Seed rows: 10 sample employees

`employees.db` is intentionally tracked because it contains demo data only.
Container deployments create and seed a separate database in their volume.

## Deliberate limits

- One SQLite table is exposed at a time.
- There is no migration system; schema changes require database recreation or
  an externally managed database.
- Each request is independent; there is no conversation memory.
- Charts require 2-20 rows with one unique text-label column and one numeric
  column whose values are non-negative and not all zero. Pie requires 2-8
  strictly positive values.
- Valid questions make three model calls; incomplete or invalid questions make
  one.
- There are no automated LLM accuracy evaluations yet.

## Not production-ready

- No authentication or authorization
- No rate limiting or usage quotas
- No OpenAI or SQLite execution timeout
- No retry or operational tracing

Do not expose the service publicly until these controls match the deployment
environment.

## Next useful work

1. Add a small golden evaluation set for question classification and SQL
   results.
2. Add request IDs, safe logging, and upstream timeouts.
3. Add authentication and rate limits only when a real deployment requires
   public or shared access.
