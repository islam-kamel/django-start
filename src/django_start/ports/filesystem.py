"""
Filesystem port for Django-Start 2.0.

Provides an isolated boundary for safe, UTF-8, atomic filesystem operations.
"""

from pathlib import Path
from typing import Protocol


class FileSystem(Protocol):
    """
    Port protocol for safe filesystem operations.
    """

    def exists(self, path: Path) -> bool:
        """Check if a file or directory exists."""
        ...

    def is_empty_dir(self, path: Path) -> bool:
        """Check if a directory is empty."""
        ...

    def read_text(self, path: Path) -> str:
        """Read text from a file, strictly enforcing UTF-8 encoding."""
        ...

    def write_text_atomic(self, path: Path, content: str) -> None:
        """
        Write text to a file atomically, strictly enforcing UTF-8 encoding.

        Implementations should write to a temporary sibling file and replace the target atomically
        to prevent truncated or corrupted files on crash.
        """
        ...

    def create_directory(self, path: Path) -> None:
        """Create a directory and any missing parent directories."""
        ...

    def remove_tree(self, path: Path) -> None:
        """
        Remove a directory tree safely.

        Safety Invariant: This method may only be used for cleaning up resources owned
        or created by the current Django-Start transaction (e.g., staging directories
        during rollback). It does not authorize recursive deletion of arbitrary user directories.
        """
        ...
