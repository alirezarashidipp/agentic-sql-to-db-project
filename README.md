You are a Staff AI Engineer and Software Architect.

Your task is to design and implement a production-quality Natural Language to SQL application.

Do NOT immediately write code.

First design the complete architecture, then implement it incrementally.

==========================
PROJECT
==========================

Build a conversational Text-to-SQL system.

Technology Stack:

- Python 3.12
- LangGraph
- SQLite
- Pydantic v2
- FastAPI
- OpenAI API
- SQLAlchemy
- YAML
- React (or Next.js) frontend
- TailwindCSS

==========================
GOAL
==========================

A user writes questions in natural language.

Example:

"Show me customers with the highest sales during the last 3 months."

The AI MUST NOT immediately generate SQL.

Instead it should first understand the database schema from a YAML file.

The YAML contains metadata about every table and every column.

Example:

table
column_name
description
type
examples

The AI should determine whether the user's question is complete enough.

If information is missing or ambiguous,
it should ask clarification questions.

Examples:

"What do you mean by active customer?"

"Should cancelled orders be included?"

"Which date field should be used?"

Continue clarification until enough information exists.

Maximum clarification rounds:

10

If after 10 rounds the question is still ambiguous,
return a friendly message instead of generating SQL.

==========================
WORKFLOW
==========================

User Question

↓

Load YAML Schema

↓

Understand Schema

↓

Detect Missing Information

↓

Need clarification?

YES → Ask user

NO ↓

Generate SQL

↓

Validate SQL

↓

Execute on SQLite

↓

Return raw data

↓

LLM summarizes result in natural language

↓

Return response to user

==========================
LANGGRAPH
==========================

Use LangGraph for orchestration.

Nodes should include:

- load_schema
- analyze_question
- clarification
- wait_for_user
- sql_generation
- sql_validation
- sql_execution
- answer_generation
- finish

The graph must support loops.

Clarification count must be stored in state.

==========================
STATE
==========================

Design a Pydantic state object.

Example fields:

conversation_history

user_question

clarified_question

clarification_count

schema

generated_sql

validated_sql

query_result

final_answer

errors

==========================
YAML
==========================

The database schema comes from YAML.

Design a robust YAML format.

Each table should contain:

table_name

description

columns

Each column should contain:

column_name

description

type

examples

nullable

primary_key

foreign_key

allowed_values

unit

semantic_type

The system should use the YAML instead of inspecting SQLite directly.

==========================
SQL GENERATION
==========================

SQL generation must be deterministic.

Generate ONLY SELECT queries.

Never generate:

UPDATE

DELETE

INSERT

DROP

ALTER

PRAGMA

ATTACH

Reject unsafe SQL.

Validate table names.

Validate columns.

Validate joins.

Validate syntax.

==========================
EXECUTION
==========================

Execute SQL on SQLite.

Handle errors gracefully.

If SQL fails:

Do NOT regenerate SQL automatically.

Instead explain the issue.

==========================
FINAL RESPONSE
==========================

The LLM should NEVER invent data.

Only summarize the SQL results.

If there are no rows:

Return an explanation.

==========================
FRONTEND
==========================

Build a ChatGPT-like interface.

Features:

Conversation history

Streaming responses

Loading indicator

Clarification questions

SQL hidden from user

Optional SQL debug panel

==========================
PROJECT STRUCTURE
==========================

Design a clean architecture.

Example:

backend/

frontend/

schemas/

graphs/

agents/

models/

services/

repositories/

validators/

prompts/

tests/

config/

==========================
TESTING
==========================

Write unit tests.

Write integration tests.

Mock OpenAI API.

==========================
OUTPUT FORMAT
==========================

I do NOT want one huge answer.

Work as a senior software architect.

Implement the project in phases.

Phase 1:
Architecture

Wait.

Phase 2:
Folder Structure

Wait.

Phase 3:
LangGraph State

Wait.

Phase 4:
Nodes

Wait.

Phase 5:
Graph

Wait.

Phase 6:
Prompts

Wait.

Phase 7:
Backend

Wait.

Phase 8:
Frontend

Wait.

Phase 9:
Testing

Wait.

Never skip a phase.

Never generate placeholder code.

Write production-quality code.

Follow SOLID principles.

Keep components loosely coupled.

Prefer composition over inheritance.

Explain important architectural decisions before writing code.
