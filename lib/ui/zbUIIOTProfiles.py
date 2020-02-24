#!/usr/bin/python

import json
from urllib.parse import urlparse
from ui.login.zbUILoginCore import Login
from zbUIShared import *
from common.zbCommon import validateDataNotEmpty
from selenium import webdriver
from random import randint
#from selenium.webdriver.common.action_chains import ActionChains
from zbAPI import zbAPI
from zbConfig import defaultEnv
import pdb, time

defaultConfig = defaultEnv()

# global CSS parameters for IOT Profile page
CSS_SELECTOR_IOT_PROFILES_INFO_COLUMNS = ['A','B','C','D','E','F']
CSS_SELECTOR_IOT_PROFILES_GENERAL_SORT_TEST = ['A','B','C','D','E','F']



# Profile Download CSS parameters
CSS_SELECTOR_PROFILE_NAME_CHECKBOX = ".ui-grid-selection-row-header-buttons"
CSS_SELECTOR_PROFILE_TOTAL_CHECKBOXES = "div.selected-text" 
CSS_SELECTOR_NEXT_BUTTON = "[ng-click='ctrl.goNext()']"
CSS_SELECTOR_SELECT_PAGE = 'md-select[ng-model="ctrl.pageSize"] span'
CSS_SELECTOR_SELECT_PAGE_ITEMS = 'md-option[ng-repeat="option in ctrl.rowPerPageOptions"] div' 
CSS_SELECTOR_PROFILE_CHECKBOXCHECKED = ".selected[name='select_button_click'] svg"
CSS_SELECTOR_PROFILE_CHECKBOXUNCHECKED = "[name='select_button_click']"
CSS_SELECTOR_LISTINGS_DOWNLOAD_BUTTON = "[tooltip-text='Download your selected Profiles'][role='button']"

CSS_SELECTOR_HOVER_PROFILE = "div.profile-name"
CSS_SELECTOR_SUMMARY_DOWNLOAD_BUTTON = "div.profile-download-link"
CSS_SELECTOR_PENDING_SPINNER = "md-progress-circular[aria-hidden='false']"
CSS_SELECTOR_SUMMARY_DOWNLOAD_LINK_LOADING = ".profile-download-link-loading"


