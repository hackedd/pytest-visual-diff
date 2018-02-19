import io
import os
from base64 import b64encode
from operator import itemgetter

import pytest
from PIL import Image
from selenium.webdriver.remote.webelement import WebElement


@pytest.fixture
def get_screenshot_path(request):
    def _get_screenshot_path(name_suffix=None):
        path_format = request.config.getini("screenshot_path_format")

        directory = request.fspath.dirpath()
        module = request.fspath.purebasename
        name = request.function.__name__

        if name_suffix:
            name += "__" + name_suffix

        return path_format.format(directory=directory, module=module,
                                  name=name, suffix=name_suffix)

    return _get_screenshot_path


def image_from_png(png_data):
    fp = io.BytesIO(png_data)
    image = Image.open(fp)

    # Some browser create screenshots with alpha channel, some without.
    # We put always work _with_ one, for consistency.
    if image.mode != "RGBA":
        image = image.convert("RGBA")

    return image


def get_element_screenshot(driver, element):
    """Create a screenshot of an element by taking a screenshot of the full
    screen and cropping it to the selected element. Returns an Image object.

    There is a `WebElement.screenshot_as_png`, but most drivers do not
    implement it (https://github.com/SeleniumHQ/selenium/issues/912), and
    PhantomJS returns the full screen.

    """
    image = image_from_png(driver.get_screenshot_as_png())
    location, size = element.location, element.size
    return image.crop((
        int(location["x"]),
        int(location["y"]),
        int(location["x"] + size["width"]),
        int(location["y"] + size["height"])
    ))


def get_multiple_element_screenshot(driver, elements):
    """Create a screenshot of multiple elements by taking a screenshot of the
    full screen and cropping it to only contain the selected elements.
    Returns an Image object.

    """
    element_bounds = []
    for element in elements:
        location, size = element.location, element.size
        element_bounds.append((
            int(location["x"]),
            int(location["y"]),
            int(location["x"] + size["width"]),
            int(location["y"] + size["height"])
        ))

    left = min(map(itemgetter(0), element_bounds))
    top = min(map(itemgetter(1), element_bounds))
    right = max(map(itemgetter(2), element_bounds))
    bottom = max(map(itemgetter(3), element_bounds))

    combined_image = Image.new("RGBA", (right - left, bottom - top))

    source_image = image_from_png(driver.get_screenshot_as_png())
    for element, bounds in zip(elements, element_bounds):
        element_image = source_image.crop(bounds)
        combined_image.paste(element_image,
                             (bounds[0] - left, bounds[1] - top))

    return combined_image


def get_screenshot(driver, element):
    if isinstance(element, WebElement):
        assert element.is_displayed()
        return get_element_screenshot(driver, element)

    assert all(e.is_displayed() for e in element)
    return get_multiple_element_screenshot(driver, element)


def save_image(image, filename):
    directory = os.path.dirname(filename)
    if not os.path.exists(directory):
        os.makedirs(directory)
    image.save(filename)


def image_to_base64(image):
    with io.BytesIO() as buffer:
        image.save(buffer, "PNG")
        return b64encode(buffer.getvalue())


@pytest.fixture()
def save_screenshot(request, driver, get_screenshot_path):
    """Save a screenshot of one or more elements."""

    def _save_screenshot(element, name=None):
        filename = get_screenshot_path(name)
        image = get_screenshot(driver, element)
        save_image(image, filename)
        return filename

    return _save_screenshot
