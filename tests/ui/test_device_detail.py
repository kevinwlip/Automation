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

from common.zbCommon import rerunIfFail, getHostname
from common.zbConfig import NUMBER_RETRIES, DELAY_SECONDS, SCREENSHOT_ON_FAIL
from ui.devices.zbUIDeviceInventory import DeviceInventory
from ui.devices.zbUIDeviceDetail import DeviceDetail


# fixture
@pytest.fixture(scope="module")
def browser(browser_factory):
    browser = browser_factory(DeviceDetail)
    return browser["selenium"]


class TestDeviceDetail:
    @pytest.mark.smoke
    def test_device_info_card(self, browser):
        assert rerunIfFail(function=browser.check_device_info_card(),
                           selenium=browser.selenium,
                           screenshot=SCREENSHOT_ON_FAIL,
                           testname=zbathome + 'artifacts/test_DeviceDetail_check_device_info.png',
                           number=NUMBER_RETRIES,
                           delay=DELAY_SECONDS)

    @pytest.mark.skip(reason="Element no longer exists")
    @pytest.mark.smoke
    def test_time_series(self, browser):
        assert rerunIfFail(function=browser.checkTimeSeries(),
                           selenium=browser.selenium,
                           screenshot=SCREENSHOT_ON_FAIL,
                           testname=zbathome + 'artifacts/test_DeviceDetail_check_time_series.png',
                           number=NUMBER_RETRIES,
                           delay=DELAY_SECONDS)

    @pytest.mark.smoke
    def test_network_traffic(self, browser):
        assert rerunIfFail(function=browser.checkNetworkTraffic(),
                           selenium=browser.selenium,
                           screenshot=SCREENSHOT_ON_FAIL,
                           testname=zbathome + 'artifacts/test_DeviceDetail_check_network_traffic.png',
                           number=NUMBER_RETRIES,
                           delay=DELAY_SECONDS)

    @pytest.mark.smoke
    def test_applications_protocols(self, browser):
        assert rerunIfFail(function=browser.checkApplicationsAndProtocols(),
                           selenium=browser.selenium,
                           screenshot=SCREENSHOT_ON_FAIL,
                           testname=zbathome + 'artifacts/test_DeviceDetail_check_application_protocol.png')

    @pytest.mark.smoke
    def test_network_usage_diagram(self, browser):
        assert rerunIfFail(function=browser.checkNetworkUsageDiagram(),
                           selenium=browser.selenium,
                           screenshot=SCREENSHOT_ON_FAIL,
                           testname=zbathome + 'artifacts/test_DeviceDetail_check_network_usage_diagram.png')

    @pytest.mark.regression
    def test_network_traffic_circles(self, browser):
        assert rerunIfFail(function=browser.check_network_traffic_circles(),
                           selenium=browser.selenium,
                           screenshot=SCREENSHOT_ON_FAIL,
                           testname=zbathome+'artifacts/test_DeviceDetail_check_network_traffic_circles.png')

    @pytest.mark.regression
    def test_resolve_and_reactivate_alert(self, browser):
        assert rerunIfFail(function=browser.check_resolve_and_reactivate_alert(),
                           selenium=browser.selenium,
                           screenshot=SCREENSHOT_ON_FAIL,
                           testname=zbathome+'artifacts/test_DeviceDetail_check_resolve_and_reactivate_alert.png')

