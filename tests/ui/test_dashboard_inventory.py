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

from ui.dashboard.zbUIDashboardInventory import DashboardInventory
from common.zbCommon import rerunIfFail, getHostname
from common.zbConfig import NUMBER_RETRIES, DELAY_SECONDS, SCREENSHOT_ON_FAIL


# fixture
@pytest.fixture(scope="module")
def browser(browser_factory):
    browser = browser_factory(DashboardInventory)
    return browser["selenium"]


class TestDashboardInventory:

    @pytest.mark.parametrize("testid", ["CXXXXXX"])
    @pytest.mark.smoke
    def test_subnets_card(self, testid, browser):
        assert rerunIfFail(function=browser.check_dashboard_inventory_subnets(),
                           selenium=browser.selenium,
                           screenshot=SCREENSHOT_ON_FAIL,
                           testname=zbathome + 'artifacts/test_DashboardInventory.png',
                           number=NUMBER_RETRIES,
                           delay=DELAY_SECONDS)

'''
    @pytest.mark.parametrize("testid", ["CXXXXXX"])
    @pytest.mark.smoke
    def test_devices_card(self, testid, browser):
        assert rerunIfFail(function=browser.check_dashboard_inventory_devices(),
                           selenium=browser.selenium,
                           screenshot=SCREENSHOT_ON_FAIL,
                           testname=zbathome + 'artifacts/test_DashboardInventory.png',
                           number=NUMBER_RETRIES,
                           delay=DELAY_SECONDS)

    @pytest.mark.parametrize("testid", ["CXXXXXX"])
    @pytest.mark.smoke
    def test_device_categories_card(self, testid, browser):
        assert rerunIfFail(function=browser.check_dashboard_inventory_device_categories(),
                           selenium=browser.selenium,
                           screenshot=SCREENSHOT_ON_FAIL,
                           testname=zbathome + 'artifacts/test_DashboardInventory.png',
                           number=NUMBER_RETRIES,
                           delay=DELAY_SECONDS)
'''
