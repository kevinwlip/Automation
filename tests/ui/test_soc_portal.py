#!/usr/bin/python
import sys
import os
import pytest

try:
    zbathome = os.environ['ZBAT_HOME']
except:
    print ('Test cannot run.  Please export ZBAT_HOME.')
    sys.exit()

if zbathome+'lib' not in sys.path:
    sys.path.append(zbathome+'lib')
    
from ui.zbUISOC import SOCDashboard
from common.zbConfig import defaultEnv, NUMBER_RETRIES, DELAY_SECONDS, SCREENSHOT_ON_FAIL
from common.zbCommon import rerunIfFail

env = defaultEnv()
socportal = env["socportal"]
if not socportal: print('SOC portal value not set in zbCommon.py'); sys.exit()

# fixture
@pytest.fixture(scope="module")
def browser(browser_factory):
    custom_payload = {
        "url": socportal
    }
    browser = browser_factory(SOCDashboard, custom_payload=custom_payload)
    return browser["selenium"]


class Test_SOC:
    @pytest.mark.smoke
    def test_SOCSmoke(self, browser):
        assert rerunIfFail(function=browser.checkSmoke(), selenium=browser.selenium, number=1, delay=DELAY_SECONDS) == True

    def test_AlertSummary(self, browser):
        assert rerunIfFail(function=browser.checkAlertSummary(), selenium=browser.selenium, screenshot=SCREENSHOT_ON_FAIL, testname=zbathome+'artifacts/test_SOCAlertSummary.png', number=NUMBER_RETRIES, delay=DELAY_SECONDS) == True

    def test_DataSummary(self, browser):
        assert rerunIfFail(function=browser.checkDataSummary(), selenium=browser.selenium, screenshot=SCREENSHOT_ON_FAIL, testname=zbathome+'artifacts/test_SOCDataSummary.png', number=NUMBER_RETRIES, delay=DELAY_SECONDS) == True
    
    @pytest.mark.skip(reason="Feature no longer exists")
    def test_SeriesGraphWidget(self, browser):
        assert rerunIfFail(function=browser.checkSeriesGraphWidget(), selenium=browser.selenium, screenshot=SCREENSHOT_ON_FAIL, testname=zbathome+'artifacts/test_SOCSeriesGraphWidget.png', number=NUMBER_RETRIES, delay=DELAY_SECONDS) == True
    
    def test_SiteWidget(self, browser):
        assert rerunIfFail(function=browser.checkSiteWidget(), selenium=browser.selenium, screenshot=SCREENSHOT_ON_FAIL, testname=zbathome+'artifacts/test_SOCSiteWidget.png', number=NUMBER_RETRIES, delay=DELAY_SECONDS) == True


    def test_AlertWidget(self, browser):
        assert rerunIfFail(function=browser.checkAlertWidget(), selenium=browser.selenium, screenshot=SCREENSHOT_ON_FAIL, testname=zbathome+'artifacts/test_SOCAlertWidget.png', number=NUMBER_RETRIES, delay=DELAY_SECONDS) == True


    def test_TopDevicesWidget(self, browser):
        assert rerunIfFail(function=browser.checkTopDevicesWidget(), selenium=browser.selenium, screenshot=SCREENSHOT_ON_FAIL, testname=zbathome+'artifacts/test_SOCTopDevicesWidget.png', number=NUMBER_RETRIES, delay=DELAY_SECONDS) == True


    def test_ExternalEndpointWidget(self, browser):
        assert rerunIfFail(function=browser.checkExternalEndpointWidget(), selenium=browser.selenium, screenshot=SCREENSHOT_ON_FAIL, testname=zbathome+'artifacts/test_SOCExternalEndpointWidget.png', number=NUMBER_RETRIES, delay=DELAY_SECONDS) == True


