"""
Domain model for deterministic project layout paths.
"""

from dataclasses import dataclass
from pathlib import Path

from django_start.domain.config import ProjectConfig


@dataclass(frozen=True, slots=True)
class ProjectLayout:
    """
    Immutable representation of deterministic, stable paths in the generated project.

    Contains only safe, conceptual paths derived from project configuration.
    Does not read from the filesystem or include unresolved infrastructure paths.
    """

    project_root: Path
    django_package_dir: Path
    manage_py: Path

    @classmethod
    def from_config(cls, config: ProjectConfig) -> "ProjectLayout":
        """Derive the deterministic project layout from the project configuration."""
        root = config.target_dir
        package_dir = root / config.name
        manage_py = root / "manage.py"

        return cls(
            project_root=root,
            django_package_dir=package_dir,
            manage_py=manage_py,
        )
