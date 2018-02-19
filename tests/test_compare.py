import pytest
from PIL import Image

from pytest_visual_diff.compare import compare_images, compute_squared_error

from helpers import expected_failure_with_chrome


@pytest.fixture
def red_image(open_image):
    return open_image("red")


@pytest.fixture
def blue_image(open_image):
    return open_image("blue")


@pytest.fixture
def green_blue_image(open_image):
    return open_image("green-blue")


def test_pixel_changes():
    # This tests starts out with two completely black images, then flips
    # individual pixels in one of them from black to white. Because this
    # makes the pixels maximally different, the squared error should increase
    # by exactly one for each successive change.
    a = Image.new("RGB", (10, 10))
    b = Image.new("RGB", (10, 10))
    assert compute_squared_error(a, b) == 0
    for i in range(1, 10):
        b.putpixel((i, 0), (255, 255, 255))
        assert compute_squared_error(a, b) == i


def test_same_image_is_equal(red_image):
    assert compare_images(red_image, red_image)

    copied = red_image.copy()
    assert compare_images(red_image, copied)


def test_different_images(red_image, blue_image):
    assert not compare_images(red_image, blue_image)


def test_different_images_fuzz(red_image, blue_image):
    # One image is completely red, the other is completely blue. The
    # difference between those about half (two out of four channels), so
    # setting the fuzz factor above that should accept them as equal.
    assert not compare_images(red_image, blue_image, 0.3)
    assert compare_images(red_image, blue_image, 0.6)


@expected_failure_with_chrome
def test_check_screenshot(colored_divs_server, testdir,
                          copy_image, selenium_args):
    testdir.makepyfile(test_module="""
    def test_one_element(driver, check_reference_screenshot):
        driver.get("{server_url}")
        element = driver.find_element_by_id("red")
        check_reference_screenshot(element)

    def test_multiple_elements(driver, check_reference_screenshot):
        driver.get("{server_url}")
        green = driver.find_element_by_id("green")
        blue = driver.find_element_by_id("blue")
        check_reference_screenshot((green, blue))
    """.format(server_url=colored_divs_server.url))

    copy_image("red", "test_module", "test_one_element")
    copy_image("green-blue", "test_module", "test_multiple_elements")

    result = testdir.runpytest(*selenium_args)
    result.assert_outcomes(passed=2)


def test_check_screenshot_changed(colored_divs_server, testdir,
                                  copy_image, selenium_args):
    testdir.makepyfile(test_module="""
    def test_one_element(driver, check_reference_screenshot):
        driver.get("{server_url}")
        element = driver.find_element_by_id("red")
        check_reference_screenshot(element)
    """.format(server_url=colored_divs_server.url))

    copy_image("blue", "test_module", "test_one_element")

    result = testdir.runpytest(*selenium_args)
    result.assert_outcomes(failed=1)
    result.stdout.fnmatch_lines([
        "*Failed: Element is different from reference image*"
    ])


def test_check_screenshot_missing(colored_divs_server, testdir, selenium_args):
    testdir.makepyfile(test_module="""
    def test_one_element(driver, check_reference_screenshot):
        driver.get("{server_url}")
        element = driver.find_element_by_id("red")
        check_reference_screenshot(element)
    """.format(server_url=colored_divs_server.url))

    result = testdir.runpytest(*selenium_args)
    result.assert_outcomes(failed=1)
    result.stdout.fnmatch_lines([
        "*Failed: Unable to check reference image*"
    ])


def test_update_screenshots(colored_divs_server, testdir,
                            copy_image, selenium_args):
    testdir.makepyfile(test_module="""
    def test_one_element(driver, check_reference_screenshot):
        driver.get("{server_url}")
        element = driver.find_element_by_id("red")
        check_reference_screenshot(element)
    """.format(server_url=colored_divs_server.url))

    result = testdir.runpytest("--update-reference-screenshots",
                               *selenium_args)
    result.assert_outcomes(skipped=1)

    screenshot = testdir.tmpdir.join("screenshots", "test_module",
                                     "test_one_element.png")
    assert screenshot.check(file=True)

    # Run the same tests a second time, to make sure they pass now.
    result = testdir.runpytest(*selenium_args)
    result.assert_outcomes(passed=1)
