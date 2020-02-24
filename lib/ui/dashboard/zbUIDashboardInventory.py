'''
Author: Kevin Ip
Revision: 1/15/2020
'''

from ui.login.zbUILoginCore import Login
from urllib.parse import urlparse
from ui.zbUIShared import waitLoadProgressDone, clickSpecificTimerange, waitSeriesGraphDone, verifyDataTimerange, checkFactory
from common.zbConfig import defaultEnv
from locator.dashboard import DashboardSecurityLoc, DashboardInventoryLoc
from selenium.webdriver.common.action_chains import ActionChains
import selenium.common.exceptions as selexcept
import pdb, os, re, time

import logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

env = defaultEnv()


class DashboardInventory:
    def __init__(self, **kwargs):
        kwargs['username'] = env['superinv_username']
        kwargs['password'] = env['superinv_password']
        self.params = kwargs
        self.selenium = Login(**kwargs).login()

    def go_to_inventory_page(self):
        if '/guardian/dashboard/inventory' in self.selenium.getCurrentURL():
            logger.info('Dashboard Inventory Page is reached')
            return True
        url = urlparse(self.params["url"])
        self.selenium.getURL(url.scheme + '://' + url.netloc + '/guardian/dashboard/inventory')
        waitLoadProgressDone(self.selenium)
        clickSpecificTimerange(self.selenium, specific="1 Year")

        inventory_tab = self.selenium.findSingleCSS(selector=DashboardInventoryLoc.CSS_ACTIVE)
        if not inventory_tab or inventory_tab.text.lower() != 'inventory':
            logger.error('Unable to find Inventory Tab')
            return False
        logger.info('Dashboard Inventory Page is reached')
        return True


    def check_dashboard_inventory_devices(self):
        self.go_to_inventory_page()

        check_factory = checkFactory(self.selenium)
        check_factory.add_to_checklist(css=DashboardInventoryLoc.CSS_DEVICES_CARD_TITLE,
                                        element_name="Devices Card Title",
                                        text="Devices") \
        .add_to_checklist(css=DashboardInventoryLoc.CSS_DEVICES_PIE_OTHER_IOT,
                                        element_name="Pie Other IoT") \
        .add_to_checklist(css=DashboardInventoryLoc.CSS_DEVICES_PIE_NON_IOT,
                                        element_name="Pie Non-IoT") \
        .add_to_checklist(css=DashboardInventoryLoc.CSS_DEVICES_PIE_TITLE,
                                        element_name="Devices Pie Title",
                                        text="Device Distribution by Type") \
        .add_to_checklist(css=DashboardInventoryLoc.CSS_DEVICES_TABLE_TITLE,
                                        element_name="Devices Table Title",
                                        text="All devices") \
        .add_to_checklist(css=DashboardInventoryLoc.CSS_DEVICES_TABLE_HEADER1,
                                        element_name="Devices Table Header 1",
                                        text="Type") \
        .add_to_checklist(css=DashboardInventoryLoc.CSS_DEVICES_TABLE_HEADER2,
                                        element_name="Devices Table Header 2",
                                        text="Devices") \
        .add_to_checklist(css=DashboardInventoryLoc.CSS_DEVICES_TABLE_HEADER3,
                                        element_name="Devices Table Header 3",
                                        text="Categories") \
        .add_to_checklist(css=DashboardInventoryLoc.CSS_DEVICES_TABLE_HEADER4,
                                        element_name="Devices Table Header 4",
                                        text="Profiles") \
        .add_to_checklist(css=DashboardInventoryLoc.CSS_DEVICES_TABLE_HEADER5,
                                        element_name="Devices Table Header 5",
                                        text="Devices at Risk") \
        .add_to_checklist(css=DashboardInventoryLoc.CSS_DEVICES_TABLE_TYPE1,
                                        element_name="Devices Table Type 1",
                                        text="Traditional IT") \
        .add_to_checklist(css=DashboardInventoryLoc.CSS_DEVICES_TABLE_TYPE2,
                                        element_name="Devices Table Type 2",
                                        text="Other IoT") \
        .add_to_checklist(css=DashboardInventoryLoc.CSS_DEVICES_TABLE_TYPE3,
                                        element_name="Devices Table Type 3",
                                        text="Medical IoT") \
        .add_to_checklist(css=DashboardInventoryLoc.CSS_DEVICES_TABLE_PAGINATION_LABEL,
                                        element_name="Devices Table Pagination Label") \
        .add_to_checklist(css=DashboardInventoryLoc.CSS_DEVICES_TABLE_PREVIOUS_PAGE,
                                        element_name="Devices Table Previous Page") \
        .add_to_checklist(css=DashboardInventoryLoc.CSS_DEVICES_TABLE_NEXT_PAGE,
                                        element_name="Devices Table Next Page") \

        if not check_factory.check_all():
            return False

        data_values = []
        values1 = self.selenium.findMultiCSSNoHover(selector=DashboardInventoryLoc.CSS_DEVICES_TABLE_COL_VALUES1)
        values2 = self.selenium.findMultiCSSNoHover(selector=DashboardInventoryLoc.CSS_DEVICES_TABLE_COL_VALUES2)
        values3 = self.selenium.findMultiCSSNoHover(selector=DashboardInventoryLoc.CSS_DEVICES_TABLE_COL_VALUES3)
        values4 = self.selenium.findMultiCSSNoHover(selector=DashboardInventoryLoc.CSS_DEVICES_TABLE_COL_VALUES4)

        for (i, j, k, l) in zip(values1, values2, values3, values4):
            data_values.append(i.text)
            data_values.append(j.text)
            data_values.append(k.text)
            data_values.append(l.text)

        if all(x == '0' for x in data_values) or len(data_values) == 0:
            logger.info('All values in the data should not all be 0 and values should exist')
            return False

        logger.info('All Items in the Dashboard Inventory Device card passed the check')
        return True


    def check_dashboard_inventory_device_categories(self):
        self.go_to_inventory_page()

        check_factory = checkFactory(self.selenium)
        check_factory.add_to_checklist(css=DashboardInventoryLoc.CSS_DEVICE_CATEGORIES_CARD_TITLE,
                                        element_name="Devices Categories Card Title",
                                        text="Device Categories") \
        .add_to_checklist(css=DashboardInventoryLoc.CSS_DEVICE_CATEGORIES_SORTING,
                                        element_name="Card Sorting",
                                        text="Risk Score") \
        .add_to_checklist(css=DashboardInventoryLoc.CSS_DEVICE_CATEGORIES_EXPAND,
                                        element_name="Card Expand") \
        .add_to_checklist(css=DashboardInventoryLoc.CSS_DEVICE_CATEGORIES_SHOW_MORE,
                                        element_name="Card Show More") \

        if not check_factory.check_all():
            return False

        show_more = self.selenium.findSingleCSS(selector=DashboardInventoryLoc.CSS_DEVICE_CATEGORIES_SHOW_MORE)
        show_more.click()
        pdb.set_trace()
        device_category_title = self.selenium.findSingleCSS(selector=DashboardInventoryLoc.CSS_DEVICE_CATEGORIES_CARD_TITLE)
        device_category_title_number = int(re.search(r'(\d+)', device_category_title.text).group())
        device_category_images = self.selenium.findMultiCSSNoHover(selector=DashboardInventoryLoc.CSS_DEVICES_CATEGORY_IMAGES)
        device_category_image_number = len(device_category_images)
        device_category_names = self.selenium.findMultiCSSNoHover(selector=DashboardInventoryLoc.CSS_DEVICES_CATEGORY_NAMES)
        device_category_name_number = len(device_category_names)
        if device_category_title_number not in {device_category_image_number, device_category_name_number}:
            logger.info('The number in the title of the section should match the number of images and names')
            return False

        device_category_subtitles = self.selenium.findMultiCSSNoHover(selector=DashboardInventoryLoc.CSS_DEVICES_CATEGORY_SUBTITLES)
        device_category_devices_subtitles = device_category_subtitles[0::2]
        device_category_profiles_subtitles = device_category_subtitles[1::2]
        device_category_risk_score_subtitles = self.selenium.findMultiCSSNoHover(selector=DashboardInventoryLoc.CSS_DEVICES_CATEGORY_RISK_SCORE_SUBTITLES)
        device_category_total_devices = self.selenium.findMultiCSSNoHover(selector=DashboardInventoryLoc.CSS_DEVICES_CATEGORY_TOTAL_DEVICES)
        device_category_total_profiles = self.selenium.findMultiCSSNoHover(selector=DashboardInventoryLoc.CSS_DEVICES_CATEGORY_TOTAL_PROFILES)
        device_category_total_risk_scores = self.selenium.findMultiCSSNoHover(selector=DashboardInventoryLoc.CSS_DEVICES_CATEGORY_TOTAL_RISK_SCORES)
        device_category_total_risk_icons = self.selenium.findMultiCSSNoHover(selector=DashboardInventoryLoc.CSS_DEVICES_CATEGORY_TOTAL_RISK_ICONS)

        logger.info('All Items in the Dashboard Inventory Device Categories card passed the check')
        return True


    def check_dashboard_inventory_subnets(self):
        self.go_to_inventory_page()

        subnet_title = self.selenium.findMultiCSSNoHover(selector=DashboardInventoryLoc.CSS_SUBNETS_CARD_TITLE)
        if "subnets" not in subnet_title[2].text.lower():
            logger.info('"Subnet" should be in the title')
            return False
        subnet_title_number = int(re.search(r'(\d+)', subnet_title[2].text).group())
        # Need to write a check here to compare the number later

        # pdb.set_trace()
        subnet_legends = self.selenium.findMultiCSSNoHover(selector=DashboardInventoryLoc.CSS_SUBNETS_CARD_LEGENDS)
        legend_values = {"medical iot", "other iot", "traditional it"}.difference({subnet_legends[0].text.lower(), subnet_legends[1].text.lower(), subnet_legends[2].text.lower()})
        if legend_values != set():
            logger.info('The set should be empty, there should be no difference in values')
            return False

        logger.info('All Items in the Dashboard Inventory Subnets card passed the check')
        return True
        # pdb.set_trace()



    def close(self):
        if self.selenium:
            self.selenium.quit()
