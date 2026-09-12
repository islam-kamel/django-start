"""
Domain error hierarchy for Django-Start 2.0.

These errors represent typed failures across the generation lifecycle.
They do not call sys.exit() or format terminal output.
"""


class DjangoStartError(Exception):
    """Base exception for all Django-Start application errors."""

    pass


class ConfigurationError(DjangoStartError):
    """Raised when provided configuration or options are invalid."""

    pass


class InvalidIdentifierError(ConfigurationError):
    """Raised when an application or project identifier is not a valid Python identifier."""

    pass


class UnsupportedVersionError(ConfigurationError):
    """Raised when a requested Python or Django version is unsupported."""

    pass


class ProjectConflictError(DjangoStartError):
    """Raised when scaffolding cannot proceed safely due to existing files or directories."""

    pass


class CommandExecutionError(DjangoStartError):
    """Raised when an external command exits with a non-zero status."""

    def __init__(
        self, message: str, returncode: int, stdout: str, stderr: str
    ) -> None:
        super().__init__(message)
        self.returncode = returncode
        self.stdout = stdout
        self.stderr = stderr


class EnvironmentCreationError(DjangoStartError):
    """Raised when virtual environment creation fails."""

    pass


class DependencyInstallError(DjangoStartError):
    """Raised when package installation fails."""

    pass


class VerificationError(DjangoStartError):
    """Raised when the generated project fails post-generation validation checks."""

    pass
