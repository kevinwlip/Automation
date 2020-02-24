#!/usr/bin/python

import pdb, time, collections, warnings, re
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import StaleElementReferenceException, NoSuchElementException
from urllib.parse import urlparse
import operator
from datetime import datetime
from locator.devices import DeviceLocators
from common.zbCommon import isValidIPv4Address, isValidMACAddress
from locator.navigator import UISharedLoc
from locator.profiles import ProfileLoc
import selenium.common.exceptions as selexcept
from selenium.webdriver.support.wait import WebDriverWait
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def unclick_all_checkboxes(browserobj):
    if not browserobj.click(selector=UISharedLoc.CSS_SELECTOR_VIEW_COLUMN):
        return False

    unchecked_boxes = browserobj.findMultiCSS(selector=UISharedLoc.CSS_SELECTOR_VIEW_COLUMN_UNCHECKED_CHECKBOX, timeout=3)
    if unchecked_boxes:
        for e in unchecked_boxes:
            e.click()

    browserobj.click(selector=UISharedLoc.CSS_SELECTOR_VIEW_COLUMN, timeout=3)

def clickEachAlertTimerange(browserobj, specific=False):
    params = {}
    params["waittype"] = "clickable"
    params["selector"] = UISharedLoc.CSS_ALERT_DATE_SELECTOR
    rcode = browserobj.click(**params)
    params["selector"] = UISharedLoc.CSS_ALERT_DATE_ENTRIES
    rcode = browserobj.findMultiCSS(**params)
    if specific:
        rcode = browserobj.findMultiCSS(**params)[ UISharedLoc.CSS_ALERT_ENTRY_TEXT[specific] ]
        rcode.click()
        waitLoadProgressDone(browserobj)
        return True
        #yield {"pass":True, "time":specific} if rcode else {"pass":False, "time":specific}
    else:
        for key, value in UISharedLoc.CSS_ALERT_ENTRY_TEXT.items():
            rcode = browserobj.findMultiCSS(**params)[UISharedLoc.CSS_ALERT_ENTRY_TEXT[key]]
            rcode.click()
            waitLoadProgressDone(browserobj)

def clickEachAlertCategory(browserobj, specific=False):
    params = {}
    params["waittype"] = "clickable"
    params["selector"] = UISharedLoc.CSS_ALERT_CATEGORY_SELECTOR
    rcode = browserobj.click(**params)
    params["selector"] = UISharedLoc.CSS_ALERT_CATEGORY_ENTRIES
    rcode = browserobj.findMultiCSS(**params)
    if specific:
        rcode = browserobj.findMultiCSS(**params)[UISharedLoc.CSS_ALERT_ENTRY_CATE[specific]]
        rcode.click()
        waitLoadProgressDone(browserobj)
        return True
        #yield {"pass":True, "time":specific} if rcode else {"pass":False, "time":specific}
    else:
        for key, value in UISharedLoc.CSS_ALERT_ENTRY_CATE.items():
            rcode = browserobj.findMultiCSS(**params)[ UISharedLoc.CSS_ALERT_ENTRY_CATE[key] ]
            rcode.click()
            waitLoadProgressDone(browserobj)


def clickEachDashboardTimerange(browserobj, specific=False):
    ''' Click through Dashboard time range and yield back webdriverobj'''
    params = {}
    params["waittype"] = "clickable"
    if type(specific) == str:
        params["selector"] = UISharedLoc.CSS_DROPDOWN_TIMERANGE_BUTTON
        rcode = browserobj.click(**params)
        params["selector"] = UISharedLoc.CSS_DROPDOWN_TIMERANGE[specific]
        rcode = browserobj.click(**params)
        yield {"pass": True, "time": specific} if rcode else {"pass": False, "time": specific}
    elif type(specific) == list:
        for time_key in specific:
            params["selector"] = UISharedLoc.CSS_DROPDOWN_TIMERANGE_BUTTON
            rcode = browserobj.click(**params)              
            params["selector"] = UISharedLoc.CSS_DROPDOWN_TIMERANGE[time_key]
            rcode = browserobj.click(**params)
            yield {"pass": True, "time": time_key} if rcode else {"pass": False, "time": time_key}
    else:
        for key, cssValue in UISharedLoc.CSS_DROPDOWN_TIMERANGE.items():
            params["selector"] = UISharedLoc.CSS_DROPDOWN_TIMERANGE_BUTTON
            browserobj.click(**params)
            params["selector"] = cssValue
            rcode = browserobj.click(**params)
            yield {"pass": True, "time": key} if rcode else {"pass": False, "time": key}


