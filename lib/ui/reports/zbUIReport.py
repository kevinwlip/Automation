#!/usr/bin/python

from ui.login.zbUILoginCore import Login
from ui.zbUIShared import *
from urllib.parse import urlparse
from selenium.common.exceptions import StaleElementReferenceException
from datetime import datetime
import time, re, pdb

#Ad-Hoc CSS Parameters


CSS_ADHOC_TAB_THINGY = "i.grey.ng-scope.material-icons"
CSS_ADHOC_REPORT_SELECTION = "ng-md-icon.grey[aria-label='Reports']"
CSS_ADHOC_SIDEBAR_REPORT_BUTTONS = "button.md-button[aria-label='Navigate to reports']"

CSS_ADHOC_BUTTON = 'span.selected-action-name.ng-binding'
CSS_ADHOC_RCONFIG_DISPLAY_NUMBER = "[ng-show='!ctrl.loading && !ctrl.fullTableType.tabName']"
CSS_ADHOC_MYREPORTS_DISPLAY_NUMBER = "span.zing-main-title.ng-binding"
CSS_ADHOC_CONFIRM_BUTTON = 'PLACEHOLDER: Confirmz'
CSS_ADHOC_EDIT_BUTTON = "i.dp36.ng-scope[pwk-event=''][title='Edit']"
CSS_ADHOC_TEMPLATE_SELECTION = "md-select.ng-valid[aria-invalid='false'][role='listbox'][ng-model='reportConfigPageCtrl.configData.template']"
CSS_ADHOC_NEW_DEVICE_SELECTION = "[name='Toggle New Device Only'] div.md-ink-ripple"
CSS_ADHOC_SEARCH_BUTTON = "ng-md-icon[name='search_toggle'][tooltip-text='Search'] svg"
CSS_ADHOC_SEARCH_BAR = "input#table-search"
CSS_ADHOC_REPORT_CONFIG_NAMES = "a.ng-binding"
CSS_ADHOC_CONFIG_CHECKBOXES = "ng-md-icon[name='select_button_click'][role='button']"
CSS_CHECKBOX_WRAPPER = "md-checkbox[name='Toggle New Device Only']"
CSS_UPDATE_BUTTON = "button[name='Update Report Config']"
CSS_FILTER_CHIP = "div.single-chip"

CSS_SUMMARY_REPORT_OPTION = "[category='Report Config'][value='SUMMARY_REPORT']"
CSS_CONNECTIVITY_REPORT_OPTION = "[category='Report Config'][value='CONNECTIVITY_REPORT']"

CSS_MYREPORT_NAMEFILTER = "md-select.report-option-selector[role='listbox'][ng-model='reportListCtrl.selectedConfig']"
CSS_MYREPORT_NAMES = "md-option[role='option'] div.md-text"

# global CSS parameters for UI > Report page
CSS_SELECTOR_REPORT_CONFIGS_INFO_COLUMNS = ['B','C','D','E','F','G','H']
CSS_SELECTOR_REPORT_CONFIGS_GENERAL_SORT_TEST = ['B','C','D','E','F','G','H']

CSS_SELECTOR_ADD_REPORT_CONFIG = "ng-md-icon[name='add']"
CSS_SELECTOR_REPORT_CONFIG_NAME_INPUT = "input[name='name']"
CSS_SELECTOR_REPORT_CONFIG_CREATE = "button[name='Create Report Config']"
CSS_SELECTOR_REPORT_CONFIG_ROW = "div.ui-grid-contents-wrapper > div[role='grid'] > div.ui-grid-viewport > div.ui-grid-canvas > div.ui-grid-row.ng-scope"
CSS_SELECTOR_REPORT_CONFIG_MENU = "ng-md-icon[name='select_button_click'][role='button']"
CSS_SELECTOR_REPORT_CONFIG_BUTTONS = "div[name='selected_action_handler'][role='button']"

CSS_REPORT_TEMPLATE_DROPDOWN = 'md-select[ng-model="reportConfigPageCtrl.configData.template"]'
CSS_REPORT_TEMPLATE_CONNECTIV_OPTION = 'md-option[category="Report Config"][value="CONNECTIVITY_REPORT"]'
CSS_REPORT_TEMPLATE_SUMMARY_OPTION = 'md-option[category="Report Config"][value="SUMMARY_REPORT"]'

