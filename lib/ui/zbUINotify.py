#!/usr/bin/python

from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import WebDriverException
from time import sleep
from urllib.parse import urlparse
from ui.login.zbUILoginCore import Login
from ui.zbUIShared import *
from common.zbCommon import validateDataNotEmpty
import pdb, time

# global CSS parameters for Policies/Alert > Notify page
CSS_SELECTOR_CHIP_INPUT = "input.md-input[type='search']"
CSS_SELECTOR_INPUT_OPTIONS_CHIPS = "md-virtual-repeat-container > div.md-virtual-repeat-scroller > div.md-virtual-repeat-offsetter > ul > li"

CSS_NOTIFY_SELECT_SYSTEM = "[md-search-text='notifyCtrl.systemText'][md-selected-item='notifyCtrl.selectedSystemItem'] [name=''][type='search']"
CSS_NOTIFY_SELECT_THREAT = "[md-search-text='notifyCtrl.threatText'] [name=''][type='search']"
CSS_NOTIFY_SELECT = "[type='search']"
CSS_NOTIFY_THREAT_SECTION = 'div.threat-section'
CSS_NOTIFY_SYSTEM_SECTION = 'div.system-section'
CSS_NOTIFY_USERS = "md-autocomplete-parent-scope strong.ng-binding"
CSS_NOTIFY_USER_CHIP = "md-chip.ng-scope" #"[ng-model='notifyCtrl.threatUserList'] md-chip[ng-repeat='$chip in $mdChipsCtrl.items']" #'md-chips > * > md-chip'
CSS_CHIP_REMOVE_BUTTON = 'button.md-chip-remove'
CSS_NOTIFY_SAVE_BUTTON = 'button[ng-click="notifyCtrl.submitTenantNotificationSettings()"]'
CSS_BUTTON_WRAPPER = "li.ng-scope"


