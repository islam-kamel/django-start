import os


class Environment:
    def __init__(self, **kwargs):
        self.__app_name = kwargs.get('app')
        self.__project_name = kwargs.get('project')
        self.__workdir = os.getcwd()
        self.__exec = os.getenv('PYTHONEXEC')
        self.__django_admin = os.getenv('DJANGOADMIN')
        self.__line_list = []

    @property
    def line_list(self) -> list: return self.__line_list

    def index(self, value: str) -> int: return self.line_list.index(value)

    def insert_line(self, flag: str, value: str) -> None:
        self.line_list.insert(self.index(flag), value)

    def replace_line(self, index: int, value: str) -> None:
        self.line_list[index] = value

    @line_list.setter
    def line_list(self, value: list) -> None:
        self.__line_list = value

    def read_file(self, file: str) -> list:
        with open(file) as f:
            self.line_list = f.readlines()
            f.close()
        return self.line_list

    def write(self, file_path: str, value = None) -> None:
        with open(file_path, 'w') as f:
            f.write(''.join(value or self.line_list))
            f.close()

    def get_app_name(self) -> str: return self.__app_name

    def get_project_name(self) -> str: return self.__project_name

    def get_workdir(self) -> str: return self.__workdir

    def get_exec(self) -> str: return self.__exec

    def get_django_admin(self) -> str: return self.__django_admin

    def test(self):
        print(f'Call {self.__class__.__name__}')
        print(f'App Name: {self.get_app_name()}')
        print(f'Project Name: {self.get_project_name()}')
        print(f'Workdir: {self.get_workdir()}')
        print(f'Python Path: {self.get_exec()}')
        print(f'Django Admin: {self.get_django_admin()}')
