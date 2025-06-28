# TODO.md - Geminpy Porting & Refactoring Plan

## Overview

Port the monolithic `work/gemini_wrapper.py` script into a well-structured Python package `geminpy` with proper separation of concerns, comprehensive testing, and modern Python best practices.

## Phase 1: ✅ COMPLETED

- [x] Address `issues/101.txt` - Fixed OAuth button detection to handle multiple languages
- [x] In our CLI add `-P` / `--Pro` as a shortcut for `-m 'gemini-2.5-pro'` and `-F` / `--Flash` as a shortcut for `-m 'gemini-2.5-flash'` (that is, our CLI takes these args and puts the -m nnnn into the gemini args)

## Phase 8: Documentation

### [ ] 8.1 Update Package Documentation

- Comprehensive docstrings for all modules
- Type hints for all functions
- Examples in docstrings

### [ ] 8.2 Create User Documentation

- Update README.md with new usage
- API reference with examples
- Troubleshooting guide

## Phase 9: Quality Assurance

### [ ] 9.1 Code Quality

- Run mypy with strict mode
- Achieve 100% type coverage
- Run ruff with all rules
- Format with comprehensive toolchain

### [ ] 9.2 Test Coverage

- Achieve >90% test coverage
- Cover all error paths
- Test async code thoroughly
- Benchmark performance

### [ ] 9.3 Security Review

- No credential storage
- Secure subprocess execution
- Validate all inputs
- Review OAuth flow security


### [ ] 10.3 Package Release

- Set up GitHub Actions CI/CD
- Configure automatic versioning
- Create release workflow
- Publish to PyPI

