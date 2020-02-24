#!/usr/bin/python

import pdb
import time
import re
import calendar
from selenium.webdriver.common.keys import Keys
from time import sleep
from urllib.parse import urlparse
from ui.login.zbUILoginCore import Login
from ui.zbUIShared import waitLoadProgressDone
from common.zbCommon import validateDataNotEmpty
from datetime import datetime
import lib.api.zbAPI
#from common.zbTrafficGenerator import Ostinato
#from ui.alerts.zbUIAlerts import CSS_SELECTOR_ALERT_POLICY_TITLE
from selenium.webdriver.common.action_chains import ActionChains
import logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

CSS_SELECTOR_ALERT_POLICY_TITLE = "zing-alert-list .policy-list .list-item div.word"
# global CSS parameters for Policies page
CSS_SELECTOR_SEVERITY_OPTIONS = ".mat-select-panel [role='option']" #"md-option[name^='Change severity option']"
CSS_SELECTOR_SEVERITY_DROPDOWN = "[formcontrolname='severity']" #"md-select[ng-model='policyDetailCtrl.ruleData.action.severity']"
CSS_SELECTOR_ADD_BUTTON = ".clickable.add-circle.md24"
CSS_SELECTOR_CREATE_BUTTON = "[aria-label='create'] .mat-button" #"button.md-raised.md-primary.md-button.md-ink-ripple.zing-hide-for-readonly.ng-scope"
CSS_SELECTOR_POLICY_NAME_INPUT = ".mat-form-field-infix [formcontrolname='name']"
CSS_SELECTOR_NOTIFY_RADIO_BUTTON = ".mat-radio-container .mat-radio-outer-circle" #"md-radio-button.md-primary.flex"
CSS_SELECTOR_CHIP_INPUT = "input.md-input[type='search']"
CSS_SELECTOR_INPUT_OPTIONS_CHIPS = "md-virtual-repeat-container > div.md-virtual-repeat-scroller > div.md-virtual-repeat-offsetter > ul > li"
CSS_SELECTOR_GROUP_CHECKBOX = "md-checkbox.md-primary"
CSS_SELECTOR_DATE_INPUT = "span.working-day"
CSS_SELECTOR_POLICY_OPTIONS = "i.clickable.dp24.material-icons.mt5.flex-center"
CSS_SELECTOR_POLICY_DELETE_BUTTON = "div.md-open-menu-container.md-clickable > md-menu-content > md-menu-item > button[name='deleted']"

CSS_POLICY_DROPDOWN_OPT = ".mat-autocomplete-panel .mat-checkbox-label"

CSS_POLICY_SEVERITY_INFO = 'md-option[name="Change severity option to info"]'
CSS_POLICY_SEVERITY_WARNING = 'md-option[name="Change severity option to low"]'
CSS_POLICY_SEVERITY_CAUTION = 'md-option[name="Change severity option to medium"]'
CSS_POLICY_SEVERITY_CRITICAL = 'md-option[name="Change severity option to high"]'

CSS_POLICY_NOTIFY_BLACKLIST = "[for='mat-radio-2-input'] .mat-radio-container" #'md-radio-button[name="Pressed Notify when Described ..."]'
CSS_POLICY_NOTIFY_WHITELIST = ".mat-radio-label[for='mat-radio-3-input'] .mat-radio-container" #'md-radio-button[name="Pressed Notify when Patterns ..."]'

CSS_POLICY_BEHAVIOR_GROUPS = 'input[aria-label="Any Device"]'
CSS_POLICY_APP = "[formcontrolname='application'] [role='combobox']"

CSS_POLICY_DAYS_DISABLE = '.working-day'
CSS_POLICY_DAYS_ENABLE = '.working-day.active'

CSS_POLICIES = '.policy-table .mat-row'
CSS_POLICY_MENU_BUTTON = ".mat-icon-button .mat-icon" #"i.clickable"
CSS_POLICY_NAME = '.policy-name'
CSS_POLICY_DELETE = 'div.md-open-menu-container[aria-hidden=false] > * > * > button[action=deleted]'
CSS_POLICY_MENU_SELECTORS = "[role='menuitem']"


