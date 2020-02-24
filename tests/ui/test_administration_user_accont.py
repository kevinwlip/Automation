#!/usr/bin/python
import sys
import os
import pytest
import random

try:
    zbathome = os.environ['ZBAT_HOME']
except:
    print('Test cannot run.  Please export ZBAT_HOME.')
    sys.exit()

if zbathome + 'lib' not in sys.path:
    sys.path.append(zbathome + 'lib')

from ui.administration.zbUIAdministration import Administration
from ui.administration.user_accounts.zbUIAdminUserAccounts import UserAccounts
from common.zbConfig import NUMBER_RETRIES, DELAY_SECONDS, SCREENSHOT_ON_FAIL
from common.zbCommon import rerunIfFail

# fixture
@pytest.fixture(scope="module")
def administration_browser(browser_factory):
    browser = browser_factory(Administration)
    return browser["selenium"]


@pytest.fixture(scope="module")
def user_account_browser(browser_factory, administration_browser):
    browser = browser_factory(UserAccounts,
                              custom_payload={"selenium": administration_browser.selenium},
                              single_br=False)
    return browser["selenium"]


@pytest.fixture(scope="module")
def user_name_to_invite():
    return "invited_new_user_@gmail.com"


class TestAdministrationUserAccounts:

    @pytest.mark.regression
    @pytest.mark.parametrize("testid", ["C359192"])
    def test_user_account_search(self, testid, user_account_browser):
        assert rerunIfFail(function=user_account_browser.check_user_account_search(),
                           selenium=user_account_browser.selenium,
                           screenshot=SCREENSHOT_ON_FAIL,
                           testname=zbathome + 'artifacts/test_Administration_UserAccount.png',
                           number=NUMBER_RETRIES,
                           delay=DELAY_SECONDS)


    @pytest.mark.regression
    @pytest.mark.parametrize("testid", ["C359193"])
    def test_invite_register_relogin_user(self, testid, user_account_browser, user_name_to_invite):
        assert rerunIfFail(function=user_account_browser.check_register_invited_user(user=user_name_to_invite),
                           selenium=user_account_browser.selenium,
                           screenshot=SCREENSHOT_ON_FAIL,
                           testname=zbathome + 'artifacts/test_Administration_UserAccount.png',
                           number=NUMBER_RETRIES,
                           delay=DELAY_SECONDS)

    @pytest.mark.regression
    @pytest.mark.parametrize("testid", ["C357135"])
    def test_user_account_inventory_sort(self, testid, user_account_browser):
        assert rerunIfFail(function=user_account_browser.check_user_account_inventory_sort(),
                           selenium=user_account_browser.selenium,
                           screenshot=SCREENSHOT_ON_FAIL,
                           testname=zbathome + 'artifacts/test_Administration_UserAccount.png',
                           number=NUMBER_RETRIES,
                           delay=DELAY_SECONDS)

    #@pytest.mark.regression
    @pytest.mark.parametrize("testid", ["C359378"])
    @pytest.mark.parametrize("role_name", ["Deployment", "Read only", "Owner", "Administrator"])
    def test_change_user_role(self, testid, user_account_browser, user_name_to_invite, role_name):
        assert rerunIfFail(function=user_account_browser.check_change_user_role(user_name_to_invite, role_name),
                           selenium=user_account_browser.selenium,
                           screenshot=SCREENSHOT_ON_FAIL,
                           testname=zbathome + 'artifacts/test_Administration_UserAccount.png',
                           number=NUMBER_RETRIES,
                           delay=DELAY_SECONDS)

    @pytest.mark.regression
    @pytest.mark.parametrize("testid", ["C359382"])
    @pytest.mark.parametrize("enable", [True, False])
    def test_change_user_2fa(self, testid, user_account_browser, user_name_to_invite, enable):
        assert rerunIfFail(function=user_account_browser.check_2fa_enable_for_one_account(user_name_to_invite, enable=enable),
                           selenium=user_account_browser.selenium,
                           screenshot=SCREENSHOT_ON_FAIL,
                           testname=zbathome + 'artifacts/test_Administration_UserAccount.png',
                           number=NUMBER_RETRIES,
                           delay=DELAY_SECONDS)

    @pytest.mark.regression
    @pytest.mark.parametrize("testid", ["C359380"])
    def test_delete_invited_user(self, testid, user_account_browser, user_name_to_invite):
        assert rerunIfFail(function=user_account_browser.check_delete_invited_user(user=user_name_to_invite),
                           selenium=user_account_browser.selenium,
                           screenshot=SCREENSHOT_ON_FAIL,
                           testname=zbathome + 'artifacts/test_Administration_UserAccount.png',
                           number=NUMBER_RETRIES,
                           delay=DELAY_SECONDS)

