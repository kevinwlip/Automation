#!/usr/bin/python

# global CSS parameters for Application Detail page
CSS_SELECTOR_DATE_TEXT = "div.date-text"
CSS_SELECTOR_PROTOCOL_NAME = "span.md-headline.ng-binding.ng-scope"
CSS_SELECTOR_ALERT_NUMBER = "div.alert-text.ng-binding"
CSS_SELECTOR_BIG_NUMBER = "span.big-number.ng-binding"
CSS_SELECTOR_CONNECTIONS_CIRCLE = "div.connections-circle"
CSS_SELECTOR_ARROW_DROPDOWN = "ng-md-icon[icon='arrow_drop_down']"
CSS_SELECTOR_PROTOCOL_PIE_CHART_SLICE = "div#protocol-pie-chart > svg > g > g"
CSS_SELECTOR_PROTOCOL_PIE_CHART_LEGEND = "div.legend-item.ng-scope.layout-align-space-between-center.layout-row"
CSS_SELECTOR_DEVICE_LINK = "span.link.ng-binding.ng-scope.ng-isolate-scope"
CSS_SELECTOR_DATA_NUMBER = "span.dataNumber.ng-binding"
CSS_SELECTOR_NETWORK_USAGE_CHART_PATHS = 'div[id=google-sankey-multiple] > div > div > div> svg >g'

from urllib.parse import urlparse
import re
from ui.login.zbUILoginCore import Login
from ui.zbUIShared import *
import pdb, time

def verifyTextDetail(browserobj):
    params = {}
    params["selector"] = CSS_SELECTOR_PROTOCOL_NAME
    if "".join(browserobj.findSingleCSS(**params).text.split()) == "":
        print ("Protocol name not found!")
        return False
    params["selector"] = CSS_SELECTOR_ALERT_NUMBER
    if not re.search('\d', browserobj.findSingleCSS(**params).text):
        print ("Alert Number not found!")
        return False
    params["selector"] = CSS_SELECTOR_DATE_TEXT
    for e in browserobj.findMultiCSS(**params):
        if not re.search('\d', e.text):
            print ("Date text not found!")
            return False
    params["selector"] = CSS_SELECTOR_BIG_NUMBER
    for e in browserobj.findMultiCSS(**params):
        if not re.search('\d', e.text):
            print ("Big number not found!")
            return False
    return True

def verifyNetworkTrafficVenn(browserobj):
    params = {}
    params["selector"] = CSS_SELECTOR_CONNECTIONS_CIRCLE
    if len(browserobj.findMultiCSS(**params)) == 0:
        return False
    return True

def verifyDataUsage(browserobj):
    params = {}
    params["selector"] = CSS_SELECTOR_PROTOCOL_PIE_CHART_SLICE
    temp = {}
    temp["selector"] = CSS_SELECTOR_PROTOCOL_PIE_CHART_LEGEND
    if len(browserobj.findMultiCSS(**params)) != len(browserobj.findMultiCSS(**temp)) or len(browserobj.findMultiCSS(**params)) == 0:
        return False
    for e in browserobj.findMultiCSS(**temp):
        if "".join(e.text.split()) == "":
            return False
    return True

def verifyDeviceLink(browserobj):
    params = {}
    params["selector"] = CSS_SELECTOR_DEVICE_LINK
    temp = {}
    temp["selector"] = CSS_SELECTOR_DATA_NUMBER
    if len(browserobj.findMultiCSS(**params)) != len(browserobj.findMultiCSS(**temp)):
        return False
    for e in browserobj.findMultiCSS(**params): #Problem here
        temptext = repr(e.text).encode('utf-8')
        print(temptext)
        if "".join(temptext.split()) == "":
            
	    print("This is why we can't have nice things param")
            return False
    for e in browserobj.findMultiCSS(**temp):
        temptext = repr(e.text).encode('utf-8')
        if "".join(temptext.split()) == "":
            return False
    return True

def verifyDetailView(browserobj):
    params = {}
    params["selector"] = CSS_SELECTOR_NETWORK_USAGE_CHART_PATHS
    if len(browserobj.findMultiCSS(**params)) == 0:
        return False
    return True



class ApplicationDetail():
    def __init__(self, **kwargs):
        self.params = kwargs
        self.selenium = Login(**kwargs).login()


    def checkTimeSeries(self):
        # go to Monitor > Device Inventory > Device Detail
        url = urlparse(self.params["url"])
        rcode = self.selenium.getURL(url.scheme+'://'+url.netloc+'/detail/protocol/https')

        if rcode:
            waitLoadProgressDone(self.selenium)
        else:
            return False

        # go through each time range
        for result in (clickEachTimerange(browserobj=self.selenium, specific=["2H", "1D", "1W", "1M"])):
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

    def checkTextDetail(self):
        # go to Monitor > Device Detail > Device Detail
        url = urlparse(self.params["url"])
        rcode = self.selenium.getURL(url.scheme+'://'+url.netloc+'/detail/protocol/https')
        if rcode:
            waitLoadProgressDone(self.selenium)
        else:
            return False

        rcode = verifyTextDetail(self.selenium)
        return rcode

    def checkNetworkTraffic(self):
        # go to Monitor > Device Inventory > Device Detail
        url = urlparse(self.params["url"])
        rcode = self.selenium.getURL(url.scheme+'://'+url.netloc+'/detail/protocol/https')
        if rcode:
            waitLoadProgressDone(self.selenium)
        else:
            return False
        rcode = verifyNetworkTrafficVenn(self.selenium)
        if not rcode:
            return False
        return True

    def checkDataUsage(self):
        # go to Monitor > Device Inventory > Device Detail
        url = urlparse(self.params["url"])
        rcode = self.selenium.getURL(url.scheme+'://'+url.netloc+'/detail/protocol/https')
        if rcode:
            waitLoadProgressDone(self.selenium)
        else:
            return False
        rcode = verifyDataUsage(self.selenium)
        if not rcode:
            return False
        return True

    def checkDeviceLink(self):
        #maybe sort check in the future
        url = urlparse(self.params["url"])
        rcode = self.selenium.getURL(url.scheme+'://'+url.netloc+'/detail/protocol/https')
        if rcode:
            waitLoadProgressDone(self.selenium)
        else:
            return False

        rcode = verifyDeviceLink(self.selenium)
        return rcode


    def checkNetworkUsageDiagram(self):
        url = urlparse(self.params["url"])
        rcode = self.selenium.getURL(url.scheme+'://'+url.netloc+'/detail/protocol/https')
        if rcode:
            waitLoadProgressDone(self.selenium)
        else:
            return False
        rcode = verifyDetailView(self.selenium)
        if not rcode:
            return False
        return True

    def close(self):
        if self.selenium:
            self.selenium.quit()
