#!/usr/bin/python

from urllib.parse import urlparse
from ui.login.zbUILoginCore import Login
from ui.zbUIShared import *
import time, pdb

# global CSS parameters for Application page
CSS_SELECTOR_APPLICATIONS_INFO_COLUMNS = ['A','B','C','D','E','F']
CSS_SELECTOR_APPLICATIONS_GENERAL_SORT_TEST = ['A','B','C','D','E']
CSS_APP_LINK = 'a[ng-click="grid.appScope.ctrl.goDetail(row)"]'




class Applications():
    def __init__(self, **kwargs):
        self.params = kwargs
        self.selenium = Login(**kwargs).login()

    def gotoApplications(self):
        url = urlparse(self.params["url"])
        rcode = self.selenium.getURL(url.scheme+'://'+url.netloc+'/monitor/applications')
        waitLoadProgressDone(self.selenium)

    def checkTimeSeries(self):
        self.gotoApplications()
        # go through each time range
        for result in (clickEachTimerange(browserobj=self.selenium, specific=['2H','1D','1W','1M'])):
            if result:

                # wait for complete load and check series graph present.
                rcode = waitLoadProgressDone(self.selenium)
                if rcode:
                    data = waitSeriesGraphDone(self.selenium)

                # verify data
                if data:
                    rcode = verifyDataTimerange(result["time"], data, strict=self.params["comparestrict"])
                else:
                    print("Traffic series did not find any data")
                    return False

                if not rcode:
                    print("Traffic series for "+str(result["time"])+" has only "+str(len(data))+" bars.")
                    return False
            else:
                return False
        return rcode

    def checkEntries(self):
        self.gotoApplications()
        resetAllSite(self.selenium)
        #rcode = verifyApplicationsEntries(self.selenium)
        rcode = verifyTableEntries(self.selenium, CSS_SELECTOR_APPLICATIONS_INFO_COLUMNS)
        return rcode

    def checkPagination(self):
        self.gotoApplications()
        resetAllSite(self.selenium)
        #rcode = verifyApplicationsEntries(self.selenium, 2)
        rcode = verifyTableEntries(self.selenium, CSS_SELECTOR_APPLICATIONS_INFO_COLUMNS, 2)
        return rcode

    def checkSort(self):
        self.gotoApplications()
        resetAllSite(self.selenium)
        #rcode = verifyApplicationsSort(self.selenium)
        rcode = verifyTableSort(self.selenium, CSS_SELECTOR_APPLICATIONS_GENERAL_SORT_TEST)
        return rcode

    def checkApplicationLink(self):
        self.gotoApplications()
        # check device link to make sure it's valid
        rcode = verifyLinkToAppDetail(self.selenium, CSS_APP_LINK)
        if not rcode:
            print("App link to App Detail is not working")
            return False
        else:
            self.gotoApplications()
            return True
            
    def close(self):
        if self.selenium:
            self.selenium.quit()
