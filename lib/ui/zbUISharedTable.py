#This library supports all functions related to V2 Inventory Table

from locator.profiles import ProfileLoc
from locator.devices import DeviceLocators
import ui.zbUIShared as UIShared_v1
import selenium.common.exceptions as selexcept
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
import pdb
import logging
import time

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def click_all_checkbox(browserobj, must_list, view_col=ProfileLoc.CSS_VIEW_COLUMN):
    obj = browserobj.findSingleCSS(selector=view_col)
    assert obj, "Column Selector is missing"
    browserobj.click(selector=view_col, timeout=0)
    column_searching_bar = browserobj.findSingleCSS(selector=".zt-search-bar")
    assert column_searching_bar, "Not showing column searching bar"
    try:
        browserobj.hoverElement(column_searching_bar)
    except selexcept.ElementClickInterceptedException as e:
        logger.error(str(e))
        logger.info('Unable to hover on the column padding card, pass')
    boxes = browserobj.findMultiCSS(selector=ProfileLoc.CSS_VIEW_COLUMN_CARD_BOXES)
    # we should not use "waittype='visible'" here, as for this CSS
    if boxes:
        try:
            for box in boxes:
                if box.text in must_list:
                    if box.find_element_by_tag_name("input").get_attribute("aria-checked") == 'false':
                        box.click()
                elif box.find_element_by_tag_name("input").get_attribute("aria-checked") == 'true':
                    box.click()
        except Exception as e:
            logger.error(str(e))
            logger.error('Unable to click all unchecked boxes in must_list')
            return False
    # The following step is for scrolling the page and making the column selection card disappear
    browserobj.findSingleCSS(selector=DeviceLocators.CSS_DEVICE_ENTRY_POINT)
    UIShared_v1.waitLoadProgressDone(browserobj)
    return True


def create_header_dict(browserobj):
    """
    This function returns a dictionary with the keys to be the column headers, and
    the values to be all UI elements under the column headers.

    Note: since in V2 inventory, the columns are loaded dynamically only when it is in view, we cannot grab
    every column header all at once by calling browserobj.findMultiCSS(selector=ProfileLoc.CSS_INVENTORY_HEADER).
    If we want to ensure we grab all columns, we should make total columns less than 8 by clicking less columns
    during column clicking and selecting, so all columns to show will be shown on the page with no need to scroll
    left or right.

    :param browserobj:
    :return:
    """
    num = len(browserobj.findMultiCSSNoHover(selector=ProfileLoc.CSS_INVENTORY_HEADER))
    output = dict()
    for i in range(num):
        header_element = browserobj.findMultiCSSNoHover(selector=ProfileLoc.CSS_INVENTORY_HEADER)[i]
        header_name = header_element.find_element_by_class_name("customHeaderLabel").text.strip()
        header_id = header_element.get_attribute("col-id")
        if header_name != "":
            custom_selector = ProfileLoc.CSS_COLUMN_ALL_CELLS + '[col-id="{}"]'.format(header_id)
            output[header_name] = browserobj.findMultiCSSNoHover(selector=custom_selector)
    return output


def click_and_reset_to_default(browserobj, view_col=ProfileLoc.CSS_VIEW_COLUMN):
    # Deselect all checkboxes
    if not click_all_checkbox(browserobj, must_list=[], view_col=view_col):
        logger.error("Unable to deselect all boxes!")
        return False
    browserobj.click(selector=view_col, timeout=0)

    # Click reset to default button to reset the columns
    reset_to_default = browserobj.findSingleCSSNoHover(selector="a.reset-enable")
    reset_to_default.click()
    boxes = browserobj.findMultiCSS(selector=ProfileLoc.CSS_VIEW_COLUMN_CARD_BOXES)
    default_columns = []
    if boxes:
        try:
            for box in boxes:
                if box.find_element_by_tag_name("input").get_attribute("aria-checked") == 'true':
                    default_columns.append(box.find_element_by_class_name("column-display").text)
        except Exception as e:
            logger.error(str(e))
            logger.error('Unable to find all boxes checked by default')
            return False

    UIShared_v1.waitLoadProgressDone(browserobj)
    # verify all default columns are present
    output = create_header_dict(browserobj)
    for key in output:
        if key not in default_columns:
            logger.error('Showing unexpected column header: ' + key)
            return False
    logger.info("The function of reset columns is verified")
    return True


def click_and_verify_columns(browserobj, verify_list, view_col=ProfileLoc.CSS_VIEW_COLUMN):
    if not click_all_checkbox(browserobj, must_list=verify_list, view_col=view_col):
        logger.info('Unable to click all columns')
        return False
    output = create_header_dict(browserobj)
    for key in verify_list:
        if key not in output:
            logger.error('Not showing expected column header: ' + key)
            return False
    logging.info('Column Headers pass the check')
    return True


def verify_table_entries(browserobj, rows=None):
    if not rows:
        rows = browserobj.findMultiCSS(selector=ProfileLoc.CSS_TOTAL_ROWS_IN_TABLE)
        if not rows:
            logger.info('No data is found below this Table, Pass')
            return True
        rows = len(rows)
        logger.info('On this page row number is: ' + str(rows))
        UIShared_v1.waitLoadProgressDone(browserobj)

    # check to see if each text columns have the correct amount of cells
    output = create_header_dict(browserobj)
    for header in output:
        if len(output[header]) != rows:
            logger.error('Fail to identify Column: ' + header)
            return False
        logger.info('Column {} in this table is verified'.format(header))
    return True


class InventoryLocalSearch(object):
    def __init__(self, browserobj):
        """
        All functions in LocalFilter is called supposing the browser is in the page of some inventory with a search icon
        :param browserobj:
        """
        self.selenium = browserobj

    def search_by_name(self, column_val):
        try:
            self.selenium.click(selector=DeviceLocators.CSS_SEARCH_ICON)
            dialog = self.selenium.findSingleCSSNoHover(selector=DeviceLocators.CSS_SEARCH_DIALOG)
            if not dialog:
                logger.error('Unable to input the key words for searching')
                return False
            dialog.click()
            dialog.send_keys(column_val, Keys.ENTER)
            self.selenium.findSingleCSS(selector=DeviceLocators.CSS_SEARCH_TAG)
            time.sleep(1)
            logger.info("Search Operation for {} is successfully performed".format(column_val))
            return True
        except Exception as e:
            logger.error(str(e))
            logger.error("Unable to finish the search operation")
            return False

    def verify_column_name(self, column_name, column_value):
        output = create_header_dict(self.selenium)
        for value in output[column_name]:
            if value.text.strip().lower() != column_value.lower():
                logger.error("the entry with {} to be {} does not match our search: {}"
                             .format(column_name, value.text.strip(), column_value))
                return False
        logger.info('Successfully verified search results for {}'.format(column_value))
        return True

    def clear_all_search_results(self):
        search_tags_clear = self.selenium.findMultiCSS(selector=DeviceLocators.CSS_SEARCH_TAG_X)
        for tag_x in search_tags_clear:
            tag_x.click()
        time.sleep(0.2)
        return not self.selenium.findSingleCSS(selector=DeviceLocators.CSS_SEARCH_TAG_X, timeout=1)








