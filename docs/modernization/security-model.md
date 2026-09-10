# Django-Start 2.0 Security Model & Threat Review

## 1. Executive Summary

As a developer CLI tool that provisions virtual environments, executes Python processes, and modifies the local filesystem, Django-Start operates in a high-privilege local execution context.

The security engineering objective is:
> **Prevent arbitrary command execution, path traversal, silent data loss, supply-chain poisoning, and environment leakage through strict defensive invariants.**

---

## 2. Threat & Mitigation Matrix

| Threat ID | Threat Category | Severity | Attack Mechanism | 1.1.6 Baseline Status | 2.0 Architectural Mitigation | Verification Mechanism |
|---|---|---|---|---|---|---|
| **THREAT-01** | Shell Injection | **Critical** | Attacker passes shell metacharacters in `--name`, `project_name`, or `--url-path` (e.g. `test; rm -rf /`). | **Vulnerable**: All subprocesses use `shell=True` and unquoted string interpolation. | **`shell=False` Invariant**: `subprocess.run` with argument sequences (`list[str]`). Identifier regex validation (`^[a-zA-Z_][a-zA-Z0-9_]*$`). | Automated unit test asserting rejection of shell metacharacters; static grep verifying zero `shell=True`. |
| **THREAT-02** | Path Traversal | **High** | Attacker provides relative path escape in project or app name (e.g. `../../sensitive`). | **Vulnerable**: `pathlib.Path(name).absolute()` does not prevent writing outside intended working directory. | **Strict Traversal Guard**: Target path must resolve inside designated project root. App names restricted to valid Python identifiers. | Unit tests attempting `../` escapes verified to raise `ConfigurationError`. |
| **THREAT-03** | Silent Data Destruction | **Critical** | Scaffolding overwrites existing `settings.py`, `urls.py`, or deletes existing user project directories. | **Partial / Defective**: Checks `os.path.exists` on root dir, but mutates files in-place without backup or rollback. | **Non-Destructive Invariant**: Generator aborts with `ProjectConflictError` if target contains files. Atomic writes with backup. | Integration test ensuring existing files remain bit-identical after conflict rejection. |
| **THREAT-04** | Supply Chain / Unpinned Dependency | **High** | Generator executes unpinned `pip install django` or unbounded pip upgrade, pulling untrusted or broken packages. | **Vulnerable**: Executes unpinned `pip install django` and `pip install --upgrade pip`. | **Deterministic Version Lock**: Every recipe locks exact tested patch versions (`Django==6.1.1`). No hidden pip upgrades. | Integration test verifying exact version match and zero unprompted package upgrades. |
| **THREAT-05** | Insecure Self-Update / Network Trust | **High** | Tool executes `pip install --upgrade django-start-automate` via shell; queries unauthenticated GitHub API. | **Vulnerable**: `django-version --update` executes pip via shell; silent crash on network error. | **Self-Update Removed**: Package managers own updates. Update checks use explicit `doctor` command with timeout. | Verify elimination of `--update` CLI option and shell call. |
| **THREAT-06** | Subprocess Environment Leakage | **Medium** | Host process leaks secrets (AWS keys, DB tokens, auth headers) into generated project venv logs. | **Uncontrolled**: Subprocesses inherit host `os.environ` completely and mutate process-wide state. | **Sanitized Environment**: Subprocesses execute with explicit filtered environment passing only necessary system paths. | Unit test verifying sanitized subprocess environment mapping. |
| **THREAT-07** | Untrusted Third-Party Recipe Code Execution | **High** | Third-party recipes executing arbitrary shell or Python code during project scaffolding. | **N/A (New Feature)** | **Sandboxed Recipe Model**: 2.0 recipes are declarative JSON/YAML + templates only. Executable Python hooks are forbidden in external recipes. | Schema validation rejecting non-declarative recipe definitions. |
| **THREAT-08** | Insecure Temporary Files / Race Conditions | **Medium** | Predictable temporary filenames in shared `/tmp` vulnerable to symlink attacks. | **Unused**: Did not use staging directories. | **Secure Staging**: Staging directories created via `tempfile.TemporaryDirectory` with `0700` permissions. | Audit temporary file lifecycle during rollback tests. |

---

## 3. Project & App Identifier Validation Rules

Django project and application names must satisfy strict lexical constraints before any filesystem or process operation begins:

1. **Python Identifier Validity**:
   - Must be a valid Python identifier matching `^[a-zA-Z_][a-zA-Z0-9_]*$`.
   - Cannot start with a digit or hyphen.
2. **Python Keyword Exclusion**:
   - Must not conflict with Python keywords (`import`, `from`, `class`, `def`, `return`, `pass`, `global`, etc.) via `keyword.iskeyword()`.
3. **Django Internal Name Exclusion**:
   - Must not conflict with standard Django module names (`django`, `test`, `site`, `apps`, `models`, `views`, `urls`).
4. **Length and Character Set**:
   - Maximum length: 100 characters.
   - Prohibited characters: spaces, slashes, backslashes, periods, null bytes, shell metacharacters (`;&|><$`).

Failure to satisfy these rules immediately raises `ConfigurationError` and exits with code 2.

---

## 4. Execution Sandbox & Permission Invariants

### 4.1 File Permissions
- All created directories are created with standard mode `0755` (user read/write/execute, group/others read/execute).
- All created text files are created with standard mode `0644` (user read/write, group/others read).
- Generated virtualenv binaries retain executable permissions created by standard library `venv`.

### 4.2 Network Isolation
- Scaffolding operations must not require network access unless package installation from PyPI is explicitly required.
- If pre-downloaded wheels or wheel caches are available, generation operates fully offline.
- Update checks must never block or delay scaffolding workflows; they run asynchronously or during explicit `doctor` invocations with a strict 2-second timeout.
