# Python & Django Ecosystem Research (September 2026)

## 1. Executive Summary

This document presents empirical, primary-source research into the Python, Django, and packaging tooling ecosystems as of September 2026.

All claims are classified using the following epistemology:
- `[FACT]`: Empirically verified against official upstream documentation, PEPs, or PyPI release metadata.
- `[RECOMMENDATION]`: Technical strategy derived from facts, engineering constraints, and product invariants.
- `[FUTURE POSSIBILITY]`: Emerging technology or upstream release candidate not yet locked into the baseline.
- `[KNOWN UNKNOWN]`: External factor whose resolution depends on future ecosystem events.

---

## 2. Python Release Landscape

### 2.1 Supported Versions and Upstream Lifecycle

The official Python lifecycle is governed by annual release PEPs published on `python.org`.

| Python Version | Release Date | Status (Sep 2026) | Bugfix Support Ends | Extended Security EOL | Primary PEP |
|---|---|---|---|---|---|
| **Python 3.15** | October 1, 2026 (Scheduled) | `[FUTURE POSSIBILITY]` RC2 (released Sep 1, 2026) | October 2028 | October 2031 | PEP 790 |
| **Python 3.14** | October 7, 2025 | `[FACT]` Active Bugfix (3.14.7 released Aug 2026) | October 2027 | October 2030 | PEP 745 |
| **Python 3.13** | October 7, 2024 | `[FACT]` Active Bugfix | October 2026 | October 2029 | PEP 719 |
| **Python 3.12** | October 2, 2023 | `[FACT]` Security Fixes Only | October 2025 | October 2028 | PEP 693 |
| **Python 3.11** | October 24, 2022 | `[FACT]` Security Fixes Only | April 2024 | October 2027 | PEP 664 |
| **Python 3.10** | October 4, 2021 | `[FACT]` End of Life Pending (Oct 2026) | May 2023 | October 2026 | PEP 619 |
| **Python 3.9** | October 5, 2020 | `[FACT]` End of Life (EOL) | May 2022 | October 2025 | PEP 596 |
| **Python 3.8** | October 14, 2019 | `[FACT]` End of Life (EOL) | May 2021 | October 2024 | PEP 569 |
| **Python 3.7** | June 27, 2018 | `[FACT]` End of Life (EOL) | June 2020 | June 2023 | PEP 537 |

*Sources: Python Enhancement Proposals: PEP 790 (Python 3.15 Release Schedule), PEP 745 (Python 3.14 Release Schedule), PEP 719 (Python 3.13 Release Schedule), PEP 693 (Python 3.12 Release Schedule), PEP 664 (Python 3.11 Release Schedule).*

### 2.2 Python Features Relevant to Django-Start 2.0

- **`[FACT]` Python 3.12+ (PEP 695 - Type Parameter Syntax)**:
  Introduces native generic class and function syntax (`def func[T](arg: T) -> T:`), type aliases (`type OptStr = str | None`), making type definitions cleaner without `TypeVar` boilerplate.
- **`[FACT]` Python 3.12+ (PEP 701 - Syntactic Formalization of f-strings)**:
  Lifts restrictions on f-strings, permitting quotes reuse, arbitrary expressions, backslashes, and multiline expressions inside expressions.
- **`[FACT]` Python 3.13+ (PEP 667, PEP 703 - Free-threaded CPython and Enhanced REPL)**:
  Provides experimental free-threaded builds and modernized terminal interactions.
- **`[FACT]` Python 3.14+ (PEP 649, PEP 749 - Deferred Evaluation of Annotations)**:
  Stringifies annotations automatically, changing how runtime introspection inspects type hints.

---

## 3. Django Release Landscape

### 3.1 Official Django Support Roadmap

According to official Django release documentation (`djangoproject.com/download/`), Django provides two release types: Feature Releases (supported for approximately 8 months of bugfixes plus 8 months of security) and Long-Term Support (LTS) Releases (supported for 3 years).

