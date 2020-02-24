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
    
#from ui.alerts.zbUIAlerts import Alerts
from common.zbSelenium import zbSelenium
from common.zbCommon import rerunIfFail, getHostname
#from common.zbNetSecTool import nmapScanHostPort
#from common.zbKafka import zbKafka
from ui.dashboard.zbUIDashboardSummary import DashboardSummary
from common.zbConfig import defaultEnv, NUMBER_RETRIES, DELAY_SECONDS, SCREENSHOT_ON_FAIL
from locator.alert import AlertListLocators, AlertDetailsLocators, VulnerabilityLocators
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
def browser(browser_factory_smoke, tenant):
    browser = browser_factory_smoke(DashboardSummary, custom_payload=tenant)
    return browser["selenium"]

@pytest.fixture(scope="module", params=["policy", "threat"])
def generate_alert(request):
    alert_type = request.param
    kwars = {}
    kwars['alert_type'] = '{0}_alert'.format(alert_type)

    # Add your custom keyword arguments, for example
    # kwars['severity'] = 'high'
    kwars['tenantid'] = zbat_tenant_id
    if alert_type == 'policy':
        if 'testing' in nodeEnv:
            kwars['ruleid'] = '5a26f42fc8272f0b00c5ef2f'
        elif 'staging' in nodeEnv:
            kwars['ruleid'] = '5a26f45b9849c50d000b857e'

    alert_name = "Automated zbat {0} alert name at unix time {1}".format(alert_type, time.time())
    alert_description = "Automated zbat {0} alert description at unix time {1}".format(alert_type, time.time())
    kwars['name'] = alert_name
    kwars['description'] = alert_description

    kafka = zbKafka()
    response = kafka.sendAlert(**kwars)

    print(('Alert name: {}'.format(alert_name)))
    print(('Alert description: {}'.format(alert_description)))
    print(('response: {}'.format(response)))

    # Leave time for server to send email and sms
    time.sleep(20)
    return kwars


