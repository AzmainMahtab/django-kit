.PHONY: help up down logs shell migrate makemigrations superuser lint format test test-fast

MANAGE = uv run python backend/manage.py
ARGS ?=
MSG ?= auto

help: ## Show this help menu
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-18s\033[0m %s\n", $$1, $$2}'

# ==========================================
# DOCKER
# ==========================================

up: ## Start the full stack (web, celery, beat, flower, postgres, redis)
	docker compose up --build -d

down: ## Stop the stack
	docker compose down

logs: ## Tail the web service logs
	docker compose logs -f web

shell: ## Open a Django shell in the web container
	docker compose exec web python backend/manage.py shell

# ==========================================
# DATABASE
# ==========================================

migrate: ## Apply migrations
	$(MANAGE) migrate

makemigrations: ## Create migrations (usage: make makemigrations MSG="add order table")
	$(MANAGE) makemigrations --name $(MSG)

superuser: ## Create a Django superuser
	$(MANAGE) createsuperuser

# ==========================================
# STATIC ANALYSIS
# ==========================================

lint: ## Run ruff, format check, mypy, and the import-linter contracts
	uv run ruff check .
	uv run ruff format --check .
	uv run mypy backend
	uv run lint-imports

format: ## Auto-fix lint findings and format the tree
	uv run ruff check . --fix
	uv run ruff format .

# ==========================================
# TESTS
# ==========================================

test: ## Run the full test suite (usage: make test ARGS="-k test_login")
	uv run pytest $(ARGS)

test-fast: ## Run tests, stopping at the first failure
	uv run pytest -x -q $(ARGS)
