#!/usr/bin/python

import sys, os, operator, pdb, time, re
from urllib.parse import urlparse
from ui.login.zbUILoginCore import Login
from ui.zbUIShared import *
from common.zbCommon import validateDataNotEmpty
from common.zbEmail import Email_Client
from datetime import datetime
from common.zbConfig import defaultEnv
if sys.version_info >= (3, 0):
    from html.parser import HTMLParser
else:
    from html.parser import HTMLParser

# global CSS parameters for Administration > User page
CSS_SELECTOR_USER_ACCOUNTS_INFO_COLUMNS =['J','K','L','M']
CSS_SELECTOR_USER_ACCOUNTS_GENERAL_SORT_TEST =['J','K','L','M']

CSS_SELECTOR_USER_ACCOUNTS_INFO_COLUMNS_ALTER = ['J','K','L','M']
# CSS_PREFERENCES_DISABLED_SMS = ".notification-checkbox[aria-label='Enable SMS Notifications'][aria-checked='false']"
CSS_PREFERENCES_DISABLED_SMS = "[ng-model='udCtrl.mUserProfile.alertNotifyPref.sms.enabled'][aria-checked='false']"
# CSS_PREFERENCES_ENABLED_SMS = ".notification-checkbox[aria-label='Enable SMS Notifications'][aria-checked='true']"
CSS_PREFERENCES_ENABLED_SMS = "[ng-model='udCtrl.mUserProfile.alertNotifyPref.sms.enabled'][aria-checked='true']"
CSS_PREFERENCES_SAVE = "[name='Save user detail'][type='button']"
CSS_PREFERENCES_CONFIRM = ".md-confirm-button"
CSS_USERNAME_FIELD = "input[ng-model='ctrl.username']"
CSS_NEXT_BUTTON = ".login-bottom-section [ng-click='ctrl.ssoNext()']"

CSS_PAGE_SIZE = "[ng-model='ctrl.pageSize']"
CSS_PAGE_MAX = "[value='200']"

def verifyUserAccountsEntries(browserobj, pageNumber=1, verifyAll=False):
    clickAllCheckboxes(browserobj)
    params = {}
    params["selector"] = CSS_SELECTOR_PAGINATION_INPUT
    pageNumber = min(pageNumber, int(browserobj.findSingleCSS(**params).get_attribute("max")))
    pageNumber = max(pageNumber, 1)
    if pageNumber > 1:
        for i in range(1, pageNumber):
            if verifyAll:
                if _verifyUserAccountRow(browserobj) is False:
                    return False
            params["selector"] = CSS_SELECTOR_CHEVRON_RIGHT_ICON
            browserobj.click(**params)
            waitLoadProgressDone(browserobj)
    if _verifyUserAccountRow(browserobj) is False:
        return False
    return True

def _verifyUserAccountRow(browserobj):
    params = {}
    params["selector"] = CSS_SELECTOR_INVENTORY_ROW
    rows = len(browserobj.findMultiCSS(**params))
    for c in CSS_SELECTOR_USER_ACCOUNTS_INFO_COLUMNS_ALTER:
        params["selector"] = CSS_SELECTOR_GENERAL_TEXT_ENTRY + c
        ret = browserobj.findMultiCSS(**params)
        if len(ret) != rows:
            print("Failed to verify users account Column " + c + ", users row counts not equal to row counts of corresponding attribute")
            return False
        for e in ret:
            if "".join(e.text.split()) == "":
                print("Failed to verify users account Column " + c + ", empty column detected")
                return False
    return True


def verifyUserAccountsSort(browserobj):
    clickAllCheckboxes(browserobj)
    params = {}
    params["selector"] = CSS_SELECTOR_CLICKABLE_SORT_HEADER
    hsort = browserobj.findMultiCSS(**params)
    for l in CSS_SELECTOR_USER_ACCOUNTS_GENERAL_SORT_TEST:

        # click column header until head ascending order
        if not clickUntilFind(browserobj, hsort[ord(l)-ord("A")], CSS_SORT_UP_ARROW):
            print("Cannot find column up arrow button")
            return False

        waitLoadProgressDone(browserobj)
        params["selector"] = CSS_SELECTOR_GENERAL_TEXT_ENTRY + l
        data = browserobj.findMultiCSS(**params)
        try:
            _validateSortOrder('ascending', data)
        except ValueError as e:
            print(e)
            return False

        # click column header until head descending order
        if not clickUntilFind(browserobj, hsort[ord(l)-ord("A")], CSS_SORT_DOWN_ARROW):
            print("Cannot find column down arrow button")
            return False

        waitLoadProgressDone(browserobj)
        params["selector"] = CSS_SELECTOR_GENERAL_TEXT_ENTRY + l
        data = browserobj.findMultiCSS(**params)
        try:
            _validateSortOrder('descending', data)
        except ValueError as e:
            print(e)
            return False
    return True

def _validateSortOrder(sortingType, data):
    op = operator.gt
    if sortingType == 'descending':
        op = operator.lt

    for i in range(0,len(data)-1):
        if data[i].text == '' or data[i+1].text == '':
            # values are not necessary present.  If so, no need to compare
            continue

        topData = data[i].text
        bottomData = data[i + 1].text
        if isinstance(topData, int) or isinstance(topData, float):
            if op(int(topData), int(bottomData)):
                raise ValueError("Sort {} got value error {}   {}".format(sortingType, topData, bottomData))
        elif isinstance(topData, str):
            try:
                if op(datetime.strptime(topData, "%b %d, %Y, %H:%M"), datetime.strptime(bottomData, "%b %d, %Y, %H:%M")):
                    raise Exception("Sort {} datetime out of order {}   {}".format(sortingType, topData, bottomData))
            except ValueError:
                if op(data[i].text.lower(), data[i+1].text.lower()):
                    raise ValueError("Sort {}} got value error {}   {}".format(sortingType, topData, bottomData))
            except Exception as e:
                raise ValueError(e)

