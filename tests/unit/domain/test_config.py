"""Tests for the domain configuration models."""

from pathlib import Path

import pytest

from django_start.domain.config import AppConfig, Profile, ProjectConfig
from django_start.domain.errors import (
    ConfigurationError,
    InvalidIdentifierError,
)


def test_app_config_valid() -> None:
    app = AppConfig("core")
    assert app.name == "core"


def test_app_config_invalid() -> None:
    with pytest.raises(
        InvalidIdentifierError,
        match="Application name 'my-app' is not a valid Python identifier.",
    ):
        AppConfig("my-app")


def test_project_config_valid() -> None:
    config = ProjectConfig(
        name="my_project",
        target_dir=Path("/tmp/my_project"),
        profile=Profile.STANDARD,
        framework_track="latest",
        apps=[AppConfig("core"), AppConfig("api")],
    )

    assert config.name == "my_project"
    assert config.target_dir == Path("/tmp/my_project")
    assert config.profile == Profile.STANDARD
    assert config.framework_track == "latest"

    # Ensure apps is stored as an immutable tuple
    assert isinstance(config.apps, tuple)
    assert len(config.apps) == 2
    assert config.apps[0].name == "core"
    assert config.apps[1].name == "api"


def test_project_config_invalid_name() -> None:
    with pytest.raises(
        InvalidIdentifierError,
        match="Project name 'my-project' is not a valid Python identifier.",
    ):
        ProjectConfig(
            name="my-project",
            target_dir=Path("/tmp/my-project"),
            profile=Profile.STANDARD,
            framework_track="latest",
            apps=[],
        )


def test_project_config_duplicate_apps() -> None:
    with pytest.raises(
        ConfigurationError,
        match="Duplicate application name requested: 'core'",
    ):
        ProjectConfig(
            name="my_project",
            target_dir=Path("/tmp/my_project"),
            profile=Profile.STANDARD,
            framework_track="latest",
            apps=[AppConfig("core"), AppConfig("api"), AppConfig("core")],
        )


def test_profile_str() -> None:
    assert str(Profile.STANDARD) == "standard"
    assert str(Profile.MINIMAL) == "minimal"
