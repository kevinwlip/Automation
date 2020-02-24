#!/usr/bin/python


'''
Author: Kaiyi Huang
Revision: 08/29/2019
'''

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
    
#from ui.alerts.zbUIAlerts import Alerts
from common.zbSelenium import zbSelenium
from common.zbCommon import rerunIfFail, getHostname
#from common.zbNetSecTool import nmapScanHostPort
#from common.zbKafka import zbKafka
from ui.dashboard.zbUIDashboardSummary import DashboardSummary
from common.zbConfig import defaultEnv, NUMBER_RETRIES, DELAY_SECONDS, SCREENSHOT_ON_FAIL
from locator.policies import PoliciesPage
from ui.zbUIPolicies import Policies
from urllib.parse import urlparse
from ui.zbUIShared import *
env = defaultEnv()

# fixture
'''
@pytest.fixture(scope="module")
def browser(browser_factory):
    return browser_factory(Alerts)


    '''


@pytest.fixture(scope='module')
def tenant(request):
    config = {}
    config["url"] = env["uiportal"]+"?tenantid="+env["tenantid"]
    print(config["url"])
    if "demo" in config["url"]:
        config["username"] = os.environ["ZBAT_DEMO_UNAME"]
        config["password"] = os.environ["ZBAT_DEMO_PWD"]
    elif "testing" in config["url"]:
        config["username"] = os.environ["ZBAT_TESTING_UNAME"]
        config["password"] = os.environ["ZBAT_TESTING_PWD"]
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

@pytest.fixture(scope="module")
def browser(browser_factory, tenant):
    browser = browser_factory(Policies, custom_payload=tenant)
    return browser["selenium"] 
'''
https://testing-soho.zingbox.com/guardian/policies
https://testing-soho.zingbox.com/guardian/policies/new
'''


class Test_Policies:
    @pytest.mark.bugs
    @pytest.mark.parametrize("testid",["C359379"])
    @pytest.mark.parametrize("test_id", ["policy_reg"])
    @pytest.mark.regression
    def test_policy_reg(self, testid, test_id,browser, tenant):
         assert rerunIfFail(function=browser.verifyPolicy(),
                           selenium=browser.selenium,
                           screenshot=SCREENSHOT_ON_FAIL,
                           testname=zbathome + 'artifacts/test_Policies.png',
                           number=NUMBER_RETRIES,
                           delay=DELAY_SECONDS)


    @pytest.mark.parametrize("testid",["C362802"])
    @pytest.mark.parametrize("test_id", ["policy_page"])
    @pytest.mark.smoke
    def test_policy_main(self, testid, test_id,browser_smoke, tenant):
        browser = browser_smoke
        if browser.selenium.driver.capabilities["browserName"] == "internet explorer":
            pytest.skip()
        url =  urlparse(browser.selenium.driver.current_url)
        rcode = browser.selenium.click(selector=PoliciesPage.CSS_POLICY_NAV)
        #rcode = browser.selenium.getURL(url.scheme+"://"+url.netloc+"/guardian/policies")
        waitLoadProgressDone(browser.selenium)
        time.sleep(2)
        for css in PoliciesPage.CSS_POLICIES_MAIN_CHECKS:
            logging.info('Finding Alert Details CSS element: {}'.format(css))
            if not browser.selenium.findSingleCSS(selector=css, timeout=3):
                assert False, logging.critical('Expected Policies Page CSS element {}'.format(css))
                break

    @pytest.mark.parametrize("testid",["C362800"])
    @pytest.mark.parametrize("test_id", ["policy_add_new"])
    @pytest.mark.smoke
    def test_policy_add(self, testid, test_id,browser_smoke, tenant):
        browser = browser_smoke
        if browser.selenium.driver.capabilities["browserName"] == "internet explorer":
            pytest.skip()
        url =  urlparse(browser.selenium.driver.current_url)
        rcode = browser.selenium.click(selector=PoliciesPage.CSS_POLICY_NAV)
        waitLoadProgressDone(browser.selenium)
        time.sleep(2)
        rcode = browser.selenium.click(selector=PoliciesPage.CSS_POLICY_ADD)
        waitLoadProgressDone(browser.selenium)
        for css in PoliciesPage.CSS_POLICIES_DETAIL_CHECKS:
            logging.info('Finding Alert Details CSS element: {}'.format(css))
            if not browser.selenium.findSingleCSS(selector=css, timeout=3):
                assert False, logging.critical('Expected Policies Details CSS element {}'.format(css))
                break

    @pytest.mark.parametrize("testid",["C362801"])
    @pytest.mark.parametrize("test_id", ["policy_edit"])
    @pytest.mark.smoke
    def test_policy_edit(self, testid, test_id,browser_smoke, tenant):
        browser = browser_smoke
        if browser.selenium.driver.capabilities["browserName"] == "internet explorer":
            pytest.skip()
        url =  urlparse(browser.selenium.driver.current_url)
        #rcode = browser.selenium.getURL(url.scheme+"://"+url.netloc+"/guardian/policies")
        rcode = browser.selenium.click(selector=PoliciesPage.CSS_POLICY_NAV)
        waitLoadProgressDone(browser.selenium)
        time.sleep(2)
        browser.selenium.click(selector=PoliciesPage.CSS_POLICY_SELECTOR)
        waitLoadProgressDone(browser.selenium)
        for css in PoliciesPage.CSS_POLICIES_DETAIL_CHECKS:
            logging.info('Finding Alert Details CSS element: {}'.format(css))
            if not browser.selenium.findSingleCSS(selector=css, timeout=3):
                assert False, logging.critical('Expected Policies Details CSS element {}'.format(css))
                break






