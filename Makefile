.PHONY: sync run check test docker-up docker-down

sync:
	uv sync --locked

run:
	uv run python main.py

check:
	uv run python main.py --check

test:
	uv run python -m unittest discover -s tests -v
	node --test tests/test_chart.cjs

docker-up:
	docker compose up --build

docker-down:
	docker compose down