class Test_Alerts:

    @pytest.mark.parametrize("testid", ["C362706"])
    @pytest.mark.parametrize("test_id", ["alert_table"])
    @pytest.mark.smoke
    def test_alert_ui(self, testid, test_id,browser_smoke, tenant):
        if browser_smoke.selenium.driver.capabilities["browserName"] == "internet explorer":
            pytest.skip()
        url =  urlparse(browser_smoke.selenium.driver.current_url)
        rcode = browser_smoke.selenium.getURL(url.scheme+"://"+url.netloc+"/guardian/policies/alerts")
        waitLoadProgressDone(browser_smoke.selenium)
        clickSpecificTimerange(browser_smoke.selenium, specific="1 Week")
        for css in AlertListLocators.CSS_ALERT_INV_CARD_LIST:
            logging.info('Finding Alert Page CSS element: {}'.format(css))
            if not browser_smoke.selenium.findSingleCSS(selector=css, timeout=3):
                assert False, logging.critical('Expected Alert Page CSS element {}'.format(css))
                break

    @pytest.mark.parametrize("testid", ["C362707"])
    @pytest.mark.parametrize("test_id", ["alert_page"])
    @pytest.mark.smoke
    def test_alert_page_ui(self, testid, test_id, browser_smoke, tenant):
        if browser_smoke.selenium.driver.capabilities["browserName"] == "internet explorer":
            pytest.skip()
        url =  urlparse(browser_smoke.selenium.driver.current_url)
        rcode = browser_smoke.selenium.getURL(url.scheme+"://"+url.netloc+"/guardian/policies/alerts")
        waitLoadProgressDone(browser_smoke.selenium)
        clickSpecificTimerange(browser_smoke.selenium, specific="1 Week")
        for css in AlertDetailsLocators.CSS_ALERT_DETAIL_CARD_LIST:
            logging.info('Finding Alert Page CSS element: {}'.format(css))
            if not browser_smoke.selenium.findSingleCSS(selector=css, timeout=3):
                assert False, logging.critical('Expected Alert Page CSS element {}'.format(css))

    @pytest.mark.parametrize("testid", ["C362709"])
    @pytest.mark.parametrize("test_id", ["alert_details"])
    @pytest.mark.smoke
    def test_alert_details_ui(self, testid, test_id,browser_smoke, tenant):
        browser = browser_smoke
        if browser.selenium.driver.capabilities["browserName"] == "internet explorer":
            pytest.skip()
        url =  urlparse(browser.selenium.driver.current_url)
        rcode = browser.selenium.getURL(url.scheme+"://"+url.netloc+"/guardian/policies/alerts")
        waitLoadProgressDone(browser.selenium)
        clickSpecificTimerange(browser_smoke.selenium, specific="1 Week")
        time.sleep(2)
        browser.selenium.click(selector=AlertListLocators.CSS_EXPAND_ALERT)
        waitLoadProgressDone(browser.selenium)
        browser.selenium.click(selector=AlertListLocators.CSS_CLICK_ALERT)
        waitLoadProgressDone(browser.selenium)
        browser.selenium.switchToLatestWindow()
        time.sleep(2)
        for css in AlertDetailsLocators.CSS_ALERT_DETAIL_FEATURE_LIST:
            logging.info('Finding Alert Details CSS element: {}'.format(css))
            if not browser.selenium.findSingleCSS(selector=css, timeout=3):
                assert False, logging.critical('Expected Alert Details CSS element {}'.format(css))
                break
    @pytest.mark.parametrize("testid", ["C362710"])
    @pytest.mark.parametrize("test_id", ["vuln_ui"])
    @pytest.mark.smoke
    def test_vulnerability_ui(self, testid, test_id,browser_smoke, tenant):
        browser = browser_smoke
        if browser.selenium.driver.capabilities["browserName"] == "internet explorer":
            pytest.skip()
        url =  urlparse(browser.selenium.driver.current_url)
        rcode = browser.selenium.getURL(url.scheme+"://"+url.netloc+"/guardian/risks/vulnerabilities")
        waitLoadProgressDone(browser.selenium)
        for css in VulnerabilityLocators.CSS_VULN_FEATURE_LIST:
            logging.info('Finding Vuln Page CSS element: {}'.format(css))
            if not browser.selenium.findSingleCSS(selector=css, timeout=3):
                assert False, logging.critical('Expected Vulnerability Page CSS element {}'.format(css))
                break

    @pytest.mark.parametrize("testid", ["C362711"])
    @pytest.mark.parametrize("test_id", ["vuln_details"])
    @pytest.mark.smoke
    def test_vulnerability_details(self, testid, test_id,browser_smoke, tenant):
        browser = browser_smoke
        if browser.selenium.driver.capabilities["browserName"] == "internet explorer":
            pytest.skip()
        url =  urlparse(browser.selenium.driver.current_url)
        rcode = browser.selenium.getURL(url.scheme+"://"+url.netloc+"/guardian/risks/vulnerabilities/CVE-1999-0524")
        waitLoadProgressDone(browser.selenium)
        for css in VulnerabilityLocators.CSS_VULN_DETAIL_LIST:
            logging.info('Finding Vulnerability Details CSS element: {}'.format(css))
            if not browser.selenium.findSingleCSS(selector=css, timeout=3):
                assert False, logging.critical('Expected Vulnerability Details CSS element {}'.format(css))
                break


    @pytest.mark.skipif("kaiyihuang" not in getHostname() and "zbat003" not in getHostname(),reason="Not in zbat003")
    @pytest.mark.parametrize("filetype", ["pdf","xlsx"])
    def test_AlertActionDownload(self,browser,filetype):
        selenium = browser["selenium"]
        assert rerunIfFail(function=selenium.checkAlertDownload(filetype), selenium=selenium.selenium )

    @pytest.mark.skipif("kaiyihuang" not in getHostname() and "zbat003" not in getHostname(),reason="Not in zbat003")
    @pytest.mark.parametrize("filetype", ["csv"])
    def test_AlertListDownload(self,browser,filetype):
        selenium = browser["selenium"]
        assert rerunIfFail(function=selenium.checkAlertListDownload(filetype), selenium=selenium.selenium )

    def test_AlertActionAddNotes(self, browser):
        selenium = browser["selenium"]
        assert rerunIfFail(function=selenium.configAlertAction(alertName="test", currentStatus="pending", action="add notes"), selenium=selenium.selenium, screenshot=SCREENSHOT_ON_FAIL, testname=zbathome+'artifacts/test_AlertActionAddNotes.png', number=NUMBER_RETRIES, delay=DELAY_SECONDS) == True
    
    def test_AlertActionAssign(self, browser):
        selenium = browser["selenium"]
        assert rerunIfFail(function=selenium.configAlertAction(alertName="test", currentStatus="pending", action="assign"), selenium=selenium.selenium, screenshot=SCREENSHOT_ON_FAIL, testname=zbathome+'artifacts/test_AlertActionAssign.png', number=NUMBER_RETRIES, delay=DELAY_SECONDS) == True

    def test_AlertSeries(self, browser):
        selenium = browser["selenium"]
        assert rerunIfFail(function=selenium.checkTimeSeries(), selenium=selenium.selenium, screenshot=SCREENSHOT_ON_FAIL, testname=zbathome+'artifacts/test_AlertSeries.png', number=NUMBER_RETRIES, delay=DELAY_SECONDS) == True

    def test_AlertFilterByIoT(self, browser):
        selenium = browser["selenium"]
        assert rerunIfFail(function=selenium.checkIoTDevice(), selenium=selenium.selenium, screenshot=SCREENSHOT_ON_FAIL, testname=zbathome+'artifacts/test_AlertFilterByIoT.png', number=NUMBER_RETRIES, delay=DELAY_SECONDS) == True

    def test_AlertSite(self, browser):
        selenium = browser["selenium"]
        assert rerunIfFail(function=selenium.checkSites(), selenium=selenium.selenium, screenshot=SCREENSHOT_ON_FAIL, testname=zbathome+'artifacts/test_AlertSite.png', number=NUMBER_RETRIES, delay=DELAY_SECONDS) == True

    def test_AlertSeverity(self, browser):
        selenium = browser["selenium"]
        assert rerunIfFail(function=selenium.checkAlertSeverity(), selenium=selenium.selenium, screenshot=SCREENSHOT_ON_FAIL, testname=zbathome+'artifacts/test_AlertSeverity.png', number=NUMBER_RETRIES, delay=DELAY_SECONDS) == True

    def test_AlertEntries(self, browser):
        selenium = browser["selenium"]
        assert rerunIfFail(function=selenium.checkEntries(), selenium=selenium.selenium, screenshot=SCREENSHOT_ON_FAIL, testname=zbathome+'artifacts/test_AlertEntries.png', number=NUMBER_RETRIES, delay=DELAY_SECONDS) == True    

    def test_AlertNumbers(self, browser):
        selenium = browser["selenium"]
        assert rerunIfFail(function=selenium.checkAlertNumbers(), selenium=selenium.selenium, screenshot=SCREENSHOT_ON_FAIL, testname=zbathome+'artifacts/test_AlertNumbers.png', number=NUMBER_RETRIES, delay=DELAY_SECONDS) == True

    @pytest.mark.skipif(os.environ["HOME"] not in ["/home/automation"],reason="Not in zbat003")
    def test_AlertExport(self, browser):
        selenium = browser["selenium"]
        assert rerunIfFail(function=selenium.checkAlertExport(), selenium=selenium.selenium, screenshot=SCREENSHOT_ON_FAIL, testname=zbathome+'artifacts/test_AlertExport.png', number=NUMBER_RETRIES, delay=DELAY_SECONDS) == True
    
    @pytest.mark.skipif(os.environ['NODE_ENV'] in ['production'], reason='Skip because Production might not have enough alert for pagination test')
    def test_AlertPagination(self, browser):
        selenium = browser["selenium"]
        assert rerunIfFail(function=selenium.checkAlertPagination(), selenium=selenium.selenium, screenshot=SCREENSHOT_ON_FAIL, testname=zbathome+'artifacts/test_AlertPagination.png', number=NUMBER_RETRIES, delay=DELAY_SECONDS) == True

    def test_AlertDetails(self, browser):
        selenium = browser["selenium"]
        assert rerunIfFail(function=selenium.checkAlertDetails(), selenium=selenium.selenium, screenshot=SCREENSHOT_ON_FAIL, testname=zbathome+'artifacts/test_AlertDetails.png', number=NUMBER_RETRIES, delay=DELAY_SECONDS) == True

    @pytest.mark.skip(os.environ['NODE_ENV'] in ['production'], reason="Disable for now until Jeffrey fix this test")
    def test_AlertActionEditPolicy(self, browser):
        selenium = browser["selenium"]
        assert rerunIfFail(function=selenium.checkAlertActionEditPolicy(), selenium=selenium.selenium, screenshot=SCREENSHOT_ON_FAIL, testname=zbathome+'artifacts/test_AlertActionEditPolicy.png', number=NUMBER_RETRIES, delay=DELAY_SECONDS) == True

    def test_AlertActionResolve(self, browser):
        selenium = browser["selenium"]
        assert rerunIfFail(function=selenium.configAlertAction(alertName="test", currentStatus="pending", action="resolve"), selenium=selenium.selenium, screenshot=SCREENSHOT_ON_FAIL, testname=zbathome+'artifacts/test_AlertActionResolve.png', number=NUMBER_RETRIES, delay=DELAY_SECONDS) == True    

    def test_AlertActionBlock(self, browser):
        selenium = browser["selenium"]
        assert rerunIfFail(function=selenium.configAlertAction(alertName="test", currentStatus="pending", action="block"), selenium=selenium.selenium, screenshot=SCREENSHOT_ON_FAIL, testname=zbathome+'artifacts/test_AlertActionBlock.png', number=NUMBER_RETRIES, delay=DELAY_SECONDS) == True

    def test_AlertActionSIEM(self, browser):
        selenium = browser["selenium"]
        assert rerunIfFail(function=selenium.configAlertAction(alertName="test", currentStatus="pending", action="siem"), selenium=selenium.selenium, screenshot=SCREENSHOT_ON_FAIL, testname=zbathome+'artifacts/test_AlertActionSIEM.png', number=NUMBER_RETRIES, delay=DELAY_SECONDS) == True

    @pytest.mark.skipif(os.environ['NODE_ENV'] in ['production'], reason='Skip because cannot access Kafka on production env to generate alert')
    @pytest.mark.aims
    @pytest.mark.bugs
    def test_AlertActionAIMS(self, generate_alert, browser):
        selenium = browser["selenium"]
        kwargs = {
            'server': env['aimsServer'],
            'token': env['aimsToken'],
            "inspector": env["inspector"]
        }
        assert rerunIfFail(function=selenium.configAlertAction(alertName="test", currentStatus="pending", action="aims", **kwargs), selenium=selenium.selenium, screenshot=SCREENSHOT_ON_FAIL, testname=zbathome+'artifacts/test_AlertActionAIMS.png', number=NUMBER_RETRIES, delay=DELAY_SECONDS) == True



    @pytest.mark.skipif(os.environ['NODE_ENV'] in ['production'], reason='Skip because cannot access Kafka on production env to generate alert')
    @pytest.mark.aims
    @pytest.mark.bugs
    def test_AlertActionAIMSDidSentToServer(self, generate_alert, browser):
        selenium = browser["selenium"]
        kwargs = {
            'server': env['aimsServer'],
            'token': env['aimsToken'],
            "inspector": env["inspector"],
            'facility': 'SOUTH',
            'tag': '1002'
        }
        assert rerunIfFail(function=selenium.checkAlertActionAIMSDidSentToServer(**kwargs), selenium=selenium.selenium, screenshot=SCREENSHOT_ON_FAIL, testname=zbathome+'artifacts/test_AlertActionAIMSDidSentToServer.png', number=NUMBER_RETRIES, delay=DELAY_SECONDS) == True



    @pytest.mark.skipif(os.environ['NODE_ENV'] in ['production'], reason='Skip because cannot access Kafka on production env to generate alert')
    @pytest.mark.bugs
    def test_AlertActionSIEMDidSentToServer(self, generate_alert, browser):
        selenium = browser["selenium"]
        kwargs = {
            'host': env['splunk'],
            'port': env['splunk_port'],
            'splunk_username': env['splunk_username'],
            'splunk_pwd': env['splunk_pwd']
        }
        if nmapScanHostPort(kwargs['host'], kwargs['port']):
            assert rerunIfFail(function=selenium.checkAlertActionSIEMDidSentToServer(**kwargs), selenium=selenium.selenium, screenshot=SCREENSHOT_ON_FAIL, testname=zbathome+'artifacts/test_AlertActionSIEMDidSentToServer.png', number=NUMBER_RETRIES, delay=DELAY_SECONDS) == True
        else:
            print("Check Splunk, host {} port {}.  Either reverse ssh tunnel, or splunk server is down".format(kwargs['host'], kwargs['port']))
            assert False == True


    @pytest.mark.skipif(os.environ['NODE_ENV'] in ['production'], reason='Skip because cannot access Kafka on production env to generate alert')
    def test_AlertActionBlockDidSentToServer(self, browser):
        # Manually trigger sending fake policy alert
        class Request:
            param = 'policy'
        generate_alert(Request)

        selenium = browser["selenium"]
        kwargs = {
            'host': env['panfw_host'],
            'panfw_username': env['panfw_username'],
            'panfw_pwd': env['panfw_pwd']
        }
        host, port = kwargs['host'].split(':')
        if nmapScanHostPort(host, port):
            assert rerunIfFail(function=selenium.checkAlertActionBlockDidSentToServer(**kwargs), selenium=selenium.selenium, screenshot=SCREENSHOT_ON_FAIL, testname=zbathome+'artifacts/test_AlertActionBlockDidSentToServer.png', number=NUMBER_RETRIES, delay=DELAY_SECONDS) == True
        else:
            print("Check PanFW, host {} port {}.  Either reverse ssh tunnel, or PanFW is down".format(host, port))
            assert False == True            


    @pytest.mark.skipif(os.environ['NODE_ENV'] in ['production'], reason='Skip because cannot access Kafka on production env to generate alert')
    @pytest.mark.connectiv
    @pytest.mark.bugs
    def test_AlertActionConnectivDidSentToServer(self, generate_alert, browser):
        selenium = browser["selenium"]
        kwargs = {
            'connectiv_uname': env['connectiv_uname'],
            'connectiv_pwd': env['connectiv_pwd'],
            'connectiv_client_id': env['connectiv_client_id'],
            'connectiv_client_secret': env['connectiv_client_secret'],
            'connectiv_client_url': env['connectiv_client_url']
        }
        assert rerunIfFail(function=selenium.checkAlertActionConnectivDidSentToServer(**kwargs), selenium=selenium.selenium, screenshot=SCREENSHOT_ON_FAIL, testname=zbathome+'artifacts/test_AlertActionConnectivDidSentToServer.png', number=NUMBER_RETRIES, delay=DELAY_SECONDS) == True
