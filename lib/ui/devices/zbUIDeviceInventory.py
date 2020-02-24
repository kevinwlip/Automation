#!/usr/bin/python
from urllib.parse import urlparse
from ui.login.zbUILoginCore import Login
from ui.zbUIShared import clickSpecificTimerange, clickUntilFind, waitLoadProgressDone, clickAllCheckboxes, \
    clickEachTimerange, waitSeriesGraphDone, verifyDataTimerange, verifyDevicesCount, resetAllDevAllSite, \
    verifyTableEntries, createHeaderDict, clickAllCheckboxesExper, verifyTableEntriesExper, checkFactory
from ui.zbUISharedTable import click_and_verify_columns, click_all_checkbox, create_header_dict, InventoryLocalSearch, \
    verify_table_entries, click_and_reset_to_default
from locator.devices import DeviceLocators
from locator.navigator import *
from common.zbCommon import convertByte, convertIP, REGEX_UI_DATA_PATTERN
from datetime import datetime
from selenium.webdriver.support.wait import WebDriverWait
import time, re, glob, os, pdb
from common.zbSelenium import get_downloaded_files, get_file_content
from selenium.webdriver.common.keys import Keys
import selenium.common.exceptions as selexcept
import base64

from ui.devices.zbUIDeviceUtil import LocalFilter, DeviceDataGenerator, DeviceTooltip

import logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def verifyLinkToDeviceDetail(browserobj, csslink):
    '''Follow a device link to device detail and verify the correct name'''
    kwargs = {"selector": csslink, "waittype": "visibility"}
    rcode = browserobj.findSingleCSS(**kwargs)

    if not rcode:
        logging.info("Devices link to device detail is not found.")
        return False
    devname1 = rcode.text.strip()
    try:
        rcode.click()
    except selexcept.ElementClickInterceptedException:
        logger.error('Possible Failure to click the Device Detail Link')
        pass
    waitLoadProgressDone(browserobj)

    # look for device name in device detail page
    kwargs = {"selector": UISharedLoc.CSS_DEVICE_DETAIL_NAME, "waittype": "visibility", "timeout":15}
    rcode = browserobj.findSingleCSS(**kwargs)

    if not rcode:
        # try another option
        kwargs = {"selector": UISharedLoc.CSS_DEVICE_DETAIL_NAME2, "waittype": "visibility", "timeout":5}
        rcode = browserobj.findSingleCSS(**kwargs)
    if not rcode:
        logger.error('Unable to find the name of the device in device detail page!')
        return False

    devname2 = rcode.text.strip()
    if devname1[:12] == devname2[:12]:
        return True
    elif (isValidMACAddress(devname1) or isValidIPv4Address(devname1)) and devname2 == "unknown":
        # check if devname is MAC address or IPv4, if that's the case, then Hostname can be labeled as "unknown"
        return True
    elif '...' in devname1:
        if devname1.replace('...', '').strip() not in devname2:
            logging.error("Devices " + str(devname1) + " link to device detail has mismatch names "+str(devname2))
            return False
    else:
        logging.error("Devices " + str(devname1) + " link to device detail has mismatch names " + str(devname2))
        return False

def verifyInventoryEntries(browserobj, page_number=0, verifyAll=True):
    """
    This functions checks the checkboxes which are on the UISharedLoc::must_list and have been checked,
    then verify if

        the number of rows in tables
        == the number of rows of 'status'
        == the number of rows for 'risk' icons .
        == the number of rows for each column appearing on this page.

    It checks the cells for each column, by selecting CSS_SELECTOR_GENERAL_TEXT_ENTRY, to see if the total number of
    the cells == rows.

    :param page_number: specify the pages to be verified. if it is 0, then verify all pages available.
    :param verifyAll: if veryfyAll, then click all unchecked boxes in the must_list
    :return: True if the number matches, False otherwise.
    """
    if verifyAll:
        logger.info('Verifying all columns available')
        if not click_all_checkbox(browserobj, UISharedLoc.must_list):
            logger.info('Unable to click all columns and present them on the page')
            return False
    params = {}
    if page_number == 0:
        try:
            page_number_text = browserobj.findSingleCSS(selector=".paginator-right-element").text
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
            browserobj.click(selector=".zt-next-page-button")
            waitLoadProgressDone(browserobj)
        page_idx = page_idx + 1

        # check number of all rows in this inventory table
        params["selector"] = DeviceLocators.CSS_SELECTOR_DEVICE_ROW_ELEMENTS
        rows = len(browserobj.findMultiCSSNoHover(**params))
        logger.info('On this page row number is: ' + str(rows))

        # check number of all status cell icons in this table
        params["selector"] = DeviceLocators.CSS_SELECTOR_STATUS_CELL_ICON
        rcode = len(browserobj.findMultiCSSNoHover(**params))
        if rcode != rows:
            logger.error("Failed Status Icon: " + str(rcode) + " found | " + "Rows:" + str(rows))
            return False
        logger.info('On this page, status cell icons pass the test')

        # check number of all risk icons in this inventory table
        params["selector"] = DeviceLocators.CSS_SELECTOR_RISK_LEVEL_ICON
        rcode = len(browserobj.findMultiCSSNoHover(**params))
        if rcode != rows:
            logger.error("Failed Risk Level Icon: " + str(rcode) + " found")
            return False
        logger.info('On this page, risk level icons pass the test')

        # check to see if each text columns have the correct amount of cells
        if not verify_table_entries(browserobj, rows=rows):
            logger.error('Unable to verify all columns on the inventory page')
            return False
    return True


def get_number_of_devices(browserobj):
    inventory_title = browserobj.findSingleCSS(selector=DeviceLocators.CSS_TABLE_NAME)
    if not inventory_title:
        logger.error("No device inventory title is found!")
        return False
    browserobj.click(selector=DeviceLocators.CSS_TABLE_NAME)
    title_text = inventory_title.text
    try:
        m = re.search('([0-9]+)', title_text)
        if m:
            total_num = m.group(0)
            return int(total_num.strip('()'))
    except Exception as e:
        logger.error(str(e))
        return -1


