"""
Package installer port for Django-Start 2.0.

Provides an isolated boundary for installing dependencies into environments.
"""
from collections.abc import Sequence
from dataclasses import dataclass
from typing import Protocol

from django_start.ports.environment import EnvironmentDetails


@dataclass(frozen=True, slots=True)
class InstallResult:
    """
    Immutable representation of a successful package installation result.
    
    Failures are propagated via DependencyInstallError, not via this class.
    """
    installed_packages: tuple[str, ...]

    def __init__(self, installed_packages: Sequence[str]) -> None:
        object.__setattr__(self, "installed_packages", tuple(installed_packages))


class PackageInstaller(Protocol):
    """
    Port protocol for installing packages.
    
    Implementations must raise DependencyInstallError on failure.
    """

    def install(
        self,
        env: EnvironmentDetails,
        requirements: Sequence[str],
        timeout: float | None = 180.0,
    ) -> InstallResult:
        """Install package specifications into the designated environment."""
        ...
