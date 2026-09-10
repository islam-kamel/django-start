# Django-Start 1.1.6 Baseline Documentation & Contract Matrix

## 1. Executive Summary

This document establishes the authoritative behavioral baseline for `django-start` version 1.1.6.
Prior to undertaking architectural modernization and refactoring for version 2.0, the identified observable behavior contracts of version 1.1.6 were characterized through a deterministic test suite consisting of 44 tests across 8 test modules.

In accordance with the project engineering rules:
- Production code in `djstartlib/` was kept strictly immutable.
- Packaging metadata in `setup.cfg` and `pyproject.toml` remained untouched.
- Test infrastructure was completely isolated using `pytest.ini` (`pythonpath = .`) and `requirements-test.txt` (`pytest==8.3.4`).
- All 31 identified behavior contracts (`BC-BOOT-01` through `BC-ORCH-01`) were validated and classified as `intended`, `legacy-reliance`, or `known-defect`.

---

## 2. Canonical Environment & Historical Assumptions

### 2.1 Canonical Characterization Environment
- **Python Target**: Python 3.11 is the canonical execution target for reproducing and verifying 1.1.6 behavior.
- **Historical Support Matrix**: The legacy packaging declared `python_requires = >=3.7` and classified Python 3.7, 3.8, 3.9, 3.10, and 3.11 as supported.
- **Separation of Concerns**: Python 3.14 and future versions are modernization targets for Django-Start 2.0 and do not alter the historical expectations of the 1.1.6 baseline.

### 2.2 Packaging & Entry Points
The distribution package `django-start-automate` 1.1.6 defines two CLI console entry points in `setup.cfg`:
- `django-start = djstartlib.main:main`: Primary CLI for scaffolding projects and applications.
- `django-version = djstartlib.version:main`: CLI for displaying version and checking/installing updates.

Both entry point callables are verified as importable and resolve to callables without side effects upon import in `tests/unit/test_bootstrap.py` (validating entry point symbol resolution; execution of the full CLI flows is characterized in `tests/unit/test_cli.py` and `tests/unit/test_version.py`).

### 2.3 Platform & Filesystem Assumptions
- **Virtualenv Executable Paths**: In `djstartlib/models/utils/helper.py` (`create_env`), path layout is determined via `platform.system()`:
  - Windows: sets `PYTHONEXEC` to `<env>\Scripts/python.exe` and `DJANGOADMIN` to `<env>\Scripts/django-admin.exe`.
  - Non-Windows (Linux / macOS): sets `PYTHONEXEC` to `<env>/bin/python3` and `DJANGOADMIN` to `<env>/bin/django-admin`.
  - **Environment Variable Mutation Quirk**: `create_env` unconditionally overwrites `PYTHONEXEC` (`os.environ['PYTHONEXEC'] = ...`), whereas `DJANGOADMIN` uses `os.environ.setdefault('DJANGOADMIN', ...)`. If `DJANGOADMIN` was pre-set in the environment, its existing value is preserved rather than updated to the new environment path.
- **Directory Layout**: Assumes a flat project structure where the Django project directory and application directory are siblings created inside the current working directory.
- **Encoding**: Files are opened with default system encoding without explicit `encoding="utf-8"`, creating cross-platform encoding vulnerabilities on non-UTF-8 default platforms (e.g., Windows CP1252).

---

## 3. Behavior Contract Matrix

The following matrix documents all 31 behavior contracts identified across the 1.1.6 codebase.
Each contract is classified as:
- **`intended`**: Expected, documented, and deliberate behavior of version 1.1.6.
- **`legacy-reliance`**: Observable behavior that existing users or workflows may rely on, but which requires architectural cleanup or deprecation in 2.0.
- **`known-defect`**: Defective, unsafe, or erroneous behavior reproduced and proven by test cases.

