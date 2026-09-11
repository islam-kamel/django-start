def test_django_start_importable():
    import django_start

    assert django_start is not None


def test_djstartlib_importable():
    import djstartlib

    assert djstartlib is not None


def test_legacy_nested_imports():
    import djstartlib.main
    import djstartlib.version
    import djstartlib.models
    import djstartlib.models.app_manager
    import djstartlib.models.project_manager
    import djstartlib.models.djstart_interface
    import djstartlib.models.utils
    import djstartlib.models.utils.environment
    import djstartlib.models.utils.helper

    assert djstartlib.main is not None