def toggleSMS(browserobj, username, enable=True): # Toggles SMS for tests/integration/test_alert_notify.py
    disabled = browserobj.findSingleCSS(selector=CSS_PREFERENCES_DISABLED_SMS, timeout=3)
    enabled = browserobj.findSingleCSS(selector=CSS_PREFERENCES_ENABLED_SMS, timeout=3)
    save = browserobj.findSingleCSS(selector=CSS_PREFERENCES_SAVE, timeout=3)

    if enable == True:
        if disabled:
            disabled.click()
            save.click()
            confirm = browserobj.findSingleCSS(selector=CSS_PREFERENCES_CONFIRM, timeout=3)
            confirm.click()
            enabled = browserobj.findSingleCSS(selector=CSS_PREFERENCES_ENABLED_SMS, timeout=3)
            if enabled:
                return True
    elif enable == False:
        if enabled:
            enabled.click()
            save.click()
            confirm = browserobj.findSingleCSS(selector=CSS_PREFERENCES_CONFIRM, timeout=3)
            confirm.click()
            disabled = browserobj.findSingleCSS(selector=CSS_PREFERENCES_DISABLED_SMS, timeout=3)
            if disabled:
                return True
    else:
        print("### Please enter a 'True' to enable SMS or a 'False' to disable SMS on the next run of the test ###")
        return False



class UserAccounts(Login):
    def __init__(self, **kwargs):
        self.params = kwargs
        #self.selenium = Login(**kwargs).login()
        Login.__init__(self, **kwargs)
        self.selenium = self.login()

    def gotoUserPage(self):
        url = urlparse(self.params["url"])
        if self.selenium:
            rcode = self.selenium.getURL(url.scheme+'://'+url.netloc+'/administration/tenantaccounts')
            waitLoadProgressDone(self.selenium)

    def gotoUserDetailPage(self, username):
        url = urlparse(self.params["url"])
        if self.selenium:
            rcode = self.selenium.getURL(url.scheme+'://'+url.netloc+'/administration/user/'+username)
            waitLoadProgressDone(self.selenium)

    def checkEntries(self):
        self.gotoUserPage()
        rcode = verifyUserAccountsEntries(self.selenium)
        return rcode

    def checkPagination(self):
        self.gotoUserPage()
        rcode = verifyUserAccountsEntries(self.selenium, 2)
        return rcode

    def checkSort(self):
        self.gotoUserPage()
        rcode = verifyUserAccountsSort(self.selenium)
        return rcode

    def toggleSMS(self, username, enable):
        self.gotoUserDetailPage(username)
        rcode = toggleSMS(self.selenium, username, enable)


    def close(self):
        if self.selenium:
            self.selenium.quit()
            

CSS_USER_PAGE = ".pageName"
CSS_USER_PROFILE = "[aria-label='User Profile'] .ng-scope" #"[category='User Profile']"
CSS_LOG_OUT = "[ng-click='ctrl.logout()']"
CSS_USERNAME_FIELD = "input[ng-model='ctrl.username']"
CSS_PASSWORD_FIELD = "input[ng-model='ctrl.password']"
CSS_LOGIN_BUTTON = "button[name='Login to application']"
CSS_GENERIC_LOGIN_BUTTON = "button.login-button"
CSS_FORGOT_PASSWORD = ".forgot-password"
CSS_FORGOT_PASSWORD_USERNAME_FIELD = ".username-input"
CSS_SEND_RESET_EMAIL = ".reset-button"
CSS_RESET_PASSWORD_FIELD = "#tooltipPassword"
CSS_SET_PASSWORD_BUTTON = ".reset-password-submit"
CSS_SET_PASSWORD_ERROR_MSG = ".reset-password-error"
CSS_LAST_FAILURE_MSG = ".timedout-body"
CSS_CONTACT_OWNER_BUTTON = 'button[name="Contact owner"]'
CSS_CONTACT_OWNER_MSG = ".notified-text"
CSS_O365_OLD_LINK = "#uxOptOutLink"
CSS_0365_USERNAME_FIELD = "input[type='email']"
CSS_0365_PASSWORD_FIELD = "[name='passwd']"
CSS_0365_NEXT_BUTTON = "[value='Next']"
CSS_0365_SIGN_IN_BUTTON = "[value='Sign in']"
CSS_0365_SIGN_IN_NO_BUTTON = "input#idBtn_Back"
CSS_0365_MAIL_BUTTON = "#ShellMail_link"
CSS_0365_OTHER_TAB = "[title='Other']"

CSS_EMAIL_COLUMN_FOR_USER = ".ui-grid-coluiGrid-000K .ui-grid-cell-contents.ng-scope"
CSS_ROLE_COLUMN_FOR_USER = ".ui-grid-coluiGrid-000L .ui-grid-cell-contents.ng-scope"
CSS_FULL_NAME_CHECKBOX_FOR_USER = ".ui-grid-cell-contents ng-md-icon"
CSS_DISABLE_ENABLE_ACCOUNT_TOP_ROW = ".selected-action-name"
CSS_ENABLE_ACCOUNT_BUTTON_NAME = ".zing-link[role='button']"
CSS_SELECT_ALL_ACCOUNTS = ".ui-grid-icon-ok.ui-grid-selection-row-header-buttons"

CSS_PREF_RESET_PASSWORD_BUTTON = "[type='button'][category='User Detail'][ng-click='udCtrl.resetButtonClick(true,$event)']"
CSS_PREF_CURR_PASSWORD_FIELD = "#new_user_oldpassword"
CSS_PREF_NEW_PASSWORD_FIELD = "#tooltipPassword"
CSS_PREF_TOGGLE_NEW_PW_VISIBILITY = ".password-strength-tooltip-container .toggle-password"
CSS_PREF_SUBMIT_BUTTON = "[name='Submit password changes made to login information']"
CSS_PREF_CANCEL_BUTTON = "[name='Cancel changes made to login information']"
CSS_PREF_PASSWORD_COMPLEXITY_MSG = ".password-strength-tooltip-container .form-error"
CSS_PREF_PASSWORD_COMPLEXITY_TOOLTIP = ".password-strength-tooltip"
CSS_PREF_PASSWORD_COMPLEXITY_TOOLTIP_ICONS = ".material-icons.status-icon"
CSS_PREF_CLOSE_BUTTON = ".md-confirm-button"
CSS_PREF_SUBMIT_ERROR = ".md-title"

