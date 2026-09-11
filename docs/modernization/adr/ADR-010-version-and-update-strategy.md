# ADR-010: Version Management, Framework Release Registry, and Self-Update Removal

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
- Naive string splitting on `.` breaks on pre-releases, post-releases, and Calendar Versioning (CalVer) schemes.
- Network operations must be explicit and attributable.

## Decision
1. **Remove Self-Update (`--update`) Completely**:
   - Django-Start 2.0 will never attempt to upgrade itself or execute `pip install --upgrade`.
   - Users upgrade their tools through their package manager (`pipx upgrade django-start-automate` or `uv tool upgrade django-start-automate`).
2. **Dynamic Version Resolution**:
   - At runtime, Django-Start derives its version dynamically from standard package metadata via `importlib.metadata.version("django-start-automate")`.
   - Single source of truth in `pyproject.toml`.
3. **Strengthened `VersionPolicy` Design**:
   - Reject string splitting on `.` and arithmetic comparisons (`sum(map(int, ...))`).
   - Adopt PyPA standard `packaging.version.Version` and `packaging.specifiers.SpecifierSet` for all version parsing, comparison, and constraint evaluation.
   - Guarantees strict PEP 440 compliance across semantic versions, pre-releases, and calendar versions.
4. **`FrameworkRelease` Model and Registry**:
   - Introduce a typed domain model representing supported Django releases:
     ```python
     @dataclass(frozen=True)
     class FrameworkRelease:
         series: str  # e.g. "6.1", "5.2", or "2028.0"
         pinned_version: str  # e.g. "6.1.1", "5.2.17"
         is_lts: bool
         eol_date: str
         python_requires: SpecifierSet
         is_calver: bool = False
     ```
   - Support both traditional SemVer-style releases (`5.2`, `6.1`, `6.2`) and DEP 20 Calendar Versioning formats (`YYYY.N`, e.g. `2028.0` onwards).
   - **Conservative Failure Handling for Unknown Versions**: If an unknown or unverified Django version or track is requested, the policy must not guess or attempt unvalidated resolution. It raises `UnsupportedVersionError`, presenting the user with the list of verified, supported framework releases.
5. **Explicit Diagnostic Check**:
   - Version checking is moved to the diagnostic command `django-start doctor`.
   - Any network queries to PyPI will use a strict 2-second timeout, explicit User-Agent headers, standard `packaging.version.Version` semantic comparison, and will degrade gracefully to offline status without halting the CLI.
6. **Standard `--version` Flag**:
   - Standard `--version` option under `django-start` reports version, Python version, and platform without network calls.

## Alternatives Evaluated
- **Keep `--update` with safe `subprocess.run`**: Rejected because self-updating across diverse environments (virtualenvs, system site-packages, pipx, Homebrew) is fundamentally unreliable and violates packaging standards.
- **Custom tuple or regex version parser**: Rejected because `packaging.version.Version` is the authoritative PyPA implementation of PEP 440.
- **Permitting arbitrary unverified Django versions**: Rejected because generator templates must guarantee verification against tested releases.

## Consequences
- Positive: Eliminates insecure shell execution; eliminates silent network crashes; conforms to modern CLI standards; robust PEP 440 and DEP 20 CalVer compatibility; deterministic framework resolution.
- Negative: Users accustomed to `django-version --update` must use standard package manager commands; adding support for new Django releases requires registry updates.

## Migration Impact
- Handled during Phase 2 (Packaging Foundation), Phase 3 (Domain & Policy), and Phase 7 (CLI Modernization).
