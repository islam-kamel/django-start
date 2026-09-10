# ADR-003: CLI Framework and Command Surface

## Status
Accepted

## Context
Django-Start 1.1.6 exposed two separate top-level console scripts via `setup.cfg`:
- `django-start`: A single command accepting positional arguments `PROJECT_NAME` and `APP_NAME`, with options `-n`, `-v`, and `-u`.
- `django-version`: A command accepting `--update` and `--check-update` flags, which invoked pip via `shell=True`.

This structure failed to provide lifecycle support for existing projects, had awkward command ergonomics, and separated version handling into an unrelated command binary.

## Decision
1. Retain **Click** as the CLI presentation framework, upgrading to `click>=8.5,<9`. Click provides mature support for command groups, subcommands, and rich terminal output without heavy dependencies.
2. Unify all capabilities under the single `django-start` CLI binary, organized into explicit subcommands:
   - `django-start new <project_name>`: Scaffold new project and initial app.
   - `django-start add <app_name>`: Add an application to an existing project.
   - `django-start doctor`: Diagnose host environment, Python, virtualenv, and project state.
   - `django-start check`: Execute `manage.py check` with structured reporting.
   - `django-start recipe`: List and inspect available project recipes.
   - `django-start --version`: Standard version display.
3. Provide a backward-compatibility adapter for the legacy syntax `django-start <project> <app>`, routing it to `new` with a deprecation notice.
4. Retain `django-version` as a deprecated console script shim pointing to `django-start --version`.

## Alternatives Evaluated
- **Migrate to Typer**: Typer provides type-hinted CLI definitions built on top of Click. Rejected because it introduces an unnecessary dependency layer when standard Click 8.5 already provides typed parameters natively.
- **Migrate to argparse**: Python standard library. Rejected because Click provides significantly superior subcommands, argument parsing, error formatting, and test runners (`CliRunner`).

## Consequences
- Positive: Modern, extensible command structure; provides lifecycle management (`add`, `doctor`, `check`); maintains backward compatibility for existing user scripts.
- Negative: Existing users of 1.1.6 will receive deprecation notices when using positional invocation.

## Migration Impact
- Handled during Phase 7 (CLI Modernization).
