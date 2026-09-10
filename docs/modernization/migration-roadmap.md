# Django-Start 2.0 Phased Migration Roadmap & Testing Architecture

## 1. Executive Summary

This document defines the ordered implementation roadmap to transition Django-Start from 1.1.6 to 2.0.0.

The roadmap strictly forbids "rewrite everything" approaches. Every phase is an isolated, test-protected milestone that leaves the repository green, with passing quality gates and zero regressions against characterization contracts.

---

## 2. Testing Architecture

The testing strategy follows a rigorous multi-tier pyramid ensuring both backward characterization fidelity and forward contract verification.

```mermaid
flowchart TD
    subgraph Pyramid ["Testing Pyramid"]
        E2E["Tier 4: Cross-Platform Packaging Smoke Tests (Ubuntu, Windows, macOS)"]
        GEN_TEST["Tier 3: Generated-Project Verification (manage.py check & py_compile)"]
        INT_TEST["Tier 2: Application Use Case & Adapter Contract Tests (Mocked Boundaries)"]
        UNIT_TEST["Tier 1: Fast Domain & Unit Tests (Validation, Policies, Layout)"]
        CHAR_TEST["Foundation: 45 Legacy Characterization Tests (Python 3.11 Isolation)"]
    end

    CHAR_TEST --> UNIT_TEST
    UNIT_TEST --> INT_TEST
    INT_TEST --> GEN_TEST
    GEN_TEST --> E2E
```

### 2.1 Test Layers Detailed

1. **Foundation: Legacy Characterization Suite**:
   - The existing 45 tests in `tests/` remain intact during early phases.
   - Run in isolated virtual environments under Python 3.11.
   - Serve as an unyielding regression detector while legacy interfaces remain.
2. **Tier 1: Unit & Domain Tests**:
   - Zero filesystem, network, or subprocess I/O.
   - Test `ProjectConfig`, naming validation regexes, recipe schemas, version comparison policies, and CLI argument parsing.
   - Execution time: < 100ms.
3. **Tier 2: Use Case & Adapter Contract Tests**:
   - Test `CreateProjectUseCase` and `AddAppUseCase` using `FakeCommandRunner` and `InMemoryFileSystem`.
   - Verify that use cases construct correct command sequences and handle errors predictably without spawning processes.
4. **Tier 3: Generated Project Verification Tests**:
   - Real subprocess executions in isolated temporary folders (`tmp_path`).
   - Run `django-admin startproject` and apply recipes.
   - **Mandatory Verification**: Every generated project configuration must pass `python manage.py check` and compile via `python -m py_compile`.
5. **Tier 4: Packaging & CLI Smoke Tests**:
   - Build wheels via `python -m build`.
   - Install wheels into a fresh, isolated test venv.
   - Execute `django-start --help`, `django-start doctor`, and `django-start new smoke_test`.

---

## 3. Target CI Architecture

### 3.1 CI Workflow Organization

```mermaid
flowchart LR
    subgraph PR ["Pull Request Pipeline (Blocking)"]
        PR_LINT["Ruff Lint & Format"]
        PR_TYPE["Mypy Strict Check"]
        PR_CHAR["Legacy 1.1.6 Tests (Py 3.11)"]
        PR_UNIT["2.0 Test Suite (Py 3.12-3.14)"]
        PR_SMOKE["Generated Project Smoke (Linux)"]
    end

    subgraph SCHEDULED ["Scheduled / Release Pipeline"]
        NATIVE_WIN["Windows 11 Runner"]
        NATIVE_MAC["macOS 14+ Runner"]
        CANARY["Python 3.15 RC Canary"]
        CODEQL["CodeQL Analysis v3"]
        PKG_BUILD["Wheel & sdist Build Verification"]
    end

    PR --> SCHEDULED
```

- **PR Gate (Fast, Blocking)**: Runs on Ubuntu with Python 3.12, 3.13, 3.14. Must finish in under 3 minutes.
- **Cross-Platform Gate (Release/Main)**: Runs on native Windows and macOS runners.
- **Canary Gate**: Weekly scheduled run against Python 3.15 preview.

