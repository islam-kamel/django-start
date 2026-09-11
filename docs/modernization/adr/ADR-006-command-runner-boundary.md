# ADR-006: Subprocess Execution, CommandRunner Boundary, and Environment Ports

## Status
Accepted

## Context
In Django-Start 1.1.6, all external commands (`create_env`, `upgrade_pip`, `install_dep`, `create_project`, `create_app`, `update`) were executed using `subprocess.call(..., shell=True)` with string interpolation.
This caused critical vulnerabilities and unreliability:
1. High vulnerability to shell injection if arguments contain shell metacharacters.
2. Fragile path handling on Windows and paths containing spaces.
3. Silent process termination via `sys.exit(1)` inside procedural helpers on error.
4. Impossible to unit-test without running real subprocesses or complex process patching.
5. Monolithic coupling of virtual environment creation, package installation, and project scaffolding.

## Decision
1. **Reaffirm CommandRunner Invariants**:
   - Introduce a strict port protocol: `CommandRunner`.
   - Prohibit `shell=True` entirely across the codebase.
   - Pass all commands as typed argument sequences (`argv: Sequence[str]`). String interpolation and shell command concatenation are strictly forbidden.
   - Execute all commands with an explicit working directory (`cwd: Path`).
   - Capture `stdout` and `stderr` as structured, typed properties in an immutable `CommandResult` dataclass alongside integer `returncode`.
   - In library and infrastructure code, never call `sys.exit()`. Raise typed `CommandExecutionError` upon non-zero exit codes.
   - Provide a `FakeCommandRunner` for fast, hermetic unit and use-case testing without spawning operating system processes.
2. **Define Segregated Environment Ports**:
   - In accordance with Interface Segregation and Single Responsibility, virtual environment lifecycle and package management are decoupled into dedicated ports.
   - **`EnvironmentManager` (Port Protocol)**: Responsible for creating and introspecting isolated virtual environments (e.g. `create(path: Path) -> Environment`, locating the Python interpreter executable, script directories, and environment paths). Default baseline adapter: `VenvEnvironmentManager` using the standard library `venv` module.
   - **`PackageInstaller` (Port Protocol)**: Responsible for installing dependencies into an environment (e.g. `install(env: Environment, specs: Sequence[str]) -> None`, `install_requirements(env: Environment, requirements_file: Path) -> None`). Default baseline adapter: `PipPackageInstaller` executing `pip` via `CommandRunner`.
3. **Secondary Fast Adapter Policy**:
   - Rather than pre-selecting `uv` as the secondary fast adapter, an unbiased comparison of dependency resolvers and installers (evaluating tools such as `pip`, `uv`, and `pip-tools` across startup latency, platform portability, dependency footprint, lockfile compatibility, and ecosystem stability) must be performed before defining and standardizing any secondary adapter.

## Alternatives Evaluated
- **Direct `subprocess.run` in use cases**: Rejected because it tightly couples business logic to operating system primitives and prevents in-memory mock testing.
- **Pre-selecting `uv` without evaluation**: Rejected in favor of conducting an unbiased comparative evaluation of resolvers and installers first.
- **Monolithic Environment Manager**: Rejected because virtual environment management and package resolution have distinct reasons to change.

## Consequences
- Positive: Eliminates shell injection vulnerabilities; guarantees safe handling of spaces in paths; enables sub-millisecond use-case unit tests; provides structured error diagnostics; cleanly decouples environment provisioning from package installation.
- Negative: Requires defining explicit argument lists rather than raw shell command strings; requires managing two separate infrastructure ports.

## Migration Impact
- Handled during Phase 3 (Ports Definition) and Phase 4 (Infrastructure Adapters). Secondary adapter evaluation scheduled before secondary adapter implementation.
