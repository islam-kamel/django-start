from models import AppManager, ProjectManager
from models.utils.hellper import create_env


class DjangoStart:
    def __init__(self, env_path, **kwargs):
        self.project_cls = ProjectManager(**kwargs)
        self.app_cls = AppManager(**kwargs)
        create_env(env_path)

    def setup_project(self):
        self.project_cls.upgrade_pip()
        self.project_cls.install_dep()
        self.project_cls.create_project()
        self.project_cls.requirements_extract()

    def setup_app(self, app_url: str = ''):
        self.app_cls.create_app()
        self.project_cls.update_settings()
        self.project_cls.update_urls(path=app_url)
        self.app_cls.update_view()
        self.app_cls.create_templates()
        self.app_cls.create_urls()
