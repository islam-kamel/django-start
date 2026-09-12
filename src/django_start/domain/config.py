"""
Domain configuration models for Django-Start 2.0.

Immutable, validated representations of user intent.
"""

from collections.abc import Sequence
from dataclasses import dataclass
from enum import Enum
from pathlib import Path

from django_start.domain.errors import ConfigurationError
from django_start.domain.policies import validate_identifier


class Profile(str, Enum):
    """Architectural project profiles."""

    STANDARD = "standard"
    MINIMAL = "minimal"
    API = "api"
    PRODUCTION = "production"

    def __str__(self) -> str:
        return self.value


@dataclass(frozen=True, slots=True)
class AppConfig:
    """Immutable representation of a Django application to be generated."""

    name: str

    def __post_init__(self) -> None:
        validate_identifier(self.name, "Application name")


@dataclass(frozen=True, slots=True)
class ProjectConfig:
    """Immutable representation of project generation intent."""

    name: str
    target_dir: Path
    profile: Profile
    framework_track: str  # e.g., 'latest', 'lts', '6.1'
    apps: tuple[AppConfig, ...]

    def __init__(
        self,
        name: str,
        target_dir: Path,
        profile: Profile,
        framework_track: str,
        apps: Sequence[AppConfig],
    ) -> None:
        validate_identifier(name, "Project name")
        object.__setattr__(self, "name", name)
        object.__setattr__(self, "target_dir", target_dir)
        object.__setattr__(self, "profile", profile)
        object.__setattr__(self, "framework_track", framework_track)

        # Ensure apps collection is an immutable tuple
        apps_tuple = tuple(apps)

        # Check for duplicate app names
        app_names = set()
        for app in apps_tuple:
            if app.name in app_names:
                raise ConfigurationError(
                    f"Duplicate application name requested: '{app.name}'"
                )
            app_names.add(app.name)

        object.__setattr__(self, "apps", apps_tuple)
