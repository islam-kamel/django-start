# Repository Pre-Commit Contract Normalization Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Achieve a fully green, stable `pre-commit run --all-files` baseline across the entire repository while preserving historical 1.1.6 runtime behavior, locking exact generated output, and leaving all characterization tests passing.

**Architecture:** Behavior-preserving style and hygiene normalization using strictly configured repository tools (`.pre-commit-config.yaml`: Black 22.8.0 with `-l 79`, Flake8 5.0.4, Pyupgrade 2.38.2, and pre-commit-hooks v4.3.0 under Python 3.10 hook environment), backed by a JSON test fixture asserting byte-for-byte HTML generation fidelity.

**Tech Stack:** Python 3.10 (hook env), Python 3.11 (canonical test env), pytest 8.3.4, pre-commit 4.6.2, black 22.8.0, flake8 5.0.4, pyupgrade 2.38.2.

## Global Constraints

- Pre-normalization reference commit SHA: `0778ade36f8a0b35f7291d9c0a8154bcea5c989e`.
- Authoritative baseline test count: 44 tests passing under Python 3.11.16.
- The existing code-style contract (`.pre-commit-config.yaml`) is authoritative and must not be weakened, disabled, replaced with Ruff, or modified to bypass failures.
- 79-column line limit enforced by Flake8 and Black must pass across all Python files (`djstartlib/**` and `tests/**`).
- No bug fixes, architectural refactorings, or packaging modernizations in this task.
- Legacy re-exports in `djstartlib/models/__init__.py` and `djstartlib/models/utils/__init__.py` must be preserved with narrow `# noqa: F401` / `# noqa: F401,F403`.
- Generated HTML output from `djstartlib.models.utils.helper.generate_html()` must remain byte-for-byte identical, locked via `tests/fixtures/generated-index-1.1.6.json`.
- Never invoke tools via `.cache/pre-commit` internal paths; use `pre-commit run <hook> ...`.
- Production semantic-diff review: classify every production diff hunk into approved categories (whitespace, Black formatting, line wrapping, indentation formatting, targeted `# noqa`, or protected output source representation).
- Final state requires `pre-commit run --all-files` exiting 0 with zero modifications on a second consecutive run.

---

### Task 1: Lock Exact Legacy Generated Output with JSON Test Fixture

**Files:**
- Create: `tests/fixtures/generated-index-1.1.6.json`
- Modify: `tests/unit/test_helper.py`

**Interfaces:**
- Consumes: `djstartlib.models.utils.helper.generate_html`
- Produces: `tests/fixtures/generated-index-1.1.6.json` static reference file and `test_generate_html_exact_match` test function.

- [ ] **Step 1: Capture mechanical output from pre-normalization reference and write `tests/fixtures/generated-index-1.1.6.json`**

Mechanically capture the exact return value of `generate_html()` from the frozen reference into `tests/fixtures/generated-index-1.1.6.json` using JSON serialization:
```json
{
  "html": "<!DOCTYPE html>\n<html lang=\"en\">\n    <head>\n        <meta charset=\"UTF-8\">\n        <title>Django Start</title>\n        <style>\n            *{text-align: center}\n            div{display:flex; justify-content:center}\n        </style>\n    </head>\n    <body>\n        <h1 style=\"text-align: center\">Hello, Django-Start</h1>\n        <a style=\"text-align: center\" class=\"github-button\" href=\"https://github.com/islam-kamel/django-start\" data-color-scheme=\"no-preference: light; light: light; dark: dark;\" data-size=\"large\" data-show-count=\"true\" aria-label=\"Star islam-kamel/django-start on GitHub\">Django-Start</a>\n    </body>\n    <script async defer src=\"https://buttons.github.io/buttons.js\"></script>\n</html>"
}
```

- [ ] **Step 2: Add exact equality test to `tests/unit/test_helper.py`**

```python
def test_generate_html_exact_match():
    """Verify generate_html produces byte-for-byte identical output to 1.1.6 fixture."""
    fixture_path = (
        pathlib.Path(__file__).resolve().parent.parent
        / "fixtures"
        / "generated-index-1.1.6.json"
    )
    data = json.loads(fixture_path.read_text(encoding="utf-8"))
    assert generate_html() == data["html"]
```

- [ ] **Step 3: Run pytest to verify the test passes**

Run: `.venv/bin/pytest tests/unit/test_helper.py::test_generate_html_exact_match -v`
Expected: PASS.

- [ ] **Step 4: Commit**

```bash
git add tests/fixtures/generated-index-1.1.6.json tests/unit/test_helper.py
git commit -m "test: lock exact legacy generated output"
```

---

### Task 2: Normalize Non-Python Repository Files (Whitespace, EOF, Config)

**Files:**
- Modify: `.github/workflows/codeql-analysis.yml`
- Modify: `.github/dependabot.yml`
- Modify: `pyproject.toml`
- Modify: `.idea/misc.xml`
- Modify: `.idea/rest-start.iml`