def _compare_tooltip_against_table(browserobj):
    # First, process the table
    check_table = dict()
    has_next_page = True
    while has_next_page:
        rows = browserobj.findMultiCSS(selector=DeviceLocators.CSS_PIE_TABLE_ROW)
        for row in rows:
            try:
                name = row.find_element_by_class_name("mat-column-name").text
                device_num = int(row.find_element_by_class_name("mat-column-devices").text.replace(',', ''))
                check_table[name] = device_num
            except:
                logger.error('Fail to get the table data')
                return False
        next_page = browserobj.findSingleCSSNoHover(selector=DeviceLocators.CSS_PIE_GRAPH_NEXTPAGE)
        has_next_page = not next_page.get_attribute("disabled")
        if has_next_page:
            next_page.click()

    # second, hover on each pie section to check the tooltips
    pie_sections = browserobj.findMultiCSS(selector=DeviceLocators.CSS_PIE_GRAPH_PIE_SECTION)
    for pie in pie_sections:
        pie_sections = browserobj.findMultiCSS(selector=DeviceLocators.CSS_PIE_GRAPH_PIE_SECTION)
        browserobj.hoverElement(pie)
        try:
            tooltip = browserobj.findSingleCSSNoHover(selector=DeviceLocators.CSS_PIE_HOVER_TOOLTIP)
            if not tooltip:
                logger.info("Unable to hover on the Pie section, continue")
                continue
            tooltip = tooltip.text
            info_list = tooltip.split(':', 1)
            name = info_list[0].strip()
            num = int(info_list[1].strip())
            assert check_table[name] == num
        except selexcept.StaleElementReferenceException as e:
            logger.error(str(e))
            logger.error('Tooltip has been expired')
            return False
        except Exception as e:
            logger.error(str(e))
            logger.error('Unable to get the name and device number on the tooltip ')
            return False
    logger.info("Statistics on the right check table is the same as the left pie graph.")
    return True


def _recursive_verifying_device_type(browserobj, device_hierarchy, pie_section):
    logger.info("On Device Hierarchy: " + device_hierarchy)
    try:
        pie_section.click()
    except selexcept.ElementClickInterceptedException as e:
        logger.info("Unable to click, pass instead")
        pass
    except Exception as e:
        logger.error(str(e))
        return False
    waitLoadProgressDone(browserobj)
    updated_device_hierarchy = browserobj.findSingleCSS(selector=DeviceLocators.CSS_PIE_GRAPH_INDEX)
    if not updated_device_hierarchy:
        logger.error("Cannot find the text of updated device hierarchy")
        return False
    updated_device_hierarchy = updated_device_hierarchy.text
    # Base case of the Recursion
    if updated_device_hierarchy == device_hierarchy:
        return True

    # Check if all pie sections has the same data with the table.
    assert _compare_tooltip_against_table(browserobj)
    logger.info("Statistics on the right check table is the same as the left pie graph.")

    # recursively verify each pie section
    pie_sections = browserobj.findMultiCSS(selector=DeviceLocators.CSS_PIE_GRAPH_PIE_SECTION)
    if not pie_sections:
        logger.error('No Pie Section is shown on this page!')
        return False
    width = range(len(pie_sections))
    for index in width:
        pie_sections = browserobj.findMultiCSS(selector=DeviceLocators.CSS_PIE_GRAPH_PIE_SECTION)
        pie = pie_sections[index]
        if not _recursive_verifying_device_type(browserobj, updated_device_hierarchy, pie):
            return False

    # forth, click back to get to the original hierarchy
    loops = 0
    prompt = browserobj.findSingleCSS(selector=DeviceLocators.CSS_PIE_GRAPH_INDEX).text

    while prompt != device_hierarchy:
        browserobj.click(selector=DeviceLocators.CSS_PIE_GRAPH_GO_BACK)
        loops += 1
        time.sleep(1)
        prompt = browserobj.findSingleCSS(selector=DeviceLocators.CSS_PIE_GRAPH_INDEX, timeout=1).text
        if loops == 5:
            break

    return prompt == device_hierarchy


def _verify_if_errors_inventory_compares(entry_1, entry_2, order=0):
    # if order == 0, check to see if there are wrong orders in an ascending list
    if order == 0:
        return entry_1 > entry_2

    # if order != 0, check to see if there are wrong orders in a descending list
    else:
        return entry_1 < entry_2


def _inventory_entry_compare(first_data, second_data, order, case_sensitive):
    # First, check if the text is empty. If so, no need to compare
    if first_data.text == '' or second_data.text == '':
        return True

    if "N/A" in first_data.text or "N/A" in second_data.text:
        return True

    # Second, check if text can be converted to datetime format, if so then compare the datetime;
    # if not then pass.
    try:
        if _verify_if_errors_inventory_compares(datetime.strptime(first_data.text, "%b %d, %Y, %H:%M"),
                                                datetime.strptime(second_data.text, "%b %d, %Y, %H:%M"),
                                                order=order):
            logger.error("Sort datetime out of order " + str(first_data.text) + ", " + str(second_data.text))
            return False
        return True
    except ValueError:
        pass

    # Third, check if data can be converted to int. if so, compare; else, pass
    try:
        if _verify_if_errors_inventory_compares(int(first_data.text),
                                                int(second_data.text),
                                                order=order):
            logger.error("Sort number out of order " + str(first_data.text) + ", " + str(second_data.text))
            return False
        return True
    except ValueError:
        pass

    # Fourth, check if data can be matched by IPV4/IPV6. If so, compare them in alphabetic order
    match_ipv4 = re.search(r'^(\d+\.){3}\d+(\/\d{1,2}){0,1}$', first_data.text)
    match_ipv6 = re.search(r'^(\w{1,4}\:){7}\w{4}$', first_data.text)
    if match_ipv4 or match_ipv6:
        # if convertIP(data[i].text) > convertIP(data[i+1].text):
        if _verify_if_errors_inventory_compares(str(first_data.text),
                                                str(second_data.text),
                                                order=order):
            logger.error("Sort IP out of order " + str(first_data.text) + ", " + str(second_data.text))
            return False
        return True

    # Fifth, handle cases for data that looks like 73 KB.  Need to convert to Byte
    match = re.search(REGEX_UI_DATA_PATTERN, first_data.text)
    if match:
        if _verify_if_errors_inventory_compares(convertByte(first_data.text),
                                                convertByte(second_data.text),
                                                order=order):
            logger.error("Sort Data out of order " + str(first_data.text) + ", " + str(second_data.text))
            return False
        return True

    # Sixth, handle normal text content
    if not case_sensitive:
        first_text = first_data.text.lower()
        second_text = second_data.text.lower()
    else:
        first_text = first_data.text
        second_text = second_data.text
    if _verify_if_errors_inventory_compares(first_text,
                                            second_text,
                                            order=order):
        # Skip, if one value is a string and the other is a mac address. Else, return False
        # This is to handle UI sorting transition from string group to mac group
        is_mac_i = re.search(r'([0-9a-f]{2}(?::[0-9a-f]{2}){5})', first_text)
        is_mac_i1 = re.search(r'([0-9a-f]{2}(?::[0-9a-f]{2}){5})', second_text)
        if is_mac_i or is_mac_i1:
            if is_mac_i and is_mac_i1:
                logger.error("Sort Mac Address out of order " + str(first_data.text) + ", " + str(second_data.text))
                return False
            return True

        # skip handling of text that has - or _ since python sorting and our UI sorting is reversed here
        combine_string = first_text + second_text
        if '-' in combine_string or '_' in combine_string:
            return True

        # process the string if it is of countries column
        m = re.search('and [0-9]+ more', first_text)
        if m:
            more_countries = m.group(0)
            first_text = first_text.replace(more_countries, "")
        m = re.search('and [0-9]+ more', second_text)
        if m:
            more_countries = m.group(0)
            second_text = second_text.replace(more_countries, "")

        if not _verify_if_errors_inventory_compares(first_text, second_text, order=order):
            return True

        logger.error("Sort String out of order " + str(first_data.text) + ", " + str(second_data.text))
        return False

    return True


