#!/usr/bin/python

import operator
import random
import os
import re
import sys
if sys.version_info >= (3, 0):
    from html.parser import HTMLParser
else:
    from html.parser import HTMLParser
import pdb
import time
from urllib.parse import urlparse
from datetime import datetime

from selenium.webdriver.common.keys import Keys

from ui.login.zbUILoginCore import Login
from ui.zbUIShared import *
from common.zbCommon import validateDataNotEmpty
from common.zbEmail import Email_Client
from zing_cloud import user

CSS_USER_ACCOUNT_CHECK_BOX = '.zingTable div.ui-grid-pinned-container .ui-grid-row .ui-grid-cell-contents ng-md-icon'
CSS_USER_ACCOUNT_EMAIL_LINK = '.zingTable div.ui-grid-row .ui-grid-cell-contents a'
CSS_USER_ACCOUNT_ROLE = '.zingTable div.ui-grid-row .ui-grid-coluiGrid-000C .ui-grid-cell-contents'
CSS_USER_ACCOUNT_ADD_USER = '.zingTable div.filter-bar ng-md-icon[tooltip-text=\'Create new\']'
CSS_USER_ACCOUNT_DELETE_USER_BTN = '.zingTable div.selection-bar i'
CSS_USER_ACCOUNT_ADD_USER_INPUT = 'div.new-user-page md-input-container input'
CSS_USER_ACCOUNT_ADD_USER_READ_ONLY_RADIO_BTN = 'div.new-user-page md-radio-button[name=\'Read only\']'
CSS_USER_ACCOUNT_ADD_USER_INVITE_BTN = 'div.new-user-page button[name=\'Invite User\']'

CSS_USER_REGISTRATION_GO_TO_REG_PAGE_BTN = 'div.onboarding-content a.zing-button'
CSS_USER_REGISTRATION_FIRST_NAME_INPUT = '.onboarding-content form input#firstname'
CSS_USER_REGISTRATION_LAST_NAME_INPUT = '.onboarding-content form input#lastname'
CSS_USER_REGISTRATION_PHONE_INPUT = '.onboarding-content form input#phone'
CSS_USER_REGISTRATION_PWD_INPUT = '.onboarding-content form input#password'
CSS_USER_REGISTRATION_TERMS_CHECKBOX = '.onboarding-content form md-checkbox div.md-container'
CSS_USER_REGISTRATION_REGISTER_BTN = '.onboarding-content form button'

CSS_USER_TABLE_SEARCH_BTN = '.zingTable .filter-bar [icon=\'search\'][name=\'search_toggle\']'
CSS_USER_TABLE_SEARCH_INPUT = '.zingTable .filter-bar input#table-search'

CSS_MSSP_RESELLERS_BTN = 'zing-menu-toggle [name=\'resellers\'] button'
CSS_MSSP_ADD_RESELLER_BTN = 'zing-portal-reseller .portal-reseller .filter-bar ng-md-icon[tooltip-text=\'Create new\']'
CSS_MSSP_ADD_RESELLER_NAME_INPUT = '.new-reseller-page md-input-container input[name=\'username\']'
CSS_MSSP_ADD_RESELLER_EMAIL_INPUT = '.new-reseller-page md-input-container input[name=\'useremail\']'
CSS_MSSP_ADD_RESELLER_INVITE_BTN = '.new-reseller-page button[name=\'Add reseller\']'

