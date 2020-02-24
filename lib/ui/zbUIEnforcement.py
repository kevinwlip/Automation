#!/usr/bin/python


from common.zbSelenium import zbSelenium
from urllib.parse import urlparse
from ui.login.zbUILoginCore import Login
from zbUIShared import clickEachTimerange, waitLoadProgressDone, waitSeriesGraphDone, verifyDataTimerange
from common.zbCommon import validateDataNotEmpty
import pdb,time


# Global CSS for Administration > Enforcement page
CSS_ADD_ENFORCEMENT_BUTTON = "div[class='individual-card add-firewall layout-align-center-center layout-column'] > div > button.md-icon-button"
CSS_CONFIG_BUTTON = "button.icon-button"
CSS_FIREWALL_LABEL = "input[name='firewallname']"
CSS_FIREWALL_DETAILS = "md-select[ng-model='fwCreateCtrl.input.model']"
CSS_FIREWALL_PA200_SELECT = "md-option[value='PA-200']"
CSS_IP_ADDRESS_LABEL = "input[name='ip']"
CSS_PORT_NUMBER_LABEL = "input[name='port']"
CSS_USERNAME_LABEL = "input[name='username']"
CSS_PASSWORD_LABEL = "input[name='password']"
CSS_INSPECTOR_DROPDOWN = "md-select[ng-model='fwCreateCtrl.input.inspectorid']"
CSS_INSPECTORS = 'md-option[ng-repeat="inspector in fwCreateCtrl.inspectorList track by inspector.inspectorid"]'
CSS_INSPECTOR_TESTING_OPTION = "md-option[value='564D29485CF37A7869FCF2090864B53F']"
CSS_TEST_CONNECTION_BUTTON = "div.test-connection"
CSS_SAVE_BUTTON = "button[ng-click='fwCreateCtrl.save()']"
CSS_CONNECTED_TEXT = "span[class='connected-check ng-scope']"
CSS_TEST_CASE_PROFILE = "zing-firewall[data]"

CSS_FW_CARDS = "zing-firewall[data=firewall]"
CSS_FW_TITLE = 'h3[ng-bind="fwCtrl.data.name"]'
CSS_FW_OPTION_BUTTON = 'ng-md-icon[icon="more_vert"]'
CSS_FW_DELETE_BUTTON = 'div.md-clickable > md-menu-content > md-menu-item > button[action=Firewall][name=Remove]'
CSS_FW_CONFIRM_BUTTON = ".confirm[type='button']"