---

## 4. Phased Migration Roadmap

```mermaid
flowchart TD
    P0["Phase 0: Baseline & Discovery (Current Complete State)"] --> P1["Phase 1: Tooling & Quality Gate Modernization"]
    P1 --> P2["Phase 2: Packaging Foundation & src/ Layout"]
    P2 --> P3["Phase 3: Domain Models & Ports Definition"]
    P3 --> P4["Phase 4: Infrastructure Adapters (Safe Runner & FS)"]
    P4 --> P5["Phase 5: Recipe Engine & Controlled Templates"]
    P5 --> P6["Phase 6: Application Use Cases & Verifier"]
    P6 --> P7["Phase 7: Modern CLI Tree & Subcommands"]
    P7 --> P8["Phase 8: Generated Project Smoke Tests & CI Matrix"]
    P8 --> P9["Phase 9: Documentation, Deprecations & 2.0 Release"]
```

---

### Phase 1: Tooling & Quality Gate Modernization

- **Objective**: Introduce Ruff and Mypy into the repository quality pipeline without modifying production behavior or breaking characterization tests.
- **Components Affected**: `pyproject.toml`, `.pre-commit-config.yaml`, `requirements-dev.txt`.
- **Prerequisites**: Baseline 1.1.6 green (current state).
- **Contracts Preserved**: All 31 contracts (`BC-BOOT-01` through `BC-ORCH-01`).
- **Tests Required**: 45/45 characterization tests passing; `pre-commit run --all-files` green.
- **Rollback Boundary**: Revert `pyproject.toml` and `.pre-commit-config.yaml` to Black/Flake8.
- **Completion Criteria**: Pre-commit runs Ruff format and Ruff check cleanly across all repository files.

---

### Phase 2: Packaging Foundation & `src/` Layout

- **Objective**: Adopt standard `src/` layout (`src/django_start/`), configure PEP 621 metadata in `pyproject.toml`, establish `django-start-automate` distribution, and create a backward compatibility redirect for `djstartlib`.
- **Components Affected**: Move `djstartlib/` to `src/django_start/`, add `src/djstartlib/` shim, delete `setup.py` and `setup.cfg`.
- **Prerequisites**: Phase 1 complete.
- **Contracts Preserved**: `BC-BOOT-01` (entry points remain importable via shim).
- **Tests Required**: Wheel build succeeds; entry points execute; test suite imports from installed or src package cleanly.
- **Rollback Boundary**: Restore `setup.cfg` and flat layout.
- **Completion Criteria**: `python -m build` generates clean wheel containing `django_start` and `djstartlib` redirect.

---

### Phase 3: Domain Models & Ports Definition

- **Objective**: Create clean domain types and port protocols in `src/django_start/domain/` and `src/django_start/ports/`.
- **Components Affected**:
  - `src/django_start/domain/config.py` (`ProjectConfig`, `AppConfig`)
  - `src/django_start/domain/errors.py` (Exception hierarchy)
  - `src/django_start/domain/policies.py` (Identifier validation, version policies)
  - `src/django_start/ports/runner.py` (`CommandRunner`, `Command`, `CommandResult`)
  - `src/django_start/ports/filesystem.py` (`FileSystem`)
  - `src/django_start/ports/environment.py` (`EnvironmentManager`)
  - `src/django_start/ports/verifier.py` (`ProjectVerifier`)
- **Prerequisites**: Phase 2 complete.
- **Contracts Preserved**: Legacy code untouched; new modules purely additive.
- **Tests Required**: Unit tests for identifier validation, configuration immutability, and policy evaluation.
- **Rollback Boundary**: Remove additive domain/port files.
- **Completion Criteria**: 100% test coverage and 100% strict mypy typing on new domain modules.

---

### Phase 4: Infrastructure Adapters (Safe Subprocess & Filesystem)