CSS_REPORT_SCOPE_DROPDOWN = 'md-select[ng-model="reportConfigPageCtrl.configData.scope.type"]'
CSS_REPORT_SCOPE_ALL = 'md-option[name="Set report template type to ALL"]'
CSS_REPORT_SCOPE_SITE = 'md-option[name="Set report template type to SITE"]'
CSS_REPORT_SCOPE_DEVICETYPE = 'md-option[name="Set report template type to DEVICE_TYPE"]'

CSS_REPORT_TEMPLATE_NEW_DEVICE_CHECKBOX = 'md-checkbox[name="Toggle New Device Only"]'

CSS_REPORT_GEN_DROPDOWN = 'md-select[ng-model="reportConfigPageCtrl.configData.frequency"]'
CSS_REPORT_GEN_WEEKLY = 'md-option[name="Set report frequency to WEEKLY"]'
CSS_REPORT_GEN_MONTHLY = 'md-option[name="Set report frequency to MONTHLY"]'

CSS_REPORT_EMAIL_INPUT = 'input[aria-label="Chips input."]'

CSS_REPORT_COUNT = "[ng-show='!ctrl.loading && !ctrl.fullTableType.tabName']"

CSS_LIST_CHECKBOXES = "ng-md-icon[name='select_button_click'][role='button']"

CSS_REPORT_FILTER_BUTTON = "ng-md-icon[ns-popover-trigger='click'] svg[viewBox='0 0 24 24']"
CSS_FILTER_CHECKBOX_WRAPPER = "md-checkbox[role='checkbox']"
CSS_FILTER_CHECKBOX = "div.md-container"

CSS_DELETE_BUTTON = 'i[title="Delete"]'


def verifyReportConfigsEntries (browserobj, pageNumber=1, verifyAll=False):
    clickAllCheckboxes(browserobj)

    params = {}
    params["selector"] = CSS_SELECTOR_PAGINATION_INPUT
    pageNumber = min(pageNumber, int(browserobj.findSingleCSS(**params).get_attribute("max")))
    pageNumber = max(pageNumber, 1)
    if pageNumber > 1:
        for i in range(1, pageNumber):
            if verifyAll:
                params["selector"] = CSS_SELECTOR_INVENTORY_ROW
                rows = len(browserobj.findMultiCSS(**params))
                for c in CSS_SELECTOR_REPORT_CONFIGS_INFO_COLUMNS:
                    params["selector"] = CSS_SELECTOR_GENERAL_TEXT_ENTRY + c
                    ret = browserobj.findMultiCSS(**params)
                    if len(ret) != rows:
                        print("Failed Column " + c + " : Not enough entries")
                        return False
                    for ind, e in enumerate(ret):
                        if "".join(e.text.split()) == "":
                            if c == "E" or c == "F":
                                params["selector"] = CSS_SELECTOR_GENERAL_TEXT_ENTRY + "C"
                                temp = browserobj.findMultiCSS(**params)
                                if temp[ind].text == "Discovery Report":
                                    continue
                            print("Failed Column " + c) 
                            return False
            params["selector"] = CSS_SELECTOR_CHEVRON_RIGHT_ICON
            browserobj.click(**params)
            waitLoadProgressDone(browserobj)
    params["selector"] = CSS_SELECTOR_INVENTORY_ROW
    rows = len(browserobj.findMultiCSS(**params))
    for c in CSS_SELECTOR_REPORT_CONFIGS_INFO_COLUMNS:
        params["selector"] = CSS_SELECTOR_GENERAL_TEXT_ENTRY + c
        ret = browserobj.findMultiCSS(**params)
        if len(ret) != rows:
            print("Failed Column " + c + " : Not enough entries")
            return False
        for ind, e in enumerate(ret):
            if "".join(e.text.split()) == "":
                if c == "E" or c == "F":
                    params["selector"] = CSS_SELECTOR_GENERAL_TEXT_ENTRY + "C"
                    temp = browserobj.findMultiCSS(**params)
                    if temp[ind].text == "Discovery Report":
                        continue
                print("Failed Column " + c)
                return False
    return True