def clickEachTimerange(browserobj, specific=False):
    """
    This generator function will choose the time ranges specified by specific parameter in the global
    filter, and yield the result to where it is called.

    :param browserobj:
    :param specific: a list of time ranges that should be clicked as this generator goes.
    :return: it generates an iterator and only executes the code when the iterator is called.
    """

    # First, click the global filter to select time
    browserobj.scroll_to_top_page()
    if not browserobj.findSingleCSS(selector=UISharedLoc.CSS_CLICK_TO_SELECT_TIME):
        logger.error('Cannot click to change time range on device page')
        yield False
    else:
        # if not specified in specific parameter, time_options should contain
        # all time ranges as key, and their related index in WebDriver element list as value;
        # else, time options only contains time range determined by specific
        time_options = {'2 Hours': 0,
                        '1 Day': 1,
                        '1 Week': 2,
                        '1 Month': 3,
                        '1 Year': 4,
                        'All to Date': 5}

        # specific param:: customize the time options
        time_keys_to_delete = []
        if type(specific) == str or type(specific) == list:
            for time_key in time_options:
                if time_key not in specific:
                    time_keys_to_delete.append(time_key)
            for time_key in time_keys_to_delete:
                del time_options[time_key]

        for time_key, time_index in time_options.items():
            logger.info('Start checking time series of time range: ' + time_key)
            browserobj.scroll_to_top_page()
            browserobj.click(selector=UISharedLoc.CSS_CLICK_TO_SELECT_TIME)
            element_specific_time = browserobj.findMultiCSS(selector=UISharedLoc.CSS_GLOBAL_TIMERANGE)[time_index]
            text = element_specific_time.text
            if text in time_options:
                element_specific_time.click()
                yield {"pass": True, "time": text}
            else:
                yield False
            browserobj.click(selector=UISharedLoc.CSS_CLICK_TO_SELECT_TIME)  # click again to close the time range list
            logger.info('Time range of ' + text + ' is Verified')
            waitLoadProgressDone(browserobj)


def clickSpecificTimerange (browserobj, specific="1 Week"):
    """
    according to the input specific parameter, looks for the buttons ranging from Two Hours to All to click.
    and click all the button given in specific paramter.

    :param browserobj:
    :param specific:
    :return: True/False
    """
    logger.info('Set up the time range: ' + specific)
    time_options = {'2 Hours': 0,
                    '1 Day': 1,
                    '1 Week': 2,
                    '1 Month': 3,
                    '1 Year': 4,
                    'All to Date': 5}
    time_index = time_options[specific]
    browserobj.scroll_to_top_page()
    browserobj.click(selector=UISharedLoc.CSS_CLICK_TO_SELECT_TIME)
    element_specific_time = browserobj.findMultiCSSNoHover(selector=UISharedLoc.CSS_GLOBAL_TIMERANGE)[time_index]
    if not element_specific_time:
        logger.error('Unable to find the time range of ' + specific)
        return False
    element_specific_time.click()
    waitLoadProgressDone(browserobj)
    browserobj.click(selector=UISharedLoc.CSS_CLICK_TO_SELECT_TIME) # To close the time option list
    return True

def verifyDataTimerange (timerange, data, strict=True, month_retention=False):
    # give margin of 85% to be a little flexible.  Sometimes test data are missing.
    margin = 0.85
    acceptable = False

    minbars = 7
    if not strict:
        if len(data) >= minbars:
            return True
        else:
            logger.error(f"Time series chart has lesser than {minbars}")
            return False

    if timerange in ["2H", "2 Hours"]:
        if 25 >= len(data) >= 23:
            return True
        if 25 >= len(data) >= int(23 * margin):
            acceptable = True
    elif timerange in ["1D", "1 Day"]:
        if 289 >= len(data) >= 287:
            return True
        if 289 >= len(data) >= int(287 * margin):
            acceptable = True
    elif timerange in ["1W", "1 Week"]:
        if 169 >= len(data) >= 167:
            return True
        if 169 >= len(data) >= int(167 * margin):
            acceptable = True
    elif timerange in ["1M", "1 Month"]:
        if 31 >= len(data) >= 30:
            return True
        if 31 >= len(data) >= int(30 * margin):
            acceptable = True
    if timerange in ["1Y", "1 Year"]:
        if 365 >= len(data) >= 290:
            return True
        if 365 >= len(data) >= int(290 * margin):
            acceptable = True
        # For certain data, we only retain 1 Month
        if month_retention:
            if 31 >= len(data) >= 30:
                return True
            if 31 >= len(data) >= int(30 * margin):
                acceptable = True
    if timerange in ["All to Date"]:
        if 365 >= len(data) >= 290:
            return True
        if 365 >= len(data) >= int(290 * margin):
            acceptable = True
        # For certain data, we only retain 1 Month
        if month_retention:
            if 31 >= len(data) >= 30:
                return True
            if 31 >= len(data) >= int(30 * margin):
                acceptable = True

    if acceptable:
        warnings.warn(UserWarning("Warning: " + timerange + " only has " + str(len(data)) + " data points."))
        return True
    else:
        print("Not enough data point for timerange {}".format(timerange))
        return False


def waitLoadProgressDone(browserobj):
    kwargs = {}
    # make sure all progress spinner done and not visible
    kwargs["selector"] = UISharedLoc.CSS_PROGRESS_SPINNER
    # kwargs["waittype"] = "invisibility"
    rcode = browserobj.findMultiCSS(hover=False, **kwargs)
    time.sleep(10)
    return True if rcode else False


def waitSeriesGraphDone(browserobj):
    '''
        Find and return all the healthy bar elements in 'Active Devices' tab in Device Inventory page.

        Even the tag is not selected, as long as the page is located at Device Inventory, these elements
        can still be found.

        :param browserobj: selenium webdriver object
        :return: all ui elements in Device Inventory Page
        '''
    kwargs = {}
    # make sure that series graph is loaded
    kwargs["selector"] = UISharedLoc.CSS_SERIES_BAR
    kwargs["waittype"] = "located"
    data = browserobj.findMultiCSS(**kwargs)
    return data if data else False


