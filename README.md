# llmkg
Exploration of using LLMs to create knowledge graphs

## Requirements

- go 1.24+
- python 3.10+
- uv
- docker
- make

## Getting Started

### Running application

Spin up the application
```bash
make up
```

This will start:
- The [API server](http://127.0.0.1:8000/ping) on port `8000`
- PostgreSQL database on port `5433`
- [Adminer](http://127.0.0.1:8080/?pgsql=db&username=user&db=llmkg_db&ns=public)
    database management tool on port `8080`

Spin down the application
```bash
make down
```

## Development

### Setup

Install dependencies
```bash
go mod download
```

Generate API code from OpenAPI spec
```bash
make openapi-generate
```

### Database migrations

First, have all docker-compose containers running with `make up`.

Create a new migration
```bash
docker compose exec app migrate create -ext sql -dir ./migrations -seq <migration_name>
```

Write your "up" and "down" SQL into the new migration files.

Run all migrations
```bash
make db-migrate-up
```

### API commands:

```bash
http POST localhost:8000/subjects data:='{"name": "Artificial Intelligence"}'
http POST localhost:8000/subjects data:='{"name": "Deep Learning"}'
http POST localhost:8000/subjects data:='{"name": "Computer Vision"}'

http GET localhost:8000/subjects/1
http GET localhost:8000/subjects/2
http GET localhost:8000/subjects/3

http POST localhost:8000/subject-relations data:='{"subject_id": 1, "related_subject_id": 2}'
http POST localhost:8000/subject-relations data:='{"subject_id": 2, "related_subject_id": 3}'

http GET localhost:8000/subjects/1
http GET localhost:8000/subjects/2
http GET localhost:8000/subjects/3
```
