import time
from .zbUILoginCombined import Login
from ui.zbUIShared import waitLoadProgressDone, checkFactory
from selenium.webdriver.common.keys import Keys
from locator.login import LoginPageLoc

import logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class SSOLogin(Login):
    def __init__(self, **kwargs):
        logger.info('Entering testing of Two FA Login...')
        super(SSOLogin, self).__init__(**kwargs)

    def verify_login_page(self):
        if not self.gotoLoginPage():
            logger.error('Unable to get to the login page!')
            return False
        check_factory = checkFactory(self.selenium)
        check_factory.add_to_checklist(css=LoginPageLoc.CSS_LOGIN_GE_LOGO,
                                       element_name="GE Healthcare & Zingbox Logo")\
                     .add_to_checklist(css=LoginPageLoc.CSS_NEXT_BUTTON,
                                       elemet_name="SSO Login Button")
        assert check_factory.check_all()
        num = len(self.selenium.findMultiCSS(selector="input"))
        if num != 1:
            logger.error('There are more than one input on login page. Unexpected in SSO Login.')
            return False
        return True

    def login_sso(self):
        logger.info("Logging in user's account...")

        # login_type is 'standard', 'sso', or '2fa'
        username = self.params['username']
        password = self.params['password']

        if not self.gotoLoginPage():
            logger.error('Unable to get to the login page!')
            return False

        # handling for IE since IE automatically login
        if self._get_v2_dashboard():
            logger.info('Dashboard page has been reached')
            return self.selenium

        # =========================================
        # SSO login block START
        # =========================================
        logger.info('Entering the SSO Login...')

        self.params["selector"] = LoginPageLoc.CSS_USERNAME_FIELD
        self.params["text"] = username
        self.selenium.sendKeys(**self.params)

        self.params["selector"] = LoginPageLoc.CSS_NEXT_BUTTON
        self.selenium.click(**self.params)

        waitLoadProgressDone(self.selenium)

        # handling for automatically login in SSO,when SSO login is not expired in the single sign on platform.
        if self._get_v2_dashboard():
            logger.info('Dashboard page has been reached')
            return self.selenium

        if self.selenium.findSingleCSS(selector=LoginPageLoc.CSS_OUTLOOK_EMAIL_ACCOUNT, timeout=0):
            logger.info('Browser remembers some accounts, skip this and add a new account instead')
            self.selenium.click(selector=LoginPageLoc.CSS_OUTLOOK_EMAIL_OTHER)

        # SSO login for IDP user
        self.params["selector"] = LoginPageLoc.CSS_OUTLOOK_EMAIL_FIELD
        self.params["text"] = username
        self.selenium.sendKeys(**self.params)

        self.params["selector"] = LoginPageLoc.CSS_OUTLOOK_SUBMIT_BUTTON
        self.selenium.click(**self.params)

        self.params["selector"] = LoginPageLoc.CSS_OUTLOOK_PASSWORD_FIELD
        self.params["text"] = password
        self.selenium.sendKeys(**self.params, timeout=2)

        self.params["selector"] = LoginPageLoc.CSS_OUTLOOK_SUBMIT_BUTTON
        self.selenium.click(**self.params)

        self.params["selector"] = LoginPageLoc.CSS_OUTLOOK_NO_BUTTON
        self.selenium.click(**self.params)

        waitLoadProgressDone(self.selenium)

        if not self._get_v2_dashboard():
            logger.error('Unable to reach V2 dashboard, Login failed!')
            return False

        return self.selenium




