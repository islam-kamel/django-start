# ADR-005: Packaging Modernization and Source Tree Layout

## Status
Accepted

## Context
Django-Start 1.1.6 used a legacy flat package layout (`djstartlib/` in repository root) coupled with `setup.py` and `setup.cfg`.
This packaging layout led to severe technical debt:
1. Production code in `djstartlib/models/__init__.py` mutated `sys.path` globally (`sys.path.append(...)`) so that internal modules could use top-level bare imports (`from models import ...`).
2. Flat layout allows tests to import local unbuilt code rather than the installed package, masking packaging defects.
3. Metadata was duplicated across `setup.cfg`, `version.py`, and `pyproject.toml`.

## Decision
1. Adopt the standard PyPA **`src/` layout**:
   - Production source moves to `src/django_start/`.
   - All imports must be fully qualified (`from django_start.domain import ...`).
   - `sys.path.append` statements in package `__init__.py` files will be eliminated.
2. Standardize packaging metadata strictly under **PEP 621** in `pyproject.toml`:
   - Eliminate `setup.cfg` and `setup.py`.
   - Use `setuptools>=84.0` with `setuptools.build_meta` backend.
3. Preserve distribution identity:
   - **PyPI Distribution Name**: `django-start-automate` (retains historical releases and PyPI authority).
   - **Import Package Name**: `django_start` (modern, idiomatic Python naming).
4. Backward Compatibility Shim:
   - Provide a temporary package alias `djstartlib` in `src/djstartlib/` that re-exports `django_start` symbols and raises a `DeprecationWarning` upon import.

## Alternatives Evaluated
- **Keep Flat Layout (`djstartlib/`)**: Rejected because it violates PyPA best practices and invites path-shadowing defects in CI.
- **Rename Distribution Package on PyPI**: Rejected because it breaks established package installation paths for existing users.
- **Migrate to Flit or Hatchling**: Evaluated, but Setuptools 84.0+ provides complete PEP 621 compliance while preserving existing build tool familiarity.

## Consequences
- Positive: Eliminates import pollution and `sys.path` manipulation; ensures test suite imports the real installed wheel; centralizes configuration in a single file.
- Negative: Requires updating test imports and creating a temporary compatibility shim for legacy users.

## Migration Impact
- Handled during Phase 2 (Packaging Foundation).
