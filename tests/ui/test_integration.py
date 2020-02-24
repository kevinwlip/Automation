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

from common.zbSelenium import zbSelenium
from common.zbCommon import rerunIfFail, getHostname
from ui.dashboard.zbUIDashboardSummary import DashboardSummary
from common.zbConfig import defaultEnv, NUMBER_RETRIES, DELAY_SECONDS, SCREENSHOT_ON_FAIL
from locator.integration import IntegrationSelectors, IntegrationAsset, IntegrationSIEM, IntegrationNAC,IntegrationManagement, IntegrationFirewall, IntegrationSOAR, IntegrationMSS, IntegrationVulnScan, IntegrationWLAN
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


class Test_Integration:

    @pytest.mark.parametrize("testid",["C362799"])
    @pytest.mark.parametrize("test_id", ["integration"])
    @pytest.mark.smoke
    def test_integration_main(self,testid,test_id,browser_smoke, tenant):
        browser = browser_smoke
        derk = True
        foundit = False
        rcode1 = browser.selenium.findSingleCSS(selector=IntegrationSelectors.CSS_INTEGRATION_NAV)
        rcode2 = browser.selenium.findMultiCSS(selector=IntegrationSelectors.CSS_NAV_ALL)
        rcode1 = browser.selenium.findSingleCSS(selector=IntegrationSelectors.CSS_INTEGRATION_NAV)
        for code in rcode2:
            if code.text == "All":
                browser.selenium.hoverElement(rcode1)
                code.click()
                waitLoadProgressDone(browser.selenium)
                foundit = True
                break
        if not foundit:
            derk= False

        foundit = False
        rcode = browser.selenium.findMultiCSS(selector=IntegrationSelectors.CSS_INTEGRATION_MAIN_CARDS)
        if len(rcode) != 9:
            logging.critical("Integration Card number wrong")
            derk= False
        
        rcode[0].click()
        #waitLoadProgressDone(browser.selenium)
        rcode1 = self.test_integration_asset_management(test_id,browser, tenant)
        if not rcode1:
            derk= False

        browser.selenium.driver.back()
        waitLoadProgressDone(browser.selenium)

        rcode = browser.selenium.findMultiCSS(selector=IntegrationSelectors.CSS_INTEGRATION_MAIN_CARDS)
        rcode[1].click()
        time.sleep(3)
        #waitLoadProgressDone(browser.selenium)
        rcode1 = self.test_integration_nac(test_id,browser, tenant)
        if not rcode1:
            derk= False

        browser.selenium.driver.back()
        waitLoadProgressDone(browser.selenium)

        rcode = browser.selenium.findMultiCSS(selector=IntegrationSelectors.CSS_INTEGRATION_MAIN_CARDS)
        rcode[2].click()
        time.sleep(3)
        #waitLoadProgressDone(browser.selenium)
        rcode1 = self.test_integration_network_management(test_id,browser, tenant)
        if not rcode1:
            derk= False

        browser.selenium.driver.back()
        waitLoadProgressDone(browser.selenium)
        rcode = browser.selenium.findMultiCSS(selector=IntegrationSelectors.CSS_INTEGRATION_MAIN_CARDS)
        rcode[3].click()
        time.sleep(3)
        waitLoadProgressDone(browser.selenium)
        rcode1 = self.test_integration_siem(test_id,browser, tenant)
        if not rcode1:
            derk= False

        browser.selenium.driver.back()
        waitLoadProgressDone(browser.selenium)
        rcode = browser.selenium.findMultiCSS(selector=IntegrationSelectors.CSS_INTEGRATION_MAIN_CARDS)
        rcode[4].click()
        time.sleep(3)
        #waitLoadProgressDone(browser.selenium)
        rcode1 = self.test_integration_firewall(test_id,browser, tenant)
        if not rcode1:
            derk= False

        browser.selenium.driver.back()
        waitLoadProgressDone(browser.selenium)
        rcode = browser.selenium.findMultiCSS(selector=IntegrationSelectors.CSS_INTEGRATION_MAIN_CARDS)
        rcode[5].click()
        time.sleep(3)
        #waitLoadProgressDone(browser.selenium)
        rcode1 = self.test_integration_soar(test_id,browser, tenant)
        if not rcode1:
            derk= False

        browser.selenium.driver.back()
        waitLoadProgressDone(browser.selenium)
        rcode = browser.selenium.findMultiCSS(selector=IntegrationSelectors.CSS_INTEGRATION_MAIN_CARDS)
        rcode[6].click()
        time.sleep(3)
        #waitLoadProgressDone(browser.selenium)
        rcode1 = self.test_integration_mss(test_id,browser, tenant)
        if not rcode1:
            derk= False

        browser.selenium.driver.back()
        waitLoadProgressDone(browser.selenium)
        rcode = browser.selenium.findMultiCSS(selector=IntegrationSelectors.CSS_INTEGRATION_MAIN_CARDS)
        rcode[7].click()
        time.sleep(3)
        #waitLoadProgressDone(browser.selenium)
        rcode1 = self.test_integration_scans(test_id,browser, tenant)
        if not rcode1:
            derk = False
        
        browser.selenium.driver.back()
        waitLoadProgressDone(browser.selenium)
        
        rcode = browser.selenium.findMultiCSS(selector=IntegrationSelectors.CSS_INTEGRATION_MAIN_CARDS)
        rcode[8].click()
        waitLoadProgressDone(browser.selenium)
        rcode1 = self.test_integration_wlan(test_id,browser, tenant)
        if not rcode1:
            derk= False

        assert derk

        



        



    @pytest.mark.parametrize("test_id", ["asset_manage"])
    def test_integration_asset_management(self,test_id,browser_smoke, tenant):
        browser = browser_smoke
        rcode = browser.selenium.findMultiCSS(selector=IntegrationAsset.CSS_ASSET_CARD)
        firstcard = rcode[0]
        secondcard = rcode[1]
        rcode = browser.selenium.findMultiCSS(selector=IntegrationAsset.CSS_SELECTOR_VENDOR_IMAGE)
        if len(rcode) == 0: #There is an asset selected
            rcode = browser.selenium.findMultiCSS(browserobj=firstcard,selector=IntegrationAsset.CSS_ELEMENT_PROPERTY)
            if len(rcode) < 4:
                print (len(rcode))
                logging.critical("Asset Management missing info lines")
                return False
        else:
            rcode = browser.selenium.findMultiCSS(browserobj=firstcard,selector=IntegrationAsset.CSS_SELECTOR_ASSET_IMAGE)
            if len(rcode) < 3:
                logging.critical("Asset Management missing vendor images")
                return False

        rcode = browser.selenium.findMultiCSS(browserobj=secondcard,selector=IntegrationAsset.CSS_PROPERTY_TITLE)
        if len(rcode) < 4:
            logging.critical("ServiceNow missing info lines")
            return False
        if "ServiceNow" not in secondcard.text:
            logging.critical("ServiceNow missing title")
            return False
        return True

                

        #ServiceNow

    @pytest.mark.parametrize("test_id", ["siem"])
    def test_integration_siem(self,test_id,browser_smoke, tenant):
        browser = browser_smoke
        rcode = browser.selenium.findSingleCSS(selector=IntegrationSIEM.CSS_SIEM_DISABLED)
        if rcode:
            logging.critical("SIEM disabled")
            return True
        rcode = browser.selenium.findSingleCSS(selector=IntegrationSIEM.CSS_EDIT_PART)
        if not rcode:
            logging.critical("SIEM missing edit buttons")
            return False

        browser.selenium.findSingleCSS(selector=IntegrationSIEM.CSS_SIEM_CARD)
        rcode = browser.selenium.findSingleVisibleCSS(selector=IntegrationSIEM.CSS_SIEM_TITLE)
        if not "SIEM" in rcode.text:
            print(rcode.text)
            logging.critical("SIEM Title incorrect")
            return False
        rcode = browser.selenium.findMultiCSS(selector=IntegrationSIEM.CSS_INK_RIPPLE)
        if len(rcode) < 3:
            logging.critical("SIEM missing checkmark")
            return False
        rcode = browser.selenium.findMultiCSS(selector=IntegrationSIEM.CSS_INFO_ELEMENTS)
        if len(rcode) < 3:
            logging.critical("SIEM missing info lines")
            return False
        return True



    @pytest.mark.parametrize("test_id", ["nac"])
    def test_integration_nac(self,test_id,browser_smoke, tenant):
        browser = browser_smoke
        rcode1 = browser.selenium.findMultiCSS(selector=IntegrationNAC.CSS_ASSET_CARD)
        if not rcode1:
            logging.critical("NAC missing card")
            return False
        
        rcode2 = browser.selenium.findSingleCSS(selector=IntegrationNAC.CSS_EDIT_PART)
        if not rcode2:
            logging.critical("NAC missing edit buttons")
            return False
        
        rcode1 = browser.selenium.findMultiCSS(selector=IntegrationNAC.CSS_ASSET_CARD)
        for ind,card in enumerate(rcode1):
            for word in IntegrationNAC.check_words[ind]:
                if word not in card.text:
                    #logging.critical("NAC missing labels {}".format(word))
                    #return False Will worry about this later
                    pass
        return True

    @pytest.mark.parametrize("test_id", ["network management"])
    def test_integration_network_management(self,test_id,browser_smoke, tenant):
        browser = browser_smoke
        rcode1 = browser.selenium.findMultiCSS(selector=IntegrationManagement.CSS_ASSET_CARD)
        if not rcode1:
            logging.critical("Network Management missing card")
            return True
        
        rcode2 = browser.selenium.findSingleCSS(selector=IntegrationManagement.CSS_EDIT_PART)
        if not rcode2:
            logging.critical("Network Management missing edit buttons")
            return False
        
        for ind,card in enumerate(rcode1):
            for word in IntegrationManagement.check_words[ind]:
                if word not in card.text:
                    logging.critical("Network Management missing labels {}".format(word))
                    return False
        return True

    @pytest.mark.parametrize("test_id", ["firewall"])
    def test_integration_firewall(self,test_id,browser_smoke, tenant):
        browser=browser_smoke
        rcode = browser.selenium.findSingleCSS(selector=IntegrationFirewall.CSS_TITLE)
        if "Enforcement" not in rcode.text:
            logging.critical("Firewall missing title")
            return False
        rcode1 = browser.selenium.findSingleCSS(selector=IntegrationFirewall.CSS_FIREWALL_CARD)
        if not rcode:
            logging.critical("No firewall implemented")
            pytest.skip()
        rcode = browser.selenium.findSingleCSS(browserobj=rcode1,selector=IntegrationFirewall.CSS_CARD_PROVIDER)
        if not rcode:
            logging.critical("Missing firewall provider image")
        for word in IntegrationFirewall.checkwords:
            if word not in rcode1.text:
                logging.critical("Firewall missing labels {}".format(word))
                return False
        return True

    @pytest.mark.parametrize("test_id", ["soar"])
    def test_integration_soar(self,test_id,browser_smoke, tenant):
        browser = browser_smoke
        rcode1 = browser.selenium.findMultiCSS(selector=IntegrationSOAR.CSS_ASSET_CARD)
        if not rcode1:
            logging.critical("SOAR missing card")
            return False
        rcode2 = browser.selenium.findSingleCSS(selector=IntegrationSOAR.CSS_EDIT_PART)
        if not rcode2:
            logging.critical("SOAR missing edit buttons")
            return False
        for ind,card in enumerate(rcode1):
            for word in IntegrationSOAR.check_words[ind]:
                if word not in card.text:
                    logging.critical("SOAR missing labels {}".format(word))
                    return False
        return True

    @pytest.mark.parametrize("test_id", ["mss"])
    def test_integration_mss(self,test_id,browser_smoke, tenant):
        browser = browser_smoke
        rcode = browser.selenium.findSingleCSS(selector=IntegrationMSS.CSS_CARD_TITLE)
        if not rcode or "Symantec" not in rcode.text:
            print(rcode.text)
            logging.critical("Managed Services missing card title")
            return False
        rcode = browser.selenium.findSingleCSS(selector=IntegrationMSS.CSS_TOGGLE, waittype="visibility")
        if not rcode:
            logging.critical("Managed Services missing toggle")
            return False
        rcode = browser.selenium.findSingleCSS(selector=IntegrationMSS.CSS_EDIT_PART, waittype="visibility")
        if not rcode:
            logging.critical("Managed Services missing edit option")
            return False
        rcode = browser.selenium.findSingleCSS(selector=IntegrationMSS.CSS_CARD)
        for word in IntegrationMSS.check_words:
            if word not in rcode.text:
                #logging.critical("Managed Services missing labels {}".format(word))
                #return False Will worry about this later
                pass
        return True

    @pytest.mark.parametrize("test_id", ["vulnscans"])
    def test_integration_scans(self,test_id,browser_smoke, tenant):
        browser = browser_smoke
        rcode = browser.selenium.findMultiCSS(selector=IntegrationVulnScan.CSS_CARD)
        
        for card in rcode:

            card_title = browser.selenium.findSingleCSS(selector=IntegrationVulnScan.CSS_CARD_TITLE)
            if not card_title:
                logging.critical("Missing title in Vulnerability Scans Page")
                for lol in IntegrationVulnScan.check_sets:
                    if card_title == lol[0]:
                        for ele in lol[1:]:
                            if ele not in card.text:
                                logging.critical(card_title + " panel in Vuln Scans missing label: ",format(ele))
                                return False
            rcode2 = browser.selenium.findSingleCSS(selector=IntegrationVulnScan.CSS_EDIT_PART)
            if not rcode2:
                logging.critical("Vuln Scans missing edit option")
                return False
            rcode2 = browser.selenium.findSingleCSS(selector=IntegrationVulnScan.CSS_VENDOR_IMAGE)
            if not rcode2:
                logging.critical("Vuln Scans missing vendor image")
                return False
        return True

    @pytest.mark.parametrize("test_id", ["wlan"])
    def test_integration_wlan(self,test_id,browser_smoke, tenant):
        browser=browser_smoke
        rcode = browser.selenium.findSingleCSS(selector=IntegrationSelectors.CSS_MAIN_TITLE)
        if "Wireless Network" not in rcode.text:
            print(rcode.text)
            logging.critical("WLAN missing title")
            return False
        rcode = browser.selenium.findSingleCSS(selector=IntegrationWLAN.CSS_ADD_BUTTON)
        if not rcode:
            logging.critical("WLAN missing add button")
            return False
        rcode1 = browser.selenium.findSingleCSS(selector=IntegrationWLAN.CSS_WLAN_CARD)
        if not rcode1:
            logging.critical("No WLAN implemented")
            pytest.skip()
        rcode1 = browser.selenium.findSingleCSS(selector=IntegrationWLAN.CSS_WLAN_CARD)
        for word in IntegrationWLAN.checkwords:
            if word not in rcode1.text:
                logging.critical("WLAN missing labels {}".format(word))
                return False
        return True


