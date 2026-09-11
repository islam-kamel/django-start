# Django-Start 2.0 Compatibility Matrix & Support Policy

## 1. Executive Summary

This document establishes the official platform, language, and framework support policy for Django-Start 2.0.

The policy reconciles the upstream lifecycles of CPython and the Django Project with the core product invariant:
> **Generation must be deterministic, reproducible, safe, and verifiable.**

---

## 2. Python Compatibility Decision

### 2.1 Evaluation of Evaluated Alternatives

| Alternative | Pros | Cons | Verdict |
|---|---|---|---|
| **Python 3.14 Only** | Maximum modernization; clean syntax; leverage deferred annotations natively. | Excludes widespread production environments; cuts off developers running Ubuntu 24.04 LTS (Python 3.12) or Debian 13; unacceptable adoption friction. | **Rejected** |
| **Python 3.13+** | Access to modern REPL and free-threaded runtime; modern type features. | Excludes Python 3.12, which remains the default Python on long-term enterprise Linux distributions until 2028+. | **Rejected** |
| **Python 3.11 - 3.14** | Covers canonical 1.1.6 baseline environment. | **Incompatible with Django 6.x**; Django 6.0 dropped Python 3.10 and 3.11. Supporting Python 3.11 for Django-Start 2.0 would require disabling Django 6 generation on 3.11, creating user confusion. | **Rejected for 2.0 Runtime** |
| **Python 3.12 - 3.14** (Selected) | Exactly matches the intersection of supported Django 5.2 LTS and Django 6.1; aligns with current enterprise Linux; manageable CI cost. | Requires deprecating Python 3.11 for the 2.0 runtime (retained only for legacy characterization tests). | **ACCEPTED** |

### 2.2 Python Minimum Version Decision
- **Minimum Supported Python**: **Python 3.12**
- **Packaging Declaration**: `requires-python = ">=3.12"` in `pyproject.toml`.
- **Legacy Characterization Suite Policy**: The 45 baseline characterization tests remain verified against Python 3.11 in isolated CI until the legacy runtime is fully retired in 2.0.

### 2.3 Preview Python Policy
- **Python 3.15 (Release Candidate)**:
  - Exercised via scheduled, non-blocking experimental CI jobs (`continue-on-error: true`).
  - Prohibited from becoming the default target or minimum requirement until at least 3 months after official 3.15.0 final release and after both Django and Click publish verified compatible wheels.

### 2.4 Upstream Version Drop Policy
- A Python minor release will be marked for deprecation when:
  1. The Python Security Response Team declares official End of Life (EOL), OR
  2. All supported Django release lines drop support for that Python version.
- Dropping a Python version requires a minor release bump in Django-Start (e.g. 2.1.0) and 60 days advance deprecation notice in CLI output.

### 2.5 Python 3.11 Legacy Characterization Lifecycle vs `djstartlib` Compatibility-Shim Testing

Django-Start maintains an explicit separation between legacy characterization test execution and backward-compatibility shim support:

1. **Python 3.11 Legacy Characterization Lifecycle**:
   - **Scope**: Covers the 45 baseline characterization tests validating the historical, unedited `djstartlib` 1.1.6 code.
   - **Runtime**: Executed strictly on **Python 3.11** in an isolated CI container.
   - **Purpose**: Provides regression protection and documents historical contracts and defects.
   - **Retirement Gates**: Eligible for full retirement at or after Django-Start 2.0 General Availability (GA) when explicit criteria are met:
     - All 2.0 replacement use cases and CLI commands are implemented and verified.
     - Functional parity is formally validated with zero regressions against characterized contracts.
     - Python 3.11 CI jobs are retired without impacting any 2.x codebase components.
2. **`djstartlib` Compatibility Redirect Shim Testing**:
   - **Scope**: Tests the deprecated redirect package that maps legacy imports (`djstartlib.*`) to new 2.0 modules (`django_start.*`) and emits `DeprecationWarning`.
   - **Runtime**: Executed across all **supported Django-Start 2.x Python versions** (Python 3.12, 3.13, and 3.14).
   - **Purpose**: Validates public contract preservation and upgrade paths for consumers running supported 2.x Python interpreters.
   - **Retirement Schedule**: Maintained throughout the entire Django-Start 2.x series; scheduled for formal deletion in Django-Start 3.0.0.

---

## 3. Django Support Policy

### 3.1 Supported Django Release Lines & DEP 20 Transition

Django-Start 2.0 operates during a major transition in Django release governance:

