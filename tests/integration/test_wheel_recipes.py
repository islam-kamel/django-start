"""Integration smoke test for BuiltinRecipeProvider on a real wheel."""

import os
import subprocess
import sys
from pathlib import Path

import pytest


def test_isolated_wheel_smoke(tmp_path):
    """
    Builds the wheel, installs it in a fresh virtualenv,
    and runs a script from outside the repo to prove
    resource loading works.
    """
    repo_root = Path(__file__).resolve().parent.parent.parent

    # 1. Build the wheel
    subprocess.run(
        [sys.executable, "-m", "build", "--wheel", str(repo_root)],
        check=True,
        capture_output=True,
    )

    dist_dir = repo_root / "dist"
    wheels = list(dist_dir.glob("*.whl"))
    assert wheels, "Wheel was not built"
    wheel_path = max(wheels, key=os.path.getctime)

    # 2. Create a fresh venv
    venv_dir = tmp_path / "venv"
    subprocess.run(
        [sys.executable, "-m", "venv", str(venv_dir)],
        check=True,
    )

    if os.name == "nt":
        venv_python = venv_dir / "Scripts" / "python.exe"
    else:
        venv_python = venv_dir / "bin" / "python"

    # 3. Install wheel
    subprocess.run(
        [str(venv_python), "-m", "pip", "install", str(wheel_path)],
        check=True,
        capture_output=True,
    )

    # 4. Write validation script
    script = """
import sys
from django_start.infrastructure.builtin_recipes import BuiltinRecipeProvider
from django_start.domain.config import Profile
from django_start.domain.policies import BUILTIN_REGISTRY

def main():
    provider = BuiltinRecipeProvider()
    meta = provider.list_metadata()
    if len(meta) != 4:
        sys.exit(f"Expected 4 profiles, got {len(meta)}")

    release = BUILTIN_REGISTRY.releases[0]
    bundle = provider.get(Profile.STANDARD, release)

    if not bundle.templates:
        sys.exit("Templates are empty")

if __name__ == "__main__":
    main()
"""
    script_path = tmp_path / "validate.py"
    script_path.write_text(script)

    # 5. Run from tmp_path (outside repo)
    result = subprocess.run(
        [str(venv_python), str(script_path)],
        cwd=str(tmp_path),
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        pytest.fail(f"Wheel validation failed: {result.stderr}")


def test_isolated_sdist_smoke(tmp_path):
    """
    Builds the sdist, installs it in a fresh virtualenv,
    and runs a script from outside the repo to prove
    resource loading works.
    """
    repo_root = Path(__file__).resolve().parent.parent.parent

    # 1. Build the sdist
    subprocess.run(
        [sys.executable, "-m", "build", "--sdist", str(repo_root)],
        check=True,
        capture_output=True,
    )

    dist_dir = repo_root / "dist"
    sdists = list(dist_dir.glob("*.tar.gz"))
    assert sdists, "Sdist was not built"
    sdist_path = max(sdists, key=os.path.getctime)

    # 2. Create a fresh venv
    venv_dir = tmp_path / "venv"
    subprocess.run(
        [sys.executable, "-m", "venv", str(venv_dir)],
        check=True,
    )

    if os.name == "nt":
        venv_python = venv_dir / "Scripts" / "python.exe"
    else:
        venv_python = venv_dir / "bin" / "python"

    # 3. Install sdist
    subprocess.run(
        [str(venv_python), "-m", "pip", "install", str(sdist_path)],
        check=True,
        capture_output=True,
    )

    # 4. Write validation script
    script = """
import sys
from django_start.infrastructure.builtin_recipes import BuiltinRecipeProvider
from django_start.domain.config import Profile
from django_start.domain.policies import BUILTIN_REGISTRY

def main():
    provider = BuiltinRecipeProvider()
    meta = provider.list_metadata()
    if len(meta) != 4:
        sys.exit(f"Expected 4 profiles, got {len(meta)}")

    release = BUILTIN_REGISTRY.releases[0]
    bundle = provider.get(Profile.STANDARD, release)

    if not bundle.templates:
        sys.exit("Templates are empty")

if __name__ == "__main__":
    main()
"""
    script_path = tmp_path / "validate.py"
    script_path.write_text(script)

    # 5. Run from tmp_path (outside repo)
    result = subprocess.run(
        [str(venv_python), str(script_path)],
        cwd=str(tmp_path),
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        pytest.fail(f"Sdist validation failed: {result.stderr}")
