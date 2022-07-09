import os
import sys
from rest_start import RestStart
from update_files import UpdateFile
import time


def start():
    return os.getcwd(), sys.argv


if __name__ == "__main__":
    workdir, arguments = start()
    data = {}
    try:
        data['core_name'] = arguments[1]
        data['app_name'] = arguments[2]
    except IndexError:
        print('Enter valid command < core_name app_name >')
        sys.exit(1)

    app = RestStart(
        workdir=workdir,
        **data
    )
    filemanager = UpdateFile(workdir=workdir, **data)

    print('Create Environment ✨')
    time.sleep(0.3)
    app.create_env()
    print('Install Django ⬇')
    time.sleep(0.3)
    app.install_dep()
    print('Create Templates 📝')
    app.create_templates()
    time.sleep(0.3)
    print('Update Settings 🔧')
    filemanager.update_settings()
    time.sleep(0.3)
    print('Update Project Urls ⬆')
    filemanager.update_urls()
    time.sleep(0.3)
    print('Create App View 📦')
    filemanager.create_view()
    time.sleep(0.3)
    print('Create App Urls 🔗')
    filemanager.create_urls()
