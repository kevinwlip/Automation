import pdb, json, sys, os, pytest, datetime, random, calendar, time
from collections import OrderedDict

try:
    nodeEnv = os.environ['NODE_ENV']
    zbathome = os.environ['ZBAT_HOME']
    kafka_home = os.environ['KAFKA_HOME']
    zbat_tenant_id = os.environ['ZBAT_TENANT_INTERNAL_ID']
    if 'staging' in nodeEnv:
        zbat_tenant_id = os.environ['ZBAT_STAGING_TENANT_INTERNAL_ID']
except:
    print('Test cannot run.  Please export ZBAT_HOME, KAFKA_HOME, ZBAT_TENANT_INTERNAL_ID.')
    sys.exit()

if zbathome+'lib' not in sys.path:
    sys.path.append(zbathome+'lib')

from common.zbSelenium import zbSelenium
from common.zbCommon import rerunIfFail, getHostname
from ui.dashboard.zbUIDashboardSummary import DashboardSummary
from common.zbConfig import defaultEnv, NUMBER_RETRIES, DELAY_SECONDS, SCREENSHOT_ON_FAIL
from locator.protocols import ProtocolPage, ProtocolDetail
from urllib.parse import urlparse
from ui.zbUIShared import *
env = defaultEnv()

@pytest.fixture(scope='module')
def tenant(request):
    config = {}
    config["url"] = env["uiportal"]+"?tenantid="+env["tenantid"]
    print(config["url"])
    if "demo" in config["url"]:
        config["username"] = os.environ["ZBAT_DEMO_UNAME"]
        config["password"] = os.environ["ZBAT_DEMO_PWD"]
    elif "soho" in config["url"]:
        config["username"] = os.environ["ZBAT_PROD_UNAME"]
        config["password"] = os.environ["ZBAT_PROD_PWD"]
    else:
        config["username"] = os.environ["ZBAT_TESTING_UNAME"]
        config["password"] = os.environ["ZBAT_TESTING_PWD"]
        
    config["comparestrict"] = False
    return config

@pytest.fixture(scope="module")
def browser_smoke(browser_factory_smoke, tenant):
    browser = browser_factory_smoke(DashboardSummary, custom_payload=tenant)
    return browser["selenium"]

class Test_Protocols:
    @pytest.mark.parametrize("testid",["C362789"])
    @pytest.mark.parametrize("test_id", ["protocols_page"])
    @pytest.mark.smoke
    def test_protocols_smoke(self, testid, test_id, browser_smoke, tenant):
        browser = browser_smoke
        if browser.selenium.driver.capabilities["browserName"] == "internet explorer":
            pytest.skip()
        url =  urlparse(browser.selenium.driver.current_url)
        rcode = browser.selenium.click(selector=ProtocolPage.CSS_PROTOCOLS_NAV)
        waitLoadProgressDone(browser.selenium)
        time.sleep(2)
        for css in ProtocolPage.CSS_BULK_PROTOCOLS_LIST:
            logging.info('Finding Protocol Page CSS element: {}'.format(css))
            if not browser.selenium.findSingleCSS(selector=css, timeout=3):
                assert False, logging.critical('Expected protocols Page CSS element {}'.format(css))
                break
        rcode = browser.selenium.findMultiCSS(selector=ProtocolPage.CSS_TABLE_HEADER)
        for item in rcode:
            if item.text not in ProtocolPage.chklist:
                assert False, logging.critical('Protocols Page Header \"'+item.text+'\" has incorrect name')
                break
        '''
        rcode = browser.selenium.findMultiCSS(selector=ProtocolPage.CSS_GRAPH_BAR)
        if len(rcode) < 24:
            assert False, logging.critical('Protocols Page Graph has missing bars')
        '''

    '''
    @pytest.mark.parametrize("test_id", ["protocols_detail"])
    @pytest.mark.smoke
    def test_protocols_detail_smoke(self,test_id,browser_smoke, tenant):
        browser = browser_smoke
        if browser.selenium.driver.capabilities["browserName"] == "internet explorer":
            pytest.skip()
        url =  urlparse(browser.selenium.driver.current_url)
        rcode = browser.selenium.click(selector=ProtocolPage.CSS_PROTOCOLS_NAV)
        waitLoadProgressDone(browser.selenium)
        time.sleep(2)
        rcode = browser.selenium.click(selector=ProtocolDetail.CSS_DETAIL_SELECTOR)
        waitLoadProgressDone(browser.selenium)
        time.sleep(2)
        rcode= browser.selenium.findSingleCSS(selector=ProtocolDetail.CSS_HEADER)
        
        if "Protocol Detail" not in rcode.text:
            assert False, logging.critical('Protocols Detail Header has incorrect name')
        for css in ProtocolDetail.CSS_BULK_CHECK:
            logging.info('Finding Protocol edit Details CSS element: {}'.format(css))
            if not browser.selenium.findSingleCSS(selector=css, timeout=3):
                assert False, logging.critical('Expected Protocols Details CSS element {}'.format(css))
                break
        
    '''






