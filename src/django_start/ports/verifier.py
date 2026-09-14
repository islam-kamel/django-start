"""
Project verification port for Django-Start 2.0.

Provides an isolated boundary for checking the validity of generated projects.
"""

from pathlib import Path
from typing import Protocol

from django_start.ports.environment import EnvironmentDetails


class ProjectVerifier(Protocol):
    """
    Port protocol for verifying generated projects.

    Implementations must raise VerificationError if the project is invalid.
    """

    def verify(self, env: EnvironmentDetails, project_dir: Path) -> None:
        """Verify the generated project (e.g., via manage.py check)."""
        ...
