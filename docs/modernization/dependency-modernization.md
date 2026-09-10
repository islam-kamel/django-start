# Dependency Modernization & Tooling Strategy

## 1. Executive Summary

This document specifies the dependency lifecycle, packaging modernization, and quality-tooling transition for Django-Start 2.0.

The design adheres to the engineering rule:
> **Published runtime dependencies use compatible bounded ranges rather than unnecessarily exact patch pins. Deletion over addition. Boring over clever.**

---

## 2. Dependency Modernization Matrix

| Dependency | Category | Current Version | Latest Stable (Sep 2026) | Target in 2.0 | Action | Technical Justification |
|---|---|---|---|---|---|---|
| **click** | Runtime | `8.1.3` | `8.5.0` | `click>=8.5,<9` | Retain & Upgrade | Upstream provides robust typing, nested subcommand trees, and clean error handling without extra dependencies. |
| **django** (generated projects) | Scaffold Target | Unpinned (`pip install django`) | `6.1.1` (Feature), `5.2.17` (LTS) | Recipe-locked exact pins | Replace Policy | Unbounded `pip install django` is removed. Generator injects deterministic tested pins into target projects. |
| **pytest** | Test | `8.3.4` | `9.1.1` | `pytest>=8.3,<10` | Retain & Upgrade | Standard test runner. Strict marker enforcement and xfail guarantees continue across Python 3.12 - 3.14. |
| **pytest-cov** | Test | Not installed | `6.0.0` | `pytest-cov>=5.0,<7` | Add in Test Env | Required to monitor coverage retention and verify the >=90% quality floor during refactoring. |
| **setuptools** | Build | Legacy (`setup.py` / `setup.cfg`) | `84.0.0` | `setuptools>=84.0` | Modernize | Full PEP 621 declarative metadata support; eliminates `setup.py` and `setup.cfg`. |
| **build** | Build | Not installed | `1.6.0` | `build>=1.2,<2` | Add in Dev/CI | Standard PyPA PEP 517 build tool for creating verified sdist and wheel distributions. |
| **black** | Lint / Format | `22.8.0` | `25.1.0` | Retired | Replace with Ruff | Replaced by unified Rust-based toolchain (`ruff format`). |
| **flake8** | Linter | `5.0.4` | `7.1.2` | Retired | Replace with Ruff | Replaced by `ruff check`. |
| **pyupgrade** | Syntax | `2.38.2` | `3.19.1` | Retired | Replace with Ruff | Replaced by `ruff check --select UP`. |
| **ruff** | Lint / Format | Not installed | `0.16.5` | `ruff>=0.16,<1` | Adopt | Single binary replaces Black, Flake8, and Pyupgrade; 10x - 50x faster; native Python 3.14 support. |
| **mypy** | Type Checker | Not installed | `2.3.1` | `mypy>=2.3,<3` | Adopt | Enforces strict static typing on `src/django_start/**`. Catches contract drift and interface violations. |
| **pre-commit** | Hook Runner | `4.6.2` | `4.6.2` | `pre-commit>=4.0,<5` | Retain | Manages Git hook lifecycles. Hook configuration will transition from multi-tool to Ruff + hygiene. |
| **actions/checkout** | CI Action | `v3` | `v4` | `v4` | Upgrade | GitHub Actions runner maintenance; node20 runtime support. |
| **actions/setup-python** | CI Action | Not configured | `v5` | `v5` | Add | Standard Python environment provisioning in GitHub Actions. |
| **github/codeql-action** | CI Action | `v2` | `v3` | `v3` | Upgrade | Supported major version of CodeQL analysis. |

---

## 3. Tooling Decision Record: Quality Tooling Evaluation

### 3.1 Evaluated Tooling Options

#### Option A: Retain Black + Flake8 + Pyupgrade (Status Quo)
- **Strengths**: Familiar to existing contributors; already passing green across baseline.
- **Weaknesses**: Requires 3 distinct tools in pre-commit; slower execution; separate configuration files (`setup.cfg`, `.pre-commit-config.yaml`); flake8 does not natively support `pyproject.toml` without plugins; multiple Python AST parsers running sequentially.
- **Verdict**: **Rejected for future state.**

#### Option B: Unified Tooling with Ruff (Selected)
- **Strengths**:
  - Replaces Black, Flake8, and Pyupgrade with a single tool.
  - Native configuration in `pyproject.toml` under `[tool.ruff]`.
  - Order-of-magnitude performance improvement on developer machines and in CI.
  - Native support for modern Python 3.12, 3.13, and 3.14 syntax rules (PEP 695, PEP 701).
  - Reliable, non-destructive autofix capabilities.
