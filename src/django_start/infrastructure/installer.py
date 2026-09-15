"""
Package installer adapter for Django-Start 2.0.
"""

from collections.abc import Sequence
from typing import final

from django_start.domain.errors import CommandError, DependencyInstallError
from django_start.ports.environment import EnvironmentDetails
from django_start.ports.installer import InstallResult, PackageInstaller
from django_start.ports.runner import Command, CommandRunner


@final
class PipPackageInstaller(PackageInstaller):
    """
    Installs packages using pip via a provided CommandRunner.
    """

    def __init__(self, runner: CommandRunner) -> None:
        self._runner = runner

    def install(
        self,
        env: EnvironmentDetails,
        requirements: Sequence[str],
        timeout: float | None = 180.0,
    ) -> InstallResult:
        if not requirements:
            return InstallResult([])

        for req in requirements:
            req_str = str(req).strip()
            if not req_str:
                raise DependencyInstallError("Empty requirement specified.")
            if req_str.startswith("-"):
                raise DependencyInstallError(
                    f"Option-like requirement rejected: {req_str}"
                )

        argv = [
            str(env.python_executable),
            "-m",
            "pip",
            "install",
            *requirements,
        ]

        command = Command(
            argv=argv,
            cwd=env.root_path,
            timeout=timeout,
        )

        try:
            self._runner.run(command)
        except CommandError as exc:
            raise DependencyInstallError(
                f"Failed to install packages: {exc}"
            ) from exc

        return InstallResult(requirements)
