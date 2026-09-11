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

Upstream verification confirms that the latest stable releases on PyPI are **Ruff 0.16.7** and **Mypy 2.3.1**.

## Decision
1. In **Phase 2 (Modern Quality Tooling)**, following Phase 1 (Packaging Foundation), transition the repository's formatting and linting suite to **Ruff** (`ruff>=0.16.7,<1`).
2. Consolidate formatting and linting configuration into standard `pyproject.toml` under `[tool.ruff]`.
3. Configure Ruff to emulate Black formatting conventions while enforcing standard PEP 8, import sorting (isort), and pyupgrade rules natively.
4. Introduce **Mypy** (`mypy>=2.3.1,<3`) with an explicit incremental typing strategy:
   - **Strict Static Typing (`src/django_start/**`)**: Full strict type checking for all 2.0 core code, domain entities, use cases, ports, and infrastructure adapters (`disallow_untyped_defs = true`, `check_untyped_defs = true`, `warn_return_any = true`, `no_implicit_optional = true`).
   - **Permissive Typing for Legacy Compatibility Shim (`src/djstartlib/**`)**: Lenient configuration allowing unannotated legacy functions, deprecated shims, and dynamic re-exports without raising type errors.
   - **Typing at Test Boundaries**: Typed signatures for custom test fixtures, test helpers, and fake adapters (`FakeCommandRunner`, `InMemoryFileSystem`), while allowing test assertion bodies pragmatic flexibility.
5. Retain pre-commit as the local Git hook orchestrator, updating hook repositories to modern releases.

## Alternatives Evaluated
- **Keep Black + Flake8 + Pyupgrade**: Rejected because of configuration fragmentation, slower CI performance, and lack of native `pyproject.toml` support in Flake8.
- **Adopt Ruff for Linting but keep Black for Formatting**: Rejected because Ruff's formatter has achieved complete stability and parity with Black, rendering dual-tool execution redundant.
- **Enforce Global Strict Mypy Across Entire Repository**: Rejected because enforcing strict typing on the legacy compatibility shim would require modifying frozen legacy code or complex typing acrobatics for deprecated APIs.

## Consequences
- Positive: Single Rust binary replaces 3 distinct Python linters; 10x to 50x faster local and CI execution; all rules centralized in `pyproject.toml`; strict type guarantees for modern architecture while isolating legacy code.
- Negative: Requires careful verification during Phase 2 migration to ensure existing code remains clean and passing under new rules without behavioral side effects.

## Migration Impact
- Handled during Phase 2 (Modern Quality Tooling) following Phase 1 (Packaging Foundation).
