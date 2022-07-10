import os


class AppManager:
    def __init__(self, *args, **kwargs):
        self.__app_name = kwargs.get('app_name', None)
        self.__workdir = kwargs.get('workdir', None) + fr'\{self.app_name}'
        self.__views = self.workdir + r'\views.py'
        self.__urls = self.workdir + r'\urls.py'
        self.__line_list = []


    @property
    def app_name(self):
        return self.__app_name


    @property
    def workdir(self):
        return self.__workdir


    @property
    def views(self):
        return self.__views


    @property
    def urls(self):
        return self.__urls


    @property
    def line_list(self):
        return self.__line_list


    @line_list.setter
    def line_list(self, value):
        self.__line_list = value
        return self.__line_list


    def index(self, value):
        return self.line_list.index(value)


    def read_file(self, file):
        with open(file, 'r') as f:
            self.line_list = f.readlines()
            f.close()
        return self.line_list


    def update_lines_list(self, flag, value):
        self.line_list.insert(self.index(flag), value)


    def replace_line(self, index, value):
        self.line_list[index] = value


    def update_view(self):
        self.read_file(self.views)
        self.replace_line(
            self.index('# Create your views here.\n'),
            'def home(request):\n\treturn render(request, \'index.html\')\n'
        )
        with open(self.views, 'w') as f:
            f.write(''.join(self.line_list))
            f.close()


    def create_urls(self):
        with open(self.urls, 'w') as f:
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
