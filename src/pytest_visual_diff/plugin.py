from pytest_visual_diff.capture import *  # noqa: F401,F403
from pytest_visual_diff.compare import *  # noqa: F401,F403


def pytest_addoption(parser):
    parser.addini("screenshot_path_format", help="",
                  default="{directory}/screenshots/{module}/{name}.png")

    parser.addoption("--update-reference-screenshots", action="store_true",
                     help="update (or create) reference screenshots")
