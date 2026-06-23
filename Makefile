PYTHON ?= python3.12

.PHONY: help bootstrap test lint format docker-build docker-smoke clean

help: ## Show this help.
	@awk 'BEGIN {FS = ":.*##"; printf "Targets:\n"} /^[a-zA-Z_-]+:.*##/ { printf "  %-20s %s\n", $$1, $$2 }' $(MAKEFILE_LIST)

bootstrap: ## Install package + dev extras + run pytest. Succeeds without Docker.
	@bash scripts/bootstrap_python_guard.sh
	python -m pip install -U pip
	pip install -e ".[dev]"
	@if [ -f .pre-commit-config.yaml ]; then \
		pre-commit install; \
	else \
		echo "pre-commit config not present yet (arrives with task-004)"; \
	fi
	pytest -q
	@if command -v docker >/dev/null 2>&1 && docker compose version >/dev/null 2>&1; then \
		echo "Docker available, run 'make docker-build' to build the image"; \
	else \
		echo "Docker not available; 'make bootstrap' succeeded without Docker image."; \
	fi

test: ## Run pytest with coverage report (cap=0 placeholder until task-002).
	pytest -q --cov=src/monte_carlo_risk --cov-fail-under=0

lint: ## Ruff check + format check + mypy.
	ruff check src tests
	ruff format --check src tests
	mypy src

format: ## Auto-fix lint issues and format code.
	ruff check --fix src tests
	ruff format src tests

docker-build: ## Build the docker image (best-effort; warns if Docker missing).
	@if command -v docker >/dev/null 2>&1 && docker compose version >/dev/null 2>&1; then \
		docker compose build; \
	else \
		echo "docker compose not installed; skipping 'docker-build'."; \
	fi

docker-smoke: ## Run a smoke check inside the docker container.
	@if command -v docker >/dev/null 2>&1 && docker compose version >/dev/null 2>&1; then \
		docker compose run --rm monte-carlo python -c "import monte_carlo_risk; print(monte_carlo_risk.__version__)"; \
	else \
		echo "docker compose not installed; skipping 'docker-smoke'."; \
	fi

clean: ## Remove caches and build artifacts.
	rm -rf .pytest_cache .mypy_cache .ruff_cache build dist *.egg-info src/*.egg-info
	find . -type d -name "__pycache__" -exec rm -rf {} +