def verifyReportConfigsSort (browserobj):
    clickAllCheckboxes(browserobj)

    params = {}
    params["selector"] = CSS_SELECTOR_CLICKABLE_SORT_HEADER
    hsort = browserobj.findMultiCSS(**params)
    for l in CSS_SELECTOR_REPORT_CONFIGS_GENERAL_SORT_TEST:
        # click column header until head ascending order
        if not clickUntilFind(browserobj, hsort[ord(l)-ord("A")], CSS_SORT_UP_ARROW):
            print("Cannot find column up arrow button")
            return False
        waitLoadProgressDone(browserobj)
        params["selector"] = CSS_SELECTOR_GENERAL_TEXT_ENTRY + l
        data = browserobj.findMultiCSS(**params)
        _validateSortOrder('ascending', data)

        # click column header until head descending order
        if not clickUntilFind(browserobj, hsort[ord(l)-ord("A")], CSS_SORT_DOWN_ARROW):
            print("Cannot find column up arrow button")
            return False
        waitLoadProgressDone(browserobj)
        params["selector"] = CSS_SELECTOR_GENERAL_TEXT_ENTRY + l
        data = browserobj.findMultiCSS(**params)
        _validateSortOrder('descending', data)
    return True

def _validateSortOrder(sortingType, data):
    op = operator.gt
    if sortingType == 'descending':
        op = operator.lt

    for i in range(0,len(data)-1):
        if data[i].text == '' or data[i+1].text == '':
            # values are not necessary present.  If so, no need to compare
            continue

        topData = data[i].text
        bottomData = data[i + 1].text
        if isinstance(topData, int) or isinstance(topData, float):
            if op(int(topData), int(bottomData)):
                raise ValueError("Sort {} got value error {}   {}".format(sortingType, topData, bottomData))
        elif isinstance(topData, str):
            try:
                if op(datetime.strptime(topData, "%b %d, %Y, %H:%M"), datetime.strptime(bottomData, "%b %d, %Y, %H:%M")):
                    raise Exception("Sort {} datetime out of order {}   {}".format(sortingType, topData, bottomData))
                if op(datetime.strptime(topData, "%b %d, %Y"), datetime.strptime(bottomData, "%b %d, %Y")):
                    raise Exception("Sort {} datetime out of order {}   {}".format(sortingType, topData, bottomData))
            except ValueError:
                if op(data[i].text.lower(), data[i+1].text.lower()):
                    raise ValueError("Sort {}} got value error {}   {}".format(sortingType, topData, bottomData))
            except Exception as e:
                raise ValueError(e)


