from ui.zbUIShared import checkFactory, clickAndVerifyColumns, verify_sort_inventory_v1, createHeaderDict, \
    waitLoadProgressDone
from ui.login.zbUILoginCore import Login
from locator.administration import AdministrationLoc
from locator.login import LoginPageLoc
from common.zbConfig import defaultEnv
env = defaultEnv()

import time
import logging
import os
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class UserAccountsManipulator(object):
    """
    This is a util class to provide tool methods for pages of user account administration to
    perform any user account related operations, including:

    1, Check the existing user account inventory.
    2, Create a user of different roles.
    3, Remove a user.

    All these operations are assumed to be performed when the page is already User Account Administration Page
    """
    def __init__(self, browserobj, **kwargs):
        self.selenium = browserobj
        self.params = kwargs

    def _fill_in_profile_info(self):
        if not self.selenium.findSingleCSS(selector=AdministrationLoc.CSS_EULA_POPUP, timeout=10):
            logging.error('Unable to get to the EULA page, the user has been invited before. Relogin instead!')
            return False

        assert self.selenium.findSingleCSS(selector=AdministrationLoc.CSS_TENTH_PAGE, timeout=15)
        assert self.selenium.click(selector=AdministrationLoc.CSS_ACCEPT_EULA, timeout=5)
        assert self.selenium.findSingleCSS(selector=AdministrationLoc.CSS_WELCOME_TEXT, timeout=15)

        first_name = self.selenium.findSingleCSS(selector=AdministrationLoc.CSS_REGISTER_NAME)
        first_name.click()
        first_name.send_keys("ZBAT")

        second_name = self.selenium.findSingleCSS(selector=AdministrationLoc.CSS_REGISTER_LAST_NAME)
        second_name.click()
        second_name.send_keys("UserAccount")

        phone = self.selenium.findSingleCSS(selector="input#phone")
        phone.click()
        phone.send_keys("7472911542")

        password = self.selenium.findSingleCSS(selector="input#tooltipPassword")
        password.click()
        password.send_keys(env["password"])

        submit = self.selenium.findSingleCSS(selector=".zing-button", waittype="clickable")
        submit.click()

        assert self.selenium.findSingleCSS(selector='.welcome-text', timeout=5)
        assert self.selenium.click(selector=".zing-button")
        waitLoadProgressDone(self.selenium)
        return True

    def _relogin_with_registered_account(self, user):
        # because invite page link does not work, we should direct to login page.
        self.params["password"] = env["password"]
        self.params["username"] = user
        login_helper = Login(browserInstance=self.selenium, **self.params)
        assert login_helper.login()
        logging.info('Re Login Successfully!')
        assert login_helper.logout()
        return True

    def check_user_account_inventory_sort(self):
        if not clickAndVerifyColumns(self.selenium, verify_list=AdministrationLoc.user_account_column_list):
            logger.info('Unable to click and verify all column headers')
            return False

        if not verify_sort_inventory_v1(self.selenium, columns_not_sort=["Access Keys"]):
            logger.error('Sorting of user account inventory fail the check')
            return False
        return True

    def check_user_account_search(self):
        # prepare the data to be searched
        user_inventory = self.selenium.findSingleCSS(selector=".zing-table-tenantAccounts")
        inventory_data = createHeaderDict(user_inventory)
        data_to_search = dict()
        for col in inventory_data.keys():
            if col in AdministrationLoc.search_item_list:
                for row in inventory_data[col][1:]:
                    if row.text is not "" and row.text is not "N/A":
                        data_to_search[col] = row.text
                        break

        for search_col, search_value in data_to_search.items():
            logger.info("Search the value of {} by typing in {}...".format(search_col, search_value))
            self.selenium.click(selector=AdministrationLoc.CSS_SEARCH_ICON)
            search_bar = self.selenium.findSingleCSS(selector=".filter-bar #table-search")
            search_bar.send_keys(search_value)
            self.selenium.click(selector='[tooltip-text="Submit search"]')
            time.sleep(2)
            tmp_table = createHeaderDict(user_inventory)
            for row in tmp_table[search_col][1:]:
                if not search_value.lower() in row.text.lower():
                    logger.error("the value we searched {} is not in the row text {}".format(search_value, row.text))
                    return False
            self.selenium.click(selector='[tooltip-text="Clear search"]')
            logger.info("Results are completely verified for this search.")
            time.sleep(2)
        return True

    def invite_new_user(self, user, role="Administrator"):
        # click the plus button to add a new user
        logger.info("Invite new user: {}".format(user))
        self.selenium.click(selector='[icon="add"]')
        new_user_page = self.selenium.findSingleCSS(selector=".new-user-page", timeout=5)
        if not new_user_page:
            logger.error("Cannot find the new user page")
            return False
        user_name = self.selenium.findSingleCSS(selector='[name="username"][type="email"]')
        user_name.click()
        user_name.send_keys(user)
        self.selenium.click(selector=".new-user-page .md-select-value")
        role_options = self.selenium.findMultiCSSNoHover(selector='[ng-value="roleOption"]')
        for role_option in role_options:
            if role_option.text == role:
                role_option.click()
                break
        self.selenium.click(selector=".new-user-page .zing-button-blue")
        if not self.selenium.findSingleCSS(selector=".invite-status", timeout=5):
            logger.error("Unable to invite new user")
            return False
        self.selenium.click(selector=".zing-cancel-button")
        return user

    def register_invited_user(self, user):
        invited_user_page = self.selenium.findSingleCSS(selector='[name="inviteUserAccounts"]')
        invited_user_data = createHeaderDict(invited_user_page)
        for i in range(len(invited_user_data["Email (Username)"])):
            if invited_user_data["Email (Username)"][i].text == user:
                href = invited_user_data["Invitation Link"][i].find_element_by_tag_name("a").get_attribute("href")
                invited_user_data["Invitation Link"][i].find_element_by_tag_name("a").click()
                self.selenium.driver.switch_to.window(self.selenium.driver.window_handles[1])

                # Deal with the wrong link failure
                if env["tenantid"] == 'qa-automation':
                    href = href.replace("qa-automation", "testing", 1)
                    self.selenium.getURL(href)
                break

        if not self.selenium.findSingleCSS(selector=".onboarding-page"):
            logging.error("Unable to find on boarding page of registering")
            return False

        self.selenium.click(selector='[aria-hidden="false"] > .zing-button', timeout=5)

        if not self._fill_in_profile_info():
            logger.info("This account {} may have been registered before. Go to Login page directly".format(user))
        assert self._relogin_with_registered_account(user)

        self.selenium.driver.close()
        self.selenium.driver.switch_to.window(self.selenium.driver.window_handles[0])
        return True

    def delete_new_user(self, user):
        """
        This function is supposed to execute when the page reaches user account page
        :param user:
        :return:
        """
        user_inventory = self.selenium.findSingleCSS(selector=".zing-table-tenantAccounts")
        inventory_data = createHeaderDict(user_inventory)
        for i in range(len(inventory_data["Email (Username)"])):
            if inventory_data["Email (Username)"][i].text == user:
                self.selenium.findMultiCSS(selector=".ui-grid-cell-contents svg")[i - 1].click()
                self.selenium.findSingleCSS(selector='[name="tenantAccounts"] .filter-bar')
                self.selenium.click(selector=".selected-action .dp36")
                self.selenium.click(selector='[name="delete user"]', timeout=5)
                waitLoadProgressDone(self.selenium)
                break
        inventory_data = createHeaderDict(user_inventory)
        for i in range(len(inventory_data["Email (Username)"])):
            if inventory_data["Email (Username)"][i].text == user:
                return False
        return True





























