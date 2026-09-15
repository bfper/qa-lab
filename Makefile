.DEFAULT_GOAL := help
COMPOSE := docker compose --env-file .env -f docker/docker-compose.yml

help: ## Show this help
	@grep -E '^[a-zA-Z_-]+:.*?## ' $(MAKEFILE_LIST) | \
		awk 'BEGIN{FS=":.*?## "}{printf "  \033[36m%-14s\033[0m %s\n", $$1, $$2}'

setup: ## Create the venv and install dependencies
	python3 -m venv .venv
	.venv/bin/pip install --upgrade pip
	.venv/bin/pip install -r requirements.txt
	@test -f .env || cp .env.example .env
	@echo "Now: source .venv/bin/activate"
	@echo "Then: make hooks   (before your first commit)"

hooks: ## Install the pre-commit guard (run once, before first commit)
	./scripts/install-hooks.sh

unit: ## Week 1 — scope rules, no containers
	pytest tests/unit -m unit

up: ## Start the lab stack (auth + mentoria + postgres)
	$(COMPOSE) up -d --build
	@echo "auth      -> http://localhost:18001"
	@echo "mentoria  -> http://localhost:18002"
	@echo "postgres  -> localhost:15432"

down: ## Stop the stack, keep the data
	$(COMPOSE) down

nuke: ## Stop the stack and destroy its volume
	$(COMPOSE) down -v

logs: ## Tail all service logs
	$(COMPOSE) logs -f

e2e: ## Weeks 2-3 — browser tests
	pytest tests/e2e -m e2e --tracing=retain-on-failure

api: ## Week 5 — HTTP-level tests
	pytest tests/api -m api

data: ## Week 6 — database oracles
	pytest tests/data -m data

all: ## Full suite, the way CI runs it
	pytest

flaky: ## Run the suite five times; any failure means flakiness
	@for i in 1 2 3 4 5; do echo "--- run $$i ---"; pytest -q || exit 1; done
	@echo "five clean runs"

.PHONY: help setup hooks unit up down nuke logs e2e api data all flaky
