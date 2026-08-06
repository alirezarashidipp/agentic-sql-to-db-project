import os
from functools import cache
from pathlib import Path

from openai import OpenAI

ROOT = Path(__file__).resolve().parent.parent
ENV_FILE = ROOT / ".env.local"


def load_local_env() -> None:
    if not ENV_FILE.exists():
        return
    for line in ENV_FILE.read_text(encoding="utf-8").splitlines():
        key, separator, value = line.partition("=")
        if separator and key.strip() and not key.lstrip().startswith("#"):
            os.environ.setdefault(key.strip(), value.strip().strip("\"'"))


def required_env(name: str) -> str:
    value = os.getenv(name)
    if not value:
        raise ValueError(f"{name} is required in .env.local.")
    return value


def positive_int(name: str) -> int:
    value = int(required_env(name))
    if value < 1:
        raise ValueError(f"{name} must be a positive integer.")
    return value


load_local_env()

MODEL = required_env("OPENAI_MODEL")
MAX_QUESTION_LENGTH = positive_int("MAX_QUESTION_LENGTH")
MAX_RESULT_ROWS = positive_int("MAX_RESULT_ROWS")

DB_PATH = Path(required_env("DATABASE_PATH"))
if not DB_PATH.is_absolute():
    DB_PATH = ROOT / DB_PATH

STATIC_DIR = ROOT / "static"
PROMPTS_DIR = ROOT / "prompts"


@cache
def get_openai_client() -> OpenAI:
    return OpenAI()
