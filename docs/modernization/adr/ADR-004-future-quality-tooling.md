# ADR-004: Future Quality Tooling Transition

## Status
Accepted

## Context
The repository currently enforces a green pre-commit baseline using:
- Black 22.8.0 (line-length 79)
- Flake8 5.0.4 (configured via `setup.cfg`)
- Pyupgrade 2.38.2 (`--py36-plus`)
- pre-commit-hooks v4.3.0 under Python 3.10 hook environment.

While this configuration is currently green and passing, it relies on multiple fragmented tools, slower Python-based linters, older tool versions from 2022, and dual configuration files (`setup.cfg` and `.pre-commit-config.yaml`).

## Decision
1. In a dedicated Phase 1 migration task, transition the repository's formatting and linting suite to **Ruff** (`ruff>=0.16,<1`).
2. Consolidate formatting and linting configuration into standard `pyproject.toml` under `[tool.ruff]`.
3. Configure Ruff to emulate Black formatting conventions while enforcing standard PEP 8, import sorting (isort), and pyupgrade rules natively.
4. Introduce **Mypy** (`mypy>=2.3,<3`) for strict static type checking of all new 2.0 code in `src/django_start/`.
5. Retain pre-commit as the local Git hook orchestrator, updating hook repositories to modern releases.

## Alternatives Evaluated
- **Keep Black + Flake8 + Pyupgrade**: Rejected because of configuration fragmentation, slower CI performance, and lack of native `pyproject.toml` support in Flake8.
- **Adopt Ruff for Linting but keep Black for Formatting**: Rejected because Ruff's formatter has achieved complete stability and parity with Black, rendering dual-tool execution redundant.

## Consequences
- Positive: Single Rust binary replaces 3 distinct Python linters; 10x to 50x faster local and CI execution; all rules centralized in `pyproject.toml`; native support for modern Python 3.12 - 3.14 syntax.
- Negative: Requires careful verification during migration to ensure legacy code remains clean and passing under new rules without behavioral side effects.

## Migration Impact
- Handled during Phase 1 (Tooling & Quality Gate Modernization).