def selectSingleSite(browserobj):
    found = False
    kwargs = {}
    # first enable all sites
    kwargs["selector"] = UISharedLoc.CSS_FILTER_ALL_CARD
    browserobj.click(**kwargs)
    waitLoadProgressDone(browserobj)

    # select a single site to enable Top Device or Top Apps
    kwargs["selector"] = UISharedLoc.CSS_SITE_ALL
    sites = browserobj.findMultiCSS(**kwargs)
    for site in sites:  
        if 'LIVE' in site.text: # and 'check_circle' in site.text:
            found = True
            # looking for device count.  only select site with count greater than 10
            match = browserobj.findSingleCSS(browserobj=site,selector="[ng-bind='item.count']").text #re.search('devices\n(\d+)\n'").text
            if int(match) > 13:
                site.click()
                break
        if 'Not Deployed' in site.text:
            continue
        if '\nDEPLOY\n' in site.text and not 'NOT DEPLOYED' in site.text:
            found = True
            site.click()
            break
    
    return [sites, site] if found else False


def checkMultiSite(browserobj, url):
    # go to dashboard, if find Site tab, then it is multi site
    url = urlparse(url)
    browserobj.getURL(url.scheme+'://'+url.netloc)
    kwargs = {"selector": UISharedLoc.CSS_SITE_TAB, "waittype":"visibility", "timeout":5}
    rcode = browserobj.findSingleCSS(**kwargs)
    return rcode


def gotoBasePage(browserobj):
    #returns back to the main page
    kwargs = {"selector": UISharedLoc.CSS_SITE_TAB, "timeout":3}
    rcode = browserobj.findSingleCSS(**kwargs)
    if rcode: rcode.click()
    waitLoadProgressDone(browserobj)
    try:
        kwargs = {"selector": "[ng-click='profileSelectorCtrl.setEditMode(true);']", "timeout":3}
        rcode = browserobj.findSingleCSS(**kwargs)
        rcode.click()
    except:
        pass
    try:
        kwargs = {"selector": UISharedLoc.CSS_SHOW_ALL, "timeout":3}
        rcode = browserobj.findSingleCSS(**kwargs)
        rcode.click()
    except:
        kwargs = {"selector": UISharedLoc.CSS_CLEAR_FILTER, "timeout":3}
        rcode = browserobj.findSingleCSS(**kwargs)
        rcode.click()
    waitLoadProgressDone(browserobj)


def findTenantName(browserobj):
    kwargs = {}
    kwargs["selector"] = UISharedLoc.CSS_TENANT_NAME
    rcode = browserobj.findSingleCSS(**kwargs)
    return rcode.text if rcode else False


def resetAllDevAllSite(browserobj, specific=False):
    """
    This function will set the global filter to the required values by specifying the
    index of the options in each filter.

    Note: Time range is not selected here, but in 'clickSpecificTimeFunction' here.

    For sites:
        1 - All sites
        2 - All Connected Sites
        3 - All disconnected Sites

    For Monitored / Discovered Devices:
        1 - Monitored Devices
        2 - Discovered Devices

    For Device Types:
        1 - All Devices
        2 - All IoT
        3 - Medical IoT
        4 - Other IoT
        5 - Traditional IoT

    :param browserobj:
    :param specific: must be a list of 3 integers.
    :return:
    """
    num_selected = [1, 2, 1]
    if type(specific) is list and len(specific) is 3:
        num_selected = specific

    # check 'All Sites'
    if num_selected[0] > 0:
        browserobj.scroll_to_top_page()
        kwargs = {"selector": UISharedLoc.CSS_CLICK_TO_SELECT_SITE}
        browserobj.click(**kwargs)
        # According to UI Design, user has to click the "All Sites" first, before selecting any specific site
        browserobj.click(selector=UISharedLoc.CSS_GLOBAL_FILTER_OPTIONS.format(1))
        site_option = browserobj.findSingleCSSNoHover(selector=UISharedLoc.CSS_GLOBAL_FILTER_OPTIONS.format(num_selected[0])) #All sites
        try:
            site_option.click()
        except selexcept.ElementClickInterceptedException:
            logger.info("Potential Failure in clicking")
            pass
        time.sleep(1.5)
        browserobj.pressKey(key=Keys.ESCAPE) # to exit the selection process of sites

    # check 'Discovered Device'
    if num_selected[1] > 0:
        browserobj.scroll_to_top_page()
        kwargs = {"selector": UISharedLoc.CSS_CLICK_TO_SELECT_MONITORED}
        browserobj.click(**kwargs)
        monitor_option = browserobj.findSingleCSSNoHover(selector=UISharedLoc.CSS_GLOBAL_FILTER_OPTIONS.format(num_selected[1]))
        # we Discovered Device, instead of Monitored Device
        try:
            monitor_option.click()
        except selexcept.ElementClickInterceptedException:
            logger.info("Potential Failure in clicking")
            pass
        time.sleep(1.5)
        browserobj.pressKey(key=Keys.ESCAPE)  # to exit the selection process of sites

    # check the  'All Device'
    if num_selected[2] > 0:
        browserobj.scroll_to_top_page()
        kwargs = {"selector": UISharedLoc.CSS_CLICK_TO_SELECT_DEVICE}
        browserobj.click(**kwargs)
        device_option = browserobj.findSingleCSSNoHover(selector=UISharedLoc.CSS_GLOBAL_FILTER_OPTIONS.format(num_selected[2]))
        try:
            device_option.click()
        except selexcept.ElementClickInterceptedException:
            logger.error('Possible Failure in click device option')
            pass
        time.sleep(1.5)
        browserobj.pressKey(key=Keys.ESCAPE) # to exit the selection process of sites

    waitLoadProgressDone(browserobj)
    logger.info('Sites and Devices have been reset.')


