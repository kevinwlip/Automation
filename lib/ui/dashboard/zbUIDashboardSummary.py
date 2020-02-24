import re
import time
import locale
import pdb
from enum import Enum
from urllib.parse import urlparse
from common.zbSelenium import zbSelenium
from selenium.common.exceptions import StaleElementReferenceException, NoSuchElementException
from ui.login.zbUILoginCore import Login
from locator.navigator import NavMenuLoc
from locator.navigator import ToolBarLoc
from locator.dashboard import DashboardSummaryLoc
from locator.risks import RisksVulnerabilitiesLoc
from locator.alert import AlertListLocators
from locator.network import NetworkSelectors
from locator.protocols import ProtocolPage
from locator.application import ApplicationLoc
from locator.devices import DeviceLocators
from common.zbCommon import validateDataNotEmpty
from ui.zbUIShared import checkElement, checkElementText, waitLoadProgressDone, clickSpecificTimerange, verifyTableSort
from selenium.webdriver.common.action_chains import ActionChains
import logging
import random

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

locale.setlocale( locale.LC_ALL, 'en_US.UTF-8' )


class ZOOM_DIRECTION(Enum):
    IN = 'zoom_in',
    OUT = 'zoom_out'

CSS_DASHBOARD_CARD_DEVICE_IOT_NUM = "[data-id='other_iot'] .devices .text"
CSS_DASHBOARD_CARD_DEVICE_NON_IOT_NUM = "[data-id='traditional_it'] .text"