CSS_MSSP_CUSTOMERS_BTN = 'zing-menu-toggle [name=\'customers\'] button'
CSS_MSSP_ADD_CUSTOMER_BTN = 'zing-portal-mssp-dashboard .filter-bar ng-md-icon[tooltip-text=\'Create new\']'
CSS_MSSP_NEW_CUSTOMER_RESELLER_DROPDOWN = '.onboarding-page .request-tryout md-input-container md-select#reseller'
CSS_MSSP_NEW_CUSTOMER_RESELLER_OPTION = 'md-select-menu md-option[name=\'Picked {}\']'
CSS_MSSP_ADD_CUSTOMER_FIRST_NAME_INPUT = '.onboarding-content input#firstname'
CSS_MSSP_ADD_CUSTOMER_LAST_NAME_INPUT = '.onboarding-content input#lastname'
CSS_MSSP_ADD_CUSTOMER_PHONE_INPUT = '.onboarding-content input#phone'
CSS_MSSP_ADD_CUSTOMER_EMAIL_INPUT = '.onboarding-content input#username'
CSS_MSSP_ADD_CUSTOMER_COMPANY_INPUT = '.onboarding-content input#organization'
CSS_MSSP_ADD_CUSTOMER_INDUSTRY_DROPDOWN = '.onboarding-content .request-tryout md-input-container md-select#industry'
CSS_MSSP_ADD_CUSTOMER_INDUSTRY_OPTION = 'md-select-menu md-option[name=\'Picked Healthcare\']'
CSS_MSSP_ADD_CUSTOMER_INVITE_BTN = '.onboarding-content .request-tryout button'
CSS_MSSP_SEARCH_CUSTOMER_BTN = 'zing-portal-mssp-dashboard .portal-mssp-dashboard .filter-bar ng-md-icon[name=\'search_toggle\'][icon=\'search\']'
CSS_MSSP_SEARCH_CUSTOMER_INPUT = 'zing-portal-mssp-dashboard .portal-mssp-dashboard .filter-bar input#table-search'
CSS_MSSP_SEARCH_RESELLER_BTN = 'zing-portal-reseller .filter-bar [name=\'search_toggle\'][icon=\'search\']'
CSS_MSSP_SEARCH_RESELLER_INPUT = 'zing-portal-reseller .filter-bar input#table-search'
CSS_MSSP_CUSTOMERS_ROWS = 'zing-portal-mssp-dashboard .portal-mssp-dashboard .ui-grid-row'

CSS_MSSP_RESELLERS_NAME_LINK = 'zing-portal-reseller .portal-reseller .ui-grid-row a'

CSS_USER_REGISTRATION_GO_TO_REG_PAGE_BTN = 'div.onboarding-content a.zing-button'
CSS_USER_REGISTRATION_FIRST_NAME_INPUT = '.onboarding-content form input#firstname'
CSS_USER_REGISTRATION_LAST_NAME_INPUT = '.onboarding-content form input#lastname'
CSS_USER_REGISTRATION_PHONE_INPUT = '.onboarding-content form input#phone'
CSS_USER_REGISTRATION_PWD_INPUT = '.onboarding-content form input#password'
CSS_USER_REGISTRATION_TERMS_CHECKBOX = '.onboarding-content form md-checkbox div.md-container'
CSS_USER_REGISTRATION_REGISTER_BTN = '.onboarding-content form button'

CSS_CUSTOMERS_ADMIN_PANEL_LOGIN_EMAIL_INPUT = 'form.login-form input#input_0'
CSS_CUSTOMERS_ADMIN_PANEL_LOGIN_PWD_INPUT = 'form.login-form input#input_1'
CSS_CUSTOMERS_ADMIN_PANEL_LOGIN_BTN = 'form.login-form button.login-button'
CSS_CUSTOMERS_ADMIN_PANEL_APPROVE_BTN = 'button[aria-label=\'Approve\']'
CSS_CUSTOMERS_ADMIN_PANEL_PROVISION_BTN = 'button[aria-label=\'Provision\']'
CSS_CUSTOMERS_ADMIN_PANEL_SEND_EMAIL_BTN = 'button[aria-label=\'Send Email\']'
CSS_CUSTOMERS_ADMIN_PANEL_CUSTOMER_PANEL = '[role=\'grid\']:nth-child(2)'
CSS_CUSTOMERS_ADMIN_PANEL_ROWS = 'div.ui-grid-viewport .ui-grid-row'
CSS_CUSTOMERS_ADMIN_PANEL_EMAIL = '.ui-grid-coluiGrid-000E div.text-lowercase'
CSS_CUSTOMERS_ADMIN_PANEL_TENANTID_INPUT = 'div.editable input'

CSS_FORGET_PWD_BUTTON = '.login-form a.forgot-password'
CSS_FORGET_PWD_EMAIL_IMPUT = '.forgot-password-form .username-input'
CSS_FORGET_PWD_RESET_BUTTON = '.forgot-password-form button.reset-button'

CSS_RESET_PWD_PWD_INPUT = 'input#reset-password-input'
CSS_RESET_PWD_CONFIRM_PWD_INPUT = 'input.reset-password-input-confirm'
CSS_RESET_PWD_BUTTON = 'button.reset-password-submit'

