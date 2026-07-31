# API

FastAPI serves the frontend and JSON endpoints. When running locally, Swagger UI
is available at <http://127.0.0.1:8000/docs>.

## `GET /`

Returns `static/index.html`.

## `GET /schema`

Returns the configured table, its live SQLite columns combined with
`COLUMN_GUIDE`, example questions, and the maximum question length.

Example response:

```json
{
  "table": "employees",
  "columns": [
    {
      "name": "EMPLOYEE_ID",
      "type": "INTEGER PRIMARY KEY",
      "description": "Unique numeric identifier for one employee.",
      "possible_values": "Integer IDs from 1001 to 1010 in the demo data."
    }
  ],
  "examples": ["How many coders?"],
  "max_question_length": 500
}
```

## `POST /ask`

Request:

```json
{
  "question": "How many coders are in MSW?"
}
```

Successful response:

```json
{
  "question": "How many coders are in MSW?",
  "normalized_question": "How many CODER employees are in MSW?",
  "status": "valid",
  "answer": "There are 2 coders in MSW.",
  "sql": "SELECT COUNT(*) AS total FROM employees WHERE STATUS = 'CODER' AND DEPARTMENT = 'MSW'",
  "rows": [{"total": 2}]
}
```

`status` is one of:

- `valid`: SQL was generated and executed.
- `incomplete`: the response asks one clarification; `sql` is `null`.
- `invalid`: the request is outside the configured table or requests a write;
  `sql` is `null`.

## Errors

| Status | Meaning |
| --- | --- |
| `400` | Workflow or SQL validation rejected the request |
| `422` | Request body or question length failed API validation |
| `500` | `OPENAI_API_KEY` is missing |
| `502` | OpenAI or SQLite failed while processing the request |

The endpoint is synchronous and each request is independent.
