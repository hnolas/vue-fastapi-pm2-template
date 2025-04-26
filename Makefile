.PHONY: dev build prod-up prod-down clean logs help

# Default target
help:
	@echo "Available commands:"
	@echo "  make dev        - Start development environment"
	@echo "  make build      - Build all images"
	@echo "  make prod-up    - Start production environment"
	@echo "  make prod-down  - Stop production environment"
	@echo "  make clean      - Remove containers, volumes, and images"
	@echo "  make logs       - View logs from all containers"

# Development mode
dev:
	docker-compose -f docker-compose.yml up --build

# Build images
build:
	docker-compose -f docker-compose.yml build

# Production start
prod-up:
	docker-compose -f docker-compose.yml up -d

# Production stop
prod-down:
	docker-compose -f docker-compose.yml down

# Clean everything
clean:
	docker-compose -f docker-compose.yml down -v --rmi all

# View logs
logs:
	docker-compose -f docker-compose.yml logs -f
