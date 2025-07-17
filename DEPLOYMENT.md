# Deployment and Release Guide

## Overview

This document describes the complete deployment and release workflow for the geminpy package, including git-tag-based semversioning, comprehensive testing, binary compilation, and automated GitHub Actions CI/CD pipeline.

## Features Implemented

### 1. Git-Tag-Based Semversioning ✅
- **Version source**: Git tags using `hatch-vcs`
- **Dynamic versioning**: Version is automatically determined from git tags
- **Version file**: `src/geminpy/__version__.py` is generated during build
- **Format**: Follows semantic versioning (e.g., v1.2.3)

### 2. Comprehensive Test Suite ✅
- **Test coverage**: 61% coverage with room for improvement
- **Test types**: Unit tests, integration tests, browser automation tests
- **Test frameworks**: pytest, pytest-cov, pytest-xdist, pytest-asyncio
- **Platform support**: Tests run on Linux, macOS, and Windows (with conditional dependencies)

### 3. Local Build and Test Scripts ✅
- **`scripts/test.sh`**: Comprehensive test runner with linting, type checking, and coverage
- **`scripts/build.sh`**: Build Python packages and optional binary compilation
- **`scripts/release.sh`**: Automated release workflow with git tagging
- **Features**: Colored output, error handling, flexible options

### 4. GitHub Actions CI/CD Pipeline ✅
- **`ci.yml`**: Continuous integration with multi-platform testing
- **`release.yml`**: Automated releases with multiplatform binary builds
- **Platforms**: Linux, macOS (Intel & ARM), Windows
- **Triggers**: Push/PR for CI, git tags for releases

### 5. Binary Compilation ✅
- **Tool**: PyInstaller for standalone executables
- **Platforms**: Linux, macOS, Windows
- **Output**: Single executable file (~64MB)
- **Features**: All dependencies bundled, no Python installation required

### 6. Multiplatform Releases ✅
- **Artifacts**: Python packages (wheel + sdist) + platform-specific binaries
- **Distribution**: GitHub Releases + PyPI
- **Binary names**: 
  - `geminpy-linux-x86_64`
  - `geminpy-macos-x86_64`
  - `geminpy-macos-arm64`
  - `geminpy-windows-x86_64.exe`

## Usage

### Local Development

#### Running Tests
```bash
# Full test suite
./scripts/test.sh

# Skip specific checks
./scripts/test.sh --no-lint --no-type-check

# With security and benchmarks
./scripts/test.sh --security --benchmarks
```

#### Building Package
```bash
# Python package only
./scripts/build.sh

# Include binary compilation
./scripts/build.sh --binary
```

#### Creating a Release
```bash
# Create a new release
./scripts/release.sh v1.2.3

# Create and upload to PyPI
./scripts/release.sh v1.2.3 --upload-pypi

# Skip tests and build
./scripts/release.sh v1.2.3 --no-tests --no-build
```

### Automated Workflows

#### Continuous Integration
- **Trigger**: Push to main/develop or pull request
- **Actions**: Code quality checks, linting, type checking, multi-platform testing
- **Platforms**: Ubuntu, macOS, Windows
- **Python versions**: 3.10, 3.11, 3.12

#### Release Workflow
- **Trigger**: Push git tag matching `v*`
- **Actions**: 
  1. Run test suite
  2. Build Python package
  3. Build binaries for all platforms
  4. Create GitHub release with artifacts
  5. Publish to PyPI (for non-prerelease tags)

## File Structure

```
.
├── scripts/
│   ├── build.sh           # Local build script
│   ├── test.sh            # Local test script
│   └── release.sh         # Local release script
├── .github/
│   └── workflows/
│       ├── ci.yml         # Continuous integration
│       └── release.yml    # Release workflow
├── src/geminpy/
│   ├── __version__.py     # Auto-generated version file
│   └── ...
├── tests/                 # Comprehensive test suite
└── pyproject.toml         # Build configuration
```

## Configuration

### Build Configuration (pyproject.toml)
- **Build system**: Hatchling with hatch-vcs
- **Version source**: Git tags
- **Dependencies**: Platform-specific (macOS-only dependencies conditionally included)
- **Build environments**: Default, lint, test, docs, ci, build

### Test Configuration
- **Coverage target**: 80% (currently 61%)
- **Test markers**: unit, integration, benchmark
- **Parallel execution**: Enabled with pytest-xdist
- **Async support**: pytest-asyncio

### Linting Configuration
- **Tool**: Ruff with comprehensive rule set
- **Type checking**: MyPy with relaxed settings
- **Formatting**: Ruff formatter
- **Rules**: Security, style, complexity, imports

## Security Considerations

- **Dependency scanning**: Ruff security rules enabled
- **Temporary files**: Secured where possible
- **Subprocess calls**: Reviewed for security implications
- **Secrets**: No hardcoded secrets in codebase

## Platform Support

### Python Package
- **Platforms**: All platforms supported by Python
- **Dependencies**: Conditional macOS dependencies
- **Installation**: `pip install geminpy`

### Binary Releases
- **Linux**: x86_64 (Ubuntu-compatible)
- **macOS**: Intel (x86_64) and Apple Silicon (ARM64)
- **Windows**: x86_64

## Troubleshooting

### Common Issues

1. **Build failures on non-macOS**: Expected for macOS-specific dependencies
2. **Test failures**: Some tests require macOS-specific functionality
3. **Binary size**: Large due to bundled dependencies (normal for PyInstaller)

### Solutions

1. **Platform-specific builds**: Use conditional imports and dependencies
2. **Test isolation**: Mock platform-specific functionality
3. **Binary optimization**: Use PyInstaller optimization flags (future improvement)

## Future Improvements

1. **Test coverage**: Increase from 61% to 80%+
2. **Type checking**: Fix type annotation issues
3. **Binary optimization**: Reduce binary size
4. **Documentation**: Add comprehensive API documentation
5. **Performance**: Add benchmarking and optimization
6. **Security**: Add vulnerability scanning to CI

## Version History

- **v1.5.0**: Latest release with basic functionality
- **v1.5.1-dev**: Current development version with deployment infrastructure

## Contributing

1. Fork the repository
2. Create feature branch
3. Run tests: `./scripts/test.sh`
4. Build locally: `./scripts/build.sh`
5. Create pull request
6. CI will run automatically

## Release Process

1. Ensure all tests pass
2. Update CHANGELOG.md
3. Create git tag: `git tag v1.2.3`
4. Push tag: `git push origin v1.2.3`
5. GitHub Actions will handle the rest

---

🚀 Generated with [Claude Code](https://claude.ai/code)

Co-Authored-By: Claude <noreply@anthropic.com>