1. **Current Supported Tracks**:
   - **Modern Feature Track (Default)**: **Django 6.1** (final released August 5, 2026; patch release 6.1.1 published September 2, 2026). Supported until December 2027.
   - **Long-Term Support Track (LTS)**: **Django 5.2 LTS** (released April 2025; patch release 5.2.17). Supported until April 2028.
   - **Upcoming Final LTS**: **Django 6.2 LTS** (scheduled April 2027). Supported until April 2030.
2. **DEP 20 and the CalVer Era**:
   - Under Django Enhancement Proposal 20 (DEP 20), the Django Project adopts annual Calendar Versioning (`YYYY.N`), starting with **Django 2028.0 in January 2028**.
   - Django 6.2 LTS is the final designated Long-Term Support release under the legacy model.
   - Post-6.2, distinct LTS designations are retired; every annual CalVer release carries a uniform 3-year support window (approx. 16 months active bugfixes followed by security fixes up to 36 months total).
3. **`lts` as a Transitional Concept**:
   - In Django-Start 2.0, the CLI flag value `--django lts` is maintained as a **transitional alias** for stability-conscious environments, mapping to Django 5.2 LTS (and later 6.2 LTS).
   - The underlying architecture treats release tracks orthogonally from archetype profiles, preparing for uniform annual release tracking under CalVer.

### 3.2 Reconciliation of Profile Archetypes vs Framework Tracks

Django-Start 2.0 enforces strict separation between architectural archetypes and framework release tracks:

- **Profile Dimension (`--profile`)**: Governs project topology, installed apps, template scaffolding, and configuration patterns.
  - `standard` (Default): Full-featured starter with SQLite, core application, static assets, templates, and health check.
  - `minimal`: Streamlined layout with minimal boilerplate for micro-services or lightweight utilities.
  - `api`: Django REST Framework starter with serialized endpoints, API router structure, and test suite.
  - `production`: Hardened deployment layout with environment-based settings split, Dockerfile, and production WSGI/ASGI configuration.
- **Framework Track Dimension (`--django`)**: Governs the Django version line and patch resolution.
  - `latest` (Default): Resolves to latest tested stable feature release (currently Django 6.1.1).
  - `lts` (Transitional): Resolves to active stable LTS release (currently Django 5.2.17).
  - `<version>`: Explicit version specification (e.g. `6.1`, `5.2`, `6.1.1`, `5.2.17`).
- **Orthogonality**: Any profile can pair with any framework track (e.g., `--profile api --django lts`, `--profile minimal --django latest`).

### 3.3 Dependency Pinning & Lockfile Policy

In accordance with product invariants:
- **Published Manifest Range**: Generated projects declare compatible bounded version ranges in their primary manifest (e.g., `dependencies = ["Django>=6.1,<6.2"]` or `["Django>=5.2,<5.3"]` in `pyproject.toml` or `requirements.in`).
- **Deterministic Provisioning Pin**: Scaffolding execution provisions the virtual environment using tested, exact patch releases (e.g., `Django==6.1.1`, `Django==5.2.17`).
- **Lock Strategy Evaluation**: The exact snapshot lockfile format for generated projects (evaluating traditional `requirements.txt` / pip-tools snapshots, PEP 751 `pylock.toml`, and tool-specific formats like `uv.lock`) is governed by the pending lock strategy evaluation. Unbounded `pip install django` is permanently prohibited.

---

## 4. Re-Architected Four-Tier CI Matrix

The CI validation pipeline is organized into four tiers, each verifying specific compatibility properties:

