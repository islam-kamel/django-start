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
| **build** | Build | Not installed | `1.6.1` | `build>=1.2,<2` | Add in Dev/CI | Re-verified actual upstream on 2026-09-11 (1.6.1 published Sep 10, replacing 1.6.0). Standard PEP 517 build tool for sdist and wheel generation. |
| **black** | Lint / Format | `22.8.0` | `25.1.0` | Retired | Replace with Ruff | Replaced by unified Rust-based toolchain (`ruff format`). |
| **flake8** | Linter | `5.0.4` | `7.1.2` | Retired | Replace with Ruff | Replaced by `ruff check`. |
| **pyupgrade** | Syntax | `2.38.2` | `3.19.1` | Retired | Replace with Ruff | Replaced by `ruff check --select UP`. |
| **ruff** | Lint / Format | Not installed | `0.16.7` | `ruff>=0.16,<1` | Adopt | Verified 0.16.7 on PyPI. Single binary replaces Black, Flake8, and Pyupgrade; 10x - 50x faster; native Python 3.14 support. |
| **mypy** | Type Checker | Not installed | `2.3.1` | `mypy>=2.3,<3` | Adopt | Enforces strict static typing on `src/django_start/**`. Catches contract drift and interface violations. |
| **pre-commit** | Hook Runner | `4.6.2` | `4.6.2` | `pre-commit>=4.0,<5` | Retain | Manages Git hook lifecycles. Hook configuration will transition from multi-tool to Ruff + hygiene. |
| **uv** | Environment / Installer | Not installed | `0.12.13` | Under evaluation | Evaluate | High-performance environment manager and installer; evaluated as pluggable adapter alongside stdlib venv + pip. |
| **actions/checkout** | CI Action | `v3` | `v7.0.1` | `actions/checkout@v7.0.1` | Upgrade | Runner checkout action updated to latest verified upstream release tag (or immutable SHA). |
| **actions/setup-python** | CI Action | Not configured | `v7.0.0` | `actions/setup-python@v7.0.0` | Add | Standard Python environment provisioning in GitHub Actions (or immutable SHA). |
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

### 4.1 Packaging Terminology & Modernization Standards

The Python packaging ecosystem has transitioned decisively from imperative setup scripts to static declarative standards:

1. **Imperative `setup.py` (Legacy / Removed)**:
   - `setup.py` is an executable script that executes Python code during package inspection, build, and installation.
   - Executing arbitrary code merely to discover metadata (such as version or dependencies) introduces security risks, non-hermetic build environments, and execution side-effects.
   - In Django-Start 2.0, `setup.py` is completely eliminated.
2. **Intermediate `setup.cfg` (Legacy / Removed)**:
   - `setup.cfg` provided declarative INI-style metadata, but was tightly coupled to `setuptools` and lacked universal tool interoperability.
   - In Django-Start 2.0, `setup.cfg` is completely eliminated.
3. **PyPA Modern Standards (PEP 517, PEP 518, PEP 621)**:
   - **PEP 518**: Standardizes build-system requirements declaration via the `[build-system]` table in `pyproject.toml`.
   - **PEP 517**: Decouples the build frontend (e.g. `build`) from the build backend (e.g. `setuptools.build_meta`), allowing consistent and isolated artifact generation.
   - **PEP 621**: Standardizes project metadata within the `[project]` table in `pyproject.toml`. Metadata is statically parsed without code execution, guaranteeing fast, safe, and reproducible package inspection.
4. **Standard Source Layout (`src/` layout)**:
   - Packaging structure relocates source code from the repository root into `src/django_start/`.
   - Prevents the local working directory from shadowing the installed package during test execution.
   - Guarantees tests run against the installed wheel artifact rather than arbitrary local source files, eliminating runtime `sys.path` hacks.
5. **Distribution Name vs Import Package Name**:
   - **Distribution Name** (PyPI): `django-start-automate` (preserves existing PyPI project authority, download history, and release identity).
   - **Import Package Name** (Python): `django_start` (standardized, idiomatic Python package naming).
6. **Dynamic Version Resolution**:
   - Runtime version resolution uses standard library `importlib.metadata.version("django-start-automate")`.
   - Single source of truth defined in packaging metadata; eliminates duplicated constants across files.

### 4.2 `djstartlib` Compatibility Redirect Shim & Deprecation Schedule

To ensure backward compatibility for consumers upgrading within modern Python environments, Django-Start 2.0 provides a dedicated compatibility redirect shim:

#### Shim Structure
The package distribution includes a thin namespace package in `src/djstartlib/` structured as follows:

```text
src/
├── django_start/                # Canonical 2.0 application and domain packages
│   ├── __init__.py
│   ├── cli.py
│   ├── application/
│   ├── domain/
│   ├── ports/
│   └── infrastructure/
└── djstartlib/                  # Deprecated compatibility redirect shim
    ├── __init__.py
    ├── core.py                  # Redirects to django_start.application use cases
    ├── version.py               # Redirects to django_start.version
    └── utilities.py             # Redirects to django_start filesystem utilities
```

#### Behavioral Contract
When any module within `djstartlib` is imported:
1. It immediately emits a standard `DeprecationWarning`:
   ```python
   import warnings

   warnings.warn(
       "The 'djstartlib' package is deprecated and will be removed in Django-Start 3.0. "
       "Please update your imports to use 'django_start'.",
       DeprecationWarning,
       stacklevel=2,
   )
   ```
2. It forwards functions, classes, and constants to their respective implementations in `django_start`.
3. The shim is verified in CI across all **supported Django-Start 2.x Python versions** (Python 3.12, 3.13, and 3.14).

#### Deprecation Schedule
- **Django-Start 2.0.0a1 to 2.0.0 GA**: Compatibility shim introduced. Warning emitted on import. Legacy CLI command `django-version` routes through compatibility shim with warning.
- **Django-Start 2.x Series**: Shim maintained and tested across all 2.x minor releases.
- **Django-Start 3.0.0**: Complete removal of `src/djstartlib/` and the `django-version` command.

### 4.3 Target `pyproject.toml` Draft Specification

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
djstartlib = ["py.typed"]
```

---

## 5. Dependency Locking Strategy & Research Constraints

A core product invariant of Django-Start is:
> **Generation must be deterministic. The exact selected Django version and dependencies must be known and verified.**

To fulfill this invariant without imposing unnecessary vendor lock-in or fragile workflow assumptions, dependency locking must be governed by explicit research constraints.

### 5.1 Mandated Lock Strategy Comparison

The project mandates an objective, empirical evaluation comparing three candidate lock mechanisms for generated Django projects and internal tooling:

1. **Traditional Requirements Snapshots (`requirements.txt` via `pip-compile` / pip)**:
   - **Characteristics**: Flat text file with exact `package==version` pins and optional SHA-256 `--hash` flags.
   - **Evaluation**:
     - *Strengths*: 100% universal support across all Python environments; works out of the box with stock `pip`; universally supported by cloud deployment platforms, PaaS, and base Docker images.
     - *Weaknesses*: Handling multi-platform hashes and environment markers can require multiple files (e.g. `requirements-linux.txt`, `requirements-win.txt`) or complex invocation options.
2. **PEP 751 `pylock.toml`**:
   - **Characteristics**: The standardized Python dependency lockfile specification defined by PyPA.
   - **Evaluation**:
     - *Strengths*: Tool-agnostic standard format; avoids proprietary lockfile lock-in; cleanly represents multi-platform markers, hashes, and dependency graphs in structured TOML.
     - *Weaknesses*: Upstream adoption is evolving across installers in 2026; require fallback handling for environments running older installer tooling.
3. **Tool-Specific Lockfiles (`uv.lock`, `poetry.lock`)**:
   - **Characteristics**: High-performance proprietary lock format generated by specific tools (such as `uv`).
   - **Evaluation**:
     - *Strengths*: Lightning-fast resolution; universal cross-platform lock graphs; integrated workspace support.
     - *Weaknesses*: Enforces tool vendor lock-in; requires target developers and CI environments to have the specific tool (`uv`) installed; cannot be natively consumed by standard `pip`.

### 5.2 Research Constraints & Decision Guardrails

1. **No Unilateral Lock Format Assumption**:
   - The team must NOT assume `requirements.lock`, `uv.lock`, or any single snapshot format before completing the formal evaluation.
2. **Evaluation Criteria**:
   - Every candidate lock format must be benchmarked against:
     - **Standardization**: PyPA standard alignment.
     - **Offline Reproducibility**: Deterministic installation using cached wheels without network access.
     - **Portability**: Verified consistency across Linux, macOS, and Windows.
     - **User Friction**: Zero requirement for end users to install unexpected third-party tools unless explicitly chosen.
     - **Maintenance Overhead**: Simplicity of updating pins when new Django security patch releases occur.
3. **Outcome Resolution**:
   - The final locking architecture will be formalized in an upcoming Architecture Decision Record (ADR) once concrete benchmarking across `pip` and `uv` installers is complete.
