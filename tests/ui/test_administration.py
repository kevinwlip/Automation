#!/usr/bin/python
import sys
import os
import pytest

try:
    zbathome = os.environ['ZBAT_HOME']
except:
    print('Test cannot run.  Please export ZBAT_HOME.')
    sys.exit()

if zbathome + 'lib' not in sys.path:
    sys.path.append(zbathome + 'lib')

from ui.administration.zbUIAdministration import Administration
from ui.administration.user_accounts.zbUIAdminUserAccounts import UserAccounts
from ui.administration.zbUIAdminNotifications import Notifications
from ui.administration.zbUIMyInspectors import SitesAndInspectors
from ui.administration.zbUIReportConfigurations import ReportConfig
from ui.administration.zbUIAuditLog import AuditLog
from ui.administration.zbUILicence import License
from common.zbCommon import rerunIfFail
from ui.administration.zbUIActiveProbing import ActiveProbe
from common.zbConfig import NUMBER_RETRIES, DELAY_SECONDS, SCREENSHOT_ON_FAIL

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
def notification_browser(browser_factory, administration_browser):
    browser = browser_factory(Notifications,
                              custom_payload={"selenium": administration_browser.selenium},
                              single_br=False)
    return browser["selenium"]


@pytest.fixture(scope="module")
def my_inspector_browser(browser_factory, administration_browser):
    browser = browser_factory(SitesAndInspectors,
                              custom_payload={"selenium": administration_browser.selenium},
                              single_br=False)
    return browser["selenium"]


@pytest.fixture(scope="module")
def active_probing_browser(browser_factory, administration_browser):
    browser = browser_factory(ActiveProbe,
                              custom_payload={"selenium": administration_browser.selenium},
                              single_br=False)
    return browser["selenium"]


@pytest.fixture(scope="module")
def report_configuration_browser(browser_factory, administration_browser):
    browser = browser_factory(ReportConfig,
                              custom_payload={"selenium": administration_browser.selenium},
                              single_br=False)
    return browser["selenium"]


@pytest.fixture(scope="module")
def audit_log_browser(browser_factory, administration_browser):
    browser = browser_factory(AuditLog,
                              custom_payload={"selenium": administration_browser.selenium},
                              single_br=False)
    return browser["selenium"]


@pytest.fixture(scope="module")
def license_browser(browser_factory, administration_browser):
    browser = browser_factory(License,
                              custom_payload={"selenium": administration_browser.selenium},
                              single_br=False)
    return browser["selenium"]


