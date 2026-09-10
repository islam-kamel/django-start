# ADR-008: Django Project Generation Engine Strategy

## Status
Accepted

## Context
Django-Start 1.1.6 modified generated Django files using fragile line and substring searches:
- `line_list.index("]\n")` was used to find the end of `INSTALLED_APPS` and `urlpatterns`.
- `# Create your views here.\n` was searched to inject the starter view function.

This mechanism is extremely brittle:
1. If a developer formats `settings.py` or `urls.py` with spaces (`    ]`) or comments, `index("]\n")` raises an unhandled `ValueError`.
2. In `settings.py`, `update_settings` inserts into the *first* list terminated with `]\n`, which can misplace the app name into `MIDDLEWARE` or other configuration lists.
3. In `views.py`, if the comment is absent, the tool emits a confusing warning and skips generation.

## Decision
1. Eliminate all heuristic string bracket searching (`index("]\n")`).
2. Adopt a **Controlled Template and Declarative Recipe Engine**:
   - Rather than letting `django-admin startproject` write an unconfigured project and then hacking its output, Django-Start uses controlled project templates via Django's native `--template` feature or renders declarative recipe templates.
   - For `django-start add <app_name>`, configuration changes (e.g. adding to `INSTALLED_APPS`) will use structured AST inspection via Python's standard `ast` module to confirm presence, combined with safe, targeted insertion.
3. Validate every generated Python file immediately after rendering using `python -m py_compile` and `manage.py check`.

## Alternatives Evaluated
- **Full AST rewriting using `libcst`**: Evaluated for lossless AST transformation. Deferred because adding `libcst` introduces a heavy third-party dependency; controlled templates eliminate the need for AST rewriting during new project creation.
- **Retain line search with Regex**: Regex improves on exact string matching, but remains brittle across differing Django version starter templates.

## Consequences
- Positive: Zero dependence on exact indentation, bracket positioning, or starter comments; 100% predictable output; native Django compliance.
- Negative: Requires maintaining controlled project templates for each supported Django line (5.2 and 6.1).

## Migration Impact
- Handled during Phase 5 (Recipe Engine & Controlled Templates).