| ID | Surface | Input / Precondition | Observed Behavior | Classification | Test Target | Notes |
|---|---|---|---|---|---|---|
| `BC-BOOT-01` | Package / Import | `import djstartlib.main`, `import djstartlib.version` | Entry point modules are importable and callables resolve without side effects | legacy-reliance | `tests/unit/test_bootstrap.py` | Validates entry point symbols bound in `setup.cfg` without invoking installed console scripts. |
| `BC-CLI-01` | CLI (`django-start`) | `django-start myproject myapp` | Resolves virtualenv path to absolute `env/`, initializes `DjangoStart`, calls `setup_project()` and `setup_app(app_url="")` | intended | `tests/unit/test_cli.py` | Standard default scaffolding invocation. |
| `BC-CLI-02` | CLI (`django-start`) | `django-start myproject myapp -n custom_env` | Converts `-n`/`--name` option to absolute `pathlib.Path` and passes as env path | intended | `tests/unit/test_cli.py` | Supports custom virtual environment directory names. |
| `BC-CLI-03` | CLI (`django-start`) | `django-start myproject myapp -v` | Prints deprecation notice `Please Don't Use This Option is Deprecated` and continues execution | legacy-reliance | `tests/unit/test_cli.py` | Flag is deprecated in 1.1.6 but does not halt execution or alter behavior. |
| `BC-CLI-04` | CLI (`django-start`) | `django-start myproject myapp -u api/v1/` | Passes `-u`/`--url-path` string to `setup_app(app_url="api/v1/")` | intended | `tests/unit/test_cli.py` | Configures prefix route in root `urls.py`. |
| `BC-CLI-05` | CLI (`django-start`) | No arguments or missing required arguments | Click exits with status code 2 and usage text | intended | `tests/unit/test_cli.py` | Click standard argument validation. |
| `BC-VER-01` | CLI / Module (`django-version`) | `django-version` (no options) or importing `version` | Returns/prints static version string constant `"1.1.6 (beta)"` | intended | `tests/unit/test_version.py` | Static constant defined in `djstartlib/version.py`. |
| `BC-VER-02` | CLI / Module (`django-version`) | `django-version --check-update` with newer version available | Compares version tuples using `sum(var_int)` and prints `New Update Available <tag>` | known-defect | `tests/unit/test_version.py` | Flawed arithmetic comparison logic; see Section 4.1. |
| `BC-VER-03` | CLI / Module (`django-version`) | `django-version --check-update` with same or older version | Compares version tuples using `sum(var_int)` and prints `You have the latest version` | intended | `tests/unit/test_version.py` | Normal status branch when no newer version detected. |
| `BC-VER-04` | Function (`check_available`) | Network error (`urllib.error.URLError`) during GitHub API request | Catches `URLError` and immediately terminates process with `sys.exit(1)` (silent exit) | intended | `tests/unit/test_version.py` | Abrupt silent termination directly inside library function without warning output. |
| `BC-VER-05` | CLI (`django-version`) | `django-version --update` | Invokes `pip install --upgrade django-start-automate` via `subprocess.call` with `shell=True` | legacy-reliance / known-defect | `tests/unit/test_version.py` | Package self-update using shell execution; see Section 4.3. |
| `BC-ENV-01` | Class (`Environment`) | `Environment(app="blog", project="mysite")` instantiation | Tracks `app`, `project`, current working directory, and reads `PYTHONEXEC` / `DJANGOADMIN` from env | intended | `tests/unit/test_environment.py` | Base state container for `ProjectManager` and `AppManager`. |
| `BC-ENV-02` | Class (`Environment`) | In-memory line operations: `read_file`, `insert_line`, `replace_line`, `write` | Reads file lines into `self.line_list`, mutates line list by index, and writes back to disk | intended | `tests/unit/test_environment.py` | Primitive line manipulation mechanism. |
| `BC-PRJ-01` | Class (`ProjectManager`) | `ProjectManager(project="mysite", app="blog")` instantiation | Derives `urls_path` (`mysite/urls.py`) and `settings_path` (`mysite/settings.py`) relative to workdir | intended | `tests/unit/test_project_manager.py` | Computes project configuration file locations. |
| `BC-PRJ-02` | Method (`create_project`) | Project directory does not exist in working directory | Executes `django-admin startproject <project> .` | intended | `tests/unit/test_project_manager.py` | Scaffolds Django project files into current working directory. |
| `BC-PRJ-03` | Method (`create_project`) | Project directory already exists in working directory | Prints warning `"<project>" Already exist!` and skips command execution | intended | `tests/unit/test_project_manager.py` | Protects existing project directory from overwrite. |
| `BC-PRJ-04` | Method (`update_settings`) | Standard `settings.py` with `INSTALLED_APPS = [...]` closed by `]\n` | Locates exact line `]\n` and inserts `\t'<app>',\n` immediately before closing bracket | legacy-reliance | `tests/unit/test_project_manager.py` | Fragile exact whitespace/string matching; see Section 4.2. |
| `BC-PRJ-05` | Method (`update_settings`) | App already present in `settings.py` | Prints warning `"<app>" is installed!` and aborts mutation | intended | `tests/unit/test_project_manager.py` | Prevents duplicate entries in `INSTALLED_APPS`. |
| `BC-PRJ-06` | Method (`update_import_statment`) | `urls.py` containing `from django.urls import path\n` | Inserts `from django.urls import include\n` above `path` line; returns 0 if combined import exists | legacy-reliance | `tests/unit/test_project_manager.py` | Method name contains historical typo `update_import_statment`. |
| `BC-PRJ-07` | Method (`update_urls`) | Standard `urls.py` with `urlpatterns = [...]` closed by `]\n` | Ensures `include` import and inserts `\tpath('<path>', include('<app>.urls')),\n` before `]\n` | legacy-reliance | `tests/unit/test_project_manager.py` | Fragile exact bracket matching. |
| `BC-PRJ-08` | Method (`update_urls`) | Target route already present in `urls.py` | Prints warning `"Urls Already Updated"` and aborts mutation | intended | `tests/unit/test_project_manager.py` | Prevents duplicate route entries in `urlpatterns`. |
| `BC-APP-01` | Method (`create_app`) | App directory does not exist in working directory | Executes `python manage.py startapp <app>` in current working directory | intended | `tests/unit/test_app_manager.py` | Scaffolds Django app via project `manage.py`. |
| `BC-APP-02` | Method (`create_app`) | App directory already exists in working directory | Prints warning `"<app>" already exist!` and skips command execution | intended | `tests/unit/test_app_manager.py` | Protects existing app directory from overwrite. |
| `BC-APP-03` | Method (`update_view`) | Default `views.py` containing `# Create your views here.\n` | Replaces comment line with generated `home(request)` view rendering `<app>/index.html` | legacy-reliance | `tests/unit/test_app_manager.py` | Fragile replacement based on standard Django starter comment. |
| `BC-APP-04` | Method (`update_view`) | Default comment `# Create your views here.\n` missing from `views.py` | Prints warning `'"home" View is Exists!'` and skips file modification | legacy-reliance / known-defect | `tests/unit/test_app_manager.py` | Misleading warning; assumes absence of comment implies view exists. |
| `BC-APP-05` | Method (`create_urls`) | App directory exists | Writes `<app>/urls.py` with imports and `urlpatterns = [path('', views.home)]` | intended | `tests/unit/test_app_manager.py` | Creates initial app-level routing file. |
| `BC-APP-06` | Method (`create_templates`) | `templates/<app>/index.html` does not exist | Creates directory structure and writes default HTML starter page | intended | `tests/unit/test_app_manager.py` | Generates initial template in namespaced folder. |
| `BC-APP-07` | Method (`create_templates`) | `templates/<app>/index.html` already exists | Prints warning `"Index.html is Already exists."` and preserves existing file | intended | `tests/unit/test_app_manager.py` | Non-destructive behavior protecting user templates. |
| `BC-HLP-01` | Module (`helper`) | Template functions: `build_view_func()`, `build_views_urls()`, `generate_html()` | Produces `string.Template` instances and HTML strings for views and templates | intended | `tests/unit/test_helper.py` | Reusable string templates. |
| `BC-HLP-02` | Module (`helper`) | Command functions: `create_env`, `executable_python_command`, `executable_django_command`, `upgrade_pip`, etc. | Executes commands via `subprocess.call` with `shell=True` and `DEVNULL`; sets environment variables (overwriting `PYTHONEXEC`, preserving `DJANGOADMIN` if preset); exits on error | legacy-reliance / known-defect | `tests/unit/test_helper.py` | Unsafe shell execution, platform-dependent environment path logic (POSIX vs Windows Scripts), and mutable process-wide state. |
| `BC-ORCH-01` | Class (`DjangoStart`) | Full pipeline execution: `setup_project()` followed by `setup_app(app_url)` | Coordinates virtualenv creation, project scaffolding, pip upgrade, django install, requirements dump, settings/url updates, and app setup | intended | `tests/integration/test_scaffold_orchestration.py` | Mocked-boundary integration test exercising complete generation workflow. |

