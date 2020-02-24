import logging
import selenium.common.exceptions as selexcept
import re
import time
import random
from locator.navigator import UISharedLoc
from urllib.parse import urlparse
from locator.profiles import ProfileLoc
from ui.login.zbUILoginCore import Login
from ui.zbUIShared import waitLoadProgressDone, checkFactory, resetAllDevAllSite, clickSpecificTimerange
from ui.zbUISharedTable import click_and_verify_columns, verify_table_entries, \
    create_header_dict, click_and_reset_to_default
from locator.navigator import UISharedLoc
from locator.profiles import ProfileLoc
from ui.devices.zbUIDeviceInventory import verifyInventorySort
from ui.devices.zbUIDeviceUtil import LocalFilter
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class Profiles:
    def __init__(self, **kwargs):
        self.params = kwargs
        self.selenium = Login(**kwargs).login()

    def _go_to_profiles_inventory_page(self):
        curr_url = self.selenium.getCurrentURL()
        # if already get to the Profiles page, just return
        if "/guardian/monitor/profiles" in curr_url:
            logger.info('Profiles Page is reached')
            self.selenium.click(selector=ProfileLoc.CSS_TABLE_NAME)
            self.selenium.scroll_to_top_page()
            return True
        # else, redirect to that page
        self.selenium.click(selector=ProfileLoc.CSS_PROFILES_ENTRYPOINT)
        waitLoadProgressDone(self.selenium)
        if "/guardian/monitor/profiles" not in self.selenium.getCurrentURL():
            logger.error('Unable to reach the profiles page')
            return False
        logger.info('Profiles Page is reached')
        return True

    def check_profile_acl(self):
        if not self._go_to_profiles_inventory_page():
            logger.error('Unable to reach the profiles page')
            return False
        clickSpecificTimerange(self.selenium, specific="1 Month")
        rcode = self.selenium.findSingleCSS(selector=ProfileLoc.CSS_ACL_LINK)
        rcode.click()
        
        self.selenium.switchToLatestWindow()
        waitLoadProgressDone(self.selenium)
        rcode = self.selenium.findSingleCSS(selector=ProfileLoc.CSS_ACL_BREADCRUMB)
        if "ACL Rules" not in rcode.text:
            logger.error('ACL title not correct')
            return False
        rcode = self.selenium.findSingleCSS(selector=ProfileLoc.CSS_ACL_CARD_TITLE)
        if not rcode:
            logger.error("ACL Page Card title missing")
            return False
        rcode = self.selenium.findMultiCSS(selector=ProfileLoc.CSS_ACL_CARD_BLOCK)
        for rc in rcode:
            if "ACL Rule" in rc.text:
                if len(re.findall(r'\d+',rc.text)) == 0:
                    logger.error("Count missing from ACL rule block")
                    return False
            elif "Last Update" in rc.text:
                if len(re.findall(r'\d{4}',rc.text)) == 0:
                    logger.error("Date missing from ACL rule block")
                    return False
            else:
                logger.error("Label missing from ACL rule block")
        self.selenium.switchToEarliestWindow()
        waitLoadProgressDone(self.selenium)
        return True

    def check_profile_view_columns_reset(self):
        if not self._go_to_profiles_inventory_page():
            logger.error('Unable to reach the profiles page')
            return False
        logger.info('Checking the reset function in viewing column card of the profiles...')
        if not click_and_reset_to_default(self.selenium):
            logger.error('Reset to Default is not working!')
            return False
        logger.info('Reset Columns passed the check')
        return True

    def check_profile_inventory(self):
        if not self._go_to_profiles_inventory_page():
            logger.error('Unable to reach the profiles page')
            return False
        logger.info('Checking the inventory of the profiles...')
        inventory_card = self.selenium.findSingleCSS(selector=ProfileLoc.CSS_PROFILE_TABLE, waittype='visibility')
        if not inventory_card:
            logger.error('Profile Inventory is not found')
            return False

        table_title = self.selenium.findSingleCSS(selector=ProfileLoc.CSS_TABLE_NAME, waittype='visibility')
        if not table_title or 'Profiles' not in table_title.text:
            logger.error('Title of the Inventory is not Profiles!')
            return False

        if not click_and_verify_columns(self.selenium, verify_list=ProfileLoc.column_list):
            logger.info('Unable to click and verify all column headers')
            return False
        return True

    def check_profiles_verify_entries(self):
        if not self._go_to_profiles_inventory_page():
            logger.info('Unable to reach the Profile page')
            return False
        clickSpecificTimerange(self.selenium, specific="1 Month")
        logger.info('Checking the inventory entries of the profiles...')
        # check to see if each text columns have the correct amount of cells
        if not verify_table_entries(self.selenium):
            logger.error('Unable to verify all columns on the inventory page')
            return False
        check_factory = checkFactory(self.selenium)
        check_factory.add_to_checklist(css=ProfileLoc.CSS_PAGE_HEADER,
                                       element_name="Page Title",
                                       text="Profiles") \
            .add_to_checklist(css=ProfileLoc.CSS_TABLE_NAME,
                              element_name="Table Title",
                              text="Profiles") \
            .add_to_checklist(css=ProfileLoc.CSS_VIEW_COLUMN,
                              element_name="View Column Icon") \
            .add_to_checklist(css=ProfileLoc.CSS_TEXT_BELOW,
                              element_name="Text below table") \
            .add_to_checklist(css=ProfileLoc.CSS_TABLE_PAGENATION,
                              element_name="pages")
        if not check_factory.check_all():
            return False

        logger.info('All Columns on the first page passed the check')
        return True

    def check_profiles_verify_entries_all_pages(self):
        self._go_to_profiles_inventory_page()
        resetAllDevAllSite(self.selenium)
        clickSpecificTimerange(self.selenium, specific="1 Year")
        logger.info('Checking the inventory entries of the profiles on all pages')

        try:
            page_number_text = self.selenium.findSingleCSS(selector=ProfileLoc.CSS_TOTAL_PAGES).text
            page_number_text_groups = page_number_text.split()
            page_number = int(page_number_text_groups[1])
        except Exception as e:
            logger.error(str(e))
            logger.error("Cannot get the total page number")
            return False
        page_idx = 0

        while page_idx < page_number:
            logger.info('Checking Inventory Entries in PageNumber: {}'.format(page_idx + 1))
            if page_idx >= 1:
                self.selenium.click(selector=ProfileLoc.CSS_NEXT_PAGES)
                waitLoadProgressDone(self.selenium)
            page_idx = page_idx + 1

            # check to see if each text columns have the correct amount of cells
            if not verify_table_entries(self.selenium):
                logger.error('Unable to verify all columns on the inventory page')
                return False
        logger.info("Successfully verified the entries on all profile inventory pages")
        return True

    def check_sort(self):
        self._go_to_profiles_inventory_page()
        resetAllDevAllSite(self.selenium)
        clickSpecificTimerange(self.selenium, specific="1 Month")
        logger.info('Checking the sorting of columns on the profiles inventory')
        assert verifyInventorySort(self.selenium,
                                   column_list_agg=ProfileLoc.CSS_SELECTOR_DEVICE_GENERAL_SORT,
                                   case_sensitive=True)
        logger.info("Successfully verified the sorting columns on profile inventory page")
        return True

    def check_profiles_devices_link(self):
        self._go_to_profiles_inventory_page()
        clickSpecificTimerange(self.selenium, specific="1 Month")
        logger.info('Checking the link to filtered device inventory page on the profiles inventory')

        # get the entries of profiles
        output = create_header_dict(self.selenium)

        # randomly pick an entry to click and verify
        rows_num = len(output["Profile Name"])
        index = random.randint(0, rows_num - 1)
        new_filter = dict()
        new_filter["Profile"] = output["Profile Name"][index].text
        logger.info("Going to verify the link of Profile Name " + new_filter["Profile"])
        link = output["Number of Devices"][index].find_element_by_tag_name("a")
        link.click()
        waitLoadProgressDone(self.selenium)

        # verify if the local filter on device inventory page is added.
        local_filter = LocalFilter(self.selenium)
        if not local_filter.check_if_filter_added(new_filter):
            logger.error("The filter of profile name cannot be verified")
        logger.info("Successfully verified the link to filtered device inventory page")
        self._go_to_profiles_inventory_page()
        return True

    def close(self):
        if self.selenium:
            self.selenium.quit()