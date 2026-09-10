# ADR-002: Django Support Policy and Deterministic Pinning

## Status
Accepted

## Context
In Django-Start 1.1.6, project generation executed an unpinned command: `pip install django`.
This practice created two major architectural flaws:
1. Generation was non-deterministic: the installed Django version was whichever release PyPI returned at runtime, meaning the same generator generated completely different project layouts and dependencies on different days.
2. Incompatibilities arose when Django released major versions that broke 1.1.6 starter code or settings conventions.

In September 2026, the official Django landscape consists of:
- **Django 6.1**: Latest stable feature release (6.1.1).
- **Django 5.2 LTS**: Current Long-Term Support release (5.2.17), supported through April 2028.
- **Django 6.2 LTS**: In development, scheduled for late 2026.

## Decision
1. Django-Start 2.0 will officially support two Django tracks:
   - **Feature Track (Default)**: Django 6.1 (pins `Django==6.1.1`).
   - **LTS Track**: Django 5.2 LTS (pins `Django==5.2.17`).
2. Unbounded commands like `pip install django` are strictly forbidden.
3. Every generated project will explicitly record its selected Django release in `requirements.txt`.
4. The exact pinned patch version will be maintained in recipe metadata.

## Alternatives Evaluated
- **Dynamic PyPI Resolution**: Query PyPI at runtime for the newest patch version within a minor range. Rejected because it requires network access and violates offline determinism.
- **Support Django 6.1 Only**: Rejected because enterprise teams often require LTS stability (Django 5.2 LTS is supported until April 2028).
- **Support Arbitrary Historical Django Releases**: Rejected because testing matrix explosion would degrade generator quality.

## Consequences
- Positive: Every generation is completely reproducible and verifiable offline. Generated code matches the exact semantics of the target Django release.
- Negative: Requires new patch releases of Django-Start when upstream Django releases security patch updates.

## Migration Impact
- Handled during Phase 5 (Recipe Engine) and Phase 6 (Application Use Cases).
