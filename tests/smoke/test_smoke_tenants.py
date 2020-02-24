#!/usr/bin/python

import pdb, json, sys, os, pytest, datetime, random, calendar, time, copy
from collections import OrderedDict

try:
    env = os.environ['ZBAT_HOME']
except:
    print('Test cannot run.  Please export ZBAT_HOME.')
    sys.exit()

if env+'lib' not in sys.path:
    sys.path.append(env+'lib')
from ui.dashboard.zbUIDashboardSummary import DashboardSummary
from common.zbSelenium import zbSelenium
from common.zbConfig import defaultEnv, NUMBER_RETRIES, DELAY_SECONDS, SCREENSHOT_ON_FAIL
from common.zbCommon import rerunIfFail
from zb_logging import logger as logging
from ui.zbUIShared import *
from urllib.parse import urlparse

'''
Old test_smoke_tenants.py code

# env = defaultEnv()
# socportal = env["socportal"]
# if not socportal: print 'SOC portal value not set in zbCommon.py'; sys.exit()

# fixture
# a mixture of tenants from x1 and x2 setup
#@pytest.fixture(scope="module", params=["baycare", "grundfos", "unitedregional", "brainerdbaptist"])
# @pytest.fixture(scope="module", params=["baycare", "waubonsee", "demo"])
# Currently running on Soho only.  Don't enable real tenant test, without considerting changing code. 
# Current username/password is for Soho only.  Had case in the past where superuser password change 
#  causing constant login to customer with wrong password.  That's why disable this test for real tenant
'''

@pytest.fixture(scope='module', params=['soho'])
def tenant(request):
    config = {}
    config["url"] = "https://"+str(request.param)+".zingbox.com/login"
    if "demo" in config["url"]:
        config["username"] = os.environ["ZBAT_DEMO_UNAME"]
        config["password"] = os.environ["ZBAT_DEMO_PWD"]
    else:
        config["username"] = os.environ["ZBAT_PROD_UNAME"]
        config["password"] = os.environ["ZBAT_PROD_PWD"]
        
    config["comparestrict"] = False
    return config

@pytest.fixture(scope="module")
def browser(browser_factory_smoke, tenant):
    browser = browser_factory_smoke(DashboardSummary, custom_payload=tenant)
    return browser["selenium"]


