PYTHON ?= python

.PHONY: install verify test doctor demo

install:
	$(PYTHON) -m pip install -e ".[dev]"

test:
	pytest -q

verify:
	$(PYTHON) -m compileall -q src scripts
	pytest -q
	$(PYTHON) scripts/check_release.py

doctor:
	$(PYTHON) scripts/doctor.py --config config/user-config.json

demo:
	$(PYTHON) scripts/run_demo.py