**Interfaces:**
- Consumes: `pre-commit run trailing-whitespace --all-files`, `pre-commit run end-of-file-fixer --all-files`, `pre-commit run check-yaml --all-files`
- Produces: Normalized non-Python files with clean EOF and no trailing whitespace.

- [ ] **Step 1: Run pre-commit hygiene hooks on all files**

Run:
```bash
pre-commit run trailing-whitespace --all-files
pre-commit run end-of-file-fixer --all-files
pre-commit run check-yaml --all-files
```

- [ ] **Step 2: Inspect diff to ensure zero semantic changes**

Run: `git diff .github/ pyproject.toml .idea/`
Ensure only whitespace and final newline characters were modified.

- [ ] **Step 3: Commit**

```bash
git add .github/ pyproject.toml .idea/
git commit -m "chore: normalize repository whitespace and eof"
```

---

### Task 3: Normalize Tests to Existing Code Style and 79-Column Limit

**Files:**
- Modify: `tests/conftest.py`
- Modify: `tests/integration/test_scaffold_orchestration.py`
- Modify: `tests/unit/test_app_manager.py`
- Modify: `tests/unit/test_bootstrap.py`
- Modify: `tests/unit/test_cli.py`
- Modify: `tests/unit/test_environment.py`
- Modify: `tests/unit/test_helper.py`
- Modify: `tests/unit/test_project_manager.py`
- Modify: `tests/unit/test_version.py`

**Interfaces:**
- Consumes: `pre-commit run black --files tests/...` and `pre-commit run flake8 --files tests/...`
- Produces: Clean, standard-formatted test modules adhering to 79 columns.

- [ ] **Step 1: Run Black on `tests/` via pre-commit**

Run:
```bash
pre-commit run black --files $(git ls-files 'tests/*.py')
```

- [ ] **Step 2: Check Flake8 on `tests/` via pre-commit and resolve remaining E501 violations**

Run:
```bash
pre-commit run flake8 --files $(git ls-files 'tests/*.py')
```
For any lines still exceeding 79 characters (such as long test docstrings, long comments, or complex assertions), manually wrap them cleanly without altering test assertions.

- [ ] **Step 3: Re-verify Black and Flake8 on `tests/`**

Run:
```bash
pre-commit run black --files $(git ls-files 'tests/*.py')
pre-commit run flake8 --files $(git ls-files 'tests/*.py')
```
Expected: Both exit with 0.

- [ ] **Step 4: Run complete pytest suite**

Run: `.venv/bin/pytest`
Expected: All tests pass.

- [ ] **Step 5: Commit**

```bash
git add tests/
git commit -m "style: normalize tests to existing code style"
```

---

### Task 4: Normalize Legacy Source Code Without Behavior Changes

**Files:**
- Modify: `djstartlib/models/__init__.py`
- Modify: `djstartlib/models/utils/__init__.py`
- Modify: `djstartlib/models/utils/helper.py`
- Modify: `djstartlib/main.py`
- Modify: `djstartlib/version.py`
- Modify: `djstartlib/models/app_manager.py`
- Modify: `djstartlib/models/project_manager.py`
- Modify: `djstartlib/models/utils/environment.py`
- Modify: `djstartlib/models/djstart_interface.py`
- Modify: `djstartlib/__init__.py`

**Interfaces:**
- Consumes: `pre-commit run black`, `pre-commit run flake8`, `pre-commit run pyupgrade`
- Produces: Clean legacy source files with preserved public re-exports, byte-for-byte identical generated HTML, zero behavior defects fixed, and a comprehensive semantic-diff classification review.

- [ ] **Step 1: Add targeted `# noqa` comments to package `__init__.py` files**

In `djstartlib/models/__init__.py`:
Add `# noqa: F401` to `AppManager`, `ProjectManager`, `DjangoStart`.

In `djstartlib/models/utils/__init__.py`:
Add `# noqa: F401` to `Environment` and `# noqa: F401,F403` to `helper.*`.

- [ ] **Step 2: Restructure `generate_html()` in `djstartlib/models/utils/helper.py` to satisfy 79 columns**

Reformat `generate_html()` using line-broken string concatenation that yields the exact identical string:
```python
def generate_html():
    """
    :return:
    Html Code
    """

    s = (
        "<!DOCTYPE html>\n"
        '<html lang="en">\n'
        "    <head>\n"
        '        <meta charset="UTF-8">\n'
        "        <title>Django Start</title>\n"
        "        <style>\n"
        "            *{text-align: center}\n"
        "            div{display:flex; justify-content:center}\n"
        "        </style>\n"
        "    </head>\n"
        "    <body>\n"
        '        <h1 style="text-align: center">Hello, Django-Start</h1>\n'
        '        <a style="text-align: center" class="github-button" '
        'href="https://github.com/islam-kamel/django-start" '
        'data-color-scheme="no-preference: light; light: light; dark: dark;" '
        'data-size="large" data-show-count="true" '
        'aria-label="Star islam-kamel/django-start on GitHub">'
        "Django-Start</a>\n"
        "    </body>\n"
        '    <script async defer src="https://buttons.github.io/buttons.js"></script>\n'
        "</html>"
    )
    return s
```

