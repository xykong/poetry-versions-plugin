# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [1.1.0] - 2026-01-26

### Added
- **Poetry 1.x compatibility**: Plugin now supports both Poetry 1.2+ and Poetry 2.x
- PEP 621 format detection: Automatically detects and handles `[project].version` (Poetry 2.x)
- New `get_project_version()` utility function for cross-version compatibility
- Comprehensive test suite for version format compatibility (8 new test cases)
- Compatibility documentation in README

### Changed
- Relaxed Poetry dependency from `>=2.0.0` to `>=1.2.0`
- Version retrieval now uses smart detection instead of hardcoded path

### Fixed
- Issue #1: Clarified Poetry 1.x and 2.x support

## [1.0.1] - 2025-05-23

### Fixed
- Version bump and release process improvements

## [1.0.0] - 2025-05-23

### Added
- Initial stable release
- Automated version management with Poetry integration
- Git information recording (branch, commit, count, dirty status)
- Customizable commit workflow
- Release process automation with git-flow support

### Changed
- Updated to Poetry 2.0.0+ (previous versions)
- Bumped minimum Python version to 3.9

[Unreleased]: https://github.com/xykong/poetry-versions-plugin/compare/v1.1.0...HEAD
[1.1.0]: https://github.com/xykong/poetry-versions-plugin/compare/v1.0.1...v1.1.0
[1.0.1]: https://github.com/xykong/poetry-versions-plugin/compare/v1.0.0...v1.0.1
[1.0.0]: https://github.com/xykong/poetry-versions-plugin/releases/tag/v1.0.0
