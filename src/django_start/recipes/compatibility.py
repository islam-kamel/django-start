"""Pure deterministic recipe compatibility validation.

Validates explicit inputs — host Python version, selected
FrameworkRelease, current Django-Start version, and
RecipeMetadata constraints — without reading sys.version_info,
importlib.metadata, the system clock, or any ambient state.
"""

from packaging.version import Version

from django_start.domain.errors import (
    ConfigurationError,
    UnsupportedVersionError,
)
from django_start.domain.policies import FrameworkRelease
from django_start.domain.recipes import (
    SUPPORTED_RECIPE_SCHEMA_VERSION,
    RecipeMetadata,
)


def validate_recipe_compatibility(
    metadata: RecipeMetadata,
    host_python_version: Version,
    release: FrameworkRelease,
    django_start_version: Version,
) -> None:
    """Validate recipe compatibility against explicit inputs.

    Args:
        metadata: Parsed recipe metadata.
        host_python_version: The host Python version to check.
        release: The selected framework release.
        django_start_version: The running Django-Start version.

    Raises:
        UnsupportedVersionError: If Python, Django, or Django-Start
            version is incompatible with the recipe.
        ConfigurationError: If the recipe schema version is
            unsupported.
    """
    _validate_schema_version(metadata.recipe_schema_version)
    _validate_python(metadata, host_python_version)
    _validate_django(metadata, release)
    _validate_django_start(metadata, django_start_version)


def _validate_schema_version(schema_version: str) -> None:
    """Validate recipe schema version matches engine capability."""
    if schema_version != SUPPORTED_RECIPE_SCHEMA_VERSION:
        raise ConfigurationError(
            f"Unsupported recipe schema version: "
            f"{schema_version!r}. "
            f"This version of Django-Start supports schema "
            f"version {SUPPORTED_RECIPE_SCHEMA_VERSION!r}. "
            f"A newer Django-Start version may be required."
        )


def _validate_python(
    metadata: RecipeMetadata,
    host_python_version: Version,
) -> None:
    """Validate host Python is within recipe requirements."""
    if host_python_version not in metadata.python_requires:
        raise UnsupportedVersionError(
            f"Host Python {host_python_version} is not "
            f"compatible with recipe '{metadata.name}'. "
            f"Requires: {metadata.python_requires}"
        )


def _validate_django(
    metadata: RecipeMetadata,
    release: FrameworkRelease,
) -> None:
    """Validate selected Django release is within recipe range."""
    if release.tested_version not in metadata.django_requires:
        raise UnsupportedVersionError(
            f"Django {release.tested_version} (series "
            f"{release.series}) is not compatible with "
            f"recipe '{metadata.name}'. "
            f"Requires: {metadata.django_requires}"
        )


def _validate_django_start(
    metadata: RecipeMetadata,
    django_start_version: Version,
) -> None:
    """Validate Django-Start version is within recipe range."""
    if django_start_version not in metadata.django_start_requires:
        raise UnsupportedVersionError(
            f"Django-Start {django_start_version} is not "
            f"compatible with recipe '{metadata.name}'. "
            f"Requires: {metadata.django_start_requires}"
        )