- [ ] **Step 3: Wrap long strings in `djstartlib/main.py` and `djstartlib/version.py`**

In `djstartlib/main.py`:
Wrap `click.secho` deprecation message:
```python
        click.secho(
            "Please Don't Use This Option is Deprecated By Default Created "
            "Virtual Environment",
            fg="white",
            bg="red",
        )
```
In `djstartlib/version.py`:
Wrap `request.urlopen`:
```python
    res = request.urlopen(
        "https://api.github.com/repos/islam-kamel/django-start/tags"
    )
```

- [ ] **Step 4: Run Black, Flake8, and Pyupgrade on `djstartlib/` via pre-commit**

Run:
```bash
pre-commit run black --files $(git ls-files 'djstartlib/*.py')
pre-commit run flake8 --files $(git ls-files 'djstartlib/*.py')
pre-commit run pyupgrade --files $(git ls-files 'djstartlib/*.py')
```
Expected: Black formats, Flake8 reports 0 errors, Pyupgrade makes 0 modifications.

- [ ] **Step 5: Perform semantic-diff review of all production changes against `0778ade36f8a0b35f7291d9c0a8154bcea5c989e`**

Inspect each diff hunk in `djstartlib/**` and classify into allowed categories:
- whitespace
- Black formatting
- line wrapping
- indentation formatting
- targeted compatibility-preserving `# noqa`
- source representation change protected by exact output characterization
Ensure no behavioral changes or bug fixes are present.

- [ ] **Step 6: Run full test suite and verify generated HTML exact match**

Run: `.venv/bin/pytest`
Expected: All tests pass.

- [ ] **Step 7: Commit**

```bash
git add djstartlib/
git commit -m "style: normalize legacy source without behavior changes"
```

---

### Task 5: Update AGENTS.md with Reinforced Quality-Gate Policies

**Files:**
- Modify: `AGENTS.md`

**Interfaces:**
- Consumes: Clarified quality-gate policy requirements from Task specification
- Produces: Explicit rules distinguishing characterization, normalization, and normal development phases; new invariants on pre-commit stability and tooling policy.

- [ ] **Step 1: Update AGENTS.md Quality Gates section**

Update `AGENTS.md` to:
1. Distinguish between:
   - *Characterization phase*: Production behavior must not be changed merely to satisfy formatting.
   - *Dedicated style-normalization phase*: Once behavioral characterization exists, repository-wide behavior-preserving formatting may be performed as an isolated task under the protection of characterization tests.
   - *Normal development after normalization*: No task may introduce or leave code-style violations. `pre-commit run --all-files` must remain green.
2. Add explicit invariant:
   > "Once the repository reaches a fully green pre-commit baseline, no subsequent task may reintroduce a pre-commit failure."
3. Add explicit invariant:
   > "Existing formatter/linter rules may only be changed through a dedicated tooling-policy decision, never as a shortcut to make a failing change pass."

- [ ] **Step 2: Ensure EOF newline in `AGENTS.md`**

Ensure `AGENTS.md` ends with a single newline and has no trailing whitespace.

- [ ] **Step 3: Commit**

```bash
git add AGENTS.md
git commit -m "docs: enforce repository-wide style quality gate"
```

---

### Task 6: Repository-Wide Pre-Commit Verification and Stability Pass

**Files:**
- None (verification and stability confirmation)

**Interfaces:**
- Consumes: All pre-commit hooks and test suite
- Produces: Confirmation of 100% green pre-commit run and idempotency verification.

- [ ] **Step 1: Run `pre-commit run --all-files`**

Run: `pre-commit run --all-files`
Expected: Every hook reports `Passed` or legitimately `Skipped` (`check-executables-have-shebangs`). Exit code 0.

- [ ] **Step 2: Run second `pre-commit run --all-files` to verify idempotency**

Run: `pre-commit run --all-files`
Expected: Zero files modified. Exit code 0.

- [ ] **Step 3: Run pytest in canonical Python 3.11 environment**

Run: `.venv/bin/pytest --collect-only -q && .venv/bin/pytest`
Expected: All tests collected, all passed.

- [ ] **Step 4: Verify git status and diff integrity**

Run: `git status`
Expected: Working tree clean.

- [ ] **Step 5: Prepare final report with all required evidence**

Capture commit SHAs, hook results, test outputs, per-file production change classification, and `# noqa` justification matrix.
