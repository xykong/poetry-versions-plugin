from unittest.mock import MagicMock

import pytest

from poetry_versions_plugin.utils import get_project_version


def test_get_version_from_tool_poetry():
    pyproject = MagicMock()
    pyproject.data = {
        "tool": {
            "poetry": {"version": "1.2.3"}
        }
    }
    assert get_project_version(pyproject) == "1.2.3"


def test_get_version_from_project_pep621():
    pyproject = MagicMock()
    pyproject.data = {
        "project": {"version": "2.0.0"}
    }
    assert get_project_version(pyproject) == "2.0.0"


def test_get_version_priority_pep621_over_tool():
    pyproject = MagicMock()
    pyproject.data = {
        "project": {"version": "2.0.0"},
        "tool": {"poetry": {"version": "1.0.0"}}
    }
    assert get_project_version(pyproject) == "2.0.0"


def test_get_version_from_both_sources():
    pyproject = MagicMock()
    pyproject.data = {
        "project": {"version": "3.0.0"},
        "tool": {"poetry": {"version": "1.5.0"}}
    }
    version = get_project_version(pyproject)
    assert version == "3.0.0"


def test_get_version_missing_raises_error():
    pyproject = MagicMock()
    pyproject.data = {}
    
    with pytest.raises(ValueError, match="Cannot find version in pyproject.toml"):
        get_project_version(pyproject)


def test_get_version_tool_without_poetry():
    pyproject = MagicMock()
    pyproject.data = {
        "tool": {"other": {"key": "value"}}
    }
    
    with pytest.raises(ValueError, match="Cannot find version in pyproject.toml"):
        get_project_version(pyproject)


def test_get_version_project_without_version():
    pyproject = MagicMock()
    pyproject.data = {
        "project": {"name": "test-project"}
    }
    
    with pytest.raises(ValueError, match="Cannot find version in pyproject.toml"):
        get_project_version(pyproject)


def test_get_version_converts_to_string():
    pyproject = MagicMock()
    pyproject.data = {
        "tool": {"poetry": {"version": 1.0}}
    }
    result = get_project_version(pyproject)
    assert result == "1.0"
    assert isinstance(result, str)
