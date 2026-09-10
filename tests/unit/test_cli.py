from pathlib import Path
from unittest.mock import MagicMock, patch

from click.testing import CliRunner

from djstartlib.main import main


def test_cli_missing_arguments_fails():
    """Characterize BC-CLI-05: missing required arguments causes Click to exit
    with code 2.
    """
    runner = CliRunner()
    result = runner.invoke(main, [])
    assert result.exit_code == 2
    assert "Missing argument" in result.output


def test_cli_default_invocation(isolated_workdir):
    """Characterize BC-CLI-01: default invocation initializes DjangoStart
    with env and executes setup.
    """
    runner = CliRunner()
    with patch("djstartlib.main.DjangoStart") as mock_dj:
        instance = MagicMock()
        mock_dj.return_value = instance

        result = runner.invoke(main, ["myproject", "myapp"])
        assert result.exit_code == 0

        call_args, call_kwargs = mock_dj.call_args
        assert call_args[0] == Path("env").absolute()
        assert call_kwargs["project"] == "myproject"
        assert call_kwargs["app"] == "myapp"

        instance.setup_project.assert_called_once()
        instance.setup_app.assert_called_once_with(app_url="")


def test_cli_custom_options(isolated_workdir):
    """Characterize BC-CLI-02, BC-CLI-03, BC-CLI-04: custom name, url-path,
    and deprecated virtualenv flag.
    """
    runner = CliRunner()
    with patch("djstartlib.main.DjangoStart") as mock_dj:
        instance = MagicMock()
        mock_dj.return_value = instance

        result = runner.invoke(
            main,
            ["myproject", "myapp", "-n", "custom_env", "-u", "api/v1/", "-v"],
        )
        assert result.exit_code == 0

        call_args, call_kwargs = mock_dj.call_args
        assert call_args[0] == Path("custom_env").absolute()
        instance.setup_app.assert_called_once_with(app_url="api/v1/")

        assert "Please Don't Use This Option is Deprecated" in result.output
