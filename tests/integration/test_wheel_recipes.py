"""Integration smoke test for BuiltinRecipeProvider."""


def test_wheel_import_smoke():
    """
    In a real wheel installation, we want to ensure
    importlib.resources can find the JSON and template files.

    This integration test just exercises list_metadata() to
    prove the anchor works without assuming an editable install.
    The real test happens in the CI workflow when it actually
    installs the wheel in an isolated venv.
    """
    from django_start.infrastructure.builtin_recipes import (
        BuiltinRecipeProvider,
    )

    provider = BuiltinRecipeProvider()
    metadata = provider.list_metadata()
    assert len(metadata) == 4