class DashboardSummary():

    def __init__(self, **kwargs):
        self.params = kwargs
        self.selenium = Login(**kwargs).login()
        self.baseurl = kwargs["url"]+'/'
        self.toplist = {}


    def gotoDashboardSum(self):
        url = urlparse(self.params["url"])
        rcode = self.selenium.getURL(url.scheme+'://'+url.netloc+'/guardian/dashboard/summary')
        waitLoadProgressDone(self.selenium)

    def verifyGlobalFilters(self):
        # Verify the Global Filters
        logger.info('Verify the Global Filters')

        css = DashboardSummaryLoc.CSS_DASHBOARD_GLOBAL_FILTERS
        global_filters = self.selenium.findMultiCSSNoHover(selector=css, timeout=0)
        filter_count = 0
        filter_matrix = [["All Sites", "All Disconnected Sites"],   # Removed "All Connected Sites" temporarily
        ["Monitored Devices", "Discovered Devices"],
        ["All Devices", "All IoT", "Medical IoT", "Other IoT", "Traditional IT"],   # Replaced "Medical IoT", Removed "Office IoT" temporarily
        ["2 Hours", "1 Day", "1 Week", "1 Month", "1 Year", "All to Date"]]

        for filter in global_filters: # Loop through Global Filters
            global_filters[filter_count].click()
            css = DashboardSummaryLoc.CSS_DASHBOARD_GLOBAL_FILTER_ELEMENTS
            filter_eles = self.selenium.findMultiCSSNoHover(selector=css, timeout=0)
            filter_ele_count = 0
            for ele_text in filter_matrix[filter_count]: # Loop through static text and actual Global Filter text
                assert ele_text in filter_eles[filter_ele_count].text, \
                "Text returned '{}', should instead contain '{}'".format(filter_eles[filter_ele_count].text, ele_text)
                filter_ele_count += 1
            
            #following will test if click on filter items, right options are checked. 
            expectedresultDic = {
                "All Devices":["All Devices","All IoT", "Medical IoT", "Other IoT", "Traditional IT"],
                "All IoT":["All IoT", "Medical IoT", "Other IoT"],
                "Medical IoT":["Medical IoT"],
                "Other IoT":["Other IoT"],
                "Traditional IT":["Traditional IT"]}

            if filter_eles[0].text.count("All Devices")>0:  # so far, only check for device type filter because of the customer issue
                for count in range(len(filter_eles)):
                    filter_eles[count].click()
                    time.sleep(3)
                    checked_List = []
                    filter_eles = self.selenium.findMultiCSSNoHover(selector=css, timeout=0)
                    for ele in filter_eles:
                        if "checked" in ele.text:
                            checked_List.append(ele.text.splitlines()[1]) 
                    assert expectedresultDic[filter_eles[count].text.splitlines()[1]] == checked_List
                    checked_List.clear()

            
            filter_count += 1

        return True

    def verifyGlobalFiltersOnTopBar(self):
        # Verify global filtering on the Top Bar Widget
        logger.info('Verify global filtering on the Top Bar Widget')

        filter_count = 0
        filter_matrix = [["All Sites", "All Disconnected Sites"],
        ["Monitored Devices", "Discovered Devices"],
        ["All Devices", "All IoT", "Medical IoT", "Other IoT", "Traditional IT"],
        ["2 Hours", "1 Day", "1 Week", "1 Month", "1 Year", "All to Date"]]

        css = DashboardSummaryLoc.CSS_DASHBOARD_GLOBAL_FILTERS
        global_filters = self.selenium.findMultiCSSNoHover(selector=css, timeout=0)

        for filter in global_filters:   # Need 'for' loop here to loop through all sites
            global_filters[filter_count].click()

            css = DashboardSummaryLoc.CSS_DASHBOARD_GLOBAL_FILTER_ELEMENTS
            filter_eles = self.selenium.findMultiCSSNoHover(selector=css, timeout=0)
            filter_eles[0].click()   # Start on first element for each filter

            all_values_lists = []
            filter_ele_count = 0

            for filter_ele in filter_matrix[filter_count]:
                if filter_ele_count == len(filter_matrix[filter_count]) - 1:   # Regarding Site filter, skips clicking on 'Disconnected Sites' and Customer sites
                    break

                css = DashboardSummaryLoc.CSS_DASHBOARD_TOP_BAR_ENTRIES
                widget_eles = self.selenium.findMultiCSSNoHover(selector=css, timeout=0)
                prev_widget_values = []
                for val in widget_eles:
                    prev_widget_values.append( int(val.text.split('\n')[0].replace(',','')) )
                all_values_lists.append(prev_widget_values)

                if filter_count == 0 or filter_count == 2:   # Only Site and Device Type filters have chips
                    css = DashboardSummaryLoc.CSS_DASHBOARD_GLOBAL_FILTER_CHIPS
                    site_chip = self.selenium.findSingleCSSNoHover(selector=css, timeout=0)
                    for ele in filter_matrix[filter_count]:   # Check chip text
                        assert filter_matrix[filter_count][filter_ele_count] in site_chip.text, \
                        "Text should be {}, instead returned {}".format(filter_matrix[filter_count][filter_ele_count], site_chip.text)   # There is an issue here in that env. has no 'Disconnected Sites', default is 'All Sites'
                        break

                css = DashboardSummaryLoc.CSS_DASHBOARD_GLOBAL_FILTER_ELEMENTS
                filter_eles = self.selenium.findMultiCSSNoHover(selector=css, timeout=0)
                filter_eles[0].click()   # Clicks back to first element, needed for Sites and Device Type filters
                time.sleep(3)
                filter_eles = self.selenium.findMultiCSSNoHover(selector=css, timeout=0)   # Needed for stale element problem
                filter_eles[filter_ele_count + 1].click()   # Clicks next filter
                time.sleep(5)
                filter_ele_count += 1

                css = DashboardSummaryLoc.CSS_DASHBOARD_TOP_BAR_ENTRIES
                widget_eles = self.selenium.findMultiCSSNoHover(selector=css, timeout=0)
                curr_widget_values = []

                for val in widget_eles:
                    curr_widget_values.append(int(val.text.split('\n')[0].replace(',','')))
                all_values_lists.append(curr_widget_values )

                if filter_count == 3:
                    try:   # Compare the top widget's values using Time Range filter
                        time.sleep(5)
                        assert prev_widget_values <= curr_widget_values, \
                        "Previous widget values: {}, should not be greater than current widget values: {}".format(prev_widget_values, curr_widget_values)
                        continue
                    except:
                        assert False, "Previous widget values: {}, should not be greater than current widget values: {}".format(prev_widget_values, curr_widget_values)

            uniq_values_lists = [list(x) for x in set(tuple(x) for x in all_values_lists)]
            assert uniq_values_lists != [], "Unique Value Lists: {}, should not be empty".format(uniq_values_list)   # Check for at least one different list

            filter_count += 1

        return True


    def checkTopBar(self):
        rcode = self.selenium.findMultiCSS(selector=DashboardSummaryLoc.CSS_DASHBOARD_TOP_BAR_ENTRIES)
        for enum,r in enumerate(rcode):
            bofa, ligma = r.text.split("\n")
            if(DashboardSummaryLoc.bar_list[enum] not in ligma):
                logging.critical("Top bar missing {}".format(DashboardSummaryLoc.bar_list[enum]))
                return False
            self.toplist[ligma] = bofa
        print(self.toplist)
        return True

    def checkDeviceCard(self):
        tot_dev = 0
        izzet = True
        rcode = self.selenium.findSingleCSS(selector=DashboardSummaryLoc.CSS_DEVICES_CARD)
        rcode = self.selenium.findSingleCSS(selector=DashboardSummaryLoc.CSS_DASHBOARD_DEVICES_CHART_NON_IOT)
        self.selenium.click(selector=DashboardSummaryLoc.CSS_DASHBOARD_TITLE_DEVICES) # To ensure the page is interactive with the mouse
        h = rcode.size["height"]
        w = rcode.size["width"]
        hover = ActionChains(self.selenium.driver).move_to_element_with_offset(rcode,4 / 5 * w, 1 / 5 * h )
        #hover.click() Currently a small issue with the graph, Jun's looking into it
        hover.perform()
        #self.selenium.hoverElement(rcode)
        sin = self.selenium.findSingleCSSNoHover(selector=DashboardSummaryLoc.CSS_DASHBOARD_DEVICES_CHART_TOOLTIP)
        noniot = re.search("\d{1,5}", sin.text)
        print(noniot.group(0))
        rcode = self.selenium.findSingleCSS(selector=DashboardSummaryLoc.CSS_DASHBOARD_DEVICES_CHART_OTHER_IOT)
        h = rcode.size["height"]
        w = rcode.size["width"]
        hover = ActionChains(self.selenium.driver).move_to_element_with_offset(rcode,50 ,60)
        hover.perform()
        sin = self.selenium.findSingleCSSNoHover(selector=DashboardSummaryLoc.CSS_DASHBOARD_DEVICES_CHART_TOOLTIP)
        iot = re.search("\d{1,5}", sin.text)
        print(iot.group(0))
        #iot_num = int(sin.text.split(" ")[1])
        rcode = self.selenium.findSingleCSS(selector=CSS_DASHBOARD_CARD_DEVICE_IOT_NUM)
        if int(rcode.text) != int(iot.group(0)):
            logging.critical("Graph pop-up not matching the IoT number listed for devices")
            izzet = False
        tot_dev += int(rcode.text)
        rcode = self.selenium.findSingleCSS(selector=CSS_DASHBOARD_CARD_DEVICE_NON_IOT_NUM)

        if int(rcode.text) != int(noniot.group(0)):
            logging.critical("Graph pop-up not matching the non-IoT number listed for devices")
            izzet = False
        tot_dev += int(rcode.text)

        if(tot_dev != int(self.toplist["Total Monitored Devices"])):
            logging.critical("Devices card total not matching top part number")
            logging.critical(str(tot_dev) +"vs "+ str(self.toplist["Total Monitored Devices"]))
            izzet = False

        return izzet

    def checkSiteCard(self):
        izzet = True
        rcode = self.selenium.findMultiCSS(selector=DashboardSummaryLoc.CSS_DASHBOARD_SITES_NUMBERS)
        for r in rcode:
            print(r.text)
        site_num_a = rcode[0].text
        inspector_num_a = rcode[1].text
        rcode = self.selenium.findMultiCSS(selector=DashboardSummaryLoc.CSS_DASHBOARD_TABLE_INSPECTOR_NUMBERS)
        tempsum=0
        for r in rcode:
            tempsum+=int(r.text)
        if tempsum != int(inspector_num_a):
            logging.critical("Inspector numbers on table not matching up with displayed")
            izzet = False

        rcode = self.selenium.findMultiCSS(selector=DashboardSummaryLoc.CSS_DASHBOARD_SITES_MONITORED)
        tempsum=0
        for r in rcode:
            tempsum+=int(r.text)

        if tempsum != int(self.toplist["Total Monitored Devices"]):
            logging.critical("Monitored device numbers on table not matching up with ones on top bar")
            izzet = False

        rcode = self.selenium.findMultiCSS(selector=DashboardSummaryLoc.CSS_DASHBOARD_SITES_DISCOVERED)
        tempsum=0
        for r in rcode:
            tempsum+=int(r.text)

        if tempsum != int(self.toplist["Total Discovered Devices"]):
            logging.critical("Discovered device numbers on table not matching up with ones on top bar")
            izzet = False

        rcode = self.selenium.findMultiCSS(selector=DashboardSummaryLoc.CSS_DASHBOARD_SITES_RISK_SCORE)
        tempsum=0
        for r in rcode:
            if int(r.text) > tempsum:
                tempsum = int(r.text)

        if abs(tempsum - int(self.toplist["Risk Score"])) > 4 :
            logging.critical("Highest Risk Score on table not matching up with one on top bar")
            izzet = False


        rcode = self.selenium.findMultiCSS(selector=DashboardSummaryLoc.CSS_DASHBOARD_TABLE_INSPECTOR_NAMES)
        clicky = random.choice(rcode)
        confirmer = clicky.text
        clicky.click()
        waitLoadProgressDone(self.selenium)
        try:
            clicky.click()
            waitLoadProgressDone(self.selenium)
        except:
            pass
        sitename = self.selenium.findSingleCSSWaitLoop(selector=DashboardSummaryLoc.CSS_INSPECTOR_TITLE_CHECK_BRIEF,retry_count=5,retry_delay=5.0)
        '''
        if confirmer not in sitename.text:
            logging.critical("Inspector name not matching up on {}".format(confirmer))
            izzet = False
        '''
        self.selenium.driver.back()
        #Will check Subnet info w/ Fan
        return izzet
        #for enum, r in enumerate(rcode):

    def regDashboardSummaryApplications(self):
        self.gotoDashboardSum()
        clickSpecificTimerange(self.selenium, specific="1 Month")
        izzet = True
        #Check sorting
        relevantHeaders = ["Application","Application Category", "Used by Devices"]
        try:
            rcode  = verifyTableSort(self.selenium,cssColumnSortable=DashboardSummaryLoc.CSS_DASHBOARD_COLUMN_HEADERS)
        except:
            izzet=False

        #Check More Link
        rcode = self.selenium.findSingleCSS(selector=DashboardSummaryLoc.CSS_DASHBOARD_APP_CLICKMORE)
        rcode2 = self.selenium.findSingleCSS(selector=DashboardSummaryLoc.CSS_DASHBOARD_APP_SUBTITLE)
        widget_num = re.findall(r'\d+',rcode2.text)[0]
        rcode.click()
        waitLoadProgressDone(self.selenium)
        izzet = rcode = self.selenium.findSingleCSS(selector=ApplicationLoc.CSS_TABLE_NAME)
        page_num = re.findall(r'\d+',rcode.text)[0]
        if( int(widget_num) != int(page_num) ):
            logging.critical("App Widget numbers incorrect to App Page")
            izzet = False
        self.selenium.driver.back()
        waitLoadProgressDone(self.selenium)

        rcode = self.selenium.findMultiCSS(selector=DashboardSummaryLoc.CSS_DASHBOARD_APP_LINK)
        checky = rcode[0].text
        check_num = rcode[1].text
        rcode[0].click()
        waitLoadProgressDone(self.selenium)
        rcode = self.selenium.findSingleCSS(selector=DeviceLocators.CSS_SELECTOR_FILTER_APP_TAG)
        if checky != rcode.text:
            logging.critical("App Widget filter not working")
            izzet = False

        rcode = self.selenium.findSingleCSS(selector=DeviceLocators.CSS_TABLE_NAME)
        rc = re.findall(r'\d+',rcode.text)[0]
        if(int(rc) != int(check_num)):
            logging.critical("App Widget number incorrect to device page")
            izzet = False
        self.selenium.driver.back()
        waitLoadProgressDone(self.selenium)
        return izzet


    def regDashboardSummaryVuln(self):
        self.gotoDashboardSum()
        clickSpecificTimerange(self.selenium, specific="1 Week")
        izzet = True
        rcode = self.selenium.findSingleCSS(selector=DashboardSummaryLoc.CSS_DASHBOARD_VULN_CARD_TITLE)
        if not rcode or not "Vulnerabilities" in rcode.text:
            logging.critical("Dashbaord Summary Vuln Card Title Error")
            izzet = False
        vuln_items = self.selenium.findMultiCSS(selector=DashboardSummaryLoc.CSS_DASHBOARD_VULN_CARD_LINKS)
        for enum,item in enumerate(vuln_items):
            item_box = self.selenium.findMultiCSS(selector=DashboardSummaryLoc.CSS_DASHBOARD_VULN_CARD_LINKS)
            if "Vulnerabilities to Date" in item_box[enum].text: #This is the total vuln count
                item_box[enum].click()
                waitLoadProgressDone(self.selenium)
                rcode = self.selenium.findVisibleMultiCSS(selector=RisksVulnerabilitiesLoc.CSS_VULN_STAT_BLOCK,text="Vulnerabilities")
                if not rcode:
                    logging.critical("Vulnerablities Link for Vulnerability card not working")
                    izzet=False
                self.selenium.driver.back()
                waitLoadProgressDone(self.selenium)
            elif "Vulnerable Devices" in item_box[enum].text:
                item_box[enum].click()
                waitLoadProgressDone(self.selenium)
                rcode = self.selenium.findVisibleMultiCSS(selector=RisksVulnerabilitiesLoc.CSS_VULN_STAT_BLOCK,text="Vulnerabilities")
                if not rcode:
                    logging.critical("Vulnerable Devices Link for Vulnerability card not working")
                    izzet=False
                self.selenium.driver.back()
                waitLoadProgressDone(self.selenium)
        rcode = self.selenium.findSingleCSS(selector=DashboardSummaryLoc.CSS_DASHBOARD_VULN_CARD_CAT_LINK)
        stor = rcode.text
        rcode.click()
        waitLoadProgressDone(self.selenium)
        rcode = self.selenium.findSingleCSS(selector=RisksVulnerabilitiesLoc.CSS_VULN_FILTER_CHIP)
        if(stor not in rcode.text):
            logging.critical("Link Filter for Vulnerability card not working")
            izzet=False
        self.selenium.driver.back()
        waitLoadProgressDone(self.selenium)
        return izzet

    def regDashboardSummaryAlerts(self):
        self.gotoDashboardSum()
        clickSpecificTimerange(self.selenium, specific="1 Week")
        izzet = True
        rcode = self.selenium.findSingleCSS(selector=DashboardSummaryLoc.CSS_DASHBOARD_ALERTS_CARD_TITLE)
        if("Alerts" not in rcode.text):
            logging.critical("Dashboard Alerts card title incorrect")
            izzet = False
        rcode = self.selenium.findSingleCSS(selector=DashboardSummaryLoc.CSS_DASHBOARD_ALERTS_CARD_BIG_NUMBER)
        if rcode:
            count = re.findall(r'\d+',rcode.text.translate({ord(','):None}))[0]
            rcode.click()
            waitLoadProgressDone(self.selenium)
            l = self.selenium.findSingleCSSWaitLoop(selector=AlertListLocators.CSS_ALERT_TITLE_NUMBER,retry_count=3,retry_delay=3)
            print(l.text)
            temp = re.findall(r'\d+',l.text)[0]

            if abs(int(temp) - int(count)) > 10 :
                print(count)
                print(temp)
                logging.critical("Card and Alert page title mismatch in numbers")
                izzet = False
            self.selenium.driver.back()
            waitLoadProgressDone(self.selenium)
            rc = self.selenium.findMultiCSS(selector=DashboardSummaryLoc.CSS_DASHBOARD_ALERTS_CARD_FILTER_LINKS)
            for ind,r in enumerate(rc):
                jank = self.selenium.findMultiCSS(selector=DashboardSummaryLoc.CSS_DASHBOARD_ALERTS_CARD_FILTER_LINKS)
                clicky = jank[ind]
                comp_text = clicky.text
                clicker = self.selenium.findSingleCSS(browserobj=clicky, selector=DashboardSummaryLoc.CSS_DASHBOARD_ALERTS_CARD_FILTER_LINK_LINKS)
                clicker.click()
                waitLoadProgressDone(self.selenium)
                jake = self.selenium.findSingleCSSWaitLoop(selector=AlertListLocators.CSS_ALERT_TITLE_NUMBER,retry_count=3,retry_delay=3)
                page_num = re.findall(r'\d+',jake.text)[0]
                card_num = comp_text.translate({ord(','):None})
                card_num = re.findall(r'\d+',card_num)[0]
                rcode = self.selenium.findSingleCSS(selector=AlertListLocators.CSS_IMPACTED_CATEGORY)
                if(rcode.text not in comp_text):
                    logging.critical("Clicked link {} not populating category filter".format(comp_text))
                    izzet = False

                if( abs(int(card_num) - int(page_num)) > 10 ):
                    logging.critical("Clicked link {} not matching numbers {} and {}".format(comp_text, card_num, page_num))
                    izzet = False
                self.selenium.driver.back()
                waitLoadProgressDone(self.selenium)
        else:
            logging.critical("Big Alert Card number doesn't exist")
            izzet = False
        return izzet

    def regDashboardSummaryRisks(self):
        self.gotoDashboardSum()
        clickSpecificTimerange(self.selenium, specific="1 Year")
        izzet = True
        mouseOverScript = "if(document.createEvent){var evObj = document.createEvent('MouseEvents');evObj.initEvent('mouseover',true, false); arguments[0].dispatchEvent(evObj);} else if(document.createEventObject) { arguments[0].fireEvent('onmouseover');}";
        rcode = self.selenium.findMultiCSS(selector=DashboardSummaryLoc.CSS_DASHBOARD_RISK_RECTANGLES)
        for bleh in rcode:
            self.selenium.driver.switch_to_window(self.selenium.driver.current_window_handle)
            self.selenium.hoverElement(bleh)
            time.sleep(1)
            self.selenium.moveMouse(xoffset=-10,yoffset=10)
            for i in range(20):
                self.selenium.moveMouse(xoffset=1,yoffset=1)
            time.sleep(1)
            rc = self.selenium.findSingleCSSNoHover(selector=DashboardSummaryLoc.CSS_DASHBOARD_RISK_OVERLAY_DATE)
            if not re.findall(r'\d+',rc.text):
                logging.critical("Overlay Date Not present")
                izzet = False

            rc = self.selenium.findSingleCSSNoHover(selector=DashboardSummaryLoc.CSS_DASHBOARD_RISK_OVERLAY_RISK_SCORE)
            if not "risk score" in rc.text.lower():
                logging.critical("Risk score not present in pop-up")
                izzet=False

        rcode = self.selenium.findSingleCSSNoHover(selector=DashboardSummaryLoc.CSS_DASHBOARD_RISK_OVERLAY_LAST_RECT)
        self.selenium.hoverElement(rcode)


        rcode2 = self.selenium.findMultiCSS(selector=DashboardSummaryLoc.CSS_DASHBOARD_RISK_OVERLAY_GENERIC)
        tots = []
        for r in rcode2:
            if "Total" in r.text:
                tots.append(r.text)

        alert_score =0
        rcode3 = self.selenium.findMultiCSS(selector=DashboardSummaryLoc.CSS_DASHBOARD_RISK_OVERLAY_ALERT_NUM)
        for r in rcode3:
            num = re.findall(r'\d+',r.text)[0]
            alert_score += int(num)


        flag_matchy = False
        for t in tots:
            if(alert_score == int(re.findall(r'\d+',t)[0]) ):
                flag_matchy = True

        if not flag_matchy:
            logging.critical("Alert score in overlay not matching with total")
            return False

        vuln_score =0
        rcode3 = self.selenium.findMultiCSS(selector=DashboardSummaryLoc.CSS_DASHBOARD_RISK_OVERLAY_VULN_NUM)
        for r in rcode3:
            num = re.findall(r'\d+',r.text)[0]
            vuln_score += int(num)

        flag_matchy = False
        for t in tots:
            if(vuln_score == int(re.findall(r'\d+',t)[0]) ):
                flag_matchy = True

        if not flag_matchy:
            logging.critical("Vulnerability score in overlay not matching with total")
            return False
        return izzet

    def regDashboardSummaryProtocols(self):
        self.gotoDashboardSum()
        clickSpecificTimerange(self.selenium, specific="1 Week")

        izzet = True

        rcode = self.selenium.findSingleCSS(selector=DashboardSummaryLoc.CSS_DASHBOARD_APP_DROPDOWN)
        rcode.click()
        time.sleep(1)
        self.selenium.click(selector=DashboardSummaryLoc.CSS_DASHBOARD_PROTOCOL_DROPDOWN)
        time.sleep(1)

        text = self.selenium.findSingleCSS(selector=DashboardSummaryLoc.CSS_DASHBOARD_PROTOCOLS_BIG_NUMBER).text
        tot_count = int(re.findall(r'\d+',text)[0])
        logger.info("total count is: " + str(tot_count))
        url = urlparse(self.params["url"])
        rcode = self.selenium.getURL(url.scheme+'://'+url.netloc+'/guardian/monitor/protocols')
        waitLoadProgressDone(self.selenium)
        clickSpecificTimerange(self.selenium, specific="1 Week")
        k =self.selenium.findSingleCSSWaitLoop(selector=ProtocolPage.CSS_TITLE,retry_count=3,retry_delay=3).text

        if(tot_count != int(re.findall(r'\d+',k)[0]) ):
            logging.critical("Widget count not matching with Page count")
        self.selenium.driver.back()
        waitLoadProgressDone(self.selenium)
        return izzet

    def regDashboardSummaryNetworks(self):
        self.gotoDashboardSum()
        clickSpecificTimerange(self.selenium, specific="1 Month")
        izzet = True
        rcode = self.selenium.findSingleCSS(selector=DashboardSummaryLoc.CSS_DASHBOARD_VLAN_TITLE)
        if not "Network Segments" in rcode.text:
            logging.critical("DBoard Summary VLAN title incorrect")
            izzet = False
        rcode = self.selenium.findSingleCSS(selector=DashboardSummaryLoc.CSS_DASHBOARD_VLAN_SUBNET)
        save = rcode.text
        rcode.click()
        waitLoadProgressDone(self.selenium)
        rcode = self.selenium.findSingleCSSWaitLoop(selector=NetworkSelectors.CSS_NETWORK_ACTIVE,retry_count=3,retry_delay=3)
        page_num = re.findall(r'\d+',rcode.text)[0]
        old_num = re.findall(r'\d+',save)[0]
        dif = abs(int(page_num)-int(old_num) )
        if dif > 5:
            logging.critical("Subnet count mismatch")
            izzet = False
        self.selenium.driver.back()
        waitLoadProgressDone(self.selenium)
        rcode= self.selenium.findMultiCSS(selector=DashboardSummaryLoc.CSS_DASHBOARD_VLAN_CAPTIONS)
        gruul = []
        for r in rcode:
            gruul.append(r.text)
        for x in ["Subnets", "With Medical Devices"]:
            if x not in gruul:
                print(gruul)
                logging.critical("Dashboard Summary VLAN panel caption mission or changed")
                izzet = False
        rcode = self.selenium.findSingleCSS(selector=DashboardSummaryLoc.CSS_DASHBOARD_VLAN_MED_CHART)
        if not rcode:
            logging.critical("Dashboard Summary VLAN panel graph missing")
            izzet = False
        rcode = self.selenium.findSingleCSS(selector=DashboardSummaryLoc.CSS_DASHBOARD_VLAN_MED_NUM)
        if not rcode:
            logging.critical("Dashboard Summary VLAN panel count missing")
            izzet = False
        return izzet

    def verifyDashboardSummaryTop(self):
        # Verify the active tab -- "Executive Summary"
        logger.info('Verify the active tab -- "Executive Summary"')
        css = DashboardSummaryLoc.CSS_DASHBOARD_NGSTAR_INSERTED_ACTIVE
        ele = self.selenium.findSingleCSSNoHover(selector=css, timeout=0)
        checkElementText(ele, css, "executive summary")

        # Verify the text identified by CSS_DASHBOARD_NGSTAR_INSERTED
        css = DashboardSummaryLoc.CSS_DASHBOARD_NGSTAR_INSERTED
        eles = self.selenium.findMultiCSSNoHover(selector=css, timeout=0)
        checkElement(eles, css)
        ele_text = []
        for ele in eles:
            text = ele.text
            if "\n" in text:
                try:
                    text = re.match(r'([\d+{,}]+)(\n)([\w+ ]+)', text).group(3)
                except:
                    assert False, "Text {} does not match pattern with number and text".format(ele.text)
            ele_text.append(text.lower())
        assert DashboardSummaryLoc.CSS_DASHBOARD_NGSTAR_INSERTED_LIST == ele_text[:8], \
            "ele text does not match: got {}, should be {}".format(ele_text[:8], DashboardSummaryLoc.CSS_DASHBOARD_NGSTAR_INSERTED_LIST)

        # Verify Subnets text
        css = DashboardSummaryLoc.CSS_DASHBOARD_SUBNETS
        ele = self.selenium.findSingleCSSNoHover(selector=css, timeout=0)
        checkElement(ele, css)
        try:
            text = re.match(r'(\d+)(\n)(\w+)', ele.text).group(3)
        except AttributeError:
            assert False, "Text {} does not match pattern with number and text".format(ele.text)
        assert text.lower() == "subnets", "Text should be subnets, got {}".format(text)

        # Verify Risk Score text
        css = DashboardSummaryLoc.CSS_DASHBOARD_RISK_SCORE
        ele = self.selenium.findSingleCSSNoHover(selector=css, timeout=0)
        checkElement(ele, css)
        try:
            text = re.match(r'(\d+)(\n)([\w+ ]+)', ele.text).group(3)
        except AttributeError:
            assert False, "Text {} does not match pattern with number and text".format(ele.text)
        assert text.lower() == "risk score", "Text should be risk score, got {}".format(text)

        return True

    def verifyDashboardSummaryGeneral(self):
        # Verify the general stuff in Dashboard Summary Page
        # Verify 3 tables exist under "Devices", "Sites" and "Applications" section
        logger.info('Verify 3 tables exist under "Devices", "Sites" and "Applications" section on "Executive Summary"')
        css = DashboardSummaryLoc.CSS_DASHBOARD_TABLES
        eles = self.selenium.findMultiCSSNoHover(selector=css, timeout=0)
        checkElement(eles, css)
        assert len(eles) == 3, "There should be 3 tables, got {} instead".format(len(eles))

        return True

    def verifyDashboardSummaryDevices(self):
        # Verify the "Devices" Section
        logger.info('Verify the "Devices" Section')
        css = DashboardSummaryLoc.CSS_DASHBOARD_TITLE_DEVICES
        ele = self.selenium.findSingleCSSNoHover(selector=css, timeout=0)
        checkElement(ele, css)
        ele_text = ele.text.split("\n")
        assert DashboardSummaryLoc.CSS_DASHBOARD_DEVICES_LIST == ele_text[:8], \
            "ele text does not match: got {}, should be {}".format(ele_text[:8], DashboardSummaryLoc.CSS_DASHBOARD_DEVICES_LIST)

        # Verify the chart show up in "Devices" Section
        css = DashboardSummaryLoc.CSS_DASHBOARD_DEVICES_CHART
        ele = self.selenium.findSingleCSSNoHover(selector=css, timeout=0)
        checkElement(ele, css)
        return True

    def verifyDashboardSummarySites(self):
        # Verify the "Sites" Section
        logger.info('Verify the "Sites" Section')
        css = DashboardSummaryLoc.CSS_DASHBOARD_TITLE_SITES
        ele = self.selenium.findSingleCSSNoHover(selector=css, timeout=0)
        checkElement(ele, css)
        ele_text = ele.text.split("\n")
        assert "Sites" == ele_text[0], \
            "ele text does not match: got {}, should be {}".format(ele_text[0], "Sites")
        start = 1 if ele_text[2].isdigit() else 0
        assert "Sites" == ele_text[2 + start], \
            "ele text does not match: got {}, should be {}".format(ele_text[3], "Sites")
        assert ele_text[3 + start].isdigit()
        assert "Inspectors" == ele_text[4 + start], \
            "ele text does not match: got {}, should be {}".format(ele_text[4 + start], "Inspectors")
        assert DashboardSummaryLoc.CSS_DASHBOARD_SITES_TABLE_LIST == ele_text[6 + start:12 + start], \
            "ele text does not match: got {}, should be {}".format(ele_text[6 + start:12 + start], \
            DashboardSummaryLoc.CSS_DASHBOARD_SITES_TABLE_LIST)
        return True

    def verifyDashboardSummaryApplications(self):
        # Verify the "Applications" Section
        logger.info('Verify the "Applications" Section')
        css = DashboardSummaryLoc.CSS_DASHBOARD_APPLICATIONS
        ele = self.selenium.findSingleCSSNoHover(selector=css, timeout=0)
        checkElement(ele, css)
        ele_text = ele.text.split("\n")
        assert DashboardSummaryLoc.CSS_DASHBOARD_APPLICATIONS_TEXT == ele_text[0:2], \
            "ele text does not match: got {}, should be {}".format(ele_text[0:2], \
            DashboardSummaryLoc.CSS_DASHBOARD_APPLICATIONS_TEXT)

        css = DashboardSummaryLoc.CSS_DASHBOARD_APPLICATIONS_TABLE
        ele = self.selenium.findSingleCSSNoHover(selector=css, timeout=0)
        checkElement(ele, css)
        ele_text = ele.text.split("\n")
        assert DashboardSummaryLoc.CSS_DASHBOARD_APPLICATIONS_TABLE_LIST == ele_text[1:4], \
            "ele text does not match: got {}, should be {}".format(ele_text[1:4], \
            DashboardSummaryLoc.CSS_DASHBOARD_APPLICATIONS_TABLE_LIST)
        try:
            re.match(r'(\d+ )(\btotal applications in\b)( \d+ )(\bapplication categories\b)', ele_text[0])
        except:
            assert False, "Text {} does not match pattern with number and text".format(ele_text[0])

        return True

    def verifyDashboardSummaryProtocols(self):
        # Verify the "Protocols" Section
        logger.info('Verify the "Protocols" Section')
        css = DashboardSummaryLoc.CSS_DASHBOARD_EXPAND_ICON
        ele = self.selenium.findSingleCSSNoHover(selector=css, timeout=0)
        checkElement(ele, css)
        ele.click()

        css = DashboardSummaryLoc.CSS_DASHBOARD_BUTTON_PROTOCOLS
        ele = self.selenium.findSingleCSS(selector=css, timeout=0)
        checkElement(ele, css)
        self.selenium.hoverElement(ele)
        time.sleep(1)
        ele.click()

        css = DashboardSummaryLoc.CSS_DASHBOARD_PROTOCOLS
        ele = self.selenium.findSingleCSS(selector=css, timeout=0)
        checkElement(ele, css)
        ele_text = ele.text.split("\n")
        assert "Protocols" == ele_text[0], "Text should be 'Protocols', got {}".format(ele_text[0])
        assert "expand_more" == ele_text[1], "Text should be 'expand_more', got {}".format(ele_text[1])
        joket = ele_text[2].split(" ")
        assert joket[0].isdigit(), "{} should be digits".format(joket[0])
        assert joket[1] == "total", "{} should be 'total'".format(joket[1])
        assert joket[2] == "protocols", "{} should be 'protocols'".format(joket[2])
        assert "Protocol" == ele_text[3], "Text should be 'Protocol', got {}".format(ele_text[3])
        assert "Profiles" == ele_text[4], "Text should be 'Profiles', got {}".format(ele_text[4])
        assert "Number of Devices" == ele_text[5], "Text should be 'Number of Devices', got {}".format(ele_text[5])
        #assert "Inbound" == ele_text[6], "Text should be 'Inbound', got {}".format(ele_text[6])
        #assert "Outbound" == ele_text[7], "Text should be 'Outbound', got {}".format(ele_text[7])

        return True

    def verifyDashboardSummaryNetworkSegments(self):
        # Verify the "Network Segments" Section
        logger.info('Verify the "Network Segments" Section')
        css = DashboardSummaryLoc.CSS_DASHBOARD_NETWORK_SEGMENTS
        ele = self.selenium.findSingleCSSNoHover(selector=css, timeout=0)
        checkElement(ele, css)
        ele_text = ele.text.split("\n")
        assert "Network Segments" == ele_text[0], "Text should be 'Network Segments', got {}".format(ele_text[0])
        # To Check there is "xx New"
        if "New" in ele_text[1]:
            start = 1
        else:
            start = 0
        assert ele_text[start+1].isdigit(), "{} should be digits".format(ele_text[start+1])
        assert "Subnets" == ele_text[start+2], "Text should be 'Subnets', got {}".format(ele_text[start+2])
        try:
            text = re.match(r'(\d+[.])*(\w+ )(\w+)', ele.text[start+3])
        except AttributeError:
            assert False, "Text {} does not match pattern with number and text".format(ele.text[start+3])
        #assert "Traffic" == ele_text[start+4], "Text should be 'Traffic', got {}".format(ele_text[start+4])
        #assert ele_text[start+5].isdigit(), "{} should be digits".format(ele_text[start+5])
        assert ele_text[start+4] == "With Mission Critical Devices" or "With Medical Devices", \
                "Text should be 'With Mission Critical Devices' or 'With Medical Devices', got {}".format(ele_text[start+6])

        return True

    def verifyDashboardSummaryRiskOverview(self):
        # Verify the "Risk Overview" Section
        logger.info('Verify the "Risk Overview" Section') # need to change to 1 year, since data for 1 month is gone in testing env
        self.gotoDashboardSum()
        clickSpecificTimerange(self.selenium, specific="1 Year") 

        css = DashboardSummaryLoc.CSS_DASHBOARD_RISK_OVERVIEW
        ele = self.selenium.findSingleCSSNoHover(selector=css, timeout=0)
        checkElement(ele, css)
        ele_text = ele.text.split("\n")
        assert "Risk Overview" == ele_text[0], "Text should be 'Risk Overview', got {}".format(ele_text[0])
        assert "Risk Score" or "Risk Score error_outline" in ele_text, \
                 "Text should include 'Risk Score' or 'Risk Score error_outline', got {}".format(ele_text)
        assert "Alerts" in ele_text, "Text should include 'Alerts', got {}".format(ele_text)
        assert "Vulnerabilities" in ele_text, "Text should include 'Vulnerabilities', got {}".format(ele_text)

        if ele_text[2].isdigit():
            start = 1
        else:
            start = 0
        assert "Risk Score error_outline" == ele_text[start+2], \
                "Text should be 'Risk Score error_outline', got {}".format(ele_text[start+2])
        assert "Risk Score" == ele_text[start+3], "Text should be 'Risk Score', got {}".format(ele_text[start+3])
        assert "Alerts" == ele_text[start+4], "Text should be 'Alerts', got {}".format(ele_text[start+4])
        assert "Vulnerabilities" == ele_text[start+5], "Text should be 'Vulnerabilities', got {}".format(ele_text[start+5])
        assert "0" == ele_text[start+6], "Graph Risk Number should start from 0, got {}".format(ele_text[start+6])
        assert "100" == ele_text[start+7], "Graph Risk Number should be up to 100, got {}".format(ele_text[start+7])
        assert "0" == ele_text[start+8], "Graph Alerts Number should start from 0, got {}".format(ele_text[start+8])
        assert isinstance(locale.atoi(ele_text[start+9]), int), \
                "Graph Alerts Number top y-axis should be a number, got {}".format(ele_text[start+9])
        assert "Risk" == ele_text[start+10], "Graph Text should be 'Risk', got {}".format(ele_text[start+9])
        assert "Alerts" == ele_text[start+11], "Graph Text should be 'Alerts', got {}".format(ele_text[start+10])

        return True

    def verifyDashboardSummaryAlerts(self):
        # Verify the "Alerts" Section
        logger.info('Verify the "Alerts" Section')
        css = DashboardSummaryLoc.CSS_DASHBOARD_ALERTS
        ele = self.selenium.findSingleCSSNoHover(selector=css, timeout=0)
        checkElement(ele, css)
        ele_text = ele.text.split("\n")
        assert "Alerts" == ele_text[0], "Text should be 'Alerts', got {}".format(ele_text[0])
        try:
            isinstance(locale.atoi(ele_text[1]), int)
            start = 0
        except ValueError:
            start = 1
        assert isinstance(locale.atoi(ele_text[start + 1]), int), "{} should be digits".format(ele_text[start + 1])
        assert "Active Alerts to Date" == ele_text[start + 2], \
                "Text should be 'Active Alerts to Date', got {}".format(ele_text[start + 2])
        try:
            text = re.match(r'([\d+{,}]+)( )(\w+)', ele_text[start + 3])
            assert isinstance(locale.atoi(text.group(1)), int), "{} should be digits".format(text.group(1))
            assert "New" == text.group(3), "{} should be 'New'".format(text.group(3))
        except AttributeError:
            assert False, "Text {} does not match pattern with number and text".format(ele_text[start + 3])

        try:
            text = re.match(r'([\d+{,}]+)( )(\w+)', ele_text[start + 4])
            assert isinstance(locale.atoi(text.group(1)), int), "{} should be digits".format(text.group(1))
            assert "Resolved" == text.group(3), "{} should be 'Resolved'".format(text.group(3))
        except AttributeError:
            assert False, "Text {} does not match pattern with number and text".format(ele_text[start + 4])

        assert "  Category Alerts to Date" == ele_text[start + 5], \
                "Text should be '  Category Alerts to Date', got {}".format(ele_text[start + 5])

        return True

    def verifyDashboardSummaryVulnerabilities(self):
        # Verify the "Vulnerabilities" Section
        logger.info('Verify the "Vulnerabilities" Section')
        css = DashboardSummaryLoc.CSS_DASHBOARD_VULNERABILITIES
        ele = self.selenium.findSingleCSSNoHover(selector=css, timeout=0)
        checkElement(ele, css)
        ele_text = ele.text.split("\n")
        assert "Vulnerabilities" == ele_text[0], "Text should be 'Vulnerabilities', got {}".format(ele_text[0])
        assert isinstance(locale.atoi(ele_text[1]), int), "{} should be digits".format(ele_text[1])
        assert "Vulnerabilities to Date" == ele_text[2], \
                "Text should be 'Vulnerabilities to Date', got {}".format(ele_text[2])
        assert isinstance(locale.atoi(ele_text[3]), int), "{} should be digits".format(ele_text[3])
        assert "Vulnerable Devices" == ele_text[4], \
                "Text should be 'Vulnerable Devices', got {}".format(ele_text[4])
        assert "  Profile Vulnerable Devices to Date" == ele_text[5], \
                "Text should be '  Profile Vulnerable Devices to Date', got {}".format(ele_text[5])

        return True

    def close(self):
        if self.selenium:
            self.selenium.quit()
