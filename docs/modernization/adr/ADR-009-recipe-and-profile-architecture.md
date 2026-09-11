# ADR-009: Recipe and Profile Architecture

## Status
Accepted

## Context
Django projects differ significantly based on their intended purpose (e.g. monolithic HTML app, REST API service, minimal microservice, production containerized setup).
Django-Start 1.1.6 had a single, hardcoded layout that injected an HTML view rendering an index page with GitHub buttons. Supporting other architectures required editing core orchestrator code, violating the Open/Closed Principle.
Furthermore, earlier conceptual drafts conflated framework release tracks (such as `lts`) with project archetypes, muddling architectural composition with Django version selection.

## Decision
1. **Orthogonal Separation: Project Profile vs Framework Track**:
   - **Project Profile (Composition)**: Defines the architectural layout, components, and boilerplate of the application. Independent of specific framework release versions.
   - **Framework Track (Release Selection)**: Selects the target Django release family (e.g. `6.1` Feature Track, `5.2` LTS Track).
   - Any profile can be generated against any compatible framework track (e.g. `standard` on 6.1, `standard` on 5.2, `production` on 6.1, `production` on 5.2).
2. **Define Four Built-In Profiles**:
   - **`standard` (Default)**: Full-stack layout, SQLite, starter app with template structure, home view, static assets directory, base settings, and starter test structure.
   - **`minimal`**: Lightweight single-file or barebones layout without demo HTML views, suited for micro-services, prototypes, or minimal footprints.
   - **`api`**: REST API service featuring Django REST Framework, API routing structure, serializer starter, and health check endpoint.
   - **`production`**: Production-ready setup featuring split settings (`base.py`, `production.py`, `local.py`), environment variable management, container/WSGI/ASGI production configuration, and security baseline.
3. **Recipe Versioning and Compatibility Metadata Schema**:
   Recipes are defined declaratively with explicit, separated versioning and compatibility constraints:
   - `recipe_schema_version`: Version of the recipe specification format itself (e.g. `"1.0"`).
   - `recipe_version`: Version of the recipe content/package itself (e.g. `"2.0.0"`).
   - `python_requires`: PEP 440 specifier for supported Python versions (e.g. `">=3.12"`).
   - `django_requires`: PEP 440 specifier for supported Django versions (e.g. `">=5.2,<6.2"`).
   - `django_start_requires`: PEP 440 specifier for compatible Django-Start CLI versions (e.g. `">=2.0,<3.0"`).
   - `name`: Unique profile/recipe identifier.
   - `description`: Human-readable summary of the profile archetype.
   - `dependencies`: Declared package dependencies with compatible ranges.
   - `template_dir`: Path or package resource pointer to template assets.
4. **Explicit Failure Handling for Compatibility and Schema Violations**:
   The recipe engine validates all compatibility metadata prior to execution:
   - **Incompatible Python**: If the active Python interpreter does not satisfy `python_requires`, abort immediately and raise `UnsupportedVersionError` detailing the active Python version and the required version range.
   - **Unsupported Django**: If the selected Django release line does not satisfy `django_requires`, abort immediately and raise `UnsupportedVersionError` detailing the requested Django release and the recipe's supported versions.
   - **Newer Recipe Schema Version**: If a recipe specifies a `recipe_schema_version` newer than the maximum schema version supported by the current Django-Start engine, abort immediately and raise `ConfigurationError` explaining that Django-Start must be updated to use this recipe.
5. **Declarative Recipe Invariant**:
   - Recipes are strictly declarative (JSON/YAML metadata and file templates).
   - Executable Python hooks or arbitrary shell commands inside recipe definitions are strictly prohibited.

## Alternatives Evaluated
- **Treating `lts` as a profile**: Rejected. LTS is a framework release track, not an architectural composition. Conflating them prevents generating API or minimal projects on LTS Django.
- **Dynamic Python plugin architecture**: Evaluated, but allows untrusted arbitrary code execution during project generation. Declarative schemas provide superior security and auditability.
- **Monolithic flag explosion (`--with-drf`, `--with-docker`, etc.)**: Rejected because flags combine exponentially and clutter CLI help.

## Consequences
- Positive: Clean separation of concerns; easy to add new profiles (e.g. `docker`, `celery`) without touching generation use cases; secure and auditable; robust validation preventing incompatible environment generation.
- Negative: Requires maintaining template trees across supported profiles and framework tracks.

## Migration Impact
- Handled during Phase 5 (Recipe Engine & Controlled Templates).
