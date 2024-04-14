build:
	docker compose build

up:
	docker compose up -d

down:
	docker compose down

app-shell:
	docker compose exec app bash

db-migrate:
	docker compose exec app alembic upgrade head

db-migrate-dry-run:
	docker compose exec app alembic upgrade head --sql

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

loadtest:
	poetry run locust -f locustfile.py --headless --tag=status \
	-u=1 -r=10 --run-time=1s --host=http://localhost:8000 && \
	poetry run locust -f locustfile.py --headless --tag=long-running \
	-u=1 -r=10 --run-time=5s --host=http://localhost:8000 && \
	poetry run locust -f locustfile.py --headless --tag=item \
	-u=1 -r=10 --run-time=1s --host=http://localhost:8000
	poetry run locust -f locustfile.py --headless --tag=items \
	-u=1 -r=10 --run-time=1s --host=http://localhost:8000

cleanup-images-volumes:
	@read -p "Are you sure you want to clean up images and volumes? (yes/no): " answer; \
	if [ "$$answer" = "yes" ]; then \
		docker compose down --rmi all --volumes --remove-orphans; \
	else \
		echo "Cleanup canceled."; \
	fi
