"""
Local filesystem adapter for Django-Start 2.0.
"""

import os
import shutil
import tempfile
from pathlib import Path
from typing import final

from django_start.domain.errors import FileSystemError
from django_start.ports.filesystem import FileSystem


@final
class LocalFileSystem(FileSystem):
    """
    Implements local filesystem operations with safe atomic constraints.
    """

    def exists(self, path: Path) -> bool:
        return path.exists()

    def is_empty_dir(self, path: Path) -> bool:
        if not path.exists():
            return False
        if not path.is_dir():
            return False
        try:
            return not any(path.iterdir())
        except OSError as exc:
            raise FileSystemError(
                f"Failed to read directory: {exc}",
                operation="is_empty_dir",
                path=str(path),
            ) from exc

    def read_text(self, path: Path) -> str:
        try:
            return path.read_text(encoding="utf-8")
        except OSError as exc:
            raise FileSystemError(
                f"Failed to read file: {exc}",
                operation="read_text",
                path=str(path),
            ) from exc
        except UnicodeError as exc:
            raise FileSystemError(
                f"Failed to decode file as UTF-8: {exc}",
                operation="read_text",
                path=str(path),
            ) from exc

    def write_text_atomic(self, path: Path, content: str) -> None:
        parent = path.parent
        self.create_directory(parent)

        tmp_path = None
        try:
            fd, tmp_name = tempfile.mkstemp(
                dir=parent, text=True, prefix=".tmp-"
            )
            tmp_path = Path(tmp_name)

            with open(fd, "w", encoding="utf-8") as f:
                f.write(content)
                f.flush()
                os.fsync(f.fileno())

            os.replace(tmp_path, path)
        except OSError as exc:
            raise FileSystemError(
                f"Failed atomic write: {exc}",
                operation="write_text_atomic",
                path=str(path),
            ) from exc
        finally:
            if tmp_path and tmp_path.exists():
                try:
                    tmp_path.unlink()
                except OSError:
                    pass

    def create_directory(self, path: Path) -> None:
        try:
            path.mkdir(parents=True, exist_ok=True)
        except OSError as exc:
            raise FileSystemError(
                f"Failed to create directory: {exc}",
                operation="create_directory",
                path=str(path),
            ) from exc

    def remove_tree(self, path: Path) -> None:
        if not path.exists():
            return

        if not path.is_dir() or path.is_symlink():
            raise FileSystemError(
                "Target is not a directory or is a symlink",
                operation="remove_tree",
                path=str(path),
            )

        # Protect against removing root or similar dangerous paths
        resolved = path.resolve()
        if resolved == resolved.parent:
            raise FileSystemError(
                "Refusing to remove filesystem root",
                operation="remove_tree",
                path=str(path),
            )

        try:
            shutil.rmtree(path)
        except OSError as exc:
            raise FileSystemError(
                f"Failed to remove tree: {exc}",
                operation="remove_tree",
                path=str(path),
            ) from exc
