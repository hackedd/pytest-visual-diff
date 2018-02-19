from pytest_visual_diff.capture import (get_element_screenshot,
                                        get_multiple_element_screenshot)

from helpers import expected_failure_with_chrome

RED = (255, 0, 0, 255)
GREEN = (0, 128, 0, 255)
BLUE = (0, 0, 255, 255)
TRANSPARENT = (0, 0, 0, 0)


@expected_failure_with_chrome
def test_get_element_screenshot(colored_divs_server, driver):
    driver.get(colored_divs_server.url)

    element = driver.find_element_by_id("red")
    image = get_element_screenshot(driver, element)

    # Check that the screenshot is the same size as the element captured
    assert image.size == (100, 100)
    assert image.mode == "RGBA"

    # Check the color of a few pixels to ensure we did not just get a
    # blank image.
    assert image.getpixel((0, 0)) == RED
    assert image.getpixel((50, 50)) == RED
    assert image.getpixel((99, 99)) == RED


@expected_failure_with_chrome
def test_get_multiple_elements_screenshot(colored_divs_server, driver):
    driver.get(colored_divs_server.url)

    # Capture the green and blue squares, which partially overlap:
    green = driver.find_element_by_id("green")
    blue = driver.find_element_by_id("blue")
    image = get_multiple_element_screenshot(driver, (green, blue))

    # Check that the screenshot is the same size as the elements captured
    # combined.
    assert image.size == (150, 150)
    assert image.mode == "RGBA"

    # Check the color of a few pixels to ensure we did not just get a
    # blank image, and the elements have been composited correctly.
    assert image.getpixel((0, 0)) == GREEN
    assert image.getpixel((49, 49)) == GREEN
    assert image.getpixel((50, 50)) == BLUE
    assert image.getpixel((149, 149)) == BLUE
    assert image.getpixel((140, 10)) == TRANSPARENT
    assert image.getpixel((10, 140)) == TRANSPARENT


def test_save_screenshot(colored_divs_server, testdir, selenium_args):
    testdir.makepyfile(test_module="""
    def test_one_element(driver, save_screenshot):
        driver.get("{server_url}")
        element = driver.find_element_by_id("red")
        assert save_screenshot(element)

    def test_multiple_elements(driver, save_screenshot):
        driver.get("{server_url}")
        green = driver.find_element_by_id("green")
        blue = driver.find_element_by_id("blue")
        assert save_screenshot((green, blue))
    """.format(server_url=colored_divs_server.url))

    result = testdir.runpytest(*selenium_args)
    result.assert_outcomes(passed=2)

    for test in ("test_one_element", "test_multiple_elements"):
        filename = testdir.tmpdir.join("screenshots", "test_module",
                                       test + ".png")
        assert filename.check(file=True)
