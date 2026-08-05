# Project State

Last updated: 2026-08-05

## Status

The learning-focused MVP is runnable locally and through Docker. A user can ask
about one configured SQLite table, receive validation or clarification, inspect
the generated SQL, and get an answer grounded in the database result.

## Working capabilities

- FastAPI serves the web UI and JSON API.
- A three-node LangGraph routes valid, incomplete, and invalid questions.
- OpenAI structured output validates questions and generates SQL.
- YAML files hold all LLM prompt text.
- A pre-provisioned SQLite file is opened read-only and introspected with
  `COLUMN_GUIDE`.
- SQL has application validation, query-only mode, and table-scoped
  authorization.
- The frontend renders columns and examples from `GET /schema`.
- The frontend offers a persisted light/dark appearance toggle.
- The frontend offers native Bar/Pie views after compatible two-column results.
- Standard-library tests cover API/schema contracts, workflow routing,
  database guardrails, result comparison, answer inputs, and chart eligibility.
- An opt-in DeepEval suite measures live question classification, generated SQL
  result equivalence, and final-answer correctness and grounding.
- Python dependencies install with standard `pip` into a local `.venv`.
- Docker and Compose include the existing fictional SQLite asset.
- GitHub Actions is configured to run deterministic checks without calling
  OpenAI.

## Current data contract

- Database asset: `employees.db`
- Table: `employees`
- Columns: `EMPLOYEE_ID`, `EMPLOYEE_NAME`, `DEPARTMENT`, `STATUS`, `TITLE`
- Rows: 100 fictional sample employees

`employees.db` is intentionally tracked because it contains demo data only.
The application and container never create, migrate, or seed it.

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
- Live evals consume OpenAI requests, can vary slightly between runs, and are
  intentionally excluded from deterministic CI.

## Not production-ready

- No authentication or authorization
- No rate limiting or usage quotas
- No OpenAI or SQLite execution timeout
- No retry or operational tracing

Do not expose the service publicly until these controls match the deployment
environment.

## Next useful work

1. Add request IDs, safe logging, and upstream timeouts.
2. Add authentication and rate limits only when a real deployment requires
   public or shared access.
