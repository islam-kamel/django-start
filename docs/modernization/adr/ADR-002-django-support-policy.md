# ADR-002: Django Support Policy and Deterministic Pinning

## Status
Accepted

## Context
In Django-Start 1.1.6, project generation executed an unpinned command: `pip install django`.
This practice created two major architectural flaws:
1. Generation was non-deterministic: the installed Django version was whichever release PyPI returned at runtime, meaning the same generator produced completely different project layouts and dependencies on different days.
2. Incompatibilities arose when Django released major versions that broke 1.1.6 starter code or settings conventions.

In September 2026, the official Django release landscape is:
- **Django 6.1**: Latest stable feature release. Django 6.1 final was released on August 5, 2026, followed by patch release Django 6.1.1 on September 2, 2026.
- **Django 5.2 LTS**: Current Long-Term Support release (5.2.17), supported through April 2028.
- **Django 6.2 LTS**: In active development, expected April 2027 (supported through April 2030).
- **Django DEP 20 (Calendar Versioning)**: Django Enhancement Proposal DEP 20 introduces an annual Calendar Versioning cycle (`YYYY.N`) starting in January 2028 with Django 2028.0. Under DEP 20, all annual releases adopt a uniform 3-year support window (1 year of bugfixes followed by 2 years of security and data-loss fixes). Consequently, Django 6.2 LTS is the final release formally designated with the "LTS" label. After 6.2 LTS, the "LTS" distinction is retired upstream because every release provides equivalent 3-year long-term support.

## Decision
1. Django-Start 2.0 officially supports two Django release tracks:
   - **Feature Track (Default)**: Django 6.1 (tested baseline `6.1.1`).
   - **LTS Track**: Django 5.2 LTS (tested baseline `5.2.17`), transitioning to Django 6.2 LTS upon its release in April 2027.
2. Unbounded commands like `pip install django` are strictly forbidden.
3. Treat `lts` as transitional user vocabulary:
   - The CLI option `--django lts` is preserved for user convenience and migration stability.
   - Recipe metadata defines explicit release target mappings (`latest`, `lts`, or specific version strings).
   - Post-2028 (under DEP 20 CalVer), `--django lts` behaves as an alias for the designated stable enterprise track (the active release with the longest remaining security window or designated conservative stability profile).
4. Re-evaluated Multi-Layered Dependency and Pinning Strategy:
   - **Compatibility Constraint**: Project manifests (e.g. `requirements.txt` or `pyproject.toml`) specify bounded compatibility ranges (e.g. `Django>=6.1.1,<6.2` or `Django>=5.2.17,<5.3`).
   - **Security Patch Absorption**: Bounded upper constraints allow downstream generated projects to automatically absorb upstream security and bugfix patches without forcing an immediate update of Django-Start.
   - **Resolver Resolution**: During standard online project generation, package installers resolve the latest patch release matching the declared compatibility constraint.
   - **Reproducibility Lock File Formats**: When deterministic lockfiles are generated (e.g. pinned lock format or pinned `requirements.txt`), exact tested pins (e.g. `Django==6.1.1`) are recorded.
   - **Offline Determinism Mode**: When offline generation is requested or network access is disabled, recipe metadata supplies a bundled, known-tested default patch version (e.g. `Django==6.1.1`, `Django==5.2.17`) for bit-for-bit reproducible, network-free generation.

## Alternatives Evaluated
- **Strict Exact Patch Pinning for All Manifests (`Django==6.1.1`)**: Rejected because it prevents downstream projects from absorbing critical upstream security patches without updating Django-Start.
- **Unbounded Dynamic PyPI Resolution (`pip install django`)**: Rejected because it breaks reproducibility, allows breaking upstream changes to enter silently, and violates offline determinism.
- **Immediate Removal of `lts` Keyword**: Rejected because users and automation scripts rely on `lts` as a stability marker. Retaining it as transitional metadata ensures backward compatibility as Django transitions to DEP 20 CalVer.

## Consequences
- Positive: Guarantees reproducible, verifiable project scaffolding while allowing downstream projects to absorb critical security fixes; smoothly supports the transition to Django DEP 20 CalVer without breaking user CLI expectations.
- Negative: Recipe metadata must maintain both compatibility bounds and default offline pins across supported Django versions.

## Migration Impact
- Handled during Phase 5 (Recipe Engine) and Phase 6 (Application Use Cases).
