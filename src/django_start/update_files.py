import os
from .project import ProjectManager

class UpdateFile:
    def __init__(self, *args, **kwargs):
        self.project = ProjectManager(**kwargs)
        self.app_name = kwargs.get('app_name', None)
        self.workdir = kwargs.get('workdir', None)
        self.app = self.workdir + fr'\{self.app_name}'
        os.chdir(self.workdir)

    def update_settings(self):
        return self.project.update_settings(self.app_name)

    def update_urls(self):
        self.project.update_urls(self.app_name)

    def create_view(self):
        with open(self.app + r'\views.py', 'r') as f:
            views = f.readlines()
            views.insert(4, "def home(request):\n\treturn render(request, 'index.html')\n")
            f.close()
            with open(self.app + r'\views.py', 'w') as vf:
                vf.write(''.join(views))
                vf.close()

    def create_urls(self):
        os.chdir(self.app)
        with open('urls.py', 'w') as f:
            content = [
                'from django.urls import path\n',
                'from . import views\n'
                '\n',
                'urlpatterns = [\n',
                '\tpath(\'\', views.home)\n'
                ']\n'
            ]
            f.write(''.join(content))
            f.close()
