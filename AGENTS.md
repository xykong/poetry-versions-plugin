# AGENTS.md - Poetry Versions Plugin Development Guide

This guide provides essential information for AI coding agents working on the Poetry Versions Plugin codebase.

## Project Overview

A Poetry plugin that automates version management and records Git information for Python projects. The plugin hooks into Poetry's version command to update version files and commit changes automatically.

## Build, Lint, and Test Commands

### Testing
```bash
# Run all tests
poetry run pytest

# Run tests via Makefile
make test

# Run a specific test file
poetry run pytest tests/services_test.py

# Run a specific test function
poetry run pytest tests/services_test.py::test_get_git_info

# Run with verbose output
poetry run pytest -v

# Run tests across multiple Python versions
tox
```

### Build and Release
```bash
# Build the package (dry run)
poetry build --dry-run

# Build the package
poetry build

# Bump version (updates pyproject.toml and configured files)
poetry version [major|minor|patch]

# Run the release script
poetry run release [major|minor|patch]
make release  # Uses 'patch' by default
```

### Development
```bash
# Install dependencies
poetry install

# Clean build artifacts
make clean

# Run commands in the virtual environment
poetry run <command>
```

## Code Style Guidelines

### Import Organization
1. **Standard library imports** (alphabetical)
2. **Third-party imports** (alphabetical)
3. **Local/project imports** (alphabetical)
4. Blank line between each group

Example from `plugin.py`:
```python
import re

from cleo.events import console_events
from cleo.events.console_command_event import ConsoleCommandEvent
from cleo.events.event_dispatcher import EventDispatcher
from cleo.io.io import IO
from cleo.io.outputs.output import Verbosity
from poetry.console.application import Application
from poetry.console.commands.version import VersionCommand
from poetry.plugins.application_plugin import ApplicationPlugin
from poetry.plugins.plugin import Plugin
from poetry.poetry import Poetry

from poetry_versions_plugin import PLUGIN_NAME
from poetry_versions_plugin.services import get_git_info, update_pyproject, update_py_file
from poetry_versions_plugin.services import update_readme, commit_local_changes
from poetry_versions_plugin.utils import pyproject_get, wrap_write_line
```

### Naming Conventions
- **Functions**: `snake_case` (e.g., `get_git_info`, `update_py_file`)
- **Classes**: `PascalCase` (e.g., `VersionsPlugin`, `VersionsApplicationPlugin`)
- **Constants**: `UPPER_SNAKE_CASE` (e.g., `PLUGIN_NAME`)
- **Private functions**: Prefix with `_` (not extensively used in this codebase)

### Type Hints
- Type hints are **NOT extensively used** in this codebase
- When adding new code, match the existing style (no type hints)
- Parameter documentation is done via docstrings instead

### Docstrings
- Use triple-quoted strings (`"""`)
- Include parameter descriptions using `:param name: description` format
- Include return type with `:return: description`
- Include raises information with `:raises: exception`

Example:
```python
def update_readme(readme_path, info, dry_run=False):
    """
    Update placeholders in the README.md file with Git information.

    :param readme_path: Path to the README.md file
    :param info: Dictionary containing Git information
    :param dry_run: If True, print what would be changed instead of modifying the file
    """
```

### Error Handling
- Use try-except blocks with specific exception types
- Raise meaningful exceptions with descriptive messages
- Use `ValueError` for invalid values, `FileNotFoundError` for missing files

Example:
```python
try:
    repo.index.commit(commit_message)
    print(f"Changes committed with message: '{commit_message}'")
except Exception as e:
    print(f"Failed to commit changes: {e}")
    raise
```

### Code Patterns

#### Git Operations
- Use `gitpython` library (`git.Repo`)
- Always handle dirty repository state
- Check for uncommitted changes before operations

#### File Operations
- Check if directories exist before creating files
- Use context managers (`with open()`) for file operations
- Support `dry_run` mode for testing without side effects

#### Plugin Integration
- Use Poetry's event system (`console_events.COMMAND`, `console_events.TERMINATE`)
- Use `Verbosity` levels for output control
- Inject helper functions via decorators (`@wrap_write_line`)

### String Formatting
- Prefer f-strings for string formatting: `f"Version: {version}"`
- Use `.format()` for user-configurable templates: `commit_message.format(current_version=x, new_version=y)`

