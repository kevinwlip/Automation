from ui.login.zbUILoginCore import Login
from ui.zbUIShared import waitLoadProgressDone, checkFactory, clickSpecificTimerange
from ui.devices.zbUIDeviceInventory import verifyInventorySort
from ui.devices.zbUIDeviceUtil import LocalFilter
from ui.zbUISharedTable import click_and_verify_columns, verify_table_entries, \
    click_and_reset_to_default, create_header_dict

from locator.navigator import UISharedLoc
from locator.application import ApplicationLoc
from locator.profiles import ProfileLoc

import random
import re, pdb
import time
import logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class Applications:
    def __init__(self, **kwargs):
        self.params = kwargs
        self.selenium = Login(**kwargs).login()

    def _go_to_applications_inventory_page(self):
        curr_url = self.selenium.getCurrentURL()
        # if already get to applications page, just return
        if "/guardian/monitor/newapplications" in curr_url:
            self.selenium.click(selector=ApplicationLoc.CSS_TABLE_NAME)
            self.selenium.scroll_to_top_page()
            logger.info('Application Page is reached')
            return True
        # else, click the nav bar to go to the applications page
        self.selenium.click(selector=ApplicationLoc.CSS_APPLICATION_ENTRYPOINT)
        waitLoadProgressDone(self.selenium)
        if "/guardian/monitor/newapplications" not in self.selenium.getCurrentURL():
            logger.error('Unable to reach the application page')
            return False
        logger.info('Application Page is reached')
        return True

    def _go_to_profiles_inventory_page(self):
        curr_url = self.selenium.getCurrentURL()
        # else, click the nav bar to go to the applications page
        self.selenium.click(selector="[data-title='Profiles']")
        waitLoadProgressDone(self.selenium)
        logger.info('Profiles Page is reached')
        return True

    def check_application_verify_headers(self):
        if not self._go_to_applications_inventory_page():
            logger.error('Unable to reach the Application page')
            return False
        logger.info('Checking the inventory headers of the applications...')
        inventory_card = self.selenium.findSingleCSS(selector=ApplicationLoc.CSS_APPLICATION_TABLE, waittype='visibility')
        if not inventory_card:
            logger.error('Application Inventory is not found')
            return False

        table_title = self.selenium.findSingleCSS(selector=ApplicationLoc.CSS_TABLE_NAME, waittype='visibility')
        if not table_title or 'Applications' not in table_title.text:
            logger.error('Title of the Applications Inventory is not Found!')
            return False

        if not click_and_verify_columns(self.selenium, verify_list=ApplicationLoc.column_list,
                                        view_col=ApplicationLoc.CSS_VIEW_COLUMN):
            logger.info('Unable to click and verify all column headers')
            return False
        return True

    def check_application_verify_entries(self):
        if not self._go_to_applications_inventory_page():
            logger.info('Unable to reach the Application page')
            return False
        logger.info('Checking the inventory entries of the applications...')
        # check to see if each text columns have the correct amount of cells
        if not verify_table_entries(self.selenium):
            logger.error('Unable to verify all columns on the inventory page')
            return False
        check_factory = checkFactory(self.selenium)
        check_factory.add_to_checklist(css=ApplicationLoc.CSS_PAGE_HEADER,
                                       element_name="Page Title",
                                       text="Applications")\
            .add_to_checklist(css=ApplicationLoc.CSS_APPLICATION_TABLE,
                              element_name="Table Title",
                              text="Applications")\
            .add_to_checklist(css=ApplicationLoc.CSS_SEARCH_ICON,
                              element_name="Search Icon")\
            .add_to_checklist(css=ApplicationLoc.CSS_VIEW_COLUMN,
                              element_name="View Column Icon")\
            .add_to_checklist(css=ApplicationLoc.CSS_TEXT_BELOW,
                              element_name="Text below table")\
            .add_to_checklist(css=ApplicationLoc.CSS_TABLE_PAGENATION,
                              element_name="pages")
        assert check_factory.check_all()
        logger.info('All Columns on the first page passed the check')
        return True

    def check_application_view_columns_reset(self):
        if not self._go_to_applications_inventory_page():
            logger.error('Unable to reach the applications page')
            return False
        logger.info('Checking the reset function in viewing column card of the applications...')
        if not click_and_reset_to_default(self.selenium):
            logger.error('Reset to Default is not working!')
            return False
        logger.info('Reset Columns passed the check')
        return True

    def check_applications_verify_entries_all_pages(self):
        self._go_to_applications_inventory_page()
        clickSpecificTimerange(self.selenium, specific="1 Year")
        logger.info('Checking the inventory entries of the applications on all pages')

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
        logger.info("Successfully verified the entries on all application inventory pages")
        return True

    def check_sort(self):
        self._go_to_applications_inventory_page()
        clickSpecificTimerange(self.selenium, specific="1 Month")
        logger.info('Checking the sorting of columns on the applications inventory')
        assert verifyInventorySort(self.selenium,
                                   column_list_agg=ApplicationLoc.CSS_SELECTOR_DEVICE_GENERAL_SORT,
                                   case_sensitive=True)
        logger.info("Successfully verified the sorting columns on applications inventory page")
        return True

    def check_applications_devices_link(self):
        self._go_to_applications_inventory_page()
        clickSpecificTimerange(self.selenium, specific="1 Month")
        logger.info('Checking the link to filtered device inventory page on the applications inventory')

        # get the entries of applications
        output = create_header_dict(self.selenium)

        # randomly pick an entry to click and verify
        rows_num = len(output["Application"])
        index = random.randint(0, rows_num - 1)
        new_filter = dict()
        new_filter["Applications"] = output["Application"][index].text
        logger.info("Going to verify the link of Application: " + new_filter["Applications"])
        link = output["Used by Devices"][index].find_element_by_tag_name("a")
        link.click()
        waitLoadProgressDone(self.selenium)

        # verify if the local filter on device inventory page is added.
        local_filter = LocalFilter(self.selenium)
        if not local_filter.check_if_filter_added(new_filter):
            logger.error("The filter of Applications cannot be verified")
        logger.info("Successfully verified the link to filtered device inventory page")
        self._go_to_applications_inventory_page()
        return True

    def check_profiles_entry_and_search(self):
        self._go_to_applications_inventory_page()
        clickSpecificTimerange(self.selenium, specific="1 Month")
        logger.info('Checking the profiles cell on the applications inventory')

        # get the entries of applications
        output = create_header_dict(self.selenium)
        profile_cells = output["Profiles"]
        for profile_cell in profile_cells:
            profile_link = self.selenium.findSingleCSS(browserobj=profile_cell, selector=".zing-link")
            if not self.selenium.findSingleCSSNoHover(selector="div.dialog.list-tooltip", timeout=2):
                logger.error("Unable to find the tooltip when mouse hovers")
                return False
            profile_link.click()
            time.sleep(3)  # wait some time for dialog background to fade away.
            dialog_window = self.selenium.findSingleCSSNoHover(selector=".cdk-overlay-pane mat-dialog-container", timeout=2)
            if not dialog_window:
                logger.error("Unable to find the dialog window after clicking")
                return False

            title = self.selenium.findSingleCSSNoHover(selector=".dialog-card .zt-title", timeout=2)
            m = re.search('([0-9]+)', title.text)
            profile_num = 0
            if m:
                total_num = m.group(0)
                profile_num = int(total_num.strip('()'))
            profiles = self.selenium.findMultiCSSNoHover(selector=".main-content .zt-list-item")
            assert profile_num == len(profiles)
            if profile_num > 0 and not self._verify_search(profiles):
                logger.info("The output pass the check")
                return False
        logger.info("The output pass the check")
        return True

    def _verify_search(self, profiles):
        search_dict = dict()
        for pf in profiles[0:3]:
            pf_words = pf.text.split()
            for word in pf_words:
                search_dict[word] = [pf] if word not in search_dict else search_dict[word].append(pf)

        for keyword in search_dict:
            input = self.selenium.findSingleCSS(selector='input[placeholder="Search profiles"]')
            input.clear()
            input.send_keys(keyword)
            time.sleep(2)
            if not len(self.selenium.findMultiCSSNoHover(selector=".zt-list-item")) == len(search_dict[keyword]):
                logger.error("Bad searching result: " + keyword)
                return False
        self.selenium.click(selector=".mat-button.primary")
        return True

    def close(self):
        if self.selenium:
            self.selenium.quit()