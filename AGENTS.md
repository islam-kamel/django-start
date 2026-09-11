# Global Rules

## 1. Engineering Objective

Django-Start is a deterministic, safe, extensible Django project scaffolding tool.

Every architectural or implementation decision MUST optimize for:

1. Safe project generation.
2. Predictable and reproducible output.
3. Compatibility with supported Python and Django versions.
4. Extensibility without modification of the core workflow.
5. Testability.
6. Cross-platform behavior.
7. Backward compatibility where it does not compromise correctness or security.

SOLID is a design constraint, not a requirement to maximize the number of classes.

---

## 2. Product Invariants

These rules are non-negotiable.

### 2.1 Never silently destroy user data

Django-Start MUST NOT overwrite an existing user-controlled file unless the operation was explicitly requested.

Existing projects, apps, settings, URLs, templates, dependency manifests, and configuration files MUST be treated as user data.

A conflict MUST produce a clear actionable error.

### 2.2 Generation must be deterministic

The same:

* Django-Start version
* recipe version
* Python version
* Django version
* command options

MUST produce equivalent project structure and configuration.

Unbounded commands such as:

```text
pip install django
```

are forbidden in project generation.

The exact selected Django version MUST be known before generation begins.

### 2.3 No hidden shell execution

`shell=True` is forbidden.

Commands MUST be passed as argument sequences.

Example:

```python
runner.run(
    [
        python_executable,
        "-m",
        "pip",
        "install",
        f"Django=={django_version}",
    ]
)
```

Never:

```python
subprocess.run(
    f"{python} -m pip install Django=={version}",
    shell=True,
)
```

User-provided values MUST never be interpolated into shell commands.

### 2.4 No hidden network operations

Network operations MUST be explicit and attributable.

The tool MUST NOT:

* upgrade pip without being asked;
* update itself;
* download arbitrary templates silently;
* install an unspecified Django version.

### 2.5 A successful generation is a verified generation

Before reporting success, Django-Start MUST verify the generated project.

At minimum:

```text
python manage.py check
```

must succeed.

Generated Python files MUST compile successfully.

---

## Development Rules
**READ** [DEVELOPMENT_RULES.md](DEVELOPMENT_RULES.md)
