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

from ui.profiles.zbUIProfiles import Profiles
from common.zbCommon import rerunIfFail, getHostname
from common.zbConfig import NUMBER_RETRIES, DELAY_SECONDS, SCREENSHOT_ON_FAIL

# fixture
@pytest.fixture(scope="module")
def browser(browser_factory):
    browser = browser_factory(Profiles)
    return browser["selenium"]


class TestProfiles:
    @pytest.mark.smoke
    def test_profile_inventory(self, browser):
        assert rerunIfFail(function=browser.check_profile_inventory(),
                           selenium=browser.selenium,
                           screenshot=SCREENSHOT_ON_FAIL,
                           testname=zbathome + 'artifacts/test_Profiles.png',
                           number=NUMBER_RETRIES,
                           delay=DELAY_SECONDS)
    
    @pytest.mark.smoke    
    def test_profile_acl(self, browser):
        assert rerunIfFail(function=browser.check_profile_acl(),
                           selenium=browser.selenium,
                           screenshot=SCREENSHOT_ON_FAIL,
                           testname=zbathome + 'artifacts/test_Profiles.png',
                           number=NUMBER_RETRIES,
                           delay=DELAY_SECONDS)

    @pytest.mark.smoke
    def test_profile_verify_entries(self, browser):
        assert rerunIfFail(function=browser.check_profiles_verify_entries(),
                           selenium=browser.selenium,
                           screenshot=SCREENSHOT_ON_FAIL,
                           testname=zbathome + 'artifacts/test_Profiles.png',
                           number=NUMBER_RETRIES,
                           delay=DELAY_SECONDS)

    @pytest.mark.regression
    def test_profiles_verify_entries_all_pages(self, browser):
        assert rerunIfFail(function=browser.check_profiles_verify_entries_all_pages(),
                           selenium=browser.selenium,
                           screenshot=SCREENSHOT_ON_FAIL,
                           testname=zbathome + 'artifacts/test_Profiles.png',
                           number=NUMBER_RETRIES,
                           delay=DELAY_SECONDS)

    @pytest.mark.regression
    def test_sort_and_reset_column(self, browser):
        assert rerunIfFail(function=browser.check_sort(),
                           selenium=browser.selenium,
                           screenshot=SCREENSHOT_ON_FAIL,
                           testname=zbathome + 'artifacts/test_Profiles.png',
                           number=NUMBER_RETRIES,
                           delay=DELAY_SECONDS)
        assert rerunIfFail(function=browser.check_profile_view_columns_reset(),
                           selenium=browser.selenium,
                           screenshot=SCREENSHOT_ON_FAIL,
                           testname=zbathome + 'artifacts/test_profile_view_columns_reset.png',
                           number=NUMBER_RETRIES,
                           delay=DELAY_SECONDS)

    @pytest.mark.regression
    def test_profiles_devices_link(self, browser):
        assert rerunIfFail(function=browser.check_profiles_devices_link(),
                           selenium=browser.selenium,
                           screenshot=SCREENSHOT_ON_FAIL,
                           testname=zbathome + 'artifacts/test_profiles_devices_link.png',
                           number=NUMBER_RETRIES,
                           delay=DELAY_SECONDS)
