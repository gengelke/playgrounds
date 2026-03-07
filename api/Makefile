# ==========================================
# Configuration
# ==========================================

VENV := .venv
PIP := $(VENV)/bin/pip
PYTHON := $(VENV)/bin/python3
PYTEST := $(VENV)/bin/pytest
UVICORN := $(VENV)/bin/uvicorn
EMPLOYEECLI := $(VENV)/bin/employee-cli
PID_FILE := .fastapi.pid
API_URL ?= http://127.0.0.1:8000
DEPS_STAMP := $(VENV)/.deps-installed
DOCKER_COMPOSE ?= docker compose

.PHONY: all
all: all-local

.PHONY: all-local
all-local:
	@set -e; \
		$(MAKE) run-bg; \
		trap '$(MAKE) stop' EXIT; \
		$(MAKE) codegen; \
		$(MAKE) install; \
		$(MAKE) test; \
		$(MAKE) example

.PHONY: all-docker
all-docker:
	$(MAKE) run-docker
	$(MAKE) codegen-docker

# ==========================================
# Setup
# ==========================================

.PHONY: venv
venv:
	@if [ ! -x "$(PIP)" ] || ! "$(PIP)" --version >/dev/null 2>&1; then rm -rf "$(VENV)"; python3 -m venv "$(VENV)"; fi

$(DEPS_STAMP): | venv
	$(PIP) install --upgrade pip
	$(PIP) install "setuptools>=61" wheel
	$(PIP) install pydantic httpx fastapi uvicorn strawberry-graphql
	$(PIP) install pytest pytest-asyncio ariadne-codegen
	touch $(DEPS_STAMP)

.PHONY: deps
deps: $(DEPS_STAMP)

# ==========================================
# Install project
# ==========================================

.PHONY: install
install: deps
	$(PIP) install -e . --no-build-isolation

# ==========================================
# Run FastAPI
# ==========================================

.PHONY: run
run: deps
	$(UVICORN) --app-dir fastapi main:app --host 127.0.0.1 --port 8000

.PHONY: run-bg
run-bg: deps stop
	$(UVICORN) --app-dir fastapi main:app --host 127.0.0.1 --port 8000 > .fastapi.log 2>&1 & echo $$! > $(PID_FILE)
	@echo "FastAPI started with PID $$(cat $(PID_FILE))"
	@for i in $$(seq 1 30); do \
		if curl -fsS $(API_URL)/docs >/dev/null 2>&1; then \
			echo "FastAPI is ready at $(API_URL)"; \
			exit 0; \
		fi; \
		sleep 1; \
	done; \
	echo "FastAPI did not become ready in time."; \
	$(MAKE) stop; \
	exit 1

.PHONY: stop
stop:
	@if [ -f "$(PID_FILE)" ]; then \
		PID=$$(cat $(PID_FILE)); \
		if kill -0 $$PID >/dev/null 2>&1; then \
			kill $$PID; \
			echo "Stopped FastAPI (PID $$PID)"; \
		fi; \
			rm -f $(PID_FILE); \
		fi

# ==========================================
# Docker mode (legacy/original style)
# ==========================================

.PHONY: run-docker
run-docker:
	$(DOCKER_COMPOSE) up --build -d fastapi

.PHONY: build
build: run-docker

.PHONY: codegen-docker
codegen-docker:
	$(DOCKER_COMPOSE) run --rm codegen

.PHONY: stop-docker
stop-docker:
	$(DOCKER_COMPOSE) down

# ==========================================
# Regenerate GraphQL client
# ==========================================

.PHONY: codegen
codegen: deps
	bash library-builder/generate-client.sh

# ==========================================
# Run pytest
# ==========================================

.PHONY: test
test: deps
	$(PYTEST) -v

# ==========================================
# Run CLI
# ==========================================

.PHONY: cli-list
cli-list: deps
	$(EMPLOYEECLI) list

# ==========================================
# Run example
# ==========================================

.PHONY: example
example: deps
	$(PYTHON) example_client.py

# ==========================================
# Clean build artifacts
# ==========================================

.PHONY: clean
clean: stop
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.pyo" -delete
	find . -type f -name "*.un~" -delete
	rm -rf generated_client
	rm -rf dist
	rm -rf *.egg-info
	rm -rf .pytest_cache
	rm -rf .mypy_cache
	rm -rf htmlcov
	rm -rf .coverage
	rm -f .fastapi.log
	rm -f $(DEPS_STAMP)
	rm -f schema.graphql schema.json


# ==========================================
# Dist clean (full reset: includes DB + venv)
# ==========================================

.PHONY: distclean
distclean: clean
	rm -rf $(VENV)
	rm -f *.sqlite
	rm -f *.db

.PHONY: dist-clean
dist-clean: distclean

.PHONY: clean-docker
clean-docker:
	$(DOCKER_COMPOSE) down --rmi local --volumes --remove-orphans

# ==========================================
# Show help
# ==========================================

.PHONY: help
help:
	@echo ""
	@echo "Available targets:"
	@echo ""
	@echo "make venv        - create virtual environment"
	@echo "make install     - install project (editable)"
	@echo "make all-local   - full local workflow (without Docker)"
	@echo "make all-docker  - start Docker API + run Docker codegen"
	@echo "make run         - start FastAPI server in foreground"
	@echo "make run-bg      - start FastAPI server in background"
	@echo "make stop        - stop background FastAPI server"
	@echo "make codegen     - regenerate GraphQL client"
	@echo "make run-docker  - start FastAPI with Docker"
	@echo "make build       - alias for run-docker (legacy)"
	@echo "make codegen-docker - regenerate GraphQL client in Docker"
	@echo "make stop-docker - stop Docker services"
	@echo "make test        - run pytest"
	@echo "make example     - run example client"
	@echo "make cli-list    - run CLI to list employees"
	@echo "make clean       - remove build artifacts"
	@echo "make distclean   - remove artifacts + venv + sqlite db"
	@echo "make dist-clean  - alias for distclean"
	@echo "make clean-docker - remove Docker containers/images/volumes"
	@echo ""
