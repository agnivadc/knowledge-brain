.PHONY: test lint

test:
	uv sync --extra dev
	uv run pytest tests/ -v

lint:
	uv sync --extra dev
	uv run ruff check knowledge_brain/ tests/