#Offline specific stuff
CSS_ALERT_ELEMENT = "div.word.ng-binding"
CSS_TIME_RANGE_1DAY = "button[category='Date Range Selector'][name='Set the date range selector to Last Day']"
CSS_NEXT_PAGE = "[ng-click='alertListCtrl.next()'] .ng-scope.material-icons"
CSS_ROW_COUNT_DROP = "md-select[ng-model='alertListCtrl.numPerPage']"
CSS_ROW_COUNT_200 = "md-option.ng-scope[value='200'][ng-repeat='option in alertListCtrl.rowPerPageOptions']"
CSS_ALERT_STATUS_DROP = "[name='Open alert severity dropdown'] md-select-value"
CSS_ALERT_STATUS_INFO = "[name='Picked Info severity']"

CSS_POLICY_EDIT_BUTTON = "div.zing-hide-for-readonly"
CSS_POLICY_OFFLINE_NAME = "[aria-invalid='true'][ng-model='policyDetailCtrl.ruleData.name']"

CSS_OFFLINE_RADIO = "[category='Policy Configuration Policy Type'][name='Select Offline Policy'] div.md-container"
CSS_GROUP_TEXT = "[ng-required='$mdAutocompleteCtrl.isRequired']"
CSS_POLICY_CREATE_BUTTON = "button.zing-hide-for-readonly[category='Policy Configuration']"

CSS_POLICY_ENTRY = ".ng-binding.policy-name"#"span.ng-binding.policy-name.left-word[ng-click='policyListCtrl.goDetail(policy)']"

CSS_EDIT_SELECTIONS = "[aria-hidden='false'] i.dp24.clickable"
CSS_POLICY_DELETE_BUTTON =".md-active md-menu-item button[ng-click='policyListCtrl.delete(policy)']"

CSS_DROPDOWN_ELEMENT = "md-autocomplete-parent-scope.ng-scope[md-autocomplete-replace='']"

CSS_SEARCH_BAR = ".search-input"

CSS_ALERT_DATE = "[aria-hidden='false'] div.alert-column.ng-binding[flex='10'][layout-align='center']"


CSS_POLICY_BEHAVIOR_DEVICES = "[formcontrolname='device'][category='Policy Configuration']"
CSS_POLICY_BEHAVIOR_DESTINATION = "[formcontrolname='destination'][category='Policy Configuration']"
CSS_POLICY_GROUP_DROPDOWN_PANE = ".mat-autocomplete-panel"
CSS_POLICY_GROUP_DROPDOWN_OPTION = ".mat-option-text"
CSS_POLICY_BEHAVIOR_DEVICES_INPUT = "[formcontrolname='device'] [role='combobox']"
CSS_POLICY_BEHAVIOR_DESTINATION_INPUT = "[formcontrolname='destination'] [role='combobox']"