def resetAllSite(browserobj):
    # check 'All sites'
    kwargs = {"selector": UISharedLoc.CSS_CLICK_TO_SELECT_SITE}
    browserobj.click(**kwargs)
    site_option = browserobj.findSingleCSSNoHover(selector=UISharedLoc.CSS_GLOBAL_FILTER_OPTIONS.format(1))  # All sites
    site_option.click()
    browserobj.pressKey(key=Keys.ESCAPE)  # to exit the selection process of sites

    waitLoadProgressDone(browserobj)


def disableAllSite(browserobj):

    kwargs = {"selector": UISharedLoc.CSS_DROPDOWN_BUTTON_SITE}
    browserobj.click(**kwargs)

    kwargs = {"selector": UISharedLoc.CSS_SELECTOR_SITE_ALL_ENABLE, "waittype":"visibility", "timeout":3}
    rcode = browserobj.findSingleCSS(**kwargs)
    if rcode:
        rcode.click()

    waitLoadProgressDone(browserobj)


def verify_sort_inventory_v1(browserobj, columns_not_sort=False):
    """
    This function grabs all columns listed on the Device Inventory Page, by calling zbUIShared.py::createHeaderDict.
    For every column headers listed which is not the white list, they would just be appended to hsort. Then hsort
    is sorted. (hsort is the sorted the header list to maintain a specific order when iterating through headers.
    if directly iterate over a dict, the order is unpredictable)
    Then for every header in hsort, we loop over and grab all data under each header. For each header, we click header
    to see the up arrow appears.

    Then for all the data under the same header, it should be sorted in ascending order. We check the data in different
    cases when it is empty, or date, IP address, mac address.

    Second Round for each header, we click header to see the down arrow appears. Then for all the data under the same
    header, it should be sorted in descending order. We check the data in different cases when it is empty, or date,
    IP address, mac address.

    :return: True only when all columns pass two rounds of checking order, False otherwise.
    """
    logger.info("Start Verifying Inventory Sort...")
    output = createHeaderDict(browserobj)
    if columns_not_sort:
        for col in columns_not_sort:
            del output[col]

    is_sorted = True
    for l in output.keys():
        logger.info('Sorting Column: ' + l + '...')
        waitLoadProgressDone(browserobj)
        from ui.devices.zbUIDeviceInventory import _inventory_entry_compare

        # Iterate over the up arrow button and down arrow button
        for idx, css_arrow_selector in enumerate([UISharedLoc.CSS_SORT_UP_ARROW_V1, UISharedLoc.CSS_SORT_DOWN_ARROW_V1]):
            direct = 'Up' if idx == 0 else 'Down'
            logger.info('Checking whether the sorted column is going ' + direct)
            # Click the header to see the up arrow indicating ascending order,
            # or the down arrow indicating descending order
            if not clickUntilFind(browserobj, output[l][0], css_arrow_selector):
                logger.error("Cannot find column arrow " + direct + " button, Column " + l + " failed")
                rcode = False
                continue
            waitLoadProgressDone(browserobj)

            data = output[l][1:]
            # column_sorted is the boolean flag to indicate whether column l is sorted
            column_sorted = True

            for i in range(0, len(data) - 1):
                if not _inventory_entry_compare(data[i], data[i + 1], idx, False):
                    column_sorted = False

            if column_sorted:
                logger.info('Sort ' + direct + ' Column ' + l + ' succeed')
            else:
                logger.error('Sort ' + direct + ' Column ' + l + " failed")

            # rcode remains to be true only when every column_sorted is true
            is_sorted = is_sorted and column_sorted
    return is_sorted


def clickAllCheckboxes (browserobj, must_list=UISharedLoc.must_list):
    try:
        obj = browserobj.findSingleCSS(selector=UISharedLoc.CSS_SELECTOR_VIEW_COLUMN)
        if not obj:
            logger.error('Column Selector is missing!')
            return False
        obj.click()
        obj = browserobj.findSingleCSS(selector=UISharedLoc.CSS_SELECTOR_VIEW_COLUMN_CARD)
        try:
            browserobj.hoverElement(obj)
        except Exception as e:
            logger.error(e)
            logger.info('Unable to hover, pass')
        unchecked_boxes = browserobj.findMultiCSS(selector=UISharedLoc.CSS_SELECTOR_VIEW_COLUMN_UNCHECKED_CHECKBOX, timeout=3)
        if unchecked_boxes:
            for e in unchecked_boxes:
                if e.text in must_list:
                    e.click()
        checked_boxes = browserobj.findMultiCSS(selector=UISharedLoc.CSS_SELECTOR_VIEW_COLUMN_CHECKED_CHECKBOX, timeout=3)
        if checked_boxes:
            for e in checked_boxes:
                if e.text not in must_list:
                    e.click()
        browserobj.click(selector=UISharedLoc.CSS_SELECTOR_VIEW_COLUMN, timeout=3)
    except Exception as e:
        logger.error('Unable to click all specified columns: ' + str(e))
        return False
    return True

