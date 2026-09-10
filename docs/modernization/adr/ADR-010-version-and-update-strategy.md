# ADR-010: Version Management and Self-Update Removal

## Status
Accepted

## Context
In Django-Start 1.1.6, version management was handled in `djstartlib/version.py`:
1. Version was defined as a hardcoded string `"1.1.6 (beta)"`.
2. A custom CLI script `django-version` offered `--check-update` and `--update`.
3. `--check-update` queried the GitHub API without timeout or error handling, compared version numbers using an erroneous arithmetic formula (`sum(var_int)`), and terminated silently with `sys.exit(1)` on network failure.
4. `--update` executed `pip install --upgrade django-start-automate` via `subprocess.call` with `shell=True`.

These mechanisms violate security invariants, cross-platform stability, and Unix philosophy:
- Package managers (pip, pipx, uv, brew, apt) own package installations and upgrades, not CLI tools themselves.
- Self-updating via shell calls inside a tool invites privilege escalation, environment corruption, and broken execution paths.
- Network operations must be explicit and attributable.

## Decision
1. **Remove self-update (`--update`) completely**:
   - Django-Start 2.0 will never attempt to upgrade itself.
   - Users upgrade their tools through their package manager (`pipx upgrade django-start-automate` or `uv tool upgrade django-start-automate`).
2. **Dynamic Version Resolution**:
   - At runtime, version is derived from standard package metadata via `importlib.metadata.version("django-start-automate")`.
   - Single source of truth in `pyproject.toml`.
3. **Explicit Diagnostic Check**:
   - Version checking is moved to the diagnostic command `django-start doctor`.
   - Any network queries to PyPI will use a strict 2-second timeout, explicit User-Agent headers, standard `packaging.version.Version` semantic comparison, and will degrade gracefully to offline status without halting the CLI.
4. **Standard `--version` Flag**:
   - Standard `--version` option under `django-start` reports version, Python version, and platform.

## Alternatives Evaluated
- **Keep `--update` with safe `subprocess.run`**: Rejected because self-updating across environments (virtualenvs, system site-packages, pipx, Homebrew) is fundamentally unreliable and violates packaging standards.
- **Maintain hardcoded `__version__` string**: Rejected to avoid version synchronization drift between package metadata and code.

## Consequences
- Positive: Eliminates insecure shell execution; eliminates silent network crashes; conforms to modern CLI standards; ensures single source of truth for versioning.
- Negative: Users accustomed to `django-version --update` must use standard package manager commands.

## Migration Impact
- Handled during Phase 2 (Packaging Foundation) and Phase 7 (CLI Modernization).
