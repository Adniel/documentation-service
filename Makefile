# Documentation Service Platform - Makefile
# ============================================================================
# Run `make help` to see available commands
# ============================================================================

.PHONY: help install dev stop status logs test lint format build clean docker db

# Default target
.DEFAULT_GOAL := help

# Colors for terminal output
CYAN := \033[36m
GREEN := \033[32m
YELLOW := \033[33m
RED := \033[31m
RESET := \033[0m

# Directories
BACKEND_DIR := backend
FRONTEND_DIR := frontend

# ============================================================================
# HELP
# ============================================================================

help: ## Show this help message
	@echo ""
	@echo "$(CYAN)Documentation Service Platform$(RESET)"
	@echo "$(CYAN)==============================$(RESET)"
	@echo ""
	@echo "$(GREEN)Usage:$(RESET) make [target]"
	@echo ""
	@echo "$(YELLOW)Setup & Installation:$(RESET)"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | grep -E '(install|setup)' | awk 'BEGIN {FS = ":.*?## "}; {printf "  $(CYAN)%-20s$(RESET) %s\n", $$1, $$2}'
	@echo ""
	@echo "$(YELLOW)Development:$(RESET)"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | grep -E '(dev|start|stop|status|run|^logs)' | awk 'BEGIN {FS = ":.*?## "}; {printf "  $(CYAN)%-20s$(RESET) %s\n", $$1, $$2}'
	@echo ""
	@echo "$(YELLOW)Testing:$(RESET)"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | grep -E '(test)' | awk 'BEGIN {FS = ":.*?## "}; {printf "  $(CYAN)%-20s$(RESET) %s\n", $$1, $$2}'
	@echo ""
	@echo "$(YELLOW)Code Quality:$(RESET)"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | grep -E '(lint|format|type)' | awk 'BEGIN {FS = ":.*?## "}; {printf "  $(CYAN)%-20s$(RESET) %s\n", $$1, $$2}'
	@echo ""
	@echo "$(YELLOW)Database:$(RESET)"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | grep -E '(db|migration)' | awk 'BEGIN {FS = ":.*?## "}; {printf "  $(CYAN)%-20s$(RESET) %s\n", $$1, $$2}'
	@echo ""
	@echo "$(YELLOW)Docker:$(RESET)"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | grep -E '(docker)' | awk 'BEGIN {FS = ":.*?## "}; {printf "  $(CYAN)%-20s$(RESET) %s\n", $$1, $$2}'
	@echo ""
	@echo "$(YELLOW)Build & Deploy:$(RESET)"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | grep -E '(build|clean|prod)' | awk 'BEGIN {FS = ":.*?## "}; {printf "  $(CYAN)%-20s$(RESET) %s\n", $$1, $$2}'
	@echo ""

# ============================================================================
# SETUP & INSTALLATION
# ============================================================================

install: install-backend install-frontend ## Install all dependencies

install-backend: ## Install backend dependencies
	@echo "$(CYAN)Installing backend dependencies...$(RESET)"
	cd $(BACKEND_DIR) && pip install -e ".[dev]"
	@echo "$(GREEN)Backend dependencies installed$(RESET)"

install-frontend: ## Install frontend dependencies
	@echo "$(CYAN)Installing frontend dependencies...$(RESET)"
	cd $(FRONTEND_DIR) && npm install
	@echo "$(GREEN)Frontend dependencies installed$(RESET)"

setup: ## Initial project setup (install deps, setup env, run migrations)
	@echo "$(CYAN)Setting up project...$(RESET)"
	@make install
	@make setup-env
	@make db-upgrade
	@echo "$(GREEN)Project setup complete!$(RESET)"

setup-env: ## Create .env files from examples
	@echo "$(CYAN)Setting up environment files...$(RESET)"
	@if [ ! -f $(BACKEND_DIR)/.env ]; then \
		cp $(BACKEND_DIR)/.env.example $(BACKEND_DIR)/.env; \
		echo "$(GREEN)Created backend/.env$(RESET)"; \
	else \
		echo "$(YELLOW)backend/.env already exists, skipping$(RESET)"; \
	fi
	@if [ ! -f $(FRONTEND_DIR)/.env ]; then \
		cp $(FRONTEND_DIR)/.env.example $(FRONTEND_DIR)/.env; \
		echo "$(GREEN)Created frontend/.env$(RESET)"; \
	else \
		echo "$(YELLOW)frontend/.env already exists, skipping$(RESET)"; \
	fi

# ============================================================================
# DEVELOPMENT SERVERS
# ============================================================================

dev: ## Start all development servers (backend + frontend) in background
	@echo "$(CYAN)Starting development servers...$(RESET)"
	@make dev-backend
	@make dev-frontend
	@echo "$(GREEN)All servers started. Use 'make logs' to view output.$(RESET)"

dev-backend: ## Start backend development server (background, logs to ./logs/backend.log)
	@mkdir -p logs
	@if pgrep -f "uvicorn src.main:app" >/dev/null 2>&1; then \
		echo "$(YELLOW)Backend already running$(RESET)"; \
	else \
		echo "$(CYAN)Starting backend server on http://localhost:8000$(RESET)"; \
		cd $(BACKEND_DIR) && nohup uvicorn src.main:app --reload --port 8000 > ../logs/backend.log 2>&1 & \
		sleep 1; \
		if pgrep -f "uvicorn src.main:app" >/dev/null 2>&1; then \
			echo "$(GREEN)Backend started (logs: ./logs/backend.log)$(RESET)"; \
		else \
			echo "$(RED)Backend failed to start. Check ./logs/backend.log$(RESET)"; \
		fi; \
	fi

dev-frontend: ## Start frontend development server (background, logs to ./logs/frontend.log)
	@mkdir -p logs
	@if pgrep -f "vite" >/dev/null 2>&1 && ! docker-compose ps --services --filter "status=running" 2>/dev/null | grep -q "^frontend$$"; then \
		echo "$(YELLOW)Frontend already running$(RESET)"; \
	else \
		echo "$(CYAN)Starting frontend server on http://localhost:5173$(RESET)"; \
		cd $(FRONTEND_DIR) && nohup npm run dev > ../logs/frontend.log 2>&1 & \
		sleep 2; \
		if lsof -i :5173 -sTCP:LISTEN >/dev/null 2>&1; then \
			echo "$(GREEN)Frontend started (logs: ./logs/frontend.log)$(RESET)"; \
		else \
			echo "$(RED)Frontend failed to start. Check ./logs/frontend.log$(RESET)"; \
		fi; \
	fi

dev-backend-interactive: ## Start backend server interactively (foreground)
	@echo "$(CYAN)Starting backend server on http://localhost:8000$(RESET)"
	cd $(BACKEND_DIR) && uvicorn src.main:app --reload --port 8000

dev-frontend-interactive: ## Start frontend server interactively (foreground)
	@echo "$(CYAN)Starting frontend server on http://localhost:5173$(RESET)"
	cd $(FRONTEND_DIR) && npm run dev

run-backend: dev-backend ## Alias for dev-backend

run-frontend: dev-frontend ## Alias for dev-frontend

stop: ## Stop all running development servers
	@echo "$(CYAN)Stopping development servers...$(RESET)"
	@-pkill -f "uvicorn src.main:app" 2>/dev/null || true
	@-pkill -f "vite" 2>/dev/null || true
	@echo "$(GREEN)Servers stopped$(RESET)"

logs: ## Tail all development server logs
	@echo "$(CYAN)Tailing logs (Ctrl+C to stop)...$(RESET)"
	@tail -f logs/backend.log logs/frontend.log 2>/dev/null || echo "$(YELLOW)No log files found. Start servers first.$(RESET)"

logs-backend: ## Tail backend logs
	@echo "$(CYAN)Tailing backend logs (Ctrl+C to stop)...$(RESET)"
	@tail -f logs/backend.log 2>/dev/null || echo "$(YELLOW)No backend log found. Start backend first.$(RESET)"

logs-frontend: ## Tail frontend logs
	@echo "$(CYAN)Tailing frontend logs (Ctrl+C to stop)...$(RESET)"
	@tail -f logs/frontend.log 2>/dev/null || echo "$(YELLOW)No frontend log found. Start frontend first.$(RESET)"

status: ## Show status of all services
	@echo ""
	@echo "$(CYAN)Service Status$(RESET)"
	@echo "$(CYAN)==============$(RESET)"
	@# Check what's running via Docker
	@DOCKER_BACKEND=$$(docker-compose ps --services --filter "status=running" 2>/dev/null | grep -q "^backend$$" && echo "1" || echo "0"); \
	DOCKER_FRONTEND=$$(docker-compose ps --services --filter "status=running" 2>/dev/null | grep -q "^frontend$$" && echo "1" || echo "0"); \
	NATIVE_BACKEND=$$(pgrep -f "uvicorn src.main:app" >/dev/null 2>&1 && echo "1" || echo "0"); \
	NATIVE_FRONTEND=$$(pgrep -f "vite" >/dev/null 2>&1 && ! docker-compose ps --services --filter "status=running" 2>/dev/null | grep -q "^frontend$$" && echo "1" || echo "0"); \
	PORT_8000=$$(lsof -i :8000 -sTCP:LISTEN >/dev/null 2>&1 && echo "1" || echo "0"); \
	PORT_5173=$$(lsof -i :5173 -sTCP:LISTEN >/dev/null 2>&1 && echo "1" || echo "0"); \
	echo ""; \
	echo "$(YELLOW)Development Servers (native):$(RESET)"; \
	if [ "$$NATIVE_BACKEND" = "1" ]; then \
		echo "  $(GREEN)●$(RESET) Backend (uvicorn)    $(GREEN)running$(RESET) on http://localhost:8000"; \
	elif [ "$$DOCKER_BACKEND" = "0" ] && [ "$$PORT_8000" = "1" ]; then \
		echo "  $(YELLOW)●$(RESET) Backend              $(YELLOW)port 8000 in use (unknown)$(RESET)"; \
	elif [ "$$DOCKER_BACKEND" = "0" ]; then \
		echo "  $(RED)○$(RESET) Backend (uvicorn)    $(RED)stopped$(RESET)"; \
	else \
		echo "  $(RED)○$(RESET) Backend (uvicorn)    $(RED)stopped$(RESET) (using Docker)"; \
	fi; \
	if [ "$$NATIVE_FRONTEND" = "1" ]; then \
		echo "  $(GREEN)●$(RESET) Frontend (vite)     $(GREEN)running$(RESET) on http://localhost:5173"; \
	elif [ "$$DOCKER_FRONTEND" = "0" ] && [ "$$PORT_5173" = "1" ]; then \
		echo "  $(YELLOW)●$(RESET) Frontend             $(YELLOW)port 5173 in use (unknown)$(RESET)"; \
	elif [ "$$DOCKER_FRONTEND" = "0" ]; then \
		echo "  $(RED)○$(RESET) Frontend (vite)     $(RED)stopped$(RESET)"; \
	else \
		echo "  $(RED)○$(RESET) Frontend (vite)     $(RED)stopped$(RESET) (using Docker)"; \
	fi; \
	echo ""; \
	echo "$(YELLOW)Docker Services:$(RESET)"; \
	if [ "$$DOCKER_BACKEND" = "1" ]; then \
		echo "  $(GREEN)●$(RESET) Backend (Docker)    $(GREEN)running$(RESET) on http://localhost:8000"; \
	else \
		echo "  $(RED)○$(RESET) Backend (Docker)    $(RED)stopped$(RESET)"; \
	fi; \
	if [ "$$DOCKER_FRONTEND" = "1" ]; then \
		echo "  $(GREEN)●$(RESET) Frontend (Docker)   $(GREEN)running$(RESET) on http://localhost:5173"; \
	else \
		echo "  $(RED)○$(RESET) Frontend (Docker)   $(RED)stopped$(RESET)"; \
	fi; \
	if docker-compose ps --services --filter "status=running" 2>/dev/null | grep -q "^postgres$$"; then \
		echo "  $(GREEN)●$(RESET) PostgreSQL           $(GREEN)running$(RESET) on localhost:5432"; \
	else \
		echo "  $(RED)○$(RESET) PostgreSQL           $(RED)stopped$(RESET)"; \
	fi; \
	if docker-compose ps --services --filter "status=running" 2>/dev/null | grep -q "^meilisearch$$"; then \
		echo "  $(GREEN)●$(RESET) Meilisearch          $(GREEN)running$(RESET) on localhost:7700"; \
	else \
		echo "  $(RED)○$(RESET) Meilisearch          $(RED)stopped$(RESET)"; \
	fi; \
	if docker-compose ps --services --filter "status=running" 2>/dev/null | grep -q "^redis$$"; then \
		echo "  $(GREEN)●$(RESET) Redis                $(GREEN)running$(RESET) on localhost:6379"; \
	else \
		echo "  $(RED)○$(RESET) Redis                $(RED)stopped$(RESET)"; \
	fi; \
	echo ""

# ============================================================================
# TESTING
# ============================================================================

test: test-backend test-frontend ## Run all tests

test-backend: ## Run backend tests
	@echo "$(CYAN)Running backend tests...$(RESET)"
	cd $(BACKEND_DIR) && pytest -v

test-frontend: ## Run frontend tests
	@echo "$(CYAN)Running frontend tests...$(RESET)"
	cd $(FRONTEND_DIR) && npm run test:run

test-watch: ## Run frontend tests in watch mode
	@echo "$(CYAN)Running frontend tests in watch mode...$(RESET)"
	cd $(FRONTEND_DIR) && npm test

test-coverage: test-coverage-backend test-coverage-frontend ## Run all tests with coverage

test-coverage-backend: ## Run backend tests with coverage report
	@echo "$(CYAN)Running backend tests with coverage...$(RESET)"
	cd $(BACKEND_DIR) && pytest --cov=src --cov-report=html --cov-report=term-missing
	@echo "$(GREEN)Coverage report: backend/htmlcov/index.html$(RESET)"

test-coverage-frontend: ## Run frontend tests with coverage report
	@echo "$(CYAN)Running frontend tests with coverage...$(RESET)"
	cd $(FRONTEND_DIR) && npm run test:coverage
	@echo "$(GREEN)Coverage report: frontend/coverage/index.html$(RESET)"

test-unit: ## Run only unit tests (backend)
	@echo "$(CYAN)Running backend unit tests...$(RESET)"
	cd $(BACKEND_DIR) && pytest tests/unit/ -v

test-integration: ## Run only integration tests (backend)
	@echo "$(CYAN)Running backend integration tests...$(RESET)"
	cd $(BACKEND_DIR) && pytest tests/integration/ -v

# ============================================================================
# CODE QUALITY
# ============================================================================

lint: lint-backend lint-frontend ## Run all linters

lint-backend: ## Run backend linter (ruff)
	@echo "$(CYAN)Linting backend code...$(RESET)"
	cd $(BACKEND_DIR) && ruff check src/

lint-frontend: ## Run frontend linter (eslint)
	@echo "$(CYAN)Linting frontend code...$(RESET)"
	cd $(FRONTEND_DIR) && npm run lint

format: format-backend ## Format all code

format-backend: ## Format backend code (ruff)
	@echo "$(CYAN)Formatting backend code...$(RESET)"
	cd $(BACKEND_DIR) && ruff format src/
	cd $(BACKEND_DIR) && ruff check --fix src/

typecheck: typecheck-backend typecheck-frontend ## Run all type checkers

typecheck-backend: ## Run backend type checker (mypy)
	@echo "$(CYAN)Type checking backend...$(RESET)"
	cd $(BACKEND_DIR) && mypy src/

typecheck-frontend: ## Run frontend type checker (tsc)
	@echo "$(CYAN)Type checking frontend...$(RESET)"
	cd $(FRONTEND_DIR) && npm run type-check

check: lint typecheck test ## Run all checks (lint, typecheck, test)

# ============================================================================
# DATABASE
# ============================================================================

db-upgrade: ## Run database migrations
	@echo "$(CYAN)Running database migrations...$(RESET)"
	cd $(BACKEND_DIR) && alembic upgrade head
	@echo "$(GREEN)Migrations complete$(RESET)"

db-downgrade: ## Rollback last database migration
	@echo "$(CYAN)Rolling back last migration...$(RESET)"
	cd $(BACKEND_DIR) && alembic downgrade -1

db-migration: ## Create a new migration (usage: make db-migration name="migration name")
	@echo "$(CYAN)Creating new migration...$(RESET)"
	cd $(BACKEND_DIR) && alembic revision --autogenerate -m "$(name)"
	@echo "$(GREEN)Migration created$(RESET)"

db-history: ## Show migration history
	@echo "$(CYAN)Migration history:$(RESET)"
	cd $(BACKEND_DIR) && alembic history

db-current: ## Show current migration
	@echo "$(CYAN)Current migration:$(RESET)"
	cd $(BACKEND_DIR) && alembic current

db-reset: ## Reset database (drop all tables and re-run migrations)
	@echo "$(RED)WARNING: This will delete all data!$(RESET)"
	@read -p "Are you sure? [y/N] " confirm && [ "$$confirm" = "y" ]
	@echo "$(CYAN)Resetting database...$(RESET)"
	cd $(BACKEND_DIR) && alembic downgrade base
	cd $(BACKEND_DIR) && alembic upgrade head
	@echo "$(GREEN)Database reset complete$(RESET)"

# ============================================================================
# DOCKER
# ============================================================================

docker-up: ## Start all Docker services
	@echo "$(CYAN)Starting Docker services...$(RESET)"
	docker-compose up -d
	@echo "$(GREEN)Services started$(RESET)"

docker-down: ## Stop all Docker services
	@echo "$(CYAN)Stopping Docker services...$(RESET)"
	docker-compose down

docker-logs: ## Show Docker service logs
	docker-compose logs -f

docker-ps: ## Show running Docker containers
	docker-compose ps

docker-infra: ## Start only infrastructure services (db, search, cache)
	@echo "$(CYAN)Starting infrastructure services...$(RESET)"
	docker-compose up -d postgres meilisearch redis
	@echo "$(GREEN)Infrastructure services started$(RESET)"
	@echo "  PostgreSQL: localhost:5432"
	@echo "  Meilisearch: localhost:7700"
	@echo "  Redis: localhost:6379"

docker-stop-infra: ## Stop infrastructure services
	@echo "$(CYAN)Stopping infrastructure services...$(RESET)"
	docker-compose stop postgres meilisearch redis

docker-clean: ## Remove all Docker containers and volumes
	@echo "$(RED)WARNING: This will delete all Docker data!$(RESET)"
	@read -p "Are you sure? [y/N] " confirm && [ "$$confirm" = "y" ]
	docker-compose down -v --remove-orphans

docker-build: ## Build Docker images
	@echo "$(CYAN)Building Docker images...$(RESET)"
	docker-compose build

# ============================================================================
# BUILD & PRODUCTION
# ============================================================================

build: build-frontend ## Build for production

build-frontend: ## Build frontend for production
	@echo "$(CYAN)Building frontend...$(RESET)"
	cd $(FRONTEND_DIR) && npm run build
	@echo "$(GREEN)Frontend build complete: frontend/dist/$(RESET)"

build-check: ## Build and verify everything works
	@echo "$(CYAN)Running production build check...$(RESET)"
	@make lint
	@make typecheck
	@make test
	@make build
	@echo "$(GREEN)Build check passed!$(RESET)"

prod-backend: ## Run backend in production mode
	@echo "$(CYAN)Starting backend in production mode...$(RESET)"
	cd $(BACKEND_DIR) && uvicorn src.main:app --host 0.0.0.0 --port 8000

prod-frontend: ## Serve frontend production build
	@echo "$(CYAN)Serving frontend production build...$(RESET)"
	cd $(FRONTEND_DIR) && npm run preview

clean: ## Clean build artifacts and caches
	@echo "$(CYAN)Cleaning build artifacts...$(RESET)"
	rm -rf $(FRONTEND_DIR)/dist
	rm -rf $(FRONTEND_DIR)/coverage
	rm -rf $(FRONTEND_DIR)/node_modules/.vite
	rm -rf $(BACKEND_DIR)/htmlcov
	rm -rf $(BACKEND_DIR)/.pytest_cache
	rm -rf $(BACKEND_DIR)/.mypy_cache
	rm -rf $(BACKEND_DIR)/.ruff_cache
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete 2>/dev/null || true
	@echo "$(GREEN)Clean complete$(RESET)"

clean-all: clean ## Clean everything including node_modules and venv
	@echo "$(CYAN)Cleaning all dependencies...$(RESET)"
	rm -rf $(FRONTEND_DIR)/node_modules
	rm -rf $(BACKEND_DIR)/venv
	@echo "$(GREEN)Full clean complete$(RESET)"

# ============================================================================
# UTILITIES
# ============================================================================

shell-backend: ## Open Python shell with app context
	@echo "$(CYAN)Opening Python shell...$(RESET)"
	cd $(BACKEND_DIR) && python -c "from src.main import app; import code; code.interact(local=locals())"

api-docs: ## Open API documentation in browser
	@echo "$(CYAN)Opening API docs...$(RESET)"
	open http://localhost:8000/api/v1/docs 2>/dev/null || xdg-open http://localhost:8000/api/v1/docs 2>/dev/null || echo "Open http://localhost:8000/api/v1/docs in your browser"

seed: ## Seed database with sample data
	@echo "$(CYAN)Seeding database...$(RESET)"
	cd $(BACKEND_DIR) && python -m scripts.seed
	@echo "$(GREEN)Database seeded$(RESET)"

.PHONY: version
version: ## Show version information
	@echo "$(CYAN)Documentation Service Platform$(RESET)"
	@echo ""
	@echo "Backend:"
	@cd $(BACKEND_DIR) && python -c "import tomllib; print('  Version:', tomllib.load(open('pyproject.toml', 'rb'))['project']['version'])" 2>/dev/null || echo "  Version: unknown"
	@python --version 2>/dev/null | sed 's/^/  /'
	@echo ""
	@echo "Frontend:"
	@cd $(FRONTEND_DIR) && node -e "console.log('  Version:', require('./package.json').version)" 2>/dev/null || echo "  Version: unknown"
	@node --version 2>/dev/null | sed 's/^/  Node: /'
	@npm --version 2>/dev/null | sed 's/^/  npm: /'
