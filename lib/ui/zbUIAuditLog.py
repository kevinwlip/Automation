#!/usr/bin/python

from urllib.parse import urlparse
from ui.login.zbUILoginCore import Login
from ui.zbUIShared import *
import pdb, time

# global CSS parameters for Monitor page
CSS_SELECTOR_AUDIT_LOGS_INFO_COLUMNS = ['A','B','C','D']
CSS_SELECTOR_AUDIT_LOGS_GENERAL_SORT_TEST = ['A','B','C','D']
CSS_TABLE_TITLE = 'div.table-title'


class AuditLog():
    def __init__(self, **kwargs):
        self.params = kwargs
        self.selenium = Login(**kwargs).login()

    def gotoAuditLog(self):
        url = urlparse(self.params["url"])
        rcode = self.selenium.getURL(url.scheme+'://'+url.netloc+'/administration/auditLogs')
        waitLoadProgressDone(self.selenium)
        params = {"selector": CSS_TABLE_TITLE, "waittype":"visibility", "timeout":10}
        rcode = self.selenium.findSingleCSS(**params)
        if not rcode:
            return False
        return True

    def checkEntries(self):
        rcode = self.gotoAuditLog()
        if not rcode:
            print("Not able to go to Audit Log page")
            return False
        #rcode = verifyAuditLogsEntries(self.selenium)
        rcode = verifyTableEntries(self.selenium, CSS_SELECTOR_AUDIT_LOGS_INFO_COLUMNS)
        return rcode

    def checkPagination(self):
        rcode = self.gotoAuditLog()
        if not rcode:
            print("Not able to go to Audit Log page")
            return False
        #rcode = verifyAuditLogsEntries(self.selenium, 2)
        rcode = verifyTableEntries(self.selenium, CSS_SELECTOR_AUDIT_LOGS_INFO_COLUMNS, 2)
        return rcode

    def checkSort(self):
        rcode = self.gotoAuditLog()
        if not rcode:
            print("Not able to go to Audit Log page")
            return False
        #rcode = verifyAuditLogsSort(self.selenium)
        rcode = verifyTableSort(self.selenium, CSS_SELECTOR_AUDIT_LOGS_GENERAL_SORT_TEST, datetimeFormat="%b %d, %Y, %H:%M")
        return rcode

    def close(self):
        if self.selenium:
            self.selenium.quit()
