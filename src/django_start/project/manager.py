class ProjectManager:
    def __init__(self, *args, **kwargs):
        self.__core_name = kwargs.get('core_name', None)
        self.__workdir = kwargs.get('workdir', None)
        self.__urls = self.__workdir + fr'\{self.core_name}\urls.py'
        self.__settings = self.__workdir + fr'\{self.core_name}\settings.py'
        self.__line_list = []

    @property
    def core_name(self):
        return self.__core_name

    @property
    def urls(self):
        return self.__urls

    @property
    def settings(self):
        return self.__settings

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

    def update_settings(self, value):
        self.read_file(self.settings)
        self.update_lines_list(']\n', f'\t\'{value}\',\n')
        with open(self.settings, 'w') as f:
            f.write(''.join(self.line_list))
            f.close()

    def update_urls(self, value):
        self.read_file(self.urls)
        self.replace_line(
            self.index('from django.urls import path\n'),
            'from django.urls import path, include\n'
        )
        self.update_lines_list(
            ']\n',
            f'\tpath(\'\', include(\'{value}.urls\')),\n'
        )
        with open(self.urls, 'w') as f:
            f.write(''.join(self.line_list))
            f.close()