class Report():
    def __init__(self, **kwargs):
        self.params = kwargs
        self.selenium = Login(**kwargs).login()

    def gotoReport(self):
        url = urlparse(self.params["url"])
        rcode = self.selenium.getURL(url.scheme+'://'+url.netloc+'/reports/configlist')
        waitLoadProgressDone(self.selenium)                

    def checkEntries(self):
        self.gotoReport()
        rcode = verifyReportConfigsEntries(self.selenium)
        return rcode

    def checkPagination(self):
        self.gotoReport()
        rcode = verifyReportConfigsEntries(self.selenium, 2)
        return rcode

    def checkSort(self):
        self.gotoReport()
        rcode = verifyReportConfigsSort(self.selenium)
        return rcode

    def verifyReport(self, reportType='summary', newDevice=False, name='zbat testing report'):
        self.gotoReport()
        waitLoadProgressDone(self.selenium)
        rcode = self.checkReportExist(name)
        if rcode:
            rcode = self.configDeleteReport(name)
            if not rcode:
                print("Delete report "+str(name)+" has issue")
                return False

        origcount = self.findReportCount()
        if not origcount:
            print("Not able to find report count")
            return False

        rcode = self.configAddReport(reportType=reportType, newDevice=newDevice, name=name)
        if not rcode:
            print("Add report "+str(name)+" has issue")
            return False

        '''
        # disabling this check.  Since pytest run concurrently, a lot of report configuration 
        # takes place at once, so the increment count is not a reliable check.
        newcount = self.findReportCount()
        if not rcode:
            print "Not able to find report count"
            return False
        if newcount != origcount+1:
            print "After adding report, count {} did not increment".format(origcount)
            return False
        '''

        rcode = self.checkReportExist(name)
        if not rcode:
            print("Report name "+str(name)+" not found after added")
            return False

        rcode = self.configDeleteReport(name)
        if not rcode:
            print("Delete report "+str(name)+" has issue")
            return False

        return rcode

    def configAddReport(self, **kwargs):
        params = {"selector": CSS_SELECTOR_ADD_REPORT_CONFIG, "waittype":"visibility", "timeout":3}
        self.selenium.click(**params)
        time.sleep(1)

        # configure report type
        reportType = kwargs['reportType']
        if reportType == 'connectivity':
            self.selenium.click(selector=CSS_REPORT_TEMPLATE_DROPDOWN)
            self.selenium.click(selector=CSS_REPORT_TEMPLATE_CONNECTIV_OPTION)
        if reportType == 'summary':
            self.selenium.click(selector=CSS_REPORT_TEMPLATE_DROPDOWN)
            self.selenium.click(selector=CSS_REPORT_TEMPLATE_SUMMARY_OPTION)

        # configure name
        name = kwargs["name"] if "name" in kwargs else "zbat testing report"
        params["selector"] = CSS_SELECTOR_REPORT_CONFIG_NAME_INPUT
        #browserobj.findSingleCSS(**params).send_keys(Keys.CONTROL, "a")
        self.selenium.findSingleCSS(**params).clear()
        self.selenium.findSingleCSS(**params).send_keys(name)

        # configure scope
        params = {"selector":CSS_REPORT_SCOPE_DROPDOWN, "waittype":"visibility", "timeout":3}
        self.selenium.click(**params)
        scope = kwargs["scope"] if "scope" in kwargs else "all"
        if scope.strip().lower() == "all": css = CSS_REPORT_SCOPE_ALL
        if scope.strip().lower() == "site":  css = CSS_REPORT_SCOPE_SITE
        if scope.strip().lower() == "devicetype":  css = CSS_REPORT_SCOPE_DEVICETYPE
        params = {"selector":css, "waittype":"visibility", "timeout":3}
        self.selenium.click(**params)
        time.sleep(1)

        # configure new device checkbox
        if kwargs['newDevice'] == True:
            self.selenium.click(selector=CSS_REPORT_TEMPLATE_NEW_DEVICE_CHECKBOX, timeout=3)

        # configure generate time
        params = {"selector":CSS_REPORT_GEN_DROPDOWN, "waittype":"visibility", "timeout":3}
        self.selenium.click(**params)
        gentime = kwargs["time"] if "time" in kwargs else "weekly"
        if gentime.strip().lower() == "weekly":  css = CSS_REPORT_GEN_WEEKLY
        if gentime.strip().lower() == "monthly":  css = CSS_REPORT_GEN_MONTHLY
        params = {"selector":css, "waittype":"visibility", "timeout":3}
        self.selenium.click(**params)
        time.sleep(1)

        # configure email
        email = kwargs["email"] if "email" in kwargs else "zbat@qa.com"
        params = {"selector":CSS_REPORT_EMAIL_INPUT, "text":email}
        self.selenium.sendKeys(**params)

        # create
        params["selector"] = CSS_SELECTOR_REPORT_CONFIG_CREATE
        self.selenium.findSingleCSS(**params).click()
        time.sleep(5)
        waitLoadProgressDone(self.selenium)

        return True


    def configDeleteReport(self, name):
        params = {"selector": CSS_SELECTOR_REPORT_CONFIG_ROW, "waittype":"visibility", "timeout":5}
        el = self.selenium.findMultiCSS(**params)

        params = {"selector": CSS_LIST_CHECKBOXES, "waittype":"visibility", "timeout":5}
        boxes = self.selenium.findMultiCSS(**params)
        try:
            for enum, e in enumerate(el):
                if e.text.find(name) != -1:
                    boxes[enum].click()
                    time.sleep(1)
                    params["selector"] = CSS_DELETE_BUTTON
                    self.selenium.findSingleCSS(**params).click()
                    waitLoadProgressDone(self.selenium)
                    self.configDeleteReport(name)
        except StaleElementReferenceException as e:
            self.configDeleteReport(name)

        return True

    def checkReportExist(self, name):
        found = False
        params = {"selector": CSS_SELECTOR_REPORT_CONFIG_ROW, "waittype":"visibility"}
        el = self.selenium.findMultiCSS(**params)
        if not el: 
            print("Not able to find any reports")
            return False
            
        for e in el:
            if e.text.find(name) != -1:
                found = True
                break
        return found


    def findReportCount(self):
        params = {"selector": CSS_REPORT_COUNT, "waittype":"visibility", "timeout":5}
        el = self.selenium.findSingleCSS(**params)
        if el:
            count = el.text
            match = re.search(r'\((\d+)\)', count)
            if match:
                count = match.group(1)
                return int(count)
        return False

    def close(self):
        if self.selenium:
            self.selenium.quit()


