"""Tests for the domain error hierarchy."""

from django_start.domain.errors import (
    CommandExecutionError,
    ConfigurationError,
    DependencyInstallError,
    DjangoStartError,
    EnvironmentCreationError,
    InvalidIdentifierError,
    ProjectConflictError,
    UnsupportedVersionError,
    VerificationError,
)


def test_error_hierarchy() -> None:
    """Ensure all errors inherit from DjangoStartError."""
    assert issubclass(ConfigurationError, DjangoStartError)
    assert issubclass(InvalidIdentifierError, ConfigurationError)
    assert issubclass(UnsupportedVersionError, ConfigurationError)
    assert issubclass(ProjectConflictError, DjangoStartError)
    assert issubclass(CommandExecutionError, DjangoStartError)
    assert issubclass(EnvironmentCreationError, DjangoStartError)
    assert issubclass(DependencyInstallError, DjangoStartError)
    assert issubclass(VerificationError, DjangoStartError)


def test_command_execution_error_attributes() -> None:
    """Ensure CommandExecutionError stores structured diagnostic information."""
    error = CommandExecutionError(
        message="Command failed",
        returncode=1,
        stdout="out",
        stderr="err",
    )

    assert str(error) == "Command failed"
    assert error.returncode == 1
    assert error.stdout == "out"
    assert error.stderr == "err"