CSS_LOGIN_USERNAME_FIELD = "input[ng-model='ctrl.username']"
CSS_LOGIN_PASSWORD_FIELD = "input[ng-model='ctrl.password']"
CSS_LOGIN_BUTTON = "button > span.ng-scope"
CSS_NAVBAR_USERNAME = 'span.username'
CSS_USER_BUTTON = 'zing-user-card button'
CSS_LOGOUT_BUTTON = 'button[category="Log out"]'

def _deleteTargetReseller(email):
    user.delete_user([email])
    user.delete_tenant([email])
    user.delete_trial_user([email])
    user.delete_reseller([email])

def _deleteTargetCustomer(email):
    user.delete_user([email])
    user.delete_tenant([email])
    user.delete_trial_user([email])
    user.delete_reseller([email])

def registerNewReseller(browserobj, **kwargs):
    rcode = True
    email = kwargs['user_onboard_email']
    o365_email = kwargs['o365_email']
    pwd = kwargs['o365_pwd']
    user_name = kwargs['user_name']
    user_pwd = kwargs['user_pwd']
    phone = kwargs['phone']
    _inviteNewReseller(browserobj, user_name, email)
    rcode = rcode and _openResellerInvitationLink(browserobj, o365_email, pwd)
    rcode = rcode and _fillInResellerRegistrationForm(browserobj, phone, user_pwd)
    time.sleep(3)
    return rcode

def registerNewCustomer(browserobj, **kwargs):
    email = kwargs['user_onboard_email']
    phone = kwargs['phone']
    company_name = kwargs['company_name']
    reseller_name = kwargs['reseller_name']
    _inviteNewCustomer(browserobj, reseller_name, email, phone, company_name)

def _inviteNewReseller(browserobj, user_name, email):
    browserobj.click(selector=CSS_MSSP_ADD_RESELLER_BTN)
    time.sleep(1)
    _fillIn(browserobj, CSS_MSSP_ADD_RESELLER_NAME_INPUT, user_name)
    _fillIn(browserobj, CSS_MSSP_ADD_RESELLER_EMAIL_INPUT, email)
    browserobj.click(selector=CSS_MSSP_ADD_RESELLER_INVITE_BTN)
    time.sleep(10)
    browserobj.acceptAlert()

def _inviteNewCustomer(browserobj, reseller_name, email, phone, company):
    browserobj.click(selector=CSS_MSSP_ADD_CUSTOMER_BTN)
    time.sleep(1)
    browserobj.click(selector=CSS_MSSP_NEW_CUSTOMER_RESELLER_DROPDOWN)
    browserobj.click(selector=CSS_MSSP_NEW_CUSTOMER_RESELLER_OPTION.format(reseller_name))
    _fillIn(browserobj, CSS_MSSP_ADD_CUSTOMER_FIRST_NAME_INPUT, 'zbat')
    _fillIn(browserobj, CSS_MSSP_ADD_CUSTOMER_LAST_NAME_INPUT, 'automated')
    _fillIn(browserobj, CSS_MSSP_ADD_CUSTOMER_PHONE_INPUT, phone)
    _fillIn(browserobj, CSS_MSSP_ADD_CUSTOMER_EMAIL_INPUT, email)
    _fillIn(browserobj, CSS_MSSP_ADD_CUSTOMER_COMPANY_INPUT, company)
    browserobj.click(selector=CSS_MSSP_ADD_CUSTOMER_INDUSTRY_DROPDOWN)
    browserobj.click(selector=CSS_MSSP_ADD_CUSTOMER_INDUSTRY_OPTION)
    browserobj.click(selector=CSS_MSSP_ADD_CUSTOMER_INVITE_BTN)
    time.sleep(1)
    browserobj.acceptAlert()

