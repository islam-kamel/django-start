import io
import json
import urllib.error
from unittest.mock import patch

import pytest
from click.testing import CliRunner
from packaging.version import Version

from djstartlib.version import (
    check_available,
    current_version,
    latest_version,
    main,
    version,
)


def test_version_string():
    """Migration contract BC-VER-01: 2.x version string via distribution
    metadata.
    """
    assert version == "2.0.0a1 (beta)"


def test_current_version_type():
    """Migration contract BC-VER-02: current_version intentionally replaced
    by packaging.version.Version.
    """
    assert isinstance(current_version(), Version)
    assert current_version() == Version("2.0.0a1")


def test_latest_version_parsing():
    """2.x version behavior: parsing GitHub tag API response into version
    string and Version object.
    """
    payload = [{"name": "1.2.0"}]
    mock_response = io.BytesIO(json.dumps(payload).encode("utf-8"))
    with patch("urllib.request.urlopen", return_value=mock_response):
        tag_name, tag_version = latest_version()
        assert tag_name == "1.2.0"
        assert tag_version == Version("1.2.0")


@pytest.mark.parametrize(
    "latest, expected_newer",
    [
        ("1.1.6", False),
        ("2.0.0a1", False),
        ("2.0.0", True),
        ("2028.0", True),
    ],
)
def test_check_available_versions(capsys, latest, expected_newer):
    """Migration contract BC-VER-03: 2.x standards-based version
    comparison.
    """
    with patch(
        "djstartlib.version.latest_version",
        return_value=(latest, Version(latest)),
    ):
        result = check_available()
        captured = capsys.readouterr()
        if expected_newer:
            assert result is True
            assert f"New Update Available {latest}" in captured.out
        else:
            assert result is None
            assert "You have the latest version" in captured.out


def test_check_available_url_error():
    """Migration contract BC-VER-04: check_available raises SystemExit(1)
    on URLError.
    """
    with patch(
        "djstartlib.version.latest_version",
        side_effect=urllib.error.URLError("network down"),
    ):
        with pytest.raises(SystemExit) as exc_info:
            check_available()
        assert exc_info.value.code == 1


def test_cli_version_default():
    """Migration contract BC-VER-01: CLI invocation of django-version prints
    version string.
    """
    runner = CliRunner()
    result = runner.invoke(main, [])
    assert result.exit_code == 0
    assert "2.0.0a1 (beta)" in result.output


def test_cli_version_check_update():
    """Migration contract BC-VER-03: CLI invocation with --check-update
    checks for update.
    """
    runner = CliRunner()
    with patch(
        "djstartlib.version.latest_version",
        return_value=("2.0.0a1", Version("2.0.0a1")),
    ):
        result = runner.invoke(main, ["--check-update"])
        assert result.exit_code == 0
        assert "You have the latest version" in result.output


def test_cli_version_update_invokes_pip_with_shell():
    """Migration contract BC-VER-05: shell=True self-update still temporarily
    present in relocated legacy implementation.
    """
    runner = CliRunner()
    with patch("subprocess.call", return_value=0) as mock_subproc:
        result = runner.invoke(main, ["--update"])
        assert result.exit_code == 0
        assert mock_subproc.called
        call_args, call_kwargs = mock_subproc.call_args
        assert "pip install --upgrade django-start-automate" in call_args[0]
        assert call_kwargs.get("shell") is True
