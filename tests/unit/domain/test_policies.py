"""Tests for validation and version policies."""
from datetime import date

import pytest
from packaging.specifiers import SpecifierSet
from packaging.version import Version

from django_start.domain.errors import (
    InvalidIdentifierError,
    UnsupportedVersionError,
)
from django_start.domain.policies import (
    FrameworkRegistry,
    FrameworkRelease,
    VersionPolicy,
    is_valid_identifier,
    validate_identifier,
)


@pytest.mark.parametrize(
    "name, expected",
    [
        ("my_project", True),
        ("core", True),
        ("app1", True),
        ("_private", True),
        ("my-project", False),
        ("123app", False),
        ("class", False),  # keyword
        ("def", False),    # keyword
        ("hello world", False),
    ],
)
def test_is_valid_identifier(name: str, expected: bool) -> None:
    assert is_valid_identifier(name) == expected


def test_validate_identifier_success() -> None:
    # Should not raise
    validate_identifier("my_project")


def test_validate_identifier_failure() -> None:
    with pytest.raises(InvalidIdentifierError, match="'my-project' is not a valid Python identifier"):
        validate_identifier("my-project")


def create_test_registry() -> FrameworkRegistry:
    """Create a synthetic registry for testing, including CalVer."""
    return FrameworkRegistry(
        (
            FrameworkRelease(
                series="6.1",
                tested_version=Version("6.1.1"),
                django_requires=SpecifierSet(">=6.1.1,<6.2"),
                python_requires=SpecifierSet(">=3.12"),
                is_lts=False,
                is_calver=False,
                eol_date=date(2026, 4, 1),
            ),
            FrameworkRelease(
                series="5.2",
                tested_version=Version("5.2.17"),
                django_requires=SpecifierSet(">=5.2.17,<5.3"),
                python_requires=SpecifierSet(">=3.10"),
                is_lts=True,
                is_calver=False,
                eol_date=date(2028, 4, 1),
            ),
            FrameworkRelease(
                series="2028.0",
                tested_version=Version("2028.0.1"),
                django_requires=SpecifierSet(">=2028.0.1,<2028.1"),
                python_requires=SpecifierSet(">=3.14"),
                is_lts=False,
                is_calver=True,
                eol_date=date(2031, 1, 1),
            ),
        )
    )


def test_version_policy_resolve_latest() -> None:
    policy = VersionPolicy(create_test_registry())
    release = policy.resolve_framework("latest")

    # In our test registry, the latest non-LTS is 2028.0 (Version 2028.0.1)
    assert release.series == "2028.0"
    assert release.tested_version == Version("2028.0.1")


def test_version_policy_resolve_lts() -> None:
    policy = VersionPolicy(create_test_registry())
    release = policy.resolve_framework("lts")

    # In our test registry, the latest LTS is 5.2
    assert release.series == "5.2"
    assert release.tested_version == Version("5.2.17")


def test_version_policy_resolve_exact_series() -> None:
    policy = VersionPolicy(create_test_registry())
    release = policy.resolve_framework("6.1")
    assert release.series == "6.1"
    assert release.tested_version == Version("6.1.1")


def test_version_policy_resolve_exact_version_string() -> None:
    policy = VersionPolicy(create_test_registry())
    release = policy.resolve_framework("5.2.17")
    assert release.series == "5.2"
    assert release.tested_version == Version("5.2.17")


def test_version_policy_resolve_unknown() -> None:
    policy = VersionPolicy(create_test_registry())
    with pytest.raises(UnsupportedVersionError, match="Unsupported framework track or version: '4.2'"):
        policy.resolve_framework("4.2")


def test_version_policy_no_lts_fallback() -> None:
    # Create registry with NO lts
    registry = FrameworkRegistry(
        (
            FrameworkRelease(
                series="6.1",
                tested_version=Version("6.1.1"),
                django_requires=SpecifierSet(">=6.1.1,<6.2"),
                python_requires=SpecifierSet(">=3.12"),
                is_lts=False,
            ),
        )
    )
    policy = VersionPolicy(registry)
    with pytest.raises(UnsupportedVersionError, match="No LTS releases available"):
        policy.resolve_framework("lts")


def test_version_policy_no_non_lts_latest_fallback() -> None:
    # Create registry with ONLY lts
    registry = FrameworkRegistry(
        (
            FrameworkRelease(
                series="5.2",
                tested_version=Version("5.2.17"),
                django_requires=SpecifierSet(">=5.2.17,<5.3"),
                python_requires=SpecifierSet(">=3.10"),
                is_lts=True,
            ),
        )
    )
    policy = VersionPolicy(registry)
    # latest should fallback to the highest version overall if no non-LTS exist
    release = policy.resolve_framework("latest")
    assert release.series == "5.2"


def test_validate_python_compatibility_success() -> None:
    policy = VersionPolicy(create_test_registry())
    release = policy.resolve_framework("6.1")

    # 6.1 requires >=3.12
    policy.validate_python_compatibility("3.12.0", release)
    policy.validate_python_compatibility("3.13.1", release)


def test_validate_python_compatibility_failure() -> None:
    policy = VersionPolicy(create_test_registry())
    release = policy.resolve_framework("2028.0")

    # 2028.0 requires >=3.14, providing 3.13 should fail
    with pytest.raises(UnsupportedVersionError, match="does not satisfy Django 2028.0 requirement"):
        policy.validate_python_compatibility("3.13.0", release)


def test_validate_python_global_minimum_failure() -> None:
    policy = VersionPolicy(create_test_registry())
    release = policy.resolve_framework("5.2")  # 5.2 in our test says >=3.10

    # But Django-Start 2.0 globally requires >=3.12
    with pytest.raises(UnsupportedVersionError, match="Django-Start 2.0 requires Python >= 3.12"):
        policy.validate_python_compatibility("3.11.0", release)


def test_is_supported_date() -> None:
    policy = VersionPolicy(create_test_registry())
    release = policy.resolve_framework("5.2")

    # 5.2 EOL is 2028-04-01 in the test registry
    assert policy.is_supported(release, date(2028, 3, 31)) is True
    assert policy.is_supported(release, date(2028, 4, 1)) is True
    assert policy.is_supported(release, date(2028, 4, 2)) is False


def test_is_supported_no_date() -> None:
    policy = VersionPolicy()

    release = FrameworkRelease(
        series="9.9",
        tested_version=Version("9.9.9"),
        django_requires=SpecifierSet(">=9.9.9,<9.10"),
        python_requires=SpecifierSet(">=3.12"),
        is_lts=False,
    )

    # Should always return True if eol_date is None
    assert policy.is_supported(release, date(2099, 1, 1)) is True