def _openResellerInvitationLink(browserobj, email, pwd):
    email_client = Email_Client('outlook.office365.com', email, pwd)
    emails = email_client.getEmails()
    for email in emails:
        _is_from_zingbox = email['from'] == 'no-reply@zingbox.com' #.getSenderEmail()
        _is_invitation_email = 'Invitation to join' in email['subject'] #.getSubject()
        if _is_from_zingbox and _is_invitation_email:
            email_body = email['body'] #.getBody()
            m = re.search(r'http(\S*)accept_invitation(\S*)\"', email_body)
            if m is not None:
                link = HTMLParser().unescape(m.group(0)[:-1])
                environment = os.environ['NODE_ENV']
                if 'testing' in environment:
                    link = link.replace('portal.mssp', 'testing')
                    link = link.replace('accept_invitation', '#accept_invitation')
                elif 'staging' in environment:
                    link = link.replace('soho', 'staging')
                    link = link.replace('accept_invitation', '#accept_invitation')
                browserobj.getURL(link)
                return True
    return False

def loginAndApproveCustomer(browserobj, **kwargs):
    login_name = kwargs['admin_panel_uname']
    login_pwd = kwargs['admin_panel_pwd']
    customer_email = kwargs['user_onboard_email']
    company_name = kwargs['company_name']
    browserobj.sendKeys(selector=CSS_CUSTOMERS_ADMIN_PANEL_LOGIN_EMAIL_INPUT, text=login_name)
    browserobj.sendKeys(selector=CSS_CUSTOMERS_ADMIN_PANEL_LOGIN_PWD_INPUT, text=login_pwd)
    browserobj.click(selector=CSS_CUSTOMERS_ADMIN_PANEL_LOGIN_BTN)
    waitLoadProgressDone(browserobj)

    panel = browserobj.findSingleCSS(selector=CSS_CUSTOMERS_ADMIN_PANEL_CUSTOMER_PANEL)
    if not panel:
        print('zbUIUserAccounts/loginAndApproveCustomer: not able to find customers panel from UI.')
        return False
    rows = browserobj.findMultiCSSFromBrowserobj(panel, selector=CSS_CUSTOMERS_ADMIN_PANEL_ROWS)
    if not rows:
        print('zbUIUserAccounts/loginAndApproveCustomer: not able to find rows of customer info from UI.')
        return False
    for row in rows:
        email = browserobj.findSingleCSS(browserobj=row, selector=CSS_CUSTOMERS_ADMIN_PANEL_EMAIL)
        if not email:
            print('zbUIUserAccounts/loginAndApproveCustomer: not able to find email field from customer info row.')
            return False
        if email.text == customer_email:
            browserobj.click(browserobj=row, selector=CSS_CUSTOMERS_ADMIN_PANEL_APPROVE_BTN)
            tenantid_input = browserobj.findSingleCSS(browserobj=row, selector=CSS_CUSTOMERS_ADMIN_PANEL_TENANTID_INPUT)
            if not tenantid_input:
                print('zbUIUserAccounts/loginAndApproveCustomer: not able to find tenantid input field from customer info row.')
                return False
            tenantid_input.clear()
            tenantid_input.send_keys(company_name)
            browserobj.click(browserobj=row, selector=CSS_CUSTOMERS_ADMIN_PANEL_PROVISION_BTN)
            return True
    print(('zbUIUserAccounts/loginAndApproveCustomer: not able to find email {}.'.format(customer_email)))
    return False

def _fillInResellerRegistrationForm(browserobj, phone, pwd):
    browserobj.click(selector=CSS_USER_REGISTRATION_GO_TO_REG_PAGE_BTN)
    kwargs = {
        "selector": CSS_USER_REGISTRATION_FIRST_NAME_INPUT,
        "waittype": "visibility",
        "timeout": 5
    }
    rcode = browserobj.waitCSS(**kwargs)
    if not rcode:
        print("zbUIUserAccounts.py/_fillInResellerRegistrationForm: Not able to enter registration page.")
        return False
    _fillIn(browserobj, CSS_USER_REGISTRATION_FIRST_NAME_INPUT, 'zbat')
    _fillIn(browserobj, CSS_USER_REGISTRATION_LAST_NAME_INPUT, 'automated')
    _fillIn(browserobj, CSS_USER_REGISTRATION_PHONE_INPUT, phone)
    _fillIn(browserobj, CSS_USER_REGISTRATION_PWD_INPUT, pwd)
    browserobj.click(selector=CSS_USER_REGISTRATION_TERMS_CHECKBOX)
    browserobj.click(selector=CSS_USER_REGISTRATION_REGISTER_BTN)
    return True

