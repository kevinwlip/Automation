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

from ui.dashboard.zbUIDashboardSecurity import DashBoardSecurity
from common.zbCommon import rerunIfFail, getHostname
from common.zbConfig import NUMBER_RETRIES, DELAY_SECONDS, SCREENSHOT_ON_FAIL


# fixture
@pytest.fixture(scope="module")
def browser(browser_factory):
    browser = browser_factory(DashBoardSecurity)
    return browser["selenium"]


class TestDashboardSecurity:

    @pytest.mark.parametrize("testid", ["C360965"])
    @pytest.mark.smoke
    def test_sites_categories_profiles(self, testid, browser):
        assert rerunIfFail(function=browser.check_all_tabs_site_cate_prof(),
                           selenium=browser.selenium,
                           screenshot=SCREENSHOT_ON_FAIL,
                           testname=zbathome + 'artifacts/test_DashboardSecurity.png',
                           number=NUMBER_RETRIES,
                           delay=DELAY_SECONDS)

    @pytest.mark.parametrize("testid", ["C360966"])
    @pytest.mark.smoke
    def test_risk_assessment(self, testid, browser):
        assert rerunIfFail(function=browser.check_risk_assessment(),
                           selenium=browser.selenium,
                           screenshot=SCREENSHOT_ON_FAIL,
                           testname=zbathome + 'artifacts/test_DashboardSecurity.png',
                           number=NUMBER_RETRIES,
                           delay=DELAY_SECONDS)

    @pytest.mark.parametrize("testid", ["C360967"])
    @pytest.mark.smoke
    def test_network_summary(self, testid, browser):
        assert rerunIfFail(function=browser.check_network_summary(),
                           selenium=browser.selenium,
                           screenshot=SCREENSHOT_ON_FAIL,
                           testname=zbathome + 'artifacts/test_DashboardSecurity.png',
                           number=NUMBER_RETRIES,
                           delay=DELAY_SECONDS)

    @pytest.mark.parametrize("testid", ["C360968"])
    @pytest.mark.smoke
    def test_external_destinations(self, testid, browser):
        assert rerunIfFail(function=browser.check_external_destinations(),
                           selenium=browser.selenium,
                           screenshot=SCREENSHOT_ON_FAIL,
                           testname=zbathome + 'artifacts/test_DashboardSecurity.png',
                           number=NUMBER_RETRIES,
                           delay=DELAY_SECONDS)

    @pytest.mark.parametrize("testid", ["C360969"])
    @pytest.mark.smoke
    def test_endpoint_protection(self, testid, browser):
        assert rerunIfFail(function=browser.check_endpoint_protection(),
                           selenium=browser.selenium,
                           screenshot=SCREENSHOT_ON_FAIL,
                           testname=zbathome + 'artifacts/test_DashboardSecurity.png',
                           number=NUMBER_RETRIES,
                           delay=DELAY_SECONDS)

    # https://testing.zingbox.com/login?tenantid=qa-automation does not have this card!
    def test_device_management(self, browser):
        assert rerunIfFail(function=browser.check_device_management(),
                           selenium=browser.selenium,
                           screenshot=SCREENSHOT_ON_FAIL,
                           testname=zbathome + 'artifacts/test_DashboardSecurity.png',
                           number=NUMBER_RETRIES,
                           delay=DELAY_SECONDS)

