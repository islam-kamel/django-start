import os
import sys
import venv


class VirtualEnv:
    def __init__(self, venv_path='env'):
        self.__venv_path = venv_path

    @property
    def venv_path(self):
        return self.__venv_path


    def isvirtualenv(self):
        return sys.prefix != sys.base_prefix


    def findfile(self, startdir, pattern):
        for root, dirs, files in os.walk(startdir):
            for name in files:
                if name.find(pattern) >= 0:
                    return root + os.sep + name

        return None

    def create_env(self):

        if self.isvirtualenv():
            print('Already in virtual environment.')
        else:
            if self.findfile(os.getcwd(), 'activate') is None:
                print('No virtual environment found. Creating one.')
                env = venv.EnvBuilder(with_pip=True)
                env.create(self.venv_path)
            else:
                print('Not in virtual environment. Virtual environment directory found.')
            os.environ['PATH'] = os.path.dirname(
                self.findfile(os.getcwd(), 'activate')) + os.pathsep + os.environ['PATH']
            sys.path.insert(1, os.path.dirname(
                self.findfile(self.venv_path, 'easy_install.py')))
