from pathlib import Path
from unittest import mock

import pytest

from django_start.domain.errors import FileSystemError
from django_start.infrastructure.filesystem import LocalFileSystem


def test_exists(tmp_path: Path) -> None:
    fs = LocalFileSystem()
    assert not fs.exists(tmp_path / "nonexistent")
    assert fs.exists(tmp_path)


def test_is_empty_dir(tmp_path: Path) -> None:
    fs = LocalFileSystem()
    assert fs.is_empty_dir(tmp_path)

    file_path = tmp_path / "file.txt"
    file_path.write_text("content")
    assert not fs.is_empty_dir(tmp_path)
    assert not fs.is_empty_dir(file_path)
    assert not fs.is_empty_dir(tmp_path / "missing")


def test_is_empty_dir_exception(tmp_path: Path) -> None:
    fs = LocalFileSystem()
    with mock.patch("pathlib.Path.iterdir", side_effect=OSError("denied")):
        with pytest.raises(FileSystemError) as exc_info:
            fs.is_empty_dir(tmp_path)
    assert exc_info.value.operation == "is_empty_dir"


def test_read_text_utf8(tmp_path: Path) -> None:
    fs = LocalFileSystem()
    content = "hello world こんにちは"
    file_path = tmp_path / "file.txt"
    file_path.write_text(content, encoding="utf-8")
    assert fs.read_text(file_path) == content


def test_read_text_oserror(tmp_path: Path) -> None:
    fs = LocalFileSystem()
    with mock.patch("pathlib.Path.read_text", side_effect=OSError("denied")):
        with pytest.raises(FileSystemError) as exc_info:
            fs.read_text(tmp_path / "file.txt")
    assert exc_info.value.operation == "read_text"


def test_read_text_encoding_error(tmp_path: Path) -> None:
    fs = LocalFileSystem()
    file_path = tmp_path / "file.txt"
    file_path.write_bytes(b"\xff\xfe\x00\x00")
    with pytest.raises(FileSystemError) as exc_info:
        fs.read_text(file_path)
    assert exc_info.value.operation == "read_text"
    assert "decode" in str(exc_info.value)


def test_write_text_atomic_success(tmp_path: Path) -> None:
    fs = LocalFileSystem()
    file_path = tmp_path / "file.txt"
    content = "atomic content こんにちは"
    fs.write_text_atomic(file_path, content)
    assert file_path.read_text(encoding="utf-8") == content


def test_write_text_atomic_failure_safety(tmp_path: Path) -> None:
    fs = LocalFileSystem()
    file_path = tmp_path / "file.txt"
    file_path.write_text("original content")

    with mock.patch("os.replace", side_effect=OSError("simulated failure")):
        with pytest.raises(FileSystemError) as exc_info:
            fs.write_text_atomic(file_path, "new content")

    assert exc_info.value.operation == "write_text_atomic"
    # Destination must remain intact
    assert file_path.read_text() == "original content"
    # Temporary files should be cleaned up
    tmp_files = list(tmp_path.glob(".tmp-*"))
    assert not tmp_files


def test_write_text_atomic_unlink_oserror(tmp_path: Path) -> None:
    fs = LocalFileSystem()
    file_path = tmp_path / "file.txt"
    with mock.patch("os.replace", side_effect=OSError("simulated failure")):
        with mock.patch(
            "pathlib.Path.unlink", side_effect=OSError("unlink fail")
        ):
            with pytest.raises(FileSystemError):
                fs.write_text_atomic(file_path, "new content")


def test_write_text_atomic_generic_exception(tmp_path: Path) -> None:
    fs = LocalFileSystem()
    file_path = tmp_path / "file.txt"
    with mock.patch("os.replace", side_effect=ValueError("some error")):
        with pytest.raises(ValueError, match="some error"):
            fs.write_text_atomic(file_path, "new content")


def test_write_text_atomic_generic_exception_unlink_fail(
    tmp_path: Path,
) -> None:
    fs = LocalFileSystem()
    file_path = tmp_path / "file.txt"
    with mock.patch("os.replace", side_effect=ValueError("some error")):
        with mock.patch(
            "pathlib.Path.unlink", side_effect=OSError("unlink fail")
        ):
            with pytest.raises(ValueError, match="some error"):
                fs.write_text_atomic(file_path, "new content")


def test_create_directory(tmp_path: Path) -> None:
    fs = LocalFileSystem()
    nested_dir = tmp_path / "a" / "b"
    fs.create_directory(nested_dir)
    assert nested_dir.is_dir()

    # Idempotence check
    fs.create_directory(nested_dir)

    # Conflict check
    file_path = tmp_path / "file.txt"
    file_path.touch()
    with pytest.raises(FileSystemError) as exc_info:
        fs.create_directory(file_path)
    assert exc_info.value.operation == "create_directory"


def test_remove_tree_success(tmp_path: Path) -> None:
    fs = LocalFileSystem()
    nested_dir = tmp_path / "a" / "b"
    nested_dir.mkdir(parents=True)
    fs.remove_tree(tmp_path / "a")
    assert not (tmp_path / "a").exists()


def test_remove_tree_idempotence(tmp_path: Path) -> None:
    fs = LocalFileSystem()
    # Missing tree should not raise
    fs.remove_tree(tmp_path / "missing")


def test_remove_tree_guardrails(tmp_path: Path) -> None:
    fs = LocalFileSystem()

    # Refuse regular file
    file_path = tmp_path / "file.txt"
    file_path.touch()
    with pytest.raises(FileSystemError, match="not a directory"):
        fs.remove_tree(file_path)

    # Refuse symlink to directory
    dir_path = tmp_path / "dir"
    dir_path.mkdir()
    symlink_path = tmp_path / "symlink"
    try:
        symlink_path.symlink_to(dir_path, target_is_directory=True)
    except OSError:
        pass  # Symlinks might require privs on some OS
    else:
        with pytest.raises(FileSystemError, match="symlink"):
            fs.remove_tree(symlink_path)

    # Refuse root
    with pytest.raises(FileSystemError, match="root"):
        fs.remove_tree(Path(tmp_path.root))


def test_remove_tree_oserror(tmp_path: Path) -> None:
    fs = LocalFileSystem()
    dir_path = tmp_path / "dir"
    dir_path.mkdir()
    with mock.patch("shutil.rmtree", side_effect=OSError("denied")):
        with pytest.raises(FileSystemError) as exc_info:
            fs.remove_tree(dir_path)
    assert exc_info.value.operation == "remove_tree"


def test_write_text_atomic_mkstemp_failure(tmp_path: Path) -> None:
    fs = LocalFileSystem()
    file_path = tmp_path / "file.txt"

    with mock.patch("tempfile.mkstemp", side_effect=OSError("mkstemp fail")):
        with pytest.raises(FileSystemError) as exc_info:
            fs.write_text_atomic(file_path, "new content")
    assert exc_info.value.operation == "write_text_atomic"


def test_write_text_atomic_mkstemp_generic_exception(tmp_path: Path) -> None:
    fs = LocalFileSystem()
    file_path = tmp_path / "file.txt"

    with mock.patch(
        "tempfile.mkstemp", side_effect=ValueError("mkstemp value error")
    ):
        with pytest.raises(ValueError):
            fs.write_text_atomic(file_path, "new content")
