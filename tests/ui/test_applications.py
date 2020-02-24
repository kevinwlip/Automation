#!/usr/bin/python
import sys
import os
import pytest

try:
    zbathome = os.environ['ZBAT_HOME']
except:
    print('Test cannot run.  Please export ZBAT_HOME.')
    sys.exit()

if zbathome + 'lib' not in sys.path:
    sys.path.append(zbathome + 'lib')

from ui.application.zbUIApplication import Applications
from common.zbCommon import rerunIfFail, getHostname
from common.zbConfig import NUMBER_RETRIES, DELAY_SECONDS, SCREENSHOT_ON_FAIL

# fixture
@pytest.fixture(scope="module")
def browser(browser_factory):
    browser = browser_factory(Applications)
    return browser["selenium"]


class TestApplications:
    @pytest.mark.smoke
    @pytest.mark.parametrize("testid", ["C362786"])
    def test_application_verify_headers(self, testid, browser):
        assert rerunIfFail(function=browser.check_application_verify_headers(),
                           selenium=browser.selenium,
                           screenshot=SCREENSHOT_ON_FAIL,
                           testname=zbathome + 'artifacts/test_applications.png',
                           number=NUMBER_RETRIES,
                           delay=DELAY_SECONDS)

    @pytest.mark.smoke
    @pytest.mark.parametrize("testid", ["C362787"])
    def test_application_verify_entries(self, testid, browser):
        assert rerunIfFail(function=browser.check_application_verify_entries(),
                           selenium=browser.selenium,
                           screenshot=SCREENSHOT_ON_FAIL,
                           testname=zbathome + 'artifacts/test_applications.png',
                           number=NUMBER_RETRIES,
                           delay=DELAY_SECONDS)

    @pytest.mark.regression
    @pytest.mark.parametrize("testid", ["C363108"])
    def test_sort_and_view_column_reset(self, testid, browser):
        assert rerunIfFail(function=browser.check_sort(),
                           selenium=browser.selenium,
                           screenshot=SCREENSHOT_ON_FAIL,
                           testname=zbathome + 'artifacts/test_sort.png',
                           number=NUMBER_RETRIES,
                           delay=DELAY_SECONDS)

        assert rerunIfFail(function=browser.check_application_view_columns_reset(),
                           selenium=browser.selenium,
                           screenshot=SCREENSHOT_ON_FAIL,
                           testname=zbathome + 'artifacts/test_application_view_columns_reset.png',
                           number=NUMBER_RETRIES,
                           delay=DELAY_SECONDS)

    @pytest.mark.regression
    @pytest.mark.parametrize("testid", ["C363109"])
    def test_applications_devices_link(self, testid, browser):
        assert rerunIfFail(function=browser.check_applications_devices_link(),
                           selenium=browser.selenium,
                           screenshot=SCREENSHOT_ON_FAIL,
                           testname=zbathome + 'artifacts/test_applications_devices_link.png',
                           number=NUMBER_RETRIES,
                           delay=DELAY_SECONDS)

    @pytest.mark.regression
    @pytest.mark.parametrize("testid", ["C363110"])
    def test_profiles_entry_and_search(self, testid, browser):
        assert rerunIfFail(function=browser.check_profiles_entry_and_search(),
                           selenium=browser.selenium,
                           screenshot=SCREENSHOT_ON_FAIL,
                           testname=zbathome + 'artifacts/test_applications_devices_link.png',
                           number=NUMBER_RETRIES,
                           delay=DELAY_SECONDS)

    @pytest.mark.regression
    @pytest.mark.parametrize("testid", ["C363111"])
    def test_applications_verify_entries_all_pages(self, testid, browser):
        assert rerunIfFail(function=browser.check_applications_verify_entries_all_pages(),
                           selenium=browser.selenium,
                           screenshot=SCREENSHOT_ON_FAIL,
                           testname=zbathome + 'artifacts/test_applications_devices_link.png',
                           number=NUMBER_RETRIES,
                           delay=DELAY_SECONDS)



