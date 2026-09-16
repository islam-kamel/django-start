"""Snapshot / golden tests for Phase 5 recipe engine."""

from pathlib import Path

import pytest
from packaging.version import Version

from django_start.domain.config import AppConfig, Profile, ProjectConfig
from django_start.domain.policies import BUILTIN_REGISTRY
from django_start.domain.recipes import ScaffoldRequest
from django_start.infrastructure.builtin_recipes import BuiltinRecipeProvider
from django_start.recipes.engine import ControlledTemplateScaffoldEngine


def serialize_plan(plan) -> str:
    lines = []
    lines.append("PATHS:")
    for rf in plan.files:
        lines.append(f"  {rf.relative_path}")

    lines.append("\nREQUIREMENTS:")
    for req in plan.requirements:
        lines.append(f"  {req}")

    for rf in plan.files:
        p = str(rf.relative_path)
        if (
            "settings" in p
            or "urls.py" in p
            or "requirements.txt" in p
            or p
            in (
                "Dockerfile",
                "docker-compose.yml",
                "testproject/wsgi.py",
                "testproject/asgi.py",
                "manage.py",
            )
        ):
            lines.append(f"\n--- {p} ---")
            lines.append(rf.content.strip())

    return "\n".join(lines) + "\n"


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

    actual = serialize_plan(plan)

    golden_file = (
        Path(__file__).parent
        / "golden"
        / f"{profile.value}_django_{release.series.replace('.', '_')}.golden"
    )
    if not golden_file.exists():
        golden_file.write_text(actual)
        pytest.fail(f"Golden file missing, created: {golden_file.name}")

    expected = golden_file.read_text()
    assert actual == expected

    # Compile all Python files to verify syntax (no malformed tokens)
    for rf in plan.files:
        if rf.relative_path.name.endswith(".py"):
            try:
                compile(rf.content, str(rf.relative_path), "exec")
            except SyntaxError as e:
                pytest.fail(f"Syntax error in {rf.relative_path}: {e}")
