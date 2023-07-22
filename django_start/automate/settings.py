import os

from django_start.utils.helpers import normalize_path, is_exist


class Settings:
    """
    Settings class for configure django project
    """

    def __init__(self, *args, **kwargs):
        self.working_dir = normalize_path(os.path.join(kwargs.get("working_dir", os.getcwd())))


class AppSettings(Settings):
    """
    AppSettings class for configure django app
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.app_name = kwargs.get("app_name")
        self.app_dir = os.path.join(self.working_dir, self.app_name)

        # check if exist dir with app_name
        if is_exist(self.app_dir):
            raise FileExistsError(f"App with name {self.app_name} already exist")


class ProjectSettings(Settings):
    """
    ProjectSettings class for configure django project
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.project_name = kwargs.get("project_name")
        self.project_dir = os.path.join(self.working_dir, self.project_name)

        # check if exist dir with project_name
        if is_exist(self.project_dir):
            raise FileExistsError(f"Project with name {self.project_name} already exist")
