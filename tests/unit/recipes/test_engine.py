"""Tests for the controlled template scaffold engine."""

from pathlib import Path, PurePosixPath

import pytest
from packaging.specifiers import SpecifierSet
from packaging.version import Version

from django_start.domain.config import AppConfig, Profile, ProjectConfig
from django_start.domain.errors import ConfigurationError
from django_start.domain.policies import FrameworkRelease
from django_start.domain.recipes import (
    RecipeBundle,
    RecipeMetadata,
    RecipeTemplate,
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
        apps=[AppConfig(name="core"), AppConfig(name="api")],
    )
    return ScaffoldRequest(
        config=config,
        release=release,
        recipe=RecipeBundle(metadata=metadata, templates=()),
        host_python_version=Version("3.12.0"),
        django_start_version=Version("2.0.0a1"),
        secret_key="secret123",
    )


def test_token_replacement(base_request):
    templates = (
        RecipeTemplate(
            relative_path=PurePosixPath(
                "__DJSTART_PROJECT_NAME__/settings.py"
            ),
            content="SECRET = __DJSTART_SECRET_KEY_PY__\n# __DJSTART_DJANGO_VERSION_COMMENT__",
            is_app_scoped=False,
        ),
        RecipeTemplate(
            relative_path=PurePosixPath("__DJSTART_APP_NAME__/apps.py"),
            content="class __DJSTART_APP_CONFIG_CLASS__:\n    name = '__DJSTART_APP_NAME__'",
            is_app_scoped=True,
        ),
    )
    import dataclasses
    request = dataclasses.replace(base_request, 
        recipe= RecipeBundle(
                metadata=base_request.recipe.metadata, templates=templates
            ),
    )

    engine = ControlledTemplateScaffoldEngine()
    plan = engine.render(request)

    # 4 files total
    assert len(plan.files) == 4

    # Check settings
    settings = next(
        f for f in plan.files if f.relative_path.name == "settings.py"
    )
    assert settings.relative_path == PurePosixPath("myproject/settings.py")
    assert "SECRET = 'secret123'" in settings.content
    assert "# Django 6.1" in settings.content

    # Check core app
    core_apps = next(
        f
        for f in plan.files
        if f.relative_path.name == "apps.py" and "core" in str(f.relative_path)
    )
    assert core_apps.relative_path == PurePosixPath("core/apps.py")
    assert "class CoreConfig:" in core_apps.content
    assert "name = 'core'" in core_apps.content

    # Check api app
    api_apps = next(
        f
        for f in plan.files
        if f.relative_path.name == "apps.py" and "api" in str(f.relative_path)
    )
    assert api_apps.relative_path == PurePosixPath("api/apps.py")
    assert "class ApiConfig:" in api_apps.content
    assert "name = 'api'" in api_apps.content


def test_django_tags_preserved(base_request):
    templates = (
        RecipeTemplate(
            relative_path=PurePosixPath("index.html"),
            content="{% extends 'base.html' %}\n{{ foo }}",
            is_app_scoped=False,
        ),
    )
    import dataclasses
    request = dataclasses.replace(base_request, 
        recipe= RecipeBundle(
                metadata=base_request.recipe.metadata, templates=templates
            ),
    )
    engine = ControlledTemplateScaffoldEngine()
    plan = engine.render(request)

    index = next(f for f in plan.files if f.relative_path.name == "index.html")
    assert "{% extends 'base.html' %}" in index.content
    assert "{{ foo }}" in index.content


def test_unknown_token_raises(base_request):
    templates = (
        RecipeTemplate(
            relative_path=PurePosixPath("test.py"),
            content="__DJSTART_UNKNOWN_TOKEN__",
            is_app_scoped=False,
        ),
    )
    import dataclasses
    request = dataclasses.replace(base_request, 
        recipe= RecipeBundle(
                metadata=base_request.recipe.metadata, templates=templates
            ),
    )
    engine = ControlledTemplateScaffoldEngine()
    with pytest.raises(ConfigurationError, match="Unknown template token"):
        engine.render(request)


def test_unresolved_tokens_raises(base_request, monkeypatch):
    # Manually insert something that looks like a token but wasn't replaced
    templates = (
        RecipeTemplate(
            relative_path=PurePosixPath("test.py"),
            content="__DJSTART_PROJECT_NAME__",  # Valid token
            is_app_scoped=False,
        ),
    )
    import dataclasses
    request = dataclasses.replace(base_request, 
        recipe= RecipeBundle(
                metadata=base_request.recipe.metadata, templates=templates
            ),
    )

    engine = ControlledTemplateScaffoldEngine()
    
    # Override context building to simulate a missing replacement
    def bad_substitute(self, text, context, source_desc):
        return text
        
    monkeypatch.setattr(ControlledTemplateScaffoldEngine, "_substitute_tokens", bad_substitute)

    with pytest.raises(
        ConfigurationError, match="Unresolved template tokens"
    ):
        engine.render(request)


def test_duplicate_path_raises(base_request):
    templates = (
        RecipeTemplate(
            relative_path=PurePosixPath("test.py"),
            content="",
            is_app_scoped=False,
        ),
        RecipeTemplate(
            relative_path=PurePosixPath("test.py"),
            content="",
            is_app_scoped=False,
        ),
    )
    import dataclasses
    request = dataclasses.replace(base_request, 
        recipe= RecipeBundle(
                metadata=base_request.recipe.metadata, templates=templates
            ),
    )
    engine = ControlledTemplateScaffoldEngine()
    with pytest.raises(
        ConfigurationError, match="Duplicate rendered file path"
    ):
        engine.render(request)


def test_engine_owned_path_collision_raises(base_request):
    templates = (
        RecipeTemplate(
            relative_path=PurePosixPath("requirements.txt"),
            content="foo",
            is_app_scoped=False,
        ),
    )
    import dataclasses
    request = dataclasses.replace(base_request, 
        recipe= RecipeBundle(
                metadata=base_request.recipe.metadata, templates=templates
            ),
    )
    engine = ControlledTemplateScaffoldEngine()
    with pytest.raises(
        ConfigurationError, match="Duplicate rendered file path"
    ):
        engine.render(request)


def test_unsafe_path_components(base_request):
    templates = (
        RecipeTemplate(
            relative_path=PurePosixPath(".git/config"),
            content="foo",
            is_app_scoped=False,
        ),
    )
    import dataclasses
    request = dataclasses.replace(base_request, 
        recipe= RecipeBundle(
                metadata=base_request.recipe.metadata, templates=templates
            ),
    )
    engine = ControlledTemplateScaffoldEngine()
    with pytest.raises(ConfigurationError, match="unsafe component"):
        engine.render(request)


def test_path_traversal(base_request):
    templates = (
        RecipeTemplate(
            relative_path=PurePosixPath("../foo.py"),
            content="foo",
            is_app_scoped=False,
        ),
    )
    import dataclasses
    request = dataclasses.replace(base_request, 
        recipe= RecipeBundle(
                metadata=base_request.recipe.metadata, templates=templates
            ),
    )
    engine = ControlledTemplateScaffoldEngine()
    with pytest.raises(ConfigurationError, match="unsafe component"):
        engine.render(request)
