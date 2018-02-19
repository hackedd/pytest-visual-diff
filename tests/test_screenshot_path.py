def test_screenshot_path_default_format(testdir):
    testdir.makepyfile(test_module="""
    import os

    directory = r"{directory}"

    def test_function(get_screenshot_path):
        expected_path = os.path.join(directory, "screenshots",
                                     "test_module",
                                     "test_function.png")
        assert get_screenshot_path() == expected_path

        expected_path = os.path.join(directory, "screenshots",
                                     "test_module",
                                     "test_function__suffix.png")
        assert get_screenshot_path("suffix") == expected_path
    """.format(directory=testdir.tmpdir))
    result = testdir.runpytest()
    result.assert_outcomes(passed=1)


def test_screenshot_path_ini_format(testdir):
    testdir.makefile(".ini", pytest="""
    [pytest]
    screenshot_path_format = /tmp/{name}.png
    """)

    testdir.makepyfile(test_module="""
    def test_function(get_screenshot_path):
        expected_path = "/tmp/test_function.png"
        assert get_screenshot_path() == expected_path

        expected_path = "/tmp/test_function__suffix.png"
        assert get_screenshot_path("suffix") == expected_path
    """.format(directory=testdir.tmpdir))
    result = testdir.runpytest()
    result.assert_outcomes(passed=1)
