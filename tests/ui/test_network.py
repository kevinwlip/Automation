#!/usr/bin/python

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
from locator.network import NetworkSelectors
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


class Test_Network:
    @pytest.mark.parametrize("test_id", ["network_page"])
    @pytest.mark.parametrize("testid",["C362803"])
    @pytest.mark.smoke
    def test_network_main(self,test_id, testid, browser_smoke, tenant):
        browser = browser_smoke
        if browser.selenium.driver.capabilities["browserName"] == "internet explorer":
            pytest.skip()
        url =  urlparse(browser.selenium.driver.current_url)
        rcode = browser.selenium.click(selector=NetworkSelectors.CSS_NETWORK_NAV)
        waitLoadProgressDone(browser.selenium)
        time.sleep(2)
        for css in NetworkSelectors.CSS_BULK_ELEMENTS:
            logging.info('Finding Alert Details CSS element: {}'.format(css))
            if not browser.selenium.findSingleCSS(selector=css, timeout=3):
                assert False, logging.critical('Expected Network CSS element {}'.format(css))
                break
        rcode = browser.selenium.findSingleCSS(selector=NetworkSelectors.CSS_PAGE_TITLE)
        if not "Network" in rcode.text:
            assert False, logging.critical('Network title incorrect')
        rcode = browser.selenium.findSingleCSS(selector=NetworkSelectors.CSS_BLOCK_TITLE)
        if not "Subnet" in rcode.text:
            assert False, logging.critical('Network subtitle incorrect')
        assert True
