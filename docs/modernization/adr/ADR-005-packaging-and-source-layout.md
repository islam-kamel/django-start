# ADR-005: Packaging Modernization and Source Tree Layout

## Status
Accepted

## Context
Django-Start 1.1.6 used a legacy flat package layout (`djstartlib/` in repository root) coupled with `setup.py` and `setup.cfg`.
This packaging layout led to severe technical debt:
1. Production code in `djstartlib/models/__init__.py` mutated `sys.path` globally (`sys.path.append(...)`) so that internal modules could use top-level bare imports (`from models import ...`).
2. Flat layout allows tests to import local unbuilt code rather than the installed package, masking packaging defects.
3. Metadata was duplicated across `setup.cfg`, `version.py`, and `pyproject.toml`.

Regarding packaging standards, direct invocation of `setup.py` commands (such as `python setup.py install`, `develop`, or `sdist`) has been formally deprecated by the Python Packaging Authority (PyPA) in favor of standard build tools (`pip`, `build`, PEP 517). However, `setup.py` as a file is not prohibited by PyPA; build backends still allow it when imperative build steps are required. Consolidating all project configuration into declarative PEP 621 `pyproject.toml` and eliminating `setup.py` entirely is a deliberate project architectural decision to achieve a transparent, reproducible, declarative packaging baseline.

## Decision
1. Adopt the standard PyPA **`src/` layout**:
   - Production source moves to `src/django_start/`.
   - All internal imports must be fully qualified (`from django_start.domain import ...`).
   - `sys.path.append` statements in package `__init__.py` files will be eliminated.
2. Standardize packaging metadata strictly under **PEP 621** in `pyproject.toml`:
   - Eliminate `setup.cfg` and `setup.py` in favor of pure declarative configuration.
   - Use `setuptools>=84.0` with `setuptools.build_meta` backend.
3. Preserve distribution identity and PyPI naming:
   - **PyPI Distribution Name**: Retain `django-start-automate` on PyPI to prevent name collisions, preserve user trust, avoid breaking automated installation scripts, and maintain continuous release history.
   - **Import Package Name**: Adopt `django_start` as the idiomatic, modern Python import namespace.
4. Backward Compatibility Shim for `djstartlib`:
   - Provide an explicit redirect shim under `src/djstartlib/` containing:
     - `djstartlib/__init__.py`
     - `djstartlib/models/__init__.py`
     - `djstartlib/models/utils.py`
     - `djstartlib/version.py`
   - Each module re-exports the corresponding modern symbols from `django_start` and issues a `DeprecationWarning` with `stacklevel=2` notifying callers of the upcoming deprecation.
   - This compatibility layer will be maintained throughout the Django-Start 2.x lifecycle and is scheduled for final removal in Django-Start 3.0.0.

## Alternatives Evaluated
- **Keep Flat Layout (`djstartlib/`)**: Rejected because it violates PyPA best practices and invites path-shadowing defects in CI.
- **Rename Distribution Package on PyPI**: Rejected because changing the distribution name would surrender PyPI package authority, create user confusion, risk name squatting, and break established installation workflows.
- **Migrate to Flit or Hatchling**: Evaluated, but Setuptools 84.0+ provides complete PEP 621 compliance while preserving existing build tool familiarity.

## Consequences
- Positive: Eliminates import pollution and `sys.path` manipulation; ensures test suite imports the real installed wheel; centralizes configuration in a single file; preserves PyPI reputation and installation continuity; provides a graceful deprecation bridge for legacy consumers.
- Negative: Requires updating test imports and maintaining compatibility redirect modules across the 2.x lifecycle.

## Migration Impact
- Handled during Phase 1 (Packaging Foundation).
