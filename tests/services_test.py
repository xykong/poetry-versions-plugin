import subprocess
from datetime import datetime
from unittest.mock import MagicMock, patch

import pytest

from poetry_versions_plugin.services import update_readme, update_py_file, get_git_info


@pytest.fixture
def mock_repo():
    """Mock the git.Repo object."""
    with patch('git.Repo') as MockRepo:
        mock_repo = MagicMock()
        MockRepo.return_value = mock_repo
        yield mock_repo


def test_get_git_info(mock_repo):
    """Test get_git_info function with mocked git repo."""
    # Setup mock values
    mock_repo.active_branch.name = 'main'
    mock_repo.head.commit.hexsha = 'abcdefg1234567'
    mock_repo.iter_commits.return_value = range(42)  # Simulate 42 commits
    mock_repo.is_dirty.return_value = False

    # Call the function to test
    info = get_git_info()

    # Assertions
    assert info['branch'] == 'main'
    assert info['commit'] == 'abcdefg'  # Only the first 7 characters
    assert info['commit_count'] == 42
    assert not info['is_dirty']
    assert 'datetime' in info  # Check if the datetime key exists


def test_get_git_info_dirty_repo(mock_repo):
    """Test get_git_info function with a dirty repo."""
    mock_repo.is_dirty.return_value = True

    info = get_git_info()

    assert info['is_dirty']


def test_get_git_info_no_commits(mock_repo):
    """Test get_git_info function with no commits."""
    mock_repo.iter_commits.return_value = iter([])  # No commits

    info = get_git_info()

    assert info['commit_count'] == 0


def test_get_git_info_on_current_repo():
    """Test get_git_info function on the current Git repository."""

    info = get_git_info()

    # Get the current branch name using Git command line
    current_branch = subprocess.check_output(
        ["git", "rev-parse", "--abbrev-ref", "HEAD"]
    ).strip().decode('utf-8')

    # Get the latest commit hash (short version)
    latest_commit = subprocess.check_output(
        ["git", "rev-parse", "--short", "HEAD"]
    ).strip().decode('utf-8')

    # Get the total number of commits on the current branch
    commit_count = int(subprocess.check_output(
        ["git", "rev-list", "--count", current_branch]
    ).strip())

    # Check if the repo is dirty
    is_dirty = bool(subprocess.call(["git", "diff", "--quiet"]) != 0)

    # Get the current date and time
    current_datetime = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # Assertions
    assert info['branch'] == current_branch
    assert info['commit'] == latest_commit
    assert info['commit_count'] == commit_count
    assert info['is_dirty'] == is_dirty
    assert info['datetime'][:16] == current_datetime[:16]  # Compare up to minutes


# def test_git_repo_is_not_dirty():
#     """Test to ensure the repository is clean (no uncommitted changes)."""
#
#     # Ensure the repository is clean
#     assert subprocess.call(["git", "diff", "--quiet"]) == 1
#
#     # Verify the function reflects this state
#     info = get_git_info()
#     assert not info['is_dirty']


# def test_git_repo_is_dirty():
#     """Test to ensure the repository reflects a dirty state when changes are made."""
#     # Make a temporary modification
#     with open("temporary_test_file.txt", "w") as f:
#         f.write("This is a temporary file for testing dirty state.")
#
#     try:
#         # Verify the function reflects this state
#         info = get_git_info()
#
#         print('info:', info)
#
#         assert info['is_dirty']
#     finally:
#         # Clean up: remove the temporary file
#         subprocess.call(["git", "checkout", "--", "temporary_test_file.txt"])


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


def test_update_readme(tmp_path, git_info):
    """Test if the update_readme function correctly replaces placeholders."""
    readme_content = """# Project

Branch: <!-- BRANCH -->
Commit: <!-- COMMIT -->
Commit Count: <!-- COMMIT_COUNT -->
Dirty: <!-- IS_DIRTY -->
Date: <!-- DATETIME -->
"""
    expected_content = """# Project

Branch: main
Commit: abcdefg
Commit Count: 42
Dirty: False
Date: 2023-10-05 10:00:00
"""
    readme_path = tmp_path / "README.md"
    readme_path.write_text(readme_content)

    update_readme(readme_path, git_info)

    assert readme_path.read_text() == expected_content


def test_update_py_file(tmp_path, git_info):
    """Test if the update_py_file function correctly generates a Python file."""
    py_path = tmp_path / "version_info.py"

    update_py_file(py_path, git_info, lambda line: None)

    assert 'branch' in py_path.read_text().strip()
    assert 'commit' in py_path.read_text().strip()
    assert 'is_dirty' in py_path.read_text().strip()
    assert 'datetime' in py_path.read_text().strip()
