# Django-Start 2.0 Modernization Documentation Index

This directory contains the complete research, discovery, architecture design, and migration specifications for the **Django-Start 2.0** modernization initiative.

---

## Specifications & Research Reports

1. [Current Architecture & Technical Debt Audit](current-architecture.md)
   - Component-by-component analysis of 1.1.6 (`djstartlib/**`)
   - Reconstructed architecture map and execution traces
   - Contract Migration Matrix categorizing all 31 baseline contracts
   - Comprehensive technical debt catalog

2. [Python & Django Ecosystem Research (September 2026)](ecosystem-research-2026.md)
   - Primary-source research on Python releases (Python 3.12 through 3.15 RC)
   - Official Django support roadmap (Django 5.2 LTS, 6.0, 6.1, 6.2 LTS)
   - Ecosystem status for Click, Pytest, Ruff, Mypy, and PyPA packaging tools
   - Epistemic classification: `[FACT]`, `[RECOMMENDATION]`, `[FUTURE POSSIBILITY]`, `[KNOWN UNKNOWN]`

3. [Compatibility Matrix & Support Policy](compatibility-matrix.md)
   - Multi-tier OS and Python/Django matrix
   - Python support policy (Python 3.12 - 3.14)
   - Django support policy (Django 6.1 default + Django 5.2 LTS)
   - Deterministic version pinning and upstream version drop policies

4. [Target Product Architecture](target-architecture.md)
   - Clean, layered architecture: Presentation -> Application -> Domain -> Ports -> Infrastructure
   - Safe `CommandRunner` subprocess boundary (`shell=False`, argument lists, structured result)
   - Safe `FileSystem` boundary (explicit UTF-8, atomic writes, non-destructive guards, rollback)
   - Controlled template generation replacing fragile bracket/comment searching
   - Recipe & Profile engine (`standard`, `lts`, `api`, `minimal`)
   - Lifecycle commands (`new`, `add`, `doctor`, `check`, `recipe`, `--version`)
   - Typed application exception hierarchy and standardized exit codes

5. [Dependency Modernization & Tooling Strategy](dependency-modernization.md)
   - Complete dependency inventory and upgrade roadmap
   - Evaluation of Quality Tooling (Ruff + Mypy transition)
   - Packaging architecture: PEP 517/621, `src/` layout, `django-start-automate` vs `django_start`

6. [Security Model & Threat Review](security-model.md)
   - Threat & Mitigation Matrix across all attack surfaces
   - Elimination of shell injection, path traversal, and unpinned dependencies
   - Project and application identifier validation rules
   - Sandbox permissions and network isolation invariants

7. [Phased Migration Roadmap & Testing Architecture](migration-roadmap.md)
   - Multi-tier testing pyramid (characterization, unit, use-case, generated-project smoke)
   - CI workflow architecture (blocking PR pipeline, scheduled matrix, release checks)
   - 9-phase sequential implementation roadmap with explicit gates and rollback criteria

---

## Architecture Decision Records (ADRs)

| ADR | Title | Summary Decision |
|---|---|---|
| [ADR-001](adr/ADR-001-python-support-policy.md) | Python Support Policy | Support Python 3.12 - 3.14; retire Python <= 3.11 for 2.0 runtime. |
| [ADR-002](adr/ADR-002-django-support-policy.md) | Django Support Policy | Support Django 6.1 (default) and Django 5.2 LTS; strictly pin tested patch releases. |
| [ADR-003](adr/ADR-003-cli-framework-and-commands.md) | CLI Framework & Commands | Retain Click (8.5+); adopt subcommands (`new`, `add`, `doctor`, `check`); legacy compat shim. |
| [ADR-004](adr/ADR-004-future-quality-tooling.md) | Future Quality Tooling | Transition to Ruff (format + lint) and Mypy (strict typing) in dedicated Phase 1. |
| [ADR-005](adr/ADR-005-packaging-and-source-layout.md) | Packaging & Source Layout | Adopt `src/django_start/` layout; PEP 621 `pyproject.toml`; `djstartlib` compatibility redirect. |
| [ADR-006](adr/ADR-006-command-runner-boundary.md) | CommandRunner Boundary | Strictly prohibit `shell=True`; use typed argument sequences and fake runner for tests. |
| [ADR-007](adr/ADR-007-filesystem-safety-and-atomicity.md) | Filesystem Safety | Mandatory UTF-8 encoding; atomic file replacement; non-destructive conflict aborts. |
| [ADR-008](adr/ADR-008-django-project-generation-engine.md) | Django Generation Engine | Controlled project templates and declarative recipes replacing fragile bracket matching. |
| [ADR-009](adr/ADR-009-recipe-and-profile-architecture.md) | Recipe & Profile Architecture | Modular declarative recipes (`standard`, `lts`, `api`, `minimal`); no executable third-party code. |
| [ADR-010](adr/ADR-010-version-and-update-strategy.md) | Version & Update Strategy | Use `importlib.metadata`; permanently remove self-update; diagnostic check in `doctor`. |