---

## 4. Documented Reproduction of Quirks & Defects

### 4.1 `sum(var_int)` Version Comparison Defect (`BC-VER-02`)
In `djstartlib/version.py`:
```python
def check_available():
    latest_tag, latest_tag_int = latest_version()
    if sum(latest_tag_int) > sum(current_version()):
        print(f"New Update Available {latest_tag}")
        return True
    print("You have the latest version")
```
Where `latest_version()` converts version segments to integers:
- Comparing `1.0.9` (`sum = 1 + 0 + 9 = 10`) against `1.1.6` (`sum = 1 + 1 + 6 = 8`) yields `10 > 8 == True`. The tool falsely reports an update is available for an older version.
- Comparing `2.0.0` (`sum = 2 + 0 + 0 = 2`) against `1.1.6` (`sum = 8`) yields `2 > 8 == False`. The tool falsely reports that `1.1.6` is the latest version when a major version 2.0.0 is released.
- This defect is characterized in `tests/unit/test_version.py` (`test_check_available_arithmetic_quirk` and `test_check_available_when_newer`).

### 4.2 Reliance on Exact Whitespace and `line_list.index("]\n")` (`BC-PRJ-04`, `BC-PRJ-07`)
In `djstartlib/models/project_manager.py`:
```python
self.insert_line("]\n", f"\t'{self.app}',\n")
```
And in `update_urls`:
```python
self.insert_line("]\n", f"\tpath('{path}', include('{self.app}.urls')),\n")
```
- The implementation searches for the exact string `"]\n"` in `self.line_list`.
- If a user or code formatter (such as Black or Ruff) formats the closing bracket with indentation (e.g. `    ]\n` or `\t]\n`), or if there is a trailing comma on the preceding line without an exact newline after the bracket, `index("]\n")` raises an unhandled `ValueError`.
- Furthermore, `update_settings` inserts before the FIRST occurrence of `"]\n"` found in the file. If another list in `settings.py` precedes `INSTALLED_APPS` (e.g., `MIDDLEWARE = [...]` or a custom list), the app name would be injected into the wrong configuration setting.

