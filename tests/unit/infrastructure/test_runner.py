import subprocess
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from django_start.domain.errors import (
    CommandExecutionError,
    CommandStartError,
    CommandTimeoutError,
)
from django_start.infrastructure.runner import SubprocessCommandRunner
from django_start.ports.runner import Command


@patch("subprocess.run")
def test_successful_execution(mock_run: MagicMock, tmp_path: Path) -> None:
    mock_run.return_value = subprocess.CompletedProcess(
        args=["mock"], returncode=0, stdout="hello world", stderr=""
    )
    runner = SubprocessCommandRunner()
    command = Command(
        argv=["dummy", "arg"],
        cwd=tmp_path,
    )
    result = runner.run(command)
    assert result.returncode == 0
    assert "hello world" in result.stdout
    assert result.stderr == ""

    mock_run.assert_called_once_with(
        command.argv,
        cwd=command.cwd,
        env=command.env,
        shell=False,
        capture_output=True,
        text=True,
        encoding="utf-8",
        timeout=command.timeout,
        check=False,
    )


@patch("subprocess.run")
def test_nonzero_exit(mock_run: MagicMock, tmp_path: Path) -> None:
    mock_run.return_value = subprocess.CompletedProcess(
        args=["mock"], returncode=42, stdout="", stderr="err"
    )
    runner = SubprocessCommandRunner()
    command = Command(
        argv=["dummy", "arg"],
        cwd=tmp_path,
    )
    with pytest.raises(CommandExecutionError) as exc_info:
        runner.run(command)
    assert exc_info.value.returncode == 42
    assert "err" in exc_info.value.stderr
    assert exc_info.value.argv == command.argv


@patch("subprocess.run")
def test_timeout(mock_run: MagicMock, tmp_path: Path) -> None:
    mock_run.side_effect = subprocess.TimeoutExpired(
        cmd=["mock"], timeout=0.1, output="partial", stderr="err_partial"
    )
    runner = SubprocessCommandRunner()
    command = Command(
        argv=["dummy"],
        cwd=tmp_path,
        timeout=0.1,
    )
    with pytest.raises(CommandTimeoutError) as exc_info:
        runner.run(command)
    assert exc_info.value.timeout == 0.1
    assert exc_info.value.stdout == "partial"
    assert exc_info.value.stderr == "err_partial"


@patch("subprocess.run")
def test_start_failure_os_error(mock_run: MagicMock, tmp_path: Path) -> None:
    mock_run.side_effect = OSError("Not found")
    runner = SubprocessCommandRunner()
    command = Command(
        argv=["/does/not/exist/executable", "--version"],
        cwd=tmp_path,
    )
    with pytest.raises(CommandStartError) as exc_info:
        runner.run(command)
    assert "Failed to start command" in str(exc_info.value)


@patch("subprocess.run")
def test_timeout_bytes_output(mock_run: MagicMock, tmp_path: Path) -> None:
    # Test that bytes output on timeout is correctly decoded
    mock_run.side_effect = subprocess.TimeoutExpired(
        cmd=["mock"], timeout=0.1, output=b"bytes_out", stderr=b"bytes_err"
    )
    runner = SubprocessCommandRunner()
    command = Command(
        argv=["dummy"],
        cwd=tmp_path,
        timeout=0.1,
    )
    with pytest.raises(CommandTimeoutError) as exc_info:
        runner.run(command)
    assert exc_info.value.stdout == "bytes_out"
    assert exc_info.value.stderr == "bytes_err"
