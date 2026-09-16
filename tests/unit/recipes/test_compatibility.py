"""Tests for pure compatibility validation."""

from pathlib import PurePosixPath

import pytest
from packaging.specifiers import SpecifierSet
from packaging.version import Version

from django_start.domain.errors import (
    ConfigurationError,
    UnsupportedVersionError,
)
from django_start.domain.policies import FrameworkRelease
from django_start.domain.recipes import RecipeMetadata
from django_start.recipes.compatibility import validate_recipe_compatibility


@pytest.fixture
def metadata():
    return RecipeMetadata(
        recipe_schema_version="1.0",
        recipe_version=Version("2.0.0"),
        name="test",
        description="Test",
        python_requires=SpecifierSet(">=3.12,<3.15"),
        django_requires=SpecifierSet(">=5.2,<6.2"),
        django_start_requires=SpecifierSet(">=2.0.0a1,<3"),
        dependencies=(),
        template_dir=PurePosixPath("templates"),
    )


@pytest.fixture
def release():
    return FrameworkRelease(
        series="6.1",
        tested_version=Version("6.1.1"),
        django_requires=SpecifierSet(">=6.1.1,<6.2"),
        python_requires=SpecifierSet(">=3.12"),
        is_lts=False,
    )


def test_compatible(metadata, release):
    validate_recipe_compatibility(
        metadata,
        Version("3.12.0"),
        release,
        Version("2.0.0a1"),
    )


def test_incompatible_schema(metadata, release):
    bad_metadata = RecipeMetadata(
        recipe_schema_version="1.1",
        recipe_version=Version("2.0.0"),
        name="test",
        description="Test",
        python_requires=SpecifierSet(">=3.12,<3.15"),
        django_requires=SpecifierSet(">=5.2,<6.2"),
        django_start_requires=SpecifierSet(">=2.0.0a1,<3"),
        dependencies=(),
        template_dir=PurePosixPath("templates"),
    )
    with pytest.raises(
        ConfigurationError, match="Unsupported recipe schema version"
    ):
        validate_recipe_compatibility(
            bad_metadata,
            Version("3.12.0"),
            release,
            Version("2.0.0a1"),
        )


def test_incompatible_python(metadata, release):
    with pytest.raises(
        UnsupportedVersionError, match="Host Python 3.11.0 is not compatible"
    ):
        validate_recipe_compatibility(
            metadata,
            Version("3.11.0"),
            release,
            Version("2.0.0a1"),
        )


def test_incompatible_django(metadata):
    bad_release = FrameworkRelease(
        series="5.0",
        tested_version=Version("5.0.1"),
        django_requires=SpecifierSet(">=5.0.1,<5.1"),
        python_requires=SpecifierSet(">=3.10"),
        is_lts=False,
    )
    with pytest.raises(
        UnsupportedVersionError, match="Django 5.0.1 .* is not compatible"
    ):
        validate_recipe_compatibility(
            metadata,
            Version("3.12.0"),
            bad_release,
            Version("2.0.0a1"),
        )


def test_incompatible_django_start(metadata, release):
    with pytest.raises(
        UnsupportedVersionError, match="Django-Start 1.1.6 is not compatible"
    ):
        validate_recipe_compatibility(
            metadata,
            Version("3.12.0"),
            release,
            Version("1.1.6"),
        )
