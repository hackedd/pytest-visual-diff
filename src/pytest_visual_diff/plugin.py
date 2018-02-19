import os

from pytest_visual_diff.capture import get_screenshot_path  # noqa: F401
from pytest_visual_diff.capture import save_screenshot  # noqa: F401
from pytest_visual_diff.capture import image_to_base64
from pytest_visual_diff.compare import check_reference_screenshot  # noqa: F401


def pytest_addoption(parser):
    default_screenshot_path_format = os.path.join(
        "{directory}", "screenshots", "{module}", "{name}.png"
    )
    parser.addini("screenshot_path_format",
                  help="controls where the reference screenshots are stored.",
                  default=default_screenshot_path_format)

    parser.addoption("--update-reference-screenshots", action="store_true",
                     help="update (or create) reference screenshots.")


def pytest_selenium_capture_debug(item,  extra):
    screenshots = getattr(item, "_pytest_visual_diff", None)
    if not screenshots:
        return

    pytest_html = item.config.pluginmanager.getplugin("html")
    if not pytest_html:
        return

    for images in screenshots:
        suffix = " " + images["name"] if images["name"] else ""

        # XXX: pytest-html expects the content to be a string, not bytes.
        data = image_to_base64(images["expected"]).decode("ascii")
        extra.append(pytest_html.extras.image(data, "Expected" + suffix))

        data = image_to_base64(images["actual"]).decode("ascii")
        extra.append(pytest_html.extras.image(data, "Actual" + suffix))
