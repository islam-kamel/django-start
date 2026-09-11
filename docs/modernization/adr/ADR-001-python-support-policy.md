# ADR-001: Python Support Policy for Django-Start 2.0

## Status
Accepted

## Context
Django-Start 1.1.6 was developed with support for Python 3.7 through 3.11, with Python 3.11 established as the canonical baseline environment for reproducing characterization tests.

In September 2026, the upstream CPython release landscape and support windows are:
- **Python 3.14**: Current stable release (released October 7, 2025; PEP 745). Active bugfix support continues through October 2027, with extended security support through October 2030.
- **Python 3.13**: Supported maintenance release (released October 7, 2024; PEP 719). Active bugfix support continues through October 2026, with security support through October 2029.
- **Python 3.12**: Supported security-only release (released October 2, 2023; PEP 693). Active bugfix ended in April 2025; security support continues through October 2028.
- **Python 3.11**: Security-only release (released October 24, 2022; PEP 664), with security support concluding in October 2027.
- **Python 3.10 and older**: Python 3.7 through 3.9 have reached End of Life (EOL). Python 3.10 reaches EOL in October 2026.
- **Python 3.15**: Pre-release preview (PEP 790), scheduled for final release in October 2026.

Crucially, Django 6.0 and 6.1 (the primary modern targets for Django-Start 2.0) dropped support for Python 3.10 and Python 3.11, requiring Python 3.12 or newer.

## Decision
1. Django-Start 2.0 will officially support **Python 3.12, 3.13, and 3.14**.
2. The package will declare `requires-python = ">=3.12"` in `pyproject.toml`.
3. Clearly separate testing lifecycles into distinct tracks:
   - **Python 3.11 Characterization Lifecycle**: Retained in isolated CI jobs strictly to execute the legacy 1.1.6 characterization test suite and protect the baseline behavior during migration. Python 3.11 is eligible for retirement at or after 2.0 GA only when explicit retirement gates are met:
     - Equivalent successor test coverage exists in the 2.0 test suite.
     - An independent `djstartlib` compatibility suite exists.
     - No active migration verification depends on 1.1.6 baseline tests.
     - Removing Python 3.11 does not reduce empirical evidence for supported compatibility claims.
   - **`djstartlib` Compatibility-Shim Testing Lifecycle**: Verifies the public contract of the backward-compatibility redirect shim using supported 2.x Python versions (Python 3.12, 3.13, and 3.14). This compatibility layer and its tests will retire in Django-Start 3.0.
4. Python 3.15 (preview) will be monitored via non-blocking scheduled CI canary jobs, but will not become an officially supported tier until after its final release and verified compatibility.

## Alternatives Evaluated
- **Support Python 3.11 - 3.14 at Runtime**: Rejected because Django 6.x cannot be installed or executed on Python 3.11, which would force the CLI to disable its primary modern feature set when running under Python 3.11.
- **Support Python 3.14 Only**: Rejected because it prematurely cuts off production enterprise Linux environments (such as Ubuntu 24.04 LTS) running Python 3.12.
- **Support Python 3.13+**: Rejected because Python 3.12 remains within security support until October 2028 and is widely deployed.

## Consequences
- Positive: Enables native modern typing features (PEP 695 type parameter syntax, PEP 701 f-strings), eliminates Python 3.10/3.11 compatibility polyfills, and matches Django 6.x requirements cleanly.
- Negative: Users constrained to Python 3.11 or older at runtime must continue using Django-Start 1.1.6.

## Migration Impact
- Requires updating the CI matrix to test the 2.0 runtime against Python 3.12, 3.13, and 3.14, while isolating Python 3.11 strictly for characterization tests.
- Handled during Phase 1 (Packaging Foundation).
