# Poetry Versions Plugin

License

## Overview

The Poetry Versions Plugin is a powerful extension for the Poetry dependency manager, designed to automate version
management and record Git information for Python projects.
This plugin simplifies the process of bumping version numbers
and integrates seamlessly with Git to ensure that all changes are tracked effectively.

## Features

- **Automated Version Management**: Easily bump major, minor, or patch versions using the `poetry version` command.
- **Git Integration**: Automatically records Git branch, commit, and status information within your project.
- **Customizable Workflow**: Configure commit message formats, allow/disallow dirty repository states, and specify which
  files to update.
- **Release Process Automation**: Provides a script to handle releases using git flow, ensuring a streamlined and
  consistent release process.

## Installation

To install the Poetry Versions Plugin, add it to your Poetry project:

```bash
poetry add poetry-versions-plugin
```

Poetry will automatically recognize the plugin without needing additional configuration in your `pyproject.toml`.

## Configuration

Configure the plugin in your `pyproject.toml` file under the `[tool.versions.settings]` section:

```toml
[tool.versions.settings]
allow_dirty = false
commit = true
commit_on = ["major", "minor", "patch"]
commit_message = "Bump version: {current_version} → {new_version}"
filename = [
    "poetry_versions_plugin/versions.py",
]
```

### Main Configuration Options

allow_dirty: (default: false) If set to true, allows the version bumping even if the working directory has uncommitted
changes.
commit: (default: true) Automatically commit changes to the local git repository after a version bump.
commit_on: Specifies which version types (major, minor, patch) trigger an automatic commit.
commit_message: Format of the commit message for version bumps.
filename: List of additional files to update with the new version information.

## Usage

### Bumping Versions

To bump the version of your project, use the `poetry version` command with the desired version type:

```bash
poetry version [major|minor|patch]
```

This command updates the version in your `pyproject.toml`, updates additional specified files, and commits changes if
configured.

### Release Process

The `scripts.release:main` script automates the release process using git flow.
To execute a release:

```bash
poetry run release [major|minor|patch]
```

This script performs the following steps:

1. Checks if you're on the `develop` branch.
2. Verifies there are no uncommitted changes.
3. Bumps the version number.
4. Starts and finishes a git flow release.
5. Publishes the package.

#### Customizing the Release Process with a Makefile

You can also customize the release process using a Makefile. Here is an example:

```makefile
bump = patch
next-version = $(shell poetry version $(bump) -s --dry-run)
release:
	@echo "Creating a new release..."
	git flow release start $(next-version)
	poetry version $(bump)
	git flow release finish -m "publish"
	git push --all
	git push --tags
```

This Makefile example automates the version bumping and release process by leveraging `git flow` and Poetry commands.

#### Notes

The release script requires git flow to be installed and initialized in your repository.
Ensure your repository is clean and on the correct branch before starting a release.

## Testing

This project uses `pytest` for unit testing.
To run tests:

```bash
poetry run pytest
```

## License

This project is licensed under the Apache License 2.0. See the LICENSE file for details.

## Contribution

We welcome contributions to the Poetry Versions Plugin!
If you have suggestions, bug reports, or pull requests, please
visit our GitHub repository.

## Acknowledgments

Special thanks to the open-source community for their continuous support and contributions.
Your feedback and
contributions are what make projects like this possible!

Feel free to reach out via email for any additional questions or support.
