# ADR-009: Recipe and Profile Architecture

## Status
Accepted

## Context
Django projects differ significantly based on their intended purpose (e.g. monolithic HTML app, REST API service, minimal microservice, production containerized setup).
Django-Start 1.1.6 had a single, hardcoded layout that injected an HTML view rendering an index page with GitHub buttons. Supporting other architectures required editing core orchestrator code, violating the Open/Closed Principle.

## Decision
1. Introduce a modular **Recipe Architecture**:
   - A recipe is a declarative definition specifying Django version constraints, pinned dependencies, project layout, initial apps, configuration templates, and verification commands.
   - Core generation logic is completely agnostic to specific file contents; it simply executes recipe definitions.
2. Provide four built-in profiles for 2.0:
   - **`standard` (Default)**: Django 6.1, SQLite, standard template structure, home view, static files directory, pinned `requirements.txt`.
   - **`lts`**: Django 5.2 LTS, SQLite, enterprise stability profile.
   - **`api`**: Django 6.1, Django REST Framework, API routing structure, health check view.
   - **`minimal`**: Django 6.1, barebones single-file or ultra-minimal layout without demo HTML views.
3. Recipe Security Invariant: External recipes are strictly declarative (JSON/YAML metadata and file templates). Executable Python hooks or arbitrary shell commands in third-party recipes are strictly prohibited.

## Alternatives Evaluated
- **Dynamic Python plugin architecture**: Evaluated, but allows untrusted arbitrary code execution during project generation. Declarative schemas provide superior security and auditability.
- **Monolithic flag explosion (`--with-drf`, `--with-docker`, etc.)**: Rejected because flags combine exponentially and clutter CLI help.

## Consequences
- Positive: Clean separation of concerns; easy to add new profiles (e.g. `docker`, `celery`) without touching generation use cases; secure and auditable.
- Negative: Requires defining formal recipe metadata schemas and template directories.

## Migration Impact
- Handled during Phase 5 (Recipe Engine & Controlled Templates).
