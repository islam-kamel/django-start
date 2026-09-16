"""Strict JSON recipe parser for Django-Start 2.0.

Implements fail-closed parsing semantics: any invalid, unknown,
or forbidden field causes immediate rejection with a typed
``ConfigurationError``. Raw parsing exceptions are never exposed
as public API behaviour.

Recipe Schema v1 is the only supported schema version.
"""

import json
import re
from pathlib import PurePosixPath

from packaging.requirements import InvalidRequirement, Requirement
from packaging.specifiers import InvalidSpecifier, SpecifierSet
from packaging.version import InvalidVersion, Version

from django_start.domain.errors import ConfigurationError
from django_start.domain.recipes import (
    SUPPORTED_RECIPE_SCHEMA_VERSION,
    RecipeMetadata,
)

# --- Schema Definition ---

_REQUIRED_FIELDS: frozenset[str] = frozenset(
    {
        "recipe_schema_version",
        "recipe_version",
        "name",
        "description",
        "python_requires",
        "django_requires",
        "django_start_requires",
        "dependencies",
        "template_dir",
    }
)

_FORBIDDEN_FIELDS: frozenset[str] = frozenset(
    {
        "post_generate_hooks",
        "pre_generate_hooks",
        "shell_commands",
        "python_hooks",
        "commands",
        "callbacks",
        "hooks",
        "scripts",
        "supported_tracks",
    }
)

# Canonical normalization per PEP 503
_NORMALIZE_RE = re.compile(r"[-_.]+")


def _normalize_package_name(name: str) -> str:
    """Normalize a package name per PEP 503."""
    return _NORMALIZE_RE.sub("-", name).lower()


# --- Public API ---


def parse_recipe_metadata(raw_json: str) -> RecipeMetadata:
    """Parse and validate a recipe JSON document.

    Args:
        raw_json: UTF-8 JSON string of a recipe metadata file.

    Returns:
        Validated, immutable ``RecipeMetadata``.

    Raises:
        ConfigurationError: On any validation failure including
            invalid JSON, missing fields, unknown fields, forbidden
            executable fields, invalid versions/specifiers, unsafe
            template paths, or malformed dependencies.
    """
    try:
        data = json.loads(raw_json)
    except json.JSONDecodeError as exc:
        raise ConfigurationError(f"Invalid recipe JSON: {exc}") from exc

    if not isinstance(data, dict):
        raise ConfigurationError(
            f"Recipe JSON must be an object, got {type(data).__name__}"
        )

    _reject_forbidden_fields(data)
    _reject_unknown_fields(data)
    _require_all_fields(data)

    schema_version = _parse_schema_version(data["recipe_schema_version"])
    recipe_version = _parse_version(data["recipe_version"], "recipe_version")
    name = _parse_name(data["name"])
    description = _parse_description(data["description"])
    python_requires = _parse_specifier(
        data["python_requires"], "python_requires"
    )
    django_requires = _parse_specifier(
        data["django_requires"], "django_requires"
    )
    django_start_requires = _parse_specifier(
        data["django_start_requires"], "django_start_requires"
    )
    dependencies = _parse_dependencies(data["dependencies"])
    template_dir = _parse_template_dir(data["template_dir"])

    return RecipeMetadata(
        recipe_schema_version=schema_version,
        recipe_version=recipe_version,
        name=name,
        description=description,
        python_requires=python_requires,
        django_requires=django_requires,
        django_start_requires=django_start_requires,
        dependencies=dependencies,
        template_dir=template_dir,
    )


# --- Internal Validators ---


def _reject_forbidden_fields(data: dict[str, object]) -> None:
    """Reject recipe documents containing executable escape hatches."""
    found = _FORBIDDEN_FIELDS & data.keys()
    if found:
        names = ", ".join(sorted(found))
        raise ConfigurationError(
            f"Recipe contains forbidden fields: {names}. "
            "Recipes must be strictly declarative — "
            "executable hooks are prohibited (ADR-009)."
        )


def _reject_unknown_fields(data: dict[str, object]) -> None:
    """Reject any fields not in the v1 schema."""
    unknown = set(data.keys()) - _REQUIRED_FIELDS
    if unknown:
        names = ", ".join(sorted(unknown))
        raise ConfigurationError(
            f"Recipe contains unknown fields: {names}. "
            f"Allowed fields: "
            f"{', '.join(sorted(_REQUIRED_FIELDS))}"
        )


def _require_all_fields(data: dict[str, object]) -> None:
    """Ensure all required v1 fields are present."""
    missing = _REQUIRED_FIELDS - set(data.keys())
    if missing:
        names = ", ".join(sorted(missing))
        raise ConfigurationError(f"Recipe is missing required fields: {names}")


def _parse_schema_version(value: object) -> str:
    """Parse and validate the recipe schema version.

    Treated as an exact protocol identifier, not a PEP 440
    version. Phase 5 accepts only ``"1.0"`` exactly.
    """
    if not isinstance(value, str):
        raise ConfigurationError(
            "recipe_schema_version must be a string, "
            f"got {type(value).__name__}"
        )
    if value != SUPPORTED_RECIPE_SCHEMA_VERSION:
        raise ConfigurationError(
            f"Unsupported recipe schema version: {value!r}. "
            f"This version of Django-Start supports schema "
            f"version {SUPPORTED_RECIPE_SCHEMA_VERSION!r}. "
            f"A newer Django-Start version may be required."
        )
    return value