def clickAllCheckboxesExper (browserobj, must_list=UISharedLoc.must_list):
    try:
        obj = browserobj.findSingleCSS(selector=UISharedLoc.CSS_SELECTOR_VIEW_COLUMN_EXPER)
        if not obj:
            logger.error('Column Selector is missing!')
            return False
        obj.click()
        obj = browserobj.findSingleCSS(selector=UISharedLoc.CSS_SELECTOR_VIEW_COLUMN_CARD)
        try:
            browserobj.hoverElement(obj)
        except Exception as e:
            logger.error(e)
            logger.info('Unable to hover, pass')
        chkboxes = browserobj.findMultiCSSNoHover(selector=UISharedLoc.CSS_SELECTOR_VIEW_COLUMN_CHECKBOX_NEW, timeout=3)
        cheked_boxes = browserobj.findMultiCSSNoHover(selector=UISharedLoc.CSS_SELECTOR_VIEW_COLUMN_CHECKBOX_NEW, timeout=3)
        if chkboxes:
            for e in chkboxes:
                if e.text in must_list and e not in cheked_boxes:
                    e.click()
        browserobj.click(selector=UISharedLoc.CSS_SELECTOR_VIEW_COLUMN, timeout=3)
    except Exception as e:
        logger.error('Unable to click all specified columns: ' + str(e))
        return False
    return True


def verify_inventory_top(browserobj):
    if not browserobj.findSingleCSS(selector=UISharedLoc.CSS_INVENTORY_SEARCH_ICON):
        logger.error('Search icon is missing!')
        return False

    if not browserobj.findSingleCSS(selector=UISharedLoc.CSS_SELECTOR_VIEW_COLUMN):
        logger.error('Column Selector is missing!')
        return False

    if not browserobj.findSingleCSS(selector=UISharedLoc.CSS_FROM_TO_TIMERANGE):
        logger.error('Date Range is missing')
        return False
    logger.info('Traffic Series has been verified! ')
    return True


def clickAndVerifyColumns(browserobj, verify_list):
    logger.info("Click all checkboxes of the column card...")
    # click some of the columns
    if not clickAllCheckboxes(browserobj, must_list=verify_list):
        logger.info('Unable to click all columns')
        return False

    logger.info("Reset the column card to default...")
    # click reset to default
    view_col = browserobj.findSingleCSS(selector=UISharedLoc.CSS_SELECTOR_VIEW_COLUMN)
    if not view_col:
        logger.error('Column Selector is missing!')
        return False
    view_col.click()
    assert browserobj.click(selector='[name="Reset default columns"]', timeout=2)
    view_col.click()

    waitLoadProgressDone(browserobj)
    output = createHeaderDict(browserobj)
    for key in verify_list:
        if key not in output:
            logger.error('Not showing expected column header: ' + key)
            return False
    logging.info('Column Headers pass the check')
    return True


def verifyDevicesCount(browserobj):
    params = {}
    params["selector"] = UISharedLoc.CSS_SELECTOR_ALL_DEVICES_BUTTONS
    for e in browserobj.findMultiCSS(**params):
        e.click()
        waitLoadProgressDone(browserobj)
        params["selector"] = UISharedLoc.CSS_SELECTOR_ALL_DEVICES_NUMBER1
        r1 = browserobj.findSingleCSS(**params).text
        params["selector"] = UISharedLoc.CSS_SELECTOR_ALL_DEVICES_NUMBER2
        r2 = browserobj.findSingleCSS(**params).text
        r2 = r2[r2.find("(")+1:r2.find(")")]
        params["selector"] = UISharedLoc.CSS_SELECTOR_ALL_DEVICES_NUMBER3
        r3 = browserobj.findSingleCSS(**params).text
        r3 = r3[r3.find("of ")+3:]
        if r1 != r2:
            logger.error(f"Device count mismatch. Total show {str(r1)}. List show {str(r2)}. Page count show {str(r3)}")
            return False
    params["selector"] = UISharedLoc.CSS_SELECTOR_IOT_DEVICES_MENU_ENTRY
    for e in browserobj.findMultiCSS(**params):
        params["selector"] = UISharedLoc.CSS_SELECTOR_IOT_DEVICES_MENU
        browserobj.click(**params)
        temp = {}
        temp["selector"] = UISharedLoc.CSS_SELECTOR_IOT_DEVICES_MENU_ENTRY
        temp["waittype"] = 'clickable'
        browserobj.waitCSS(**temp)
        e.click()
        waitLoadProgressDone(browserobj)
        params["selector"] = UISharedLoc.CSS_SELECTOR_ALL_DEVICES_NUMBER1
        r1 = browserobj.findSingleCSS(**params).text
        params["selector"] = UISharedLoc.CSS_SELECTOR_ALL_DEVICES_NUMBER2
        r2 = browserobj.findSingleCSS(**params).text
        r2 = r2[r2.find("(")+1:r2.find(")")]
        params["selector"] = UISharedLoc.CSS_SELECTOR_ALL_DEVICES_NUMBER3
        r3 = browserobj.findSingleCSS(**params).text
        r3 = r3[r3.find("of ")+3:]
        if r1 != r2:
            logger.error(f"Device count mismatch. Total show {str(r1)}. List show {str(r2)}. Page count show {str(r3)}")
            return False
    return True


