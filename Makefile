# Backend Application

build:
	docker compose build

up:
	docker compose up -d

down:
	docker compose down

# Scripts

run-test-client:
	docker compose exec app sh -c \
	'go run cmd/testclient/main.go'

run-subjpopulate:
	docker compose exec app sh -c \
	'go run cmd/subjpopulate/main.go'

# Database migrations

db-migrate-up:
	docker compose exec app sh -c \
	'migrate -path=./migrations -database="$${DATABASE_URL}?sslmode=disable" up'

db-migrate-down-1:
	docker compose exec app sh -c \
	'migrate -path=./migrations -database="$${DATABASE_URL}?sslmode=disable" down 1'

db-migrate-down-all:
	docker compose exec app sh -c \
	'migrate -path=./migrations -database="$${DATABASE_URL}?sslmode=disable" down -all'

# Cleanup

cleanup-images-volumes:
	@read -p "Are you sure you want to clean up images and volumes? (yes/no): " answer; \
	if [ "$$answer" = "yes" ]; then \
		docker compose down --rmi all --volumes --remove-orphans; \
	else \
		echo "Cleanup canceled."; \
	fi