class Policies(object):
    def __init__(self, **kwargs):
        self.params = kwargs
        if "selenium" in kwargs:
            self.selenium = kwargs["selenium"]
        else:
            self.selenium = Login(**kwargs).login()


    def gotoPolicyPage(self):
        # go to Policies/Alerts > Policies
        curr_url = self.selenium.getCurrentURL()
        if '/guardian/policies' in curr_url:
            return
        curr_url = urlparse(curr_url)
        rcode = self.selenium.getURL(curr_url.scheme+'://'+curr_url.netloc+'/guardian/policies')
        waitLoadProgressDone(self.selenium)

    def verifyPolicy(self, **kwargs):
        name = kwargs["name"] if "name" in kwargs else "zbat test policy"
        self.gotoPolicyPage()

        # clean up any existing
        exist = self.checkPolicyExist(name)
        if exist:
            self.configDeletePolicy(name)

        # add policy
        rcode = self.configAddPolicy()
        # confirm add successful
        if rcode: 
            exist = self.checkPolicyExist(name)
        if not exist:
            print("Cannot find policy "+name)
            return False

        # clean up
        self.configDeletePolicy(name)
        return rcode

    def configAddPolicy(self, add=True, **policyconfig):
        # click add
        if add:
            params = {}
            params["selector"] = CSS_SELECTOR_ADD_BUTTON
            self.selenium.click(**params)
        
        # create policy
        clickparams = {}
        clickparams["selector"] = CSS_SELECTOR_CREATE_BUTTON
        clickparams["waittype"] = 'clickable'
        self.selenium.waitCSS(**clickparams)

        # configure policy severity
        params = {}
        severity = policyconfig["severity"] if "severity" in policyconfig else "critical"
        params["selector"] = CSS_SELECTOR_SEVERITY_DROPDOWN
        self.selenium.click(**params)

        params["selector"] = CSS_SELECTOR_SEVERITY_OPTIONS
        opts = self.selenium.findMultiCSSNoHover(**params)
        '''
        if "critical" in severity.lower():
            clickparams = {"selector": CSS_POLICY_SEVERITY_CRITICAL, "waittype":"visibility", "timeout":3}
        if "warning" in severity.lower():
            clickparams = {"selector": CSS_POLICY_SEVERITY_WARNING, "waittype":"visibility", "timeout":3}
        if "caution" in severity.lower():
            clickparams = {"selector": CSS_POLICY_SEVERITY_CAUTION, "waittype":"visibility", "timeout":3}
        if "info" in severity.lower():
            clickparams = {"selector": CSS_POLICY_SEVERITY_INFO, "waittype":"visibility", "timeout":3}
        '''
        for scry in opts:
            if scry.text.lower() == severity.lower():
                print (scry.text)
                clicky = scry
                clicky.click()
                break
        time.sleep(1)
        
        # enter policy name
        name = policyconfig["name"] if "name" in policyconfig else "zbat test policy"
        typeparams = {"selector":CSS_SELECTOR_POLICY_NAME_INPUT, "text":name, "waittype":"visibility", "timeout":3}
        self.selenium.sendKeys(**typeparams)

        # configure notification
        notify = policyconfig["notify"] if "notify" in policyconfig else "blacklist"
        if "blacklist" not in notify:
            clickparams = {"selector": CSS_POLICY_NOTIFY_WHITELIST, "waittype":"visibility", "timeout":3}
        else:
            clickparams = {"selector": CSS_POLICY_NOTIFY_BLACKLIST, "waittype":"visibility", "timeout":3}
        self.selenium.click(**clickparams)

        # configure group1
        group1 = policyconfig["group1"] if "group1" in policyconfig else ["Intranet"]
        rcode = self.selenium.findSingleCSS(selector=CSS_POLICY_BEHAVIOR_DEVICES, waittype="located", timeout=3)
        g1 = self.selenium.findSingleCSS(selector=CSS_POLICY_BEHAVIOR_DEVICES, waittype="located", timeout=3)
        g2 = self.selenium.findSingleCSS(selector=CSS_POLICY_BEHAVIOR_DESTINATION, waittype="located", timeout=3)
        for item in group1:
            g1.click()
            time.sleep(1)
            rcode = self.selenium.findSingleCSS(selector=CSS_POLICY_BEHAVIOR_DEVICES_INPUT, waittype="located", timeout=3)
            rcode.send_keys(item)
            time.sleep(2)
            rcode = self.selenium.findSingleCSS(selector=CSS_POLICY_GROUP_DROPDOWN_OPTION, waittype="located", timeout=3)
            rcode.click()
            #rcode.send_keys(item+Keys.ARROW_DOWN+Keys.ARROW_DOWN+Keys.ENTER)
            time.sleep(1)
            rcode = self.selenium.findSingleCSS(selector=CSS_POLICY_BEHAVIOR_DEVICES_INPUT, waittype="located", timeout=3)
            rcode.send_keys(Keys.ESCAPE)
        time.sleep(1)

        # configure group2
        group2 = policyconfig["group2"] if "group2" in policyconfig else ["External (Domestic)"]
        for item in group2:
            g2.click()
            time.sleep(1)
            rcode = self.selenium.findSingleCSS(selector=CSS_POLICY_BEHAVIOR_DESTINATION_INPUT, waittype="located", timeout=3)
            rcode.send_keys(item)
            time.sleep(2)
            rcode = self.selenium.findSingleCSS(selector=CSS_POLICY_GROUP_DROPDOWN_OPTION, waittype="located", timeout=3)
            rcode.click()
            #rcode.send_keys(item+Keys.ARROW_DOWN+Keys.ARROW_DOWN+Keys.ENTER)
            time.sleep(1)
            rcode = self.selenium.findSingleCSS(selector=CSS_POLICY_BEHAVIOR_DESTINATION_INPUT, waittype="located", timeout=3)
            rcode.send_keys(Keys.ESCAPE)
        time.sleep(1)

        # configure app
        apps = policyconfig["apps"] if "apps" in policyconfig else ["https"]
        params = {"selector": CSS_POLICY_APP, "waittype":"located", "timeout":3}
        rcode = self.selenium.findSingleCSS(**params)
        for item in apps:
            rcode.click()
            time.sleep(1)
            rcode.send_keys(item)
            time.sleep(2)
            rcode = self.selenium.findSingleCSS(selector=CSS_POLICY_GROUP_DROPDOWN_OPTION, waittype="located", timeout=3)
            rcode.click()
            #rcode.send_keys(item+Keys.ARROW_DOWN+Keys.ARROW_DOWN+Keys.ENTER)
            time.sleep(1)
            rcode = self.selenium.findSingleCSS(selector=CSS_POLICY_BEHAVIOR_DESTINATION_INPUT, waittype="located", timeout=3)
            rcode = self.selenium.findSingleCSS(**params)
            rcode.send_keys(Keys.ESCAPE)
        time.sleep(1)

        # configure time
        days = policyconfig["days"] if "days" in policyconfig else ['Su','Tu']
        # lowercase all str in time
        days = [x.lower() for x in days]
        if len(days) > 0:
            # initialize by disable all days
            params = {"selector": CSS_POLICY_DAYS_ENABLE, "waittype":"visibility", "timeout":5}
            rcode = self.selenium.findMultiCSS(**params)
            if rcode:
                for day in rcode: day.click()

            # enable day based on input
            params = {"selector": CSS_POLICY_DAYS_DISABLE, "waittype":"visibility", "timeout":5}
            rcode = self.selenium.findMultiCSS(**params)
            if rcode:
                for day in rcode:
                    if day.text.strip().lower() in days: day.click()

        # save
        time.sleep(1)
        params = {"selector": CSS_SELECTOR_CREATE_BUTTON, "waittype": "clickable", "timeout":10}
        rcode = self.selenium.findSingleCSS(**params)
        rcode.click()

        return rcode


    def configDeletePolicy(self, policyname):
        self.gotoPolicyPage()
        params = {"selector": CSS_POLICIES, "waittype":"visibility", "timeout":3}
        rcode = self.selenium.findMultiCSS(**params)
        if rcode:
            for policy in rcode:
                params = {"selector": CSS_POLICY_NAME, "waittype":"visibility", "timeout":3}
                name = self.selenium.findSingleCSS(**params)
                if name:
                    if name.text.strip() == policyname.strip():
                        params = {"browserobj": policy, "selector": CSS_POLICY_MENU_BUTTON, "waittype":"visibility", "timeout":3}
                        self.selenium.click(**params)
                        params = {"selector": CSS_POLICY_MENU_SELECTORS, "waittype":"visibility", "timeout":3}
                        rc = self.selenium.findMultiCSS(**params)
                        for item in rc:
                            if "Delete" in item.text:
                                item.click()
                                time.sleep(1)
                        self.gotoPolicyPage()
        return True


    def checkPolicyExist(self, policyname):
        self.gotoPolicyPage()
        params = {"selector": CSS_POLICIES, "waittype":"visibility", "timeout":3}
        rcode = self.selenium.findMultiCSS(**params)
        if rcode:
            for policy in rcode:
                params = {"selector": CSS_POLICY_NAME, "waittype":"visibility", "timeout":3}
                name = self.selenium.findSingleCSS(**params)
                if name:
                    if name.text.strip() == policyname.strip():
                        return policy
        return False

    def close(self):
        if self.selenium:
            self.selenium.quit()