### 4.3 `shell=True` Subprocess Execution and Unpinned Dependencies (`BC-VER-05`, `BC-HLP-02`)
In `djstartlib/models/utils/helper.py`:
```python
def executable_python_command(command: str):
    ...
    if subprocess.call(f"{os.environ['PYTHONEXEC']} {command}",
                       stdout=subprocess.DEVNULL,
                       stderr=subprocess.STDOUT, shell=True) == 1:
        sys.exit(1)
```
- `shell=True` is used for all command executions (`create_env`, `upgrade_pip`, `install_dep`, `requirements_extract`, `executable_python_command`, `executable_django_command`).
- Running subprocesses through a shell exposes command string interpolation hazards and platform-specific shell quirks.
- `install_dep()` executes unpinned `pip install django`, violating product determinism (BC rule 2.2).
- `upgrade_pip()` executes unbounded `pip install --upgrade pip` without user opt-in.
- `requirements_extract()` executes `pip freeze > requirements.txt`, dumping the entire virtualenv state rather than explicitly declaring required dependencies.

### 4.4 Incomplete Deprecation Handling for `--virtualenv` / `-v` (`BC-CLI-03`)
In `djstartlib/main.py`:
```python
@click.option('-v', '--virtualenv', is_flag=True, default=False,
              help="Please Don't Use This Option is Deprecated")
def main(name, virtualenv, ...):
    if virtualenv:
        warn_stdout("Please Don't Use This Option is Deprecated")
    app = DjangoStart(Path(name).absolute(), ...)
    ...
```
- The option was intended to allow skipping virtualenv creation or specifying virtualenv mode, but in 1.1.6 `DjangoStart` always calls `create_env()` unconditionally in its constructor.
- The flag serves no functional purpose other than printing a warning message to stdout.