def _fillInCustomerRegistrationForm(browserobj, pwd):
    _fillIn(browserobj, CSS_USER_REGISTRATION_PWD_INPUT, pwd)
    browserobj.click(selector=CSS_USER_REGISTRATION_TERMS_CHECKBOX)
    browserobj.click(selector=CSS_USER_REGISTRATION_REGISTER_BTN)
    return True

def verifyNewReseller(browserobj, user_name):
    browserobj.click(selector=CSS_MSSP_SEARCH_RESELLER_BTN)
    browserobj.sendKeys(selector=CSS_MSSP_SEARCH_RESELLER_INPUT, text=user_name)
    browserobj.pressKey(key=Keys.ENTER)
    params = {}
    params["selector"] = CSS_MSSP_RESELLERS_NAME_LINK
    current_users = browserobj.findMultiCSS(**params)
    if not current_users:
        print('zbUIUserAccounts/verifyNewReseller: not able to find username from UI.')
        return False
    for element in current_users:
        if element.text == user_name:
            return True
    print('zbUIUserAccounts/verifyNewReseller: new user is not in the list')
    return False

def verifyNewCustomer(browserobj, **kwargs):
    company_name = kwargs['company_name']
    browserobj.click(selector=CSS_MSSP_SEARCH_CUSTOMER_BTN)
    browserobj.sendKeys(selector=CSS_MSSP_SEARCH_CUSTOMER_INPUT, text=company_name)
    browserobj.pressKey(key=Keys.ENTER)

    rows = browserobj.findMultiCSS(selector=CSS_MSSP_CUSTOMERS_ROWS)
    if not rows:
        print('zbUIUserAccounts/verifyNewCustomer: not able to find registered customer from search result.')
        return False
    return True

def sendEmailToCustomer(browserobj, _email):
    panel = browserobj.findSingleCSS(selector=CSS_CUSTOMERS_ADMIN_PANEL_CUSTOMER_PANEL)
    if not panel:
        print('zbUIUserAccounts/sendEmailToCustomer: not able to find customers panel from UI.')
        return False
    rows = browserobj.findMultiCSSFromBrowserobj(panel, selector=CSS_CUSTOMERS_ADMIN_PANEL_ROWS)
    if not rows:
        print('zbUIUserAccounts/sendEmailToCustomer: not able to find rows of customer info from UI.')
        return False
    for row in rows:
        email = browserobj.findSingleCSS(browserobj=row, selector=CSS_CUSTOMERS_ADMIN_PANEL_EMAIL)
        if not email:
            print('zbUIUserAccounts/sendEmailToCustomer: not able to find email field from customer info row.')
            return False
        if email.text == _email:
            browserobj.click(browserobj=row, selector=CSS_CUSTOMERS_ADMIN_PANEL_SEND_EMAIL_BTN)
            time.sleep(15)
            return True
    print(('zbUIUserAccounts/sendEmailToCustomer: not able to find email {}.'.format(_email)))
    return False

def fillInCustomerRegistrationForm(browserobj, **kwargs):
    email = kwargs['o365_email']
    pwd = kwargs['o365_pwd']
    user_pwd = kwargs['user_pwd']
    company_name = kwargs['company_name']
    rcode = True
    rcode = rcode and _openCustomerInvitationLink(browserobj, email, pwd, company_name)
    rcode = rcode and _fillInCustomerRegistrationForm(browserobj, user_pwd)
    return rcode

def _openCustomerInvitationLink(browserobj, email, pwd, company_name):
    email_client = Email_Client('outlook.office365.com', email, pwd)
    emails = email_client.getEmails()
    for email in emails:
        _is_from_zingbox = email['from'] == 'no-reply@zingbox.com' #.getSenderEmail()
        _is_invitation_email = 'Your account is approved' in email['subject'] #.getSubject()
        if _is_from_zingbox and _is_invitation_email:
            email_body = email['body'] #.getBody()
            m = re.search(r'http(\S*)register(\S*)\"', email_body)
            if m is not None:
                link = HTMLParser().unescape(m.group(0)[:-1])
                environment = os.environ['NODE_ENV']
                if 'testing' in environment:
                    link = link.replace(company_name, 'testing')
                    link = link.replace('register', '#register')
                elif 'staging' in environment:
                    link = link.replace(company_name, 'staging')
                    link = link.replace('register', '#register')
                browserobj.getURL(link)
                return True
    return False

