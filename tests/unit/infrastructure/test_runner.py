import sys
from pathlib import Path

import pytest

from django_start.domain.errors import (
    CommandExecutionError,
    CommandStartError,
    CommandTimeoutError,
)
from django_start.infrastructure.runner import SubprocessCommandRunner
from django_start.ports.runner import Command


def test_successful_execution(tmp_path: Path) -> None:
    runner = SubprocessCommandRunner()
    command = Command(
        argv=[sys.executable, "-c", "print('hello world')"],
        cwd=tmp_path,
    )
    result = runner.run(command)
    assert result.returncode == 0
    assert "hello world" in result.stdout
    assert result.stderr == ""


def test_nonzero_exit(tmp_path: Path) -> None:
    runner = SubprocessCommandRunner()
    command = Command(
        argv=[
            sys.executable,
            "-c",
            "import sys; print('err', file=sys.stderr); sys.exit(42)",
        ],
        cwd=tmp_path,
    )
    with pytest.raises(CommandExecutionError) as exc_info:
        runner.run(command)
    assert exc_info.value.returncode == 42
    assert "err" in exc_info.value.stderr
    assert exc_info.value.argv == command.argv


def test_timeout(tmp_path: Path) -> None:
    runner = SubprocessCommandRunner()
    command = Command(
        argv=[
            sys.executable,
            "-c",
            "import time; print('started'); time.sleep(10)",
        ],
        cwd=tmp_path,
        timeout=0.1,
    )
    with pytest.raises(CommandTimeoutError) as exc_info:
        runner.run(command)
    assert exc_info.value.timeout == 0.1
    # stdout might be captured partially depending on buffer,
    # but shouldn't fail.
    assert isinstance(exc_info.value.stdout, str)


def test_start_failure_missing_executable(tmp_path: Path) -> None:
    runner = SubprocessCommandRunner()
    command = Command(
        argv=["/does/not/exist/executable", "--version"],
        cwd=tmp_path,
    )
    with pytest.raises(CommandStartError):
        runner.run(command)


def test_start_failure_invalid_cwd(tmp_path: Path) -> None:
    runner = SubprocessCommandRunner()
    command = Command(
        argv=[sys.executable, "-c", "pass"],
        cwd=tmp_path / "nonexistent",
    )
    with pytest.raises(CommandStartError):
        runner.run(command)


def test_cwd_with_spaces(tmp_path: Path) -> None:
    space_dir = tmp_path / "my dir with spaces"
    space_dir.mkdir()
    runner = SubprocessCommandRunner()
    command = Command(
        argv=[sys.executable, "-c", "import os; print(os.getcwd())"],
        cwd=space_dir,
    )
    result = runner.run(command)
    assert result.returncode == 0
    assert "my dir with spaces" in result.stdout


def test_literal_shell_metacharacters(tmp_path: Path) -> None:
    runner = SubprocessCommandRunner()
    # Test that shell metacharacters are passed literally to the python script
    # and not executed as shell commands.
    command = Command(
        argv=[
            sys.executable,
            "-c",
            "import sys; print(sys.argv[1])",
            "&& echo hacked > hacked.txt",
        ],
        cwd=tmp_path,
    )
    result = runner.run(command)
    assert result.returncode == 0
    assert "&& echo hacked > hacked.txt" in result.stdout
    assert not (tmp_path / "hacked.txt").exists()


def test_custom_environment(tmp_path: Path) -> None:
    runner = SubprocessCommandRunner()
    command = Command(
        argv=[
            sys.executable,
            "-c",
            "import os; print(os.environ.get('MY_CUSTOM_VAR', 'none'))",
        ],
        cwd=tmp_path,
        env={"MY_CUSTOM_VAR": "custom_value"},
    )
    result = runner.run(command)
    assert result.returncode == 0
    assert "custom_value" in result.stdout


def test_unicode_output(tmp_path: Path) -> None:
    runner = SubprocessCommandRunner()
    command = Command(
        argv=[sys.executable, "-c", "print('こんにちは')"],
        cwd=tmp_path,
    )
    result = runner.run(command)
    assert result.returncode == 0
    assert "こんにちは" in result.stdout


def test_empty_argv(tmp_path: Path) -> None:
    runner = SubprocessCommandRunner()
    command = Command(
        argv=["", "--version"],
        cwd=tmp_path,
    )
    with pytest.raises(CommandStartError, match="must not be empty"):
        runner.run(command)

    # Note: Command dataclass takes care of tuple initialization,
    # but if we pass empty:
    with pytest.raises(CommandStartError, match="at least one element"):
        cmd = Command(argv=[], cwd=tmp_path)
        runner.run(cmd)