def _parse_version(value: object, field: str) -> Version:
    """Parse a PEP 440 version string."""
    if not isinstance(value, str):
        raise ConfigurationError(
            f"{field} must be a string, got {type(value).__name__}"
        )
    try:
        return Version(value)
    except InvalidVersion as exc:
        raise ConfigurationError(
            f"Invalid PEP 440 version in {field}: {value!r}"
        ) from exc


def _parse_name(value: object) -> str:
    """Parse and validate the recipe name."""
    if not isinstance(value, str):
        raise ConfigurationError(
            f"name must be a string, got {type(value).__name__}"
        )
    if not value.strip():
        raise ConfigurationError("Recipe name must not be empty")
    return value


def _parse_description(value: object) -> str:
    """Parse the recipe description."""
    if not isinstance(value, str):
        raise ConfigurationError(
            f"description must be a string, got {type(value).__name__}"
        )
    return value


def _parse_specifier(value: object, field: str) -> SpecifierSet:
    """Parse a PEP 440 specifier set string."""
    if not isinstance(value, str):
        raise ConfigurationError(
            f"{field} must be a string, got {type(value).__name__}"
        )
    try:
        return SpecifierSet(value)
    except InvalidSpecifier as exc:
        raise ConfigurationError(
            f"Invalid PEP 440 specifier in {field}: {value!r}"
        ) from exc


def _parse_template_dir(value: object) -> PurePosixPath:
    """Parse and validate the template directory path."""
    if not isinstance(value, str):
        raise ConfigurationError(
            f"template_dir must be a string, got {type(value).__name__}"
        )
    if not value.strip():
        raise ConfigurationError("template_dir must not be empty")

    path = PurePosixPath(value)

    if path.is_absolute():
        raise ConfigurationError(
            f"template_dir must be relative, got: {value!r}"
        )
    if ".." in path.parts:
        raise ConfigurationError(
            f"template_dir must not contain '..', got: {value!r}"
        )
    return path


def _parse_dependencies(value: object) -> tuple[str, ...]:
    """Parse, validate, and deduplicate recipe dependencies.

    Rules:
    - Must be valid PEP 508 requirements
    - Must have bounded upper constraints
    - No direct URL dependencies
    - No option-like strings starting with ``-``
    - No duplicate package names after normalization
    - Must not declare Django itself
    """
    if not isinstance(value, list):
        raise ConfigurationError(
            f"dependencies must be an array, got {type(value).__name__}"
        )

    deps: list[str] = []
    seen_names: set[str] = set()

    for i, item in enumerate(value):
        if not isinstance(item, str):
            raise ConfigurationError(
                f"dependencies[{i}] must be a string, "
                f"got {type(item).__name__}"
            )

        dep_str = item.strip()
        if not dep_str:
            raise ConfigurationError(f"dependencies[{i}] must not be empty")

        if dep_str.startswith("-"):
            raise ConfigurationError(
                f"dependencies[{i}] looks like a pip option, "
                f"not a package requirement: {dep_str!r}"
            )

        try:
            req = Requirement(dep_str)
        except InvalidRequirement as exc:
            raise ConfigurationError(
                f"dependencies[{i}] is not a valid PEP 508 "
                f"requirement: {dep_str!r}"
            ) from exc

        # Reject direct URL dependencies
        if req.url:
            raise ConfigurationError(
                f"dependencies[{i}] must not use a direct URL: {dep_str!r}"
            )

        # Reject unbounded dependencies
        if not _has_upper_bound(req.specifier):
            raise ConfigurationError(
                f"dependencies[{i}] must have a bounded upper "
                f"constraint: {dep_str!r}. "
                f"Use e.g. 'package>=1.0,<2' instead of "
                f"'package>=1.0' or 'package'."
            )

        # Reject Django itself
        canonical = _normalize_package_name(req.name)
        if canonical == "django":
            raise ConfigurationError(
                f"dependencies[{i}] must not declare Django. "
                "Django is controlled exclusively by "
                "FrameworkRelease.django_requires."
            )

        # Reject duplicates
        if canonical in seen_names:
            raise ConfigurationError(
                f"dependencies[{i}] duplicates package "
                f"{req.name!r} (after normalization)"
            )
        seen_names.add(canonical)
        deps.append(dep_str)

    return tuple(deps)


def _has_upper_bound(specifier: SpecifierSet) -> bool:
    """Check if a specifier set contains an upper bound.

    An upper bound is any constraint using ``<``, ``<=``,
    ``==``, or ``~=`` (compatible release, which implies an upper
    bound on the next major/minor).
    """
    upper_ops = {"<", "<=", "==", "~="}
    for spec in specifier:
        if spec.operator in upper_ops:
            return True
    return False
