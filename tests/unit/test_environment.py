from djstartlib.models.utils.environment import Environment


def test_environment_initialization(monkeypatch, tmp_path):
    """Characterize BC-ENV-01: Environment tracks app, project, workdir, PYTHONEXEC, and DJANGOADMIN."""
    monkeypatch.setenv("PYTHONEXEC", "/custom/bin/python")
    monkeypatch.setenv("DJANGOADMIN", "/custom/bin/django-admin")
    monkeypatch.chdir(tmp_path)

    env = Environment(app="blog", project="mysite")
    assert env.get_app_name() == "blog"
    assert env.get_project_name() == "mysite"
    assert env.get_workdir() == str(tmp_path)
    assert env.get_exec() == "/custom/bin/python"
    assert env.get_django_admin() == "/custom/bin/django-admin"
    assert env.line_list == []


def test_environment_file_operations(tmp_path):
    """Characterize BC-ENV-02: Environment reads, modifies, and writes files."""
    sample_file = tmp_path / "sample.txt"
    sample_file.write_text("line 1\nline 2\nline 3\n", encoding="utf-8")

    env = Environment()
    lines = env.read_file(str(sample_file))
    assert lines == ["line 1\n", "line 2\n", "line 3\n"]
    assert env.index("line 2\n") == 1

    env.insert_line("line 2\n", "line 1.5\n")
    assert env.line_list == ["line 1\n", "line 1.5\n", "line 2\n", "line 3\n"]

    env.replace_line(2, "line 2 updated\n")
    assert env.line_list == ["line 1\n", "line 1.5\n", "line 2 updated\n", "line 3\n"]

    output_file = tmp_path / "output.txt"
    env.write(str(output_file))
    assert output_file.read_text(encoding="utf-8") == "line 1\nline 1.5\nline 2 updated\nline 3\n"
