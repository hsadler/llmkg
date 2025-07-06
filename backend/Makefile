black:
	poetry run black .

flake8:
	poetry run flake8 .

isort:
	poetry run isort . || true

mypy:
	poetry run mypy .

lint: black isort flake8 mypy

pytest:
	poetry run pytest

pre-commit: lint pytest
