#!/usr/bin/python

import pdb, json, sys, os, pytest, datetime, random, calendar, time

try:
    zbathome = os.environ['ZBAT_HOME']
except:
    #pdb.set_trace()
    print('Test cannot run.  Please export ZBAT_HOME.')
    sys.exit()

if zbathome+'lib' not in sys.path:
    sys.path.append(zbathome+'lib')
    
from ui.mssp.zbUIMSSP import MSSP
from common.zbConfig import defaultEnv, NUMBER_RETRIES, DELAY_SECONDS, SCREENSHOT_ON_FAIL
from common.zbCommon import rerunIfFail


env = defaultEnv()

# fixtures
@pytest.fixture(scope="module")
def browser(browser_factory):
    return browser_factory(MSSP)


@pytest.fixture(scope="module", params=["1D"])
def timerange(request):
    return request.param


@pytest.mark.skipif(os.environ['NODE_ENV'] in ['production'], reason='MSSP test should not be run on Production')
class Test_MSSP:
    
    @pytest.mark.bugs #AP-3992
    def test_SummaryCompareCustomers(self, browser, timerange):
        selenium = browser["selenium"]
        assert rerunIfFail(function=selenium.verifyMSSPCustomers(timerange), selenium=selenium.selenium, screenshot=SCREENSHOT_ON_FAIL, testname=zbathome+'artifacts/test_MSSPSummaryCompareCustomers.png', number=NUMBER_RETRIES, delay=DELAY_SECONDS) == True

    @pytest.mark.bugs #AP-3460
    def test_Resellers(self, browser):
        selenium = browser["selenium"]
        assert rerunIfFail(function=selenium.verifyMSSPResellers(), selenium=selenium.selenium, screenshot=SCREENSHOT_ON_FAIL, testname=zbathome+'artifacts/test_MSSPResellers.png', number=NUMBER_RETRIES, delay=DELAY_SECONDS) == True

    @pytest.mark.bugs #AP-3460
    def test_CustomerDetail(self, browser):
        selenium = browser["selenium"]
        assert rerunIfFail(function=selenium.verifyCustomerDetail(), selenium=selenium.selenium, screenshot=SCREENSHOT_ON_FAIL, testname=zbathome+'artifacts/test_MSSPCustomerDetail.png', number=NUMBER_RETRIES, delay=DELAY_SECONDS) == True

    @pytest.mark.bugs #AP-3460
    def test_CustomerCompareDashboard(self, browser):
        selenium = browser["selenium"]
        assert rerunIfFail(function=selenium.verifyMSSPDashboard(), selenium=selenium.selenium, screenshot=SCREENSHOT_ON_FAIL, testname=zbathome+'artifacts/test_MSSPCustomerCompareDashboard.png', number=NUMBER_RETRIES, delay=DELAY_SECONDS) == True