CSS_USER_SETTINGS_GEAR = ".filter-bar .material-icons"
CSS_USER_SETTINGS_SUPER_GEAR = "[layout-align='space-between end'] [role='button'][title='']"
CSS_USER_SETTINGS_CURRENT_DROPDOWN_OPTION = ".menu-selection-button span.ng-binding" #"md-select-value .selected"
CSS_USER_SETTINGS_EXPIRATION_DROPDOWN_OPTION = "[role='option'][ng-repeat='item in accountExpirationConfigCtrl.idleOptions']"
CSS_USER_SETTINGS_TIMEOUT_DROPDOWN_OPTION = "[ng-repeat='item in accountExpirationConfigCtrl.idleOptions'][role='option']"
CSS_USER_SETTINGS_DROPDOWN_BUTTON = "md-input-container"
CSS_USER_SETTINGS_SAVE_BUTTON = "[name='Save config']"
CSS_USER_SETTINGS_ROW_FRAME = ".account-expiration-config [ng-if='accountExpirationConfigCtrl.showContent'] div [layout='row']"
# CSS_SUBMIT_ERROR_MESSAGE = "body > zing-reset-password > div > md-card > div.reset-password.ng-scope > div > div > div.reset-password-password-section.reset-password-wrapper > div > div"
CSS_SUBMIT_ERROR_MESSAGE =  "[ng-if='::!dialog.mdHtmlContent']"

CSS_PASSWORD_EXPIRATION_DROPDOWN_OPTIONS = "[ng-repeat='item in accountExpirationConfigCtrl.expirationOptions'] [layout='row'] .ng-binding"

CSS_IDLE_TIMEOUT_DROPDOWN_CLICK = "[ng-change='accountExpirationConfigCtrl.selectedIdleChanged()']"
CSS_IDLE_TIMEOUT_DROPDOWN_OPTIONS = ".account-expiration-config-item[ng-repeat='item in accountExpirationConfigCtrl.idleOptions']"


