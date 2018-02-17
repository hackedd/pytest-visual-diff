import os

import pytest
from PIL import Image

from pytest_visual_diff.capture import get_screenshot, save_image


def compute_squared_error(image_a, image_b):
    assert image_a.size == image_b.size
    assert image_a.mode == image_b.mode

    squared_error = 0
    for ca, cb in zip(image_a.getdata(), image_b.getdata()):
        for a, b in zip(ca, cb):
            d = a / 255.0 - b / 255.0
            squared_error += d * d

    return squared_error / len(image_a.getbands())


def compare_images(expected, actual, fuzz=0.0):
    """Compare two images. Returns true if the images are the same. The
    optional `fuzz` parameter can be used to make the comparison less strict.
    With `fuzz` set to zero (the default) the images need to be identical,
    when set to one (the maximum), any two images will compare equal.

    """
    error = compute_squared_error(expected, actual)
    maximum_acceptable_error = expected.width * expected.height * fuzz
    return error <= maximum_acceptable_error


@pytest.fixture
def check_reference_screenshot(request, driver, get_screenshot_path):
    """Compare an element on the page to a previously created screenshot."""

    update_reference = request.config.getoption(
        "--update-reference-screenshots"
    )

    def _check_reference_screenshot(element, name=None, fuzz=0.0):
        actual = get_screenshot(driver, element)

        # TODO: Record each screenshot for pytest_runtest_makereport
        # Where? Store as attributes on the test?

        filename = get_screenshot_path(name)
        if update_reference:
            save_image(actual, filename)
            pytest.skip("Updated reference image %s" % filename)

        if not os.path.exists(filename):
            pytest.fail("Unable to check reference image because "
                        "%s does not exist" % filename)

        expected = Image.open(filename)
        if not compare_images(expected, actual, fuzz):
            pytest.fail("Element is different from reference image")

    return _check_reference_screenshot
