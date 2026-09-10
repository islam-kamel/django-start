import os
from unittest.mock import patch

from djstartlib.models.project_manager import ProjectManager


def test_project_paths(isolated_workdir):
    """Characterize BC-PRJ-01: Project paths initialization for urls.py
    and settings.py.
    """
    pm = ProjectManager(project="mysite", app="blog")
    assert pm.urls_path == os.path.join(
        str(isolated_workdir), "mysite/urls.py"
    )
    assert pm.settings_path == os.path.join(
        str(isolated_workdir), "mysite/settings.py"
    )


def test_create_project_when_new(isolated_workdir):
    """Characterize BC-PRJ-02: Project creation when directory does not
    exist.
    """
    pm = ProjectManager(project="mysite", app="blog")
    with patch(
        "djstartlib.models.project_manager.executable_django_command"
    ) as mock_cmd:
        pm.create_project()
        mock_cmd.assert_called_once_with("startproject mysite .")


def test_create_project_when_exists(isolated_workdir, capsys):
    """Characterize BC-PRJ-03: Project creation warns and skips command when
    project directory exists.
    """
    (isolated_workdir / "mysite").mkdir()
    pm = ProjectManager(project="mysite", app="blog")
    with patch(
        "djstartlib.models.project_manager.executable_django_command"
    ) as mock_cmd:
        pm.create_project()
        mock_cmd.assert_not_called()
        captured = capsys.readouterr()
        assert '"mysite" Already exist!' in captured.out


def test_update_settings_inserts_app_before_closing_bracket(isolated_workdir):
    """Characterize BC-PRJ-04: update_settings inserts app name before
    closing bracket in settings.py.
    """
    proj_dir = isolated_workdir / "mysite"
    proj_dir.mkdir()
    settings_file = proj_dir / "settings.py"
    settings_file.write_text(
        "INSTALLED_APPS = [\n\t'django.contrib.admin',\n]\n", encoding="utf-8"
    )

    pm = ProjectManager(project="mysite", app="blog")
    pm.update_settings()

    content = settings_file.read_text(encoding="utf-8")
    assert "\t'blog',\n]\n" in content


def test_update_settings_warns_when_already_installed(
    isolated_workdir, capsys
):
    """Characterize BC-PRJ-05: update_settings warns when app is already
    present in settings.py.
    """
    proj_dir = isolated_workdir / "mysite"
    proj_dir.mkdir()
    settings_file = proj_dir / "settings.py"
    settings_file.write_text(
        "INSTALLED_APPS = [\n\t'blog',\n]\n", encoding="utf-8"
    )

    pm = ProjectManager(project="mysite", app="blog")
    pm.update_settings()

    captured = capsys.readouterr()
    assert '"blog" is installed!' in captured.out


def test_update_import_statement_inserts_include(isolated_workdir):
    """Characterize BC-PRJ-06: update_import_statment inserts include before
    path import.
    """
    pm = ProjectManager(project="mysite", app="blog")
    pm.line_list = ["from django.urls import path\n", "urlpatterns = []\n"]
    pm.update_import_statment()
    assert pm.line_list == [
        "from django.urls import include\n",
        "from django.urls import path\n",
        "urlpatterns = []\n",
    ]


def test_update_import_statement_skips_when_combined_present(isolated_workdir):
    """Characterize BC-PRJ-06: update_import_statment returns 0 and skips
    insertion if path, include already imported.
    """
    pm = ProjectManager(project="mysite", app="blog")
    pm.line_list = [
        "from django.urls import path, include\n",
        "urlpatterns = []\n",
    ]
    res = pm.update_import_statment()
    assert res == 0
    assert len(pm.line_list) == 2


def test_update_urls_wiring(isolated_workdir):
    """Characterize BC-PRJ-07: update_urls inserts include statement and
    app urlpatterns wiring.
    """
    proj_dir = isolated_workdir / "mysite"
    proj_dir.mkdir()
    urls_file = proj_dir / "urls.py"
    urls_file.write_text(
        "from django.urls import path\n\nurlpatterns = [\n]\n",
        encoding="utf-8",
    )

    pm = ProjectManager(project="mysite", app="blog")
    pm.update_urls(path="api/blog/")

    content = urls_file.read_text(encoding="utf-8")
    assert "from django.urls import include\n" in content
    assert "\tpath('api/blog/', include('blog.urls')),\n]\n" in content


def test_update_urls_warns_when_already_present(isolated_workdir, capsys):
    """Characterize BC-PRJ-08: update_urls warns when view path is already
    present in urls.py.
    """
    proj_dir = isolated_workdir / "mysite"
    proj_dir.mkdir()
    urls_file = proj_dir / "urls.py"
    urls_file.write_text(
        "from django.urls import path\n\n"
        "urlpatterns = [\n\tpath('', include('blog.urls')),\n]\n",
        encoding="utf-8",
    )

    pm = ProjectManager(project="mysite", app="blog")
    pm.update_urls(path="")

    captured = capsys.readouterr()
    assert "Urls Already Updated" in captured.out


def test_helper_delegations():
    """Characterize ProjectManager static helper delegations to module-level
    helper functions.
    """
    with patch("djstartlib.models.project_manager.upgrade_pip") as m_upg:
        ProjectManager.upgrade_pip()
        m_upg.assert_called_once()

    with patch("djstartlib.models.project_manager.install_dep") as m_inst:
        ProjectManager.install_dep()
        m_inst.assert_called_once()

    with patch(
        "djstartlib.models.project_manager.requirements_extract"
    ) as m_req:
        ProjectManager.requirements_extract()
        m_req.assert_called_once()
