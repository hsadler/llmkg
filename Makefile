# Streamlit

poc_streamlit:
	poetry run -C streamlit/ streamlit run streamlit/poc_llm_knowledge_graph.py

populate:
	poetry run -C streamlit/ streamlit run streamlit/populate.py


# Backend

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

cleanup-images-volumes:
	@read -p "Are you sure you want to clean up images and volumes? (yes/no): " answer; \
	if [ "$$answer" = "yes" ]; then \
		docker compose down --rmi all --volumes --remove-orphans; \
	else \
		echo "Cleanup canceled."; \
	fi