def verifyDevicesCountExist (browserobj):
    ''' For page like IoT Profiles page, the number just have to exist, but doesn't have to match up'''
    params = {}
    params["selector"] = UISharedLoc.CSS_SELECTOR_ALL_DEVICES_BUTTONS
    for e in browserobj.findMultiCSS(**params):
        e.click()
        waitLoadProgressDone(browserobj)
        params["selector"] = UISharedLoc.CSS_SELECTOR_ALL_DEVICES_NUMBER1
        r1 = browserobj.findSingleCSS(**params).text
        params["selector"] = UISharedLoc.CSS_SELECTOR_ALL_DEVICES_NUMBER2
        r2 = browserobj.findSingleCSS(**params).text
        r2 = r2[r2.find("(")+1:r2.find(")")]
        params["selector"] = UISharedLoc.CSS_SELECTOR_ALL_DEVICES_NUMBER3
        r3 = browserobj.findSingleCSS(**params).text
        r3 = r3[r3.find("of ")+3:]
        if not r1 or not r2 or not r3:
            logger.error(f"Device count mismatch. Total show {str(r1)}. List show {str(r2)}. Page count show {str(r3)}")
            return False
    params["selector"] = UISharedLoc.CSS_SELECTOR_IOT_DEVICES_MENU_ENTRY
    for e in browserobj.findMultiCSS(**params):
        params["selector"] = UISharedLoc.CSS_SELECTOR_IOT_DEVICES_MENU
        browserobj.click(**params)
        temp = {}
        temp["selector"] = UISharedLoc.CSS_SELECTOR_IOT_DEVICES_MENU_ENTRY
        temp["waittype"] = 'clickable'
        browserobj.waitCSS(**temp)
        e.click()
        waitLoadProgressDone(browserobj)
        params["selector"] = UISharedLoc.CSS_SELECTOR_ALL_DEVICES_NUMBER1
        r1 = browserobj.findSingleCSS(**params).text
        params["selector"] = UISharedLoc.CSS_SELECTOR_ALL_DEVICES_NUMBER2
        r2 = browserobj.findSingleCSS(**params).text
        r2 = r2[r2.find("(")+1:r2.find(")")]
        params["selector"] = UISharedLoc.CSS_SELECTOR_ALL_DEVICES_NUMBER3
        r3 = browserobj.findSingleCSS(**params).text
        r3 = r3[r3.find("of ")+3:]
        if not r1 or not r2 or not r3:
            logger.error(f"Device count mismatch. Total show {str(r1)}. List show {str(r2)}. Page count show {str(r3)}")
            return False
    return True


def verifyNetworkTraffic(browserobj):
    params = {}
    params["selector"] = UISharedLoc.CSS_SELECTOR_BLUE_NUMBER
    for e in browserobj.findMultiCSS(**params):
        if not re.search(r'\d', e.text):
            return False
    params["selector"] = UISharedLoc.CSS_SELECTOR_TOTAL_DATA
    if not re.search(r'\d',browserobj.findSingleCSS(**params).text):
        return False
    params["selector"] = UISharedLoc.CSS_SELECTOR_ENCRYPTED_PERCENTAGE
    if not re.search(r'\d',browserobj.findSingleCSS(**params).text):
        return False
    return True


def clickUntilFind(browserobj, elemobj, findcss, selector=DeviceLocators.CSS_INVENTORY_HEADER, idx=0):
    """
    This function is to click the column header element, which is elemobj, until the findcss element is found.
    Due to the possibility that once elemobj is clicked, it will be refreshed and the DOM replace it with a new
    UI element, we need to let the elemobj assigend with the updated selection by browserobj.findMultiCSS(), too.

    :param browserobj:
    :param elemobj:
    :param findcss:
    :param selector:
    :param idx:
    :return: return the lastest version of elemobj, which are the latest one to be attached to the DOM tree.
    """
    for i in range(5):
        try:
            elemobj.click()
        except selexcept.StaleElementReferenceException:
            elemobj = browserobj.findMultiCSSNoHover(selector=selector)[idx]
            elemobj.click()
        except Exception as e:
            logger.error(str(e))
            logger.error("Unable to click the headers and get the arrow")
            return False
        time.sleep(3)
        params = {"selector": findcss, "timeout": 10, "waittype": "located"}
        if browserobj.findSingleCSS(**params):
            return browserobj.findMultiCSSNoHover(selector=selector)[idx]

    return False


def verifyLinkToAppDetail(browserobj, csslink):
    '''Follow app link to app detail and verify the correct name'''
    kwargs = {"selector": csslink, "waittype": "visibility"}
    rcode = browserobj.findSingleCSS(**kwargs)
    appname1 = rcode.text.strip()
    rcode.click()

    if not rcode:
        logger.error(f"Application {str(appname1)} link to app detail does not work.")
        return False
    else:
        kwargs = {"selector": UISharedLoc.CSS_APP_DETAIL_NAME, "waittype": "visibility"}
        rcode = browserobj.findSingleCSS(**kwargs)
        appname2 = rcode.text.strip()
        if appname1 == appname2:
            waitLoadProgressDone(browserobj)
            browserobj.goBack()
            return True
        else:
            logger.error(f"Application {str(appname1)} link to app detail has mismatch names {str(appname2)}")
            return False


def clickEachSite (browserobj):
    disableAllSite(browserobj)
    params = {}
    temp = {}
    temp['waittype'] = 'clickable'
    temp['timeout'] = 3
    params["selector"] = UISharedLoc.CSS_SELECTOR_SITE_DROPDOWN_UNSELECTED_OPTIONS
    rcode = browserobj.findSingleCSS(**params)
    if rcode: rcode.click()
    for e in browserobj.findMultiCSS(**params):
        params["selector"] = UISharedLoc.CSS_SELECTOR_SITE_DROPDOWN
        browserobj.click(**params)
        temp['selector'] = UISharedLoc.CSS_SELECTOR_SITE_DROPDOWN_UNSELECTED_OPTIONS
        browserobj.click(**temp)
        rcode = waitLoadProgressDone(browserobj)
        yield rcode


