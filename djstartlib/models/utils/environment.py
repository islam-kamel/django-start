"""
        self.__app_manager = AppManager(*args, **kwargs)
        self.__workdir = os.getcwd()
        self.__app_name = kwargs.get("app_name", None)
        self.__core_name = kwargs.get("core_name", None)
        self.__urls = self.__workdir + rf"{os.sep}{self.core_name}{os.sep}urls.py"
        self.__settings = (
            self.__workdir + rf"{os.sep}{self.core_name}{os.sep}settings.py"
        )
        self.python = os.environ.get("PYTHONPATH", None)
        self.django_admin = os.environ.get("DJANGOADMIN", None)
        self.__other_dependencies = []
        self.__line_list = []


        self.__app_name = kwargs.get("app_name", None)
        self.__workdir = os.getcwd() + rf"{os.sep}{self.app_name}"
        self.__views = self.workdir + rf"{os.sep}views.py"
        self.__urls = self.workdir + rf"{os.sep}urls.py"
        self.__templates = self.workdir + f"{os.sep}templates"
        self.python = os.environ.get("PYTHONPATH", None)
        self.__line_list = []
"""
import os


class Environment:
    def __init__(self, **kwargs):
        self.__app_name = kwargs.get('app')
        self.__project_name = kwargs.get('project')
        self.__workdir = os.getcwd()
        self.__exec = os.getenv('PYTHONEXEC')
        self.__django_admin = os.getenv('DJANGOADMIN')
        self.test()

    def get_app_name(self): return self.__app_name

    def get_project_name(self): return self.__project_name

    def get_workdir(self): return self.__workdir

    def get_exec(self): return self.__exec

    def get_django_admin(self): return self.__django_admin

    def test(self):
        print(f'Call {self.__class__.__name__}')
        print(f'App Name: {self.get_app_name()}')
        print(f'Project Name: {self.get_project_name()}')
        print(f'Workdir: {self.get_workdir()}')
        print(f'Python Path: {self.get_exec()}')
        print(f'Django Admin: {self.get_django_admin()}')
