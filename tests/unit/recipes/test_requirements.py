"""Tests for requirements manifest generation."""

from pathlib import Path, PurePosixPath

import pytest
from packaging.specifiers import SpecifierSet
from packaging.version import Version

from django_start.domain.config import AppConfig, Profile, ProjectConfig
from django_start.domain.policies import FrameworkRelease
from django_start.domain.recipes import (
    RecipeBundle,
    RecipeMetadata,
    ScaffoldRequest,
)
from django_start.recipes.engine import ControlledTemplateScaffoldEngine


@pytest.fixture
def base_request():
    metadata = RecipeMetadata(
        recipe_schema_version="1.0",
        recipe_version=Version("2.0.0"),
        name="test",
        description="Test",
        python_requires=SpecifierSet(">=3.12,<3.15"),
        django_requires=SpecifierSet(">=5.2,<6.2"),
        django_start_requires=SpecifierSet(">=2.0.0a1,<3"),
        dependencies=("requests>=2.0,<3",),
        template_dir=PurePosixPath("templates"),
    )
    release = FrameworkRelease(
        series="6.1",
        tested_version=Version("6.1.1"),
        django_requires=SpecifierSet(">=6.1.1,<6.2"),
        python_requires=SpecifierSet(">=3.12"),
        is_lts=False,
    )
    config = ProjectConfig(
        name="myproject",
        target_dir=Path("/tmp/myproject"),
        profile=Profile.STANDARD,
        framework_track="6.1",
        apps=[AppConfig(name="core")],
    )
    return ScaffoldRequest(
        config=config,
        release=release,
        recipe=RecipeBundle(metadata=metadata, templates=()),
        host_python_version=Version("3.12.0"),
        django_start_version=Version("2.0.0a1"),
        secret_key="secret123",
    )


def test_django_requirement_is_first(base_request):
    engine = ControlledTemplateScaffoldEngine()
    plan = engine.render(base_request)

    assert plan.requirements[0] == "Django<6.2,>=6.1.1"
    assert plan.requirements[1] == "requests>=2.0,<3"


def test_requirements_txt_rendered_file(base_request):
    engine = ControlledTemplateScaffoldEngine()
    plan = engine.render(base_request)

    req_file = next(
        f for f in plan.files if f.relative_path.name == "requirements.txt"
    )

    assert req_file.content == "Django<6.2,>=6.1.1\nrequests>=2.0,<3\n"
