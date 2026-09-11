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

According to official Django release documentation (`djangoproject.com/download/`), Django historically provides two release types: Feature Releases (supported for approximately 8 months of bugfixes plus 8 months of security) and Long-Term Support (LTS) Releases (supported for 3 years).

| Django Version | Release Date | Status (Sep 2026) | End of Bugfix Support | End of Extended Security | Supported Python Versions |
|---|---|---|---|---|---|
| **Django 6.2 LTS** | April 2027 (Announced) | `[FUTURE POSSIBILITY]` Final Designated LTS (In Development) | December 2027 | April 2030 | 3.12, 3.13, 3.14, 3.15 |
| **Django 6.1** | August 5, 2026 | `[FACT]` Latest Stable Feature Release (6.1.1 on Sep 2, 2026) | April 2027 | December 2027 | 3.12, 3.13, 3.14 |
| **Django 6.0** | December 2025 | `[FACT]` Stable Feature Release (6.0.8) | August 2026 | April 2027 | 3.12, 3.13, 3.14 |
| **Django 5.2 LTS** | April 2025 | `[FACT]` Current Stable LTS (5.2.17) | December 2025 | April 2028 | 3.10, 3.11, 3.12, 3.13, 3.14 |
| **Django 5.1** | August 2024 | `[FACT]` End of Life | April 2025 | December 2025 | 3.10, 3.11, 3.12, 3.13 |
| **Django 4.2 LTS** | April 2023 | `[FACT]` End of Life | December 2023 | April 2026 | 3.8, 3.9, 3.10, 3.11, 3.12 |

*Sources: Django Project official download and roadmap documentation (`https://www.djangoproject.com/download/`). Django 6.1 final released on August 5, 2026; patch release 6.1.1 published on September 2, 2026; Django 6.2 LTS scheduled for April 2027.*

### 3.2 Django Enhancement Proposal 20 (DEP 20): Annual CalVer & Uniform Support

`[FACT]` DEP 20 formalizes a structural evolution in the Django release and support model:

1. **Adoption of Calendar Versioning (CalVer)**:
   - Beginning in January 2028, Django transitions from SemVer-style numbering (`X.Y`) to an annual Calendar Versioning scheme: `YYYY.N` (starting with **Django 2028.0** in January 2028).
   - Under this scheme, the primary annual feature release arrives each January (`YYYY.0`), followed by scheduled minor iterations (`YYYY.1`, etc.).
2. **Retirement of the Designated LTS Model Post-6.2**:
   - **Django 6.2 LTS (April 2027)** will be the final release bearing the explicit Long-Term Support (LTS) designation under the legacy cadence.
   - Post-6.2, the distinction between "Feature" and "LTS" releases is formally retired.
3. **Uniform 3-Year Support Window**:
   - Starting with Django 2028.0, every annual release receives uniform 3-year support (approximately 16 months of active bugfixes followed by security maintenance extending to 36 months total).
   - Users and tooling can rely on consistent, predictable lifecycle overlap without alternating between short-lived and long-lived release tiers.
4. **Strategic Impact on Django-Start**:
   - The CLI designation `--django lts` is a **transitional concept**. In the immediate term, `--django lts` maps to Django 5.2 LTS (and subsequently Django 6.2 LTS).
   - For long-term architecture, Django-Start decouples project archetype profiles from framework release tracks. In the CalVer era, Django-Start will target annual releases under uniform support rather than bifurcated LTS versus non-LTS tracks.

### 3.3 Key Architectural Implications for Django-Start 2.0

1. **`[FACT]` Django 6.0 Dropped Python 3.10 and Python 3.11**:
   Django 6.0 and Django 6.1 strictly require Python 3.12 or newer. Generating a Django 6.x project inside a Python 3.11 environment is impossible because `pip install "django>=6.0"` rejects Python 3.11.
2. **`[FACT]` Django 5.2 LTS is Supported Until April 2028**:
   Organizations prioritizing stability remain on Django 5.2 LTS. Django 5.2 runs on Python 3.10 through 3.14.
3. **`[RECOMMENDATION]` Dual-Track Support Model (Transitional)**:
   Django-Start 2.0 must support generating both Django 5.2 LTS (for enterprise stability) and Django 6.1 (for modern feature sets). The generator default is Django 6.1.1 (latest tested stable feature release).
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
  - Latest version on PyPI: `0.16.7` (verified September 11, 2026)
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
  - `build` 1.6.1 (re-verified actual upstream on 2026-09-11 as 1.6.1 published September 10, 2026, replacing 1.6.0) provides deterministic, isolated wheel and sdist builds (`python -m build`).
  - `src/` layout: The PyPA officially recommends `src/<package_name>` to prevent accidental imports of the local source tree instead of the installed package during testing.
- **`[RECOMMENDATION]` Target Specification**: Migrate to a pure `pyproject.toml` (PEP 621) configuration using `setuptools>=84.0` as build backend and adopt `src/django_start/` directory structure.

### 4.6 Package Manager & Environment Provisioning Evaluation

Django-Start 2.0 requires provisioning isolated virtual environments and installing pinned dependencies (such as Django and recipe packages). This section provides an objective, unbiased evaluation of potential environment and package management tooling options:

#### Option 1: Standard Library `venv` + Standard `pip`
- **Mechanism**: Use Python's standard library `venv` module to create isolated virtual environments, and use the bundled `pip` executable for dependency installation.
- **Strengths**:
  - Zero additional runtime dependencies: universally present across standard CPython installations.
  - Battle-tested stability and cross-platform compatibility across Linux, macOS, and Windows.
  - Compliant with enterprise air-gapped or restricted environments that disallow unvetted external binary executables.
  - Complete alignment with PyPA standards.
