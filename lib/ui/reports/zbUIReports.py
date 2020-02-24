import re, pdb
from common.zbSelenium import zbSelenium
from selenium.common.exceptions import StaleElementReferenceException, NoSuchElementException
from ui.login.zbUILoginCore import Login
from locator.navigator import NavMenuLoc
from locator.navigator import ToolBarLoc
from locator.dashboard import DashboardSummaryLoc ### Remove Later ###
from locator.reports import ReportsLoc, ReportsTabLoc, LogsTabLoc, ScanReportsTabLoc
from ui.zbUIShared import waitLoadProgressDone, checkElement, checkElementText
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class Reports():

    def __init__(self, **kwargs):
        self.params = kwargs
        self.selenium = Login(**kwargs).login()

    def verifyReports(self):
        #Navigate to the Reports Page
        css = NavMenuLoc.CSS_REPORTS
        ele = self.selenium.findSingleCSSNoHover(selector=css, timeout=0)
        ele.click()
        self.selenium.waitCSS(selector=ReportsTabLoc.CSS_REPORTS_TAB_TITLE)

        # Verify the URL of the Reports Page with initial Reports Tab
        logger.info('Verify the URL of the Reports Page with initial Reports Tab')
        assert self.selenium.is_current_url("/report/myreports")

        # Verify the title of the Reports Page
        logger.info('Verify the title of the Reports Page')
        css = ReportsLoc.CSS_REPORTS_HEADER_TITLE
        ele = self.selenium.findSingleCSSNoHover(selector=css, timeout=0)
        checkElementText(ele, css, "reports & logs")

        # Verify the tabs of the Reports Page
        logger.info('Verify the tabs of the Reports Page')
        css = ReportsLoc.CSS_REPORTS_TABS
        tabs = self.selenium.findMultiCSSNoHover(selector=css, timeout=0)
        checkElementText(tabs[0], css, "reports")

        checkElementText(tabs[1], css, "logs")

        checkElementText(tabs[2], css, "vulnerability scan reports")

        return True

    def verifyReportsTab(self):
        # Clicks on Nav Menu Reports Tab
        css = NavMenuLoc.CSS_REPORTS
        ele = self.selenium.findSingleCSSNoHover(selector=css, timeout=0)
        ele.click()
        self.selenium.waitCSS(selector=ReportsTabLoc.CSS_REPORTS_TAB_TITLE)

        # Verify the title of the Reports Tab
        logger.info('Verify the title of the Reports Tab')
        css = ReportsTabLoc.CSS_REPORTS_TAB_TITLE
        title = self.selenium.findMultiCSSNoHover(selector=css, timeout=0)
        title = title[0].text + title[1].text
        title = title.split()
        assert title[0].lower() == 'reports', "'Reports' title not found"

        reports_num = re.search(r'\(\d+\)', title[1])
        assert reports_num.group() in title[1], "Reports number {} could not be found".format(reports_num.group())

        # Verify the filters of the Reports Tab
        logger.info('Verify the filters of the Reports Tab')
        css = ReportsTabLoc.CSS_REPORTS_CONTENT_FILTERS
        filters = self.selenium.findMultiCSSNoHover(selector=css, timeout=0)
        checkElementText(filters[0], css, "all frequencies")

        checkElementText(filters[1], css, "all configs")

        assert "sites" in filters[2].text.lower(),  "'Sites' keyword not found"

        # Verify the date elements of the Reports Tab
        logger.info('Verify the date elements of the Reports Tab')
        css = ReportsTabLoc.CSS_REPORTS_CALENDAR_ICON
        icon = self.selenium.findSingleCSSNoHover(selector=css, timeout=0)
        checkElement(icon, css)

        css = ReportsTabLoc.CSS_REPORTS_DATE_FROM_TO
        from_to = self.selenium.findMultiCSSNoHover(selector=css, timeout=0)
        checkElementText(from_to[0], css, "from")
        
        checkElementText(from_to[1], css, "to")
        
        css = ReportsTabLoc.CSS_REPORTS_START_DATE
        start_date = self.selenium.findSingleCSSNoHover(selector=css, timeout=0)
        checkElement(start_date, css)

        css = ReportsTabLoc.CSS_REPORTS_END_DATE
        end_date = self.selenium.findSingleCSSNoHover(selector=css, timeout=0)
        checkElement(end_date, css)

        css = ReportsTabLoc.CSS_REPORTS_ROTATE_ARROW
        rotate_arrow = self.selenium.findSingleCSSNoHover(selector=css, timeout=0)
        checkElement(rotate_arrow, css)
        
        css = ReportsTabLoc.CSS_REPORTS_PAGE_RANGE
        page_range = self.selenium.findSingleCSSNoHover(selector=css, timeout=0)

        page_phrase = re.search(r'\d+ to \d+ of \d+', page_range.text)
        assert page_phrase.group() in page_range.text, "Page phrase {} could not be found".format(page_phrase.group())

        css = ReportsTabLoc.CSS_REPORTS_PAGE_ARROWS
        page_arrows = self.selenium.findMultiCSSNoHover(selector=css, timeout=0)
        
        arr_num = 0
        for arrow in page_arrows:
            try:
                checkElementText(page_arrows[arr_num], css, "navigate_before")
                checkElementText(page_arrows[arr_num+1], css, "navigate_next")
                break
            except:
                print("Page Arrows could not be found")
            arr_num += 1

        return True

    def verifyLogsTab(self):
        # Clicks on Nav Menu Reports Tab
        css = NavMenuLoc.CSS_REPORTS
        ele = self.selenium.findSingleCSSNoHover(selector=css, timeout=0)
        ele.click()
        self.selenium.waitCSS(selector=LogsTabLoc.CSS_LOGS_TAB_TITLE)

        css = ReportsLoc.CSS_REPORTS_TABS
        ele = self.selenium.findMultiCSSNoHover(selector=css, timeout=0)
        ele[1].click()
        self.selenium.waitCSS(selector=LogsTabLoc.CSS_LOGS_TAB_TITLE)

        # Verify the URL of the Logs Tab
        logger.info('Verify the URL of the Logs Tab')
        assert self.selenium.is_current_url("/report/reportsAndLogs")

        # Verify the title of the Logs Tab
        logger.info('Verify the title of the Logs Tab')
        css = LogsTabLoc.CSS_LOGS_TAB_TITLE
        title = self.selenium.findSingleVisibleCSS(selector=css, timeout=3)
        title = title.text
        #print(title)
        title = title.lower()

        assert 'logs' in title, "'Logs' title not found"

        logs_num = re.search('\(\d+\)', title)
        assert logs_num.group() in title, "Logs number {} could not be found".format(logs_num.group())

        # Verify the column headers of the Logs Tab
        logger.info('Verify the column headers of the Logs Tab')
        css = LogsTabLoc.CSS_LOGS_COL_HEADERS
        col_headers = self.selenium.findMultiCSSNoHover(selector=css, timeout=0)
        checkElementText(col_headers[0], css, "device")
        checkElementText(col_headers[1], css, "log name")
        checkElementText(col_headers[2], css, "type")
        checkElementText(col_headers[3], css, "time range")
        checkElementText(col_headers[4], css, "status")

        return True

    def verifyScanReportsTab(self):
        # Clicks on Nav Menu Reports Tab
        css = NavMenuLoc.CSS_REPORTS
        ele = self.selenium.findSingleCSSNoHover(selector=css, timeout=0)
        ele.click()
        self.selenium.waitCSS(selector=LogsTabLoc.CSS_LOGS_TAB_TITLE)

        css = ReportsLoc.CSS_REPORTS_TABS
        ele = self.selenium.findMultiCSSNoHover(selector=css, timeout=0)
        ele[2].click()
        self.selenium.waitCSS(selector=LogsTabLoc.CSS_LOGS_TAB_TITLE)

        # Verify the URL of the Vulnerability Scan Reports Tab
        logger.info('Verify the URL of the Vulnerability Scan Reports Tab')
        assert self.selenium.is_current_url("/report/reportsAndLogs")

        # Verify the title of the Vulnerability Scan Reports Tab
        logger.info('Verify the title of the Vulnerability Scan Reports Tab')
        css = LogsTabLoc.CSS_LOGS_TAB_TITLE
        title = self.selenium.findMultiCSSNoHover(selector=css, timeout=0)
        titley = ""
        for x in title:
            titley = titley + x.text
        titley = titley.split()
        scans_title = titley[0] + " " + titley[1] + " " + titley[2]
        assert scans_title.lower() == 'vulnerability scan reports', "'Vulnerability Scan Reports' title not found"

        scans_num = re.search(r'\(\d+\)', titley[3])
        assert scans_num.group() in titley[3], "Vulnerability Scan Reports number {} could not be found".format(scans_num.group())
        
        # Verify the column headers of the Vulnerability Scan Reports Tab
        logger.info('Verify the column headers of the Vulnerability Scan Reports Tab')
        css = ScanReportsTabLoc.CSS_SCAN_REPORTS_COL_HEADERS
        col_headers = self.selenium.findMultiCSSNoHover(selector=css, timeout=0)
        checkElementText(col_headers[0], css, "scanned device")

        checkElementText(col_headers[1], css, "report name")

        checkElementText(col_headers[2], css, "scan type")

        checkElementText(col_headers[3], css, "status")

        checkElementText(col_headers[4], css, "user name")

        return True

    def close(self):
        if self.selenium:
            self.selenium.quit()
