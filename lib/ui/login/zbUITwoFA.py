import time
from .zbUILoginCombined import Login
from ui.zbUIShared import waitLoadProgressDone
from selenium.webdriver.common.keys import Keys
from locator.login import LoginPageLoc

import logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class TwoFaLogin(Login):
    def __init__(self, **kwargs):
        logger.info('Entering testing of Two FA Login...')
        super(TwoFaLogin, self).__init__(**kwargs)

    # ====================================================
    # For every type of user
    # ====================================================
    def _go_to_preference_setting(self):
        logger.info('Acquiring the link to preference page...')
        if not self.selenium.click(selector=LoginPageLoc.CSS_AVATAR, timeout=3):
            logger.error('Unable to click Avatar icon')
            return False
        if not self.selenium.click(selector=".mat-menu-content a:nth-of-type(1)", timeout=3):
            logger.error('Unable to click Preference')
            return False
        time.sleep(10)
        return True

    def _2fa_switch_turn_on(self, *args):
        # Turn on the 2FA switch
        two_fa_element = self.selenium.findSingleCSS(selector=LoginPageLoc.CSS_TWO_FA_SWITCH)
        if not two_fa_element:
            logger.error('zbSelenium/click: {}'.format("unable to click"))
            return False

        if two_fa_element.get_attribute("aria-checked") == 'true':
            logger.info('Two FA Authentication has already been enabled. Pass')
            return True

        two_fa_element.click()
        time.sleep(2)

        self.selenium.click(selector='button[ng-click="ctrl.twofaSteps.startInfo = true"]')

        if not self._confirm_pw_verify_phone():
            logger.error('Unable to confirm password and verify phone number when enabling 2FA for user: ' + self.params['username'])
            return False

        if len(args) == 1 and args[0] == 'all':
            if not self.selenium.click(selector='button[name="verify code"][ng-click="ctrl.tenantTwoFA(\'enable\')"]', timeout=3):
                logger.error('Not get confirmation of this operation result!')
                return False
            waitLoadProgressDone(self.selenium)
            return True
        else:
            if not self.selenium.click(selector='button[name="close dialog"][ng-click="ctrl.closeDialog(true)"]', timeout=3):
                logger.error('Not get confirmation of this operation result!')
                return False
            waitLoadProgressDone(self.selenium)
            return True


    def _2fa_switch_turn_off(self, *args):
        # Turn off the 2FA switch
        two_fa_element = self.selenium.findSingleCSS(selector=LoginPageLoc.CSS_TWO_FA_SWITCH)
        if not two_fa_element:
            logger.error('zbSelenium/click: {}'.format("unable to click"))
            return False

        if two_fa_element.get_attribute("aria-checked") == 'false':
            logger.info('Two FA Authentication has already been disabled. Pass')
            return True

        two_fa_element.click()
        time.sleep(2)

        if not self._confirm_pw_verify_phone():
            logger.error('Unable to confirm password and verify phone number when disabling 2FA for user: ' + self.params['username'])
            return False

        if len(args) == 1 and args[0] == 'all':
            if not self.selenium.click(selector='button[name="verify code"][ng-click="ctrl.tenantTwoFA(\'disable\')"]'):
                logger.error('Not get confirmation of this operation result!')
                return False
            waitLoadProgressDone(self.selenium)
            return True
        else:
            if not self.selenium.click(selector='button[name="close dialog"][ng-click="ctrl.closeDialog(true)"]'):
                logger.error('Not get confirmation of this operation result!')
                return False
            waitLoadProgressDone(self.selenium)
            return True


    def _confirm_pw_verify_phone(self):
        try:
            password = self.params['password']
            self.params["selector"] = LoginPageLoc.CSS_TWO_FA_PASSWORD
            self.params["text"] = password
            self.selenium.sendKeys(**self.params)
            time.sleep(2)

            self.params["selector"] = LoginPageLoc.CSS_CONFIRM_PASSOWORD_BUTTON

            # normal login don't work no good on these browsers
            if self.params["browser"] in ["chromeipad", "internet explorer"]:
                self.params["text"] = Keys.ENTER
                rcode = self.selenium.sendKeys(**self.params)
            else:
                rcode = self.selenium.click(**self.params)

            if not rcode:
                logger.error('Confirm password: Unable to login')
                return False

                # case1: there is already an telephone number stored, then change it to the Ringcentral-compatible one
            if self.selenium.findSingleCSS(selector=LoginPageLoc.CSS_CHANGE_PHONE_NUMBER, timeout=1):
                self.selenium.click(selector=LoginPageLoc.CSS_CHANGE_PHONE_NUMBER, timeout=2)

                # case2: there is no user telephone number is stored
            if self.selenium.findSingleCSS(selector=LoginPageLoc.CSS_INPUT_NEW_PHONE):
                if not self._set_up_phone_info():
                    logger.error("Unable to complete phone number verification!")
                    return False
            time.sleep(2)

            # Now the phone number is sure to be the same with RingCentral Account.
            # We can fill the blank with RingCentral SMS Code
            if not self._type_in_sms_code(auth="auth"):
                logger.error("Unable to verify sms code!")
                return False
            waitLoadProgressDone(self.selenium)
            return True

        except Exception as e:
            logger.error(e.message)
            return False

    def check_enable_2fa_user_for_self(self):
        if not self._go_to_preference_setting():
            return False
        logger.info('Entering Preference setting Page to enable Two FA...')
        if not self._2fa_switch_turn_on():
            logger.error('Unable to confirm 2FA for user: ' + self.params['username'])
            return False

        waitLoadProgressDone(self.selenium)
        return True

    def check_disable_2fa_user_for_self(self):
        if not self._go_to_preference_setting():
            return False
        logger.info('Entering Preference setting Page to disable Two FA...')
        if not self._2fa_switch_turn_off():
            logger.error('Unable to turn off 2FA for user: ' + self.params['username'])
            return False

        waitLoadProgressDone(self.selenium)
        return True

    # ====================================================
    # Only for owner
    # ====================================================
    def _goto_user_account_setting(self):
        logger.info('Entering user account setting ...')

        # Hover on administration
        admin_element = self.selenium.findSingleCSS(selector=LoginPageLoc.CSS_NAVBAR_APPLICATION, timeout=1)
        if not admin_element or not admin_element.is_displayed():
            logger.error('Unable to find administration in dashboard')
            return False
        self.selenium.hoverElement(admin_element)

        # Click User Account Setting
        if not self.selenium.click(selector=LoginPageLoc.CSS_USER_ACCOUNT, timeout=1):
            logger.error('Unable to enter administration')
            return False
        waitLoadProgressDone(self.selenium)
        return True

    def check_enable_2fa_owner_for_all(self):
        if not self._goto_user_account_setting():
            logger.error('Unable to go to the user account setting')
            return False

        logger.info('Entering administrator setting page to enable two FA...')

        if not self._2fa_switch_turn_on('all'):
            logger.error('Unable to confirm 2FA for all users in this tenant')
            return False

        waitLoadProgressDone(self.selenium)
        return True

    def check_disable_2fa_owner_for_all(self):
        if not self._goto_user_account_setting():
            logger.error('Unable to go to the user account setting')
            return False

        logger.info('Entering administrator setting page to disable two FA...')

        if not self._2fa_switch_turn_off('all'):
            logger.error('Unable to disable 2FA for all users in this tenant')
            return False

        waitLoadProgressDone(self.selenium)
        return True