'''=========AD HOC REPORT STUFF GOES UNDER HERE========='''

def verifyAdHocReports(kek, browser, settings):

    #commented out sections are logic for new devices checkbox


    rcode = True
    params = {}
    
    non_decimal = re.compile(r'[^\d.]+')


    conn = "zbat testing conn"
    summ = "zbat testing summary"

    params["selector"] = CSS_MYREPORT_NAMEFILTER
    browser.findSingleCSS(**params).click()

    params["selector"] = CSS_MYREPORT_NAMES
    names = browser.findMultiCSS(**params)

    for name in names:
        if settings == "summary" and name.text == summ:
            name.click()
            break
        elif settings != "summary" and name.text == conn:
            name.click()
            break

    waitLoadProgressDone(browser)
    params["selector"] = CSS_ADHOC_MYREPORTS_DISPLAY_NUMBER
    oldCount = non_decimal.sub('',browser.findSingleCSS(**params).text)
    chip = None


    kek.gotoReportConfigs()
    waitLoadProgressDone(browser)

    params["selector"] = CSS_ADHOC_SEARCH_BUTTON
    browser.findSingleCSS(**params).click()

    params["selector"] = CSS_ADHOC_SEARCH_BAR
    bar = browser.findSingleCSS(**params)

    bar.click()

    try:
        params["selector"] = CSS_FILTER_CHIP
        params["timeout"] = 3
        chip = browser.findSingleCSS(**params)
    except:
        chip = None


    bar.clear()
    if settings == "summary":
        bar.send_keys("zbat testing summary",Keys.ENTER)
    else:
        bar.send_keys("zbat testing conn",Keys.ENTER)

    '''
    if chip is False:
        bar.send_keys("zbat_testing_config",Keys.ENTER)
    else:
        bar.send_keys(Keys.ENTER)
    '''
    waitLoadProgressDone(browser)

    params["selector"] = CSS_ADHOC_CONFIG_CHECKBOXES
    browser.findSingleCSS(**params).click()

    waitLoadProgressDone(browser)

    params["selector"] = CSS_ADHOC_EDIT_BUTTON
    browser.findSingleCSS(**params).click()
    waitLoadProgressDone(browser)

    params["selector"] = CSS_ADHOC_TEMPLATE_SELECTION
    browser.findSingleCSS(**params).click()
    if settings == "summary":
        params["selector"] = CSS_SUMMARY_REPORT_OPTION
        browser.driver.execute_script("arguments[0].click();", browser.findSingleCSS(**params))
    else:
        params["selector"] = CSS_CONNECTIVITY_REPORT_OPTION
        #browser.driver.execute_script("arguments[0].click();", browser.findSingleCSS(**params))
        browser.executeScript("arguments[0].click();",**params)
    time.sleep(1)

    '''
    params["selector"] = CSS_CHECKBOX_WRAPPER
    wrapper = browser.findSingleCSS(**params)

    params["selector"] = CSS_ADHOC_NEW_DEVICE_SELECTION
    params["err_msg"] = "Oh come on"
    box = browser.findSingleCSS(**params)

    if (wrapper.get_attribute("aria-checked") == u"false" and settings[1] == True):
        print "activated"
        box.click()
    elif (wrapper.get_attribute("aria-checked") == u"true" and settings[1] == False):
        print "deactivated"
        box.click()
    '''
    params["selector"] = CSS_UPDATE_BUTTON
    browser.findSingleCSS(**params).click()

    time.sleep(3)
    params["selector"] = CSS_ADHOC_CONFIG_CHECKBOXES
    browser.findSingleCSS(**params).click()

    params["selector"] = CSS_ADHOC_BUTTON
    browser.findMultiCSS(**params)[5].click()

    time.sleep(3)

    browser.acceptAlert()

    # function to get latest report count and return it
    def checkLatestReportCount(settings=settings):
        kek.gotoMyReports()
        waitLoadProgressDone(browser)

        params["selector"] = CSS_MYREPORT_NAMEFILTER
        browser.findSingleCSS(**params).click()

        params["selector"] = CSS_MYREPORT_NAMES
        names = browser.findMultiCSS(**params)

        for name in names:
            if settings == "summary" and name.text == summ:
                name.click()
                break
            elif settings != "summary" and name.text == conn:
                name.click()
                break

        time.sleep(2)
        params["selector"] = CSS_ADHOC_MYREPORTS_DISPLAY_NUMBER
        newCount = non_decimal.sub('', browser.findSingleCSS(**params).text)
        return newCount
    
    for i in range(0,15):
        time.sleep(10)
        newCount = checkLatestReportCount()
        if int(newCount) <= int(oldCount):
            print("ERROR: REPORT NOT GENERATED.  Check {}, oldcount {}, newcount {}".format(i, oldCount, newCount))
            rcode = False
        else:
            return True
        
    return rcode


