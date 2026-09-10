import json
import os
import pathlib
import subprocess
from unittest.mock import patch

import pytest

from djstartlib.models.utils.helper import (
    build_view_func,
    build_views_urls,
    create_env,
    executable_django_command,
    executable_python_command,
    generate_html,
    install_dep,
    requirements_extract,
    upgrade_pip,
    warn_stdout,
)


def test_template_generators():
    """Characterize BC-HLP-01: template generator string substitution and
    HTML output.
    """
    view_template = build_view_func().substitute(
        app_name="blog", html_file="index.html"
    )
    assert "def home(request):" in view_template
    assert "return render(request, 'blog" in view_template

    url_template = build_views_urls().substitute(view_name="home")
    assert "path('', views.home)" in url_template

    html = generate_html()
    assert "<title>Django Start</title>" in html
    assert "Hello, Django-Start" in html


def test_generate_html_exact_match():
    """Verify generate_html produces byte-for-byte identical output to
    1.1.6 fixture.
    """
    fixture_path = (
        pathlib.Path(__file__).resolve().parent.parent
        / "fixtures"
        / "generated-index-1.1.6.json"
    )
    data = json.loads(fixture_path.read_text(encoding="utf-8"))
    assert generate_html() == data["html"]


def test_warn_stdout(capsys):
    """Characterize warn_stdout printing formatted warning message to
    stdout.
    """
    warn_stdout("test warning")
    captured = capsys.readouterr()
    assert "WARNING: test warning" in captured.out


def test_create_env_sets_environment_variables(tmp_path, monkeypatch):
    """Characterize BC-HLP-02: create_env creates venv and sets
    PYTHONEXEC and DJANGOADMIN.
    """
    # Hermetically clear inherited environment variables before testing
    monkeypatch.delenv("PYTHONEXEC", raising=False)
    monkeypatch.delenv("DJANGOADMIN", raising=False)

    with patch("subprocess.call", return_value=0) as mock_call:
        with patch("platform.system", return_value="Darwin"):
            create_env(str(tmp_path / "myenv"))
            mock_call.assert_called_once()
            call_arg = mock_call.call_args[0][0]
            assert "-m venv" in call_arg
            assert str(tmp_path / "myenv") in call_arg
            assert os.environ["PYTHONEXEC"] == str(
                tmp_path / "myenv/bin/python3"
            )
            assert os.environ["DJANGOADMIN"] == str(
                tmp_path / "myenv/bin/django-admin"
            )


def test_create_env_windows_default_paths(tmp_path, monkeypatch):
    """Characterize BC-HLP-02: create_env on Windows sets Scripts paths
    in environment.
    """
    monkeypatch.delenv("PYTHONEXEC", raising=False)
    monkeypatch.delenv("DJANGOADMIN", raising=False)

    with patch("subprocess.call", return_value=0) as mock_call:
        with patch("platform.system", return_value="Windows"):
            env_path = str(tmp_path / "winenv")
            create_env(env_path)
            mock_call.assert_called_once()
            call_arg = mock_call.call_args[0][0]
            assert "-m venv" in call_arg
            assert env_path in call_arg
            assert os.environ["PYTHONEXEC"] == os.path.join(
                env_path, "Scripts/python.exe"
            )
            assert os.environ["DJANGOADMIN"] == os.path.join(
                env_path, "Scripts/django-admin.exe"
            )


def test_create_env_windows_django_admin_setdefault_behavior(
    tmp_path, monkeypatch
):
    """Characterize BC-HLP-02: create_env overwrites PYTHONEXEC but
    preserves pre-set DJANGOADMIN via setdefault.
    """
    monkeypatch.setenv("PYTHONEXEC", "/preexisting/python")
    monkeypatch.setenv("DJANGOADMIN", "/custom/django-admin")

    with patch("subprocess.call", return_value=0):
        with patch("platform.system", return_value="Windows"):
            env_path = str(tmp_path / "winenv")
            create_env(env_path)
            # PYTHONEXEC is unconditionally overwritten
            assert os.environ["PYTHONEXEC"] == os.path.join(
                env_path, "Scripts/python.exe"
            )
            assert os.environ["PYTHONEXEC"] != "/preexisting/python"
            # DJANGOADMIN uses setdefault, so the pre-existing value
            # is preserved
            assert os.environ["DJANGOADMIN"] == "/custom/django-admin"


def test_executable_python_command(monkeypatch):
    """Characterize BC-HLP-02: executable_python_command invokes
    subprocess.call with shell=True.
    """
    monkeypatch.setenv("PYTHONEXEC", "/usr/bin/python3")
    with patch("subprocess.call", return_value=0) as mock_call:
        executable_python_command("-m pip --version")
        mock_call.assert_called_once_with(
            "/usr/bin/python3 -m pip --version",
            stdout=subprocess.DEVNULL,
            stderr=subprocess.STDOUT,
            shell=True,
        )


def test_executable_python_command_failure_exits(monkeypatch):
    """Characterize BC-HLP-02: executable_python_command exits with code 1
    on non-zero process exit.
    """
    monkeypatch.setenv("PYTHONEXEC", "/usr/bin/python3")
    with patch("subprocess.call", return_value=1):
        with patch("platform.system", return_value="Darwin"):
            with pytest.raises(SystemExit) as exc_info:
                executable_python_command("invalid")
            assert exc_info.value.code == 1


def test_executable_django_command(monkeypatch):
    """Characterize BC-HLP-02: executable_django_command invokes
    subprocess.call with shell=True.
    """
    monkeypatch.setenv("DJANGOADMIN", "/usr/bin/django-admin")
    with patch("subprocess.call", return_value=0) as mock_call:
        executable_django_command("version")
        mock_call.assert_called_once_with(
            "/usr/bin/django-admin version",
            stdout=subprocess.DEVNULL,
            stderr=subprocess.STDOUT,
            shell=True,
        )


def test_helper_shortcut_commands():
    """Characterize shortcut functions delegating to
    executable_python_command.
    """
    with patch(
        "djstartlib.models.utils.helper.executable_python_command"
    ) as mock_exec:
        upgrade_pip()
        mock_exec.assert_called_with("-m pip install --upgrade pip")

        install_dep()
        mock_exec.assert_called_with("-m pip install django")

        requirements_extract()
        mock_exec.assert_called_with("-m pip freeze > requirements.txt")
