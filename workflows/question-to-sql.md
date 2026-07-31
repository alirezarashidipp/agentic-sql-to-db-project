# Question-to-SQL Workflow

This file is the human-readable contract for the LangGraph implementation in
`app/workflow.py`.

## State

The workflow may carry:

- original and normalized questions;
- live schema text;
- review status and message;
- generated SQL;
- returned rows;
- final answer.

## Nodes

1. `load_schema` combines SQLite metadata with `COLUMN_GUIDE`.
2. `review_question` returns `valid`, `incomplete`, or `invalid`.
3. `generate_sql` runs only for a valid normalized question.
4. `run_sql` validates and executes the query.
5. `generate_answer` answers only from the question, SQL, and rows.

## Routing

```text
START -> load_schema -> review_question
                         | valid
                         v
                       generate_sql -> run_sql -> generate_answer -> END
                         |
                         + incomplete / invalid ---------------------> END
```

## Change contract

- Do not bypass question review for user input.
- Do not call SQLite with SQL that has not passed `validate_sql`.
- Keep incomplete and invalid paths free of SQL and database execution.
- Update the matching prompt version when prompt behavior changes.
- Add a deterministic test for routing or guardrail changes.
