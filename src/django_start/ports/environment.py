"""
Environment management port for Django-Start 2.0.

Provides an isolated boundary for virtual environment lifecycle operations.
"""

from dataclasses import dataclass
from pathlib import Path
from typing import Protocol


@dataclass(frozen=True, slots=True)
class EnvironmentDetails:
    """Immutable representation of a Python environment's paths."""

    root_path: Path
    python_executable: Path
    scripts_path: Path


class EnvironmentManager(Protocol):
    """
    Port protocol for managing virtual environments.

    Implementations should raise EnvironmentCreationError on failure.
    """

    def create(self, target_dir: Path) -> EnvironmentDetails:
        """Create an isolated virtual environment at the target directory."""
        ...

    def exists(self, target_dir: Path) -> bool:
        """Check if an environment exists at the target directory."""
        ...
