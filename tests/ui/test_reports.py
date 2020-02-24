import sys, os, pytest, pdb

try:
    zbathome = os.environ['ZBAT_HOME']
except:
    print('Test cannot run.  Please export ZBAT_HOME.')
    sys.exit()

if zbathome+'lib' not in sys.path:
    sys.path.append(zbathome+'lib')

from ui.reports.zbUIReports import Reports
from common.zbSelenium import zbSelenium
from common.zbCommon import rerunIfFail
from common.zbConfig import NUMBER_RETRIES, DELAY_SECONDS, SCREENSHOT_ON_FAIL
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# fixture
@pytest.fixture(scope="module")
def browser(browser_factory):
    browser = browser_factory(Reports)
    return browser["selenium"]


@pytest.mark.parametrize("testid",["C362783"])
@pytest.mark.smoke
#@pytest.mark.parametrize("testid", [("TC_DASHBOARD_001::Smoke::Verify Reports Page")])
def test_reports(testid, browser):
    """ Smoke -- Verify all the items in Reports Page can be loaded """
    assert rerunIfFail(function=browser.verifyReports(), selenium=browser.selenium, \
            number=NUMBER_RETRIES, delay=DELAY_SECONDS) == True
    assert rerunIfFail(function=browser.verifyReportsTab(), selenium=browser.selenium, \
            number=NUMBER_RETRIES, delay=DELAY_SECONDS) == True
    assert rerunIfFail(function=browser.verifyLogsTab(), selenium=browser.selenium, \
            number=NUMBER_RETRIES, delay=DELAY_SECONDS) == True
    assert rerunIfFail(function=browser.verifyScanReportsTab(), selenium=browser.selenium, \
            number=NUMBER_RETRIES, delay=DELAY_SECONDS) == True