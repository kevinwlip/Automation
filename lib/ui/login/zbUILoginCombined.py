#!/usr/bin/python

import time
import os
from common.zbSelenium import zbSelenium
from ui.zbUIShared import waitLoadProgressDone
from urllib.parse import urlparse
from selenium.webdriver.common.keys import Keys
from util.ring_central import RingCentral
from builtins import str
from locator.login import LoginPageLoc
import logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class Login(object):
    def __init__(self, **kwargs):
        self.params = kwargs
        if "browser" not in kwargs:  self.params["browser"] = "chrome"
        # If there are no existing browser object, then create new, else reuse
        self.selenium = kwargs["browserInstance"] if "browserInstance" in kwargs else zbSelenium(**self.params)

    def go_to_dashboard(self):
        logger.info('Entering dashboard page ...')
        url = urlparse(self.params["url"])
        if not self.selenium.getURL(url.scheme + '://' + url.netloc):
            logger.error("Unable to reach the dashboard")
            return False
        waitLoadProgressDone(self.selenium)
        return True

    def gotoLoginPage(self):
        if self.selenium.getCurrentURL() == self.params["url"]:
            self.selenium.scroll_to_top_page()
            return self.selenium
        if self.selenium.getURL(self.params["url"]):
            waitLoadProgressDone(self.selenium)
            return self.selenium
        else:
            return False

    def login(self, login_type=None, remember_token=False, alwaysProceed=False, **kwargs):
        """Login to dashboard
        :param login_type: (optional) Specify the only login method among 'sso', 'standard'and '2fa' to be used.
        :param remember_token: (optional) Remember the computer for 24 hours if True.
        :param alwaysProceed: (optional) Always retry when fail to login if True.
        :param kwargs: (optional) dictionary containing RingCentral Configurations.
        Usage::
        >> browser = new Login()
        >> browser.login()
        If no params are passed into login, then it just login with the method available as the browser goes.
        After logging in, the page will land on V2 dashboard.
        >> browser.login(login_type='standard')
        If login_type = 'standard', then it only returns True when it login successfully with standard login.
        If the account requires 2FA login, it returns False
        >> browser.login(login_type='2fa')
        If login_type = '2fa', then it only returns True when it login successfully with 2fa login.
        If the account does not require 2FA login, it returns False
        """

        logger.info("Logging in user's account...")

        # login_type is 'standard', 'sso', or '2fa'
        username = self.params['username']
        password = self.params['password']

        if not self.gotoLoginPage():
            logger.error('Unable to get to the login page!')
            return False

        # handling for IE since IE automatically login
        if self.selenium.findSingleCSS(selector=LoginPageLoc.CSS_INSPECTOR_ONBOARD_PAGE, timeout=2) or self.selenium.findSingleCSS(
                selector=LoginPageLoc.CSS_SERIES_BAR, timeout=1):
            return self.selenium

        # =========================================
        # SSO login block START
        # =========================================

        if self.selenium.findSingleCSS(selector=LoginPageLoc.CSS_NEXT_BUTTON, timeout=1):
            if login_type and login_type != 'sso':
                logger.error('Entering the SSO page, unable to login with ' + login_type)
                return False
            logger.info('Entering the SSO Login...')

            self.params["selector"] = LoginPageLoc.CSS_USERNAME_FIELD
            self.params["text"] = username
            self.selenium.sendKeys(**self.params)

            self.params["selector"] = LoginPageLoc.CSS_NEXT_BUTTON
            self.selenium.click(**self.params)

            # Standard login for internal user
            if self.selenium.findSingleCSS(selector=LoginPageLoc.CSS_LOGIN_BUTTON, timeout=3):
                self.params["selector"] = LoginPageLoc.CSS_PASSWORD_FIELD
                self.params["text"] = password
                self.selenium.sendKeys(**self.params)
                time.sleep(2)

                self.params["selector"] = LoginPageLoc.CSS_LOGIN_BUTTON
                # normal login don't work no good on these browsers
                if self.params["browser"] in ["chromeipad", "internet explorer"]:
                    self.params["text"] = Keys.ENTER
                    self.selenium.sendKeys(**self.params)
                else:
                    self.selenium.click(**self.params)
                waitLoadProgressDone(self.selenium)

            # SSO login for IDP user
            else:
                self.params["selector"] = LoginPageLoc.CSS_OUTLOOK_EMAIL_FIELD
                self.params["text"] = username
                self.selenium.sendKeys(**self.params)

                self.params["selector"] = LoginPageLoc.CSS_OUTLOOK_SUBMIT_BUTTON
                self.selenium.click(**self.params)

                self.params["selector"] = LoginPageLoc.CSS_OUTLOOK_PASSWORD_FIELD
                self.params["text"] = password
                self.selenium.sendKeys(**self.params)

                self.params["selector"] = LoginPageLoc.CSS_OUTLOOK_SUBMIT_BUTTON
                self.selenium.click(**self.params)

                self.params["selector"] = LoginPageLoc.CSS_OUTLOOK_NO_BUTTON
                self.selenium.click(**self.params)

            waitLoadProgressDone(self.selenium)

            if not self._get_v2_dashboard():
                logger.error('Unable to reach V2 dashboard, Login failed!')
                return False

            return self.selenium

        # =========================================
        # standard login block START
        # =========================================

        elif self.selenium.findSingleCSS(selector=LoginPageLoc.CSS_LOGIN_BUTTON, timeout=1):
            if login_type == 'sso':
                logger.error('Enterting Standard Login Page, not support SSO Login')
                return False
            logger.info('Entering Standard Login...')
            self.params["selector"] = LoginPageLoc.CSS_USERNAME_FIELD
            self.params["text"] = username
            self.selenium.sendKeys(**self.params)

            self.params["selector"] = LoginPageLoc.CSS_PASSWORD_FIELD
            self.params["text"] = password

            self.selenium.sendKeys(**self.params)
            self.params["selector"] = LoginPageLoc.CSS_LOGIN_BUTTON
            # normal login don't work no good on these browsers
            if self.params["browser"] in ["chromeipad", "internet explorer"]:
                self.params["text"] = Keys.ENTER
                rcode = self.selenium.sendKeys(**self.params)
            else:
                rcode = self.selenium.click(**self.params)

            # =========================================
            # 2FA login block START
            # =========================================
            # This process would always happen after the normal login process of standard login
            if self.selenium.findSingleCSS(selector=LoginPageLoc.CSS_2FA_FIELD, timeout=1) \
                    or self.selenium.findSingleCSS(selector=LoginPageLoc.CSS_2FA_SET_UP_WITHOUT_INFO, timeout=1):

                if login_type and login_type != '2fa':
                    logger.error('This page is 2FA login page, does not support other login type!')
                    return False
                logger.info("Entering Two FA login...")

                # After ordinary login, user may be required to provide their phone number for 2FA, if owner requires so.
                # The user may not set up phone number before
                if self.selenium.findSingleCSS(selector=LoginPageLoc.CSS_2FA_SET_UP_WITHOUT_INFO):
                    logger.info("Two FA has been enabled by owner.")
                    if not self.selenium.click(selector=LoginPageLoc.CSS_2FA_INFO_GET_STARTED):
                        logger.error("Unable to click to start 2FA phone info accessing!")
                        return False
                    waitLoadProgressDone(self.selenium)
                    if self.selenium.findSingleCSS(selector=LoginPageLoc.CSS_INPUT_NEW_PHONE):
                        if not self._set_up_phone_info():
                            logger.info("User phone number is not prepared. Accessing User Phone number...")
                            logger.error("Unable to complete phone number verification!")
                            return False
                    waitLoadProgressDone(self.selenium)

                # After ordinary login, user may be required to provide their phone number for 2FA.
                # The user have set up phone number beforehand
                if self.selenium.findSingleCSS(selector=LoginPageLoc.CSS_2FA_FIELD):
                    logger.info("Two FA has been enabled. Type in sms code to verify...")
                    if not self._type_in_sms_code(auth="login", remember_token=remember_token, **kwargs):
                        logger.error("Unable to verify sms code!")
                        return False
                    self.selenium.click(selector=LoginPageLoc.CSS_TWO_FA_AUTH)
                    waitLoadProgressDone(self.selenium)
                else:
                    logger.error('Unable to log in with 2FA')
                    return False

        # =========================================
        # Login block END
        # =========================================
        waitLoadProgressDone(self.selenium)

        if not self._get_v2_dashboard():
            logger.error('Unable to reach V2 dashboard')
            return False
        return self.selenium

    def _get_v2_dashboard(self):
        """
        After log in, check to see if reach the V2 version dashboard
        :return: True if no error, False otherwise
        """
        if self.selenium.findSingleCSS(selector=".dialog-card", timeout=0.1):
            self.selenium.click(selector=".mat-button.primary")

        # Check the status, make sure we reach the v2 version
        if not self.selenium.findSingleCSS(selector=LoginPageLoc.CSS_V2_LOGO):
            logger.error('Not Reach V2 home page')
            return False
        return True

    def _set_up_phone_info(self):
        phone_num = str(os.environ['RING_CENTRAL_ACCOUNT'])[1:]
        self.selenium.sendKeys(selector=LoginPageLoc.CSS_INPUT_NEW_PHONE, text=phone_num, timeout=3)
        self.params["selector"] = LoginPageLoc.CSS_TWO_FA_NEXT
        if self.params["browser"] in ["chromeipad", "internet explorer"]:
            self.params["text"] = Keys.ENTER
            rcode = self.selenium.sendKeys(**self.params)
        else:
            rcode = self.selenium.click(**self.params)
        if not rcode:
            logger.error('Unable to set phone number!')
            return False
        return True

    def _type_in_sms_code(self, auth="enable", remember_token=False, **kwargs):
        ring_central = RingCentral(**kwargs)
        sms_code = ring_central.get_2fa_code()
        if not sms_code:
            logger.critical("Test Script Failure: unable to receive sms_code!")
            return False

        self.selenium.sendKeys(selector=LoginPageLoc.CSS_2FA_FIELD, text=sms_code, timeout=3)

        if remember_token:
            self.selenium.click(selector=LoginPageLoc.CSS_REMEMBER_TOKEN, timeout=3)
        self.params["selector"] = LoginPageLoc.CSS_TWO_FA_AUTH if auth == "login" else LoginPageLoc.CSS_TWO_FA_VERIFY

        if self.params["browser"] in ["chromeipad", "internet explorer"]:
            self.params["text"] = Keys.ENTER
            rcode = self.selenium.sendKeys(**self.params)
        else:
            rcode = self.selenium.click(**self.params)

        if not rcode:
            logger.error('Unable to send sms_code!')
            return False

        if remember_token:
            self.selenium.click(selector=LoginPageLoc.CSS_REMEMBER_TOKEN, timeout=3)
        return True

    def logout(self):
        logger.info('logging out from the current account...')
        if not self.selenium.click(selector=LoginPageLoc.CSS_AVATAR, timeout=3):
            logger.error('Unable to click Avatar icon')
            return False
        if not self.selenium.click(selector=LoginPageLoc.CSS_LOG_OUT, timeout=3):
            logger.error('Unable to click Preference')
            return False
        waitLoadProgressDone(self.selenium)
        return True

    def close(self):
        if self.selenium:
            self.selenium.quit()