- **Objective**: Implement concrete adapters adhering to port protocols: `SubprocessCommandRunner` (`shell=False`), `LocalFileSystem` (atomic writes, UTF-8), and `VenvEnvironmentManager`.
- **Components Affected**: `src/django_start/infrastructure/`.
- **Prerequisites**: Phase 3 complete.
- **Contracts Preserved**: Eliminates `shell=True` and unencoded file operations in new code.
- **Tests Required**: Adapter contract tests using isolated temporary directories; verification that `SubprocessCommandRunner` rejects shell metacharacters and executes commands safely.
- **Rollback Boundary**: Delete infrastructure adapters.
- **Completion Criteria**: Adapters pass contract test suites across POSIX and Windows path representations.

---

### Phase 5: Recipe Engine & Controlled Templates

- **Objective**: Implement the declarative recipe provider and bundle baseline project templates for Django 5.2 LTS and Django 6.1.
- **Components Affected**: `src/django_start/recipes/`, `src/django_start/infrastructure/builtin_recipes.py`.
- **Prerequisites**: Phase 4 complete.
- **Contracts Preserved**: Replaces fragile string bracket matching (`line_list.index("]\n")`).
- **Tests Required**: Snapshot tests verifying rendered settings, URLs, and templates across `standard`, `lts`, `api`, and `minimal` recipes.
- **Rollback Boundary**: Revert recipe directory and template assets.
- **Completion Criteria**: Recipe engine renders valid Python files that compile under `py_compile` without string hacking.

---

### Phase 6: Application Use Cases & Verification

- **Objective**: Implement application orchestration: `CreateProjectUseCase`, `AddAppUseCase`, `DiagnoseEnvironmentUseCase`, and `VerifyProjectUseCase`.
- **Components Affected**: `src/django_start/application/`.
- **Prerequisites**: Phase 5 complete.
- **Contracts Preserved**: Replaces procedural `DjangoStart.setup_project()` and `setup_app()`.
- **Tests Required**: Comprehensive use-case tests using `FakeCommandRunner` and `InMemoryFileSystem`; failure rollback verification.
- **Rollback Boundary**: Revert application use cases.
- **Completion Criteria**: Full orchestration executes in memory with complete mock boundaries, demonstrating staging, verification, and rollback.

---

### Phase 7: Modern CLI Tree & Subcommands

- **Objective**: Build the Click 8.5+ command interface (`django-start new`, `add`, `doctor`, `check`, `recipe`) and eliminate the legacy self-updater (`django-version --update`).
- **Components Affected**: `src/django_start/cli.py`.
- **Prerequisites**: Phase 6 complete.
- **Contracts Preserved**:
  - `BC-CLI-01` supported via backward-compatibility adapter for `django-start <project> <app>`.
  - `django-version` retained as a deprecation shim pointing to `--version`.
  - `BC-VER-05` (shell update) permanently removed.
- **Tests Required**: CLI runner tests verifying arguments, options, error presentation, exit codes, and deprecation notices.
- **Rollback Boundary**: Revert CLI entry points.
- **Completion Criteria**: All subcommands functional with clean user help output and standardized exit codes.

---

### Phase 8: Generated Project Smoke Tests & CI Matrix

- **Objective**: Construct end-to-end integration tests that generate real Django projects and execute `python manage.py check` inside provisioned environments.
- **Components Affected**: `tests/e2e/`, `.github/workflows/ci.yml`.
- **Prerequisites**: Phase 7 complete.
- **Contracts Preserved**: Confirms product invariant 2.5: a successful generation is a verified generation.
- **Tests Required**: Test matrix: Python [3.12, 3.13, 3.14] x Django [5.2 LTS, 6.1] on Ubuntu, macOS, and Windows.
- **Rollback Boundary**: Disable flaky CI combinations if upstream issues arise.
- **Completion Criteria**: All matrix combinations build and pass `manage.py check` cleanly in CI.

---

### Phase 9: Documentation, Deprecations & 2.0 Release

- **Objective**: Update documentation, write migration guides, publish release notes, and tag `2.0.0a1` release.
- **Components Affected**: `README.md`, `docs/`, `CHANGELOG.md`.
- **Prerequisites**: Phase 8 complete.
- **Completion Criteria**: Comprehensive user documentation, green release build, verified PyPI artifact.