def registerNewUser(browserobj, **kwargs):
    rcode = True
    email = kwargs['user_onboard_email']
    o365_email = kwargs['o365_email']
    pwd = kwargs['o365_pwd']
    user_pwd = kwargs['user_pwd']
    phone = kwargs['phone']
    _inviteNewUser(browserobj, email)
    rcode = rcode and _openInvitationLink(browserobj, o365_email, pwd)
    rcode = rcode and _fillInUserRegistrationForm(browserobj, phone, user_pwd)
    time.sleep(3)

    return rcode

def _deleteTargetUser(browserobj, email):
    params = {}
    params["selector"] = CSS_USER_ACCOUNT_EMAIL_LINK
    current_users_emails = browserobj.findMultiCSS(**params)
    params["selector"] = CSS_USER_ACCOUNT_ROLE
    current_users_roles = browserobj.findMultiCSS(**params)
    params["selector"] = CSS_USER_ACCOUNT_CHECK_BOX
    check_boxes = browserobj.findMultiCSS(**params)
    if not current_users_emails or not current_users_roles or not check_boxes:
        raise Exception('zbUIOnboarding.py/_deleteTargetUser: not able to find emails, roles or check boxes from UI.')
    if len(current_users_emails) != len(check_boxes):
        raise Exception('zbUIOnboarding.py/_deleteTargetUser: email count is different from checkbox count, it is dangerous to delete user, raise exception.')
    for index, element in enumerate(current_users_emails):
        email_text = element.text
        if email_text == email:
            if current_users_roles[index].text != 'Readonly':
                raise Exception('zbUIOnboarding.py/_deleteTargetUser: user to be deleted not a Readonly account, this is dangerous and is restricted.')
            check_boxes[index].click()
            browserobj.click(selector=CSS_USER_ACCOUNT_DELETE_USER_BTN)
            user.delete_user([email])
            user.delete_tenant([email])
            user.delete_trial_user([email])
            user.delete_reseller([email])
            return
    print(('zbUIOnboarding.py/_deleteTargetUser: email {} not found, no users get deleted.'.format(email)))
    return # It's okay if the user is not there

def _inviteNewUser(browserobj, email):
    browserobj.click(selector=CSS_USER_ACCOUNT_ADD_USER)
    time.sleep(1)
    browserobj.sendKeys(selector=CSS_USER_ACCOUNT_ADD_USER_INPUT, text=email)
    browserobj.click(selector=CSS_USER_ACCOUNT_ADD_USER_READ_ONLY_RADIO_BTN)
    browserobj.click(selector=CSS_USER_ACCOUNT_ADD_USER_INVITE_BTN)
    time.sleep(10)

def _openInvitationLink(browserobj, email, pwd):
    email_client = Email_Client('outlook.office365.com', email, pwd)
    emails = email_client.getEmails()
    for email in emails:
        _is_from_zingbox = email['from'] == 'no-reply@zingbox.com' #.getSenderEmail()
        _is_invitation_email = 'Invitation to join' in email['subject'] #.getSubject()
        if _is_from_zingbox and _is_invitation_email:
            email_body = email['body'] #.getBody()
            m = re.search(r'http(\S*)accept_invitation(\S*)\"', email_body)
            if m is not None:
                link = HTMLParser().unescape(m.group(0)[:-1])
                environment = os.environ['NODE_ENV']
                if 'testing' in environment:
                    link = link.replace('testing-soho', 'testing')
                    link = link.replace('accept_invitation', '#accept_invitation')
                elif 'staging' in environment:
                    link = link.replace('soho', 'staging')
                    link = link.replace('accept_invitation', '#accept_invitation')
                browserobj.getURL(link)
                return True
    return False

def _fillInUserRegistrationForm(browserobj, phone, pwd):
    browserobj.click(selector=CSS_USER_REGISTRATION_GO_TO_REG_PAGE_BTN)
    kwargs = {
        "selector": CSS_USER_REGISTRATION_FIRST_NAME_INPUT,
        "waittype": "visibility",
        "timeout": 5
    }
    rcode = browserobj.waitCSS(**kwargs)
    if not rcode:
        print("zbUIOnboarding.py.py/_fillInUserRegistrationForm: Not able to enter registration page.")
        return False
    _fillIn(browserobj, CSS_USER_REGISTRATION_FIRST_NAME_INPUT, 'zbat')
    _fillIn(browserobj, CSS_USER_REGISTRATION_LAST_NAME_INPUT, 'automated')
    _fillIn(browserobj, CSS_USER_REGISTRATION_PHONE_INPUT, phone)
    _fillIn(browserobj, CSS_USER_REGISTRATION_PWD_INPUT, pwd)
    browserobj.click(selector=CSS_USER_REGISTRATION_TERMS_CHECKBOX)
    browserobj.click(selector=CSS_USER_REGISTRATION_REGISTER_BTN)
    return True

