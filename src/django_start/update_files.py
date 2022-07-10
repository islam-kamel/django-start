import os
from .project import ProjectManager
from .app import AppManager


class UpdateFile:
    def __init__(self, *args, **kwargs):
        self.project = ProjectManager(**kwargs)
        self.app = AppManager(**kwargs)
        self.app_name = kwargs.get('app_name', None)
        self.workdir = kwargs.get('workdir', None)
        os.chdir(self.workdir)

    def update_settings(self):
        return self.project.update_settings(self.app_name)

    def update_urls(self):
        self.project.update_urls(self.app_name)

    def create_view(self):
        self.app.update_view()

    def create_urls(self):
        self.app.create_urls()

    def create_templates(self):
        self.app.create_templates()