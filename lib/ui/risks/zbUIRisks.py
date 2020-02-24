import re
import time
import locale
import os
from enum import Enum
from urllib.parse import urlparse
from common.zbSelenium import zbSelenium
from selenium.common.exceptions import StaleElementReferenceException, NoSuchElementException
from ui.login.zbUILoginCore import Login
from locator.navigator import NavMenuLoc
from locator.navigator import ToolBarLoc
from locator.risks import RisksVulnerabilitiesLoc, RisksRecallsLoc
from ui.zbUIShared import checkElement, checkElementText
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

locale.setlocale( locale.LC_ALL, 'en_US.UTF-8' )


class ZOOM_DIRECTION(Enum):
    IN = 'zoom_in',
    OUT = 'zoom_out'


class RisksVulnerabilities():

    def __init__(self, **kwargs):
        self.params = kwargs
        self.selenium = Login(**kwargs).login()
        self.baseurl = kwargs["url"]+'/'

    def gotoRisksVulnPage(self):
        # Go to Risks Vulnerability Page
        logger.info('Go to Risks Vulnerability Page')
        css = NavMenuLoc.CSS_RISKS
        ele = self.selenium.findSingleCSSNoHover(selector=css, timeout=0)
        checkElementText(ele, css, "risks") 
        self.selenium.hoverElement(ele)

        css = RisksVulnerabilitiesLoc.CSS_RISKS_VULNERABILITIES
        ele = self.selenium.findSingleCSSNoHover(selector=css, timeout=0)
        checkElementText(ele, css, "vulnerabilities") 
        ele.click()
        self.selenium.waitCSS(selector=RisksVulnerabilitiesLoc.CSS_RISKS_VULN_LIST)
        cur_url = self.selenium.current_url()
        assert "/risks/vulnerabilities" in cur_url, "/risks/vulnerabilities should be in {}".format(cur_url)

    def gotoRisksRecallsPage(self):
        # Go to Risks Recalls Page
        logger.info('Go to Risks Recalls Page')
        css = NavMenuLoc.CSS_RISKS
        ele = self.selenium.findSingleCSSNoHover(selector=css, timeout=0)
        checkElementText(ele, css, "risks") 
        self.selenium.hoverElement(ele)

        css = RisksRecallsLoc.CSS_RISKS_RECALL
        ele = self.selenium.findSingleCSSNoHover(selector=css, timeout=0)
        if (os.environ['NODE_ENV']) != 'testing':
            if not ele:
                logger.warning("RECALLS page is NOT available for testing")
                return True

        checkElementText(ele, css, "recalls")
        ele.click()
        self.selenium.waitCSS(selector=RisksRecallsLoc.CSS_RISKS_RECALL_TABLE)
        cur_url = self.selenium.current_url()
        assert "/risks/recall" in cur_url, "/risks/recall should be in {}".format(cur_url)

    def verifyRisksVulnTopSec(self):
        # Verify the top sections of Risks Vulnerability -- title & Global Filter
        self.gotoRisksVulnPage()
        logger.info('Verify the top sections of Risks Vulnerability -- title & Global Filter')

        css = RisksVulnerabilitiesLoc.CSS_RISKS_VULN_TITLE
        ele = self.selenium.findSingleCSS(selector=css, timeout=0)
        self.selenium.hoverElement(ele)
        checkElementText(ele, css, "vulnerabilities") 

        css = RisksVulnerabilitiesLoc.CSS_RISKS_VULN_GLOBAL_FILTER
        ele = self.selenium.findSingleCSSNoHover(selector=css, timeout=0)
        checkElement(ele, css)
        ele_text = ele.text.split("\n")
        css = RisksVulnerabilitiesLoc.CSS_RISKS_VULN_GLOBAL_FILTER_TEXT
        assert ele_text == css, "{} should be {}".format(ele_text, css)
        return True

    def verifyRisksVulnSummary(self):
        # Verify Risks Vulnerability -- Summary Part
        logger.info('Verify Risks Vulnerability -- Summary Part')

        # To save some time, don't go to VulnPage again, since this is not the first test to be executed
        # self.gotoRisksVulnPage()

        # Verify Vulnerability Summary Card shows up
        css = RisksVulnerabilitiesLoc.CSS_RISKS_VULN_SUMMARY_CARD
        if not self.selenium.findSingleCSS(selector=css):
            logger.error('Unable to find Vulnerability Summnary Card')
            return False

        #Verify Severity table exists
        if not self.selenium.findSingleCSS(selector=RisksVulnerabilitiesLoc.CSS_RISK_VULN_SUMMARY_CARD_SEVERITY_TABLE):
            logger.error('Unable to find Severity table in Vulnerability Summnary Card')
            return False
         
        #Verify severity label correct
        severityList = ["Critical","High","Medium","Low"] 
        eles = self.selenium.findMultiCSSNoHover(selector=RisksVulnerabilitiesLoc.CSS_RISKS_VULN_SUMMARY_CARD_SEVERITY_TEXT)
        for i,ele in enumerate(eles):
            assert eles[i].text.strip() == severityList[i]
        
        #Verify sum of vulnerability count  matches to total vulnerability count
        eles = self.selenium.findMultiCSSNoHover(selector=RisksVulnerabilitiesLoc.CSS_RISKS_VULN_SUMMARY_CARD_VULNERABILITY_COUNT) 
        totalCount = 0
        for ele in eles:
            assert isinstance(locale.atoi(ele.text), int), "{} should be digits".format(ele.text) 
            totalCount = totalCount + int(ele.text)
          
        eles = self.selenium.findSingleCSS(selector=RisksVulnerabilitiesLoc.CSS_RISKS_VULN_SUMMARY_CARD_VULNERABILITY_NUM_TOTAL)
        assert int(eles.text) == totalCount, "Total vulnerability count {} is not matched to {}".format(eles.text, str(totalCount))

        css = RisksVulnerabilitiesLoc.CSS_RISKS_VULN_STAT_CONFIRMED
        eles = self.selenium.findMultiCSSNoHover(selector=css, timeout=0)
        for ele in eles:
            text = re.match(r'(\d+)\s+(\w+)', ele.text)
            assert isinstance(locale.atoi(text.group(1)), int), "{} should be digits".format(text.group(1))
            assert 'Confirmed' == text.group(2), "{} should be Confirmed".format(text.group(2))

        return True

    def verifyRisksVulnTable(self):
        # Verify Risks Vulnerability -- Table
        logger.info('Verify Risks Vulnerability -- Table')

        # To save some time, don't go to VulnPage again, since this is not the first test to be executed
        # self.gotoRisksVulnPage()
        eles = self.selenium.findSingleCSS(selector=RisksVulnerabilitiesLoc.CSS_RISKS_VULN_SUMMARY_CARD_VULNERABILITY_NUM_TOTAL)

        css = RisksVulnerabilitiesLoc.CSS_RISKS_VULN_TABLE
        ele = self.selenium.findSingleCSS(selector=css, timeout=0)
        ele_text = ele.text.split("\n")
        assert "Vulnerabilities (" + eles.text + ")" == ele_text[0], "{} should be Vulnerabilities".format(ele_text[0], css)
        css = RisksVulnerabilitiesLoc.CSS_RISKS_VULN_TABLE_HEADER
        assert css == ele_text[1:12], "{} should be {}".format(ele_text[1:12], css)
        return True

    def verifyRisksRecalls(self):
        # Verify Risks Vulnerability -- Table
        logger.info('Verify Risks Vulnerability -- Recalls')
        if self.gotoRisksRecallsPage():
            return True

        css = RisksRecallsLoc.CSS_RISKS_RECALL_TITLE
        ele = self.selenium.findSingleCSS(selector=css, timeout=0)
        checkElementText(ele, css, "recalls")

        css = RisksRecallsLoc.CSS_RISKS_RECALL_TABLE_TITLE
        ele = self.selenium.findSingleCSS(selector=css, timeout=0)
        ele_text = ele.text.split(" ")
        assert "Recall" == ele_text[0], "{} should be Recall".format(ele_text[0], css)
        assert re.match(r'\(\d+\)', ele_text[1]), "{} should be () with number inside".format(ele_text[1])

        css = RisksRecallsLoc.CSS_RISKS_RECALL_TABLE_HEADER
        ele = self.selenium.findSingleCSS(selector=css, timeout=0)
        ele_text = ele.text.split("\n")
        text = RisksRecallsLoc.CSS_RISKS_RECALL_TABLE_HEADER_TEXT
        assert text == ele_text, "{} should be {}".format(ele_text, text)

        return True

    def close(self):
        if self.selenium:
            self.selenium.quit()
