.PHONY: all clean
VENV := .venv/bin


clean:
	@echo "Cleaning up generated files..."
	rm -rf .tox
	rm -rf .venv
	rm -rf .pytest_cache
	rm -rf dist
	find . \( -name '*.pyc' -o -name '__pycache__' \) -exec rm -rf {} +


test:
	$(VENV)/pytest tests/


release:
	@echo "Creating a new release..."
	$(VENV)/poetry run release patch