class IOTProfiles():
    def __init__(self, **kwargs):
        self.params = kwargs
        self.selenium = Login(**kwargs).login()

    def gotoIOTProfiles(self):
        url = urlparse(self.params["url"])
        rcode = self.selenium.getURL(url.scheme+'://'+url.netloc+'/monitor/profiles')
        waitLoadProgressDone(self.selenium)

    def checkTimeSeries(self):
        self.gotoIOTProfiles()

        # go through each time range
        for result in (clickEachTimerange(self.selenium)):
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

    def checkButtons(self):
        self.gotoIOTProfiles()
        resetAllDevAllSite(self.selenium)
        rcode = verifyDevicesCountExist(self.selenium)
        return rcode


    def checkEntries(self):
        self.gotoIOTProfiles()
        resetAllDevAllSite(self.selenium)
        #rcode = verifyIOTEntries(self.selenium)
        rcode = verifyTableEntries(self.selenium, CSS_SELECTOR_IOT_PROFILES_INFO_COLUMNS)
        return rcode


    def checkPagination(self):
        self.gotoIOTProfiles()
        resetAllDevAllSite(self.selenium)
        #rcode = verifyIOTEntries(self.selenium, 2)
        rcode = verifyTableEntries(self.selenium, CSS_SELECTOR_IOT_PROFILES_INFO_COLUMNS, 2)
        return rcode

    def checkSort(self):
        self.gotoIOTProfiles()
        resetAllDevAllSite(self.selenium)
        #rcode = verifyIOTProfilesSort(self.selenium)
        rcode = verifyTableSort(self.selenium, CSS_SELECTOR_IOT_PROFILES_GENERAL_SORT_TEST)
        return rcode




    # checkListingsDownload(), checkSummaryDownload(), and checkSummaryData()
    #  are used to check IoT Profile Downloads
    def checkListingsDownload(self):
        params = {}
        self.gotoIOTProfiles()
        for i in clickEachTimerange(browserobj=self.selenium, specific=["1M"]): pass
        self.selectLastPage()
        self.selectProfileNameCheckbox()
        rcode = self.verifyProfileNamesChecked()
        self.selectRandomProfileCheckbox()
        if rcode:
           rcode = self.verifyListingsDownloadButton()
        if rcode:
            return True

    def selectProfileNameCheckbox(self):
        params = {}
        try:
            params["selector"] = CSS_SELECTOR_PROFILE_NAME_CHECKBOX
            rcode = self.selenium.findSingleCSS(**params).click()
            time.sleep(2) #If this is not here and >1 seconds, some freakish glitch causes only the top checkbox to be checked on the UI
        except Exception as e:
            print(("This is not clean" + str(e)))

    def verifyProfileNamesChecked(self):
        params = {}
        total = 0
        params["selector"] = CSS_SELECTOR_PROFILE_TOTAL_CHECKBOXES
        temptext = self.selenium.findSingleCSS(selector=CSS_SELECTOR_PROFILE_TOTAL_CHECKBOXES, err_msg='Not able to find Total Selected text').text
        checkboxtotal = temptext[0:temptext.find(" ")]
        params["selector"] = CSS_SELECTOR_PROFILE_CHECKBOXCHECKED
        rcode = self.selenium.findMultiCSS(**params)

        count = len(rcode)
        total = total + count
        if count == int(checkboxtotal):
            return True
        else:
            return False


    def selectLastPage(self):
        params = {}
        params["selector"] = CSS_SELECTOR_SELECT_PAGE
        rcode = self.selenium.findSingleCSS(**params).click()
        params["selector"] = CSS_SELECTOR_SELECT_PAGE_ITEMS
        rcode = self.selenium.findMultiCSS(**params)
        #lastpage = len(rcode)-1
        rcode = rcode[-1]
        rcode.click()
        time.sleep(2)
               
    def selectRandomProfileCheckbox(self):
        params = {}
        params["selector"] = CSS_SELECTOR_PROFILE_CHECKBOXUNCHECKED
        rcode = self.selenium.findMultiCSS(**params)
        randomcheckbox = randint(0, len(rcode)-1) # random number generator for CSS
        rcode = rcode[randomcheckbox] # randomly select a profile
        rcode.click()

    def verifyListingsDownloadButton(self):
        params = {}
        params["selector"] = CSS_SELECTOR_LISTINGS_DOWNLOAD_BUTTON
        rcode = self.selenium.findSingleCSS(**params)
        if rcode:
            rcode = rcode.click()
            return True



    def checkSummaryDownload(self):
        params = {}
        self.gotoIOTProfiles()
        for i in clickEachTimerange(browserobj=self.selenium, specific=["1W"]): 
            pass
        #waitLoadProgressDone(self.selenium)
        rcode = self.selectRandomProfileDownload()
        if rcode:
            return True

    def selectRandomProfileDownload(self):
        params = {}
        params["selector"] = CSS_SELECTOR_HOVER_PROFILE
        rcode = self.selenium.findMultiCSS(**params)
        randomprofile = randint(0, len(rcode)-1) # random number generator for CSS
        rcode = rcode[randomprofile] # randomly select a profile
        
        params["selector"] = CSS_SELECTOR_SUMMARY_DOWNLOAD_BUTTON
        rcode2 = self.selenium.findMultiCSS(**params) # selects all of the buttons for random download
        rcode2 = rcode2[randomprofile] # selects the specific random profile download button
        
        self.selenium.hoverElement(rcode) # needs to rehover because of 
        rcode2.click()

        # Check the Pending Spinner
        self.selenium.hoverElement(rcode)
        rcode3 = self.selenium.findMultiCSS(selector=CSS_SELECTOR_PENDING_SPINNER, waittype='visibility', timeout=5)
        if not rcode3:
            print("Spinner should be visible")
            return False
    
        # Check the Downloading Link Text
        self.selenium.hoverElement(rcode)
        rcode4 = self.selenium.findMultiCSS(selector=CSS_SELECTOR_SUMMARY_DOWNLOAD_LINK_LOADING, waittype='visibility', timeout=5)
        if not rcode4:
            print("Downloading link text should be visible")
            return False
        
        for i in range(0,30):
            # Check that Pending Spinner is gone 
            self.selenium.hoverElement(rcode) 
            rcode5 = self.selenium.findMultiCSS(selector=CSS_SELECTOR_PENDING_SPINNER, waittype='invisibility', timeout=5)
            if rcode5:
                break
                
        if rcode5 != []:
            print("Spinner should be invisible")
            return False
        return True

        # Check that Downloading Link Text is gone
        self.selenium.hoverElement(rcode)
        rcode6 = self.selenium.findMultiCSS(selector=CSS_SELECTOR_SUMMARY_DOWNLOAD_LINK_LOADING, waittype='invisibility', timeout=5)
        if rcode6 != []:
            print("Spinner should be invisible")
            return False
        return True



    def checkSummaryData(self):
        req = zbAPI()
        # name = 'createreport?direction..', click on Headers and check the Request URL,
        # params trail the URL and are separated by an '&' 
        definedlist = ["direction","appName","ip","port","devicenumber","geolocation","remoteURL","data","sessions"]
        generatedlist = []

        params = {
            'tenantid': defaultConfig['tenantid'],
            'direction': 'all',
            'stime': '2017-11-26T18:15Z',
            'etime': 'now',
            'filter_monitored': 'yes',
            'filter_profile_id': 'Macintosh',
            'interval': 'hour',
            'page': 1,
            'report_type': 'profile'
        }
        count = 0
        response = None
        fileKey = None
        # Create a API call to iotProfileCreateReport
        # Need to run multiple times because sometimes we get no response
        while (count < 5):
            response = req.iotProfileCreateReport(host=defaultConfig['siteTest'], **params)
            response = json.loads(response)
            count += 1

            fileKey = response['file']['fileKey']
            if fileKey is None:
                time.sleep(1)
                continue
            else:
                break

        # Check that fileKey is found, else it fails
        if fileKey is None:
            print("FileKey not found")
            return False
        # Get the bucket name and filekey from response
        # name = 'download?bucket..', click on Headers and check the Request URL,
        # kwargs trail the URL and are separated by an '&'

        kwargs = {
            'tenantid': defaultConfig['tenantid'],
            'filekey': fileKey,
            'bucket': response['file']['bucket']

        }

        while (count < 5):
            response = req.iotProfileCheckReport(host=defaultConfig['siteTest'],**kwargs)
            response = json.loads(response)
            count += 1

            status = response['file']['status']
            if status != 'EXIST':
                time.sleep(5)
                continue
            else:
                break



        

        # Create another API call to iotProfileDownload
        response = req.iotProfileDownload(host=defaultConfig['siteTest'], **kwargs)
        # Formatting of the headers from the response in iotProfileDownload
        headings = response.split('\n', 1)[0]
        headingslist = headings.split(',')

        # Encoding elements to UTF-8 strings and stripping ' " '
        for itemh in headingslist:
            encoded = itemh.encode('utf8')
            stripped = encoded.strip('"')
            generatedlist.append(stripped)

        # Compare two lists and see if they have mismatches
        finallist = list(set(definedlist)^set(generatedlist))
        
        # If there are no mismatches, return True
        if len(finallist) == 0:
            return True

        print("### Your defined list of headers and the generated list of headers from the response do not match ###")
        print("### The defined list: {} ###".format(definedlist))
        print("### The generated list: {} ###".format(generatedlist))
        print("### The mismatch is {} ###".format(finallist))
        return False


    def close(self):
        if self.selenium:
            self.selenium.quit()

