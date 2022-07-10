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

    @property
    def app_name(self):
        return self.__app_name

    @property
    def workdir(self):
        return self.__workdir

    def create_env(self):
        os.chdir(self.workdir)
        self.env.create_env()

    def install_dep(self):
        os.system('pip install django')

    def create_project(self):
        os.system(f'django-admin startproject {self.core_name} {self.workdir}')

    def create_app(self):
        os.system(f'python manage.py startapp {self.app_name}')
