.PHONY: test coverage lint

test:
	pytest -v

coverage:
	pytest --cov=. --cov-report=term-missing --cov-report=html

lint:
	ruff check .
