import os
from unittest.mock import patch

from djstartlib.models.app_manager import AppManager


def test_app_paths(isolated_workdir):
    """Characterize app paths initialization and properties."""
    am = AppManager(project="mysite", app="blog")
    assert am.app_name == "blog"
    assert am.workdir == os.path.join(str(isolated_workdir), "blog")
    assert am.views == os.path.join(str(isolated_workdir), "blog/views.py")
    assert am.urls == os.path.join(str(isolated_workdir), "blog/urls.py")
    assert am.templates == os.path.join(str(isolated_workdir), "blog/templates")


def test_create_app_when_new(isolated_workdir):
    """Characterize BC-APP-01: create_app executes manage.py startapp when app dir does not exist."""
    am = AppManager(project="mysite", app="blog")
    with patch("djstartlib.models.app_manager.executable_python_command") as mock_cmd:
        am.create_app()
        mock_cmd.assert_called_once_with("manage.py startapp blog")


def test_create_app_when_exists(isolated_workdir, capsys):
    """Characterize BC-APP-02: create_app warns and skips command when app directory exists."""
    (isolated_workdir / "blog").mkdir()
    am = AppManager(project="mysite", app="blog")
    with patch("djstartlib.models.app_manager.executable_python_command") as mock_cmd:
        am.create_app()
        mock_cmd.assert_not_called()
        captured = capsys.readouterr()
        assert '"blog" already exist!' in captured.out


def test_update_view_replaces_default_comment(isolated_workdir):
    """Characterize BC-APP-03: update_view replaces default comment with home view function."""
    app_dir = isolated_workdir / "blog"
    app_dir.mkdir()
    views_file = app_dir / "views.py"
    views_file.write_text("from django.shortcuts import render\n\n# Create your views here.\n", encoding="utf-8")

    am = AppManager(project="mysite", app="blog")
    am.update_view()

    content = views_file.read_text(encoding="utf-8")
    assert "def home(request):" in content
    assert "return render(request, 'blog" in content
    assert "index.html')" in content


def test_update_view_warns_when_comment_missing(isolated_workdir, capsys):
    """Characterize BC-APP-04: update_view warns when default comment is missing."""
    app_dir = isolated_workdir / "blog"
    app_dir.mkdir()
    views_file = app_dir / "views.py"
    views_file.write_text("from django.shortcuts import render\n", encoding="utf-8")

    am = AppManager(project="mysite", app="blog")
    am.update_view()

    captured = capsys.readouterr()
    assert '"home" View is Exists!' in captured.out
    assert views_file.read_text(encoding="utf-8") == "from django.shortcuts import render\n"


def test_create_urls(isolated_workdir):
    """Characterize BC-APP-05: create_urls creates urls.py with home view route."""
    app_dir = isolated_workdir / "blog"
    app_dir.mkdir()

    am = AppManager(project="mysite", app="blog")
    am.create_urls()

    urls_file = app_dir / "urls.py"
    assert urls_file.exists()
    content = urls_file.read_text(encoding="utf-8")
    assert "from django.urls import path" in content
    assert "from . import views" in content
    assert "path('', views.home)" in content


def test_create_templates(isolated_workdir):
    """Characterize BC-APP-06: create_templates generates index.html in templates/<app>/ directory."""
    app_dir = isolated_workdir / "blog"
    app_dir.mkdir()

    am = AppManager(project="mysite", app="blog")
    am.create_templates()

    index_file = app_dir / "templates" / "blog" / "index.html"
    assert index_file.exists()
    content = index_file.read_text(encoding="utf-8")
    assert "<title>Django Start</title>" in content
    assert "Hello, Django-Start" in content


def test_create_templates_warns_when_already_exists(isolated_workdir, capsys):
    """Characterize BC-APP-07: create_templates warns and preserves existing index.html."""
    app_dir = isolated_workdir / "blog"
    app_dir.mkdir()
    templates_dir = app_dir / "templates" / "blog"
    templates_dir.mkdir(parents=True)
    index_file = templates_dir / "index.html"
    index_file.write_text("existing", encoding="utf-8")

    am = AppManager(project="mysite", app="blog")
    am.create_templates()

    captured = capsys.readouterr()
    assert "Index.html is Already exists." in captured.out
    assert index_file.read_text(encoding="utf-8") == "existing"
