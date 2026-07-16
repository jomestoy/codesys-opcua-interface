.PHONY: setup demo api web stop reset-demo test test-integration test-ui test-load lint build package-gateway screenshots backup restore

PYTHON ?= python

setup:
	$(PYTHON) -m pip install -e ".[test]"

demo:
	$(PYTHON) -m codesys_opcua_interface.demo --columns 200 --ticks 12
	@echo "API Hito 4: $(PYTHON) -m services.api.run"
	@echo "Web Hito 4: cd apps/web && npm install && npm run dev"

api:
	$(PYTHON) -m services.api.run

web:
	cd apps/web && npm run dev

stop:
	@echo "Demo local sin procesos persistentes en este prototipo."

reset-demo:
	@echo "Reset demo: no hay estado persistente en este hito."

test:
	$(PYTHON) -m pytest -q

test-integration:
	$(PYTHON) -m pytest -q tests

test-ui:
	@echo "Fuente React/Vite disponible en apps/web. Playwright queda pendiente para Hito 9."

test-load:
	$(PYTHON) -m codesys_opcua_interface.demo --columns 200 --ticks 30

lint:
	$(PYTHON) -m compileall codesys_opcua_interface tests

build:
	$(PYTHON) -m compileall codesys_opcua_interface tests

package-gateway:
	@echo "El gateway se empaqueta en el repositorio column-gateway."

screenshots:
	@echo "Pendiente hito UI."

backup:
	@echo "Pendiente hito base de datos."

restore:
	@echo "Pendiente hito base de datos."
