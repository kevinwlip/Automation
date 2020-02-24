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

from ui.dashboard.zbUIDashboardOperational import DashBoardOperational
from common.zbCommon import rerunIfFail, getHostname
from common.zbConfig import NUMBER_RETRIES, DELAY_SECONDS, SCREENSHOT_ON_FAIL

# fixture
@pytest.fixture(scope="module")
def browser(browser_factory):
    browser = browser_factory(DashBoardOperational)
    return browser["selenium"]


class TestDashboardOperational:
    @pytest.mark.smoke
    @pytest.mark.parametrize("testid",["C360970"])
    def test_device_items(self, testid, browser):
        assert rerunIfFail(function=browser.check_device_items(),
                           selenium=browser.selenium,
                           screenshot=SCREENSHOT_ON_FAIL,
                           testname=zbathome + 'artifacts/test_DashboardOperational.png',
                           number=NUMBER_RETRIES,
                           delay=DELAY_SECONDS)

    @pytest.mark.smoke
    @pytest.mark.parametrize("testid",["C360971"])
    def test_category_profile_card(self, testid, browser):
        assert rerunIfFail(function=browser.check_category_profile_card(),
                           selenium=browser.selenium,
                           screenshot=SCREENSHOT_ON_FAIL,
                           testname=zbathome + 'artifacts/test_DashboardOperational.png',
                           number=NUMBER_RETRIES,
                           delay=DELAY_SECONDS)

    @pytest.mark.smoke
    @pytest.mark.parametrize("testid",["C360972"])
    def test_image_charts(self, testid, browser):
        assert rerunIfFail(function=browser.check_image_charts(),
                           selenium=browser.selenium,
                           screenshot=SCREENSHOT_ON_FAIL,
                           testname=zbathome + 'artifacts/test_DashboardOperational.png',
                           number=NUMBER_RETRIES,
                           delay=DELAY_SECONDS)

    @pytest.mark.smoke
    @pytest.mark.parametrize("testid",["C360973"])
    def test_healthcare_device_usage(self, testid, browser):
        assert rerunIfFail(function=browser.check_healthcare_device_usage(),
                           selenium=browser.selenium,
                           screenshot=SCREENSHOT_ON_FAIL,
                           testname=zbathome + 'artifacts/test_DashboardOperational.png',
                           number=NUMBER_RETRIES,
                           delay=DELAY_SECONDS)

    @pytest.mark.smoke
    @pytest.mark.parametrize("testid",["C360974"])
    def test_image_patient_data(self, testid, browser):
        assert rerunIfFail(function=browser.check_image_patient_data(),
                           selenium=browser.selenium,
                           screenshot=SCREENSHOT_ON_FAIL,
                           testname=zbathome + 'artifacts/test_DashboardOperational.png',
                           number=NUMBER_RETRIES,
                           delay=DELAY_SECONDS)

    @pytest.mark.smoke
    @pytest.mark.parametrize("testid",["C360975"])
    def test_image_scan_analysis(self, testid,  browser):
        assert rerunIfFail(function=browser.check_image_scan_analysis(),
                           selenium=browser.selenium,
                           screenshot=SCREENSHOT_ON_FAIL,
                           testname=zbathome + 'artifacts/test_DashboardOperational.png',
                           number=NUMBER_RETRIES,
                           delay=DELAY_SECONDS)