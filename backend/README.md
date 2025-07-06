# llmkg-backend

## Getting started

Requirements:
- docker
- pyenv
- poetry
- httpie

Ensure the correct python version is installed
```sh
pyenv install
```

Tell poetry which python to use
```sh
poetry env use python
```

Install dependencies (including dev dependencies)
```sh
poetry install
```

Build images
```sh
docker compose build
```

Run containers locally
```sh
docker compose up -d
```

Verify server is running by hitting the status endpoint
```sh
http GET http://localhost:8000/status
```

Run DB migrations
```sh
docker compose exec app alembic upgrade head
```

### Running the docker containers will spin-up Swagger docs and Adminer

- Visit Swagger docs here:

    ```sh
    http://127.0.0.1:8000/docs
    ```

- Visit Adminer DB management tool here:

    ```sh
    http://127.0.0.1:8080/?pgsql=db&username=user&db=llmkg_db&ns=public
    ```

## Database migrations

Alembic is used to manage raw SQL migrations. Migrations are not automatically
run when doing local development, but _are_ run automatically when a production
container is started.

The process for creating new migration files, dry-run testing, and application
of a new migration is as follows.

Make sure you have the containers up and running in a terminal tab:
```sh
docker compose up -d
```

Open a poetry shell
```sh
poetry shell
```

Create a new migration file
```sh
alembic revision -m "my new migration"
# and also write your `upgrade` and `downgrade` queries
```

Dry run your migration
```sh
docker compose exec app alembic upgrade head --sql
```

Apply your new migration
```sh
docker compose exec app alembic upgrade head
```

(optional) Roll-back your migration
```sh
docker compose exec app alembic downgrade -1
```