class Notify():
    def __init__(self, **kwargs):
        self.params = kwargs
        self.selenium = Login(**kwargs).login()


    def gotoNotify(self):
        # go to Policies/Alerts > Notify
        url = urlparse(self.params["url"])
        rcode = self.selenium.getURL(url.scheme+'://'+url.netloc+'/policiesalerts/notifications')
        waitLoadProgressDone(self.selenium)


    def verifyThreatNotifications(self, **kwargs):
        self.gotoNotify()
        rcode = self.configAddThreatNotifications(**kwargs)
        return rcode


    def verifySystemNotifications(self, **kwargs):   
        self.gotoNotify()    
        rcode = self.configAddSystemNotifications(**kwargs)
        return rcode

    def configAddThreatNotifications(self, **kwargs):
        
        # set default user if none entered
        # Using 'aaa Zbat Automation' in list because other accounts could not be found in dropdown or due to the need to scroll down

        user = kwargs["user"] if "user" in kwargs  else ["aaa Zbat Automation"]
        user = [x.lower() for x in user]
        user = ''.join(user)

        # initialize by delete all pre-existing user first
        self.configDeleteNotifyUser(user)

        # configure threat notification
        params = {"selector": CSS_NOTIFY_THREAT_SECTION, "waittype":"visibility", "timeout":3}
        threat = self.selenium.findSingleCSS(**params)
        params = {"selector": CSS_NOTIFY_SELECT_THREAT, "waittype":"visibility", "timeout":3}
        threatNotify = self.selenium.findSingleCSS(**params)
        if not threatNotify:
            print("Notification Threats not able to find recipient fields.")
            return False
        threatNotify.click()
        time.sleep(1)
        
        
        threatNotify.send_keys("aaa")
        params = {"selector":CSS_NOTIFY_USERS, "waittype":"located", "timeout":3, "err_msg": "Unable to find users again"}
        rcode = self.selenium.findMultiCSS(**params)
        if not rcode:
            print("Notification not able to find any users for System recipient")
        for index, item in enumerate(rcode):
            if item.text.strip().lower() in user:
                item.click()
                time.sleep(1)
                break

        threatNotify.click()
        threatNotify.send_keys(Keys.ESCAPE)
        time.sleep(1)

        params = {"selector": CSS_NOTIFY_SAVE_BUTTON, "waittype":"visibility", "timeout":3}
        rcode = self.selenium.click(**params)

        # make sure that it's properly added
        rcode = self.configCheckUserExist(user, usertype="threat")
        
        return rcode


    def configAddSystemNotifications(self, **kwargs):
        # set default user if none entered
        # Using 'aaa Zbat Automation' in list because other accounts could not be found in dropdown or due to the need to scroll down
        user = kwargs["user"] if "user" in kwargs  else ["aaa Zbat Automation"]
        user = [x.lower() for x in user]

        # initialize by delete all pre-existing user first
        self.configDeleteNotifyUser(user)

        # configure System notification
        params = {"selector": CSS_NOTIFY_SYSTEM_SECTION, "waittype":"visibility", "timeout":3}
        system = self.selenium.findSingleCSS(**params)
        params = {"selector": CSS_NOTIFY_SELECT_SYSTEM, "waittype":"located", "timeout":3}
        systemNotify = self.selenium.findSingleCSS(**params)
        if not systemNotify:
            print("Notification System not able to find recipient fields.")
            return False
        
        
        systemNotify.click()
        time.sleep(1)
        
        
        systemNotify.send_keys("aaa")
        params = {"selector":CSS_NOTIFY_USERS, "waittype":"located", "timeout":3, "err_msg": "Unable to find users again"}
        rcode = self.selenium.findMultiCSS(**params)
        if not rcode:
            print("Notification not able to find any users for System recipient")
        for index, item in enumerate(rcode):
            if item.text.strip().lower() in user:
                item.click()
                time.sleep(1)
                break

        systemNotify.click()
        systemNotify.send_keys(Keys.ESCAPE)
        time.sleep(1)
        waitLoadProgressDone(self.selenium)
        params = {"selector": CSS_NOTIFY_SAVE_BUTTON, "waittype":"visibility", "timeout":3}
        rcode = self.selenium.click(**params)

        # make sure that it's properly added
        rcode = self.configCheckUserExist(user, usertype="system")
        return rcode


    def configDeleteNotifyUser(self, user):
        userlist = [user] if type(user) == str else user
        #userlist = [x.lower() for x in userlist]

        '''
        params = {"selector": CSS_NOTIFY_THREAT_SECTION, "waittype":"visibility", "timeout":3}
        section = self.selenium.findSingleCSS(**params)
        params = {"browserobj": section, "selector": CSS_NOTIFY_SELECT, "waittype":"visibility", "timeout":3}
        field = self.selenium.findSingleCSS(**params)
        if not field:
            print "Notification field not able to find any recipient"
            return False
        '''
        params = {"selector": CSS_NOTIFY_USER_CHIP, "waittype":"located", "timeout":5}
        
        chips = self.selenium.findMultiCSS(**params)
        
        if not chips:
            print("No chips found")
            # if no chips found, then no need to delete, return True.
            return True
        for chip in chips:
            chiptext = chip.text.split('\n')[0]
            if chiptext.strip().lower() in userlist:
                params = {"browserobj":chip, "selector":CSS_CHIP_REMOVE_BUTTON, "waittype":"clickable", "timeout":3}
                rcode = self.selenium.click(**params)
                #field.send_keys(Keys.ENTER)
        time.sleep(1)
        params = {"selector": CSS_NOTIFY_SAVE_BUTTON, "waittype":"visibility", "timeout":3}
        rcode = self.selenium.click(**params)
        return rcode



    def configCheckUserExist(self, userlist, usertype="threat"):
        self.gotoNotify()

        #userlist = [x.lower() for x in userlist]
        print(userlist)

        # configure threat notification
        if usertype == "threat":
            params = {"selector": CSS_NOTIFY_THREAT_SECTION, "waittype":"visibility", "timeout":3}
        if usertype == "system":
            params = {"selector": CSS_NOTIFY_SYSTEM_SECTION, "waittype":"visibility", "timeout":3}

        section = self.selenium.findSingleCSS(**params)
        params = {"browserobj": section, "selector": CSS_NOTIFY_SELECT, "waittype":"visibility", "timeout":3}
        field = self.selenium.findSingleCSS(**params)
        if not field:
            return False
        params = {"browserobj": section, "selector": CSS_NOTIFY_USER_CHIP, "waittype":"visibility", "timeout":5}
        chips = self.selenium.findMultiCSS(**params)

        if not chips:
            print("no matching user chip found")
            return False
        for chip in chips:
            chiptext = chip.text.split('\n')[0]
            if chiptext.strip().lower() in userlist:
                # found user match
                return True
        return False

    def close(self):
        if self.selenium:
            self.selenium.quit()
