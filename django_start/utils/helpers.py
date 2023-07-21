import os


def normalize_path(path):
    """
    Normalize path
    :param path: str    :return: str
    """
    return os.path.normpath(path)


def get_dirs(path, full_path=False):
    """
    Read all directories in a path
    and return a list of directories
    :param full_path:
    :param path: str
    :return: list
    """
    norm_path = normalize_path(path)

    # check if path exists
    if not os.path.exists(norm_path):
        raise FileNotFoundError(f"Path {path} not found")

    if full_path:
        return [os.path.join(norm_path, d) for d in os.listdir(norm_path) if os.path.isdir(os.path.join(norm_path, d))]
    else:
        return [d for d in os.listdir(norm_path) if os.path.isdir(os.path.join(norm_path, d))]


def find_specific_dir(path, dirs):
    """
    Find Specific Directory in a path
    :param path: str
    :param dirs: list
    :return: str or None
    """
    for directory in get_dirs(path):
        if directory not in dirs:
            continue

        return os.path.join(normalize_path(path), directory)


def read_file(path):
    """
    Read a file and return a list of lines
    :param path: str
    :return: list
    """
    # check if file exists
    if not os.path.isfile(normalize_path(path)):
        raise FileNotFoundError(f"File {path} not found")

    line_list = []

    with open(path, "r") as f:
        line_list = f.readlines()
        f.close()

    return line_list


def is_exist(path):
    """
    Check if path exists
    :param path: str
    :return: bool
    """
    return os.path.exists(normalize_path(path))
