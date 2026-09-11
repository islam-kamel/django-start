# ADR-008: Django Project Generation Engine Strategy

## Status
Accepted

## Context
Django-Start 1.1.6 modified generated Django files using fragile line and substring searches:
- `line_list.index("]\n")` was used to find the end of `INSTALLED_APPS` and `urlpatterns`.
- `# Create your views here.\n` was searched to inject the starter view function.

This mechanism is extremely brittle:
1. If a developer formats `settings.py` or `urls.py` with spaces (`    ]`) or comments, `index("]\n")` raises an unhandled `ValueError`.
2. In `settings.py`, `update_settings` inserts into the first list terminated with `]\n`, which can misplace the app name into `MIDDLEWARE` or other configuration lists.
3. In `views.py`, if the comment is absent, the tool emits a confusing warning and skips generation.
4. Hardcoded, monolithic output layout prevented scaffolding alternative project styles.
5. Dependencies were installed unpinned (`pip install django`), producing non-deterministic projects without lockfiles or reproducible manifests.

## Decision
1. **Eliminate Heuristic String Bracket Searching**:
   - Eliminate all line searching, substring matching, and bracket index searching (`index("]\n")`).
2. **Adopt Controlled Template and Declarative Recipe Engine**:
   - Rather than letting `django-admin startproject` write an unconfigured project and then hacking its output, Django-Start uses controlled Django project templates and declarative recipe file trees.
3. **Orthogonal Profiles and Framework Tracks**:
   - Decouple architectural composition (**Project Profile**) from framework release selection (**Framework Track**).
   - The generation engine renders templates and configuration corresponding to the orthogonal pair: `(profile, framework_track)`.
   - The Project Profile defines structural components, included apps, settings organization, and baseline services (e.g. `standard`, `minimal`, `api`, `production`).
   - The Framework Track selects the target Django release family (e.g. Django 6.1 Feature Track vs Django 5.2 LTS Track).
   - Template assets are structured by profile and parameterized or specialized by target Django release family to accommodate version-specific settings, syntax, and conventions.
4. **Dependency Manifest and Reproducible Locking Strategy**:
   - The generation engine produces a clean, declarative dependency manifest (e.g. `requirements.txt`) specifying curated, compatible bounded dependency ranges (e.g. `Django>=6.1,<6.2`).
   - The generation of an exact, reproducible lock file will depend on the outcome of the locking strategy evaluation (evaluating formats such as `requirements.lock`, standard PEP 751 `pylock.toml`, or `uv.lock`). The baseline engine generates bounded declarative manifests, with reproducible lock file generation plugged in once the locking evaluation is concluded.
5. **App Registration via Structured AST Inspection**:
   - For `django-start add <app_name>`, configuration changes (such as verifying and registering the app in `INSTALLED_APPS`) will use structured AST inspection via Python's standard `ast` module to confirm presence, combined with safe, targeted insertion.
6. **Mandatory Post-Generation Verification**:
   - Validate every generated Python file immediately after rendering using `python -m py_compile` and Django's native `manage.py check`. A generation is only successful when verified.

## Alternatives Evaluated
- **Full AST rewriting using `libcst`**: Evaluated for lossless AST transformation. Deferred because adding `libcst` introduces a heavy third-party dependency; controlled templates eliminate the need for AST rewriting during new project creation.
- **Retain line search with Regex**: Regex improves on exact string matching, but remains brittle across differing Django version starter templates.
- **Pre-selecting a specific lockfile format prior to evaluation**: Rejected. Lockfile formats must be evaluated objectively before selecting a standard.

## Consequences
- Positive: Zero dependence on exact indentation, bracket positioning, or starter comments; 100% predictable output; clean separation of profile composition and Django release track; deterministic manifests.
- Negative: Requires maintaining controlled project templates for each supported Django release family.

## Migration Impact
- Handled during Phase 5 (Recipe Engine & Controlled Templates) and Phase 6 (Application Use Cases).
