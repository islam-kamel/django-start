from pathlib import Path

from django_start.infrastructure.environment import VenvEnvironmentManager


def test_real_venv_creation(tmp_path: Path) -> None:
    manager = VenvEnvironmentManager()
    target = tmp_path / "venv"

    details = manager.create(target)

    assert details.root_path == target
    assert manager.exists(target)
    assert (target / "pyvenv.cfg").exists()
    assert details.python_executable.exists()