def verifyInventorySort(browserobj, column_list_agg=DeviceLocators.CSS_SELECTOR_DEVICE_GENERAL_SORT,
                        case_sensitive=False):
    """
    This function will check the columns
    :param browserobj: the browser object
    :param column_list_agg: a list of column lists, the columns will be selected according to one list per time.
    :param case_sensitive: if True, then compare the ASCII order of string, else convert all string into lower case
                           before comparison.
    :return: True if all rows of the first page in every column pass the sort checking.
    """
    logger.info("Start Verifying Inventory Sort...")

    # rcode: boolean flag for all columns
    rcode = True
    for columns_list in column_list_agg:
        click_all_checkbox(browserobj, columns_list)
        num_column = len(columns_list)

        for idx_column in range(num_column):
            header_element = browserobj.findMultiCSSNoHover(selector=DeviceLocators.CSS_INVENTORY_HEADER)[idx_column]
            header_name = header_element.find_element_by_class_name("customHeaderLabel").text.strip()
            if header_name == "":
                continue
            logger.info('Sorting Column: ' + header_name + '...')

            # Iterate over the up arrow button and down arrow button
            for idx, css_arrow_selector in enumerate([UISharedLoc.CSS_SORT_UP_ARROW, UISharedLoc.CSS_SORT_DOWN_ARROW]):
                direct = 'Up' if idx == 0 else 'Down'
                logger.info('Checking whether the sorted column is going ' + direct)
                # Click the header to see the up arrow indicating ascending order,
                # or the down arrow indicating descending order
                cocy = browserobj.findMultiCSSNoHover(selector=DeviceLocators.CSS_INVENTORY_HEADER)[idx_column]
                clicky = browserobj.findSingleCSS(browserobj=cocy, selector=DeviceLocators.CSS_INVENTORY_HEADER_TIGHT)

                header_element = clickUntilFind(browserobj, clicky, css_arrow_selector,
                                         selector=DeviceLocators.CSS_INVENTORY_HEADER_TIGHT, idx=idx_column)
                if not header_element:
                    logger.error("Cannot find column arrow " + direct + " button, Column " + header_name + " failed")
                    rcode = False
                    continue
                time.sleep(2)  # wait for the refresh of all cells after sorting
                cocy = browserobj.findMultiCSSNoHover(selector=DeviceLocators.CSS_INVENTORY_HEADER)[idx_column]
                header_id = cocy.get_attribute("col-id")
                custom_selector = DeviceLocators.CSS_COLUMN_ALL_CELLS + '[col-id="{}"]'.format(header_id)

                data = browserobj.findMultiCSS(selector=custom_selector)

                # column_sorted is the boolean flag to indicate whether column l is sorted
                column_sorted = True

                for i in range(0, len(data) - 1):
                    if not _inventory_entry_compare(data[i], data[i + 1], order=idx, case_sensitive=case_sensitive):
                        column_sorted = False

                if column_sorted:
                    logger.info('Sort ' + direct + ' Column ' + header_name + ' succeed')
                else:
                    logger.error('Sort ' + direct + ' Column ' + header_name + " failed")

                # rcode remains to be true only when every column_sorted is true
                rcode = rcode and column_sorted
    return rcode


def exportInventory(browserobj):
    """
    This function clicks the download inventory button. If the icon of 'downloading in progress' is shown, return true;
    Only check the icon, instead of the backend API.

    :param browserobj:
    :return: True / False
    """
    exportBtn = DeviceLocators.CSS_EXPORT_BUTTON
    messageSelector = DeviceLocators.CSS_DOWNLOAD_INPROGRESS_MESSAGE
    params = {"selector": exportBtn, "timeout": 3}
    download_element = browserobj.findSingleCSS(**params)
    if not download_element:
        logger.error("Fail to click on export button")
        return False
    return True


def downloadInventory(browserobj):
    """
    firstly, it click the downloading button.

    Secondly, check if there is csv files in the download file path.

    Thirdly, open the first file with the postfix '.csv' and check if the headers in the downloading
    file matches the label list.

    :param browserobj:
    :return: True / False

    """
    label_list = ["hostname","ip address","mac address","profile type","profile vertical","category","profile","last activity","long description","vlan","site name","risk score","risk level","in use","subnet","number of critical alerts","number of warning alerts","number of caution alerts","number of info alerts","first seen date","confidence score","location","vendor","model","description","asset tag","os group","os/firmware version","OS Support","OS End of Support","Serial Number","endpoint protection","EPP Last Activity","NetworkLocation","AET","DHCP","wire or wireless","department","SMB","Switch Port","Switch Name","Switch IP","Source","services","is server","parent mac","NAC profile","NAC profile source","NAC Auth State","NAC Auth Info","Synced With Third-Party","Time Synced With Third-Party","Access Point IP","Access Point Name","SSID","Authentication Method","Encryption Cipher","rssi","CMMS Source","CMMS Category","CMMS State","External Inventory Sync Field","AD Username","AD Domain","WIFI Auth Timestamp","WIFI Auth Status","EAP Method","OS is obsoleted","OS obsoleted reason","Managed by VMWare","Applications","Tags","Ports","ports_detail","WLC Device Type","International Access","Countries","Protocols","External Network","External Network Date"]


    exportBtn = DeviceLocators.CSS_EXPORT_BUTTON
    params = {"selector": exportBtn, "waittype": "visibility", "timeout": 3}
    rcode = browserobj.click(**params)
    if not rcode:
        logging.error("Fail to click on export button")
        return False

    while browserobj.findSingleCSS(selector=DeviceLocators.CSS_DOWNLOAD_INPROGRESS_MESSAGE, waittype="visibility", timeout=3):
        time.sleep(3)

    # After the in-progress icon disappears, Wait for the file is loaded in the OS file system.
    #time.sleep(20)
    filey = WebDriverWait(browserobj.driver, 30, 1).until(get_downloaded_files)
    #filey = get_downloaded_files(browserobj.driver)
    print (filey)
    if len(filey) == 0:
        logger.info("Error: File not Downloaded")
        return False
    linx = get_file_content(browserobj.driver,filey[-1])
    trutext = linx.split(",")[-1]
    trutext = base64.standard_b64decode(trutext)
    trutext = trutext.decode("utf-8")

    lines = trutext.split("\n")
    line = lines[0]
    # Check if labels are in order
    line = line.strip("\n")
    line_list = line.split(",")
    for liney in line_list:
        liney_cut = liney.strip('\"')
        if liney_cut not in label_list:
            logger.info("Error: " + liney_cut + " Labels not in the label list should not appear")
            return False

    logger.info('Downloaded CSV file has been verified. Delete it now.')
    return True


