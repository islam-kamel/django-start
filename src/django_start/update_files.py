import os


class UpdateFile:
    def __init__(self, *args, **kwargs):
        self.core_name = kwargs.get('core_name', None)
        self.app_name = kwargs.get('app_name', None)
        self.workdir = kwargs.get('workdir', None)
        self.settings = self.workdir + fr'\{self.core_name}\settings.py'
        self.urls = self.workdir + fr'\{self.core_name}\urls.py'
        self.app = self.workdir + fr'\{self.app_name}'
        os.chdir(self.workdir)


    def update_settings(self):
        with open(self.settings, 'r+') as f:
            settings = f.readlines()
            settings.insert(settings.index(']\n') - 1, f"\t'{self.app_name}',\n")
            f.close()
            with open(self.settings, 'w') as sf:
                sf.write(''.join(settings))
                sf.close()

    def update_urls(self):
        with open(self.urls, 'r') as f:
            urls = f.readlines()
            urls[urls.index('from django.urls import path\n')] = 'from django.urls import path, include\n'
            urls.insert(urls.index(']\n') - 1, f"\tpath('', include('{self.app_name}.urls')),\n")
            f.close()
            with open(self.urls, 'w') as uf:
                uf.write(''.join(urls))
                uf.close()

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
