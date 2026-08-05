import sys

from app.api import app
from app.config import TABLE_NAME
from app.database import describe_table, execute_sql


def self_check() -> None:
    schema = describe_table()
    assert TABLE_NAME in schema
    assert execute_sql(
        f'SELECT COUNT(*) AS total FROM "{TABLE_NAME}"'
    )[0]["total"] >= 0
    print("self-check passed")


if __name__ == "__main__":
    if "--check" in sys.argv:
        self_check()
    else:
        import uvicorn

        uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