def exportSelectedInventory(browserobj):
    """
    Clicks the inventory check box on the leftmost column of the table, and then click the button of
    downloading selected item. Then it checks how many rows selected and then it stires them in nums[0]

    :param browserobj:
    :return: True/False
    """
    linkz = browserobj.findMultiCSS(selector=DeviceLocators.CSS_SELECTOR_DEVICE_NAME)[:2]
    rcode = browserobj.findVisibleMultiCSS(selector=DeviceLocators.CSS_INVENTORY_CHECKBOX)
    rcode[0].click()
    time.sleep(1)
    #pdb.set_trace()
    rcode[1].click()
    time.sleep(1)
    exportBtn = DeviceLocators.CSS_DOWNLOAD_SELECTED_INVENTORY_BUTTON
    messageSelector = DeviceLocators.CSS_DOWNLOAD_SELECTED_INVENTORY_INPROGRESS_MESSAGE
    params = {"selector": exportBtn, "waittype": "visibility", "timeout": 3}
    rcode = browserobj.click(**params)
    if not rcode:
        logger.error("Fail to click on export button")
        return False
    msg = browserobj.getText(selector=DeviceLocators.CSS_DOWNLOAD_COUNT_MESSAGE)
    nums = [int(s) for s in msg.split() if s.isdigit()]
    if len(nums) < 1:
        logger.error('zbUIDeviceInventory.py/exportSelectedInventory: No numbers in CSS_SELECTED_INVENTORY_NUM_TEXT.')
        return False
    elif nums[0] < 1:
        logger.error('zbUIDeviceInventory.py/exportSelectedInventory: CSS_SELECTED_INVENTORY_NUM_TEXT shows an invalid count {}.'.format(
                nums[0]))
        return False
    '''
    successDom = browserobj.findSingleCSS(
        selector=DeviceLocators.CSS_DOWNLOAD_SELECTED_INVENTORY_SUCCESS_DOM,
        timeout=3,
        err_msg='CSS_DOWNLOAD_SELECTED_INVENTORY_SUCCESS_DOM not found'
    )
    '''
    linkerz = [linkz[0].text,linkz[1].text]
    filey = WebDriverWait(browserobj.driver, 30, 1).until(get_downloaded_files)
    #filey = get_downloaded_files(browserobj.driver)
    print (filey)
    if len(filey) == 0:
        logger.info("Error: File not Downloaded")
        return False
    linx = get_file_content(browserobj.driver,filey[-1])
    trutext = linx.split(",")[-1]
    trutext = base64.standard_b64decode(trutext)
    trutext = trutext.decode("utf-8")

    lines = trutext.split("\n")
    score = 0
    for liney in lines:
        j = liney.split(",")
        for i in j:
            if(linkerz[0] in i or linkerz[1] in i):
                score+=1
    if score < 2:
        logger.critical("Exported inventory not complete")
        return False
    return True


def verifyBulkEntryMenu(browserobj):
    """
    Select the top2 devices in the inventory, click the edit button, and check if the editing page pops up and verify the title of
    that page to be 'Edit Device'.

    Then it looks for all input types in the edit device menu, including device type, category, profile, vendor, model...
    If there are all appearing on the page, then it closes the menu.

    Then it goes to the detail of one device page. then it clicks the three vertical dots to reset device details.
    After it clicks 'edit', the edit page pops up again, and it verifies the title of that page to be 'Edit Device'.
    Then it returns True.

    :param browserobj:
    :return: True if pass the check, False otherwise
    """

    logger.info('Begin verifying bulk entry editing...')
    # Select the devices
    params = {}
    params["selector"] = DeviceLocators.CSS_SELECTOR_DEVICE_CHECKBOXES
    params["err_msg"] = 'ERROR: Checkboxes cannot be found'
    rows = browserobj.findMultiCSS(**params)
    waitLoadProgressDone(browserobj)
    # This one is needed to get back to the top of the device inventory.

    logger.info('click 2 devices at the top of the table...')
    rows[0].click()  # Just grab the first two elements
    rows[1].click()
    params["selector"] = DeviceLocators.CSS_SELECTOR_DEVICE_BULK_EDIT_BUTTON
    params["err_msg"] = 'ERROR: Edit Button is missing'
    bulkEditButton = browserobj.findSingleCSS(**params)
    bulkEditButton.click()
    waitLoadProgressDone(browserobj)

    # Confirm bulk edit menu
    params["selector"] = DeviceLocators.CSS_SELECTOR_BULK_MENU_TITLE
    params["err_msg"] = 'ERROR: Bulk Edit Menu Title cannot be found'
    menuTitle = browserobj.findSingleCSS(**params)
    if not menuTitle:
        logging.error("Error: Edit Menu Title is not found")
        return False
    if menuTitle.text != "Edit Device":
        logger.error("Error: Edit Menu Title is incorrect")
        return False
    bulktestlist = [DeviceLocators.CSS_SELECTOR_BULK_IOT,
                    DeviceLocators.CSS_SELECTOR_BULK_NON_IOT,
                    DeviceLocators.CSS_SELECTOR_BULK_EDITING_CATEGORY,
                    DeviceLocators.CSS_SELECTOR_BULK_EDITING_PROFILE,
                    DeviceLocators.CSS_SELECTOR_BULK_EDITING_VENDOR,
                    DeviceLocators.CSS_SELECTOR_BULK_EDITING_MODEL,
                    DeviceLocators.CSS_SELECTOR_BULK_EDITING_LOCATION,
                    DeviceLocators.CSS_SELECTOR_BULK_EDITING_TAGS,
                    DeviceLocators.CSS_SELECTOR_BULK_EDITING_DESCRIPTION
                    ]
    for token in bulktestlist:
        params["selector"] = token
        params["err_msg"] = 'ERROR:' + token + 'cannot be found'
        if browserobj.findSingleCSS(**params) is False:
            return False

    logger.info('Every Field in the bulktest list is verified in the edit menu. close this menu...')
    # Closing the menu
    params["selector"] = DeviceLocators.CSS_SELECTOR_BULK_EDITING_CLOSE
    params["err_msg"] = 'ERROR: Close button cannot be found'
    browserobj.findSingleCSS(**params).click()
    waitLoadProgressDone(browserobj)

    # Edit one single device
    params["selector"] = DeviceLocators.CSS_SELECTOR_DEVICE_NAMES
    params["err_msg"] = 'ERROR: Device names cannot be found'
    browserobj.findSingleCSS(**params).click()
    time.sleep(3)
    params["selector"] = DeviceLocators.CSS_RESET_MENU_BUTTON
    browserobj.findSingleCSS(**params).click()
    time.sleep(3)
    params["selector"] = DeviceLocators.CSS_SELECTOR_ALT_DEVICE_EDIT_BUTTON
    params["err_msg"] = 'ERROR: Alternate DEVICE Edit Button cannot be found'
    try:
        browserobj.findSingleCSS(**params).click()
    except:
        return False
    time.sleep(3)
    params["selector"] = DeviceLocators.CSS_SELECTOR_BULK_MENU_TITLE
    params["err_msg"] = 'ERROR: Alternate Bulk Edit Menu Title cannot be found'
    menuTitle = browserobj.findSingleCSS(**params).text
    if menuTitle != "Edit Device":
        logger.error("Error: Alternate Edit Menu Title is incorrect")
        return False
    return True


