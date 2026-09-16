"""Tests for the BuiltinRecipeProvider."""

import pytest

from django_start.domain.config import Profile
from django_start.domain.policies import BUILTIN_REGISTRY
from django_start.domain.recipes import RecipeBundle
from django_start.infrastructure.builtin_recipes import BuiltinRecipeProvider


def test_list_metadata():
    provider = BuiltinRecipeProvider()
    metadata_list = provider.list_metadata()

    assert len(metadata_list) == 4
    names = {m.name for m in metadata_list}
    assert names == {"standard", "minimal", "api", "production"}


@pytest.mark.parametrize(
    "profile",
    [Profile.STANDARD, Profile.MINIMAL, Profile.API, Profile.PRODUCTION],
)
@pytest.mark.parametrize(
    "release", BUILTIN_REGISTRY.releases, ids=lambda r: r.series
)
def test_get_bundle(profile, release):
    provider = BuiltinRecipeProvider()
    bundle = provider.get(profile, release)

    assert isinstance(bundle, RecipeBundle)
    assert bundle.metadata.name == profile.value
    assert len(bundle.templates) > 0

    # Verify templates have content and correct paths
    for tmpl in bundle.templates:
        assert isinstance(tmpl.content, str)
        # empty content is ok for __init__.py
        # No .tmpl suffix
        assert not tmpl.relative_path.name.endswith(".tmpl")
