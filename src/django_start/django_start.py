import os
from .virtualenv.virtualenv import VirtualEnv


class DjangoStart:
    def __init__(self, *args, **kwargs):
        self.__workdir = kwargs.get('workdir', None)
        self.__app_name = kwargs.get('app_name', None)
        self.__core_name = kwargs.get('core_name', None)
        self.env = VirtualEnv()

    @property
    def core_name(self):
        return self.__core_name

    @core_name.setter
    def core_name(self, name):
        self.__core_name = name
        return self.core_name

    @property
    def app_name(self):
        return self.__app_name

    @app_name.setter
    def app_name(self, name):
        self.__app_name = name
        return self.app_name

    @property
    def workdir(self):
        return self.__workdir

    @workdir.setter
    def workdir(self, workdir):
        self.__workdir = workdir
        return self.workdir

    def change_dir(self):
        os.chdir(self.workdir)

    def create_env(self):
        self.change_dir()
        self.env.create_env()

    def install_dep(self):
        os.system('pip install django djangorestframework')
        os.system(f'django-admin startproject {self.core_name} {self.workdir}')
        os.system(f'python ./manage.py startapp {self.app_name}')

    def create_project(self):
        os.system(f'django-admin startproject {self.core_name} {self.workdir}')
        os.system(f'python ./manage.py startapp {self.app_name}')

    def create_templates(self):
        os.mkdir(fr'{self.workdir}\{self.app_name}\templates')
        with open(fr'{self.workdir}\{self.app_name}\templates\index.html', 'w') as f:
            content = [
                '<!DOCTYPE html>\n',
                '<html lang="en">\n',
                '<head>\n',
                '\t<meta charset="UTF-8">\n',
                '\t<title>Hello, Django-Start</title>\n',
                '</head>\n',
                '<body>\n',
                '\t<h1 style="text-align: center"> Hello, Django-Start</h1>\n',
                '\t<a href="https://github.com/islam-kamel/django-start"><h1 style="text-align: center">Project</h1></a>\n',
                '</body>\n</html>'
            ]
            f.write(''.join(content))
            f.close()

