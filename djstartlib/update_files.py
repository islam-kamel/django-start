import os
from .app_manager import AppManager
from .project_manager import ProjectManager


class UpdateFile:
    def __init__(self, *args, **kwargs):
        self.project = ProjectManager(**kwargs)
        self.app = AppManager(**kwargs)
        os.chdir(self.project.workdir)

    def update_settings(self):
        print(f"🔧 Update {self.project.core_name} Settings")
        return self.project.update_settings(self.app.app_name)

    def update_urls(self):
        print(f"⬆  Update {self.project.core_name} Urls")
        self.project.update_urls(self.app.app_name)

    def create_view(self):
        print(f"📦 Update {self.app.app_name} View")
        self.app.update_view()

    def create_urls(self):
        print(f"🔗 Create {self.app.app_name} Urls")
        self.app.create_urls()

    def create_templates(self):
        print(f"📝 Create Templates For {self.app.app_name}")
        self.app.create_templates()

    def update_project_files(self):
        self.update_settings()
        self.update_urls()
        self.create_templates()
        self.create_view()
        self.create_urls()