| Django Version | Release Date | Status (Sep 2026) | End of Bugfix Support | End of Extended Security | Supported Python Versions |
|---|---|---|---|---|---|
| **Django 6.2 LTS** | Dec 2026 (Announced) | `[FUTURE POSSIBILITY]` In development | ~Dec 2029 | ~Dec 2029 | 3.12, 3.13, 3.14, 3.15 |
| **Django 6.1** | April 2026 | `[FACT]` Latest Stable Feature Release (6.1.1) | April 2027 | December 2027 | 3.12, 3.13, 3.14 |
| **Django 6.0** | December 2025 | `[FACT]` Stable Feature Release (6.0.8) | August 2026 | April 2027 | 3.12, 3.13, 3.14 |
| **Django 5.2 LTS** | April 2025 | `[FACT]` Current Stable LTS (5.2.17) | December 2025 | April 2028 | 3.10, 3.11, 3.12, 3.13, 3.14 |
| **Django 5.1** | August 2024 | `[FACT]` End of Life | April 2025 | December 2025 | 3.10, 3.11, 3.12, 3.13 |
| **Django 4.2 LTS** | April 2023 | `[FACT]` End of Life | December 2023 | April 2026 | 3.8, 3.9, 3.10, 3.11, 3.12 |

*Sources: Django Project official download and roadmap documentation (`https://www.djangoproject.com/download/`).*

### 3.2 Key Architectural Implications for Django-Start 2.0

1. **`[FACT]` Django 6.0 Dropped Python 3.10 and Python 3.11**:
   Django 6.0 and Django 6.1 strictly require Python 3.12 or newer. Generating a Django 6.x project inside a Python 3.11 environment is impossible because `pip install "django>=6.0"` rejects Python 3.11.
2. **`[FACT]` Django 5.2 LTS is Supported Until April 2028**:
   Organizations prioritizing stability remain on Django 5.2 LTS. Django 5.2 runs on Python 3.10 through 3.14.
3. **`[RECOMMENDATION]` Dual-Track Support Model**:
   Django-Start 2.0 must support generating both Django 5.2 LTS (for enterprise stability) and Django 6.1 (for modern feature sets). The generator default should be Django 6.1 (latest tested stable feature release).
4. **`[RECOMMENDATION]` Python Baseline Selection**:
   Because Django 6.x requires Python 3.12+, the minimum Python version for Django-Start 2.0 must be **Python 3.12**.

---

## 4. Upstream Dependency & Tooling Research

### 4.1 CLI Framework: Click

- **Current Version in Repo**: `click==8.1.3` (released April 2022)
- **`[FACT]` Latest Stable Version**: `click==8.5.0` (released August 26, 2026 on PyPI)
- **Python Compatibility**: Python 3.8 through 3.14
- **Key Enhancements since 8.1.3**:
  - Full typing support across command callbacks and decorators (`click.Context`, `click.Parameter`).
  - Improved shell completion generators for zsh, bash, and fish.
  - Better handling of terminal color themes and modern terminal escape sequences.
  - Native support for nested command groups and subcommands with rich custom help formatters.
- **`[RECOMMENDATION]` Target Specification**: `click>=8.5,<9` for runtime dependency.

### 4.2 Test Framework: Pytest

- **Current Version in Repo**: `pytest==8.3.4` (released December 2024)
- **`[FACT]` Latest Stable Version**: `pytest==9.1.1` (released on PyPI)
- **Python Compatibility**: Python 3.8 through 3.14
- **Key Enhancements**:
  - Full compatibility with Python 3.13 free-threaded builds and Python 3.14 AST changes.
  - Improved assertion introspection and sub-millisecond execution overhead.
- **`[RECOMMENDATION]` Target Specification**: `pytest>=8.3,<10` for test runner.

### 4.3 Quality Tooling: Ruff vs Black + Flake8 + Pyupgrade

- **Current State**:
  - `.pre-commit-config.yaml` runs Black 22.8.0, Flake8 5.0.4, Pyupgrade 2.38.2, and pre-commit-hooks v4.3.0 under Python 3.10.