| Tier | Name | Frequency & Policy | Scope | Compatibility Properties Proven |
|---|---|---|---|---|
| **Tier 1** | **PR Blocking Linux** | Every PR (Blocking) | Ubuntu 24.04+<br>Python 3.12, 3.13, 3.14<br>Django 5.2 LTS, 6.1 | Primary Linux server compatibility; core use cases; unit test suite; integration scaffolding; generated-project verification (`manage.py check`); Ruff linting and formatting; mypy strict typing. |
| **Tier 2** | **PR Blocking Cross-Platform Smoke** | Every PR (Blocking) | macOS 14+, Windows 11 / Server 2022<br>Python 3.12, 3.14<br>Django 6.1 | Cross-platform filesystem path separators (`/` vs `\`); virtual environment directory layout (`bin/` vs `Scripts/`); argument vector serialization without shell invocation; Windows `.exe` executable resolution; atomic rename safety. |
| **Tier 3** | **Scheduled Full Matrix** | Weekly & Pre-Release (Blocking on Release) | All OS (Ubuntu, macOS, Windows)<br>All Python (3.12, 3.13, 3.14)<br>All Tracks (5.2 LTS, 6.1)<br>All Profiles (`standard`, `minimal`, `api`, `production`) | Complete Cartesian compatibility; multi-profile template compilation; recipe dependency conflict detection; offline generation reproducibility; package wheel distribution installation (`python -m build` artifact verification). |
| **Tier 4** | **Canary Experimental** | Weekly Cron (`continue-on-error: true`) | Ubuntu Latest<br>Python 3.15 (RC / Preview)<br>Django 6.1 & Django `main` branch | Forward compatibility with upcoming Python language and AST changes; early detection of upstream deprecation warnings; verification of upcoming Django releases before final publication. |
| **Legacy** | **Legacy Characterization Gate** | PR & Main (Isolated) | Ubuntu 24.04+<br>Python 3.11<br>Historical 1.1.6 baseline | Regression baseline verification for original 45 characterization tests against untouched `djstartlib/` 1.1.6 code. Retained until 2.0 GA retirement gates are met. |

---

## 5. Detailed Compatibility Proof Matrix by Tier

### 5.1 Tier 1: Primary Linux Validation Matrix
Runs synchronously on all pull requests. All jobs must pass before merge.

| Job ID | OS | Python | Django Track | Exact Pin | Proven Compatibility Property |
|---|---|---|---|---|---|
| `t1-py312-dj61` | Ubuntu 24.04 | 3.12 | Modern Feature (Default) | Django 6.1.1 | Verifies minimum supported Python 3.12 on modern Django feature track; full CLI use case coverage. |
| `t1-py312-dj52` | Ubuntu 24.04 | 3.12 | LTS (Transitional) | Django 5.2.17 | Verifies stability track under minimum supported Python; ensures backwards-compatible template generation. |
| `t1-py313-dj61` | Ubuntu 24.04 | 3.13 | Modern Feature | Django 6.1.1 | Verifies Python 3.13 runtime behavior, modern REPL, and threading enhancements with Django 6.1. |
| `t1-py313-dj52` | Ubuntu 24.04 | 3.13 | LTS (Transitional) | Django 5.2.17 | Verifies Python 3.13 runtime behavior with Django 5.2 LTS. |
| `t1-py314-dj61` | Ubuntu 24.04 | 3.14 | Modern Feature | Django 6.1.1 | Verifies latest stable Python 3.14 with modern Django; tests deferred annotations (PEP 649/749). |
| `t1-py314-dj52` | Ubuntu 24.04 | 3.14 | LTS (Transitional) | Django 5.2.17 | Verifies Python 3.14 runtime behavior with Django 5.2 LTS. |

### 5.2 Tier 2: Cross-Platform Smoke Matrix
Runs synchronously on all pull requests. Fast-fail smoke verification on non-Linux platforms.

| Job ID | OS | Python | Django Track | Proven Compatibility Property |
|---|---|---|---|---|
| `t2-macos-py312` | macOS 14 | 3.12 | Django 6.1.1 | Verifies POSIX macOS environment provisioning, framework path resolution, and CLI generation. |
| `t2-macos-py314` | macOS 14 | 3.14 | Django 6.1.1 | Verifies latest Python on macOS ARM64 runner with Django 6.1. |
| `t2-win-py312` | Windows 2022 | 3.12 | Django 6.1.1 | Verifies Windows Scripts/ directory resolution, python.exe executable lookup, backslash path normalization. |
| `t2-win-py314` | Windows 2022 | 3.14 | Django 6.1.1 | Verifies latest Python on Windows; validates atomic replace file handling under Windows filesystem semantics. |

### 5.3 Tier 3: Scheduled Full Matrix
Runs weekly on schedule and on release candidate branches. Exercises all profiles and versions.

- **OS Matrix**: Ubuntu 24.04, macOS 14, Windows Server 2022
- **Python Matrix**: 3.12, 3.13, 3.14
- **Django Tracks**: Modern Feature (6.1.1), LTS (5.2.17)
- **Profile Matrix**: `standard`, `minimal`, `api`, `production`
- **Proven Properties**: Complete Cartesian validation, template syntax compilation across all profiles, wheel package build (`build`) and clean install verification into virgin virtual environment.

### 5.4 Tier 4: Canary / Experimental Upstream Matrix
Runs weekly on schedule. Non-blocking (`continue-on-error: true`).

- **OS**: Ubuntu Latest
- **Python**: Python 3.15 (Release Candidate / Dev)
- **Django**: Django 6.1 and Django upstream development branch (`main`)
- **Proven Properties**: Early alert system for upstream syntax deprecations, C API changes, and future Django framework changes before public release.