class Test_UI:

    '''
    Old UI smoke tests

    # @pytest.mark.skip("Skip UI test due to Risk Score column changes in Device Detail page")
    # def test_dashboard_ui(self, browser_factory, tenant):

    #     browser = browser_factory(Dashboard, custom_payload=tenant)
    #     selenium = browser["selenium"]
    #     # need to add back all time range once released
    #     #rcode = selenium.checkTimeSeries()
    #     if "demo" in tenant["url"]:
    #         rcode = selenium.checkTimeSeries(specific=["2 Hour", "1 Day", "1 Week"])
    #     else:
    #         rcode = selenium.checkTimeSeries(specific=["2 Hour", "1 Day", "1 Week", "1 Month", "1 Year", "ALL"])
    #     assert rcode == True

    # @pytest.mark.skip("Skip UI test due to Risk Score column changes in Device Detail page")
    # def test_device_inventory_ui(self, browser_factory, tenant):
    #     browser = browser_factory(DeviceInventory, custom_payload=tenant)
    #     selenium = browser["selenium"]
    #     rcode = selenium.checkDeviceLink()
    #     assert rcode == True
    '''

    def test_dashboard_ui(self, browser, tenant):
        #after login smoke test should check that each UI element is loaded
        #the details of each card might change so only checking that these exist for now
        if browser.selenium.driver.capabilities["browserName"] == "internet explorer":
            pytest.skip()
        # Dashboard V1 REMOVE AFTER BETA
        ################################
        if browser.selenium.findSingleCSS(selector="[ng-model='dashboardController.dashboard_type']", timeout=3):

            #Dashboard V1
            '''
            global filter
            sites
            series bar
            risk assessment
            network summary
            devices by category
            external endpoints
            '''

            check_css = [
                "zing-profile-selector",
                ".category-listing-selector",
                ".highcharts-plot-background",
                ".dashboard-summary-item zing-gauge-meter",
                ".highcharts-plot-background",
                ".dashboard-summary-item.network-summary",
                "zing-devices-pie-chart",
                "zing-map-base"
            ]

            logging.info('Dashboard version 1.0')
            for css in check_css:
                #log message that this is Dashboard V1
                #log message to show which CSS we are searching
                logging.info('Finding CSS element: {}'.format(css))
                
                if not browser.selenium.findSingleCSS(selector=css, timeout=2):
                    assert False, logging.critical('Expected CSS element {}'.format(css))
                    break

            return True

        ################################


        #Dashboard V2
        '''
        Dashboard tab selection
        global filter
        top bar
        applications
        network segments
        risk overview
        alerts
        vulnerabilities
        '''

        check_css = [
            'zing-dashboard-tabs',
            'zing-global-filter.ng-star-inserted',
            "[data-id='dashboard-overall'] .dashboard-card-content",
            "[data-id='dashboard-devices'] .dashboard-card-content",
            "[data-id='dashboard-sites'] .dashboard-card-content",
            "[data-id='dashboard-app-protocols'] .dashboard-card-content",
            "[data-id='dashboard-vlans-summary'] .dashboard-card-content",
            "[data-id='dashboard-risk-score-trend'] .dashboard-card-content",
            "[data-id='dashboard-alerts'] .dashboard-card-content"
        ]
        check_class = [
            "ngx-dnd-container components-drop-container",
            "ngx-dnd-item move-disabled overall ng-star-inserted",
            "ngx-dnd-item move-disabled ng-star-inserted",
            "ngx-dnd-item even move-disabled ng-star-inserted",
            "ngx-dnd-item odd move-disabled ng-star-inserted"
        ]
        
        for css in check_css:
            logging.info('Finding Executive CSS element: {}'.format(css))
            
            if not browser.selenium.findSingleCSS(selector=css, timeout=3):
                assert False, logging.critical('Expected CSS element {}'.format(css))
                break

        url =  urlparse(browser.selenium.driver.current_url)
        rcode = browser.selenium.getURL(url.scheme+"://"+url.netloc+"/guardian/dashboard/security")
        waitLoadProgressDone(browser.selenium)
        check_security_css = [
            ".date-range-wrap",
            ".dashboard-summary-item.left.small-height-ie-item.flex-50",
            ".dashboard-summary-item.left.small-height-ie-item.flex-50",
            ".dashboard-summary-item.small-height-ie-item.right.network-summary.flex-50",
            ".left.height-ie-item.ng-isolate-scope.flex-50",
            ".right.height-ie-item.ng-isolate-scope.flex-50",
            ".layout-row.ml",
            ".ml.ng-scope.layout-row"
        ]
        for css in check_security_css:
            logging.info('Finding Security CSS element: {}'.format(css))
            
            if not browser.selenium.findSingleCSS(selector=css, timeout=3):
                assert False, logging.critical('Expected CSS element {}'.format(css))
                break

        
        '''
        for classy in check_class:
            logging.info('Finding CSS element: {}'.format(classy))
            if not browser.selenium.findSingleClass(selector=classy, timeout=3):
                assert False, logging.critical('Expected Class element {}'.format(classy))
                break
                '''

    
    def test_soc_ui(self, soc_browser, tenant):
        if soc_browser.selenium.driver.capabilities["browserName"] == "internet explorer":

            pytest.skip()
        url =  urlparse(browser.selenium.driver.current_url)
        rcode = browser.selenium.getURL(url.scheme+"://"+url.netloc+"/guardian/monitor/inventory")
        waitLoadProgressDone(browser.selenium)
        check_css = [
            ".dashboard-card.component-container.mat-card.ng-star-inserted",
            ".content_body.ng-scope.layout-column",
            "[ng-if='!ctrl.fullTableType.noTimeRange']",
            "zing-inventory-downloader",
            "[icon='file_upload'][ng-click='ctrl.uploadFile()']",
            "[ng-show='!ctrl.searchToggle']"
            "[name='inventory']"
        ]
        for css in check_css:
            logging.info('Finding Device Inventory CSS element: {}'.format(css))
            if not browser.selenium.findSingleCSS(selector=css, timeout=3):
                assert False, logging.critical('Expected Device Inventory CSS element {}'.format(css))
                break

    def test_device_detail_ui(self,browser, tenant):
        if browser.selenium.driver.capabilities["browserName"] == "internet explorer":
            pytest.skip()
        url =  urlparse(browser.selenium.driver.current_url)
        rcode = browser.selenium.getURL(url.scheme+"://"+url.netloc+"/guardian/monitor/inventory/device/VTJGc2RHVmtYMTlyZHM1UFh1RnR6UFdNc0pCcWJNdkJJcW5kQ2NPMUh5NklMY1R2ci9tYThzQ1BVeFZiMkpRQQ%3D%3D")
        waitLoadProgressDone(browser.selenium)
        check_css = [
            ".mat-card",
            ".device-detail-overall-ml.device-detail-overall._md",
            ".device-detail-overall-ml.device-detail-overall.secondary-card._md",
            ".device-traffic-network-loader.zing-card-container",
            ".left.height-ie-item.ng-isolate-scope.flex-50",
            ".graph-selector",
            "._md.ng-scope.md-active.md-no-scroll"
        ]
        for css in check_css:
            logging.info('Finding Device Detail CSS element: {}'.format(css))
            if not browser.selenium.findSingleCSS(selector=css, timeout=3):
                assert False, logging.critical('Expected Device Detail CSS element {}'.format(css))
                break


                break

    def test_alert_details_ui(self,browser, tenant):
        if browser.selenium.driver.capabilities["browserName"] == "internet explorer":
            pytest.skip()
        url =  urlparse(browser.selenium.driver.current_url)
        rcode = browser.selenium.getURL(url.scheme+"://"+url.netloc+"/guardian/policies/alerts")
        waitLoadProgressDone(browser.selenium)
        check_css = [
            ".mat-card .content",
            ".alert-head._md",
            ".impacted-device.ng-scope",
            ".device-detail-overall-ml.device-detail-overall._md",
            ".device-detail-overall-ml.device-detail-overall.secondary-card._md"
        ]
        for css in check_css:
            logging.info('Finding Alert Details CSS element: {}'.format(css))
            if not browser.selenium.findSingleCSS(selector=css, timeout=3):
                assert False, logging.critical('Expected Alert Details CSS element {}'.format(css))
                break

    def test_vulnerability_ui(self,browser, tenant):
        if browser.selenium.driver.capabilities["browserName"] == "internet explorer":
            pytest.skip()
        url =  urlparse(browser.selenium.driver.current_url)
        rcode = browser.selenium.getURL(url.scheme+"://"+url.netloc+"/guardian/policies/alerts")
        waitLoadProgressDone(browser.selenium)
        check_css = [
            ".mat-card"
            ".vulnerability-summary._md",
            ".zingTable.zing-table-vulnerabilityList"
        ]
        for css in check_css:
            logging.info('Finding Vuln Page CSS element: {}'.format(css))
            if not browser.selenium.findSingleCSS(selector=css, timeout=3):
                assert False, logging.critical('Expected Vulnerability Page CSS element {}'.format(css))
                break
    @pytest.mark.parametrize("test_id",["vuln_details"])
    def test_vulnerability_details(self,test_id,browser, tenant):
        if browser.selenium.driver.capabilities["browserName"] == "internet explorer":
            pytest.skip()
        url =  urlparse(browser.selenium.driver.current_url)
        rcode = browser.selenium.getURL(url.scheme+"://"+url.netloc+"/guardian/policies/alerts")
        waitLoadProgressDone(browser.selenium)
        check_css = [
            "._md.summary-card",
            ".vulnerability-detail-page .table"
        ]
        for css in check_css:
            logging.info('Finding Vulnerability Details CSS element: {}'.format(css))
            if not browser.selenium.findSingleCSS(selector=css, timeout=3):
                assert False, logging.critical('Expected Vulnerability Details CSS element {}'.format(css))
                break

    """
    https://soho.zingbox.com/guardian/report/reportsAndLogs/reports
    https://soho.zingbox.com/guardian/report/reportsAndLogs/logs
    https://soho.zingbox.com/guardian/report/reportsAndLogs/scanReports
    """
    '''
    @pytest.mark.parametrize("test_id")
    def test_reports_ui(self,test_id,browser, tenant):
        if browser.selenium.driver.capabilities["browserName"] == "internet explorer":
            pytest.skip()
        url =  urlparse(browser.selenium.driver.current_url)
        rcode = browser.selenium.getURL(url.scheme+"://"+url.netloc+"/guardian/report/reportsAndLogs/reports")
        waitLoadProgressDone(browser.selenium)
        check_css = [
            ".report-list",

        ]

        rcode = browser.selenium.getURL(url.scheme+"://"+url.netloc+"/guardian/report/reportsAndLogs/logs")
        waitLoadProgressDone(browser.selenium)

        rcode = browser.selenium.getURL(url.scheme+"://"+url.netloc+"/guardian/report/reportsAndLogs/scanReports")
        waitLoadProgressDone(browser.selenium)
    '''



