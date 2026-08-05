# Changelog

Notable changes are recorded here.

## Unreleased

- Simplified the LangGraph pipeline, prompt rendering, tests, and frontend;
  removed stale audit/design artifacts without changing user-facing behavior.
- Standardized local development, CI, and Docker on `venv` and `pip`.
- Added `EMPLOYEE_NAME`, expanded the fictional database to 100 rows, and made
  SQLite a pre-provisioned read-only runtime dependency.
- Added conditional post-result Bar and Pie charts without a chart dependency.
- Added focused architecture, API, deployment, database, security, and ADR
  documentation.
- Added agent and project-state context.
- Added deterministic database security tests.
- Added Docker, Compose, Make, and GitHub Actions support.
- Added project-local AI skill and workflow guidance.
- Explicitly close SQLite connections after use.
- Added the FastAPI and LangGraph natural-language-to-SQL workflow.
- Added schema-driven SQLite access and read-only guardrails.
- Added a responsive static frontend and tracked sample database.
