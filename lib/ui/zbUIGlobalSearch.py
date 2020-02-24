from urllib.parse import urlparse
from ui.login.zbUILoginCore import Login
from ui.zbUIShared import waitLoadProgressDone
import time, os, pdb
from selenium.webdriver.common.keys import Keys
import re
import logging
from locator.devices import DeviceDetailLocators
from locator.alert import VulnerabilityLocators
from locator.globalsearch import globalLocators

CSS_GLOBAL_SEARCH_ICON = ".zing_icon_search" #"i.material-icons.search-button" #"i.material-icons.search-button"
CSS_GLOBAL_SEARCH_FIELD = ".mat-input-element.mat-form-field-autofill-control" #".mat-form-field" #"input[id='autocompleteFieldID']"


CSS_GLOBAL_SEARCH_DROPDOWN_DEVICES_DEVICE_NAME = ".zt-global-search-group-item-devices"
CSS_GLOBAL_SEARCH_DROPDOWN_DEVICES_MAC_ADDRESS = "div > div.ng-tns-c7-16 > mark"
CSS_GLOBAL_SEARCH_DROPDOWN_DEVICES_IP_ADDRESS = "div > div.ng-tns-c7-1.ng-star-inserted"
CSS_GLOBAL_SEARCH_DROPDOWN_DEVICES_IOT_PROFILE = "div > div.zing-link"

CSS_GLOBAL_SEARCH_DEVICES_DEVICE_NAME = "div.ng-scope .ng-binding.md-headline"
CSS_GLOBAL_SEARCH_DEVICES_MAC_ADDRESS = "[ng-if='ctrl.mac'] .ng-binding.flex"
CSS_GLOBAL_SEARCH_DEVICES_IP_ADDRESS = "[ng-if='ctrl.data.ip'] .ng-binding.flex"
CSS_GLOBAL_SEARCH_DEVICES_IOT_PROFILE = "[ng-if='ctrl.data.profileid'] .flex.ng-binding"


CSS_DEVICE_INVENTORY_DEVICE_NAME = "span.md-headline.ng-binding.ng-scope"
CSS_DEVICE_INVENTORY_MAC_ADDRESS = "[ng-if='ctrl.mac'] .ng-binding.flex"
CSS_DEVICE_INVENTORY_IOT_PROFILE = "[ng-if='ctrl.data.profileid'] .flex.ng-binding"
CSS_DEVICE_INVENTORY_IP_ADDRESS = "[ng-if='ctrl.data.ip'] .ng-binding.flex"

CSS_GLOBAL_SEARCH_ALERTS_DEVICE_NAME = ".zt-global-search-group-item-alerts > .ng-tns-c7-16" #"div > div:nth-child(6) > mark"
CSS_GLOBAL_SEARCH_ALERTS_MAC_ADDRESS = ".zt-global-search-group-item-alerts > .ng-tns-c7-1"
CSS_GLOBAL_SEARCH_ALERTS_IP_ADDRESS = ".zt-global-search-group-item-alerts > .ng-tns-c7-1"
CSS_GLOBAL_SEARCH_ALERTS_NAME = "div[ng-bind-html='item.data.name | cut:false:13 | highlight:globalSearchCtrl.searchText']"

CSS_ALERT_DETAILS_PAGE_ALERT_NAME = ".md-headline"
CSS_ALERT_DETAILS_PAGE_ALERT_CARD = "[zing-tooltip-card=''] [ng-bind='alertDetailCtrl.alert.hostnameCombine']"
CSS_ALERT_DETAILS_PAGE_TOOLTIP_DETAILS = ".item-tooltip .detail-breakdown .flex-70"
CSS_ALERT_DETAILS_PAGE_IP_MATCH = ".ng-scope[ng-if='ctrl.data.ip']"


CSS_ALERTS_NAME = "div.word.ng-binding"
CSS_NUMBER_OF_ALERTS = "span[ng-if='!alertListCtrl.loading']"
CSS_ALERTS_DROPDOWN_ARROW = "md-select[name='Open pending/resolved dropdown']>md-select-value> span[class='md-select-icon']"
CSS_ALL_ALERTS_SELECTION = "md-option[name='Picked All Alerts']"
CSS_TIMERANGE_BUTTON = "button[ng-click='timerangeDropdownCtrl.openMenu($mdOpenMenu, $event)']"
CSS_TIMERANGE_6_MONTHS = "div[ng-click='timerangeDropdownCtrl.selectDateRange($index)']" #element 4


