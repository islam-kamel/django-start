import pytest


@pytest.fixture
def isolated_workdir(tmp_path, monkeypatch):
    """Hermetic working directory fixture ensuring tests do not mutate developer filesystem."""
    monkeypatch.chdir(tmp_path)
    return tmp_path
