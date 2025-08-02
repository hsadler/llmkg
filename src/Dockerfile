# Base image with common dependencies
FROM golang:1.24.5-bullseye AS base

WORKDIR /app
COPY . .

RUN apt-get update -y
RUN go install -tags 'postgres' github.com/golang-migrate/migrate/v4/cmd/migrate@v4.18.2

# Development stage
FROM base AS development
RUN apt-get install -y git
RUN go install -mod=mod github.com/githubnemo/CompileDaemon
EXPOSE 8000

# Production stage
FROM base AS production
RUN go build -o app .
ENV IS_PROD=true
EXPOSE 8000
ENTRYPOINT migrate -path=./migrations -database="$DATABASE_URL?sslmode=disable" up && ./build/app