def simpleCheck(browserobj):
    """
    This function selects the devices, goes into the edit menu, and in the new table of that edit page, it
    checks table cell attributes and returns them

    Firstly it selectes the time range by calling zbUIShared.py::clickSpecificTimerange,
    Secondly it searches the TEST_DEVICE(Rhombus-Camera-QA),
    Thirdly it clicks all rows that appear as the search result
    Then it clicks the edit button, and it reaches the 'Edit Device' page and see a new table of deviced to be edited
    Then it counts the number of total rows in this page
    Then it stores a list of dict info in originalInfo list
    For every column header, there is a ID number that can be derived from the id attribute of the element, which is part of the selector for cells below this header.
    By these selectors we can get originalInfo list. Every element in it is a dict recording one row, while the keys are the header names
    and the values are the 'ng-class' attribute values or text of UI elements under that header.

    :param browserobj:
    :return: originalInfo
    """

    params = {}
    originalInfo = []
    clickSpecificTimerange(browserobj, specific="1 Week")
    params["selector"] = DeviceLocators.CSS_SELECTOR_SEARCH_TOGGLE
    browserobj.findSingleCSS(**params).click()
    params["selector"] = DeviceLocators.CSS_SELECTOR_DEVINV_SEARCH
    browserobj.findSingleCSS(**params).send_keys(DeviceLocators.TEST_DEVICE, Keys.ENTER)
    waitLoadProgressDone(browserobj)

    params["selector"] = DeviceLocators.CSS_SELECTOR_DEVICE_CHECKBOXES
    params["err_msg"] = 'ERROR: Checkboxes cannot be found'
    checks = browserobj.findMultiCSS(**params)
    for button in checks:
        button.click()
    waitLoadProgressDone(browserobj)

    params["selector"] = DeviceLocators.CSS_SELECTOR_DEVICE_BULK_EDIT_BUTTON
    params["err_msg"] = 'ERROR: Edit Button is missing'
    bulkEditButton = browserobj.findSingleCSS(**params)
    bulkEditButton.click()
    waitLoadProgressDone(browserobj)
    time.sleep(3)

    params["selector"] = DeviceLocators.CSS_SELECTOR_DEVICE_ROW_ELEMENTS
    params["err_msg"] = 'ERROR: Rows cannot be found'
    rows = browserobj.findMultiCSS(**params)
    rowcount = len(rows) / 2

    i = 0
    while i < rowcount:
        originalInfo.append({})
        i = i + 1
    params["selector"] = DeviceLocators.CSS_SELECTOR_DEVICE_COLUMN_HEADER
    headers = browserobj.findMultiCSS(**params)
    for head in headers:
        text = str(head.get_attribute('id'))
        m = re.search('-0...', text)
        if m:
            currentID = m.group(0)
        else:
            logger.error("Error: Oh no, the columns are inaccurate, again")
            return False
        params["selector"] = ".ui-grid-coluiGrid" + currentID + " div div"
        elements = browserobj.findMultiCSS(**params)
        for enum, ele in enumerate(elements[3:]):
            if head.text == 'Type':
                originalInfo[enum][head.text] = str(ele.get_attribute('ng-class'))
            else:
                originalInfo[enum][head.text] = ele.text
    return originalInfo


