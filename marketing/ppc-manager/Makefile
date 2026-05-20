# ppc-manager plugin — development tasks
#
# Usage:
#   make install      Install Python dependencies into a local dev venv
#   make test         Run unit + lint + manifest tests (default; no network)
#   make test-live    Run live integration tests (requires PPC_MANAGER_LIVE_TESTS=1)
#   make lint         Run skill-lint and manifest validation only
#   make coverage     Run pytest with coverage report
#   make clean        Remove dev venv and caches

VENV := .venv
PYTHON := $(VENV)/bin/python
PIP := $(VENV)/bin/pip
PYTEST := $(VENV)/bin/pytest

.PHONY: install test test-live lint coverage clean

$(VENV):
	python3 -m venv $(VENV)
	$(PIP) install --upgrade pip

install: $(VENV)
	$(PIP) install -r requirements-dev.txt

test: install
	$(PYTEST) tests/unit tests/lint tests/integration -k "not live" -v

test-live: install
	PPC_MANAGER_LIVE_TESTS=1 $(PYTEST) tests/integration -k "live" -v

lint: install
	$(PYTEST) tests/lint -v

coverage: install
	$(PYTEST) --cov=scripts/lib --cov=mcp_servers --cov-report=term-missing --cov-report=html tests/unit tests/lint

clean:
	rm -rf $(VENV) .pytest_cache .coverage htmlcov
	find . -type d -name __pycache__ -exec rm -rf {} +
