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

from ui.integrations.zbUIIntegration import Integration
from ui.integrations.zbAssetManageSystems import AssetManagementSystems
from common.zbConfig import NUMBER_RETRIES, DELAY_SECONDS, SCREENSHOT_ON_FAIL
from common.zbCommon import rerunIfFail

# fixture
@pytest.fixture(scope="module")
def integration_browser(browser_factory):
    browser = browser_factory(Integration)
    return browser["selenium"]


@pytest.fixture(scope="module")
def asset_management_browser(browser_factory, integration_browser):
    browser = browser_factory(AssetManagementSystems,
                              custom_payload={"selenium": integration_browser.selenium},
                              single_br=False)
    return browser["selenium"]

class TestIntegrationAssetManagement:

    @pytest.mark.regression
    def test_asset_management_regression(self, asset_management_browser):
        assert rerunIfFail(function=asset_management_browser.check_asset_configuration(),
                           selenium=asset_management_browser.selenium,
                           screenshot=SCREENSHOT_ON_FAIL,
                           testname=zbathome + 'artifacts/test_Integration.png',
                           number=NUMBER_RETRIES,
                           delay=DELAY_SECONDS)

    @pytest.mark.regression
    def test_servicenow_integration_regression(self, asset_management_browser):
        assert rerunIfFail(function=asset_management_browser.check_servicenow_integration(),
                           selenium=asset_management_browser.selenium,
                           screenshot=SCREENSHOT_ON_FAIL,
                           testname=zbathome + 'artifacts/test_Integration.png',
                           number=NUMBER_RETRIES,
                           delay=DELAY_SECONDS)
