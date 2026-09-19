.PHONY: install test lint eval run docker

install:
	python -m pip install -e ".[dev]"

test:
	pytest

lint:
	ruff check app tests

eval:
	python -m app.cli eval --output artifacts/evaluation.json

run:
	python -m app.cli serve

docker:
	docker compose up --build
