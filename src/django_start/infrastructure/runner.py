"""
Subprocess-based command runner for Django-Start 2.0.
"""

import subprocess
from typing import final

from django_start.domain.errors import (
    CommandExecutionError,
    CommandStartError,
    CommandTimeoutError,
)
from django_start.ports.runner import Command, CommandResult, CommandRunner


@final
class SubprocessCommandRunner(CommandRunner):
    """
    Executes commands securely using subprocess.run with shell=False.
    """

    def run(self, command: Command) -> CommandResult:
        if not command.argv:
            raise CommandStartError(
                "Command argv must contain at least one element.",
                argv=command.argv,
            )
        if not command.argv[0]:
            raise CommandStartError(
                "Command executable (argv[0]) must not be empty.",
                argv=command.argv,
            )

        try:
            result = subprocess.run(
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
        except subprocess.TimeoutExpired as exc:
            stdout = (
                exc.stdout
                if isinstance(exc.stdout, str)
                else (
                    exc.stdout.decode("utf-8", errors="replace")
                    if exc.stdout
                    else ""
                )
            )
            stderr = (
                exc.stderr
                if isinstance(exc.stderr, str)
                else (
                    exc.stderr.decode("utf-8", errors="replace")
                    if exc.stderr
                    else ""
                )
            )
            raise CommandTimeoutError(
                f"Command timed out after {command.timeout} seconds.",
                argv=command.argv,
                timeout=command.timeout or 0.0,
                stdout=stdout,
                stderr=stderr,
            ) from exc
        except OSError as exc:
            raise CommandStartError(
                f"Failed to start command: {exc}",
                argv=command.argv,
            ) from exc

        if result.returncode != 0:
            raise CommandExecutionError(
                f"Command exited with status {result.returncode}.",
                argv=command.argv,
                returncode=result.returncode,
                stdout=result.stdout,
                stderr=result.stderr,
            )

        return CommandResult(
            returncode=result.returncode,
            stdout=result.stdout,
            stderr=result.stderr,
        )
