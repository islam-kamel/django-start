import os

from models.utils import Environment
from models.utils.hellper import (
    build_view_func,
    build_views_urls,
    executable_python_command,
    generate_html,
    print_status,
    warn_stdout,
)


class AppManager(Environment):
    def __init__(self, *args, **kwargs):
        super().__init__(**kwargs)
        self.test()

    @property
    def templates_path(self) -> str:
        return self.join_path("templates")

    @property
    def views_path(self) -> str:
        return self.join_path("views.py")

    @property
    def urls_path(self) -> str:
        return self.join_path("urls.py")

    def create_app(self) -> None:
        print_status(f"\U00002728 Create '{self.app_name}' App...")

        if self.app_name not in os.listdir(self.base_dir()):
            executable_python_command(f"manage.py startapp {self.app_name}")
        else:
            warn_stdout(f'"{self.app_name}" already exist!')

    def create_urls(self) -> None:
        print_status(f"\U0001F517 Create {self.app_name} URLs...")

        block_of_code = build_views_urls().substitute(view_name="home")
        self.write(self.urls_path, value=block_of_code)

    def create_templates(self) -> None:
        print_status(f"\U0001F389 Generate '{self.app_name}' Index Page...")

        self.create_templates_dir()
        self.create_html_page()

    def create_templates_dir(self) -> None:
        if not os.path.exists(self.templates_path):
            os.mkdir(self.templates_path)

    def create_html_page(self) -> None:
        app_templates_path = os.path.join(self.templates_path, self.app_name)
        html_page_name = os.path.join(app_templates_path, "index.html")

        if not os.path.exists(app_templates_path):
            os.mkdir(app_templates_path)
            self.write(html_page_name, value=generate_html())
        else:
            warn_stdout("Index.html is Already exists.")

    def update_view(self) -> None:
        print_status(f"\U0001F304 Create '{self.app_name}' Views...")

        self.read_file(self.views_path)
        if "# Create your views here.\n" in self.line_list:
            block_of_code = build_view_func().substitute(
                app_name=self.app_name, html_file="index.html"
            )
            self.replace_line(
                self.index("# Create your views here.\n"), block_of_code
            )
            self.write(self.views_path)

        else:
            warn_stdout('"home" View is Exists!')
