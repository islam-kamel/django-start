# ADR-006: Subprocess Execution and CommandRunner Boundary

## Status
Accepted

## Context
In Django-Start 1.1.6, all external commands (`create_env`, `upgrade_pip`, `install_dep`, `create_project`, `create_app`, `update`) were executed using `subprocess.call(..., shell=True)` with string interpolation.
This caused critical vulnerabilities and unreliability:
1. High vulnerability to shell injection if arguments contain shell metacharacters.
2. Fragile path handling on Windows and paths containing spaces.
3. Silent process termination via `sys.exit(1)` inside procedural helpers on error.
4. Impossible to unit-test without running real subprocesses or complex process patching.

## Decision
1. Introduce a strict port protocol: `CommandRunner`.
2. Prohibit `shell=True` entirely across the codebase.
3. Pass all commands as typed argument sequences (`list[str]`), with explicit working directory (`cwd: Path`), structured capture of stdout/stderr, and explicit timeout.
4. Return an immutable `CommandResult` object.
5. In library code, raise `CommandExecutionError` upon non-zero exit codes instead of calling `sys.exit()`.
6. Provide a `FakeCommandRunner` for fast, hermetic unit and use-case testing without spawning operating system processes.

## Alternatives Evaluated
- **Direct `subprocess.run` in use cases**: Rejected because it tightly couples business logic to operating system primitives and prevents in-memory mock testing.
- **Third-party process libraries (e.g. `sh`, `plumbum`)**: Rejected to avoid adding unnecessary runtime dependencies. Standard library `subprocess` wrapped in a clean protocol is completely sufficient.

## Consequences
- Positive: Eliminates shell injection vulnerabilities; guarantees safe handling of spaces in paths; enables sub-millisecond use-case unit tests; provides structured error diagnostics.
- Negative: Requires defining explicit argument lists rather than raw shell command strings.

## Migration Impact
- Handled during Phase 3 (Ports Definition) and Phase 4 (Infrastructure Adapters).
