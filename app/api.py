import os
import sqlite3
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from openai import OpenAIError
from pydantic import BaseModel, Field

from .config import MAX_QUESTION_LENGTH, STATIC_DIR, TABLE_NAME
from .database import describe_table, initialize_database, table_schema
from .schema import EXAMPLE_QUESTIONS
from .workflow import question_graph


class QuestionRequest(BaseModel):
    question: str = Field(min_length=2, max_length=MAX_QUESTION_LENGTH)


@asynccontextmanager
async def lifespan(_app: FastAPI):
    initialize_database()
    describe_table()
    yield


app = FastAPI(title=f"{TABLE_NAME} SQL Assistant", lifespan=lifespan)
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")


@app.get("/", response_class=FileResponse)
def index():
    return STATIC_DIR / "index.html"


@app.get("/schema")
def schema():
    return {
        "table": TABLE_NAME,
        "columns": table_schema(),
        "examples": EXAMPLE_QUESTIONS,
        "max_question_length": MAX_QUESTION_LENGTH,
    }


@app.post("/ask")
def ask(payload: QuestionRequest):
    if not os.getenv("OPENAI_API_KEY"):
        raise HTTPException(500, "OPENAI_API_KEY is missing from .env.local.")

    try:
        result = question_graph.invoke({"question": payload.question})
        return {
            "question": payload.question,
            "normalized_question": (
                result.get("normalized_question") or payload.question
            ),
            "status": result["status"],
            "answer": result["answer"],
            "sql": result.get("sql"),
            "rows": result.get("rows", []),
        }
    except ValueError as error:
        raise HTTPException(400, str(error)) from error
    except (OpenAIError, sqlite3.Error) as error:
        raise HTTPException(502, f"Request failed: {error}") from error
