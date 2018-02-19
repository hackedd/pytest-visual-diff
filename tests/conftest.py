import inspect

import py
import pytest
from PIL import Image
from selenium import webdriver

pytest_plugins = ["pytester"]
images_dir = py.path.local(__file__).join("..", "images")


def pytest_addoption(parser):
    """Add extra options to the command line."""
    parser.addoption("--driver-arg", default=[], action="append",
                     help="Pass an additional option to the WebDriver. Can "
                          "be specified more than once.")
    parser.addoption("--headless", action="store_true",
                     help="Run headless. Only applies to Chrome and Firefox.")


@pytest.fixture
def driver_args(request):
    return request.config.getoption("--driver-arg")


@pytest.fixture
def chrome_options(request, chrome_options):
    if request.config.getoption("--headless"):
        chrome_options.add_argument("--headless")
    return chrome_options


@pytest.fixture
def firefox_options(request, firefox_options):
    if request.config.getoption("--headless"):
        firefox_options.add_argument("-headless")
    return firefox_options


@pytest.fixture
def driver(driver):
    """Returns a WebDriver instance based on options and capabilities"""
    yield driver

    if isinstance(driver, webdriver.PhantomJS):
        # During selenium.quit(), send_remote_shutdown_command() is called.
        # PhantomJS does not actually send a remote shutdown command, but it
        # does close the temporary cookie file. This sometimes fails with
        # [Errno 9] Bad file descriptor. We call it here, so that if it does
        # fail, it does not prevent selenium.quit() from executing the other
        # shutdown tasks.
        try:
            driver.service.send_remote_shutdown_command()
        except OSError:
            pass
        driver.service._cookie_temp_file = None


@pytest.fixture
def open_image():
    return lambda name: Image.open(str(images_dir.join(name + ".png")))


colored_divs = """\
<!DOCTYPE html>
<html>
  <head>
    <title>Test Document</title>
    <style>
      div { width: 100px; height: 100px; }
      #red { background: red; }
      #green { background: green; }
      #blue { background: blue; position: relative; left: 50px; top: -50px; }
    </style>
  </head>
  <body>
    <h1>Hello World!</h1>
    <div id="red"></div>
    <div id="green"></div>
    <div id="blue"></div>
  </body>
</html>
"""


@pytest.fixture
def colored_divs_server(httpserver):
    httpserver.serve_content(content=colored_divs)
    return httpserver


@pytest.fixture
def testdir(testdir):
    # Copy parts of our own conftest.py into the new test dir
    conftest = ["import pytest", "from selenium import webdriver"]
    for f in (pytest_addoption, driver_args, driver,
              chrome_options, firefox_options):
        conftest.append(inspect.getsource(f))
    testdir.makeconftest(conftest)
    return testdir


@pytest.fixture
def copy_image(testdir):
    def _copy_image(name, module, test):
        screenshot_dir = testdir.tmpdir.join("screenshots", module)
        screenshot_dir.ensure(dir=True)

        source = images_dir.join(name + ".png")
        source.copy(screenshot_dir.join(test + ".png"))

    return _copy_image


@pytest.fixture
def selenium_args(request):
    args = ("--driver", request.config.getoption('driver'))
    if request.config.getoption("--headless"):
        args += ("--headless", )
    return args
