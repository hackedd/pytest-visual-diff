import re

from helpers import expected_failure_with_chrome

link_re = '<a class="image" href=".*?" target="_blank">(.*?)</a>'
image_re = '<div class="image"><a href=".*"><img src=".*"/></a></div>'


def test_images_are_added_to_report(colored_divs_server, testdir,
                                    copy_image, selenium_args):
    testdir.makepyfile(test_module="""
    def test_one_element(driver, check_reference_screenshot):
        driver.get("{server_url}")
        element = driver.find_element_by_id("red")
        check_reference_screenshot(element)
    """.format(server_url=colored_divs_server.url))

    copy_image("blue", "test_module", "test_one_element")

    report_path = testdir.tmpdir.join("report.html")
    result = testdir.runpytest("--html", report_path, *selenium_args)
    result.assert_outcomes(failed=1)

    assert report_path.check(file=True)
    report_html = report_path.read()

    matches = re.findall(link_re, report_html)
    assert matches == ["Screenshot", "Expected", "Difference", "Actual"]
    assert len(re.findall(image_re, report_html)) == len(matches)


@expected_failure_with_chrome
def test_multiple_images_are_added_to_report(colored_divs_server, testdir,
                                             copy_image, selenium_args):
    testdir.makepyfile(test_module="""
    def test_one_element(driver, check_reference_screenshot):
        driver.get("{server_url}")
        element = driver.find_element_by_id("red")
        check_reference_screenshot(element, "foo")
        check_reference_screenshot(element, "bar")
    """.format(server_url=colored_divs_server.url))

    copy_image("red", "test_module", "test_one_element__foo")
    copy_image("blue", "test_module", "test_one_element__bar")

    report_path = testdir.tmpdir.join("report.html")
    result = testdir.runpytest("--html", report_path, *selenium_args)
    result.assert_outcomes(failed=1)

    assert report_path.check(file=True)
    report_html = report_path.read()

    # Check that both comparisons added screenshots to the report and that
    # the second comparison added a 'difference' image.
    matches = re.findall(link_re, report_html)
    assert matches == ["Screenshot", "Expected foo", "Actual foo",
                       "Expected bar", "Difference bar", "Actual bar"]
    assert len(re.findall(image_re, report_html)) == len(matches)
