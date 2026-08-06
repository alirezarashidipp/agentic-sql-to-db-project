import json
from typing import Literal, NotRequired, TypedDict

from langgraph.graph import END, START, StateGraph
from pydantic import BaseModel

from .config import MAX_RESULT_ROWS, MODEL, get_openai_client
from .database import describe_table, execute_sql
from .prompts import load_prompt, render_prompt

ReviewStatus = Literal["valid", "incomplete", "invalid"]


class WorkflowState(TypedDict):
    question: str
    schema: NotRequired[str]
    status: NotRequired[ReviewStatus]
    normalized_question: NotRequired[str]
    message: NotRequired[str]
    sql: NotRequired[str]
    rows: NotRequired[list[dict]]
    answer: NotRequired[str]


class QuestionReview(BaseModel):
    status: ReviewStatus
    normalized_question: str
    message: str


class SqlQuery(BaseModel):
    sql: str


def review_question(state: WorkflowState) -> dict:
    schema = describe_table()
    response = get_openai_client().responses.parse(
        model=MODEL,
        reasoning={"effort": "none"},
        input=[
            {
                "role": "developer",
                "content": render_prompt(
                    "question_review", schema=schema
                ),
            },
            {"role": "user", "content": state["question"]},
        ],
        text_format=QuestionReview,
        store=False,
    )
    if not response.output_parsed:
        raise ValueError("The model could not review the question.")

    review = response.output_parsed
    update = {"schema": schema, **review.model_dump()}
    if review.status != "valid":
        update["answer"] = review.message
    return update


def route_after_review(state: WorkflowState) -> Literal["query_database", END]:
    return "query_database" if state["status"] == "valid" else END


def query_database(state: WorkflowState) -> dict:
    response = get_openai_client().responses.parse(
        model=MODEL,
        reasoning={"effort": "none"},
        input=[
            {
                "role": "developer",
                "content": render_prompt(
                    "sql_generation",
                    schema=state["schema"],
                    max_rows=MAX_RESULT_ROWS,
                ),
            },
            {"role": "user", "content": state["normalized_question"]},
        ],
        text_format=SqlQuery,
        store=False,
    )
    if not response.output_parsed:
        raise ValueError("The model did not return a SQL query.")
    sql = response.output_parsed.sql.strip()
    return {"sql": sql, "rows": execute_sql(sql)}


def generate_answer(state: WorkflowState) -> dict:
    response = get_openai_client().responses.create(
        model=MODEL,
        reasoning={"effort": "none"},
        instructions=load_prompt("answer"),
        input=json.dumps(
            {
                "question": state["normalized_question"],
                "sql": state["sql"],
                "rows": state["rows"],
            },
            ensure_ascii=False,
        ),
        store=False,
    )
    return {"answer": response.output_text}


builder = StateGraph(WorkflowState)
builder.add_node("review_question", review_question)
builder.add_node("query_database", query_database)
builder.add_node("generate_answer", generate_answer)
builder.add_edge(START, "review_question")
builder.add_conditional_edges("review_question", route_after_review)
builder.add_edge("query_database", "generate_answer")
builder.add_edge("generate_answer", END)
question_graph = builder.compile()
