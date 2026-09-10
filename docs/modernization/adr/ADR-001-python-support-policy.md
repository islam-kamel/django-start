# ADR-001: Python Support Policy for Django-Start 2.0

## Status
Accepted

## Context
Django-Start 1.1.6 was developed with support for Python 3.7 through 3.11, with Python 3.11 established as the canonical baseline environment for reproducing characterization tests.
In September 2026, Python 3.7 through 3.10 have reached or are reaching End of Life (EOL). Python 3.14 is the current stable release, Python 3.13 and 3.12 are supported, and Python 3.15 is in Release Candidate (PEP 790).
Crucially, Django 6.0 and 6.1 (the primary modern target for Django-Start 2.0) dropped support for Python 3.10 and Python 3.11, requiring Python 3.12 or newer.

## Decision
1. Django-Start 2.0 will officially support **Python 3.12, 3.13, and 3.14**.
2. The package will declare `requires-python = ">=3.12"` in `pyproject.toml`.
3. Python 3.11 support will be retired for the 2.0 runtime, but retained in isolated CI jobs strictly to execute the legacy characterization test suite until the legacy codebase is phased out.
4. Python 3.15 (preview) will be monitored via non-blocking scheduled CI canary jobs, but will not become a supported tier until post-final release.

## Alternatives Evaluated
- **Support Python 3.11 - 3.14**: Rejected because Django 6.x cannot be installed or executed on Python 3.11, which would force the CLI to disable its primary modern feature set when running under Python 3.11.
- **Support Python 3.14 Only**: Rejected because it prematurely cuts off production enterprise Linux environments (such as Ubuntu 24.04 LTS) running Python 3.12.
- **Support Python 3.13+**: Rejected because Python 3.12 remains within security support until October 2028.

## Consequences
- Positive: Enables native modern typing features (PEP 695 type parameter syntax, PEP 701 f-strings), eliminates Python 3.10/3.11 compatibility polyfills, and matches Django 6.x requirements cleanly.
- Negative: Users constrained to Python 3.11 or older must continue using Django-Start 1.1.6.

## Migration Impact
- Requires updating CI matrix to test against Python 3.12, 3.13, and 3.14.
- Handled during Phase 2 (Packaging Foundation).
