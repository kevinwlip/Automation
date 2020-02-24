import sys, os, pytest

try:
    zbathome = os.environ['ZBAT_HOME']
except:
    print('Test cannot run.  Please export ZBAT_HOME.')
    sys.exit()

if zbathome+'lib' not in sys.path:
    sys.path.append(zbathome+'lib')

from ui.risks.zbUIRisks import RisksVulnerabilities
from common.zbSelenium import zbSelenium
from common.zbCommon import rerunIfFail
from common.zbConfig import NUMBER_RETRIES, DELAY_SECONDS, SCREENSHOT_ON_FAIL
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# fixture
@pytest.fixture(scope="module")
def browser(browser_factory):
    browser = browser_factory(RisksVulnerabilities)
    return browser["selenium"]


@pytest.mark.smoke
@pytest.mark.parametrize("testid", [("TC_RISKS_VULN_001::Smoke::Verify Risks Vulnerability Page")])
def test_risks_vulnerabilities(testid, browser):
    """ Smoke -- Verify all the items in Risks Vulnerabilities Page can be loaded """
    assert rerunIfFail(function=browser.verifyRisksVulnTopSec(), selenium=browser.selenium, \
            number=NUMBER_RETRIES, delay=DELAY_SECONDS) == True
    assert rerunIfFail(function=browser.verifyRisksVulnSummary(), selenium=browser.selenium, \
            number=NUMBER_RETRIES, delay=DELAY_SECONDS) == True
    assert rerunIfFail(function=browser.verifyRisksVulnTable(), selenium=browser.selenium, \
            number=NUMBER_RETRIES, delay=DELAY_SECONDS) == True


@pytest.mark.smoke
@pytest.mark.parametrize("testid", [("TC_RISKS_RECALLS_001::Smoke::Verify Risks Recalls Page")])
def test_risks_recalls(testid, browser):
    """ Smoke -- Verify all the items in Risks Recalls Page can be loaded """
    assert rerunIfFail(function=browser.verifyRisksRecalls(), selenium=browser.selenium, \
            number=NUMBER_RETRIES, delay=DELAY_SECONDS) == True
