"""Tests for the ProjectLayout domain model."""

from pathlib import Path

from django_start.domain.config import AppConfig, Profile, ProjectConfig
from django_start.domain.layout import ProjectLayout


def test_project_layout_from_config() -> None:
    config = ProjectConfig(
        name="my_project",
        target_dir=Path("/workspace/my_project"),
        profile=Profile.STANDARD,
        framework_track="latest",
        apps=[AppConfig("core")],
    )

    layout = ProjectLayout.from_config(config)

    assert layout.project_root == Path("/workspace/my_project")
    assert layout.django_package_dir == Path(
        "/workspace/my_project/my_project"
    )
    assert layout.manage_py == Path("/workspace/my_project/manage.py")
