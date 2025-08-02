# Golang + Ogen + Postgres

A simple "items" CRUD API implementation using:
- [Golang](https://golang.org/) - Programming language
- [ogen](https://github.com/ogen-go/ogen) - OpenAPI code generator for Go
- [pgx](https://github.com/jackc/pgx) - PostgreSQL driver and toolkit for Go

## Requirements

- go 1.24+
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
- [Adminer](http://127.0.0.1:8080/?pgsql=db&username=user&db=example_db&ns=public)
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
docker compose run app migrate create -ext sql -dir ./migrations -seq <migration_name>
```

Write your "up" and "down" SQL into the new migration files.

Run all migrations
```bash
make db-migrate-up
```
