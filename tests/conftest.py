import inspect

import pytest

pytest_plugins = ["pytester"]


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
    driver.set_window_position(100, 100)
    driver.set_window_size(800, 600)
    return driver


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
    conftest = ["import pytest"]
    for f in (pytest_addoption, driver_args, chrome_options, firefox_options):
        conftest.append(inspect.getsource(f))
    testdir.makeconftest(conftest)
    return testdir


@pytest.fixture
def selenium_args(request):
    args = ("--driver", request.config.getoption('driver'))
    if request.config.getoption("--headless"):
        args += ("--headless", )
    return args
