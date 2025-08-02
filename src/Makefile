.PHONY: build up down test

openapi-generate:
	docker run --rm --volume=".:/workspace" ghcr.io/ogen-go/ogen:latest \
		--target=/workspace/internal/openapi/ogen \
		--package=ogen \
		--clean \
		/workspace/openapi-schema.yaml \
		--generate-wrappers=on

compile-binaries:
	go build -o ./build/app ./cmd/serverd

testclient:
	go run cmd/testclientd/testclient.go

test:
	go test -v ./...

# Cleanup

cleanup-images-volumes:
	@read -p "Are you sure you want to clean up images and volumes? (yes/no): " answer; \
	if [ "$$answer" = "yes" ]; then \
		docker compose down --rmi all --volumes --remove-orphans; \
	else \
		echo "Cleanup canceled."; \
	fi

