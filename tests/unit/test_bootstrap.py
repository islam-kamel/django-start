def test_package_entry_points_importable():
    """Verify djstartlib entry points are importable and callables resolve
    without crashing.
    """
    import djstartlib
    import djstartlib.main
    import djstartlib.version

    assert hasattr(djstartlib.main, "main")
    assert callable(djstartlib.main.main)

    assert hasattr(djstartlib.version, "main")
    assert callable(djstartlib.version.main)