### Comments
- Use `#` for inline comments
- Comment `noinspection` for PyCharm/IDE-specific warnings
- Commented-out test code should be removed or enabled

### Line Length
- No strict line length limit enforced
- Keep lines readable (generally under 120 characters)

## Testing Guidelines

### Test Structure
- Test files named `<module>_test.py` (e.g., `services_test.py`)
- Use pytest fixtures for reusable test data
- Mock external dependencies (Git operations, file I/O)

### Fixtures
```python
@pytest.fixture
def git_info():
    """Provide a sample Git information dictionary for testing."""
    return {
        "branch": "main",
        "commit": "abcdefg",
        "commit_count": 42,
        "is_dirty": False,
        "datetime": "2023-10-05 10:00:00"
    }
```

### Mocking
- Use `unittest.mock` for mocking: `@patch('git.Repo')`
- Use `MagicMock` for complex mock objects
- Mock at the import level, not at the test level

## Project Structure

```
poetry-versions-plugin/
├── poetry_versions_plugin/   # Main plugin code
│   ├── __init__.py           # Plugin name constant
│   ├── plugin.py             # Plugin classes and event handlers
│   ├── services.py           # Core business logic (Git, file updates)
│   ├── utils.py              # Helper functions and decorators
│   └── versions.py           # Generated version info file
├── scripts/                  # Utility scripts
│   └── release.py            # Release automation script
├── tests/                    # Test suite
│   ├── services_test.py      # Tests for services module
│   ├── poetry_test.py        # Tests for Poetry integration
│   └── release_test.py       # Tests for release script
├── pyproject.toml            # Poetry configuration
├── Makefile                  # Build automation
└── tox.ini                   # Multi-version testing config
```

## Key Behavioral Patterns

### Version Bumping Flow
1. User runs `poetry version [major|minor|patch]`
2. `before_version_command` event captures current version and Git info
3. Poetry updates version in `pyproject.toml`
4. `after_version_command` event triggers plugin actions:
   - Update `[tool.versions]` section in `pyproject.toml`
   - Update configured Python files (e.g., `versions.py`)
   - Update README.md placeholders (if configured)
   - Commit changes if conditions are met

### Commit Conditions
All must be true for automatic commit:
- `commit = true` in settings
- Version argument in `commit_on_argument` list
- Current branch matches `commit_on_branches` regex patterns
- Repository is clean OR `allow_dirty = true`

## Configuration Reference

In `pyproject.toml`:
```toml
[tool.versions.settings]
allow_dirty = false                          # Allow dirty repo for version bump
commit = true                                # Auto-commit changes
commit_on_argument = ["major", "minor", "patch"]  # Which version types trigger commit
commit_on_branches = ["release/.*"]          # Branch regex patterns for auto-commit
commit_message = "Bump version: {current_version} → {new_version}"
filename = ["poetry_versions_plugin/versions.py"]  # Additional files to update
```

## Important Notes for Agents

1. **Never suppress type errors** with `# type: ignore` or similar
2. **Match existing patterns**: This codebase doesn't use type hints heavily
3. **Test with mocks**: Git operations should be mocked in tests
4. **Dry-run support**: New file-writing functions should support `dry_run` parameter
5. **Verbosity control**: Use `Verbosity` enum for console output
6. **Git flow**: Release process uses git-flow (develop → release → master)
7. **Python compatibility**: Support Python 3.9+ (see `pyproject.toml`)

## Common Development Tasks

### Adding a new file update handler
1. Add function to `services.py` with signature `(file_path, info, write_line=None, dry_run=False)`
2. Update `after_version_command` in `plugin.py` to call your handler
3. Add tests to `tests/services_test.py`
4. Support dry-run mode for testing

### Modifying Git info structure
1. Update `get_git_info()` in `services.py`
2. Update all consumers: `update_pyproject`, `update_py_file`, `update_readme`
3. Update tests to reflect new structure
4. Update `[tool.versions]` schema in documentation

### Debugging plugin behavior
- Use `--verbose` or `-vv` flags with Poetry commands
- Check `write_line()` output for plugin lifecycle events
- Test with `--dry-run` to avoid unwanted commits
