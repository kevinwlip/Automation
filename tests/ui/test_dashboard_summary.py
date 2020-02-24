from ui.zbUIShared import clickSpecificTimerange
import sys, os, pytest

try:
    zbathome = os.environ['ZBAT_HOME']
except:
    print('Test cannot run.  Please export ZBAT_HOME.')
    sys.exit()

if zbathome+'lib' not in sys.path:
    sys.path.append(zbathome+'lib')

from ui.dashboard.zbUIDashboardSummary import DashboardSummary
from common.zbSelenium import zbSelenium
from common.zbCommon import rerunIfFail
from common.zbConfig import NUMBER_RETRIES, DELAY_SECONDS, SCREENSHOT_ON_FAIL
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# fixture
@pytest.fixture(scope="module")
def browser(browser_factory):
    browser = browser_factory(DashboardSummary)
    return browser["selenium"]

@pytest.mark.smoke
@pytest.mark.parametrize("testid", ["C363021"])
def test_global_filters(testid, browser):
    """ Smoke -- Verify Global Filters elements appear  """
    assert rerunIfFail(function=browser.verifyGlobalFilters(), selenium=browser.selenium, \
            number=NUMBER_RETRIES, delay=DELAY_SECONDS) == True

@pytest.mark.bugs
@pytest.mark.regression
@pytest.mark.parametrize("testid", ["C360806"])
def test_global_filters_reg(testid, browser):
    """ Regression -- Verify selecting different Global Filters changes values in Top Bar Widget """
    assert rerunIfFail(function=browser.verifyGlobalFiltersOnTopBar(), selenium=browser.selenium, \
            number=NUMBER_RETRIES, delay=DELAY_SECONDS) == True

@pytest.mark.regression
@pytest.mark.parametrize("testid", ["C360814"])
def test_dashboard_summary_protocols(testid, browser):
    assert rerunIfFail(function=browser.regDashboardSummaryProtocols(), selenium=browser.selenium, \
        number=NUMBER_RETRIES, delay=DELAY_SECONDS) == True

@pytest.mark.parametrize("testid", ["C360807"])
@pytest.mark.regression
def test_dashboard_summary_apps(testid, browser):
    assert rerunIfFail(function=browser.regDashboardSummaryApplications(), selenium=browser.selenium, \
        number=NUMBER_RETRIES, delay=DELAY_SECONDS) == True

@pytest.mark.parametrize("testid", ["C360820"])
@pytest.mark.regression
def test_dashboard_summary_networks(testid, browser):
    assert rerunIfFail(function=browser.regDashboardSummaryNetworks(), selenium=browser.selenium, \
        number=NUMBER_RETRIES, delay=DELAY_SECONDS) == True

@pytest.mark.parametrize("testid", ["C360821"])
@pytest.mark.regression
def test_dashboard_summary_vuln(testid, browser):
    assert rerunIfFail(function=browser.regDashboardSummaryVuln(), selenium=browser.selenium, \
        number=NUMBER_RETRIES, delay=DELAY_SECONDS) == True

@pytest.mark.parametrize("testid", ["C360822"])
@pytest.mark.regression
def test_dashboard_summary_alerts(testid, browser):
    assert rerunIfFail(function=browser.regDashboardSummaryAlerts(), selenium=browser.selenium, \
        number=NUMBER_RETRIES, delay=DELAY_SECONDS) == True

@pytest.mark.parametrize("testid", ["C360823"])
@pytest.mark.regression
def test_dashboard_summary_risks(testid, browser):
    assert rerunIfFail(function=browser.regDashboardSummaryRisks(), selenium=browser.selenium, \
        number=NUMBER_RETRIES, delay=DELAY_SECONDS) == True

@pytest.mark.parametrize("testid", ["C360805"])
@pytest.mark.regression
def test_dashboard_summary_reg(testid, browser):
    clickSpecificTimerange(browser.selenium, specific="1 Month")
    assert rerunIfFail(function=browser.checkTopBar(), selenium=browser.selenium, \
        number=NUMBER_RETRIES, delay=DELAY_SECONDS) == True
    clickSpecificTimerange(browser.selenium, specific="1 Month")
    assert rerunIfFail(function=browser.checkDeviceCard(), selenium=browser.selenium, \
        number=NUMBER_RETRIES, delay=DELAY_SECONDS) == True
    clickSpecificTimerange(browser.selenium, specific="1 Month")
    assert rerunIfFail(function=browser.checkSiteCard(), selenium=browser.selenium, \
        number=NUMBER_RETRIES, delay=DELAY_SECONDS) == True

@pytest.mark.parametrize("testid", ["C360802"])
@pytest.mark.smoke
@pytest.mark.parametrize("test_id", [("TC_DASHBOARD_001::Smoke::Verify Dashboard Summary Page")])
def test_dashboard_summary(testid, test_id, browser):
    """ Smoke -- Verify all the items in Dashboard Summary Page can be loaded """
    clickSpecificTimerange(browserobj=browser.selenium, specific="1 Month")
    assert rerunIfFail(function=browser.verifyDashboardSummaryTop(), selenium=browser.selenium, \
            number=NUMBER_RETRIES, delay=DELAY_SECONDS) == True
    assert rerunIfFail(function=browser.verifyDashboardSummaryGeneral(), selenium=browser.selenium, \
            number=NUMBER_RETRIES, delay=DELAY_SECONDS) == True
    assert rerunIfFail(function=browser.verifyDashboardSummaryDevices(), selenium=browser.selenium, \
            number=NUMBER_RETRIES, delay=DELAY_SECONDS) == True
    assert rerunIfFail(function=browser.verifyDashboardSummarySites(), selenium=browser.selenium, \
            number=NUMBER_RETRIES, delay=DELAY_SECONDS) == True
    assert rerunIfFail(function=browser.verifyDashboardSummaryApplications(), selenium=browser.selenium, \
            number=NUMBER_RETRIES, delay=DELAY_SECONDS) == True
    assert rerunIfFail(function=browser.verifyDashboardSummaryProtocols(), selenium=browser.selenium, \
            number=NUMBER_RETRIES, delay=DELAY_SECONDS) == True 
    assert rerunIfFail(function=browser.verifyDashboardSummaryNetworkSegments(), selenium=browser.selenium, \
            number=NUMBER_RETRIES, delay=DELAY_SECONDS) == True
    assert rerunIfFail(function=browser.verifyDashboardSummaryAlerts(), selenium=browser.selenium, \
            number=NUMBER_RETRIES, delay=DELAY_SECONDS) == True
    assert rerunIfFail(function=browser.verifyDashboardSummaryVulnerabilities(), selenium=browser.selenium, \
            number=NUMBER_RETRIES, delay=DELAY_SECONDS) == True
    assert rerunIfFail(function=browser.verifyDashboardSummaryRiskOverview(), selenium=browser.selenium, \
           number=NUMBER_RETRIES, delay=DELAY_SECONDS) == True