- **Weaknesses**:
  - Slower execution speed during package downloads, wheel building, and environment creation compared to compiled Rust tooling.
  - Lacks native single-file lockfile support without auxiliary tools (such as `pip-tools`).
- **Evaluation**: Baseline standard adapter.

#### Option 2: `uv` (Astral)
- **Mechanism**: High-performance Python package and environment manager written in Rust, utilizing `uv venv` and `uv pip install`.
- **Strengths**:
  - Dramatic performance gains: 10x to 100x faster package resolution, caching, and installation.
  - Unified command surface handling both environment creation and package installation.
  - Built-in global wheel cache reduces bandwidth and disk usage across repeated generations.
- **Weaknesses**:
  - External non-stdlib dependency: requires either bundling the binary, expecting user pre-installation on PATH, or dynamically fetching it.
  - Fast-evolving CLI surface and lockfile format require continuous tracking of upstream changes.
  - Enterprise environments may restrict running pre-compiled third-party binaries.
- **Evaluation**: High-performance optional accelerator under evaluation; not pre-selected as a mandatory dependency.

#### Option 3: Other Alternatives (`virtualenv`, `poetry`, `pipenv`)
- **Mechanism**: Third-party Python tools for virtual environment creation and workflow management.
- **Strengths**: Mature ecosystems with legacy community adoption.
- **Weaknesses**:
  - Substantial runtime dependency footprint and slow cold-start times.
  - Enforce proprietary project layouts or lock formats that conflict with clean, standard Django project structures.
- **Evaluation**: Rejected for core scaffolding workflows.

#### Architectural Resolution
Rather than hardcoding a single package manager, Django-Start 2.0 segregates environment management and package installation behind distinct port interfaces (`EnvironmentManager` and `PackageInstaller`). The baseline adapter uses `stdlib venv + pip` (`VenvEnvironmentManager` and `PipInstaller`) to guarantee 100% portable, zero-dependency execution out of the box. High-performance adapters (such as `UvInstaller`) remain under evaluation as pluggable, non-mandatory accelerators.

---

## 5. Summary Matrix of Evaluated Tools & Tooling Freshness Table

The following table records the formal freshness audit of upstream tools and components as of research timestamp **2026-09-11**:

| Tool / Component | Research Timestamp | Authoritative Source | Latest Upstream Version | Recommended / Target Version | Evaluation & Strategic Plan |
|---|---|---|---|---|---|
| **Python Target** | 2026-09-11 | `python.org` (PEP 745, PEP 790) | 3.14.7 (stable), 3.15.0rc2 | `Python 3.12 - 3.14` | Target 2.0 runtime to Python 3.12 - 3.14. Retain 3.11 in CI only for legacy characterization suite. |
| **Django Target** | 2026-09-11 | `djangoproject.com/download/` | 6.1.1 (and 5.2.17 LTS) | `6.1.1` (default), `5.2.17` (LTS) | Recipe-locked patch pins. Unpinned `pip install django` forbidden. Prepare for DEP 20 CalVer (2028.0). |
| **Click** | 2026-09-11 | PyPI (`pypi.org/project/click/`) | 8.5.0 | `click>=8.5,<9` | Upgrade to Click 8.5.0+. Adopt subcommands (`new`, `add`, `doctor`, `check`, `recipe`). |
| **Pytest** | 2026-09-11 | PyPI (`pypi.org/project/pytest/`) | 9.1.1 | `pytest>=8.3,<10` | Standard test runner. Strict marker enforcement and xfail guarantees continue across Python 3.12 - 3.14. |
| **Ruff** | 2026-09-11 | PyPI (`pypi.org/project/ruff/`) | 0.16.7 | `ruff>=0.16,<1` | Adopt Ruff in dedicated tooling phase to replace Black, Flake8, and Pyupgrade with unified Rust toolchain. |
| **Mypy** | 2026-09-11 | PyPI (`pypi.org/project/mypy/`) | 2.3.1 | `mypy>=2.3,<3` | Strict static type checking for all new `src/django_start/` code targeting Python 3.12+. |
| **Setuptools** | 2026-09-11 | PyPI (`pypi.org/project/setuptools/`) | 84.0.0 | `setuptools>=84.0` | Standard PEP 621 declarative build backend. Eliminate `setup.cfg` and `setup.py`. |
| **Build** | 2026-09-11 | PyPI (`pypi.org/project/build/`) | 1.6.1 | `build>=1.2,<2` | Re-verified actual upstream on 2026-09-11 (1.6.1 published Sep 10, replacing 1.6.0). Standard PEP 517 build tool. |
| **Pre-commit** | 2026-09-11 | PyPI (`pypi.org/project/pre-commit/`) | 4.6.2 | `pre-commit>=4.0,<5` | Git hook lifecycle management; transition hooks to Ruff and file hygiene checks. |
| **uv** | 2026-09-11 | PyPI / GitHub (`astral.sh/uv`) | 0.12.13 | Under evaluation | High-performance environment manager and installer; evaluated as pluggable adapter alongside stdlib venv + pip. |
| **actions/checkout** | 2026-09-11 | GitHub Marketplace | v7.0.1 | `actions/checkout@v7.0.1` | Modernize CI runner checkout action to latest upstream release (or immutable SHA). |
| **actions/setup-python** | 2026-09-11 | GitHub Marketplace | v7.0.0 | `actions/setup-python@v7.0.0` | Standard Python runtime provisioning across multi-tier CI matrix (or immutable SHA). |
