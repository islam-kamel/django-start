"""
Domain recipe types for Django-Start 2.0.

Immutable value objects representing parsed recipe data,
template bundles, rendered output, and scaffold plans.

All types are genuinely immutable via frozen dataclasses and
tuples. No mutable containers.
"""

from dataclasses import dataclass
from pathlib import PurePosixPath

from packaging.specifiers import SpecifierSet
from packaging.version import Version

from django_start.domain.config import ProjectConfig
from django_start.domain.policies import FrameworkRelease

# --- Recipe Schema Constants ---

SUPPORTED_RECIPE_SCHEMA_VERSION = "1.0"
"""Exact protocol version string for Recipe Schema v1.

This is treated as an exact protocol identifier, not a PEP 440
package version. Phase 5 accepts only ``"1.0"`` exactly.
"""


# --- Recipe Metadata ---


@dataclass(frozen=True, slots=True)
class RecipeMetadata:
    """Parsed, validated recipe metadata from a recipe.json file.

    All version constraints use PyPA standard types for
    PEP 440 compliance. The ``recipe_schema_version`` is an
    exact protocol string (not a PEP 440 Version) because it
    identifies a wire format, not a software release.
    """

    recipe_schema_version: str
    recipe_version: Version
    name: str
    description: str
    python_requires: SpecifierSet
    django_requires: SpecifierSet
    django_start_requires: SpecifierSet
    dependencies: tuple[str, ...]
    template_dir: PurePosixPath


# --- Template Assets ---


@dataclass(frozen=True, slots=True)
class RecipeTemplate:
    """A single template asset within a recipe bundle.

    Attributes:
        relative_path: The logical generated target path using
            ``__DJSTART_*__`` tokens for variable segments.
            For example: ``__DJSTART_PROJECT_NAME__/settings.py``
            or ``__DJSTART_APP_NAME__/apps.py``.
        content: UTF-8 text content of the template, containing
            ``__DJSTART_*__`` tokens for substitution.
        is_app_scoped: When True, this template is rendered once
            per ``AppConfig`` in the project. The
            ``__DJSTART_APP_NAME__`` token in the path and content
            is substituted with each app's name.
    """

    relative_path: PurePosixPath
    content: str
    is_app_scoped: bool


@dataclass(frozen=True, slots=True)
class RecipeBundle:
    """Immutable bundle of recipe metadata and template assets.

    Returned by ``RecipeProvider.get()``. Contains fully resolved
    text content — no open file handles or traversable references
    leak across the provider boundary.

    Templates include both framework baseline files and
    profile-specific overlays, already merged by the provider.
    """

    metadata: RecipeMetadata
    templates: tuple[RecipeTemplate, ...]


# --- Rendered Output ---


@dataclass(frozen=True, slots=True)
class RenderedFile:
    """A single rendered output file within a scaffold plan.

    Attributes:
        relative_path: Project-relative target path. Must be
            relative (no leading ``/``), contain no ``..``
            traversal, and resolve within the project root.
        content: Fully rendered UTF-8 text content with all
            ``__DJSTART_*__`` tokens resolved.
    """

    relative_path: PurePosixPath
    content: str


@dataclass(frozen=True, slots=True)
class ScaffoldPlan:
    """Immutable, deterministic output of the scaffold engine.

    Contains all information needed for Phase 6 to write files,
    create directories, install dependencies, and verify the
    generated project — without re-reading recipe metadata.

    Files are sorted deterministically by POSIX path string.
    Two identical inputs must produce equal plans.
    """

    files: tuple[RenderedFile, ...]
    requirements: tuple[str, ...]


@dataclass(frozen=True, slots=True)
class ScaffoldRequest:
    """Immutable request object for the scaffold engine.

    All compatibility inputs are explicit — the engine never
    reads ``sys.version_info``, ``importlib.metadata``, the
    system clock, or any other ambient state.
    """

    config: ProjectConfig
    release: FrameworkRelease
    recipe: RecipeBundle
    host_python_version: Version
    django_start_version: Version
    secret_key: str
