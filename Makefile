.PHONY: all clean
VENV := .venv/bin


clean:
	@echo "Cleaning up generated files..."
	rm -f prometheus_remote_writer/proto/*.py
	rm -rf .tox
	find . \( -name '*.pyc' -o -name '__pycache__' \) -exec rm -rf {} +
	rm -rf dist


test:
	$(VENV)/pytest tests/


release:
	@echo "Creating a new release..."
	$(VENV)/python scripts/release.py minor
