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

from ui.servers.zbUIServers import Servers
from common.zbCommon import rerunIfFail, getHostname
from common.zbConfig import NUMBER_RETRIES, DELAY_SECONDS, SCREENSHOT_ON_FAIL

# fixture
@pytest.fixture(scope="module")
def browser(browser_factory):
    browser = browser_factory(Servers)
    return browser["selenium"]

@pytest.mark.skip
class TestServers:

    @pytest.mark.skip(reason="Element no longer exists")
    @pytest.mark.smoke
    def test_server_highcharts(self, browser):
        assert rerunIfFail(function=browser.check_server_highcharts(),
                           selenium=browser.selenium,
                           screenshot=SCREENSHOT_ON_FAIL,
                           testname=zbathome + 'artifacts/test_Servers.png',
                           number=NUMBER_RETRIES,
                           delay=DELAY_SECONDS)

    @pytest.mark.smoke
    def test_server_inventory(self, browser):
        assert rerunIfFail(function=browser.check_server_inventory(),
                           selenium=browser.selenium,
                           screenshot=SCREENSHOT_ON_FAIL,
                           testname=zbathome + 'artifacts/test_Servers.png',
                           number=NUMBER_RETRIES,
                           delay=DELAY_SECONDS)