### 4.5 Fragile View Replacement Heuristic (`BC-APP-03`, `BC-APP-04`)
In `djstartlib/models/app_manager.py`:
```python
def update_view(self):
    try:
        self.replace_line(
            self.index('# Create your views here.\n'),
            build_view_func().substitute(app_name=self.app, html_file="index.html")
        )
        self.write(self.views)
    except ValueError:
        warn_stdout('"home" View is Exists!')
```
- The code assumes that if `# Create your views here.\n` is missing, the `home` view already exists.
- If the view file was touched, edited, or formatted in any way, the tool skips generating the view function and emits a confusing warning message.

### 4.6 Process-Wide Side Effects & Mutable Global State (`BC-VER-04`, `BC-HLP-02`)
- Subprocess failure in `executable_python_command` calls `sys.exit(1)`.
- Network failure in `check_available` calls `sys.exit(1)`.
- `create_env` mutates process-wide environment variables `os.environ["PYTHONEXEC"]` and `os.environ["DJANGOADMIN"]`.
- Library functions should raise typed exceptions instead of aborting the host process.

---

## 5. Safety Net Guarantees for 2.0 Modernization

The baseline characterization suite provides a robust safety net for the upcoming 2.0 refactoring:

1. **Deterministic Regression Protection**:
   - 44 tests continuously verify observable behavior across entry points, CLI parsing, environment modeling, project generation, app generation, template generation, and full orchestration.
   - All tests run in isolated temporary environments (`tmp_path`) with zero network access and zero mutation of developer filesystems.

2. **Clean Boundary Separation**:
   - The test suite distinguishes between intended contracts to preserve (e.g., non-destructive template preservation, directory conflict checks) and known defects to resolve (e.g., `sum(var_int)` comparison, `shell=True`, `line_list.index("]\n")`).

3. **Modernization Architectural Roadmap**:
   - Under the 2.0 architecture defined in `AGENTS.md`:
     - CLI parsing will move to Click 8+ clean command trees (`new` subcommand).
     - Subprocess execution will pass through a typed `CommandRunner` port with argument sequences (`shell=False`).
     - Virtual environment management will be handled by an isolated `EnvironmentManager` adapter.
     - Settings and URL manipulation will use robust AST or controlled template generation instead of naive string bracket replacement.
     - The package self-updater (`django-version --update`) will be removed.

---

## 6. Mechanical Verification Summary