class Enforcement():

    def __init__(self, **kwargs):
        self.params = kwargs
        self.selenium = Login(**kwargs).login()

        rcode = self.selenium.getURL(kwargs["url"]+'/')
        if rcode: waitLoadProgressDone(self.selenium)


    def gotoEnforcementPage(self):
        url = urlparse(self.params["url"])
        rcode = self.selenium.getURL(url.scheme+'://'+url.netloc+'/administration/integrations/firewallIntegration')

    def verifyPANFW(self, **kwargs):
        kwargs["name"] = "zbat test panfw"

        # before start, clean up sites        
        rcode = self.configDeletePANFW(kwargs["name"])
        # add new site
        rcode = self.configAddPANFW(**kwargs)
        if not rcode:
            print("PANFW configuration failed.")
            return False
        rcode = self.checkPANFWExist(kwargs["name"])
        if not rcode:
            print("Enforcement add PanFW has issue.  Did not find FW "+str(kwargs["name"])+" after add.")
            return False

        # delete site
        if rcode:
            rcode = self.configDeletePANFW(kwargs["name"])
        rcode = self.checkPANFWExist(kwargs["name"])
        # if site delete correctly, then return True
        return True if not rcode else False


    def configAddPANFW(self, **fwconfig):
        kwargs = {}
        inputs = {
            "name" : "zbat test panfw",
            "address" : "192.168.10.23",
            "port" : "443",
            "username" : "admin",
            "password" : "admin"
        }

        kwargs["selector"] = CSS_ADD_ENFORCEMENT_BUTTON
        rcode = self.selenium.findSingleCSS(**kwargs)
        rcode.click()

        kwargs["selector"] = CSS_CONFIG_BUTTON
        rcode = self.selenium.findSingleCSS(**kwargs)
        rcode.click()

        if 'name' in fwconfig:
            fwName = fwconfig["name"]
        else:
            fwName = inputs["name"]    
        kwargs["selector"] = CSS_FIREWALL_LABEL
        kwargs["text"] = fwName
        time.sleep(0.5)
        for char in fwName: #Slows down the typing to avoid AngularJS bug
            time.sleep(0.5)
            kwargs["text"] = char
            rcode = self.selenium.sendKeys(**kwargs)

        kwargs["selector"] = CSS_FIREWALL_DETAILS
        rcode = self.selenium.findSingleCSS(**kwargs)
        rcode.click()

        kwargs["selector"] = CSS_FIREWALL_PA200_SELECT
        rcode = self.selenium.findSingleCSS(**kwargs)
        rcode.click()

        if 'address' in fwconfig:
            ipAddress = fwconfig["address"]
        else:
            ipAddress = inputs["address"]    

        time.sleep(1)
        kwargs["selector"] = CSS_IP_ADDRESS_LABEL
        kwargs["text"] = ipAddress
        rcode = self.selenium.sendKeys(**kwargs)

        if 'port' in fwconfig:
            portNum = fwconfig["port"]
        else:
            portNum = inputs["port"]

        time.sleep(1)
        kwargs["selector"] = CSS_PORT_NUMBER_LABEL
        kwargs["text"] = portNum
        rcode = self.selenium.sendKeys(**kwargs)

        if 'username' in fwconfig:
            username = fwconfig["username"]
        else:
            username = inputs["username"]
                
        kwargs["selector"] = CSS_USERNAME_LABEL
        kwargs["text"] = username
        rcode = self.selenium.sendKeys(**kwargs)

        if 'password' in fwconfig:
            password = fwconfig["password"]
        else:
            password = inputs["password"]
            
        kwargs["selector"] = CSS_PASSWORD_LABEL
        kwargs["text"] = password
        rcode = self.selenium.sendKeys(**kwargs)

        kwargs["selector"] = CSS_INSPECTOR_DROPDOWN
        rcode = self.selenium.findSingleCSS(**kwargs)
        rcode.click()

        inspector = fwconfig["inspector"]
        found = False
        kwargs = {"selector": CSS_INSPECTORS, "waittype":"visibility", "timeout":3}
        rcode = self.selenium.findMultiCSS(**kwargs)
        if not rcode:
            print("Enforcement config does not have any inspectors")
            return False
        for insp in rcode:
            if inspector.strip() in insp.text.strip():
                insp.click()
                found = True
                break
        if not found: 
            print("Enforcement config not able to find valid inspector "+str(inspector))
            return False
        kwargs = {}


        kwargs["selector"] = CSS_TEST_CONNECTION_BUTTON
        rcode = self.selenium.findSingleCSS(**kwargs)
        rcode.click()
        
        kwargs["selector"] = CSS_CONNECTED_TEXT
        kwargs["waittype"] = "visibility"
        rcode = self.selenium.waitCSS(**kwargs)
        if not rcode:
            print("PANFW configuration was not able to connect")
            return False

        kwargs["selector"] = CSS_SAVE_BUTTON
        rcode = self.selenium.findSingleCSS(**kwargs)
        rcode.click()

        #make sure that after save, UI return to base screen
        rcode = self.selenium.findSingleCSS(selector=CSS_ADD_ENFORCEMENT_BUTTON, waittype="visibility", timeout=3)
        if not rcode:
            print ("Was not able to save Enforcement")
            return False
        else:
            return True


    def checkPANFWExist(self, fwname):
        self.gotoEnforcementPage()
        self.selenium.scrollToBottomPage()

        kwargs = {"selector": CSS_FW_TITLE, "waittype":"visibility", "timeout":3}
        fws = self.selenium.findMultiCSS(**kwargs)
        if not fws:
            print("Not able to find CSS for Firewall names.")
            return False

        for fw in fws:
            if fw.text.strip() == fwname.strip():
                return True

        print("Firewall "+str(fwname)+" not found.")
        return False


    def configDeletePANFW(self, fwname):
        self.gotoEnforcementPage()

        found = False
        kwargs = {"selector": CSS_FW_CARDS, "waittype":"visibility", "timeout":3}
        sites = self.selenium.findMultiCSS(**kwargs)
        if not sites: return True

        for site in sites:
            kwargs = {"browserobj": site, "selector": CSS_FW_TITLE, "waittype":"visibility", "timeout":3}
            namefound = self.selenium.findSingleCSS(**kwargs)
            if namefound:
                if namefound.text.strip() == fwname.strip(): #cleanup clause
                    kwargs = {"browserobj": site, "selector": CSS_FW_OPTION_BUTTON, "waittype":"clickable", "timeout":3}
                    self.selenium.click(**kwargs)
                    
                    kwargs = {"selector": CSS_FW_DELETE_BUTTON, "waittype":"visibility", "timeout":3}
                    self.selenium.click(**kwargs)
                    time.sleep(1)
                    kwargs = {"selector": CSS_FW_CONFIRM_BUTTON, "waittype":"visibility", "timeout":3}
                    self.selenium.click(**kwargs)
                    
                    found = True
                    break    
                else:
                    found = False            
                        
        if not found: 
            # nothing found, meaning all deleted.  return True
            return True
        else:
            # recursively call self to delete more
            self.configDeletePANFW(fwname)

    def close(self):
        if self.selenium:
            self.selenium.quit()