def changeElement(browserobj, input_list):  # Sets the element to the testing states
    """
    This function edits the devices, selected by device name with "Rhombus-Camera", to be the status hardcoded by QA.
    Firstly it select the time range to be '1 Week' by calling zbUIShared.py::clickSpecificTimerange (which is outdated),
    Then it clicks the search magnifier, then it sends the keys and gets to the search result.
    Then it selects all search result and comes to the edit page.

    In the Edit device page, it sets the device info exactly the same as what we have already hardcoded. It fills in
    the form with category, profile, vendor, model, location, description.

    :param browserobj:
    :param input_list: specify what to fill in some of the blanks of edit menu.
    :return: number of devices changed by this function.s
    """
    params = {}
    # clickEachTimerange(browserobj, specific="1 Week")
    # Not using this generator, because this statement returns an object but does not start execution immediately.
    params["selector"] = DeviceLocators.CSS_SELECTOR_SEARCH_TOGGLE
    browserobj.findSingleCSS(**params).click()
    params["selector"] = DeviceLocators.CSS_SELECTOR_DEVINV_SEARCH
    browserobj.findSingleCSS(**params).send_keys(DeviceLocators.TEST_DEVICE, Keys.ENTER)
    waitLoadProgressDone(browserobj)
    params["selector"] = DeviceLocators.CSS_SELECTOR_DEVICE_CHECKBOXES
    params["err_msg"] = 'ERROR: Checkboxes cannot be found'
    checks = browserobj.findMultiCSS(**params)
    for button in checks:
        button.click()
    params["selector"] = DeviceLocators.CSS_SELECTOR_DEVICE_BULK_EDIT_BUTTON
    params["err_msg"] = 'ERROR: Edit Button is missing'
    bulkEditButton = browserobj.findSingleCSS(**params)
    bulkEditButton.click()
    waitLoadProgressDone(browserobj)
    if input_list[0]:
        params["selector"] = DeviceLocators.CSS_SELECTOR_BULK_IOT
        browserobj.findSingleCSS(**params).click()
    else:
        params["selector"] = DeviceLocators.CSS_SELECTOR_BULK_NON_IOT
        browserobj.findSingleCSS(**params).click()

    params["selector"] = DeviceLocators.CSS_SELECTOR_BULK_EDITING_CATEGORY
    field = browserobj.findSingleCSS(**params)
    browserobj.click(**params)
    field.send_keys(input_list[1], Keys.ENTER)

    params["selector"] = DeviceLocators.CSS_SELECTOR_BULK_EDITING_PROFILE
    field = browserobj.findSingleCSS(**params)
    browserobj.click(**params)
    # we use the click function in our own library to
    # catch potential 'ElementClickInterceptedException'.
    # browserobj.driver.execute_script("arguments[0].click();", field)
    field.send_keys(input_list[2])

    params["selector"] = DeviceLocators.CSS_SELECTOR_BULK_EDITING_VENDOR
    field = browserobj.findSingleCSS(**params)
    browserobj.click(**params)
    field.send_keys(input_list[3])

    params["selector"] = DeviceLocators.CSS_SELECTOR_BULK_EDITING_MODEL
    field = browserobj.findSingleCSS(**params)
    browserobj.click(**params)
    field.send_keys(input_list[4])

    params["selector"] = DeviceLocators.CSS_SELECTOR_BULK_EDITING_LOCATION
    field = browserobj.findSingleCSS(**params)
    browserobj.click(**params)
    field.send_keys(input_list[5])

    params["selector"] = DeviceLocators.CSS_SELECTOR_BULK_EDITING_DESCRIPTION
    field = browserobj.findSingleCSS(**params)
    browserobj.click(**params)
    field.send_keys(input_list[6])

    params["selector"] = DeviceLocators.CSS_SELECTOR_BULK_EDITING_OK_BUTTON
    browserobj.click(**params)
    waitLoadProgressDone(browserobj)

    params["selector"] = DeviceLocators.CSS_SELECTOR_BULK_EDITING_CONFIRM_YES
    browserobj.click(**params)
    waitLoadProgressDone(browserobj)
    return len(checks)


