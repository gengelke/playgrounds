# ==========================================
# Configuration
# ==========================================

VENV           := .venv
PIP            := $(VENV)/bin/pip
PYTHON         := $(VENV)/bin/python3
PYTEST         := $(VENV)/bin/pytest
UVICORN        := $(VENV)/bin/uvicorn
EMPLOYEECLI    := $(VENV)/bin/employee-cli
PID_FILE       := .fastapi.pid
API_URL        ?= http://127.0.0.1:8000
DEPS_STAMP     := $(VENV)/.deps-installed
DOCKER_COMPOSE ?= docker compose
MODE           ?= bare

.PHONY: all
all: workflow

.PHONY: check-mode
check-mode:
	@case "$(MODE)" in \
		bare|docker) ;; \
		*) echo "Invalid MODE='$(MODE)'. Use MODE=bare or MODE=docker."; exit 2 ;; \
	esac

# ==========================================
# Workflows
# ==========================================

.PHONY: workflow
workflow: deps
	@set -e; \
	$(MAKE) up MODE=$(MODE); \
	trap '$(MAKE) down MODE=$(MODE)' EXIT; \
	$(MAKE) codegen MODE=$(MODE); \
	$(MAKE) install; \
	PYTHONPATH=. $(PYTEST) -v; \
	$(PYTHON) example_client.py

.PHONY: up down codegen
up: check-mode _up-$(MODE)
down: check-mode _down-$(MODE)
codegen: check-mode _codegen-$(MODE)

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

.PHONY: install
install: deps
	$(PIP) install -e . --no-build-isolation

# ==========================================
# Run FastAPI (bare)
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
# Mode implementations
# ==========================================

.PHONY: _up-bare _down-bare _codegen-bare
_up-bare: run-bg

_down-bare: stop

_codegen-bare: deps
	bash library-builder/generate-client.sh

.PHONY: _up-docker _down-docker _codegen-docker
_up-docker:
	$(DOCKER_COMPOSE) up --build -d fastapi

_down-docker:
	$(DOCKER_COMPOSE) down

_codegen-docker:
	$(DOCKER_COMPOSE) run --rm codegen

# ==========================================
# Test, example, CLI
# ==========================================

.PHONY: test
test: deps
	@set -e; \
	$(MAKE) up MODE=$(MODE); \
	trap '$(MAKE) down MODE=$(MODE)' EXIT; \
	$(MAKE) codegen MODE=$(MODE); \
	$(MAKE) install; \
	PYTHONPATH=. $(PYTEST) -v

.PHONY: example
example: deps
	$(PYTHON) example_client.py

.PHONY: cli-list
cli-list: deps
	$(EMPLOYEECLI) list

# ==========================================
# Clean
# ==========================================

.PHONY: clean
clean: check-mode
	$(MAKE) down MODE=$(MODE)
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type f \( -name "*.pyc" -o -name "*.pyo" -o -name "*.un~" \) -delete
	rm -rf generated_client dist *.egg-info .pytest_cache .mypy_cache htmlcov
	rm -f .fastapi.log .coverage $(DEPS_STAMP) schema.graphql schema.json

.PHONY: distclean
distclean: clean
	rm -rf $(VENV)
	rm -f *.sqlite *.db

# ==========================================
# Help
# ==========================================

.PHONY: help
help:
	@echo ""
	@echo "Mode-driven lifecycle (MODE=bare|docker, default bare):"
	@echo "  make up MODE=bare|docker       start API"
	@echo "  make codegen MODE=bare|docker  regenerate GraphQL client"
	@echo "  make down MODE=bare|docker     stop API/services"
	@echo "  make workflow MODE=bare|docker full workflow: up, codegen, test, example"
	@echo "  make test MODE=bare|docker     run pytest (manages lifecycle automatically)"
	@echo ""
	@echo "Bare-mode helpers:"
	@echo "  make run            start FastAPI in foreground (bare only)"
	@echo "  make run-bg         start FastAPI in background (bare only)"
	@echo "  make stop           stop background FastAPI (bare only)"
	@echo "  make example        run example client"
	@echo "  make cli-list       list employees via CLI"
	@echo ""
	@echo "Cleanup (mode aware):"
	@echo "  make clean MODE=bare|docker"
	@echo "  make distclean MODE=bare|docker"
	@echo ""
	@echo "Legacy default:"
	@echo "  make                same as make workflow MODE=bare"
