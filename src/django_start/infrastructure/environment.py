"""
Virtual environment management for Django-Start 2.0.
"""

import os
import shutil
import venv
from pathlib import Path
from typing import final

from django_start.domain.errors import EnvironmentCreationError
from django_start.ports.environment import (
    EnvironmentDetails,
    EnvironmentManager,
)


def _get_env_paths(root: Path, is_windows: bool) -> EnvironmentDetails:
    """
    Deterministic private helper to compute environment paths across platforms.
    """
    if is_windows:
        scripts = root / "Scripts"
        python = scripts / "python.exe"
    else:
        scripts = root / "bin"
        python = scripts / "python"

    return EnvironmentDetails(
        root_path=root,
        python_executable=python,
        scripts_path=scripts,
    )


@final
class VenvEnvironmentManager(EnvironmentManager):
    """
    Manages virtual environments using the standard library `venv`.
    """

    def create(self, target_dir: Path) -> EnvironmentDetails:
        if target_dir.exists():
            raise EnvironmentCreationError(
                f"Target environment directory already exists: {target_dir}"
            )

        builder = venv.EnvBuilder(with_pip=True, clear=False)
        try:
            builder.create(target_dir)
        except Exception as exc:
            # If the creation fails partway, clean up the partially
            # created target
            cleanup_failed = False
            cleanup_exc = None
            if target_dir.exists():
                try:
                    shutil.rmtree(target_dir)
                except OSError as err:
                    cleanup_failed = True
                    cleanup_exc = err

            msg = f"Failed to create virtual environment: {exc}"
            if cleanup_failed:
                msg += (
                    ". Cleanup also failed, target directory may still "
                    f"exist: {cleanup_exc}"
                )
            raise EnvironmentCreationError(msg) from exc

        return _get_env_paths(target_dir, is_windows=(os.name == "nt"))

    def exists(self, target_dir: Path) -> bool:
        if not target_dir.is_dir():
            return False

        cfg_exists = (target_dir / "pyvenv.cfg").is_file()
        paths = _get_env_paths(target_dir, is_windows=(os.name == "nt"))
        python_exists = paths.python_executable.is_file()

        return cfg_exists and python_exists
