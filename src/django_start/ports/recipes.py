"""Recipe provider port for Django-Start 2.0.

Defines the protocol for loading recipe metadata and template
bundles. The provider owns resource access; consumers receive
immutable data.
"""

from typing import Protocol

from django_start.domain.config import Profile
from django_start.domain.policies import FrameworkRelease
from django_start.domain.recipes import RecipeBundle, RecipeMetadata


class RecipeProvider(Protocol):
    """Protocol for loading recipe bundles.

    Implementations load recipe metadata and template assets
    from package resources, local directories, or other sources.

    The provider resolves the orthogonal (profile, release) pair
    into a complete ``RecipeBundle`` containing parsed metadata
    and all template content as immutable text.
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
            ConfigurationError: If the recipe cannot be loaded
                or is invalid.
        """
        ...

    def list_metadata(self) -> tuple[RecipeMetadata, ...]:
        """List metadata for all available recipes.

        Returns:
            Tuple of ``RecipeMetadata`` for each available
            recipe, in deterministic order.
        """
        ...
