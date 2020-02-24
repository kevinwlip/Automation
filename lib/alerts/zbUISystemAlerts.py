#!/usr/bin/python


from urllib.parse import urlparse
from ui.login.zbUILoginCore import Login
from ui.zbUIShared import *
from datetime import datetime

# global CSS parameters for Alert Page
CSS_SELECTOR_SYSTEM_ALERTS_DROPDOWN = "button.selector-menu-button.md-button.md-ink-ripple.layout-align-space-between-center.layout-row"
CSS_SELECTOR_SYSTEM_ALERTS_DROPDOWN_OPTIONS = "div.menu-selection-button.layout-align-space-between-center.layout-row"
# column B is inspector data, but doesn't necessary have to have data in the case when inspector is already removed
#CSS_SELECTOR_SYSTEM_ALERTS_INFO_COLUMNS = ['A','B','C']
CSS_SELECTOR_SYSTEM_ALERTS_INFO_COLUMNS = ['A','D']
CSS_SELECTOR_SYSTEM_ALERTS_GENERAL_SORT_TEST = ['D']



def verifySystemAlertsEntries (browserobj, pageNumber=1, verifyAll=False):
    clickparams = {}
    clickparams["selector"] = CSS_SELECTOR_SYSTEM_ALERTS_DROPDOWN
    clickparams["waittype"] = 'clickable'
    browserobj.click(**clickparams)
    clickparams["selector"] = CSS_SELECTOR_SYSTEM_ALERTS_DROPDOWN_OPTIONS
    browserobj.findMultiCSS(**clickparams)[2].click()
    waitLoadProgressDone(browserobj)
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
                for c in CSS_SELECTOR_SYSTEM_ALERTS_INFO_COLUMNS:
                    params["selector"] = CSS_SELECTOR_GENERAL_TEXT_ENTRY + c
                    ret = browserobj.findMultiCSS(**params)
                    if len(ret) != rows:
                        print("Failed Column " + c)
                        return False
                    for e in ret:
                        if "".join(e.text.split()) == "":
                            print("Failed Column " + c)
                            return False
            params["selector"] = CSS_SELECTOR_CHEVRON_RIGHT_ICON
            browserobj.click(**params)
            waitLoadProgressDone(browserobj)
    params["selector"] = CSS_SELECTOR_INVENTORY_ROW
    rows = len(browserobj.findMultiCSS(**params))
    for c in CSS_SELECTOR_SYSTEM_ALERTS_INFO_COLUMNS:
        params["selector"] = CSS_SELECTOR_GENERAL_TEXT_ENTRY + c
        ret = browserobj.findMultiCSS(**params)
        if len(ret) != rows:
            print("Failed Column " + c)
            return False
        for e in ret:
            if "".join(e.text.split()) == "":
                print("Failed Column " + c)
                return False
    return True


def verifySystemAlertsSort (browserobj):
    clickparams = {}
    clickparams["selector"] = CSS_SELECTOR_SYSTEM_ALERTS_DROPDOWN
    clickparams["waittype"] = 'clickable'
    browserobj.click(**clickparams)
    clickparams["selector"] = CSS_SELECTOR_SYSTEM_ALERTS_DROPDOWN_OPTIONS
    browserobj.findMultiCSS(**clickparams)[2].click()
    waitLoadProgressDone(browserobj)
    clickAllCheckboxes(browserobj)

    params = {}
    params["selector"] = CSS_SELECTOR_CLICKABLE_SORT_HEADER
    hsort = browserobj.findMultiCSS(**params)
    for l in CSS_SELECTOR_SYSTEM_ALERTS_GENERAL_SORT_TEST:

        # click column header until head ascending order
        if not clickUntilFind(browserobj, hsort[ord(l)-ord("A")], CSS_SORT_UP_ARROW):
            print("Cannot find column up arrow button")
            return False

        waitLoadProgressDone(browserobj)
        params["selector"] = CSS_SELECTOR_GENERAL_TEXT_ENTRY + l
        data = browserobj.findMultiCSS(**params)
        for i in range(0,len(data)-1):
            try:
                if datetime.strptime(data[i].text, "%b %d, %Y, %H:%M") > datetime.strptime(data[i+1].text, "%b %d, %Y, %H:%M"):
                    return False
            except ValueError:
                pass

        # click column header until head ascending order
        if not clickUntilFind(browserobj, hsort[ord(l)-ord("A")], CSS_SORT_DOWN_ARROW):
            print("Cannot find column down arrow button")
            return False
            
        waitLoadProgressDone(browserobj)
        params["selector"] = CSS_SELECTOR_GENERAL_TEXT_ENTRY + l
        data = browserobj.findMultiCSS(**params)
        for i in range(0,len(data)-1):
            try:
                if datetime.strptime(data[i].text, "%b %d, %Y, %H:%M") < datetime.strptime(data[i+1].text, "%b %d, %Y, %H:%M"):
                    return False
            except ValueError:
                pass
    return True



class SystemAlerts():
    def __init__(self, **kwargs):
        self.params = kwargs
        self.selenium = Login(**kwargs).login()

    def gotoSystemAlert(self):
        url = urlparse(self.params["url"])
        rcode = self.selenium.getURL(url.scheme+'://'+url.netloc+'/policiesalerts/systemalerts')
        waitLoadProgressDone(self.selenium)

    def checkEntries(self):
        self.gotoSystemAlert()
        rcode = verifySystemAlertsEntries(self.selenium)
        #rcode = verifyTableEntries(self.selenium, CSS_SELECTOR_SYSTEM_ALERTS_INFO_COLUMNS)
        return rcode

    def checkPagination(self):
        self.gotoSystemAlert()
        rcode = verifySystemAlertsEntries(self.selenium, 2)
        #rcode = verifyTableEntries(self.selenium, CSS_SELECTOR_SYSTEM_ALERTS_INFO_COLUMNS, 2)
        return rcode

    def checkSort(self):
        self.gotoSystemAlert()
        rcode = verifySystemAlertsSort(self.selenium)
        #rcode = verifyTableSort(self.selenium, CSS_SELECTOR_SYSTEM_ALERTS_GENERAL_SORT_TEST)
        return rcode

    def close(self):
        if self.selenium:
            self.selenium.quit()