def clickEachDevicesButton (browserobj):
    params = {}
    params["selector"] = UISharedLoc.CSS_SELECTOR_ALL_DEVICES_BUTTONS
    for e in browserobj.findMultiCSS(**params):
        e.click()
        rcode = waitLoadProgressDone(browserobj)
        yield rcode
    params["selector"] = UISharedLoc.CSS_SELECTOR_IOT_DEVICES_MENU_ENTRY
    for e in browserobj.findMultiCSS(**params):
        params["selector"] = UISharedLoc.CSS_SELECTOR_IOT_DEVICES_MENU
        browserobj.click(**params)
        temp = {}
        temp["selector"] = UISharedLoc.CSS_SELECTOR_IOT_DEVICES_MENU_ENTRY
        temp["waittype"] = 'clickable'
        browserobj.waitCSS(**temp)
        e.click()
        rcode = waitLoadProgressDone(browserobj)
        yield rcode


def verifyTableSort (browserobj, cssColumnSortable, datetimeFormat="%Y/%m/%d, %H:%M"):
    clickAllCheckboxes(browserobj)

    params = {}
    params["selector"] = UISharedLoc.CSS_SELECTOR_CLICKABLE_SORT_HEADER
    hsort = browserobj.findMultiCSS(err_msg='UISharedLoc.CSS_SELECTOR_CLICKABLE_SORT_HEADER', **params)
    for l in cssColumnSortable:
        # click column header until head ascending order
        if not clickUntilFind(browserobj, hsort[ord(l)-ord("A")], UISharedLoc.CSS_SORT_UP_ARROW):
            logger.error("Cannot find column up arrow button")
            return False

        params = {}
        params["selector"] = UISharedLoc.CSS_SELECTOR_GENERAL_TEXT_ENTRY + l
        data = browserobj.findMultiCSS(err_msg='UISharedLoc.CSS_SELECTOR_GENERAL_TEXT_ENTRY', **params)
        for i in range(0,len(data)-1):
            if data[i].text == '' or data[i+1].text == '':
                # values are not necessary present.  If so, no need to compare
                continue
            try:
                if datetime.strptime(data[i].text, datetimeFormat) > datetime.strptime(data[i+1].text, datetimeFormat):
                    return False
                continue # if datetime parsing does not throw error, it is a date. No need to do int and str comparison
            except:
                pass
            try:
                if int(data[i].text) > int(data[i+1].text):
                    logger.error(f"Sort order not correct for {data[i+1].text} and {data[i].text}")
                    return False
            except ValueError:
                if data[i].text.lower() > data[i+1].text.lower():
                    logger.error(f"Sort order not correct for {data[i+1].text} and {data[i].text}")
                    return False

        # click column header until head descending order
        if not clickUntilFind(browserobj, hsort[ord(l)-ord("A")], UISharedLoc.CSS_SORT_DOWN_ARROW):
            logger.error("Cannot find column up arrow button")
            return False

        params = {}
        params["selector"] = UISharedLoc.CSS_SELECTOR_GENERAL_TEXT_ENTRY + l
        data = browserobj.findMultiCSS(err_msg='UISharedLoc.CSS_SELECTOR_GENERAL_TEXT_ENTRY'+l, **params)
        for i in range(0,len(data)-1):
            if data[i].text == '' or data[i+1].text == '':
                # values are not necessary present.  If so, no need to compare
                continue
            try:
                if datetime.strptime(data[i].text, datetimeFormat) < datetime.strptime(data[i+1].text, datetimeFormat):
                    return False
                continue # if datetime parsing does not throw error, it is a date. No need to do int and str comparison
            except:
                pass
            try:
                if int(data[i].text) < int(data[i+1].text):
                    logger.error(f"Sort order not correct for {data[i+1].text} and {data[i].text}")
                    return False
            except ValueError:
                if data[i].text.lower() < data[i+1].text.lower():
                    logger.error(f"Sort order not correct for {data[i+1].text} and {data[i].text}")
                    return False
    return True


def verifyTableEntries (browserobj, rows=None):
    if not rows:
        rows = browserobj.findMultiCSS(selector=DeviceLocators.CSS_SELECTOR_DEVICE_ROW_ELEMENTS)
        if not rows:
            logger.info('No data is found below the Table, Pass')
            return True
        rows = len(rows) / 2
        logger.info('On this page row number is: ' + str(rows))
        waitLoadProgressDone(browserobj)

    # check to see if each text columns have the correct amount of cells
    headers = browserobj.findMultiCSS(selector=UISharedLoc.CSS_DEVICE_INVENTORY_HEADERS)
    cnt = 0
    for head in headers:
        cnt = cnt + 1
        text = str(head.get_attribute('id'))
        m = re.search('-0...', text)
        if m:
            currentID = m.group(0)
        else:
            logger.info("Error: Oh no, the columns are inaccurate, again")
            return False
        elements = browserobj.findMultiCSS(selector=".ui-grid-coluiGrid" + currentID)

        if not elements or len(elements) - 1 != rows:
            logger.error('Fail to identify Column: ' + head.text)
            return False
        logger.info('Column {} in this table is verified'.format(cnt))
    return True