- **Weaknesses**: Requires a dedicated migration phase to adjust repository rules without breaking characterization tests.
- **Verdict**: **ACCEPTED**. To be implemented in a dedicated tooling migration phase.

#### Option C: Hybrid Configuration (Ruff for linting, Black for formatting)
- **Strengths**: Preserves exact Black formatting AST while using Ruff for speed.
- **Weaknesses**: Unnecessary dual-tool maintenance. Ruff's formatter has reached near 100% parity with Black formatting conventions.
- **Verdict**: **Rejected.** Unnecessary complexity.

### 3.2 Target Ruff Configuration Specification

To be placed in `pyproject.toml` during the tooling modernization phase:
```toml
[tool.ruff]
target-version = "py312"
line-length = 88
src = ["src", "tests"]

[tool.ruff.lint]
select = [
    "E",    # pycodestyle errors
    "W",    # pycodestyle warnings
    "F",    # pyflakes
    "I",    # isort
    "UP",   # pyupgrade
    "B",    # flake8-bugbear
    "C4",   # flake8-comprehensions
    "SIM",  # flake8-simplify
    "T20",  # flake8-print (disallow raw print in library code)
    "PT",   # flake8-pytest-style
]
ignore = [
    "E501", # line-too-long handled by formatter
]

[tool.ruff.format]
quote-style = "double"
indent-style = "space"
```

---

## 4. Packaging Architecture & Specification

### 4.1 PyPA Modernization Principles

1. **Declarative Metadata (PEP 621)**: All project metadata, dependencies, classifiers, and entry points live in `pyproject.toml`. The legacy `setup.cfg` and `setup.py` are deprecated and will be removed.
2. **Standard Source Layout (`src/` layout)**:
   - Packaging structure moves from flat `djstartlib/` to `src/django_start/`.
   - Prevents the local working directory from shadowing the installed package in test suites.
   - Eliminates the need for runtime `sys.path` mutations.
3. **Distribution vs Import Name Separation**:
   - **Distribution Package Name** (on PyPI): `django-start-automate` (preserves existing package authority, releases, and user download paths).
   - **Importable Module Name** (in Python): `django_start` (replaces legacy `djstartlib` with standard, idiomatic naming).
   - **Temporary Compatibility Bridge**: In 2.0, `djstartlib` will remain as a thin deprecated redirect package pointing to `django_start`, emitting a `DeprecationWarning` upon import.
4. **Dynamic Versioning via Package Metadata**:
   - Version resolved at runtime using standard library `importlib.metadata.version("django-start-automate")`.
   - Eliminates duplicated static version constants across `setup.cfg`, `version.py`, and `__init__.py`.

### 4.2 Target `pyproject.toml` Draft Specification

```toml
[build-system]
requires = ["setuptools>=84.0"]
build-backend = "setuptools.build_meta"

[project]
name = "django-start-automate"
version = "2.0.0a1"
description = "Deterministic, safe, extensible Django project scaffolding CLI."
readme = "README.md"
license = { text = "MIT" }
authors = [
    { name = "Islam Kamel", email = "dev.islam.kamel@gmail.com" }
]
requires-python = ">=3.12"
classifiers = [
    "Development Status :: 5 - Production/Stable",
    "Environment :: Console",
    "Framework :: Django",
    "Framework :: Django :: 5.2",
    "Framework :: Django :: 6.0",
    "Framework :: Django :: 6.1",
    "Intended Audience :: Developers",
    "License :: OSI Approved :: MIT License",
    "Operating System :: OS Independent",
    "Programming Language :: Python :: 3",
    "Programming Language :: Python :: 3.12",
    "Programming Language :: Python :: 3.13",
    "Programming Language :: Python :: 3.14",
    "Topic :: Software Development :: Build Tools",
    "Topic :: Software Development :: Code Generators",
]
dependencies = [
    "click>=8.5,<9",
]

[project.optional-dependencies]
test = [
    "pytest>=8.3,<10",
    "pytest-cov>=5.0,<7",
]
dev = [
    "pre-commit>=4.0,<5",
    "ruff>=0.16,<1",
    "mypy>=2.3,<3",
    "build>=1.2,<2",
]

[project.scripts]
django-start = "django_start.cli:cli"
# Compatibility script (deprecated)
django-version = "django_start.cli:version_shim"

[tool.setuptools.packages.find]
where = ["src"]

[tool.setuptools.package-data]
django_start = ["recipes/**/*.json", "recipes/**/*.tmpl", "py.typed"]
```
