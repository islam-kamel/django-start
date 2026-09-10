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

---

## 3. Django Support Policy

### 3.1 Supported Django Release Lines

Django-Start 2.0 supports two distinct Django tracks:

1. **Modern Feature Track (Default)**:
   - **Target**: **Django 6.1** (latest stable feature release)
   - **Characteristics**: Latest ORM features, asynchronous capabilities, modernized template tags, Python 3.12 - 3.14.
   - **CLI Invocation**: Default behavior for `django-start new <project>`.
2. **Long-Term Support Track (LTS)**:
   - **Target**: **Django 5.2 LTS**
   - **Characteristics**: Enterprise stability, support guaranteed until April 2028, Python 3.12 - 3.14.
   - **CLI Invocation**: Explicitly selected via `django-start new <project> --django 5.2` or `--profile lts`.

### 3.2 Deterministic Version Pinning Policy

In accordance with product invariant 2.2:
- Unbounded commands such as `pip install django` are strictly forbidden.
- For each supported release line, Django-Start maintains a tested, exact patch release lock in its recipe registry.
- As of September 2026:
  - `django-6.1`: Pins `Django==6.1.1`
  - `django-5.2-lts`: Pins `Django==5.2.17`
- Generation requires network access only when explicitly requested; if wheels are pre-cached, installation remains deterministic and offline-capable.

---

## 4. Full Compatibility Matrix

| Operating System | Python Version | Django Version | Status in Django-Start 2.0 | CI Pipeline Tier |
|---|---|---|---|---|
| **Ubuntu 24.04+** | 3.12 | Django 5.2 LTS | Supported | Tier 1 (PR Blocking) |
| **Ubuntu 24.04+** | 3.12 | Django 6.1 | Supported (Default) | Tier 1 (PR Blocking) |
| **Ubuntu 24.04+** | 3.13 | Django 5.2 LTS | Supported | Tier 1 (PR Blocking) |
| **Ubuntu 24.04+** | 3.13 | Django 6.1 | Supported | Tier 1 (PR Blocking) |
| **Ubuntu 24.04+** | 3.14 | Django 5.2 LTS | Supported | Tier 1 (PR Blocking) |
| **Ubuntu 24.04+** | 3.14 | Django 6.1 | Supported | Tier 1 (PR Blocking) |
| **macOS 14+** | 3.12, 3.13, 3.14 | Django 6.1 | Supported | Tier 2 (PR Blocking Smoke) |
| **Windows 11 / Server 2022** | 3.12, 3.13, 3.14 | Django 6.1 | Supported | Tier 2 (PR Blocking Smoke) |
| **Any OS** | 3.15 (Preview) | Django 6.1 | Experimental | Tier 3 (Scheduled Non-blocking) |
| **Any OS** | 3.11 | Any Django | Unsupported for 2.0 (Characterization Only) | Legacy Gate Only |

---

## 5. Cross-Platform Tier Definitions

### Tier 1: Primary Linux Validation (Ubuntu)
- Runs on every pull request.
- Executes full unit, integration, scaffold orchestration, and generated-project verification (`python manage.py check`).
- Executes full pre-commit, linting, formatting, and mypy type checking.

### Tier 2: Native Cross-Platform Validation (macOS & Windows)
- Runs on PR merge to main and on release branches.
- Executes virtual environment creation, path resolution, and CLI generation smoke tests on native macOS and Windows runners.
- Protects against path separator assumptions (`os.sep` vs `/`) and `.exe` script resolution quirks.

### Tier 3: Canary / Upstream Validation (Python 3.15 RC)
- Runs weekly on a cron schedule.
- Detects upstream deprecation warnings and syntax changes before they reach final release.
