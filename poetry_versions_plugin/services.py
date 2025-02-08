import os
from datetime import datetime

import git


def get_git_info(version=None):
    """
    Retrieve information about the current Git repository, including branch name,
    short SHA of the latest commit, total number of commits, whether there are uncommitted changes,
    and the current date and time.
    """
    repo = git.Repo(search_parent_directories=True)
    branch = repo.active_branch.name
    commit = repo.head.commit.hexsha[:7]
    commit_count = sum(1 for _ in repo.iter_commits(branch))
    is_dirty = repo.is_dirty()
    current_datetime = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    return {
        "branch": branch,
        "commit": commit,
        "commit_count": commit_count,
        "is_dirty": is_dirty,
        "datetime": current_datetime,
        "version": version
    }


def update_readme(readme_path, info, dry_run=False):
    """
    Update placeholders in the README.md file with Git information.

    :param readme_path: Path to the README.md file
    :param info: Dictionary containing Git information
    :param dry_run: If True, print what would be changed instead of modifying the file
    """
    # Open the README file and read its content
    with open(readme_path, 'r') as f:
        content = f.read()

    # Replace placeholders with actual info
    new_content = content.replace("<!-- BRANCH -->", info['branch'])
    new_content = new_content.replace("<!-- COMMIT -->", info['commit'])
    new_content = new_content.replace("<!-- COMMIT_COUNT -->", str(info['commit_count']))
    new_content = new_content.replace("<!-- IS_DIRTY -->", str(info['is_dirty']))
    new_content = new_content.replace("<!-- DATETIME -->", info['datetime'])

    if dry_run:
        # If dry_run is True, print what would be changed
        print(f"Would update {readme_path} with the following changes:")
        print(new_content)
    else:
        # If not a dry run, write changes to the file
        with open(readme_path, 'w') as f:
            f.write(new_content)


def update_py_file(py_path, info, dry_run=False):
    """
    Create or update a Python file with Git information.

    :param py_path: Path to the Python file
    :param info: Dictionary containing Git information
    :param dry_run: If True, print what would be done instead of making changes
    """
    # Get the directory path
    dir_path = os.path.dirname(py_path)

    # Check if the directory exists, create it if not
    if not os.path.exists(dir_path):
        if dry_run:
            print(f"Would create directory: {dir_path}")
        else:
            os.makedirs(dir_path, exist_ok=True)

    # Prepare the content to write
    content = "# THIS FILE IS GENERATED DURING PROJECT BUILD\n"
    content += "# See poetry poetry-versions-plugin for details\n\n"

    for key, value in info.items():
        # Format output based on the type of value
        if isinstance(value, str):
            content += f"{key} = '{value}'\n"
        else:
            content += f"{key} = {value}\n"

    content += "\n"
    content += "full_version = f'{version}.{branch}+{commit_count}.{commit}'\n"
    content += "# END OF GENERATED CODE\n"

    if dry_run:
        print(f"Would write to file: {py_path}")
        print("File content would be:")
        print(content)
    else:
        with open(py_path, 'w') as f:
            f.write(content)


def update_pyproject(info, pyproject, io, dry_run=False):
    """
    Update the pyproject.toml file with Git information and version number.

    :param info: Dictionary containing Git information
    :param pyproject: The poetry pyproject command object
    :param io: The input/output interface for logging messages
    :param dry_run: If True, skip the actual file write
    :return: None
    """

    # Update pyproject.toml
    try:
        if 'versions' not in pyproject.data['tool']:
            pyproject.data['tool']['versions'] = {}

        versions = pyproject.data['tool']['versions']

        # Loop through the info dictionary and update each field
        for key, value in info.items():
            versions[key] = value
    except KeyError as ex:
        io.write_line(f'Error parsing pyproject: {ex}')
        return

    # Save the updates
    if dry_run:
        io.write_line('dry-run mode, skip updating pyproject.toml')
    else:
        pyproject.save()


def commit_local_changes(repo_path, commit_message):
    """
    Commit local changes in the specified Git repository.

    :param repo_path: Path to the local Git repository.
    :param commit_message: Commit message to use.
    :raises: ValueError if there are no changes to commit.
    """

    # Ensure the repository path exists
    if not os.path.exists(repo_path):
        raise FileNotFoundError(f"The specified repository path does not exist: {repo_path}")

    # Initialize the repository
    repo = git.Repo(repo_path)

    # Check for uncommitted changes
    if not repo.is_dirty(untracked_files=True):
        raise ValueError("No changes to commit.")

    # Stage all changes
    repo.git.add(update=True)

    # Include new untracked files
    repo.git.add(A=True)

    # Commit the changes
    try:
        repo.index.commit(commit_message)
        print(f"Changes committed with message: '{commit_message}'")
    except Exception as e:
        print(f"Failed to commit changes: {e}")
        raise