def _fillIn(browserobj, selector, text):
    browserobj.sendKeys(selector=selector, text=text)
    browserobj.pressKey(key=Keys.TAB)

def verifyNewUser(browserobj, email):
    browserobj.click(selector=CSS_USER_TABLE_SEARCH_BTN)
    browserobj.sendKeys(selector=CSS_USER_TABLE_SEARCH_INPUT, text=email)
    browserobj.pressKey(key=Keys.ENTER)
    params = {}
    params["selector"] = CSS_USER_ACCOUNT_EMAIL_LINK
    current_users_emails = browserobj.findMultiCSS(**params)
    if not current_users_emails:
        print('zbUIOnboarding.py/verifyNewUser: not able to find emails from UI.')
        return False
    for element in current_users_emails:
        if element.text == email:
            return True
    print('zbUIOnboarding.py/verifyNewUser: new user is not in the list')
    return False

def _requestResetPwd(browserobj, email):
    browserobj.click(selector=CSS_FORGET_PWD_BUTTON)
    browserobj.sendKeys(selector=CSS_FORGET_PWD_EMAIL_IMPUT, text=email)
    browserobj.click(selector=CSS_FORGET_PWD_RESET_BUTTON)

def _openResetPasswordLink(browserobj, email, pwd):
    email_client = Email_Client('outlook.office365.com', email, pwd)
    emails = email_client.getEmails()
    for email in emails:
        _is_from_zingbox = email['from'] == 'no-reply@zingbox.com' #.getSenderEmail()
        _is_reset_pwd_email = 'Password Reset' in email['subject'] #.getSubject()
        if _is_from_zingbox and _is_reset_pwd_email:
            email_body = email['body'] .getBody()
            m = re.search(r'http(\S*)resetpwd(\S*)\"', email_body)
            if m is not None:
                link = HTMLParser().unescape(m.group(0)[:-1])
                environment = os.environ['NODE_ENV']
                if 'testing' in environment:
                    link = link.replace('zb-accounts', 'testing')
                    link = link.replace('resetpwd', '#resetpwd')
                elif 'staging' in environment:
                    link = link.replace('zb-accounts', 'staging')
                    link = link.replace('resetpwd', '#resetpwd')
                elif 'production' in environment:
                    link = link.replace('zb-accounts', 'production-candidate')
                    link = link.replace('resetpwd', '#resetpwd')
                browserobj.getURL(link)
                return True
    return False

def _fillInResetPwdForm(browserobj, newPwd):
    browserobj.sendKeys(selector=CSS_RESET_PWD_PWD_INPUT, text=newPwd)
    browserobj.sendKeys(selector=CSS_RESET_PWD_CONFIRM_PWD_INPUT, text=newPwd)
    browserobj.click(selector=CSS_RESET_PWD_BUTTON)

def login(browserobj, email, pwd):
    browserobj.sendKeys(selector=CSS_LOGIN_USERNAME_FIELD, text=email)
    browserobj.sendKeys(selector=CSS_LOGIN_PASSWORD_FIELD, text=pwd)
    browserobj.click(selector=CSS_LOGIN_BUTTON)

def logout(browserobj):
    browserobj.click(selector=CSS_USER_BUTTON)
    time.sleep(2)
    browserobj.click(selector=CSS_LOGOUT_BUTTON)