#=============OFFLINE ADDITION====================

class Actions(ActionChains):
    def wait(self, time_s):
        self._actions.append(lambda: time.sleep(time_s))
        return self

def processList(browser, inputy, matcher):
    params = {}
    pattern = re.compile(matcher)
    for element in inputy:
        if pattern.match(element.text) is not None:
            element.click()
            params["selector"] = CSS_ALERT_DATE
            datey = browser.findSingleCSS(**params)
            alert_date = datetime.strptime(datey.get_attribute('innerHTML'), "%H:%M %B %d, %Y")
            today = datetime.today()
            delta = today - alert_date
            if delta.days < 1:
                return True
    return False

def verifyOfflineAlerts(browser):
    params = {}
    rcode = False
    pages = 0
    policy_list = [
    "zing offline testing profiles - DO NOT DELETE",
    "zing offline testing category - DO NOT DELETE",
    "zing offline testing hostname - DO NOT DELETE"
    ]
    #params["selector"] = CSS_TIME_RANGE_1DAY
    #browser.click(**params)
    #waitLoadProgressDone(browser)
    params["selector"] = CSS_ROW_COUNT_DROP
    browser.click(**params)
    time.sleep(1)
    params["selector"] = CSS_ROW_COUNT_200
    browser.click(**params)
    waitLoadProgressDone(browser)
    params["selector"] = CSS_ALERT_STATUS_DROP
    browser.click(**params)
    time.sleep(1)
    params["selector"] = CSS_ALERT_STATUS_INFO
    browser.click(**params)
    waitLoadProgressDone(browser)

    while pages < 5:
        try:
            alert_list = browser.findMultiCSS(selector=CSS_ALERT_ELEMENT)
            for policy_name in policy_list:
                if processList(browser, alert_list, policy_name) == True:
                    policy_list.remove(policy_name)
                    rcode = True
            if len(policy_list) == 0:
                return True
            else:
                rcode = False
            params["selector"] = CSS_NEXT_PAGE
            browser.click(**params)
            waitLoadProgressDone(browser)
            pages = pages + 1
        except Exception as e:
            print(e)
            print("ERROR: Alerts not found")
            rcode = False
            break

    return rcode

