from pathlib import Path
from unittest import mock

import pytest

from django_start.domain.errors import EnvironmentCreationError
from django_start.infrastructure.environment import (
    VenvEnvironmentManager,
    _get_env_paths,
)


def test_get_env_paths_posix() -> None:
    root = Path("/fake/env")
    paths = _get_env_paths(root, is_windows=False)
    assert paths.root_path == root
    assert paths.scripts_path == root / "bin"
    assert paths.python_executable == root / "bin" / "python"


def test_get_env_paths_windows() -> None:
    root = Path("C:/fake/env")
    paths = _get_env_paths(root, is_windows=True)
    assert paths.root_path == root
    assert paths.scripts_path == root / "Scripts"
    assert paths.python_executable == root / "Scripts" / "python.exe"


def test_exists_missing(tmp_path: Path) -> None:
    manager = VenvEnvironmentManager()
    assert not manager.exists(tmp_path / "missing")


def test_exists_random_dir(tmp_path: Path) -> None:
    manager = VenvEnvironmentManager()
    assert not manager.exists(tmp_path)


def test_exists_valid(tmp_path: Path) -> None:
    manager = VenvEnvironmentManager()

    (tmp_path / "pyvenv.cfg").touch()

    paths = _get_env_paths(tmp_path, is_windows=True)
    paths.python_executable.parent.mkdir(parents=True, exist_ok=True)
    paths.python_executable.touch()

    paths_posix = _get_env_paths(tmp_path, is_windows=False)
    paths_posix.python_executable.parent.mkdir(parents=True, exist_ok=True)
    paths_posix.python_executable.touch()

    # The existence check uses `os.name == "nt"`, but our dummy
    # setup populated both
    assert manager.exists(tmp_path)


def test_create_rejects_existing_target(tmp_path: Path) -> None:
    manager = VenvEnvironmentManager()
    with pytest.raises(EnvironmentCreationError, match="already exists"):
        manager.create(tmp_path)


def test_create_cleans_up_on_failure(tmp_path: Path) -> None:
    manager = VenvEnvironmentManager()
    target = tmp_path / "venv"

    # Simulate a failure inside builder.create
    with mock.patch(
        "venv.EnvBuilder.create", side_effect=Exception("mocked failure")
    ) as mock_create:

        def side_effect_create(path):
            Path(path).mkdir()  # simulate partial creation
            raise Exception("mocked failure")

        mock_create.side_effect = side_effect_create

        with pytest.raises(EnvironmentCreationError):
            manager.create(target)

    # The partial creation should have been cleaned up
    assert not target.exists()


def test_create_cleans_up_on_failure_rmtree_oserror(tmp_path: Path) -> None:
    manager = VenvEnvironmentManager()
    target = tmp_path / "venv"

    with mock.patch(
        "venv.EnvBuilder.create", side_effect=Exception("fail")
    ) as mock_create:

        def side_effect_create(path):
            Path(path).mkdir()  # simulate partial creation
            raise Exception("fail")

        mock_create.side_effect = side_effect_create

        with mock.patch("shutil.rmtree", side_effect=OSError("rm fail")):
            with pytest.raises(EnvironmentCreationError):
                manager.create(target)
