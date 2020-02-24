from ui.zbUIShared import checkFactory, clickAndVerifyColumns, verifyTableEntries, createHeaderDict,\
    waitLoadProgressDone
from selenium.webdriver.common.action_chains import ActionChains
from locator.login import LoginPageLoc

import selenium.common.exceptions as selexcept

import time

import logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class OneUserEditor(object):
    """
    All of the below public functions are called when the page is at the User Accounts Page.
    """
    def __init__(self, browserobj, user, **kwargs):
        self.selenium = browserobj
        self.params = kwargs
        self.params["user"] = user

    def _get_to_edit_page(self):
        if self.params["user"] in self.selenium.getCurrentURL():
            return True
        user_inventory = self.selenium.findSingleCSS(selector=".zing-table-tenantAccounts")
        inventory_data = createHeaderDict(user_inventory)
        for i in range(1, len(inventory_data["Email (Username)"])):
            print(inventory_data["Email (Username)"][i].text)
            if inventory_data["Email (Username)"][i].text == self.params["user"]:
                inventory_data["Email (Username)"][i].click()
                waitLoadProgressDone(self.selenium)
                return True
        logger.error("Unable to get to the edit page of user: " + self.params["user"])
        return False

    def _get_to_edit_subcard(self, card_header):
        # Supposing the User Account Page First has already been reached. Now start from getting to the
        # edit page of one user account.
        if not self._get_to_edit_page():
            return False
        cards = self.selenium.findMultiCSS(selector="md-card._md")

        for card in cards:
            try:
                card_title = card.find_element_by_tag_name("md-title")
                if card_title.text == card_header:
                    logger.info("Find the User Role & Access Section in this page")
                    hover = ActionChains(self.selenium.driver).move_to_element(card)
                    hover.perform()
                    return card
            except selexcept.NoSuchElementException:
                pass
        logger.error("Unable to find the card of: " + card_header)
        return False

    def verify_user_role(self, expected_role):
        user_inventory = self.selenium.findSingleCSS(selector=".zing-table-tenantAccounts")
        inventory_data = createHeaderDict(user_inventory)
        for i in range(1, len(inventory_data["Email (Username)"])):
            if inventory_data["Email (Username)"][i].text == self.params["user"]:
                if inventory_data["Role"][i].text == expected_role:
                    logger.info("The user role of {} is verified!".format(expected_role))
                    return True
                else:
                    logger.error("The expected role is {} while the actual role is {}.".format(
                        expected_role,
                        inventory_data["Role"][i].text))
                return False
        logger.error("Unable to find the specified user")
        return False

    def reassign_user_role(self, new_role):
        role_card = self._get_to_edit_subcard("User Role & Access")
        if not role_card:
            return False
        button_to_select = role_card.find_element_by_class_name("md-select-icon")
        button_to_select.click()

        options = self.selenium.findMultiCSS(selector='md-option[ng-value="userRoleOption"]')
        for opt in options:
            if opt.text == new_role:
                opt.click()
                time.sleep(2)
                self.selenium.click(selector="div.buttons button.md-raised")
                waitLoadProgressDone(self.selenium)
                logger.info("Successfully selected the user role!")
                return True
        return False

    def require_2fa_authentication(self, enable=True):
        if not self._get_to_edit_page():
            return False
        switch_card = self._get_to_edit_subcard("Login")
        switch = self.selenium.findSingleCSS(selector=LoginPageLoc.CSS_TWO_FA_SWITCH)
        if not switch:
            logger.error("Unable to find 2FA switch!")
            return False

        expected_attr = 'true' if enable else 'false'
        if switch.get_attribute("aria-checked") == expected_attr:
            logger.info("The 2fa has already been set as required")
            self.selenium.click(selector="div.buttons button.md-raised")
            waitLoadProgressDone(self.selenium)
            return True
        switch.click()
        time.sleep(2)
        if switch.get_attribute("aria-checked") != expected_attr:
            logger.error("Clicking the swicth does not change the setting!")
            return False
        self.selenium.click(selector="div.buttons button.md-raised")
        waitLoadProgressDone(self.selenium)
        logger.info("Successfully set the 2FA for the user!")
        return True

    def verify_2fa_enable_or_not(self, enable=True):
        user_inventory = self.selenium.findSingleCSS(selector=".zing-table-tenantAccounts")
        inventory_data = createHeaderDict(user_inventory)
        expected_status = 'enabled' if enable else 'disabled'
        for i in range(1, len(inventory_data["Email (Username)"])):
            if inventory_data["Email (Username)"][i].text == self.params["user"]:
                if inventory_data["Two-Factor Authentication"][i].text == expected_status:
                    logger.info('Successfully verified the 2fa authentication requirement')
                    return True
                else:
                    logger.error('Unable to verify the 2fa authentication')
                    logger.error('The actual 2fa status is {} but what we expect is {}'.format(
                        inventory_data["Two-Factor Authentication"][i].text,
                        expected_status))
                    return False
        logger.error('Cannot find the user {} in the user inventory'.format(self.params["user"]))
        return False