def makeOfflinePolicy(browser, group_entry):
    params = {}
    try:
        flag = True
        try:
            params["selector"] = CSS_POLICY_ENTRY
            entries = browser.findMultiCSS(**params)
            for entry in entries:
                if entry.text == "zbat offline temp test":
                    time.sleep(2)
                    flag = False
                    break
            if flag == True:
                raise Exception('K')
        except:
            params["selector"] = CSS_POLICY_EDIT_BUTTON
            browser.click(**params)
            params["selector"] = CSS_POLICY_OFFLINE_NAME
            element = browser.findSingleCSS(**params)
            element.click()
            element.send_keys("zbat offline temp test")
            params["selector"] = CSS_OFFLINE_RADIO
            browser.click(**params)
        params["selector"] = CSS_GROUP_TEXT

        element = browser.findSingleVisibleCSS(**params)
        #browser.executeScript("arguments[0].click()",**params)
        actions = Actions(browser.driver)
        actions.click(element)
        actions.wait(1)
        actions.send_keys(group_entry)
        actions.wait(1)
        actions.send_keys(Keys.ARROW_DOWN+Keys.ARROW_DOWN+Keys.ENTER)
        actions.perform()
        params["selector"] = CSS_POLICY_CREATE_BUTTON
        browser.click(**params)

        return True
    except Exception as E:
        print(E)
        return False



def checkAndDeletePolicy(browser, policy_name):
    params = {}
    try:
        params["selector"] = CSS_SEARCH_BAR
        bar = browser.findSingleCSS(**params)
        bar.click()
        bar.send_keys("zbat offline temp test" + Keys.ENTER)
        waitLoadProgressDone(browser)
        params["selector"] = CSS_POLICY_ENTRY
        params["timeout"] = 3
        entries = browser.findMultiCSS(**params)
        params["selector"] = CSS_EDIT_SELECTIONS
        selections = browser.findSingleCSS(**params)
        selections.click()
        waitLoadProgressDone(browser)
        params["selector"]  = CSS_POLICY_DELETE_BUTTON
        deletes = browser.findSingleCSS(**params)
        deletes.click()
        waitLoadProgressDone(browser)
        return True
    except Exception as E:
        return False




class Offline:
    def __init__(self, **kwargs):
        self.params = kwargs
        self.selenium = Login(**kwargs).login()

    def gotoPolicies(self):
        # go to MonitorS > Device Inventory
        url = urlparse(self.params["url"])
        rcode = self.selenium.getURL(url.scheme+'://'+url.netloc+'/policiesalerts/policies')
        waitLoadProgressDone(self.selenium)

    def gotoAlerts(self):
        url = urlparse(self.params["url"])
        rcode = self.selenium.getURL(url.scheme+'://'+url.netloc+'/policiesalerts/alerts?interval=oneday')
        waitLoadProgressDone(self.selenium)

    def checkOfflinePolicy(self,group_entry):
        self.gotoPolicies()
        rcode = True
        rcode2 = True
        rcode = makeOfflinePolicy(self.selenium, group_entry)
        rcode2 = checkAndDeletePolicy(self.selenium, "zbat offline temp test")
        return rcode and rcode2

    def checkOfflineAlerts(self):
        self.gotoAlerts()
        rcode = True
        rcode = verifyOfflineAlerts(self.selenium)
        return rcode
    
    def close(self):
        if self.selenium:
            self.selenium.quit()
