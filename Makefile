.PHONY: test coverage lint type

PYTHON ?= python

test:
	$(PYTHON) -m pytest -v

coverage:
	$(PYTHON) -m pytest --cov=. --cov-report=term-missing --cov-report=html

lint:
	$(PYTHON) -m ruff check .

type:
	$(PYTHON) -m mypy
