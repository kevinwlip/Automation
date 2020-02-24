import sys
import os
import pytest

try:
    zbathome = os.environ['ZBAT_HOME']
except:
    print('Test cannot run.  Please export ZBAT_HOME.')
    sys.exit()

if zbathome+'lib' not in sys.path:
    sys.path.append(zbathome+'lib')
    
from ui.zbUIGlobalSearch import GlobalSearch
from common.zbCommon import rerunIfFail
from common.zbConfig import NUMBER_RETRIES, DELAY_SECONDS, SCREENSHOT_ON_FAIL

# fixture
@pytest.fixture(scope="module")
def browserGlobalSearch(browser_factory):
    return browser_factory(GlobalSearch)

@pytest.mark.skipif(os.environ["NODE_ENV"] in ["testing"], reason="Testing doesn't have a functioning global search") #Testing doesn't have a functioning global search
@pytest.mark.skipif(os.environ["NODE_ENV"] in ["staging"], reason="Not enough data")
#@pytest.mark.skip(reason="Test flaky result.  Skip until fixed")
class Test_Global_Search:

    @pytest.mark.parametrize("testid",["C359696"])
    @pytest.mark.regression     
    def test_global_search_devices(self, testid, browserGlobalSearch):
        selenium = browserGlobalSearch["selenium"]
        assert rerunIfFail(function=selenium.verifyGlobalSearchDevices(), selenium=selenium.selenium, screenshot=SCREENSHOT_ON_FAIL, testname=zbathome+'artifacts/test_global_search_device.png', number=NUMBER_RETRIES, delay=DELAY_SECONDS) == True

    @pytest.mark.parametrize("testid",["C362797"])
    @pytest.mark.regression     
    def test_global_search_alerts(self, testid, browserGlobalSearch):
        selenium = browserGlobalSearch["selenium"]
        assert rerunIfFail(function=selenium.verifyGlobalSearchAlerts(), selenium=selenium.selenium, screenshot=SCREENSHOT_ON_FAIL, testname=zbathome+'artifacts/test_global_search_alerts.png', number=NUMBER_RETRIES, delay=DELAY_SECONDS) == True

    @pytest.mark.parametrize("testid",["C362798"])
    @pytest.mark.regression
    def test_global_search_results(self, testid, browserGlobalSearch):
        selenium = browserGlobalSearch["selenium"]
        assert rerunIfFail(function=selenium.verifyGlobalSearchResultPage(), selenium=selenium.selenium, screenshot=SCREENSHOT_ON_FAIL, testname=zbathome+'artifacts/test_global_search_alerts.png', number=NUMBER_RETRIES, delay=DELAY_SECONDS) == True
