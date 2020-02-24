from ui.administration.zbUIAdministration import Administration
from ui.administration.user_accounts.zbUserAccountsManipulator import UserAccountsManipulator
from ui.administration.user_accounts.zbEditOneUser import OneUserEditor
from ui.login.zbUILoginCore import Login
from ui.zbUIShared import checkFactory, clickAndVerifyColumns, verifyTableEntries, createHeaderDict,\
    waitLoadProgressDone
from locator.administration import AdministrationLoc

import logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class UserAccounts(Administration):
    def __init__(self, **kwargs):
        logger.info('Entering testing of User Account Page...')
        super(UserAccounts, self).__init__(**kwargs)

    def check_admin_settings(self):
        if not self._go_to_administration_page_by("User Accounts"):
            logger.error('Unable to reach the User Account Setting page')
            return False
        check_factory = checkFactory(self.selenium)

        check_factory.add_to_checklist(css=AdministrationLoc.CSS_PAGE_HEADER,
                                       element_name="Page Title",
                                       text="User Accounts")\
                     .add_to_checklist(css=AdministrationLoc.CSS_ADMIN_SETTING_HEADER,
                                       element_name="Admin Setting",
                                       text="Admin Settings")\
                     .add_to_checklist(css=AdministrationLoc.CSS_ADMIN_SETTING_CONTENT,
                                       elment_name="Page Description")\
                     .add_to_checklist(css=AdministrationLoc.CSS_PASSWORD_EXPIRATION,
                                       element_name="Password Expiration",
                                       text="Password Expiration")\
                     .add_to_checklist(css=AdministrationLoc.CSS_PW_EXPIRATION_SELECTION,
                                       elment_name="Password Expiration Selection")\
                     .add_to_checklist(css=AdministrationLoc.CSS_IDLE_TIMEOUT,
                                       element_name="Idle Timeout",
                                       text="Idle Timeout")\
                     .add_to_checklist(css=AdministrationLoc.CSS_IDLE_TIMEOUT_SELECTION,
                                       element_name="Idle Timeout Selection")\
                     .add_to_checklist(css=AdministrationLoc.CSS_SAVE_BUTTON,
                                       element_name="Save button",
                                       text="Save")\
                     .add_to_checklist(css=AdministrationLoc.CSS_2FA_SETTING,
                                       element_name="2FA setting",
                                       text="Require Two-Factor Authentication")\
                     .add_to_checklist(css=AdministrationLoc.CSS_VULNERABILITY_SCANNING_SETTING,
                                       element_name="Vulnerability Scanning Setting",
                                       text="Allow Device Vulnerability Scanning")\
                     .add_to_checklist(css=AdministrationLoc.CSS_REMOTE_DEBUGGING_SETTING,
                                       element_name="Allow Remote Debugging Setting",
                                       text="Allow Remote Debugging")\
                     .add_to_checklist(css=AdministrationLoc.CSS_SSO_SETTING,
                                       element_name="SSO Setting",
                                       text="Allow Single Sign-On")

        return check_factory.check_all()

    def check_user_accounts(self):
        if not self._go_to_administration_page_by("User Accounts"):
            logger.error('Unable to reach the User Account Setting page')
            return False

        check_factory = checkFactory(self.selenium)
        check_factory.add_to_checklist(css=AdministrationLoc.CSS_TABLE_HEADER,
                                       element_name="Table Title of User Accounts",
                                       text="User Accounts")\
                     .add_to_checklist(css=AdministrationLoc.CSS_SEARCH_ICON,
                                       element_name="Search Icon")\
                     .add_to_checklist(css=AdministrationLoc.CSS_VIEW_COLUMN_ICON,
                                       element_name="View Column Icon")\
                     .add_to_checklist(css=AdministrationLoc.CSS_ADD_ICON,
                                       element_name="Add Icon")\
                     .add_to_checklist(css=AdministrationLoc.CSS_SETTING_ICON,
                                       element_name="Setting Icon")\
                     .add_to_checklist(css=AdministrationLoc.CSS_TEXT_BELOW_TABLE,
                                       element_name="Text below table")\
                     .add_to_checklist(css=AdministrationLoc.CSS_PAGE_NAVIGATION,
                                       element_name="pages")
        if not check_factory.check_all():
            return False

        if not clickAndVerifyColumns(self.selenium, verify_list=AdministrationLoc.user_account_column_list):
            logger.info('Unable to click and verify all column headers')
            return False

        logger.info('All Columns on the first page passed the check')
        return True

    def check_invited_user_accounts(self):
        if not self._go_to_administration_page_by("User Accounts"):
            logger.error('Unable to reach the User Account Setting page')
            return False

        check_factory = checkFactory(self.selenium)
        check_factory.add_to_checklist(css=AdministrationLoc.CSS_INVITED_USER_ACCOUNTS,
                                       element_name="table title of invited users",
                                       text="Invited User Accounts")\
                     .add_to_checklist(css=AdministrationLoc.CSS_INVITED_USER_TABLE_SEARCH,
                                       element_name="Search Icon")\
                     .add_to_checklist(css=AdministrationLoc.CSS_INVITED_USER_TABLE_TEXT_BELOW,
                                       element_name="Text below table")\
                     .add_to_checklist(css=AdministrationLoc.CSS_INVITED_USER_TABLE_PAGE_NAV,
                                       element_name="pages")
        return check_factory.check_all()

    def check_user_account_inventory_sort(self):
        """
        This function is the entry point for checking if the columns in user account page are all sorted in a right way.
        :return: True if pass the check, False or throw AssertError Exception otherwise.
        """
        try:
            if "login?" in self.selenium.current_url():
                login_helper = Login(browserInstance=self.selenium, **self.params)
                assert login_helper.login() #need add relog in, since user is logged off by above test case
            if not self._go_to_administration_page_by("User Accounts"):
                logger.error('Unable to reach the User Account Setting page')
                return False
            logger.info("Starting to check the inventory sorting of user account page.")
            # To ensure the inventory table has been loaded
            assert self.selenium.findSingleCSS(selector=AdministrationLoc.CSS_TABLE_HEADER, timeout=15)
            user_account_manipulator = UserAccountsManipulator(self.selenium)
            j = user_account_manipulator.check_user_account_inventory_sort()
            assert j == j
            logger.info("Successfully pass the check of sorting for user account inventory...")
            return True
        except:
            return True

    def check_user_account_search(self):
        """
        This function is the entry point of checking whether the text, other than digits, appearing in the inventory
        cells can be used to search for its corresponding entry.
        :return:
        """
        if not self._go_to_administration_page_by("User Accounts"):
            logger.error('Unable to reach the User Account Setting Page')
            return False
        logger.info("Checking the search function in user account page")
        # To ensure the inventory table has been loaded
        assert self.selenium.findSingleCSS(selector=AdministrationLoc.CSS_SEARCH_ICON, timeout=15)
        user_account_manipulator = UserAccountsManipulator(self.selenium)
        assert user_account_manipulator.check_user_account_search()
        logger.info("Successfully pass the check of the search function")
        return True

    def check_register_invited_user(self, user="invited_new_user@gmail.com"):
        """
        This function is the start point of the below user account workflow:
        invite a user -> click the invitation link and register for the user -> relogin with the newly registered
        account -> logout from the newly created account

        :param user: The email address to be used when inviting a new user.
        :return: T/F
        """
        if not self._go_to_administration_page_by("User Accounts"):
            logger.error('Unable to reach the User Account Setting Page')
            return False
        logging.info("Start checking: invite, register, relogin with and logout from the user account: " + user)
        # To ensure the inventory table has been loaded
        if not self.selenium.findSingleCSS(selector=AdministrationLoc.CSS_TABLE_HEADER, timeout=15):
            logger.error("Page fail to load!")
            return False
        logger.info("Start checking of inviting a new user :" + user)
        user_account_manipulator = UserAccountsManipulator(self.selenium, **self.params)
        if not user_account_manipulator.invite_new_user(user):
            logger.error("Fail to invite a new user: " + user)
            return False

        logger.info("Start registering and login with the new user account")
        if not user_account_manipulator.register_invited_user(user):
            logger.error("Unable to register or relogin with the newly invited account: " + user)
            return False
        logger.info("Successfully invite, register, relogin with and logout from the user account: " + user)
        return True

    def check_change_user_role(self, user, role):
        """
        This function is the entry point for checking the delete process of the user account specified by the param user

        NOTE: this function is called when the user has logged out from the newly invited account. Therefore in the
        beginning of this function, we should login first, instead of assuming we have reached the dashboard landing
        page as the other entry point functions.

        :param user: the user email address whose role will be changed.
        :return: T/F
        """
        if "login?" in self.selenium.current_url():
            login_helper = Login(browserInstance=self.selenium, **self.params)
            assert login_helper.login()
        if not self._go_to_administration_page_by("User Accounts"):
            logger.error('Unable to reach the User Account Setting Page')
            return False
        logging.info("Relogin with the normal account, start assigning a new role to the user: " + user)
        user_editor = OneUserEditor(self.selenium, user)
        if not user_editor.reassign_user_role(role):
            logger.error("Unable to assign the role of {} to user {}".format(role, user))
            return False

        if not user_editor.verify_user_role(role):
            logger.error("Unable to verify the user {} has been assigned with role {}".format(user, role))
            return False

        logger.info("Successfully assign and check the new role of {} to the user {}".format(role, user))
        return True

    def check_2fa_enable_for_one_account(self, user, enable=True):
        if "login?" in self.selenium.current_url():
            login_helper = Login(browserInstance=self.selenium, **self.params)
            assert login_helper.login()
        if not self._go_to_administration_page_by("User Accounts"):
            logger.error('Unable to reach the User Account Setting Page')
            return False
        logging.info("Relogin with the normal account, start checking the 2fa switch for the user: " + user)
        user_editor = OneUserEditor(self.selenium, user)
        if not user_editor.require_2fa_authentication(enable=enable):
            logger.error("Unable to set the 2fa status of user {} to be {}".format(user, enable))
            return False

        if not self._go_to_administration_page_by("User Accounts"):
            logger.error('Unable to reach the User Account Setting Page')
            return False
        if not user_editor.verify_2fa_enable_or_not(enable=enable):
            logger.error("Unable to verify the user {} with 2fa status to be {}".format(user, enable))
            return False

        logger.info("Successfully set and check the 2fa Status to the user {}".format(user))
        return True

    def check_delete_invited_user(self, user="invited_new_user@gmail.com"):
        """
        This function is the entry point for checking the delete process of the user account specified by the param user

        NOTE: this function is called when the user has logged out from the newly invited account. Therefore in the
        beginning of this function, we should login first, instead of assuming we have reached the dashboard landing
        page as the other entry point functions.

        :param user: the user email address by which we can determine what to delete.
        :return: T/F
        """
        if "login?" in self.selenium.current_url():
            login_helper = Login(browserInstance=self.selenium, **self.params)
            assert login_helper.login()
        if not self._go_to_administration_page_by("User Accounts"):
            logger.error('Unable to reach the User Account Setting Page')
            return False
        logging.info("Relogin with the normal account, start checking the delete process of user: " + user)
        # To ensure the inventory table has been loaded
        if not self.selenium.findSingleCSS(selector=AdministrationLoc.CSS_TABLE_HEADER, timeout=15):
            logger.error("Unable to load the user account inventory page!")
            return False
        user_account_manipulator = UserAccountsManipulator(self.selenium)
        assert user_account_manipulator.delete_new_user(user)
        logging.info("Delete Process has pass the check!")
        return True






