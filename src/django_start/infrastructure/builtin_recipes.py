"""Built-in recipe provider for Django-Start 2.0.

Loads package-owned JSON metadata and UTF-8 template assets
using ``importlib.resources``. Works identically from source
checkout and installed wheel.

Phase 5 supports built-in package recipes only — no arbitrary
external recipe paths, Git URLs, or entry-point plugins.
"""

from importlib import resources as importlib_resources
from pathlib import PurePosixPath
from typing import final

from django_start.domain.config import Profile
from django_start.domain.errors import ConfigurationError
from django_start.domain.policies import FrameworkRelease
from django_start.domain.recipes import (
    RecipeBundle,
    RecipeMetadata,
    RecipeTemplate,
)
from django_start.recipes.parser import parse_recipe_metadata

# Mapping from Django series to baseline directory name
_SERIES_TO_BASELINE: dict[str, str] = {
    "6.1": "django_6_1",
    "5.2": "django_5_2",
}

# Template file extension to strip when computing target path
_TEMPLATE_SUFFIX = ".tmpl"

# Convention prefixes in resource tree
_PROJECT_PREFIX = "project/"
_APP_PREFIX = "app/"


def _resource_anchor() -> str:
    """Return the importlib.resources anchor for builtin assets."""
    return "django_start.recipes.builtin"


