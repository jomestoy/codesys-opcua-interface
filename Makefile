.PHONY: setup demo demo-offline api web stop reset-demo test test-integration test-ui test-load lint build package-gateway screenshots backup restore

PYTHON ?= python
COMPOSE ?= docker compose -f docker-compose.demo.yml
GATEWAY_REPO ?= ../column-gateway

setup:
	$(PYTHON) -m pip install -e ".[test]"

demo:
	$(COMPOSE) up --build

demo-offline:
	$(PYTHON) -m codesys_opcua_interface.demo --columns 200 --ticks 12
	@echo "API offline: $(PYTHON) -m services.api.run"
	@echo "Web offline: cd apps/web && npm install && npm run dev"

api:
	$(PYTHON) -m services.api.run

web:
	cd apps/web && npm run dev

stop:
	$(COMPOSE) down

reset-demo:
	$(COMPOSE) down -v
	$(COMPOSE) up --build

test:
	$(PYTHON) -m pytest -q

test-integration:
	$(PYTHON) -m pytest -q tests

test-ui:
	@echo "Fuente React/Vite disponible en apps/web. Playwright queda pendiente para Hito 9."

test-load:
	$(PYTHON) -m codesys_opcua_interface.demo --columns 200 --ticks 30

lint:
	$(PYTHON) -m compileall codesys_opcua_interface services tests scripts

build:
	$(PYTHON) -m compileall codesys_opcua_interface services tests scripts

package-gateway:
	cd $(GATEWAY_REPO) && $(PYTHON) scripts/package.py

screenshots:
	@echo "Pendiente hito UI."

backup:
	$(PYTHON) scripts/backup_demo.py

restore:
	$(PYTHON) scripts/restore_demo.py $(BACKUP)
