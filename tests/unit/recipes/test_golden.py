"""Snapshot / golden tests for Phase 5 recipe engine."""

from pathlib import Path

import pytest
from packaging.version import Version

from django_start.domain.config import AppConfig, Profile, ProjectConfig
from django_start.domain.policies import BUILTIN_REGISTRY
from django_start.domain.recipes import ScaffoldRequest
from django_start.infrastructure.builtin_recipes import BuiltinRecipeProvider
from django_start.recipes.engine import ControlledTemplateScaffoldEngine


@pytest.mark.parametrize(
    "profile",
    [Profile.STANDARD, Profile.MINIMAL, Profile.API, Profile.PRODUCTION],
)
@pytest.mark.parametrize(
    "release", BUILTIN_REGISTRY.releases, ids=lambda r: r.series
)
def test_golden_generation(profile, release):
    """Verify end-to-end generation for each profile x release combination."""
    provider = BuiltinRecipeProvider()
    engine = ControlledTemplateScaffoldEngine()

    bundle = provider.get(profile, release)

    config = ProjectConfig(
        name="testproject",
        target_dir=Path("/tmp/testproject"),
        profile=profile,
        framework_track=release.series,
        apps=[AppConfig(name="core"), AppConfig(name="api")],
    )

    request = ScaffoldRequest(
        config=config,
        release=release,
        recipe=bundle,
        host_python_version=Version("3.12.0"),
        django_start_version=Version("2.0.0a1"),
        secret_key="golden_secret_key_123",
    )

    plan = engine.render(request)

    # Verify core files exist in the plan
    file_paths = {str(f.relative_path) for f in plan.files}

    assert "requirements.txt" in file_paths
    assert "manage.py" in file_paths

    # Every profile has a project-level urls and wsgi
    assert "testproject/urls.py" in file_paths
    assert "testproject/wsgi.py" in file_paths
    assert "testproject/asgi.py" in file_paths

    # Standard and minimal have settings.py, production has a package
    if profile == Profile.PRODUCTION:
        assert "testproject/settings/__init__.py" in file_paths
        assert "testproject/settings/base.py" in file_paths
        assert "testproject/settings/production.py" in file_paths
    else:
        assert "testproject/settings.py" in file_paths

    # Core app files exist
    assert "core/apps.py" in file_paths
    assert "api/apps.py" in file_paths

    # Compile all Python files to verify syntax (no malformed tokens)
    for rf in plan.files:
        if rf.relative_path.name.endswith(".py"):
            try:
                compile(rf.content, str(rf.relative_path), "exec")
            except SyntaxError as e:
                pytest.fail(
                    f"Syntax error in {rf.relative_path}: {e}"
                )
