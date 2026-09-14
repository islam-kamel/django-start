"""
Command execution port for Django-Start 2.0.

Provides an isolated boundary for safely executing subprocesses without shell injection.
"""

from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from pathlib import Path
from typing import Protocol


@dataclass(frozen=True, slots=True)
class Command:
    """
    Immutable representation of an external command to execute.

    String interpolation and shell execution are strictly forbidden by architecture.
    """

    argv: tuple[str, ...]
    cwd: Path
    env: Mapping[str, str] | None
    timeout: float | None

    def __init__(
        self,
        argv: Sequence[str],
        cwd: Path,
        env: Mapping[str, str] | None = None,
        timeout: float | None = 120.0,
    ) -> None:
        object.__setattr__(self, "argv", tuple(argv))
        object.__setattr__(self, "cwd", cwd)

        # Defensively copy the environment dictionary to prevent caller mutations
        safe_env = dict(env) if env is not None else None
        object.__setattr__(self, "env", safe_env)

        if timeout is not None and timeout <= 0:
            raise ValueError(f"Timeout must be positive, got {timeout}")
        object.__setattr__(self, "timeout", timeout)


@dataclass(frozen=True, slots=True)
class CommandResult:
    """
    Immutable representation of a successful command execution result.

    Failures are propagated via CommandExecutionError, not via this class.
    """

    returncode: int
    stdout: str
    stderr: str


class CommandRunner(Protocol):
    """
    Port protocol for executing external commands.

    Implementations must raise CommandExecutionError on non-zero exit codes.
    """

    def run(self, command: Command) -> CommandResult:
        """Execute command synchronously and return structured result."""
        ...
