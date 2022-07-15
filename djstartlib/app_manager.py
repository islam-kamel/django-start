import os
import subprocess
from hellper import warn_stdout


class AppManager:
    def __init__(self, *args, **kwargs):
        self.__app_name = kwargs.get("app_name", None)
        self.__workdir = os.getcwd() + rf"{os.sep}{self.app_name}"
        self.__views = self.workdir + rf"{os.sep}views.py"
        self.__urls = self.workdir + rf"{os.sep}urls.py"
        self.__templates = self.workdir + rf"{os.sep}templates"
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
        return self.line_list

    def index(self, value):
        return self.line_list.index(value)

    def read_file(self, file):
        with open(file) as f:
            self.line_list = f.readlines()
            f.close()
        return self.line_list

    def update_lines_list(self, flag, value):
        self.line_list.insert(self.index(flag), value)

    def replace_line(self, index, value):
        self.line_list[index] = value

    def create_app(self):
        if self.app_name not in os.listdir(
            f"{os.sep}".join(self.workdir.split(os.sep)[:-1])
        ):
            print(f'✨ Create App "{self.app_name}"')
            subprocess.call(
                f"python manage.py startapp {self.app_name}", shell=True
            )
        else:
            warn_stdout(f'"{self.app_name}" already exist!')

    def update_view(self):
        self.read_file(self.views)
        if "# Create your views here.\n" in self.line_list:
            print(f"🏗️ Create {self.app_name} View")
            self.replace_line(
                self.index("# Create your views here.\n"),
                "def home(request):\n\treturn render(request, 'index.html')\n",
            )
            with open(self.views, "w") as f:
                f.write("".join(self.line_list))
                f.close()
        else:
            warn_stdout('"home" View is already created!')

    def create_urls(self):
        with open(self.urls, "w") as f:
            print(f"🔗 Create {self.app_name} Urls")
            content = [
                "from django.urls import path\n",
                "from . import views\n" "\n",
                "urlpatterns = [\n",
                "\tpath('', views.home)\n" "]\n",
            ]
            f.write("".join(content))
            f.close()

    def create_templates(self):
        print(f"🌐 Create {self.app_name} index.html")
        if not os.path.exists(self.__templates):
            os.mkdir(self.__templates)
        with open(rf"{self.__templates}{os.sep}index.html", "w") as f:
            content = [
                "<!DOCTYPE html>\n",
                '<html lang="en">\n',
                "<head>\n",
                '\t<meta charset="UTF-8">\n',
                "\t<title>Hello, Django-Start</title>\n",
                "</head>\n",
                "<body>\n",
                '\t<h1 style="text-align: center"> Hello, Django-Start</h1>\n',
                '\t<a href="https://github.com/islam-kamel/django-start"><h1 style="text-align: center">Project</h1></a>\n',  # noqa E501
                "</body>\n</html>",
            ]
            f.write("".join(content))
            f.close()
