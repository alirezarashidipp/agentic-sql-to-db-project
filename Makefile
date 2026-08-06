.PHONY: install run check test docker-up docker-down

install:
	python -m pip install -r requirements.txt

run:
	python main.py

check:
	python main.py --check

test:
	python -m unittest discover -s tests -v
	node --test tests/test_chart.cjs

docker-up:
	docker compose up --build

docker-down:
	docker compose down
