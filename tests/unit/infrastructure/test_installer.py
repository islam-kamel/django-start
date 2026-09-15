from pathlib import Path

import pytest

from django_start.domain.errors import (
    CommandExecutionError,
    DependencyInstallError,
)
from django_start.infrastructure.installer import PipPackageInstaller
from django_start.ports.environment import EnvironmentDetails
from django_start.ports.runner import Command, CommandResult, CommandRunner


class FakeRunner(CommandRunner):
    def __init__(self) -> None:
        self.calls: list[Command] = []
        self.fail_with: Exception | None = None

    def run(self, command: Command) -> CommandResult:
        self.calls.append(command)
        if self.fail_with:
            raise self.fail_with
        return CommandResult(returncode=0, stdout="success", stderr="")


def test_empty_requirements() -> None:
    runner = FakeRunner()
    installer = PipPackageInstaller(runner)
    env = EnvironmentDetails(
        root_path=Path("/fake/env"),
        python_executable=Path("/fake/env/bin/python"),
        scripts_path=Path("/fake/env/bin"),
    )

    result = installer.install(env, [])

    assert result.installed_packages == ()
    assert not runner.calls


def test_reject_dangerous_flags() -> None:
    runner = FakeRunner()
    installer = PipPackageInstaller(runner)
    env = EnvironmentDetails(
        root_path=Path("/fake/env"),
        python_executable=Path("/fake/env/bin/python"),
        scripts_path=Path("/fake/env/bin"),
    )

    with pytest.raises(DependencyInstallError, match="Option-like"):
        installer.install(env, ["-e", "."])

    with pytest.raises(DependencyInstallError, match="Option-like"):
        installer.install(env, ["--index-url", "https://evil.com"])


def test_reject_empty_requirement() -> None:
    runner = FakeRunner()
    installer = PipPackageInstaller(runner)
    env = EnvironmentDetails(
        root_path=Path("/fake/env"),
        python_executable=Path("/fake/env/bin/python"),
        scripts_path=Path("/fake/env/bin"),
    )

    with pytest.raises(DependencyInstallError, match="Empty requirement"):
        installer.install(env, ["django", "  "])


def test_command_construction() -> None:
    runner = FakeRunner()
    installer = PipPackageInstaller(runner)
    env = EnvironmentDetails(
        root_path=Path("/fake/env dir"),
        python_executable=Path("/fake/env dir/bin/python"),
        scripts_path=Path("/fake/env dir/bin"),
    )

    result = installer.install(env, ["django==4.2", "psycopg2"])

    assert result.installed_packages == ("django==4.2", "psycopg2")
    assert len(runner.calls) == 1

    cmd = runner.calls[0]
    assert cmd.cwd == env.root_path
    assert cmd.argv == (
        str(env.python_executable),
        "-m",
        "pip",
        "install",
        "django==4.2",
        "psycopg2",
    )


def test_command_failure_translation() -> None:
    runner = FakeRunner()
    installer = PipPackageInstaller(runner)
    env = EnvironmentDetails(
        root_path=Path("/fake/env"),
        python_executable=Path("/fake/env/bin/python"),
        scripts_path=Path("/fake/env/bin"),
    )

    runner.fail_with = CommandExecutionError(
        "failed", argv=["pip"], returncode=1, stdout="", stderr="error"
    )

    with pytest.raises(DependencyInstallError) as exc_info:
        installer.install(env, ["django"])

    assert exc_info.value.__cause__ is runner.fail_with
