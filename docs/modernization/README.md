# Django-Start 2.0 Modernization Documentation Index

This directory contains the complete research, discovery, architecture design, and migration specifications for the **Django-Start 2.0** modernization initiative.

---

## Specifications & Research Reports

1. [Current Architecture & Technical Debt Audit](current-architecture.md)
   - Component-by-component analysis of 1.1.6 (`djstartlib/**`)
   - Reconstructed architecture map and execution traces
   - Contract Migration Matrix categorizing all 31 baseline contracts
   - Packaging transition to `src/django_start/` under `django-start-automate` with `src/djstartlib/` compatibility shim
   - Comprehensive technical debt catalog

2. [Python & Django Ecosystem Research (September 2026)](ecosystem-research-2026.md)
   - Primary-source research on Python releases (Python 3.12 through 3.15 preview)
   - Official Django support roadmap (Django 5.2 LTS, Django 6.1 released August 5, 2026 / 6.1.1 September 2, 2026, Django 6.2 LTS April 2027, and accepted DEP 20 annual Calendar Versioning transition for 2028.0 with uniform 3-year support)
   - Ecosystem status for Click, Pytest, Ruff, Mypy, and PyPA packaging tools
   - Epistemic classification: `[FACT]`, `[RECOMMENDATION]`, `[FUTURE POSSIBILITY]`, `[KNOWN UNKNOWN]`

3. [Compatibility Matrix & Support Policy](compatibility-matrix.md)
   - Multi-tier OS and Python/Django matrix
   - Python support policy (Python 3.12 - 3.14 runtime, Python 3.11 isolated characterization suite)
   - Django support policy (Django 6.1 default + Django 5.2 LTS)
   - Deterministic version pinning and upstream version drop policies

4. [Target Product Architecture](target-architecture.md)
   - Clean, layered architecture: Presentation -> Application -> Domain -> Ports -> Infrastructure
   - Safe `CommandRunner` subprocess boundary (`shell=False`, argument lists, structured result, zero shell execution)
   - Safe `FileSystem` boundary (explicit UTF-8, atomic writes, non-destructive guards, transactional rollback)
   - Controlled template generation replacing fragile bracket/comment searching
   - Recipe & Profile engine: orthogonal archetype profiles (`standard`, `minimal`, `api`, `production`) combinable with framework release tracks (`--django 6.1` default, `--django 5.2` / `--django lts`)
   - Lifecycle commands (`new`, `add`, `doctor`, `check`, `recipe`, `--version`)
   - Typed application exception hierarchy and standardized exit codes

5. [Dependency Modernization & Tooling Strategy](dependency-modernization.md)
   - Complete dependency inventory and upgrade roadmap
   - Evaluation of Quality Tooling (Ruff + Mypy transition)
   - Packaging architecture: PEP 517/621, `src/` layout, `django-start-automate` distribution vs `django_start` import package, with `djstartlib` compatibility redirect shim

6. [Security Model & Threat Review](security-model.md)
   - Threat & Mitigation Matrix across all attack surfaces
   - Elimination of shell injection, path traversal, and unpinned dependencies
   - Project and application identifier validation rules
   - Defensive invariants: zero-shell guarantee, explicit network invariant, sandbox permissions, and safe staging

7. [Phased Migration Roadmap & Testing Architecture](migration-roadmap.md)
   - Multi-tier testing pyramid (Python 3.11 characterization baseline, unit, use-case, generated-project smoke)
   - CI workflow architecture (blocking PR pipeline, scheduled cross-platform matrix, release verification checks)
   - 9-phase sequential implementation roadmap starting with Phase 1: Packaging Foundation & `src/` Layout followed by Phase 2: Modern Quality Tooling (Ruff + Mypy), with explicit gates and rollback criteria

---

## Architecture Decision Records (ADRs)

| ADR | Title | Summary Decision |
|---|---|---|
| [ADR-001](adr/ADR-001-python-support-policy.md) | Python Support Policy | Support Python 3.12 - 3.14 runtime; isolated Python 3.11 characterization suite eligible for retirement at or after 2.0 GA only after documented retirement gates are satisfied. |
| [ADR-002](adr/ADR-002-django-support-policy.md) | Django Support Policy | Support Django 6.1 (default, released Aug 2026) and Django 5.2 LTS; specify compatible bounded ranges with reproducible offline lock strategy; accepted DEP 20 annual Calendar Versioning transition. |
| [ADR-003](adr/ADR-003-cli-framework-and-commands.md) | CLI Framework & Commands | Retain Click (8.5+); adopt subcommands (`new`, `add`, `doctor`, `check`); legacy compat shim. |
| [ADR-004](adr/ADR-004-future-quality-tooling.md) | Future Quality Tooling | Transition to Ruff (format + lint) and Mypy (strict typing) in dedicated Phase 2 (post-packaging). |
| [ADR-005](adr/ADR-005-packaging-and-source-layout.md) | Packaging & Source Layout | Adopt `src/django_start/` layout; PEP 621 `pyproject.toml`; `django-start-automate` distribution with `src/djstartlib/` compatibility redirect shim in Phase 1. |
| [ADR-006](adr/ADR-006-command-runner-boundary.md) | CommandRunner Boundary | Strictly prohibit `shell=True`; use typed argument sequences and fake runner for tests. |
| [ADR-007](adr/ADR-007-filesystem-safety-and-atomicity.md) | Filesystem Safety | Mandatory UTF-8 encoding; atomic file replacement; non-destructive conflict aborts. |
| [ADR-008](adr/ADR-008-django-project-generation-engine.md) | Django Generation Engine | Controlled project templates and declarative recipes replacing fragile bracket matching. |
| [ADR-009](adr/ADR-009-recipe-and-profile-architecture.md) | Recipe & Profile Architecture | Modular declarative recipes with orthogonal archetype profiles (`standard`, `minimal`, `api`, `production`) and framework release tracks; no executable third-party code. |
| [ADR-010](adr/ADR-010-version-and-update-strategy.md) | Version & Update Strategy | Use `importlib.metadata`; permanently remove self-update; diagnostic check in `doctor`. |