### 6.1 Test Collection Count
Executing `.venv/bin/pytest --collect-only -q`:
```text
tests/integration/test_scaffold_orchestration.py::test_full_scaffold_lifecycle
tests/unit/test_app_manager.py::test_app_paths
tests/unit/test_app_manager.py::test_create_app_when_new
tests/unit/test_app_manager.py::test_create_app_when_exists
tests/unit/test_app_manager.py::test_update_view_replaces_default_comment
tests/unit/test_app_manager.py::test_update_view_warns_when_comment_missing
tests/unit/test_app_manager.py::test_create_urls
tests/unit/test_app_manager.py::test_create_templates
tests/unit/test_app_manager.py::test_create_templates_warns_when_already_exists
tests/unit/test_bootstrap.py::test_package_entry_points_importable
tests/unit/test_cli.py::test_cli_missing_arguments_fails
tests/unit/test_cli.py::test_cli_default_invocation
tests/unit/test_cli.py::test_cli_custom_options
tests/unit/test_environment.py::test_environment_initialization
tests/unit/test_environment.py::test_environment_file_operations
tests/unit/test_helper.py::test_template_generators
tests/unit/test_helper.py::test_warn_stdout
tests/unit/test_helper.py::test_create_env_sets_environment_variables
tests/unit/test_helper.py::test_create_env_windows_default_paths
tests/unit/test_helper.py::test_create_env_windows_django_admin_setdefault_behavior
tests/unit/test_helper.py::test_executable_python_command
tests/unit/test_helper.py::test_executable_python_command_failure_exits
tests/unit/test_helper.py::test_executable_django_command
tests/unit/test_helper.py::test_helper_shortcut_commands
tests/unit/test_project_manager.py::test_project_paths
tests/unit/test_project_manager.py::test_create_project_when_new
tests/unit/test_project_manager.py::test_create_project_when_exists
tests/unit/test_project_manager.py::test_update_settings_inserts_app_before_closing_bracket
tests/unit/test_project_manager.py::test_update_settings_warns_when_already_installed
tests/unit/test_project_manager.py::test_update_import_statement_inserts_include
tests/unit/test_project_manager.py::test_update_import_statement_skips_when_combined_present
tests/unit/test_project_manager.py::test_update_urls_wiring
tests/unit/test_project_manager.py::test_update_urls_warns_when_already_present
tests/unit/test_project_manager.py::test_helper_delegations
tests/unit/test_version.py::test_version_string
tests/unit/test_version.py::test_current_version_tuple
tests/unit/test_version.py::test_latest_version_parsing
tests/unit/test_version.py::test_check_available_when_newer
tests/unit/test_version.py::test_check_available_when_not_newer
tests/unit/test_version.py::test_check_available_arithmetic_quirk
tests/unit/test_version.py::test_check_available_url_error
tests/unit/test_version.py::test_cli_version_default
tests/unit/test_version.py::test_cli_version_check_update
tests/unit/test_version.py::test_cli_version_update_invokes_pip_with_shell

44 tests collected in 0.10s
```

### 6.2 Test Execution Results
Executing `.venv/bin/pytest`:
```text
============================= test session starts ==============================
platform darwin -- Python 3.11.16, pytest-8.3.4, pluggy-1.6.0
rootdir: /Volumes/Dev/Personal/django-start
configfile: pytest.ini
testpaths: tests
collected 44 items

tests/integration/test_scaffold_orchestration.py .                       [  2%]
tests/unit/test_app_manager.py ........                                  [ 20%]
tests/unit/test_bootstrap.py .                                           [ 22%]
tests/unit/test_cli.py ...                                               [ 29%]
tests/unit/test_environment.py ..                                        [ 34%]
tests/unit/test_helper.py .........                                      [ 54%]
tests/unit/test_project_manager.py ..........                            [ 77%]
tests/unit/test_version.py ..........                                    [100%]

============================== 44 passed in 0.13s ==============================
```

### 6.3 Test Distribution by Functional Area
| Test File | Type | Tests | Primary Contracts Characterized |
|---|---|---|---|
| `tests/unit/test_bootstrap.py` | Unit | 1 | `BC-BOOT-01` |
| `tests/unit/test_cli.py` | Unit | 3 | `BC-CLI-01`, `BC-CLI-02`, `BC-CLI-03`, `BC-CLI-04`, `BC-CLI-05` |
| `tests/unit/test_version.py` | Unit | 10 | `BC-VER-01`, `BC-VER-02`, `BC-VER-03`, `BC-VER-04`, `BC-VER-05` |
| `tests/unit/test_environment.py` | Unit | 2 | `BC-ENV-01`, `BC-ENV-02` |
| `tests/unit/test_project_manager.py` | Unit | 10 | `BC-PRJ-01`, `BC-PRJ-02`, `BC-PRJ-03`, `BC-PRJ-04`, `BC-PRJ-05`, `BC-PRJ-06`, `BC-PRJ-07`, `BC-PRJ-08` |
| `tests/unit/test_app_manager.py` | Unit | 8 | `BC-APP-01`, `BC-APP-02`, `BC-APP-03`, `BC-APP-04`, `BC-APP-05`, `BC-APP-06`, `BC-APP-07` |
| `tests/unit/test_helper.py` | Unit | 9 | `BC-HLP-01`, `BC-HLP-02` |
| `tests/integration/test_scaffold_orchestration.py` | Integration | 1 | `BC-ORCH-01` |
| **Total** | | **44** | **31 Identified Contracts Characterized** |
