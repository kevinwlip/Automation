import sys, os, pytest

try:
    zbathome = os.environ['ZBAT_HOME']
except:
    print('Test cannot run.  Please export ZBAT_HOME.')
    sys.exit()

if zbathome+'lib' not in sys.path:
    sys.path.append(zbathome+'lib')

from ui.navigator.zbUINavigator import Navigator
from common.zbSelenium import zbSelenium
from common.zbCommon import rerunIfFail
from common.zbConfig import NUMBER_RETRIES, DELAY_SECONDS, SCREENSHOT_ON_FAIL
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# fixture
@pytest.fixture(scope="module")
def browser(browser_factory):
    browser = browser_factory(Navigator)
    return browser["selenium"]

@pytest.mark.smoke
@pytest.mark.parametrize("testid", [("TC_NAVIGATOR_001::Smoke::Verify Navigator Menu and Top Bars")])
def test_navigator(testid, browser):
    """ Smoke -- Verify all the items in left panel and toolbar can be loaded """
    assert rerunIfFail(function=browser.verifyNavigatorMenu(), selenium=browser.selenium, \
             number=NUMBER_RETRIES, delay=DELAY_SECONDS) == True