@final
class BuiltinRecipeProvider:
    """Loads built-in recipe bundles from package resources.

    Uses ``importlib.resources`` to access recipe JSON and
    template assets, ensuring the provider works identically
    from a source checkout and an installed wheel.

    The provider resolves the orthogonal (profile, release) pair:
    - Framework baseline templates come from ``base/<django_x_y>/``
    - Profile templates come from ``<profile>/templates/``
    - Profile templates override baseline files at the same target path

    Template text content is read eagerly and returned as
    immutable ``RecipeBundle`` objects. No file handles or
    ``Traversable`` references leak across the provider boundary.
    """

    def get(
        self,
        profile: Profile,
        release: FrameworkRelease,
    ) -> RecipeBundle:
        """Load a recipe bundle for a profile and release.

        Args:
            profile: The architectural profile to load.
            release: The target framework release.

        Returns:
            Immutable ``RecipeBundle`` with metadata and
            template text content.

        Raises:
            ConfigurationError: If the recipe cannot be loaded,
                the baseline is missing, or assets are invalid.
        """
        metadata = self._load_metadata(profile)
        baseline_templates = self._load_baseline_templates(
            release
        )
        profile_templates = self._load_profile_templates(
            profile, metadata
        )

        # Merge: profile templates override baseline at same path
        merged = self._merge_templates(
            baseline_templates, profile_templates
        )

        return RecipeBundle(
            metadata=metadata,
            templates=merged,
        )

    def list_metadata(self) -> tuple[RecipeMetadata, ...]:
        """List metadata for all four built-in profiles.

        Returns:
            Tuple of ``RecipeMetadata`` in canonical profile order
            (standard, minimal, api, production).
        """
        return tuple(
            self._load_metadata(profile)
            for profile in Profile
        )

    # --- Internal Loading ---

    def _load_metadata(
        self, profile: Profile
    ) -> RecipeMetadata:
        """Load and parse recipe.json for a profile."""
        anchor = _resource_anchor()
        try:
            ref = importlib_resources.files(anchor).joinpath(
                profile.value, "recipe.json"
            )
            raw_json = ref.read_text(encoding="utf-8")
        except (
            FileNotFoundError,
            ModuleNotFoundError,
            TypeError,
        ) as exc:
            raise ConfigurationError(
                f"Cannot load recipe metadata for profile "
                f"'{profile.value}': {exc}"
            ) from exc

        return parse_recipe_metadata(raw_json)

    def _load_baseline_templates(
        self, release: FrameworkRelease
    ) -> tuple[RecipeTemplate, ...]:
        """Load framework baseline templates for a release."""
        baseline_dir = _SERIES_TO_BASELINE.get(release.series)
        if baseline_dir is None:
            raise ConfigurationError(
                f"No framework baseline templates for Django "
                f"{release.series}. Supported baselines: "
                f"{', '.join(sorted(_SERIES_TO_BASELINE.keys()))}"
            )

        anchor = _resource_anchor()
        try:
            base_ref = importlib_resources.files(
                anchor
            ).joinpath("base", baseline_dir)
        except (
            FileNotFoundError,
            ModuleNotFoundError,
            TypeError,
        ) as exc:
            raise ConfigurationError(
                f"Cannot access baseline templates for Django "
                f"{release.series}: {exc}"
            ) from exc

        return self._collect_templates(base_ref, "")

    def _load_profile_templates(
        self,
        profile: Profile,
        metadata: RecipeMetadata,
    ) -> tuple[RecipeTemplate, ...]:
        """Load profile-specific template overlays."""
        anchor = _resource_anchor()
        try:
            tmpl_ref = importlib_resources.files(
                anchor
            ).joinpath(
                profile.value,
                str(metadata.template_dir),
            )
        except (
            FileNotFoundError,
            ModuleNotFoundError,
            TypeError,
        ) as exc:
            raise ConfigurationError(
                f"Cannot access profile templates for "
                f"'{profile.value}': {exc}"
            ) from exc

        return self._collect_templates(tmpl_ref, "")

    def _collect_templates(
        self,
        root: object,
        prefix: str,
    ) -> tuple[RecipeTemplate, ...]:
        """Recursively collect .tmpl files from a resource tree.

        Maps resource paths to logical target paths:
        - ``project/`` prefix -> ``__DJSTART_PROJECT_NAME__/``
        - ``app/`` prefix -> ``__DJSTART_APP_NAME__/``
          (marked as app-scoped)
        - Other paths -> kept as-is
        """
        import importlib.resources.abc
        templates: list[RecipeTemplate] = []
        traversable: importlib.resources.abc.Traversable = root  # type: ignore[assignment]

        try:
            children = sorted(
                traversable.iterdir(),
                key=lambda c: c.name,
            )
        except (AttributeError, TypeError):
            return ()

        for child in children:
            child_name: str = child.name
            rel = f"{prefix}{child_name}"

            if child.is_dir():
                sub = self._collect_templates(
                    child, f"{rel}/"
                )
                templates.extend(sub)
            elif child_name.endswith(_TEMPLATE_SUFFIX):
                # Strip .tmpl suffix for target filename
                target_name = child_name[: -len(_TEMPLATE_SUFFIX)]
                target_rel = f"{prefix}{target_name}"

                # Map resource prefix to logical target path
                target_path, is_app_scoped = (
                    _map_resource_to_target(target_rel)
                )

                content: str = child.read_text(encoding="utf-8")
                templates.append(
                    RecipeTemplate(
                        relative_path=PurePosixPath(
                            target_path
                        ),
                        content=content,
                        is_app_scoped=is_app_scoped,
                    )
                )

        return tuple(templates)

    def _merge_templates(
        self,
        baseline: tuple[RecipeTemplate, ...],
        profile: tuple[RecipeTemplate, ...],
    ) -> tuple[RecipeTemplate, ...]:
        """Merge baseline and profile templates.

        Profile templates override baseline at the same target
        path (controlled overlay). This is not an error — it is
        the intended composition mechanism.
        """
        # Index baseline by path
        merged: dict[PurePosixPath, RecipeTemplate] = {}
        for tmpl in baseline:
            merged[tmpl.relative_path] = tmpl

        # Profile overlays replace baseline at same path
        for tmpl in profile:
            merged[tmpl.relative_path] = tmpl

        # Return sorted by path for determinism
        return tuple(
            merged[k]
            for k in sorted(merged.keys(), key=str)
        )


def _map_resource_to_target(
    resource_path: str,
) -> tuple[str, bool]:
    """Map a resource-relative path to a logical target path.

    Convention:
    - ``project/X`` -> ``__DJSTART_PROJECT_NAME__/X``
    - ``app/X`` -> ``__DJSTART_APP_NAME__/X`` (app-scoped)
    - Other -> kept as-is

    Returns:
        Tuple of (target_path, is_app_scoped).
    """
    if resource_path.startswith(_APP_PREFIX):
        suffix = resource_path[len(_APP_PREFIX):]
        return (
            f"__DJSTART_APP_NAME__/{suffix}",
            True,
        )
    if resource_path.startswith(_PROJECT_PREFIX):
        suffix = resource_path[len(_PROJECT_PREFIX):]
        return (
            f"__DJSTART_PROJECT_NAME__/{suffix}",
            False,
        )
    return (resource_path, False)