class Onboarding():

    def __init__(self, **kwargs):
        self.params = kwargs
        self.selenium = Login(**kwargs).login()

    def verifyResetPassword(self, **kwargs):
        email = kwargs['o365_email']
        pwd = kwargs['o365_pwd']
        newPwd = kwargs['newPwd']
        logout(self.selenium)
        time.sleep(2)
        try:
            _requestResetPwd(self.selenium, email)
        except:
            print('zbUILoginCore.py/verifyResetPassword: unable to request password reset.')
            return False
        time.sleep(15)
        rcode = _openResetPasswordLink(self.selenium, email, pwd)
        waitLoadProgressDone(self.selenium)
        try:
            _fillInResetPwdForm(self.selenium, newPwd)
        except:
            print('zbUILoginCore.py/verifyResetPassword: unable to fill in reset password form.')
            return False
        time.sleep(2)
        rcode = rcode and self.selenium.getURL(self.params["url"])
        login(self.selenium, email, newPwd)
        rcode = rcode and self.selenium.findSingleCSS(selector=CSS_NAVBAR_USERNAME, timeout=5)
        return rcode

    def checkResetPassword(self, **kwargs):
        pwd = kwargs['o365_pwd']
        newPwd = pwd + '1'
        rcode = self.verifyResetPassword(newPwd=newPwd, **kwargs)
        # Reset password to original one
        rcode = rcode and self.verifyResetPassword(newPwd=pwd, **kwargs)
        return rcode

    def gotoUserPage(self):
        url = urlparse(self.params["url"])
        rcode = self.selenium.getURL(url.scheme+'://'+url.netloc+'/administration/tenantaccounts')
        waitLoadProgressDone(self.selenium)

    def checkUserOnboard(self, **kwargs):
        user.setup()
        self.gotoUserPage()
        email = kwargs['user_onboard_email']
        try:
            _deleteTargetUser(self.selenium, email)
        except Exception as error:
            print(error)
            return False
        time.sleep(3)
        self.gotoUserPage()
        rcode = registerNewUser(self.selenium, **kwargs)
        self.gotoUserPage()
        rcode = rcode and verifyNewUser(self.selenium, email)
        user.teardown()
        return rcode

    def gotoResellersPage(self):
        url = urlparse(self.params["url"])
        rcode = self.selenium.getURL(url.scheme+'://'+url.netloc+'/msspindex.html')
        waitLoadProgressDone(self.selenium)
        self.selenium.click(selector=CSS_MSSP_RESELLERS_BTN)
        waitLoadProgressDone(self.selenium)

    def gotoCustomerPage(self):
        url = urlparse(self.params["url"])
        rcode = self.selenium.getURL(url.scheme+'://'+url.netloc+'/msspindex.html')
        waitLoadProgressDone(self.selenium)
        self.selenium.click(selector=CSS_MSSP_CUSTOMERS_BTN)
        waitLoadProgressDone(self.selenium)

    def gotoAdminPortal(self, url):
        url = urlparse(url)
        rcode = self.selenium.getURL(url.scheme+'://'+url.netloc+'/login')
        waitLoadProgressDone(self.selenium)

    def checkResellerOnboard(self, **kwargs):
        user.setup()
        self.gotoResellersPage()
        email = kwargs['user_onboard_email']
        try:
            _deleteTargetReseller(email)
        except Exception as error:
            print(error)
            return False
        identity = int(random.random() * 1000)
        user_name = 'zbat_automated_{}'.format(identity)
        kwargs['user_name'] = user_name
        rcode = registerNewReseller(self.selenium, **kwargs)
        self.gotoResellersPage()
        rcode = rcode and verifyNewReseller(self.selenium, user_name)
        user.teardown()
        return rcode

    def checkCustomerOnboard(self, **kwargs):
        user.setup()
        self.gotoCustomerPage()
        email = kwargs['user_onboard_email']
        admin_uiportal = kwargs['admin_uiportal']
        try:
            _deleteTargetCustomer(email)
        except Exception as error:
            print(error)
            return False
        registerNewCustomer(self.selenium, **kwargs)
        self.gotoAdminPortal(admin_uiportal)
        rcode = loginAndApproveCustomer(self.selenium, **kwargs)
        time.sleep(5)
        user.mark_trial_user_ready([email])
        self.selenium.refresh()
        waitLoadProgressDone(self.selenium)
        rcode = rcode and sendEmailToCustomer(self.selenium, email)
        rcode = rcode and fillInCustomerRegistrationForm(self.selenium, **kwargs)
        self.gotoCustomerPage()
        rcode = rcode and verifyNewCustomer(self.selenium, **kwargs)
        user.teardown()
        return rcode

    def close(self):
        if self.selenium:
            self.selenium.quit()
