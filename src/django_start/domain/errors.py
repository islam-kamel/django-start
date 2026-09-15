"""
Domain error hierarchy for Django-Start 2.0.

These errors represent typed failures across the generation lifecycle.
They do not call sys.exit() or format terminal output.
"""

from collections.abc import Sequence


class DjangoStartError(Exception):
    """Base exception for all Django-Start application errors."""

    pass


class ConfigurationError(DjangoStartError):
    """Raised when provided configuration or options are invalid."""

    pass


class InvalidIdentifierError(ConfigurationError):
    """Raised when an application or project identifier is not a valid Python
    identifier."""

    pass


class UnsupportedVersionError(ConfigurationError):
    """Raised when a requested Python or Django version is unsupported."""

    pass


class ProjectConflictError(DjangoStartError):
    """Raised when scaffolding cannot proceed safely due to existing files
    or directories."""

    pass


class CommandError(DjangoStartError):
    """Base exception for all external command execution failures."""

    pass


class CommandStartError(CommandError):
    """Raised when an external command cannot be started (e.g., OS errors)."""

    def __init__(self, message: str, argv: Sequence[str]) -> None:
        super().__init__(message)
        self.argv = tuple(argv)


class CommandTimeoutError(CommandError):
    """Raised when an external command times out."""

    def __init__(
        self,
        message: str,
        argv: Sequence[str],
        timeout: float,
        stdout: str,
        stderr: str,
    ) -> None:
        super().__init__(message)
        self.argv = tuple(argv)
        self.timeout = timeout
        self.stdout = stdout
        self.stderr = stderr


class CommandExecutionError(CommandError):
    """Raised when an external command exits with a non-zero status."""

    def __init__(
        self,
        message: str,
        argv: Sequence[str],
        returncode: int,
        stdout: str,
        stderr: str,
    ) -> None:
        super().__init__(message)
        self.argv = tuple(argv)
        self.returncode = returncode
        self.stdout = stdout
        self.stderr = stderr


class FileSystemError(DjangoStartError):
    """Raised when a safe filesystem operation fails."""

    def __init__(self, message: str, operation: str, path: str) -> None:
        super().__init__(message)
        self.operation = operation
        self.path = path


class EnvironmentCreationError(DjangoStartError):
    """Raised when virtual environment creation fails."""

    pass


class DependencyInstallError(DjangoStartError):
    """Raised when package installation fails."""

    pass


class VerificationError(DjangoStartError):
    """Raised when the generated project fails post-generation
    validation checks."""

    pass
