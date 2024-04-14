# Base image with common dependencies
FROM python:3.12-slim-bullseye AS base
WORKDIR /app
RUN pip install poetry
COPY pyproject.toml poetry.lock ./

# Development stage
FROM base AS development
RUN apt-get update -y && apt-get install -y make gcc python3-dev
RUN poetry config virtualenvs.create false && \
    poetry install --no-interaction --no-ansi
COPY . .
EXPOSE 8000
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]

# Production stage
FROM base AS production
RUN poetry config virtualenvs.create false && \
    poetry install --no-dev --no-interaction --no-ansi
COPY . .
ENV IS_PROD=true
EXPOSE 8000
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]