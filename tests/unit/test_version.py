import io
import json
import urllib.error
from unittest.mock import patch

import pytest
from click.testing import CliRunner

from djstartlib.version import (
    check_available,
    current_version,
    latest_version,
    main,
    version,
)


def test_version_string():
    """Characterize BC-VER-01: version string constant is '1.1.6 (beta)'."""
    assert version == "1.1.6 (beta)"


def test_current_version_tuple():
    """Characterize current_version returning integer list [1, 1, 6]."""
    assert current_version() == [1, 1, 6]


def test_latest_version_parsing():
    """Characterize parsing GitHub tag API response into version string and integer components."""
    payload = [{"name": "1.2.0-beta"}]
    mock_response = io.BytesIO(json.dumps(payload).encode("utf-8"))
    with patch("urllib.request.urlopen", return_value=mock_response):
        tag_name, tag_ints = latest_version()
        assert tag_name == "1.2.0-beta"
        assert tag_ints == [1, 2, 0]


def test_check_available_when_newer(capsys):
    """Characterize BC-VER-02: check_available reports update when sum(latest) > sum(current).

    Note: The brief specified ("2.0.0", [2, 0, 0]), but because 1.1.6 compares versions
    using sum(), sum([2, 0, 0]) = 2 is less than sum([1, 1, 6]) = 8, causing 2.0.0
    to be reported as not newer. Using 1.1.7 (sum 9 > 8) correctly exercises the update branch.
    """
    with patch("djstartlib.version.latest_version", return_value=("1.1.7", [1, 1, 7])):
        result = check_available()
        captured = capsys.readouterr()
        assert result is True
        assert "New Update Available 1.1.7" in captured.out


def test_check_available_when_not_newer(capsys):
    """Characterize BC-VER-03: check_available reports latest version when not newer."""
    with patch("djstartlib.version.latest_version", return_value=("1.1.6", [1, 1, 6])):
        result = check_available()
        captured = capsys.readouterr()
        assert result is None
        assert "You have the latest version" in captured.out


def test_check_available_arithmetic_quirk(capsys):
    """Characterize BC-VER-02 defect: sum(var_int) arithmetic comparison defect.

    Demonstrates known defect where sum([1, 0, 9]) = 10 > sum([1, 1, 6]) = 8.
    Reports new update available even though 1.0.9 is older.
    """
    with patch("djstartlib.version.latest_version", return_value=("1.0.9", [1, 0, 9])):
        with patch("djstartlib.version.current_version", return_value=[1, 1, 6]):
            result = check_available()
            captured = capsys.readouterr()
            assert result is True
            assert "New Update Available 1.0.9" in captured.out


def test_check_available_url_error():
    """Characterize BC-VER-04: check_available raises SystemExit(1) on URLError."""
    with patch("djstartlib.version.latest_version", side_effect=urllib.error.URLError("network down")):
        with pytest.raises(SystemExit) as exc_info:
            check_available()
        assert exc_info.value.code == 1


def test_cli_version_default():
    """Characterize BC-VER-01: CLI invocation of django-version prints version string."""
    runner = CliRunner()
    result = runner.invoke(main, [])
    assert result.exit_code == 0
    assert "1.1.6 (beta)" in result.output


def test_cli_version_check_update():
    """Characterize BC-VER-03: CLI invocation with --check-update checks for update."""
    runner = CliRunner()
    with patch("djstartlib.version.latest_version", return_value=("1.1.6", [1, 1, 6])):
        result = runner.invoke(main, ["--check-update"])
        assert result.exit_code == 0
        assert "You have the latest version" in result.output


def test_cli_version_update_invokes_pip_with_shell():
    """Characterize BC-VER-05: CLI invocation with --update calls subprocess.call with shell=True."""
    runner = CliRunner()
    with patch("subprocess.call", return_value=0) as mock_subproc:
        result = runner.invoke(main, ["--update"])
        assert result.exit_code == 0
        assert mock_subproc.called
        call_args, call_kwargs = mock_subproc.call_args
        assert "pip install --upgrade django-start-automate" in call_args[0]
        assert call_kwargs.get("shell") is True