def verifyTableEntriesExper(browserobj, rows=None):
    if not rows:
        rows = browserobj.findMultiCSS(selector=DeviceLocators.CSS_SELECTOR_DEVICE_ROW_ELEMENTS)
        if not rows:
            logger.info('No data is found below the Table, Pass')
            return True
        rows = len(rows)
        logger.info('On this page row number is: ' + str(rows))
        waitLoadProgressDone(browserobj)

    # check to see if each text columns have the correct amount of cells
    headers = browserobj.findMultiCSS(selector=".ag-header-cell")
    cnt = 0
    for head in headers:
        cnt = cnt + 1
        text = str(head.get_attribute('col-id'))
        if text:
            currentID = text
        else:
            logger.info("Error: Oh no, the columns are inaccurate, again")
            return False
        elements = browserobj.findMultiCSS(selector="[col-id=" + currentID + "]")

        if not elements or len(elements) - 1 != rows:
            logger.error('Fail to identify Column: ' + head.text)
            return False
        logger.info('Column {} in this table is verified'.format(cnt))
    return True



def validateSortOrder(sortingType, data):
    op = operator.gt
    if sortingType == 'descending':
        op = operator.lt

    for i in range(0,len(data)-1):
        if data[i].text == '' or data[i+1].text == '':
            # values are not necessary present.  If so, no need to compare
            continue

        topData = data[i].text
        bottomData = data[i + 1].text
        if isinstance(topData, int) or isinstance(topData, float):
            if op(int(topData), int(bottomData)):
                raise ValueError("Sort {} got value error {}   {}".format(sortingType, topData, bottomData))
        elif isinstance(topData, str) or isinstance(topData, str):
            topData = topData.encode('ascii','ignore')
            try:
                if op(datetime.strptime(topData, "%b %d, %Y, %H:%M"), datetime.strptime(bottomData, "%b %d, %Y, %H:%M")):
                    raise Exception("Sort {} datetime out of order {}   {}".format(sortingType, topData, bottomData))
                else:
                    return True
                if op(datetime.strptime(topData, "%b %d, %Y"), datetime.strptime(bottomData, "%b %d, %Y")):
                    raise Exception("Sort {} datetime out of order {}   {}".format(sortingType, topData, bottomData))
                else:
                    return True
            except ValueError:
                if op(data[i].text.lower(), data[i+1].text.lower()):
                    raise ValueError("Sort {} got value error {}   {}".format(sortingType, topData, bottomData))
                else:
                    return True
            except Exception as e:
                raise ValueError(e)

def selectOTDashboardCategory(browserobj, category):
    data = browserobj.findMultiCSS(selector=UISharedLoc.CSS_OT_CATEGORY_BUTTONS, timeout=3)
    if data:
        for cat in data:
            if category in cat.text:
                cat.click()
                time.sleep(1)
                waitLoadProgressDone(browserobj)
                return True
    return False

def setDeviceDetailTab(browserobj, text):
    choices = browserobj.findMultiCSS(selector=UISharedLoc.CSS_GRAPH_TAB_OPTIONS)
    if text == "Alerts":
        choices[0].click()
    elif text == "Security":
        choices[1].click()
    elif text == "Operational":
        choices[2].click()
    waitLoadProgressDone(browserobj)


def createHeaderDict(browserobj):
    """
    This function finds all column headers of device inventory. With the id contained in the header element,
    we can get the CSS selector of all cells under that column.

    :param browserobj:
    :return: returns a dict with keys to be the column header, and values to be all cell UI elements under that column.
    """
    output = {}
    try:
        headers = browserobj.find_elements_by_css_selector(UISharedLoc.CSS_DEVICE_INVENTORY_HEADERS)
    except AttributeError:
        headers = browserobj.findMultiCSS(selector=UISharedLoc.CSS_DEVICE_INVENTORY_HEADERS)
    for head in headers:
        output[head.text.strip()] = head
    prog = re.compile(r"-0...")
    for head in output:
        id_string = output[head].get_attribute("id")
        column_id = (prog.search(id_string)).group(0)
        custom_selector = UISharedLoc.CSS_DEVICE_INVENTORY_DATA_BLANK + column_id
        try:
            output[head] = browserobj.find_elements_by_css_selector(custom_selector)
        except AttributeError:
            output[head] = browserobj.findMultiCSS(selector=custom_selector)

    if '' in output:
        del output['']
    return output

def checkElement(ele, css):
    assert ele, "Element {} NOT FOUND".format(css)

def checkElementText(ele, css, match):
    checkElement(ele, css)
    assert ele.text.lower() == match, "element text does not match: got {}, should be {}".format(ele.text, match)

class checkFactory(object):
    def __init__(self, browserobj, **kwargs):
        self.check_list = []
        self.selenium = browserobj
        self.check_scope = kwargs["check_scope"] if "check_scope" in kwargs else browserobj.driver

    def add_to_checklist(self, **kwargs):
        """
        This function will continuously add the CSS selectors of UI elements into self.check_list. Once check_all
        function is called, the function will check all elements in the check_list.

        'text' in kwargs: the expected text within the UI element specified by the CSS selector.
        'element_name' in kwargs: will be used in logger files to address the specified UI element.

        :param kwargs:
        :return: the intance itself
        """
        if "css" in kwargs and "element_name" in kwargs:
            self.check_list.append(kwargs)
        return self

    def check_all(self):
        for item in self.check_list:
            ui_element = self.selenium.findSingleCSS(selector=item["css"],
                                                     browserobj=self.check_scope,
                                                     timeout=item["timeout"] if "timeout" in item else 3)
            if not ui_element:
                logger.error("Unable to find " + item["element_name"])
                return False
            if "text" in item and item["text"] not in ui_element.text:
                logger.error("text is not matched: expected text: " + item["text"])
                return False
            logger.info('The element of {} is verified'.format(item["element_name"]))
        return True

    def clear_all(self):
        self.check_list.clear()

