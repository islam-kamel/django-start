# ADR-003: CLI Framework and Command Surface

## Status
Accepted

## Context
Django-Start 1.1.6 exposed two separate top-level console scripts via `setup.cfg`:
- `django-start`: A single command accepting positional arguments `PROJECT_NAME` and `APP_NAME`, with options `-n`, `-v`, and `-u`.
- `django-version`: A command accepting `--update` and `--check-update` flags, which invoked pip via `shell=True`.

This structure failed to provide lifecycle support for existing projects, had awkward command ergonomics, and separated version handling into an unrelated command binary.

Upstream research confirms that the latest release of Click on PyPI is **Click 8.5.0** (released August 26, 2026). Click 8.5.0 provides native typing across command definitions, nested command groups, shell completion, and robust test runners without third-party wrapper dependencies.

## Decision
1. Retain **Click** as the CLI presentation framework, upgrading to the recommended specification `click>=8.5,<9`.
2. Unify all capabilities under the single `django-start` CLI binary, organized into explicit subcommands:
   - `django-start new <project_name> [OPTIONS]`: Scaffold a new project and initial app. Project generation options are structured into orthogonal dimensions:
     - `--profile <standard|api|minimal|production>`: Selects the architectural layout and scaffolding recipe (defaults to `standard`).
     - `--django <latest|lts|version>`: Selects the Django target track or version (defaults to `latest`). The CLI parses this as a general track or version token rather than assuming a fixed `X.Y` format, allowing seamless support for traditional releases (`6.1`, `5.2`) and future Django DEP 20 CalVer releases (`2028.0`).
     - `--app <app_name>`: Specifies the name of the initial application (optional, defaults to project conventions).
   - `django-start add <app_name>`: Add an application to an existing project.
   - `django-start doctor`: Diagnose host environment, Python, virtualenv, and project state.
   - `django-start check`: Execute `manage.py check` with structured reporting.
   - `django-start recipe`: List and inspect available project recipes.
   - `django-start --version`: Standard version display.
3. Provide a backward-compatibility adapter for the legacy syntax `django-start <project> <app>`, routing it to `new` with a deprecation notice.
4. Retain `django-version` as a deprecated console script shim pointing to `django-start --version`. Eliminate the insecure `--update` shell invocation.

## Alternatives Evaluated
- **Migrate to Typer**: Typer provides type-hinted CLI definitions built on top of Click. Rejected because it introduces an unnecessary dependency layer when standard Click 8.5 already provides typed parameters natively.
- **Migrate to argparse**: Python standard library. Rejected because Click provides significantly superior subcommands, argument parsing, error formatting, and test runners (`CliRunner`).

## Consequences
- Positive: Modern, extensible command structure; orthogonal separation of architectural profiles from Django release tracks; full support for both SemVer and CalVer versions; maintains backward compatibility for legacy positional invocations.
- Negative: Existing users of 1.1.6 will receive deprecation notices when using positional invocation.

## Migration Impact
- Handled during Phase 7 (Modern CLI).