- **`[FACT]` Ruff Status**:
  - Latest version on PyPI: `0.16.5`
  - Replaces Flake8, Black, isort, Pyupgrade, pydocstyle, flake8-bugbear, and flake8-comprehensions with a single Rust binary.
  - Performance: 10x to 100x faster than running Python-based linters.
  - Native support for Python 3.12, 3.13, and 3.14 syntax.
  - Configuration consolidated in standard `pyproject.toml` under `[tool.ruff]`.
- **Autofix Safety**: Ruff supports safe autofix (`ruff check --fix`) and strict rule configuration.
- **`[RECOMMENDATION]` Migration Decision**: Transition the repository quality pipeline to Ruff (formatter + linter) in a dedicated tooling modernization phase, replacing the legacy multi-tool setup.

### 4.4 Static Type Checking: Mypy

- **Current State**: No static type checking configured in the repository. Production code in `djstartlib` lacks type hints.
- **`[FACT]` Mypy Status**:
  - Latest version on PyPI: `2.3.1` (released August 14, 2026)
  - Full support for PEP 695 (Python 3.12 type parameter syntax) and Python 3.13/3.14 typing features.
- **`[RECOMMENDATION]` Adoption Plan**: Introduce strict static type checking with mypy targeting `src/django_start/` under Python 3.12+.

### 4.5 Packaging Standards: PEP 517 / PEP 621 / Build

- **Current State**: Dual configuration with `setup.py` (3 lines calling `setup()`), `setup.cfg` (76 lines of metadata), and minimal `pyproject.toml` (build-system only).
- **`[FACT]` Packaging Authority Best Practices**:
  - PEP 621: Standardized `[project]` metadata table in `pyproject.toml`.
  - PEP 517 / 518: Standardized build-system invocation via `setuptools.build_meta` or `flit_core` / `hatchling`.
  - `setuptools` 84.0.0 (August 2026) provides complete PEP 621 support, eliminating `setup.cfg` and `setup.py`.
  - `build` 1.6.0 provides deterministic, isolated wheel and sdist builds (`python -m build`).
  - `src/` layout: The PyPA officially recommends `src/<package_name>` to prevent accidental imports of the local source tree instead of the installed package during testing.
- **`[RECOMMENDATION]` Target Specification**: Migrate to a pure `pyproject.toml` (PEP 621) configuration using `setuptools>=84.0` as build backend and adopt `src/django_start/` directory structure.

---

## 5. Summary Matrix of Evaluated Tools

| Tool | Current Repo Version | Researched Latest (Sep 2026) | Evaluation & Target Recommendation |
|---|---|---|---|
| **Python Target** | 3.11 (canonical baseline) | 3.14 (stable), 3.15 (RC2) | Move 2.0 runtime to `Python 3.12 - 3.14`. Retain 3.11 in CI only for characterization suite. |
| **Django Target** | Unpinned (`pip install django`) | 5.2.17 (LTS), 6.1.1 (Feature) | Deterministic profiles: Default `6.1.1`, optional LTS `5.2.17`. Unpinned installation strictly forbidden. |
| **Click** | 8.1.3 | 8.5.0 | Upgrade to `click>=8.5,<9`. Adopt subcommands (`new`, `add`, `doctor`). |
| **Pytest** | 8.3.4 | 9.1.1 | Upgrade to `pytest>=8.3,<10`. Retain `--strict-markers` and `xfail_strict`. |
| **Ruff** | Not configured | 0.16.5 | Adopt Ruff to replace Black, Flake8, and Pyupgrade in dedicated tooling phase. |
| **Mypy** | Not configured | 2.3.1 | Adopt mypy with strict settings for all new 2.0 application code. |
| **Build Backend** | `setup.cfg` + `setup.py` | `setuptools==84.0.0` (PEP 621) | Eliminate `setup.cfg` and `setup.py`. Consolidate into `pyproject.toml`. Adopt `src/` layout. |
| **Build Tool** | Not configured | `build==1.6.0` | Use `python -m build` for verifiable sdist/wheel artifact generation. |
| **GitHub Actions** | `checkout@v3`, `codeql@v2` | `checkout@v4`, `codeql@v3` | Modernize Actions to current immutable SHA or latest major versions. |