class DeviceInventory():

    def __init__(self, **kwargs):
        self.params = kwargs
        self.selenium = Login(**kwargs).login()

    def gotoDeviceInventory(self):
        url = urlparse(self.params["url"])
        self.selenium.getURL(url.scheme + '://' + url.netloc + '/guardian/monitor/inventory')
        waitLoadProgressDone(self.selenium)
        logger.info('Device Invetory Page is reached')
        return True

    def _verify_sum_of_two_options(self, comb=[1, 2, 1], option1=[2, 2, 1], option2=[3, 2, 1], strict=False):
        """
        Internal method for global filtering to check whether the complementary
        filtered results can be summed as expected.

        :param comb: this is the setting when global filtered the total number of devices.
        :param option1: option1 is either a number or a list. If it is a number it shows the number of filtered result,
                        If it is a list, it will be the setting parameter of global filters in resetAllDevAllSite.
        :param option2: option2 is the complementary part of option 1.
                        eg. <Connected Sites / Disconnected Sites>, <IoT devices / Traditional IT devices>

        :return: True if filtered result number of option 1 + option 2 = filtered result number of comb; False otherwise
        """

        # Get the total number of devices
        result_of_filtering = []
        for op in [comb, option1, option2]:
            if type(op) is int:
                result_of_filtering.append(op)
            else:
                resetAllDevAllSite(self.selenium, specific=op)
                number = get_number_of_devices(self.selenium)
                assert number >= 0, "Fail to get the number of filtered devices"
                result_of_filtering.append(number)

        if len(result_of_filtering) is not 3:
            logger.error('Unable to find all numbers of filtered devices')
            return False

        if strict:
            return result_of_filtering[0] == result_of_filtering[1] + result_of_filtering[2]
        else:
            return result_of_filtering[0] >= result_of_filtering[1] + result_of_filtering[2]


    def checkDeviceInventoryTimeSeries(self, time_series=['2 Hours', '1 Day', '1 Week'], strict=True):
        """
        Select the time ranges of ['2 Hours', '1 Day', '1 Week', '1 Month', '1 Year', 'All to Date']
        Check if number of time series bar is corresponding to the time range selected.

        :param: time_series can be a string or a list of string, indicating the time series to be tested.
        :return: a list of all time series UI elements shown after the final time option is selected.
        """
        logger.info('Start checking Device Inventory TimeSeries...')
        self.gotoDeviceInventory()
        resetAllDevAllSite(self.selenium, specific=[1, 2, 1])
        data = []
        for result in (clickEachTimerange(self.selenium, specific=time_series)):
            if not result:
                logger.error('Unable to click all time ranges')
                return False
            if not waitLoadProgressDone(self.selenium) and False: #Yo this never passes
                logger.error('Unable to load device inventory in selected time range')
                return False
            data = waitSeriesGraphDone(self.selenium)
            if not data:
                logger.error('Traffic series did not find any data')
                return False
            if not verifyDataTimerange(result["time"], data, strict=self.params["comparestrict"]):
                logger.error("Traffic series for " + str(result["time"]) + " has only " + str(len(data)) + " bars.")
                if strict:
                    return False
        return data

    def checkButtons(self):
        self.gotoDeviceInventory()
        rcode = verifyDevicesCount(self.selenium)
        return rcode

    def checkEntries(self, pageNumber=0):
        self.gotoDeviceInventory()
        resetAllDevAllSite(self.selenium)
        clickSpecificTimerange(self.selenium, specific="1 Year")
        rcode = verifyInventoryEntries(self.selenium, page_number=pageNumber)
        return rcode

    def checkDeviceTypes(self):
        logger.info('Start checking Device Type section of Device Inventory Page')
        self.gotoDeviceInventory()
        resetAllDevAllSite(self.selenium, specific=[1, 1, 1])
        clickSpecificTimerange(self.selenium, specific="1 Month")
        if not self.selenium.findSingleCSS(selector='.title.ng-star-inserted'):
            logger.error('Unable to find Device Types Section')
            return False
        if not self.selenium.findSingleCSS(selector='path.pie'):
            logger.error('Unable to find Pie Graph of devices')
            return False
        if not self._verifyDevicesMat():
            logger.error('The devices mat table is not loaded')
            return False
        return True


    def checkPagination(self):
        self.gotoDeviceInventory()
        resetAllDevAllSite(self.selenium)
        rcode = verifyInventoryEntries(self.selenium, 2)
        return rcode

    def checkDownload(self):
        """
        This function goes to the device inventory page, and call downloadInventory,
        return the result of downloadInventory

        :return:
        """
        self.gotoDeviceInventory()
        resetAllDevAllSite(self.selenium)
        rcode = downloadInventory(self.selenium)
        return rcode

    def checkSort(self):
        self.gotoDeviceInventory()
        resetAllDevAllSite(self.selenium)
        clickSpecificTimerange(self.selenium, specific="1 Year")
        rcode = verifyInventorySort(self.selenium)
        return rcode

    def check_create_policy_from_tooltip(self):
        self.gotoDeviceInventory()
        clickSpecificTimerange(self.selenium, specific="1 Month")
        device_tooltip = DeviceTooltip(self.selenium)
        # check the UI element loading in tooltip
        assert device_tooltip.check_tooltip_ui_elements()

        # check the link to alerts page on tooltip
        self.gotoDeviceInventory()
        assert device_tooltip.check_link_to_alerts_page()

        # check how to add and remove policy through the tooltip
        self.gotoDeviceInventory()
        clickSpecificTimerange(self.selenium, specific="1 Month")
        assert device_tooltip.add_check_remove_policy_from_device_inventory()

        # check how to cancel the policy creation process through the tooltip
        self.gotoDeviceInventory()
        clickSpecificTimerange(self.selenium, specific="1 Month")
        assert device_tooltip.add_check_remove_policy_from_device_inventory(cancel=True)
        return True

    def check_view_columns_reset(self):
        if not self.gotoDeviceInventory():
            logger.error('Unable to reach the device inventory page')
            return False
        logger.info('Checking the reset function in viewing column card of the device inventory page...')
        if not click_and_reset_to_default(self.selenium):
            logger.error('Reset to Default is not working!')
            return False
        logger.info('Reset Columns passed the check')
        return True

    def close(self):
        if self.selenium:
            self.selenium.quit()

    def checkDeviceLink(self):
        logger.info('Checking if the device name in the inventory table directs to device detail page...')
        self.gotoDeviceInventory()
        # check if the link to device detail is working
        if not verifyLinkToDeviceDetail(self.selenium, DeviceLocators.CSS_SELECTOR_DEVICE_NAMES):
            logger.error("Device link to Device Detail is not working")
            return False
        else:
            logger.info("Device link to Device Detail passes the check")
            return True

    def checkInventoryExport(self, selected=False):
        """
        This function will call zbUIDeviceInventory.py::exportInventory, if selected is false;
        or call zbUIDeviceInventory.py::exportSelectedInventory if selected is true.

        :param selected:
        :return: True if succeed in catching the downloading spinning circle
        """
        self.gotoDeviceInventory()
        if not selected:
            rcode = exportInventory(self.selenium)
        else:
            rcode = exportSelectedInventory(self.selenium)
        return rcode

    def check_local_search(self):
        self.gotoDeviceInventory()
        resetAllDevAllSite(self.selenium, specific=[1, 1, 1])
        clickSpecificTimerange(self.selenium, specific="1 Year")
        local_search = InventoryLocalSearch(self.selenium)
        data_generator = DeviceDataGenerator(self.selenium)
        device_names = data_generator.get_device_names_from_inventory()[:20]
        for name in device_names:
            assert local_search.search_by_name(name)
            assert local_search.verify_column_name("Device Name", name)
            local_search.clear_all_search_results()
        return True

    def check_local_filter(self):
        self.gotoDeviceInventory()
        resetAllDevAllSite(self.selenium, specific=[1, 1, 1])
        clickSpecificTimerange(self.selenium, specific="1 Week")
        local_filter = LocalFilter(self.selenium)
        #check if UI elements load as expected
        assert local_filter.check_ui_elements()
        logger.info("UI elments of the filter card are verified")

        # check if we can add more than one filters at one time
        filters = dict()
        filters["Profile"] = "PC-Windows"
        filters["Vendor"] = "YAKUMO Enterprise"
        assert self._add_more_than_one_filter_at_same_time(filters, local_filter)
        logger.info("More than one filters are added at the same time and verified")

        # filters list is empty after prev checking. Now check if exclude filter is working
        filters["Profile"] = "PC-Windows"
        assert self._check_exclude_filters(filters, "Profile", local_filter)
        logger.info("Exclude filter for Profile has been verified")

        # check filters of Risk, Internet Access, International Access
        filter_comb = dict()
        filter_comb["filter_name"] = "Risk"
        filter_comb["filter_options"] = ["Critical", "High", "Medium", "Low"]
        assert self._check_specific_filter_by_selection(filter_comb, local_filter), "Risk Filters Fail the test"
        logger.info("Filters of Risks are verified")

        filter_comb["filter_name"] = "Internet Access"
        filter_comb["filter_options"] = ["Yes", "No"]
        assert self._check_specific_filter_by_selection(filter_comb, local_filter), "Internet Access Filters Fail the test"
        logger.info("Filters of Internet Access are verified")

        filter_comb["filter_name"] = "International Access"
        filter_comb["filter_options"] = ["Yes", "No"]
        assert self._check_specific_filter_by_selection(filter_comb, local_filter), "International Access Filters Fail the test"
        logger.info("Filters of International Access are verified")

        # check all other valid filters
        assert self._check_multiple_filter(local_filter)
        logger.info("Any other filter with valid data are verified")
        return True

    def _add_more_than_one_filter_at_same_time(self, filters_to_check, local_filter):
        assert local_filter.add_filter(filters_to_check)
        assert local_filter.check_if_filter_added(filters_to_check)
        local_filter.reset_filters()
        return True

    def _check_exclude_filters(self, filter_to_check, filter_name, local_filter):
        assert local_filter.add_filter(filter_to_check, include=False)
        output = create_header_dict(self.selenium)
        elements = output[filter_name]
        for element in elements:
            if element.text == filter_to_check[filter_name]:
                return False
        local_filter.reset_filters()
        return True

    def _check_specific_filter_by_selection(self, filter_comb, local_filter):
        """
        For Filters like "Risk", "Internet Access", we have to set the filter by selection. Therefore the
        testing logics are different from other filters. This one checks every single filter options, indicated
        by filter_comb, add them up to see if the total number of devices is as expected.

        :param filter_comb: dictionary contains: <filter_name: xxx>, <filter_options: [xx, xxx]>
        :return: true if pass the test, false othewise
        """
        filter_to_check = dict()
        total_devices = get_number_of_devices(self.selenium)
        result_devices = 0
        for filter_value in filter_comb["filter_options"]:
            filter_to_check[filter_comb["filter_name"]] = filter_value
            assert local_filter.add_filter(filter_to_check, by='Selection')
            assert local_filter.check_if_filter_added(filter_to_check)
            result_devices += get_number_of_devices(self.selenium)
            local_filter.reset_filters()
        if result_devices > total_devices:
            logger.error('The number for devices under {} filters are not matched'.format(filter_comb["filter_name"]))
            return False
        return True

    def _check_multiple_filter(self, local_filter):
        # Get two helper class prepared
        device_data_generator = DeviceDataGenerator(self.selenium)

        for filter_columns in DeviceLocators.filtered_columns_list:
            # Append "Device Name" to select the columns present in the page
            filter_columns.append("Device Name")
            if not click_and_verify_columns(self.selenium, verify_list=filter_columns,
                                            view_col=DeviceLocators.CSS_TABLE_VIEW_COLUMN):
                logger.info('Unable to click and verify all column headers')
                return False
            # Remove "Device Name" such that only original columns in filter_columns will be checked as filters
            del filter_columns[-1]
            filter_data = device_data_generator.get_data_from_inventory(filter_columns)

            fail_name = None
            pass_check = True
            for single_filter in filter_data:
                device_name = single_filter["Device Name"]
                del single_filter["Device Name"]
                assert local_filter.add_filter(single_filter)
                assert local_filter.check_if_filter_added(single_filter)
                output = create_header_dict(self.selenium)
                device_names_elements = output["Device Name"]
                single_filter_pass_check = False
                for device_names_element in device_names_elements:
                    if device_names_element.text == device_name:
                        single_filter_pass_check = True
                        break
                fail_name = single_filter
                local_filter.reset_filters()
                pass_check = pass_check and single_filter_pass_check
            if not pass_check:
                logger.error('Unable to verify all the filters in ' + str(filter_columns))
                logger.error('Failed on' + str(fail_name))
                return False
        return True

    def check_global_filter(self, time_range="1 Month", to_be_filtered="sites"):
        self.gotoDeviceInventory()
        clickSpecificTimerange(self.selenium, specific=time_range)

        # check the sites under devices
        if to_be_filtered == "sites":
            if os.environ['NODE_ENV'] == 'testing':
                verify_result = self._verify_sum_of_two_options(comb=[1, 2, 1],
                                                                option1=[2, -1, -1],
                                                                option2=0,
                                                                strict=True)
            else:
                verify_result = self._verify_sum_of_two_options(comb=[1, 2, 1],
                                                                option1=[2, -1, -1],
                                                                option2=[3, -1, -1],
                                                                strict=True)
            if not verify_result:
                logger.error('Unable to verify the numbers of devices filtered by connected sites '
                             ', disconnected sites and all sites')
                return False
        elif to_be_filtered == "devices":
            if os.environ['NODE_ENV'] == 'testing':
                option2 = [-1, -1, 5]
            else:
                option2 = [-1, -1, 6]
            assert self._verify_sum_of_two_options(comb=[1, 2, 1], option1=[-1, -1, 2], option2=option2), \
                "Unable to verify the number of devices filtered by all, IoT and Non-IoT"

        else:
            resetAllDevAllSite(self.selenium, specific=[1, 2, 1])
            discovered_device = get_number_of_devices(self.selenium)
            resetAllDevAllSite(self.selenium, specific=[-1, 1, -1])
            monitored_device = get_number_of_devices(self.selenium)
            assert monitored_device <= discovered_device,\
                "Number of monitored devices is larger than discovered devices "
        return True

    def check_device_types_recursive(self, time_range="1 Year"):
        self.gotoDeviceInventory()
        clickSpecificTimerange(self.selenium, specific=time_range)
        resetAllDevAllSite(self.selenium, specific=[1, 1, 1])

        # Check if all pie sections has the same data with the table.
        assert _compare_tooltip_against_table(self.selenium)

        # recursively verify each pie section
        pie_sections = self.selenium.findMultiCSS(selector=DeviceLocators.CSS_PIE_GRAPH_PIE_SECTION)
        for index in range(len(pie_sections)):
            pie_sections = self.selenium.findMultiCSS(selector=DeviceLocators.CSS_PIE_GRAPH_PIE_SECTION)
            pie = pie_sections[index]
            if not _recursive_verifying_device_type(self.selenium, "All devices", pie):
                return False

        prompt = self.selenium.findSingleCSS(selector=DeviceLocators.CSS_PIE_GRAPH_INDEX).text
        return prompt == "All devices"

    def _verifyDevicesMat(self):
        # Number of rows on this page
        pages = self.selenium.findSingleCSS(selector=DeviceLocators.CSS_PIE_GRAPH_PAGES)
        pages = pages.text.strip().split()
        entries_per_page = int(pages[2])
        logger.info('There should be ' + pages[2] + ' entries in Device Mat')

        # find all headers
        headers = self.selenium.findMultiCSS(selector=DeviceLocators.CSS_PIE_GRAPH_HEADERS)

        # for every cells under the header, they should have the same number as entries_per_page
        for header in headers:
            s = header.get_attribute("class")
            try:
                column = re.search('cdk-column-[A-Za-z]+', s).group(0)
                cells_in_column = self.selenium.findMultiCSS(selector=('td.' + column))

                if not cells_in_column or len(cells_in_column) is not entries_per_page:
                    logger.error('Cells below column ' + header.text + ' are not matched')
                    return False

                logger.info('Cells below column ' + column.split('-')[2] + ' are matched with entry number')

            except Exception as e:
                logger.error(str(e))
                logger.error('Unable to get the cell selector from header element')
                return False

        return True

class BulkEdit(object):

    def __init__(self, **kwargs):
        self.params = kwargs
        self.selenium = Login(**kwargs).login()

    def gotoDeviceInventory(self):
        url = urlparse(self.params["url"])
        self.selenium.getURL(url.scheme + '://' + url.netloc + '/guardian/monitor/inventory')
        waitLoadProgressDone(self.selenium)
        logger.info('Device Invetory Page is reached')

    def checkDefault(self):
        self.gotoDeviceInventory()
        resetAllDevAllSite(self.selenium)
        rcode = verifyBulkEntryMenu(self.selenium)
        return rcode

    def checkTable(self):
        self.gotoDeviceInventory()
        resetAllDevAllSite(self.selenium)
        try:
            simpleCheck(self.selenium)
        except:
            return False
        return True

    def checkBulkEditChange(self):
        self.gotoDeviceInventory()
        rcode = verifyFilterChange(self.selenium)
        return rcode

    def close(self):
        if self.selenium:
            self.selenium.quit()

