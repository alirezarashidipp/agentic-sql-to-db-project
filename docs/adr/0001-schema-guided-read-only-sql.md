# ADR 0001: Schema-guided read-only SQL pipeline

- Status: Accepted
- Date: 2026-07-31

## Context

The schema-guided SQL application must keep the natural-language-to-SQL flow
visible without a large framework. It also executes model-generated text, so
prompt instructions alone cannot protect the database.

## Decision

Use:

- FastAPI for the HTTP boundary and static frontend;
- LangGraph for an explicit validation-to-answer state graph;
- OpenAI structured output for question review and SQL shape;
- live SQLite metadata plus `COLUMN_GUIDE` as the validation contract;
- YAML files for prompt text;
- a pre-provisioned SQLite file opened in read-only mode, with a single-table
  `SELECT` validator, query-only mode, and an authorizer callback.

The system exposes only the fixed table `data`. Invalid or incomplete
questions end after review and never reach SQL generation.

## Consequences

Benefits:

- The request flow is visible in a small number of files.
- Prompt text, dataset knowledge, and execution controls change independently.
- The SQLite authorizer remains effective even if a model returns unsafe SQL.
- A new dataset keeps the table name `data` and requires schema-guide changes.

Costs:

- Valid requests make three model calls.
- SQL capabilities are intentionally narrow.
- Schema and data lifecycle remain the responsibility of the external producer.
- Moving to another database engine requires a new adapter and safety model.

## Rejected alternatives

- A direct question-to-SQL call: fewer steps, but no explicit clarification or
  scope validation.
- An ORM: it does not remove the need to validate model-generated query intent
  and adds concepts unrelated to this application's scope.
- Prompt-only SQL safety: model instructions are not an execution boundary.
- A migration framework: unnecessary because database lifecycle is external.