class PasswordandLoginEnhancements():

    def __init__(self, **kwargs):
        self.params = kwargs
        self.admin_account = kwargs["admin_account"]
        self.admin_pwd = kwargs["admin_pwd"]
        self.email_account = kwargs["emailusername"]
        self.email_pwd = kwargs["password"]
        self.mypage = Login(**self.params)


    def _get_login_status(self):

        #waitLoadProgressDone(self.selenium)

        # temporary checks REMOVE AFTER BETA
        #####################################################
        # method to click out Try Out and Welcome message box

        if not self.selenium.click(selector="[ng-click='tryitDialogCtrl.close()']", timeout=5):
            time.sleep(2)
            beta_message = "button.primary"
            self.selenium.click(selector=beta_message, timeout=5)
            rcode = self.selenium.click(selector="div.avatar[aria-haspopup='true']", timeout=2)
            if rcode:
                time.sleep(1)
                self.selenium.click(selector="[role='menuitem'][zingpwkevent='']", timeout=2)
                self._get_login_status()

        #####################################################

        # Dashboard V1 REMOVE AFTER BETA
        #####################################################################
        # dashboard v1 out of service in March
        # will keep check for dashboard V1 standalone so it is easy to remove

    def resetPassword(self):
        """ Function for testing the Reset Password feature """
        initial_password = "R3setp@ssword"   ### ~~~ CHANGE THIS IF TEST BREAKS!!! Breaks if password used recently ~~~ ###
        new_password = 'N3wp@ssword'   ### ~~~ CHANGE THIS IF TEST BREAKS!!! Breaks if password used recently ~~~ ###
        user_account = self.params["username"]
        user_password = self.params["password"]
        pwdchanges = 0
        pwdattempts = 6

        self.selenium = self.mypage.gotoLoginPage()
        self.resetInitialPassword(user_account) # Flow will reset initial password to keep true account password consistent
        self.gotoOffice365Emails()
        self.gotoPWResetLink()
        initial_password = self.setInitialPassword(initial_password) # Will loop up to 6 times (0-5) to set the initial password
        self.selenium = self.mypage.gotoLoginPage()
        self.loggingIn(user_account, initial_password)
        self.gotoPreferences()
        self.changePasswordFail(initial_password)
        curr_password = initial_password
        while pwdchanges < pwdattempts: # Will loop 6 times (0-5) to revert password
            self.changePasswordSuccess(curr_password, new_password)
            curr_password = new_password
            pwdchanges += 1
            new_password = new_password+str(pwdchanges)
        self.mypage.logout()
        self.loginAfterPasswordChange(user_account, curr_password)
        self.gotoPreferences()
        self.revertPassword(curr_password, user_password)
        self.mypage.logout()
        self.loggingIn(user_account, user_password)
        return self.mypage.logout()

    def setPasswordExpiration(self):
        """ Function for testing the Set Password Expiration feature """
        admin_account=self.admin_account
        admin_password=self.admin_pwd

        self.selenium = self.mypage.gotoLoginPage()
        self.loggingIn(admin_account, admin_password)
        self.gotoUserAccounts()
        return self.selectExpiration() and self.mypage.logout()

    def setIdleTimeout(self):
        """ Function for testing the Set Password Expiration feature """
        admin_account=self.admin_account
        admin_password=self.admin_pwd

        self.selenium = self.mypage.gotoLoginPage()
        self.loggingIn(admin_account, admin_password)
        self.gotoUserAccounts()
        return self.selectTimeout() and self.mypage.logout()

    def multipleFailedLogins(self):
        """ Function for testing the Multiple Failed Logins feature """
        user_account = self.params["username"]
        user_password = self.params["password"]

        self.selenium = self.mypage.gotoLoginPage()
        self.loginFailureSetup()
        self.failureTimes(numoftimes = 5)
        self.checkLastFailureMessage()
        self.gotoZingBox()
        self.loggingIn(user_account, user_password, expectFail=True)
        self.contactOwner()
        self.checkContactOwnerMessage()
        self.gotoZingBox()
        self.reloginAsAdmin()
        self.gotoUserAccounts()
        self.enableAccount(user_account)
        self.mypage.logout()
        #self.checkforEnabledEmail()
        self.loggingIn(user_account, user_password)
        return self.mypage.logout()

    def disableEnableAccounts(self):
        """ Function for testing the Disable Enable Accounts feature """
        admin_account = self.admin_account
        admin_password = self.admin_pwd
        user_account = self.params["username"]
        user_password = self.params["password"]

        self.selenium = self.mypage.gotoLoginPage()
        self.loggingIn(admin_account, admin_password)
        self.gotoUserAccounts()

        self.disableAccount(user_account)
        self.mypage.logout()
        self.loggingIn(user_account, user_password, expectFail=True)
        self.selenium = self.mypage.gotoLoginPage()
        self.reloginAsAdmin()
        self.gotoUserAccounts()
        self.enableAccount(user_account)
        self.mypage.logout()
        self.loggingIn(user_account, user_password)
        return self.mypage.logout()

    def canOnlyDisableOneAdmin(self):
        """ Function for testing the Disable One Admin feature """
        admin_account = self.admin_account
        admin_password = self.admin_pwd

        self.selenium = self.mypage.gotoLoginPage()
        self.loggingIn(admin_account, admin_password)
        self.gotoUserAccounts()
        self.checkDisableButton()
        return self.mypage.logout()

    # Loops through expiration settings and saves each option one by one, checks if 'optionlist' == 'options' and if equal returns true
    def selectExpiration(self, num_of_options = 4, options = ["Never", "Expire after 3 months", "Expire after 6 months", "Expire after 12 months"]):
        count = 0
        optionlist = []
        while count != num_of_options:
            time.sleep(2)

            pe_settings = self.selenium.findSingleCSS(selector=CSS_USER_SETTINGS_GEAR)

            current_option_text = self.selenium.findVisibleMultiCSS(selector=CSS_USER_SETTINGS_CURRENT_DROPDOWN_OPTION, timeout=5)
            if not pe_settings:
                print("### USER ACCOUNT SETTINGS NOT FOUND, Function 'selectExpiration' failed ###")
                return False
            if pe_settings and not current_option_text:
                pe_settings.click()
                time.sleep(0.5)

             # Will hold options text to be compared to 'options' in the end
            expiration_bar = self.selenium.findVisibleMultiCSS(selector=CSS_USER_SETTINGS_ROW_FRAME, waittype="visibility")[0]
            if self.selenium.findSingleCSS(browserobj=expiration_bar,selector=CSS_USER_SETTINGS_CURRENT_DROPDOWN_OPTION, timeout=5) == False:
                if self.selenium.findSingleCSS(browserobj=expiration_bar,selector="[ng-if='accountExpirationConfigCtrl.ssoEnabled']", timeout=5) != False:
                    print("SSO enabled for Expiration")
                    return True
                else:
                    print("Dropdown for Expiration missing")
                    return False

            if(self.selenium.findVisibleMultiCSS(selector=CSS_USER_SETTINGS_CURRENT_DROPDOWN_OPTION, timeout=5) == False):
                self.selenium.findSingleCSS(selector=CSS_USER_SETTINGS_SUPER_GEAR).click()
            current_option_text = self.selenium.findMultiCSS(selector=CSS_USER_SETTINGS_CURRENT_DROPDOWN_OPTION, timeout=5)
            if not current_option_text[0]:
                print("### CURRENT OPTION TEXT NOT FOUND, Function 'selectExpiration' failed ###")
                return False
            if current_option_text[0]:
                selected_option_text = current_option_text[0].text
                optionlist.append(selected_option_text)

            if count == 1:
                optionlist.pop(0) # Because of how the UI and my code is structured, there is a duplicate value of the first value 'Never'

            pe_dropdown = self.selenium.findMultiCSS(selector=CSS_USER_SETTINGS_DROPDOWN_BUTTON)
            if not pe_dropdown[0]:
                print("### DROPDOWN NOT FOUND, Function 'selectExpiration' failed ###")
                return False
            time.sleep(0.5)
            pe_dropdown[0].click()
            pe_dropdown_options = self.selenium.findMultiCSS(selector=CSS_PASSWORD_EXPIRATION_DROPDOWN_OPTIONS)
            if not pe_dropdown_options:
                print("### DROPDOWN OPTIONS NOT FOUND, Function 'selectExpiration' failed ###")
                return False
            time.sleep(0.5)
            pe_dropdown_options[count].click()
            
            pe_save = self.selenium.findSingleCSS(selector=CSS_USER_SETTINGS_SAVE_BUTTON, waittype="visibility", timeout=3) 
            if pe_save:
                time.sleep(0.5)
                pe_save.click()
                count += 1
                if count == num_of_options: # if count is equal to the number of dropdown options, then return to the first option setting
                    time.sleep(1)
                    pe_settings.click()
                    current_option_text = self.selenium.findVisibleMultiCSS(selector=CSS_USER_SETTINGS_CURRENT_DROPDOWN_OPTION)
                    selected_option_text = current_option_text[0].text
                    print(selected_option_text)
                    print(count)
                    optionlist.append(selected_option_text)
                    pe_dropdown = self.selenium.findMultiCSS(selector=CSS_USER_SETTINGS_DROPDOWN_BUTTON) 
                    time.sleep(0.5)
                    pe_dropdown[0].click()
                    pe_dropdown_options = self.selenium.findMultiCSS(selector=CSS_PASSWORD_EXPIRATION_DROPDOWN_OPTIONS)
                    pe_dropdown_options[0].click()
                    pe_save = self.selenium.findSingleCSS(selector=CSS_USER_SETTINGS_SAVE_BUTTON, waittype="visibility", timeout=3)
                    time.sleep(0.5)
                    pe_save.click()
                    if optionlist != options:

                        print("### OPTION LIST IS NOT EQUAL TO OPTIONS, Function 'selectExpiration' failed ###")
                        print(optionlist)
                        print(options)
                        return False
                    if optionlist == options:

                        return True
                    
                    print("### DROPDOWN OR DROPDOWN CSS NOT FOUND, Function 'selectExpiration' failed ###")
                    return False
                continue

            time.sleep(0.5)
            count += 1

        print("### Function 'selectExpiration' failed ###")
        return False

    # Almost the same as selectExpiration and shares the same CSS
    def selectTimeout(self, num_of_options = 6, options = ["Never", "5 mins", "15 mins", "30 mins", "1 hour", "2 hours"]):
        count = 0
        optionlist = [] # Will hold options text to be compared to 'options' in the end

        while count != num_of_options:
            time.sleep(2)
            it_settings = self.selenium.findSingleCSS(selector=CSS_USER_SETTINGS_GEAR)
            current_option_text = self.selenium.findVisibleMultiCSS(selector=CSS_USER_SETTINGS_CURRENT_DROPDOWN_OPTION, timeout=5, waittype="visibility")
            if not it_settings:
                print("### USER ACCOUNT SETTINGS NOT FOUND, Function 'selectTimeout' failed ###")
                return False
            if it_settings and not current_option_text:
                it_settings.click()
                time.sleep(1)
                current_option_text = self.selenium.findVisibleMultiCSS(selector=CSS_USER_SETTINGS_CURRENT_DROPDOWN_OPTION, timeout=5, waittype="visibility")

            timeout_bar = self.selenium.findVisibleMultiCSS(selector=CSS_USER_SETTINGS_ROW_FRAME, waittype="visibility")[2]
            if self.selenium.findSingleCSS(browserobj=timeout_bar,selector=CSS_USER_SETTINGS_CURRENT_DROPDOWN_OPTION, timeout=5, waittype="visibility") == False:
                if self.selenium.findSingleCSS(browserobj=timeout_bar,selector="[ng-if='accountExpirationConfigCtrl.ssoEnabled']", timeout=5) != False:
                    print("SSO enabled for Timeout")
                    return True
                else:
                    print("Dropdown for Timeout missing")
                    return False

            if not current_option_text[-1]:
                print("### CURRENT OPTION TEXT NOT FOUND, Function 'selectTimeout' failed ###")
                return False
            if current_option_text[-1]:
                selected_option_text = current_option_text[-1].text
                optionlist.append(selected_option_text)

            if count == 1:
                optionlist.pop(0) # Because of how the UI and my code is structured, there is a duplicate value of the first value 'Never'

            it_dropdown = self.selenium.findMultiCSS(selector=CSS_IDLE_TIMEOUT_DROPDOWN_CLICK, waittype="visibility")
            for it in it_dropdown:
                if(it.is_displayed() == False):
                    it_dropdown.remove(it)
            if not it_dropdown[0]:
                print("### DROPDOWN NOT FOUND, Function 'selectTimeout' failed ###")
                return False
            time.sleep(0.5)
            it_dropdown[0].click()

            it_dropdown_options = self.selenium.findMultiCSS(selector=CSS_IDLE_TIMEOUT_DROPDOWN_OPTIONS)
            if not it_dropdown_options:
                print("### DROPDOWN OPTIONS NOT FOUND, Function 'selectTimeout' failed ###")
                return False
            time.sleep(2)
            it_dropdown_options[count].click()

            time.sleep(1)
            
            it_save = self.selenium.findSingleCSS(selector=CSS_USER_SETTINGS_SAVE_BUTTON, waittype="visibility", timeout=3) 
            if it_save:
                time.sleep(0.5)
                it_save.click()
                count += 1
                if count == num_of_options: # if count is equal to the number of dropdown options, then return to the first option setting
                    time.sleep(1)
                    it_settings.click()
                    current_option_text = self.selenium.findVisibleMultiCSS(selector=CSS_USER_SETTINGS_CURRENT_DROPDOWN_OPTION)
                    selected_option_text = current_option_text[-1].text
                    optionlist.append(selected_option_text)
                    it_dropdown = self.selenium.findMultiCSS(selector=CSS_IDLE_TIMEOUT_DROPDOWN_CLICK) 
                    time.sleep(0.5)
                    it_dropdown[0].click()
                    it_dropdown_options = self.selenium.findMultiCSS(selector=CSS_IDLE_TIMEOUT_DROPDOWN_OPTIONS)

                    it_dropdown_options[0].click()
                    it_save = self.selenium.findSingleCSS(selector=CSS_USER_SETTINGS_SAVE_BUTTON, waittype="visibility", timeout=3)
                    time.sleep(0.5)
                    it_save.click()
                    for op in optionlist:
                        op = op.strip("Idle Timeout\nIdle Timeout\n")
                    if optionlist != options:
                        print("### OPTION LIST IS NOT EQUAL TO OPTIONS, Function 'selectTimeout' failed ###")
                        print(("Options: {0}".format(options) ))
                        print(("Options List: {0}".format(optionlist)))
                        return False
                    if optionlist == options:
                        return True
                    print("### DROPDOWN OR DROPDOWN CSS NOT FOUND, Function 'selectTimeout' failed ###")
                    return False
                continue

            time.sleep(0.5)
            count += 1

        print("### Function 'selectTimeout' failed ###")
        return False

    def loggingIn(self, user, password, expectFail=False): # Use default login information specified by the "test_FILE"
        url = urlparse(self.params["url"])
        if self.selenium:
            rcode = self.selenium.getURL(defaultEnv()["uiportal"] )
            waitLoadProgressDone(self.selenium)
        self.selenium.sendKeys(selector=CSS_USERNAME_FIELD, text=user)
        try:
            self.params["selector"] = CSS_NEXT_BUTTON
            self.params["timeout"] = 8
            self.selenium.click(**self.params)
        except:
            pass

        # rcode = self.selenium.sendKeys(selector=CSS_USERNAME_FIELD, text=user)

        # if rcode:
        rcode = self.selenium.sendKeys(selector=CSS_PASSWORD_FIELD, text=password)

        if rcode:
            rcode = self.selenium.click(selector=CSS_LOGIN_BUTTON, timeout=3)
            waitLoadProgressDone(self.selenium)

        if rcode:
            # if logged in correctly, check to make sure that it does not see the generic login button anymore
            rcode = True if not self.selenium.findSingleCSS(selector=CSS_GENERIC_LOGIN_BUTTON, timeout=3) else False
                    # temporary checks REMOVE AFTER BETA
        #####################################################
        # method to click out Try Out and Welcome message box

            self._get_login_status()

        if rcode or expectFail:
            return True

        print("### Function 'loggingIn' failed ###")
        return False

    def loginFailureSetup(self): # Enters in login info
        self.params["selector"] = CSS_USERNAME_FIELD
        self.params["text"] = self.params["username"]
        rcode = self.selenium.sendKeys(**self.params)
        try:
            self.params["selector"] = CSS_NEXT_BUTTON
            self.params["timeout"] = 8
            self.selenium.click(**self.params)
        except:
            pass
        if rcode:
            self.params["selector"] = CSS_PASSWORD_FIELD
            self.params["text"] = 'failpassword'
            rcode = self.selenium.sendKeys(**self.params)

        if rcode:
            return True
        print("### Function 'loginFailureSetup' failed ###")
        return False

    def failureTimes(self, numoftimes): # Input the amount of times you want to fail
        rcode = self.selenium
        times = 0
        while (times < numoftimes):
            if self.selenium.findSingleCSS(selector=CSS_LOGIN_BUTTON, timeout=3):
                rcode = self.selenium.click(selector=CSS_LOGIN_BUTTON)
                time.sleep(0.5)
            else:
                # check if the first few login get lockout failure message, then user probably is already locked out.  Can skip this function
                if self.checkLastFailureMessage() and times < numoftimes:
                    break

            times = times + 1

        if rcode:
            return True
        print("### Function 'failureTimes' failed ###")
        return False

    def checkLastFailureMessage(self): # Checks for the "Account Disabled" message
        rcode = self.selenium.findSingleCSS(selector=CSS_LAST_FAILURE_MSG) # get an object to use '.text'
        rcode = rcode.text
        
        if "Your account is disabled" in rcode:
            return True
        print("### Function 'checkLastFailureMessage' failed ###")
        return False

    def contactOwner(self): # Clicks on the Contact Owner button after 5 failures
        if self.selenium:
            rcode = self.selenium.click(selector=CSS_CONTACT_OWNER_BUTTON)
            waitLoadProgressDone(self.selenium)

        if rcode:
            return True
        print("### Function 'contactOwner' failed ###")
        return False

    def checkContactOwnerMessage(self): # Checks for the message that appears after the Contact Owner button is clicked
        rcode = self.selenium.findSingleCSS(selector=CSS_CONTACT_OWNER_MSG) # get an object to use '.text'
        rcode = rcode.text

        if "Your request has been received" in rcode:
            return True
        print("### Function 'checkLastFailureMessage' failed ###")
        return False

    def gotoZingBox(self): # Goes to the ZingBox home page
        rcode = self.selenium.getURL(self.params["url"])
        waitLoadProgressDone(self.selenium)

        if rcode:
            return True
        print("### Function 'gotoZingBox' failed ###")
        return False

    def gotoPreferences(self): # Goes to the Preferences page for the user
        url = urlparse(self.params["url"])
        if self.selenium:
            rcode = self.selenium.getURL(url.scheme+'://'+url.netloc+'/administration/preference/'+self.params["username"])
            waitLoadProgressDone(self.selenium)

        if rcode:
            return True
        print("### Function 'gotoPreferences' failed ###")
        return False

    def gotoUserAccounts(self): # Goes to the account page listing all users
        url = urlparse(self.params["url"])
        if self.selenium:
            rcode = self.selenium.getURL(url.scheme+'://'+url.netloc+'/administration/tenantaccounts')
            waitLoadProgressDone(self.selenium)

        if rcode:
            return True
        print("### Function 'gotoUserAccounts' failed ###")
        return False

    def reloginAsAdmin(self): # Login as the Administrator
        url = urlparse(self.params["url"])
        if self.selenium:
            rcode = self.selenium.getURL(url.scheme+'://'+url.netloc+'/login')
            waitLoadProgressDone(self.selenium)
        rcode = self.selenium.sendKeys(selector=CSS_USERNAME_FIELD, text=self.admin_account)
        try:
            self.params["selector"] = CSS_NEXT_BUTTON
            self.params["timeout"] = 8
            self.selenium.click(**self.params)
        except:
            pass
        if rcode:
            rcode = self.selenium.sendKeys(selector=CSS_PASSWORD_FIELD, text=self.admin_pwd)

        if rcode:
            rcode = self.selenium.click(selector=CSS_LOGIN_BUTTON)
            waitLoadProgressDone(self.selenium)

        if rcode:
            return True
        print("### Function 'reloginAsAdmin' failed ###")
        return False

    def disableAccount(self, account):
        self.selenium.click(selector=CSS_PAGE_SIZE)
        time.sleep(1)
        meme = self.selenium.findSingleVisibleCSS(selector=CSS_PAGE_MAX)
        meme.click()


        count = 0
        if self.selenium:
            rcode = self.selenium.findMultiCSS(selector=CSS_EMAIL_COLUMN_FOR_USER)
            for email in rcode:
                if email.text == account:
                    break
                count += 1
        
        if rcode:
            rcode = self.selenium.findMultiCSS(selector=CSS_FULL_NAME_CHECKBOX_FOR_USER)
            rcode[count].click()

        if rcode:    
            rcode = self.selenium.findMultiCSS(selector=CSS_DISABLE_ENABLE_ACCOUNT_TOP_ROW)

        if "Enable" in rcode[2].text:
            rcode = rcode[2].click() # If already disabled account, click enable button in blue bar

        if "Disable" in rcode[1].text:
            rcode = rcode[1].click() # If default enabled account, click disable button in blue bar
            return True
        print("### Function 'disableAccount' failed ###")
        return False

    def enableAccount(self, account): # Enables the user account
        self.selenium.click(selector=CSS_PAGE_SIZE, timeout=5)
        time.sleep(1)
        self.selenium.click(selector=CSS_PAGE_MAX, timeout=3)
        
        count = 0
        if self.selenium:
            rcode = self.selenium.findMultiCSS(selector=CSS_EMAIL_COLUMN_FOR_USER, timeout = 3)
            for email in rcode:
                if email.text == account:
                    break
                count += 1
        
        if rcode:
            rcode = self.selenium.findMultiCSS(selector=CSS_FULL_NAME_CHECKBOX_FOR_USER)
            rcode[count].click()

        if rcode:    
            rcode = self.selenium.findMultiCSS(selector=CSS_DISABLE_ENABLE_ACCOUNT_TOP_ROW)

        if "Enable" in rcode[2].text:
            rcode = self.selenium.click(selector=CSS_ENABLE_ACCOUNT_BUTTON_NAME) # Enable using link
            return True
        print("### Function 'enableAccount' failed ###")
        return False

    def checkDisableButton(self):
        countowner = 0
        countadmin = 0
        
        if self.selenium:
            allaccounts = self.selenium.findSingleCSS(selector=CSS_SELECT_ALL_ACCOUNTS)

        allaccounts.click()

        button = self.selenium.findMultiCSS(selector=CSS_DISABLE_ENABLE_ACCOUNT_TOP_ROW)

        if not button[1].text: # Check for empty text, no "Disable"
            roles = self.selenium.findMultiCSS(selector=CSS_ROLE_COLUMN_FOR_USER)
            for role in roles:
                if role.text == "Owner":
                    break
                countowner += 1
            for role in roles:
                if role.text == "Administrator":
                    break
                countadmin += 1

        if button[1].text:
            print("### Function 'checkDisableButton' failed, selecting all accounts should not find disable button ###")
            return False

        allaccounts.click()

        checkbox = self.selenium.findMultiCSS(selector=CSS_FULL_NAME_CHECKBOX_FOR_USER)

        checkbox[countowner].click()
        button = self.selenium.findMultiCSS(selector=CSS_DISABLE_ENABLE_ACCOUNT_TOP_ROW)
        if button[1].text:
            print("### Function 'checkDisableButton' failed, selecting an owner account should not find a disable button ###")
            return False
        checkbox[countowner].click()

        checkbox[countadmin].click()
        button = self.selenium.findMultiCSS(selector=CSS_DISABLE_ENABLE_ACCOUNT_TOP_ROW)
        if not button[1].text:
            print("### Function 'checkDisableButton' failed, selecting an administrator account should find a disable button ###")
            return False
        
        checkbox[countadmin+1].click()

        button = self.selenium.findMultiCSS(selector=CSS_DISABLE_ENABLE_ACCOUNT_TOP_ROW)
        if not button[1].text:
            return True
        print("### Function 'checkDisableButton' failed, selecting more than one account should not find the disable button ###")
        return False

    def resetInitialPassword(self, user):
        self.selenium.sendKeys(selector=CSS_USERNAME_FIELD, text=user)
        self.selenium.click(selector=CSS_NEXT_BUTTON)

        if self.selenium:
            self.selenium.click(selector=CSS_FORGOT_PASSWORD)

        self.selenium.sendKeys(selector=CSS_FORGOT_PASSWORD_USERNAME_FIELD, text=user)
        rcode = self.selenium.click(selector=CSS_SEND_RESET_EMAIL)

        if rcode:
            return True
        print("### Function 'resetInitialPassword' failed ###")
        return False

    def setInitialPassword(self, password): # Loops up to 6 times to make sure that the intial password can be set
        for i in range(0,12):
            try:
                if self.selenium:
                    reset_pw_field = self.selenium.findSingleCSS(selector=CSS_RESET_PASSWORD_FIELD)
                    reset_pw_field.click()
                    reset_pw_field.clear()
                    self.selenium.sendKeys(selector=CSS_RESET_PASSWORD_FIELD, text=password)
                rcode = self.selenium.click(selector=CSS_SET_PASSWORD_BUTTON)
                
                rcode_err = self.selenium.findSingleCSS(selector=CSS_SET_PASSWORD_ERROR_MSG, waittype='visibility', timeout=3)
                if rcode_err is False:
                    break
                if rcode_err is not False and "error" in rcode_err.text.lower():
                    password = password + str(i)
            except:
                raise Exception("Could not set the initial password after " + str(i) + " tries. Will fail test to save time.")
        return password

    def gotoOffice365Emails(self):
        url = urlparse(self.params["url"])
        if self.selenium:
            self.selenium.getURL(url.scheme+'://login.microsoftonline.com')
            waitLoadProgressDone(self.selenium)
        
        self.selenium.sendKeys(selector=CSS_0365_USERNAME_FIELD, text=self.email_account)
        self.selenium.click(selector=CSS_0365_NEXT_BUTTON)
        self.selenium.sendKeys(selector=CSS_0365_PASSWORD_FIELD, text=self.email_pwd)
        self.selenium.click(selector=CSS_0365_SIGN_IN_BUTTON)
        self.selenium.click(selector=CSS_0365_SIGN_IN_NO_BUTTON)
        waitLoadProgressDone(self.selenium)
        self.selenium.click(selector=CSS_0365_MAIL_BUTTON)
        waitLoadProgressDone(self.selenium)
        
        #switchToLatestWindow() does not have a return, so rcode will always be None
        #selenium switch_to_window() also does not have a return so not possible to check if it succeed
        self.selenium.switchToLatestWindow()
        waitLoadProgressDone(self.selenium)

        # if rcode:
        #     return True
        # print("### Function 'gotoOffice365Emails' failed ###")
        # return False
        return True

    def gotoPWResetLink(self): # Goes to the reset password link from the reset password email
        email_client = Email_Client('outlook.office365.com', self.email_account, self.email_pwd)
        emails = email_client.getEmails(search_key='Recent')
        for email in emails:
            _is_from_zingbox = 'no-reply@zingbox.com' in email['from']#email.getSenderEmail()
            if not _is_from_zingbox:
                raise Exception("Could not find email 'no-reply@zingbox.com' from ZingBox as a sender")
            _is_pwreset_email = 'Password Reset Request' in email['subject'] #.getSubject()
            if not _is_pwreset_email:
                raise Exception("Could not find subject title 'Password Reset Request' from ZingBox's password reset email")
            if _is_from_zingbox and _is_pwreset_email:
                email_body = email['body'] #.getBody()
                m = re.search(r'http(\S*)resetpwd(\S*)\"', email_body)
                if m is not None:
                    link = HTMLParser().unescape(m.group(0)[:-1])
                    environment = os.environ["NODE_ENV"]
                    if 'testing' in environment:
                        link = link.replace('zb-accounts', 'testing')
                        link = link.replace('/reset', '/#reset')
                    elif 'staging' in environment:
                        link = link.replace('zb-accounts', 'staging')
                        link = link.replace('/reset', '/#reset')
                    elif 'production' in environment:
                        link = link.replace('zb-accounts', 'production-candidate')
                        link = link.replace('/reset', '/#reset')
                    self.selenium.getURL(link)
                    return True

        print("### Function 'gotoPWResetLink' failed ###")
        return False

    def checkforEnabledEmail(self): # Checks for the enabled email, not through the UI
        email_client = Email_Client('outlook.office365.com', self.email_account, self.email_pwd)
        emails = email_client.getEmails()
        for email in emails:
            _is_from_zingbox = 'no-reply@zingbox.com'.lower() in email['from'].lower() #.getSenderEmail()
            _is_unlocked_email = 'ZingBox Account Unlocked Notification'.lower() in email['subject'].lower() #.getSubject()
            if _is_from_zingbox and _is_unlocked_email:
                return True

        print("### Function 'checkforEnabledEmail' failed ###")
        return False

    def changePasswordFail(self, password): # Sets a password that is less than the minimum length, fails
        textlist = []

        if self.selenium:
            rcode = self.selenium.click(selector=CSS_PREF_RESET_PASSWORD_BUTTON)

        if rcode:
            rcode = self.selenium.click(selector=CSS_PREF_TOGGLE_NEW_PW_VISIBILITY)

        if rcode:
            rcode = self.selenium.findSingleCSS(selector=CSS_PREF_PASSWORD_COMPLEXITY_TOOLTIP) # get an object to use '.text'
            tooltip_lines = rcode.text
            
            firstline = re.search(r'protect your account', tooltip_lines)
            secondline = re.search(r'8 characters', tooltip_lines)
            thirdline = re.search(r'lowercase letter', tooltip_lines)
            fourthline = re.search(r'uppercase letter', tooltip_lines)
            fifthline = re.search(r'number', tooltip_lines)
            sixthline = re.search(r'special character', tooltip_lines)
            seventhline = re.search(r'your name or email address', tooltip_lines)

            if (firstline or secondline or thirdline or fourthline or fifthline or sixthline or seventhline) is None:
                print("At least one of the tooltip lines cannot be found")
                return False

        if rcode:
            rcode = self.selenium.sendKeys(selector=CSS_PREF_CURR_PASSWORD_FIELD, text=password)

        if rcode:
            pwdfield = self.selenium.findSingleCSS(selector=CSS_PREF_NEW_PASSWORD_FIELD)
            # Enter in a password that doesn't satisfy all conditions, "badpassword"
            rcode = self.selenium.sendKeys(selector=CSS_PREF_NEW_PASSWORD_FIELD, text="badpassword")
            rcode = self.selenium.findMultiCSS(selector=CSS_PREF_PASSWORD_COMPLEXITY_TOOLTIP_ICONS)
            for icons in rcode:
                textlist.append(icons.text) # appends the icon text to the list
            if "close" not in textlist:
                print("This password should not pass all conditions")
                return False
            textlist[:] = [] # empties the list

        if rcode:
            rcode = self.selenium.click(selector=CSS_PREF_SUBMIT_BUTTON)
            
        if rcode:
            rcode = pwdfield.clear()
            pwdfield = self.selenium.findSingleCSS(selector=CSS_PREF_NEW_PASSWORD_FIELD)
            # Enter in a password that doesn't satisfy the name or email address , "...qatest1"
            rcode = self.selenium.sendKeys(selector=CSS_PREF_NEW_PASSWORD_FIELD, text="N3w!passqatest1")
            rcode = self.selenium.findMultiCSS(selector=CSS_PREF_PASSWORD_COMPLEXITY_TOOLTIP_ICONS)
            for icons in rcode:
                textlist.append(icons.text) # appends the icon text to the list
            if "close" not in textlist:
                print("This password should not pass all conditions")
                return False

        if rcode:
            rcode = self.selenium.click(selector=CSS_PREF_SUBMIT_BUTTON) # Should not be able to accept the password
            waitLoadProgressDone(self.selenium)

        if rcode:
            rcode = self.selenium.findSingleCSS(selector=CSS_PREF_PASSWORD_COMPLEXITY_MSG)
            rcode = rcode.text
            if "Your password must meet the complexity requirements" not in rcode:
                return False

        if rcode:
            rcode = self.selenium.click(selector=CSS_PREF_CANCEL_BUTTON)
            
        if rcode:
            return True

    def changePasswordSuccess(self, curr_password, new_password): # Sets a password that meets the minimum requirements, succeeds
        textlist = []
        if self.selenium: # These rcodes have been checked for visibility in changePasswordFail
            rcode = self.selenium.click(selector=CSS_PREF_RESET_PASSWORD_BUTTON)
            rcode = self.selenium.findSingleCSS(selector=CSS_PREF_CURR_PASSWORD_FIELD)
            rcode = rcode.clear()
            rcode = self.selenium.findSingleCSS(selector=CSS_PREF_NEW_PASSWORD_FIELD)
            rcode = rcode.clear()
            rcode = self.selenium.sendKeys(selector=CSS_PREF_CURR_PASSWORD_FIELD, text=curr_password)
            rcode = self.selenium.sendKeys(selector=CSS_PREF_NEW_PASSWORD_FIELD, text=new_password)
            rcode = self.selenium.findMultiCSS(selector=CSS_PREF_PASSWORD_COMPLEXITY_TOOLTIP_ICONS)
            for icons in rcode:
                textlist.append(icons.text)
                if "close" in textlist:
                    print("This password should pass all conditions")
                    return False

        if rcode:
            rcode = self.selenium.click(selector=CSS_PREF_SUBMIT_BUTTON)

        rcode_err = self.selenium.findSingleCSS(selector=CSS_PREF_SUBMIT_ERROR, waittype='visibility', timeout=3)
        if rcode_err is not False and "error" in rcode_err.text.lower():
            temp = self.selenium.findSingleCSS(selector=CSS_SUBMIT_ERROR_MESSAGE)
            if "same as current one" in temp.text:
                self.changePasswordSuccess(new_password, curr_password)
            else:
                raise Exception("A submit error message occured, will fail test to prevent looping this function 5 more times to save time")

        if rcode:
            rcode = self.selenium.click(selector=CSS_PREF_CLOSE_BUTTON)

        if rcode:
            return True
        print("### Function 'changePasswordSuccess' failed ###")
        return False

    def loginAfterPasswordChange(self, user, password): # Login to the user's account after the password change
        rcode = self.selenium.sendKeys(selector=CSS_USERNAME_FIELD, text=user)

        if rcode:
            rcode = self.selenium.sendKeys(selector=CSS_PASSWORD_FIELD, text=password)

        if rcode:
            rcode = self.selenium.click(selector=CSS_LOGIN_BUTTON)
            waitLoadProgressDone(self.selenium)

        if rcode:
            return True
        print("### Function 'loginAfterPasswordChange' failed ###")
        return False

    def revertPassword(self, new_password, old_password): # Changes the password back to the user's original password
        if self.selenium:
            rcode = self.selenium.click(selector=CSS_PREF_RESET_PASSWORD_BUTTON)

        if rcode:
            rcode = self.selenium.sendKeys(selector=CSS_PREF_CURR_PASSWORD_FIELD, text=new_password)

        if rcode:
            rcode = self.selenium.sendKeys(selector=CSS_PREF_NEW_PASSWORD_FIELD, text=old_password)

        if rcode:
            rcode = self.selenium.click(selector=CSS_PREF_TOGGLE_NEW_PW_VISIBILITY)

        if rcode:
            rcode = self.selenium.click(selector=CSS_PREF_SUBMIT_BUTTON)

        if rcode:
            rcode = self.selenium.click(selector=CSS_PREF_CLOSE_BUTTON)

        if rcode:
            return True
        print("### Function 'revertPassword' failed ###")
        return False

    def close(self):
        if self.selenium:
            self.selenium.quit()
