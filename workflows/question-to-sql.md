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

1. `review_question` loads the schema and returns `valid`, `incomplete`, or
   `invalid`.
2. `query_database` generates one query, then validates and executes it.
3. `generate_answer` answers only from the question, SQL, and rows.

## Routing

```text
START -> review_question
          | valid -> query_database -> generate_answer -> END
          ` incomplete / invalid -----------------------> END
```

## Change contract

- Do not bypass question review for user input.
- Do not call SQLite with SQL that has not passed `validate_sql`.
- Keep incomplete and invalid paths free of SQL and database execution.
- Update the matching prompt version when prompt behavior changes.
- Add a deterministic test for routing or guardrail changes.
