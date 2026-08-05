import json
import os
import sys
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import pytest
from deepeval import assert_test
from deepeval.metrics import AnswerRelevancyMetric, FaithfulnessMetric, GEval
from deepeval.test_case import LLMTestCase, SingleTurnParams

from app import workflow
from app.config import TABLE_NAME
from app.database import execute_sql
from app.prompts import load_prompt
from app.schema import EVAL_CASES

JUDGE_MODEL = os.getenv("OPENAI_MODEL_NAME", "gpt-4.1")

if not os.getenv("OPENAI_API_KEY"):
    raise RuntimeError("OPENAI_API_KEY is required in .env.local to run evals.")


def _row_values(row):
    return tuple(
        sorted((type(value).__name__, repr(value)) for value in row.values())
    )


def _rows_equal(actual, expected, mode):
    if mode == "scalar":
        return (
            len(actual) == len(expected) == 1
            and len(actual[0]) == len(expected[0]) == 1
            and next(iter(actual[0].values()))
            == next(iter(expected[0].values()))
        )

    actual_values = list(map(_row_values, actual))
    expected_values = list(map(_row_values, expected))
    if mode == "ordered":
        return actual_values == expected_values
    if mode in {"grouped", "unordered"}:
        return sorted(actual_values) == sorted(expected_values)
    raise ValueError(f"Unknown comparison mode: {mode}")


def _sql(template):
    return template.format(table=TABLE_NAME)


@pytest.mark.parametrize(
    "case", EVAL_CASES["sql"], ids=lambda case: case["id"]
)
def test_generated_sql_matches_reference_result(case):
    review = workflow.review_question({"question": case["question"]})
    assert review["status"] == "valid", review

    generated = workflow.query_database(review)
    expected_rows = execute_sql(_sql(case["reference_sql"]))
    assert _rows_equal(generated["rows"], expected_rows, case["compare"]), (
        f"generated SQL: {generated['sql']}\n"
        f"generated rows: {generated['rows']}\n"
        f"expected rows: {expected_rows}"
    )


@pytest.mark.parametrize(
    "case", EVAL_CASES["rejected"], ids=lambda case: case["id"]
)
def test_unclear_or_invalid_question_is_rejected_without_sql(case):
    with patch.object(
        workflow,
        "execute_sql",
        side_effect=AssertionError("A rejected question attempted to run SQL."),
    ):
        result = workflow.question_graph.invoke({"question": case["question"]})

    assert result["status"] == case["expected_status"], result
    assert "sql" not in result
    assert "rows" not in result


@pytest.mark.parametrize(
    "case", EVAL_CASES["answers"], ids=lambda case: case["id"]
)
def test_final_answer_is_correct_relevant_and_grounded(case):
    result = workflow.generate_answer(
        {
            "normalized_question": case["question"],
            "sql": _sql(case["sql"]),
            "rows": case["rows"],
        }
    )
    test_case = LLMTestCase(
        input=case["question"],
        actual_output=result["answer"],
        expected_output=case["reference_answer"],
        retrieval_context=[
            json.dumps(case["rows"], ensure_ascii=False, default=str)
        ],
    )
    assert_test(
        test_case,
        [
            AnswerRelevancyMetric(threshold=0.7, model=JUDGE_MODEL),
            FaithfulnessMetric(threshold=0.7, model=JUDGE_MODEL),
            GEval(
                name="Answer correctness",
                criteria=load_prompt("answer_eval"),
                evaluation_params=[
                    SingleTurnParams.INPUT,
                    SingleTurnParams.ACTUAL_OUTPUT,
                    SingleTurnParams.EXPECTED_OUTPUT,
                ],
                threshold=0.7,
                model=JUDGE_MODEL,
            ),
        ],
    )
