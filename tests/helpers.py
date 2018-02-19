import pytest

expected_failure_with_chrome = pytest.mark.xfail(
    pytest.config.getoption("driver") == "Chrome" and
    not pytest.config.getoption("--headless"),
    reason="colors in Chrome screenshots are incorrect"
)
