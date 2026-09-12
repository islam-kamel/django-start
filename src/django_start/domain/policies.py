"""
Domain policies for validation and version management.

These policies must be pure and free from ambient system state (no I/O, no sys.version).
"""
import keyword
from collections.abc import Sequence
from dataclasses import dataclass
from datetime import date

from packaging.specifiers import SpecifierSet
from packaging.version import Version

from django_start.domain.errors import (
    InvalidIdentifierError,
    UnsupportedVersionError,
)


def is_valid_identifier(name: str) -> bool:
    """Check if a string is a valid Python identifier, excluding keywords."""
    return name.isidentifier() and not keyword.iskeyword(name)


def validate_identifier(name: str, entity_type: str = "Identifier") -> None:
    """Validate identifier and raise a typed error if invalid."""
    if not is_valid_identifier(name):
        raise InvalidIdentifierError(f"{entity_type} '{name}' is not a valid Python identifier.")


@dataclass(frozen=True, slots=True)
class FrameworkRelease:
    """Immutable representation of a supported Django framework release."""
    series: str
    tested_version: Version
    django_requires: SpecifierSet
    python_requires: SpecifierSet
    is_lts: bool
    is_calver: bool = False
    eol_date: date | None = None


@dataclass(frozen=True, slots=True)
class FrameworkRegistry:
    """Immutable registry of supported framework releases."""
    releases: tuple[FrameworkRelease, ...]

    def __init__(self, releases: Sequence[FrameworkRelease]) -> None:
        object.__setattr__(self, "releases", tuple(releases))


# Explicit registry containing only currently accepted supported releases (ADR-002)
# Django 6.1 (Feature Track, baseline 6.1.1)
# Django 5.2 LTS (LTS Track, baseline 5.2.17)
BUILTIN_REGISTRY = FrameworkRegistry(
    (
        FrameworkRelease(
            series="6.1",
            tested_version=Version("6.1.1"),
            django_requires=SpecifierSet(">=6.1.1,<6.2"),
            python_requires=SpecifierSet(">=3.12"),
            is_lts=False,
            is_calver=False,
        ),
        FrameworkRelease(
            series="5.2",
            tested_version=Version("5.2.17"),
            django_requires=SpecifierSet(">=5.2.17,<5.3"),
            python_requires=SpecifierSet(">=3.10"),  # Django 5.2 supports >=3.10
            is_lts=True,
            is_calver=False,
        ),
    )
)


class VersionPolicy:
    """Evaluates version selection and support policies."""

    def __init__(self, registry: FrameworkRegistry = BUILTIN_REGISTRY) -> None:
        self._registry = registry

    def resolve_framework(self, track: str) -> FrameworkRelease:
        """
        Resolve a framework track (latest, lts, or specific version) to a FrameworkRelease.
        Unknown tracks raise UnsupportedVersionError.
        """
        if track == "latest":
            # Return the latest feature release (highest tested version not an LTS)
            # Actually, per ADR-002, latest is newest tested stable feature line.
            # We can just sort by version.
            try:
                return max(
                    (r for r in self._registry.releases if not r.is_lts),
                    key=lambda r: r.tested_version
                )
            except ValueError:
                # Fallback if no non-LTS releases exist, just get the max
                return max(self._registry.releases, key=lambda r: r.tested_version)

        elif track == "lts":
            # Return the active LTS release
            try:
                return max(
                    (r for r in self._registry.releases if r.is_lts),
                    key=lambda r: r.tested_version
                )
            except ValueError:
                raise UnsupportedVersionError("No LTS releases available in the registry.")

        else:
            # Try to match the series (e.g. '6.1', '5.2', '2028.0')
            for release in self._registry.releases:
                if release.series == track:
                    return release

            # If not matching series, try exact version string match
            for release in self._registry.releases:
                if str(release.tested_version) == track:
                    return release

            # Format the error with available choices
            available = ", ".join(f"'{r.series}'" for r in self._registry.releases)
            raise UnsupportedVersionError(
                f"Unsupported framework track or version: '{track}'. "
                f"Available releases: {available}, or 'latest', 'lts'."
            )

    def validate_python_compatibility(self, host_python: str, release: FrameworkRelease) -> None:
        """
        Validate explicit host Python version against the release requirements.
        Raises UnsupportedVersionError if incompatible.
        """
        host_version = Version(host_python)

        # Django-Start 2.0 requires Python >= 3.12 itself.
        if host_version < Version("3.12"):
            raise UnsupportedVersionError(
                f"Django-Start 2.0 requires Python >= 3.12. Active version: {host_python}."
            )

        if str(host_version) not in release.python_requires:
            raise UnsupportedVersionError(
                f"Host Python {host_python} does not satisfy Django {release.series} "
                f"requirement: {release.python_requires}."
            )

    def is_supported(self, release: FrameworkRelease, on_date: date) -> bool:
        """
        Evaluate if a release is supported on a given date.
        """
        if release.eol_date is None:
            return True
        return on_date <= release.eol_date