class TestAdministration:
    @pytest.mark.parametrize("testid",["C357128"])
    @pytest.mark.regression
    def test_inspector(self, testid, my_inspector_browser):
        assert rerunIfFail(function=my_inspector_browser.regInspectors(),
                           selenium=my_inspector_browser.selenium,
                           screenshot=SCREENSHOT_ON_FAIL,
                           testname=zbathome + 'artifacts/test_Administration.png',
                           number=NUMBER_RETRIES,
                           delay=DELAY_SECONDS)

    @pytest.mark.parametrize("testid",["C362794"])
    @pytest.mark.regression
    def test_active_probing_regression(self, testid, active_probing_browser):
        assert rerunIfFail(function=active_probing_browser.reg_active_probing(),
                           selenium=active_probing_browser.selenium,
                           screenshot=SCREENSHOT_ON_FAIL,
                           testname=zbathome + 'artifacts/test_Administration.png',
                           number=NUMBER_RETRIES,
                           delay=DELAY_SECONDS)

    @pytest.mark.parametrize("testid",["C362792"])
    @pytest.mark.regression
    def test_auditlog_regression(self, testid, audit_log_browser):
        assert rerunIfFail(function=audit_log_browser.reg_audit_log(),
                           selenium=audit_log_browser.selenium,
                           screenshot=SCREENSHOT_ON_FAIL,
                           testname=zbathome + 'artifacts/test_Administration.png',
                           number=NUMBER_RETRIES,
                           delay=DELAY_SECONDS)

    # User Account Page
    @pytest.mark.smoke
    @pytest.mark.parametrize("testid", ["C357129"])
    def test_admin_settings(self, testid, user_account_browser):
        assert rerunIfFail(function=user_account_browser.check_admin_settings(),
                           selenium=user_account_browser.selenium,
                           screenshot=SCREENSHOT_ON_FAIL,
                           testname=zbathome + 'artifacts/test_Administration.png',
                           number=NUMBER_RETRIES,
                           delay=DELAY_SECONDS)

    @pytest.mark.smoke
    @pytest.mark.parametrize("testid", ["C357130"])
    def test_user_accounts(self, testid, user_account_browser):
        assert rerunIfFail(function=user_account_browser.check_user_accounts(),
                           selenium=user_account_browser.selenium,
                           screenshot=SCREENSHOT_ON_FAIL,
                           testname=zbathome + 'artifacts/test_Administration.png',
                           number=NUMBER_RETRIES,
                           delay=DELAY_SECONDS)

    @pytest.mark.smoke
    @pytest.mark.parametrize("testid", ["C357134"])
    def test_invited_user_accounts(self, testid, user_account_browser):
        assert rerunIfFail(function=user_account_browser.check_invited_user_accounts(),
                           selenium=user_account_browser.selenium,
                           screenshot=SCREENSHOT_ON_FAIL,
                           testname=zbathome + 'artifacts/test_Administration.png',
                           number=NUMBER_RETRIES,
                           delay=DELAY_SECONDS)

    # Notification Page
    @pytest.mark.smoke
    @pytest.mark.parametrize("testid", ["C362997"])
    def test_notification_smoke(self, testid, notification_browser):
        assert rerunIfFail(function=notification_browser.check_notification_setting(),
                           selenium=notification_browser.selenium,
                           screenshot=SCREENSHOT_ON_FAIL,
                           testname=zbathome + 'artifacts/test_Administration.png',
                           number=NUMBER_RETRIES,
                           delay=DELAY_SECONDS)

    @pytest.mark.regression
    @pytest.mark.parametrize("testid", ["C363020"])
    def test_notification_regression(self, testid, notification_browser):
        assert rerunIfFail(function=notification_browser.reg_notification_setting(),
                           selenium=notification_browser.selenium,
                           screenshot=SCREENSHOT_ON_FAIL,
                           testname=zbathome + 'artifacts/test_Administration.png',
                           number=NUMBER_RETRIES,
                           delay=DELAY_SECONDS)

    @pytest.mark.smoke
    @pytest.mark.parametrize("testid", ["C362998"])
    def test_site_items(self, testid, my_inspector_browser):
        assert rerunIfFail(function=my_inspector_browser.check_sites_inventory(),
                           selenium=my_inspector_browser.selenium,
                           screenshot=SCREENSHOT_ON_FAIL,
                           testname=zbathome + 'artifacts/test_Administration.png',
                           number=NUMBER_RETRIES,
                           delay=DELAY_SECONDS)

    #Active Browser Page
    @pytest.mark.smoke
    @pytest.mark.parametrize("testid", ["C362999"])
    def test_active_probing(self, testid, active_probing_browser):
        assert rerunIfFail(function=active_probing_browser.check_active_probing(),
                           selenium=active_probing_browser.selenium,
                           screenshot=SCREENSHOT_ON_FAIL,
                           testname=zbathome + 'artifacts/test_Administration.png',
                           number=NUMBER_RETRIES,
                           delay=DELAY_SECONDS)

    # Report Config Page
    @pytest.mark.smoke
    @pytest.mark.parametrize("testid", ["C363016"])
    def test_report_config_history(self, testid, report_configuration_browser):
        assert rerunIfFail(function=report_configuration_browser.check_report_config_history(),
                           selenium=report_configuration_browser.selenium,
                           screenshot=SCREENSHOT_ON_FAIL,
                           testname=zbathome + 'artifacts/test_Administration.png',
                           number=NUMBER_RETRIES,
                           delay=DELAY_SECONDS)

    # Audit Log Page
    @pytest.mark.smoke
    @pytest.mark.parametrize("testid", ["C363017"])
    def test_audit_log(self, testid, audit_log_browser):
        assert rerunIfFail(function=audit_log_browser.check_audit_log(),
                           selenium=audit_log_browser.selenium,
                           screenshot=SCREENSHOT_ON_FAIL,
                           testname=zbathome + 'artifacts/test_Administration.png',
                           number=NUMBER_RETRIES,
                           delay=DELAY_SECONDS)

    # License Page
    @pytest.mark.parametrize("testid",["C362795"])
    @pytest.mark.smoke
    def test_license_page(self, testid, license_browser):
        assert rerunIfFail(function=license_browser.check_license_page(),
                           selenium=license_browser.selenium,
                           screenshot=SCREENSHOT_ON_FAIL,
                           testname=zbathome + 'artifacts/test_Administration.png',
                           number=NUMBER_RETRIES,
                           delay=DELAY_SECONDS)

    # EULA page
    @pytest.mark.parametrize("testid",["C362796"])
    @pytest.mark.smoke
    def test_EULA_page(self, testid, license_browser):
        assert rerunIfFail(function=license_browser.check_EULA_page(),
                           selenium=license_browser.selenium,
                           screenshot=SCREENSHOT_ON_FAIL,
                           testname=zbathome + 'artifacts/test_Administration.png',
                           number=NUMBER_RETRIES,
                           delay=DELAY_SECONDS)

    # Privacy Policy Page
    @pytest.mark.parametrize("testid",["C363018"])
    @pytest.mark.smoke
    def test_private_policy_page(self, testid, license_browser):
        assert rerunIfFail(function=license_browser.check_private_policy_page(),
                           selenium=license_browser.selenium,
                           screenshot=SCREENSHOT_ON_FAIL,
                           testname=zbathome + 'artifacts/test_Administration.png',
                           number=NUMBER_RETRIES,
                           delay=DELAY_SECONDS)