class GlobalSearch():

    def __init__(self, **kwargs):
        self.params = kwargs
        self.selenium = Login(**kwargs).login()
        waitLoadProgressDone(self.selenium)

    def verifyGlobalSearchDevices(self):
        kwargs = {}
        #url = urlparse(self.params["url"])
        #rcode = self.selenium.getURL(url.scheme+'://'+url.netloc+'')
        if os.environ["NODE_ENV"] == "staging":
            searchInput = ["Rhombus-Camera", "b8:27:eb:1b:37:20", "Macintosh", "192.168.10.105" ]
        else:
            searchInput = ["Rhombus-Camera", "b8:27:eb:1b:37:20", "Macintosh", "192.168.10.105" ]
        for i in searchInput:
            try:
                kwargs["selector"] = CSS_GLOBAL_SEARCH_ICON
                rcode = self.selenium.findSingleCSS(**kwargs)
                rcode.click()
            except:
                kwargs["selector"] = CSS_GLOBAL_SEARCH_FIELD
                rcode = self.selenium.findSingleCSSNoHover(**kwargs)
                rcode.click()

            kwargs["selector"] = CSS_GLOBAL_SEARCH_FIELD
            kwargs["text"] = i
            rcode = self.selenium.findSingleCSSNoHover(**kwargs)
            self.selenium.hoverElement(rcode)
            time.sleep(2)
            rcode.send_keys(i)
            
            time.sleep(2)
            # Searches device name in the search bar
            if "Rhombus-Camera" in i:
                # Gets device name from the devices dropdown
                kwargs["selector"] = CSS_GLOBAL_SEARCH_DROPDOWN_DEVICES_DEVICE_NAME
                rcode = self.selenium.findSingleCSS(**kwargs)
                deviceName = rcode.text
                
                if "Rhombus-Camera" not in deviceName:
                    print("Device name in dropdown devices does not match search input")
                    return False
                rcode.click()
                waitLoadProgressDone(self.selenium)
                self.selenium.switchToLatestWindow()
                waitLoadProgressDone(self.selenium)
                kwargs= {"selector": CSS_DEVICE_INVENTORY_DEVICE_NAME, "waittype":"visibility", "timeout":10}
                rcode = self.selenium.findSingleCSS(**kwargs)
                rcode = rcode.text
                if i not in rcode:
                    print("Device name in inventory does not match search input")
                    return False
                self.selenium.driver.close()
                self.selenium.switchToEarliestWindow()


            # Searches MAC address in the search bar
            elif i == "b8:27:eb:1b:37:20":
                # Gets MAC address from the devices dropdown
                kwargs["selector"] = CSS_GLOBAL_SEARCH_DROPDOWN_DEVICES_MAC_ADDRESS
                rcode = self.selenium.findSingleCSS(**kwargs)
                macAddress = rcode.text
                if i != macAddress:
                    print("Mac address in dropdown devices does not match search input")
                    return False
                rcode.click()
                time.sleep(2)
                self.selenium.switchToLatestWindow()
                waitLoadProgressDone(self.selenium)
                kwargs= {"selector": CSS_DEVICE_INVENTORY_MAC_ADDRESS, "waittype":"located", "timeout":10}
                rcode = self.selenium.findSingleCSS(**kwargs)
                rcode = rcode.text
                if i != rcode:
                    print("Mac address in inventory does not match search input")
                    return False
                self.selenium.driver.close()
                self.selenium.switchToEarliestWindow()

            # Searches 'Macintosh' in the search bar
            elif i == "Macintosh":
                # Gets a 'Macintosh' from the devices dropdown
                time.sleep(2)
                kwargs["selector"] = CSS_GLOBAL_SEARCH_DROPDOWN_DEVICES_IOT_PROFILE
                r = self.selenium.findMultiCSS(**kwargs)
                rcode = r[0]
                rcode2 = r[1]
                iotProfile = rcode.text
                iotProfile2 = rcode2.text
                if i != iotProfile and i!= iotProfile2:
                    for ju in r:
                        print(ju.text)
                    print("IoT profile in dropdown devices does not match search input")
                    return False
                
                #kwargs["selector"] = CSS_GLOBAL_SEARCH_DEVICES_MAC_ADDRESS
                #rcode = self.selenium.findSingleCSS(**kwargs)
                rcode.click()
                
                self.selenium.switchToLatestWindow()
                waitLoadProgressDone(self.selenium)
                kwargs= {"selector": CSS_DEVICE_INVENTORY_IOT_PROFILE, "waittype":"visibility", "timeout":10}
                rcode = self.selenium.findSingleCSS(**kwargs)
                rcode = rcode.text
                if i not in rcode:
                    print("IoT profile in inventory does not match search input")
                    print (i)
                    print (rcode)
                    return False
                self.selenium.driver.close()
                self.selenium.switchToEarliestWindow()

            # Searches IP address in the search bar
            elif i == "192.168.10.105":
                # Gets IP address from the devices dropdown
                kwargs["selector"] = ".zt-global-search-group-item-devices > .ng-tns-c7-16"
                rcode = self.selenium.findMultiCSS(**kwargs)
                ipAddress = rcode[1].text
                if i != ipAddress:
                    print("IP Address dropdown does not match input")
                    return False
                rcode[1].click()
                time.sleep(2)
                self.selenium.switchToLatestWindow()
                waitLoadProgressDone(self.selenium)
                kwargs= {"selector": CSS_DEVICE_INVENTORY_IP_ADDRESS, "waittype":"visibility", "timeout":10}
                rcode = self.selenium.findMultiCSS(**kwargs)
                rcode = rcode[0].text
                if i != rcode:
                    print("IP address in inventory does not match search input")
                    return False
                self.selenium.driver.close()
                self.selenium.switchToEarliestWindow()

        self.cleanup()
        return True

        '''
        <div _ngcontent-c7="" class="ng-tns-c7-16 group-item zt-global-search-group-item-devices ng-star-inserted" fxlayout="row" fxlayoutalign="space-between center" style="flex-direction: row; box-sizing: border-box; display: flex; place-content: center space-between; align-items: center;"><div _ngcontent-c7="" class="device-iot-wraper" fxflex="25" fxlayout="row" fxlayoutalign="start center" style="flex-direction: row; box-sizing: border-box; display: flex; place-content: center flex-start; align-items: center; flex: 1 1 100%; max-width: 25%;"><!----><!----><img _ngcontent-c7="" class="iot-icon iot-non ng-tns-c7-16 ng-star-inserted" src=""><!----><div _ngcontent-c7="" class="ng-tns-c7-16" fxflex="" style="flex: 1 1 0%; box-sizing: border-box;">inspector-000ec4ce28e4</div></div><div _ngcontent-c7="" class="ng-tns-c7-16" fxflex="20" style="flex: 1 1 100%; box-sizing: border-box; max-width: 20%;">00:0e:c4:ce:28:e4</div><div _ngcontent-c7="" class="zing-link" fxflex="20" style="flex: 1 1 100%; box-sizing: border-box; max-width: 20%;"><mark>Zing</mark>Box-Inspector</div><!----><div _ngcontent-c7="" fxflex="10" class="ng-tns-c7-16 ng-star-inserted" style="flex: 1 1 100%; box-sizing: border-box; max-width: 10%;">192.168.10.227</div><div _ngcontent-c7="" class="ng-tns-c7-16" fxflex="10" style="flex: 1 1 100%; box-sizing: border-box; max-width: 10%;"></div><div _ngcontent-c7="" class="zing-link" fxflex="15" style="flex: 1 1 100%; box-sizing: border-box; max-width: 15%;"><!----><!---->Explore Topology</div></div>
        '''
        
    def verifyGlobalSearchAlerts(self):
        kwargs = {}
        searchInput = ["Rhombus-Camera", "18:65:90:cd:88:0d", "192.168.10.189" ]

        for i in searchInput:
            kwargs["selector"] = CSS_GLOBAL_SEARCH_ICON
            rcode = self.selenium.findSingleCSS(**kwargs)
            rcode.click()
            kwargs["selector"] = CSS_GLOBAL_SEARCH_FIELD
            kwargs["text"] = i
            self.selenium.findSingleCSS(**kwargs)
            rcode = self.selenium.sendKeys(**kwargs)
            waitLoadProgressDone(self.selenium)
            time.sleep(3)

            # Searches device name in the search bar
            if i == "Rhombus-Camera":
                # Gets device name from the alerts dropdown
                kwargs["selector"] = CSS_GLOBAL_SEARCH_ALERTS_DEVICE_NAME
                rcode = self.selenium.findMultiCSS(**kwargs)
                if not rcode:
                    print (rcode)
                    print("Device name in dropdown alerts does not exist")
                    return False
                nametext = rcode[5].text.split(' ', 1)[0] # Obtains partial text of the alert name due to dropdown
                rcode[5].click()
                self.selenium.switchToLatestWindow() # Alerts now open in new tab
                waitLoadProgressDone(self.selenium)
                kwargs= {"selector": CSS_ALERT_DETAILS_PAGE_ALERT_NAME, "waittype":"visibility", "timeout":10}
                rcode = self.selenium.findSingleCSS(**kwargs)
                if nametext not in rcode.text:
                    print(nametext)
                    print(rcode.text)
                    print("Device name in dropdown alerts does not match search input")
                    return False

            # Searches MAC address in the search bar
            elif i == "18:65:90:cd:88:0d":
                # Gets MAC address from the alerts dropdown
                self.selenium.switchToLatestWindow()
                kwargs["selector"] = CSS_GLOBAL_SEARCH_ALERTS_MAC_ADDRESS
                rcode = self.selenium.findMultiCSS(**kwargs)
                if not rcode:
                    print("Device Mac Address in dropdown alerts does not exist")
                    return False
                mactext = rcode[6].text.split(' ', 1)[0] # Obtains partial text of the MAC Address due to dropdown
                rcode[6].click()
                self.selenium.switchToLatestWindow() # Alerts now open in new tab
                waitLoadProgressDone(self.selenium)
                #time.sleep(2)

                # Hovers over tooltip
                '''
                kwargs= {"selector": CSS_ALERT_DETAILS_PAGE_ALERT_CARD, "waittype":"located", "timeout":10}
                rcode = self.selenium.findSingleCSS(**kwargs)
                time.sleep(3)
                '''
                # Get the tooltip details
                kwargs= {"selector": CSS_GLOBAL_SEARCH_DEVICES_MAC_ADDRESS, "waittype":"located", "timeout":10}
                rcode = self.selenium.findMultiCSS(**kwargs)
                if rcode[0].text != i:
                    print(mactext)
                    print(rcode[0].text)
                    print("MAC address in dropdown alerts does not match search input")
                    return False

            # Searches IP address in the search bar
            elif i == "192.168.10.189":
                # Gets IP address from the alerts dropdown
                self.selenium.switchToLatestWindow()
                kwargs["selector"] = CSS_GLOBAL_SEARCH_ALERTS_IP_ADDRESS
                rcode = self.selenium.findMultiCSS(**kwargs)
                if not rcode:
                    print("Device IP Address in dropdown alerts does not match search input")
                    return False
                iptext = rcode[0].text.split(' ', 1)[0] # Obtains partial text of the IP Address due to dropdown
                rcode[0].click()
                self.selenium.switchToLatestWindow() # Alerts now open in new tab
                waitLoadProgressDone(self.selenium)

                # Hovers over tooltip
                '''
                kwargs= {"selector": CSS_ALERT_DETAILS_PAGE_ALERT_CARD, "waittype":"located", "timeout":10}
                rcode = self.selenium.findSingleCSS(**kwargs)
                time.sleep(3) # needed to obtain tooltip details
                '''
                # # Get the tooltip details
                # kwargs= {"selector": CSS_ALERT_DETAILS_PAGE_TOOLTIP_DETAILS, "waittype":"located", "timeout":10}
                # rcode = self.selenium.findMultiCSS(**kwargs)
                # print(rcode[0].text)
                # pdb.set_trace()
                # if iptext not in rcode[0].text:
                #     print("IP address in dropdown alerts does not match search input")
                #     return False
                rcode = self.selenium.findSingleCSS(selector=CSS_ALERT_DETAILS_PAGE_IP_MATCH, timeout=3)
                if iptext not in rcode.text:
                    print(iptext)
                    print(rcode.text)
                    print("IP address in dropdown alerts does not match search input")
                    return False
        self.cleanup()
        return True

    def verifyGlobalSearchResultPage(self):
        searchTerm = "zing"
        nothingHere = False
        kwargs = {}
        try:
            kwargs["selector"] = CSS_GLOBAL_SEARCH_ICON
            rcode = self.selenium.findSingleCSS(**kwargs)
            rcode.click()
        except:
            kwargs["selector"] = CSS_GLOBAL_SEARCH_FIELD
            rcode = self.selenium.findSingleCSSNoHover(**kwargs)
            rcode.click()
        kwargs["selector"] = CSS_GLOBAL_SEARCH_FIELD
        kwargs["text"] = searchTerm
        rcode = self.selenium.findSingleCSSNoHover(**kwargs)
        self.selenium.hoverElement(rcode)
        time.sleep(2)
        rcode.send_keys(searchTerm)
        rcode.send_keys(Keys.ENTER)
        time.sleep(1)
        rcode.send_keys(Keys.ENTER)
        time.sleep(1)
        self.selenium.switchToLatestWindow()
        waitLoadProgressDone(self.selenium)
        card_list = self.selenium.findMultiCSS(selector=globalLocators.CSS_SEARCH_RESULT_CARDS)
        for enum,card in enumerate(card_list):
            card_list2 = self.selenium.findMultiCSS(selector=globalLocators.CSS_SEARCH_RESULT_CARDS)
            first_list = []
            rcode = self.selenium.findMultiCSS(selector=globalLocators.CSS_SEARCH_ITEM,browserobj=card_list2[enum])
            for word in rcode:
                if not re.search(".*"+searchTerm+".*",word.text, flags=re.IGNORECASE):
                    print(word.text)
                    print("~~~~~~~~~~~~MENACING~~~~~~~~~~~~~~~~")
                    nothingHere = True
                print(word.text)
                print("~~~~~~~~~~~~MENACING~~~~~~~~~~~~~~~~")
                first_list.append(word.text)
            card_list2 = self.selenium.findMultiCSS(selector=globalLocators.CSS_SEARCH_RESULT_CARDS)
            self.selenium.click(selector=globalLocators.CSS_VIEW_ALL, browserobj=card_list2[enum])
            waitLoadProgressDone(self.selenium)
            second_list = self.selenium.findMultiCSS(selector=globalLocators.CSS_OTHER_SEARCH_ITEM)
            rangy = len(card_list)
            for ind,ele in enumerate(second_list[:rangy]):
                if not ele.text in first_list:
                    print(ele.text)
                    print("=========")
                    print(first_list[ind])
                    logging.critical("Search results not accurate on View All.")
                    nothingHere = True
            self.selenium.goBack()
            waitLoadProgressDone(self.selenium)
            time.sleep(2)
            card_list2 = self.selenium.findMultiCSS(selector=globalLocators.CSS_SEARCH_RESULT_CARDS)
            second_list = self.selenium.findMultiCSS(selector=globalLocators.CSS_OTHER_SEARCH_ITEM, browserobj=card_list2[enum])
            check_strings = second_list[enum].text.split("\n")
            second_list[enum].click()
            waitLoadProgressDone(self.selenium)
            if(enum == 0):
                rcode = self.selenium.findSingleCSS(selector=DeviceDetailLocators.CSS_INFO_CARD)
                for enumy,string in enumerate(check_strings):
                    if string not in rcode.text and string != "Topology":
                        if(enumy == 0):
                            logging.critical("Device Name {} not matching search result".format(string))
                        elif(enumy==1):
                            logging.critical("MAC Address {} not matching search result".format(string))
                        elif(enumy==2):
                            logging.critical("IP Address {} not matching search result".format(string))
                        elif(enumy==3):
                            logging.critical("Profile {} not matching search result".format(string))
                        elif(enumy==4):
                            logging.critical("Category {} not matching search result".format(string))
                        elif(enumy==5):
                            logging.critical("Vendor {} not matching search result".format(string))
                        nothingHere = True
            elif(enum == 2):
                rcode = self.selenium.findSingleCSS(selector=VulnerabilityLocators.CSS_VULN_DETAIL_CARD)
                for enumy,string in enumerate(check_strings[:-1]):
                    processy = string
                    if(enumy == 0):
                        processed = string.split(' ')
                        processy = processed[0]+": "+processed[1]
                    if processy not in rcode.text:
                        if(enumy == 0):
                            logging.critical("Severity level {} not matching search result".format(string))
                        elif(enumy==1):
                            logging.critical("Vuln Name {} not matching search result".format(string))
                        nothingHere = True
            elif(enum == 3):
                self.selenium.switchToLatestWindow()
                rcode = self.selenium.findSingleCSS(selector=".name.external")
                title = check_strings[0]
                if rcode.text not in title:
                    logging.critical("Topology map for {} not matching search result".format(title))
                    nothingHere = True
            self.selenium.goBack()
            waitLoadProgressDone(self.selenium)


        return not nothingHere


        #Enter search term
    def cleanup(self):
        self.selenium.switchToEarliestWindow()
        self.selenium.driver.refresh()
        waitLoadProgressDone(self.selenium)

    def close(self):
        if self.selenium:
            self.selenium.quit()
