from unittest.mock import patch

import pytest

from djstartlib.models.djstart_interface import DjangoStart


@pytest.mark.integration
def test_full_scaffold_lifecycle(isolated_workdir):
    """Characterize BC-ORCH-01: DjangoStart full lifecycle orchestration
    with mocked boundaries.
    """
    env_dir = isolated_workdir / "env"
    proj_dir = isolated_workdir / "demo_proj"
    app_dir = isolated_workdir / "demo_app"

    def simulate_startproject(cmd):
        proj_dir.mkdir()
        (proj_dir / "settings.py").write_text(
            "INSTALLED_APPS = [\n]\n", encoding="utf-8"
        )
        (proj_dir / "urls.py").write_text(
            "from django.urls import path\nurlpatterns = [\n]\n",
            encoding="utf-8",
        )

    def simulate_startapp(cmd):
        app_dir.mkdir()
        (app_dir / "views.py").write_text(
            "# Create your views here.\n", encoding="utf-8"
        )

    with (
        patch(
            "djstartlib.models.djstart_interface.create_env"
        ) as mock_create_env,
        patch(
            "models.project_manager.executable_django_command",
            side_effect=simulate_startproject,
        ) as mock_dj_cmd,
        patch("models.project_manager.upgrade_pip"),
        patch("models.project_manager.install_dep"),
        patch("models.project_manager.requirements_extract"),
        patch(
            "models.app_manager.executable_python_command",
            side_effect=simulate_startapp,
        ) as mock_py_cmd,
    ):
        app = DjangoStart(str(env_dir), project="demo_proj", app="demo_app")
        mock_create_env.assert_called_once_with(str(env_dir))

        app.setup_project()
        mock_dj_cmd.assert_called_once_with("startproject demo_proj .")

        app.setup_app(app_url="demo/")
        mock_py_cmd.assert_called_once_with("manage.py startapp demo_app")

        # Verify all file mutations completed successfully
        settings_text = (proj_dir / "settings.py").read_text(encoding="utf-8")
        assert "\t'demo_app',\n]\n" in settings_text

        urls_text = (proj_dir / "urls.py").read_text(encoding="utf-8")
        assert "from django.urls import include\n" in urls_text
        assert "\tpath('demo/', include('demo_app.urls')),\n]\n" in urls_text

        views_text = (app_dir / "views.py").read_text(encoding="utf-8")
        assert "def home(request):" in views_text

        app_urls_text = (app_dir / "urls.py").read_text(encoding="utf-8")
        assert "path('', views.home)" in app_urls_text

        index_html = app_dir / "templates" / "demo_app" / "index.html"
        assert index_html.exists()
        assert "Hello, Django-Start" in index_html.read_text(encoding="utf-8")