class AdHocReport:
    def __init__(self, **kwargs):
        self.params = kwargs
        self.selenium = Login(**kwargs).login()

    def gotoMyReports(self):
        #url = urlparse(self.params["url"])
        #rcode = self.selenium.getURL(url.scheme+'://'+url.netloc+'/reports/myreports')
        self.selenium.refresh()
        params = {}
        try:
            params["selector"] = CSS_ADHOC_REPORT_SELECTION
            self.selenium.findSingleCSS(**params).click()
        except:
            params["selector"] = CSS_ADHOC_TAB_THINGY
            self.selenium.findSingleCSS(**params).click()
            waitLoadProgressDone(self.selenium)
            params["selector"] = CSS_ADHOC_REPORT_SELECTION
            self.selenium.findSingleCSS(**params).click()   
        try:
            params["selector"] = CSS_ADHOC_SIDEBAR_REPORT_BUTTONS
            self.selenium.findMultiCSS(**params)[1].click()
        except:
            params["selector"] = CSS_ADHOC_REPORT_SELECTION
            self.selenium.findSingleCSS(**params).click()   
            waitLoadProgressDone(self.selenium)
            params["selector"] = CSS_ADHOC_SIDEBAR_REPORT_BUTTONS
            self.selenium.findMultiCSS(**params)[1].click()

        waitLoadProgressDone(self.selenium)

    def gotoReportConfigs(self):
        #url = urlparse(self.params["url"])
        #rcode = self.selenium.getURL(url.scheme+'://'+url.netloc+'/reports/configlist')
        params = {}

        try:
            params["selector"] = CSS_ADHOC_REPORT_SELECTION
            self.selenium.findSingleCSS(**params).click()
        except:
            params["selector"] = CSS_ADHOC_TAB_THINGY
            self.selenium.findSingleCSS(**params).click()
            waitLoadProgressDone(self.selenium)
            params["selector"] = CSS_ADHOC_REPORT_SELECTION
            self.selenium.findSingleCSS(**params).click()   
        try:
            params["selector"] = CSS_ADHOC_SIDEBAR_REPORT_BUTTONS
            self.selenium.findMultiCSS(**params)[0].click()
        except:
            params["selector"] = CSS_ADHOC_REPORT_SELECTION
            self.selenium.findSingleCSS(**params).click()   
            waitLoadProgressDone(self.selenium)
            params["selector"] = CSS_ADHOC_SIDEBAR_REPORT_BUTTONS
            self.selenium.findMultiCSS(**params)[0].click()

        waitLoadProgressDone(self.selenium)

    def checkAdHocReports(self, settings):
        waitLoadProgressDone(self.selenium)
        self.gotoMyReports()
        rcode = verifyAdHocReports(self,self.selenium,settings)
        return rcode

    def close(self):
        if self.selenium:
            self.selenium.quit()
