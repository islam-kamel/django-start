"""
Tests to prove the structural compatibility of port definitions.

These tests use minimal fake implementations merely to prove that the Protocol
definitions and their typed interfaces are usable, instantiable, and satisfy type checkers.
"""
from collections.abc import Sequence
from pathlib import Path

import pytest

from django_start.domain.errors import (
    CommandExecutionError,
    DependencyInstallError,
    EnvironmentCreationError,
    VerificationError,
)
from django_start.ports.environment import (
    EnvironmentDetails,
    EnvironmentManager,
)
from django_start.ports.filesystem import FileSystem
from django_start.ports.installer import InstallResult, PackageInstaller
from django_start.ports.runner import Command, CommandResult, CommandRunner
from django_start.ports.verifier import ProjectVerifier

# -- FAKES --

class FakeCommandRunner(CommandRunner):
    def run(self, command: Command) -> CommandResult:
        if "fail" in command.argv:
            raise CommandExecutionError(
                message="Command failed",
                returncode=1,
                stdout="",
                stderr="error",
            )
        return CommandResult(returncode=0, stdout="success", stderr="")


class FakeFileSystem(FileSystem):
    def exists(self, path: Path) -> bool:
        return str(path) == "/exists"

    def is_empty_dir(self, path: Path) -> bool:
        return str(path) == "/empty"

    def read_text(self, path: Path) -> str:
        return "content"

    def write_text_atomic(self, path: Path, content: str) -> None:
        pass

    def create_directory(self, path: Path) -> None:
        pass

    def remove_tree(self, path: Path) -> None:
        pass


class FakeEnvironmentManager(EnvironmentManager):
    def create(self, target_dir: Path) -> EnvironmentDetails:
        if str(target_dir) == "/fail":
            raise EnvironmentCreationError("Failed to create env")
        return EnvironmentDetails(
            root_path=target_dir,
            python_executable=target_dir / "bin" / "python",
            scripts_path=target_dir / "bin",
        )

    def exists(self, target_dir: Path) -> bool:
        return str(target_dir) == "/exists"


class FakePackageInstaller(PackageInstaller):
    def install(
        self,
        env: EnvironmentDetails,
        requirements: Sequence[str],
        timeout: float | None = 180.0,
    ) -> InstallResult:
        if "fail" in requirements:
            raise DependencyInstallError("Failed to install")
        return InstallResult(installed_packages=requirements)


class FakeProjectVerifier(ProjectVerifier):
    def verify(self, env: EnvironmentDetails, project_dir: Path) -> None:
        if str(project_dir) == "/fail":
            raise VerificationError("Project verification failed")


# -- TESTS --

def test_command_dataclass_immutability_and_env_protection() -> None:
    original_env = {"A": "1"}
    cmd = Command(
        argv=["ls"],
        cwd=Path("/tmp"),
        env=original_env,
    )

    assert isinstance(cmd.argv, tuple)

    # Mutating original should not mutate cmd
    original_env["A"] = "2"
    assert cmd.env is not None
    assert cmd.env["A"] == "1"

    with pytest.raises(ValueError, match="Timeout must be positive"):
        Command(argv=["ls"], cwd=Path("/tmp"), timeout=-1.0)


def test_command_runner_contract() -> None:
    runner = FakeCommandRunner()

    # Success
    cmd = Command(argv=["ls"], cwd=Path("/tmp"))
    result = runner.run(cmd)
    assert result.returncode == 0
    assert result.stdout == "success"

    # Failure
    cmd_fail = Command(argv=["fail"], cwd=Path("/tmp"))
    with pytest.raises(CommandExecutionError, match="Command failed"):
        runner.run(cmd_fail)


def test_filesystem_contract() -> None:
    fs = FakeFileSystem()
    assert fs.exists(Path("/exists")) is True
    assert fs.exists(Path("/missing")) is False
    assert fs.is_empty_dir(Path("/empty")) is True
    assert fs.read_text(Path("/any")) == "content"


def test_environment_manager_contract() -> None:
    manager = FakeEnvironmentManager()

    env = manager.create(Path("/tmp/env"))
    assert env.root_path == Path("/tmp/env")
    assert env.python_executable == Path("/tmp/env/bin/python")

    with pytest.raises(EnvironmentCreationError, match="Failed to create env"):
        manager.create(Path("/fail"))

    assert manager.exists(Path("/exists")) is True


def test_package_installer_contract() -> None:
    installer = FakePackageInstaller()
    env = EnvironmentDetails(
        root_path=Path("/tmp/env"),
        python_executable=Path("/tmp/env/bin/python"),
        scripts_path=Path("/tmp/env/bin"),
    )

    result = installer.install(env, ["django==6.1.1"])
    assert result.installed_packages == ("django==6.1.1",)

    with pytest.raises(DependencyInstallError, match="Failed to install"):
        installer.install(env, ["fail"])


def test_project_verifier_contract() -> None:
    verifier = FakeProjectVerifier()
    env = EnvironmentDetails(
        root_path=Path("/tmp/env"),
        python_executable=Path("/tmp/env/bin/python"),
        scripts_path=Path("/tmp/env/bin"),
    )

    # Success returns None
    verifier.verify(env, Path("/ok"))

    with pytest.raises(VerificationError, match="Project verification failed"):
        verifier.verify(env, Path("/fail"))
