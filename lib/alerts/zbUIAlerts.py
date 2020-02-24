#!/usr/bin/python
import json
import time
import os
import re
import random, glob
from datetime import datetime
from urllib.parse import urlparse
from selenium.webdriver.common.keys import Keys
from ui.login.zbUILoginCore import Login
from ui.zbUIAssetManagement import enableAIMS, enableConnectiv
from common.zbUIShared import *
from common.zbCommon import compareStringLists, isValidIPv4Address, isValidMACAddress, fuzzyRegexSearch
from common.zbPolicyProfile import Policy_Profile
from common.zbAIMS import AIMS
from common.zbSplunk import Splunk
from common.zbPANFW import PanFW
from common.zbConnectiv import Connectiv
from common.zbFile import ReadFile

# global CSS parameters for Monitor > Alert page
CSS_SELECTOR_ALERT_NUMBER = "div.layout-row > div.layout-column > zing-alert-widget > div.alert-widget > div > div.alert-number"
CSS_SELECTOR_ALTER_DETAILS_NUMBER = 'zing-alert-widget[alert=\'{severity: item.value, value: alertDetailCtrl.alertStatData[item.value]}\'] .alert-widget .alert-display-item .alert-number'

CSS_SELECTOR_ALERT_DROPDOWN = "md-select.alert-status-selector"
CSS_SELECTOR_ALERT_DROPDOWN_OPTIONS = "div.md-active > md-select-menu > md-content > md-option"

CSS_ALERT_LIST_FRAME = 'md-card.alert-list'

CSS_ALERT_STATUS_DROPDOWN = 'md-select[name="Open pending/resolved dropdown"]'
CSS_ALERT_STATUS_PENDING = 'md-option[name="Picked Pending"]'
CSS_ALERT_STATUS_RESOLVED = 'md-option[name="Picked Resolved"]'
CSS_ALERT_STATUS_ALL = 'md-option[name="Picked All Alerts"]'
CSS_ALERT_STATUS_IGNORED = 'md-option[name="Picked Ignored"]'
CSS_ALERT_STATUS_SENDTOSIEM = 'md-option[name="Picked Sent to SIEM"'
CSS_ALERT_STATUS_WORKORDERCREATED = 'md-option[name="Picked Work Order Created"]'
CSS_ALERT_STATUS_INTERNAL = 'md-option[name="Picked Internal Review"]'

CSS_SELECTOR_ALERT_POLICY_TITLE = "zing-alert-list .policy-list .list-item div.word"
CSS_SELECTOR_ALERT_POLICY_DROPDOWN = "div.layout-align-start-center.layout-row.flex-40"
CSS_SELECTOR_ALERT_POLICY = "div.alert-item[aria-hidden='false']"

CSS_ALERT_SEVERITY_DROPDOWN = 'md-select[name="Open alert severity dropdown"]'
CSS_ALERT_SEVERITY_CRITICAL = 'md-option[name="Picked Critical severity"]'
CSS_ALERT_SEVERITY_WARNING = 'md-option[name="Picked Warning severity"]'
CSS_ALERT_SEVERITY_CAUTION = 'md-option[name="Picked Caution severity"]'
CSS_ALERT_SEVERITY_INFO = 'md-option[name="Picked Info severity"]'
CSS_ALERT_SEVERITY_ALLLEVELS = 'md-option[name="Picked All Severity Levels severity"]'

CSS_ALERT_ICON_CRITICAL = 'div.alert-widget.high > div.alert-display-item > i.alert-icon'
CSS_ALERT_ICON_WARNING = 'div.alert-widget.medium > div.alert-display-item > img.alert-icon'
CSS_ALERT_ICON_CAUTION = 'div.alert-widget.low > div.alert-display-item > i.alert-icon'
CSS_ALERT_ICON_INFO = 'div.alert-widget.info > div.alert-display-item > i.alert-icon'

CSS_ALERT_COUNT_TOTAL = 'span[ng-if="!alertListCtrl.loading"]'
CSS_ALERT_NAME = 'h4[category="Alert List"]'
CSS_ALERT_DESCRIPTION = 'div.policy-list .alert-column h5'
CSS_ALERT_SINGLE = 'a.alert-detail-nav.ng-scope'
CSS_ALERT_SINGLE_CHECKBOX = "md-checkbox[aria-label='Select alert']"
CSS_ALERT_SINGLE_SRCDEV_LINK = 'div.ip-listing'
CSS_ALERT_SINGLE_APP_LINK = 'div.ip-listing'
CSS_ALERT_SINGLE_ACTION_DROPDOWN = "md-select[ng-click='alertDetailCtrl.getActionRelatedConfig();']"
CSS_ALERT_ACTION_RESOLVE = "[ng-click='alertDetailCtrl.showResolvePromp(alertDetailCtrl.alert)']"
CSS_ALERT_ACTION_BLOCK = 'div.md-clickable > * > * > md-option[value=block]'
CSS_ALERT_ACTION_SIEM = 'div.md-clickable > * > * > md-option[value=siem]'
CSS_ALERT_ACTION_AIMS = 'div.md-clickable > * > * > md-option[value=assetmanagement]'
CSS_ALERT_ACTION_CONNECTIV = CSS_ALERT_ACTION_AIMS
CSS_ALERT_ACTION_IGNORE = 'div.md-clickable > * > * > md-option[value=ignore]'
CSS_ALERT_ACTION_EDIT_POLICY = 'div.md-clickable > * > * > md-option[value=disable]'

CSS_ALERT_PAGE_PENDING = 'md-select[aria-label="Filter by status: Pending"]'
CSS_ALERT_PAGE_RESOLVE = 'md-select[aria-label="Filter by status: Resolved"]'
CSS_ALERT_PAGE_ALL = 'md-select[aria-label="Filter by status: All Alerts"]'
CSS_ALERT_PAGE_IGNORE = 'md-select[aria-label="Filter by status: Ignored"]'
CSS_ALERT_PAGE_SIEM = 'md-select[aria-label="Filter by status: Sent to SIEM"]'
CSS_ALERT_PAGE_AIMS = 'md-select[aria-label="Filter by status: Work Order Created"]'
CSS_ALERT_PAGE_INTERNAL = 'md-select[aria-label="Filter by status: Internal Review"]'

CSS_ALERT_ACTION_RESOLVE_COMMENT = '.alert-resolve input'
CSS_ALERT_ACTION_COMMENT = 'input[ng-model="enforceModalCtrl.selectedAction.comment"]'
CSS_ALERT_ACTION_RESOLVE_BUTTON = '.alert-resolve button.zing-button-blue'
CSS_ALERT_ACTION_BLOCK_BUTTON = 'button[ng-if="enforceModalCtrl.selectedAction.value == \'block\'"][aria-disabled=false]'
CSS_ALERT_ACTION_SIEM_BUTTON = 'button[ng-if="enforceModalCtrl.selectedAction.value == \'siem\'"][aria-disabled=false]'
CSS_ALERT_ACTION_AIMS_BUTTON = 'button[type=\'submit\'][aria-disabled=\'false\']'
CSS_ALERT_ACTION_CANCEL_BUTTON = 'button[ng-click="enforceModalCtrl.close()"]'


CSS_ALERT_ROWS_PER_PAGE_DESCRIPTION_TEXT = 'zing-alert-list .pagination .description.ng-binding'
CSS_ALERT_NEXT_PAGE_BUTTON = 'zing-alert-list .pagination button[ng-click=\'alertListCtrl.next()\']'
CSS_ALERT_CURRENT_PAGE_SIZE = '.rows_per_page .md-select-value div.md-text.ng-binding'
CSS_ALERT_PAGE_SIZE_DROPDOWN = 'zing-alert-list .pagination .rows_per_page md-select'
CSS_ALERT_PAGE_SIZE_FORMATTED_STR = 'md-option[value=\'{}\']'

CSS_ALERT_DETAILS_MORE_DETAILS_BUTTON = 'zing-alert-list .policy-list .alert-detail-nav'
CSS_ALERT_DETAILS_MORE_DETAILS_TITLE = 'zing-alert-detail .alert-detail-page .alert-header-row .main-heading'
CSS_ALERT_DETAILS_DEVICE_BUTTON = 'a.ip-listing.linked.ng-isolate-scope'
CSS_ALERT_DETAILS_DEVICE_TITLE = 'span.md-headline.ng-binding.ng-scope'
CSS_ALERT_DETAILS_PORTOCOL_BUTTON = '.app-via span.appname'
CSS_ALERT_DETAILS_PORTOCOL_TITLE = 'zing-protocol-overall .title-row .md-headline'
CSS_ALERT_DETAILS_MAC_ADDRESS = 'zing-alert-detail .alert-detail-page [ng-bind=\'alertDetailCtrl.alert.deviceid\']'
CSS_ALERT_DETAILS_SRC_IP_ADDRESS = 'zing-alert-detail .alert-detail-page [ng-bind=\'alertDetailCtrl.device.ip\']'
CSS_ALERT_DETAILS_DEST_IP_ADDRESS = '#main-column .alert-list .alert-list-content .layout-column .alert-item [ng-if=\'$index === alert.UI.connIps.length -1\']'
CSS_ALERT_DETAILS_IOT_SCORE = 'zing-alert-detail .alert-detail-page [ng-bind=\'alertDetailCtrl.device.profile_type_score\']'
CSS_ALERT_DETAILS_TRAFFIC_INFO_CHIP = 'zing-alert-detail .chips-wrapper md-chip'
CSS_ALERT_DETAILS_TRAFFIC_TOOLTIP_TEXT = 'div.zing-tooltip-content-container li'

CSS_AIMS_ALERT_ACTION_PRIORITY_DROPDOWN = 'div.enforcement-modal md-select[ng-model=\'enforceModalCtrl.workorder.priority\']'
CSS_AIMS_ALERT_ACTION_PRIORITY_OPTION = 'md-option[ng-value=\'priorityObj\']'
CSS_AIMS_ALERT_ACTION_ASSIGNEE_DROPDOWN = 'div.enforcement-modal md-select[ng-model=\'enforceModalCtrl.workorder.assignee\']'
CSS_AIMS_ALERT_ACTION_ASSIGNEE_OPTION = 'md-option[ng-repeat=\'assignee in enforceModalCtrl.employeeList | filter: enforceModalCtrl.facility\']'

CSS_BLOCK_ACL_RULE_NAME = '.enforcement-modal .block-row-item span.ng-binding'

alert_description = ''
alert_action_comment = ''
alert_action_priority = ''
alert_action_assignee = ''
rule_name = ''

CSS_ALERT_POLICY_SEVERITY = 'form .policy-content md-select-value'
CSS_ALERT_POLICY_SEVERITY_OPTION = 'md-option[value=\'{}\'][category=\'Policy Detail\']'
CSS_ALERT_POLICY_NAME = 'form .policy-content md-input-container [name=\'name\']'
CSS_ALERT_POLICY_ENABLED = 'form .policy-content md-checkbox'
CSS_ALERT_POLICY_NOTIFY_RADIO_BUTTON = 'form .policy-content md-radio-button'
CSS_ALERT_POLICY_NOTIFY_WHITELIST_RADIO_BUTTON = 'form .policy-content md-radio-button:nth-child(2)'
CSS_ALERT_POLICY_REMOVE_TAGS = 'form .policy-content .md-chip-remove-container'
CSS_ALERT_POLICY_BEHAVIOR_GROUP_1 = 'form .policy-content zing-policy-tag-widget[name=\'Set behavior Group1\'] md-chip-template'
CSS_ALERT_POLICY_BEHAVIOR_GROUP_2 = 'form .policy-content zing-policy-tag-widget[name=\'Set behavior Group2\'] md-chip-template'
CSS_ALERT_POLICY_BEHAVIOR_INPUT = 'zing-policy-tag-widget md-input-container .md-chip-input-container md-autocomplete-wrap input'
CSS_ALERT_POLICY_BEHAVIOR_GROUP_1_OPTION = 'div.md-virtual-repeat-scroller ul#ul-242 li:nth-child(2)'
CSS_ALERT_POLICY_BEHAVIOR_GROUP_2_OPTION = 'div.md-virtual-repeat-scroller ul#ul-244 li:nth-child(2)'
CSS_ALERT_POLICY_PROTOCOLS = 'form .policy-content zing-policy-tag-widget[name=\'Set the App/Protocol\'] md-chip-template'
CSS_ALERT_POLICY_PROTOCOLS_OPTION = 'div.md-virtual-repeat-scroller ul#ul-244 li:nth-child(2)'
CSS_ALERT_POLICY_WORKING_DAYS_BUTTON = 'form .policy-content md-input-container .working-day'
CSS_ALERT_POLICY_DURATION_SLIDER_THUMB = 'form .policy-content .md-thumb-containers'
CSS_ALERT_POLICY_NOTIFY_EMAIL = 'form .policy-content md-input-container[name=\'Set Notify\'] md-chip md-chip-template'
CSS_ALERT_POLICY_NOTIFY_EMAIL_INPUT = 'form .policy-content md-input-container[name=\'Set Notify\'] input'
CSS_ALERT_POLICY_UPDATE_BUTTON = '.zing-policy-detail button[name=\'Update policy detail\']'


CSS_SELECT_ALL_ALERTS_CHECKBOX = '.policy-list .left-column md-checkbox'
CSS_SELECTED_ALERTS_NUM_TEXT = '.selection-bar .selected-text'
CSS_DOWNLOAD_SELECTED_INVENTORY_BUTTON = '.selected-table-downloader'
CSS_DOWNLOAD_SELECTED_INVENTORY_INPROGRESS_MESSAGE = 'div.download-in-progress'
CSS_DOWNLOAD_SELECTED_INVENTORY_SUCCESS_DOM = '.zing-qa-hidden-dom'

CSS_ALERT_RESOLVE_NO_ACTION_NEEDED_BTN = '.alert-resolve md-radio-button[value="No Action Needed"]'
CSS_ALERT_RESOLVE_ACTION_SWITCHES = '.alert-resolve md-switch'

CSS_ALERT_ACTION_ASSIGN = "button.md-button[ng-click='alertDetailCtrl.showAssignPrompt(alertDetailCtrl.alert);']"
CSS_ALERT_ACTION_ADD_NOTES = "button.md-button[ng-click='alertDetailCtrl.showNotePrompt(alertDetailCtrl.alert);']"
CSS_ALERT_ACTION_ASSIGN_BUTTON = "button.zing-button.zing-button-blue"
CSS_ALERT_ACTION_NOTE_BUTTON = ".zing-button-blue[ng-click='alertResolveCtrl.addNote()']"
CSS_ALERT_NOTE_INPUT = "input[ng-model='alertResolveCtrl.reason']"
CSS_ALERT_EMAIL_FIELD = "[ng-required='$mdAutocompleteCtrl.isRequired'][name='']"
CSS_ALERT_EMAIL_AUTOFILL = "li.ng-scope[md-virtual-repeat='item in $mdAutocompleteCtrl.matches']"
CSS_ALERT_ACTION_COMMENT_ASSIGN = "[name='reason'][type='text']"
CSS_ALERT_MORE_DETAILS = "a.ng-scope.alert-detail-nav"

CSS_SENDTO_BUTTON = "md-select[ng-click='alertDetailCtrl.getActionRelatedConfig();']"
CSS_ALERT_ACTION_LIST = "div.ng-scope.main-text"
CSS_ALERT_SIEM_SENDTO = "md-option[value='siem']"
CSS_IOT_DEVICE_SELECTION = "[ng-click='iotTabCtrl.openMenu($mdOpenMenu, $event)']"
CSS_IOT_DEVICE_ALL_IOT = "button.md-button[ng-click='iotTabCtrl.changeToIndustry(false)']"

CSS_ALERT_ACTION_MENU = "[md-container-class='action-dropdown']"
CSS_ALERT_ACTION_DOWNLOAD = "md-content [value='download'] .md-text"
CSS_PDF_DOWNLOAD = "[ng-click='ctrl.downloadPdf()']"
CSS_XLS_DOWNLOAD = "[ng-click='ctrl.downloadExcel($event)']"
CSS_XLS_LIST_DOWNLOAD = "[ng-click='ctrl.downloadExcel()']"
CSS_ALERT_DETAIL_POLICY = ".main-heading.ng-binding"

CSS_ALERT_EXPAND_MENU = "[ng-click='alertAggListCtrl.toggleExpandArrow(policy)'] h4.ng-binding"
CSS_ALERT_GOTO_DETAIL = "[ng-bind='alert.hostname']"
CSS_ALERT_NO_EXPAND_NAME = "[ng-click='alertAggListCtrl.goToDeviceDetail($event,policy.deviceids[0])']"

CSS_ALERT_POLICY_CHECKBOX = "[aria-label='Select policy'] [md-ink-ripple=''][md-ink-ripple-checkbox='']"
CSS_ALERT_LIST_DOWNLOAD = ".selected-table-downloader"
def _verifyAlertListDownload(browserobj, filetype):
    alert_names = []
    menu = browserobj.findSingleCSS(selector=CSS_ALERT_EXPAND_MENU)
    alert_names.append(menu.text)
    menu.click()
    time.sleep(2)
    browserobj.hoverElement(menu)
    browserobj.click(selector=CSS_ALERT_POLICY_CHECKBOX, waittype="visibility")
    alert_list = browserobj.findMultiCSS(selector=CSS_ALERT_GOTO_DETAIL, waittype="visibility")
    if not alert_list:
        alert_list = []
        alert_list.append(browserobj.findSingleCSS(selector=CSS_ALERT_NO_EXPAND_NAME))
    for element in alert_list:
        print(element.text)
        alert_names.append(element.text)

    browserobj.click(selector=CSS_ALERT_LIST_DOWNLOAD )
    time.sleep(1)
    #if(filetype == "pdf"): #Bugged
        #browserobj.click(selector=CSS_PDF_DOWNLOAD)
    if(filetype == "csv"):
        browserobj.click(selector=CSS_XLS_LIST_DOWNLOAD)
    time.sleep(8)
    downloc = browserobj.downloadFilepath
    os.chdir(downloc)
    ''' BUGGED
    if filetype == "pdf":
        reader = ReadFile()
        if len(glob.glob("*.pdf")) == 0:
            print "Error: File not found"
            return False
        myfile = glob.glob("*.pdf")[0]
        text = reader.parseScannedPDF(myfile)
        if fuzzyRegexSearch(text, alert_name, 8) is None: #Check for title
            print text
            print "PDF check failed"
            return False

    '''
    if filetype == "csv":
        if len(glob.glob("*.csv")) == 0: #Only alert name is in there
            print("XLS file not found")
            return False
        with open(glob.glob("*.csv")[0]) as myfile:
            worklist = myfile.read()
            print(worklist)
            for alert_name in alert_names:

                if alert_name.encode('ascii', 'ignore') not in worklist:
                    print("Alert name not found")
                    return False

    return True

def _verifyAlertDownloads(browserobj, filetype):
    browserobj.click(selector=CSS_ALERT_EXPAND_MENU)
    time.sleep(2)

    browserobj.click(selector=CSS_ALERT_GOTO_DETAIL)
    browserobj.switchToLatestWindow()
    waitLoadProgressDone(browserobj)

    device_name = browserobj.getText(selector=CSS_ALERT_DETAILS_DEVICE_TITLE)
    alert_name = browserobj.getText(selector=CSS_ALERT_DETAIL_POLICY)

    browserobj.click(selector=CSS_ALERT_ACTION_MENU)
    time.sleep(1)
    browserobj.click(selector=CSS_ALERT_ACTION_DOWNLOAD)
    time.sleep(1)
    if(filetype == "pdf"):
        browserobj.click(selector=CSS_PDF_DOWNLOAD)
    elif(filetype == "xlsx"):
        browserobj.click(selector=CSS_XLS_DOWNLOAD)
    time.sleep(8)
    downloc = browserobj.downloadFilepath
    os.chdir(downloc)
    if filetype == "pdf":
        reader = ReadFile()
        if len(glob.glob("*.pdf")) == 0:
            print("Error: File not found")
            return False
        myfile = glob.glob("*.pdf")[0]
        text = reader.parseScannedPDF(myfile)
        if fuzzyRegexSearch(text, alert_name, 8) is None: #Check for title
            print(text)
            print("PDF check failed")
            return False

    elif filetype == "xlsx":
        if len(glob.glob("*.xlsx")) == 0: #Only alert name is in there
            print("XLS file not found")
            return False
        with open(glob.glob("*.xlsx")[0]) as myfile:
            worklist = myfile.read()
            if alert_name.encode('ascii', 'ignore') not in worklist:
                print("Alert name not found")
                return False

    return True

def verifyAlertRowsPerPage(browserobj):
    rcode = True

    expectedRowsPerPage = _getExpectedAlertsCountInPage(browserobj)
    alertsCount = _getAlertsCountInPage(browserobj)
    rcode = rcode and alertsCount == expectedRowsPerPage

    newPageSize = 25
    _changePageSize(browserobj, newPageSize)
    pageSize = int(browserobj.getText(selector=CSS_ALERT_CURRENT_PAGE_SIZE))
    if pageSize != newPageSize:
        print('Alert page size is not displaying correctly after changed')
        rcode = False

    expectedRowsPerPage = _getExpectedAlertsCountInPage(browserobj)
    alertsCount = _getAlertsCountInPage(browserobj)
    rcode = rcode and alertsCount == expectedRowsPerPage

    return rcode

def _getExpectedAlertsCountInPage(browserobj):
    description = browserobj.getText(selector=CSS_ALERT_ROWS_PER_PAGE_DESCRIPTION_TEXT) # e.g. 1-50 of 1000
    array_of_match = re.findall(r'\d+', description)
    if array_of_match == None or len(array_of_match) < 2:
        print('Alert rows per page description does not contain number')
        return -1
    count = int(array_of_match[1]) - int(array_of_match[0]) + 1
    return count

def _getAlertsCountInPage(browserobj):
    count = 0
    titles = _getAlertPoliciesTitle(browserobj)
    for title in titles:
        array_of_match = re.findall(r'\d+', title)
        if array_of_match == None:
            print('Alert policy title does not contain count number')
            return -1
        count += int(array_of_match[-1])
    return count

def _changePageSize(browserobj, size=25):
    browserobj.click(selector=CSS_ALERT_PAGE_SIZE_DROPDOWN)

    selector = CSS_ALERT_PAGE_SIZE_FORMATTED_STR.format(size)
    browserobj.click(selector=selector)

    waitLoadProgressDone(browserobj)

def _getAlertPoliciesTitle(browserobj):
    params = {}
    params["selector"] = CSS_SELECTOR_ALERT_POLICY_TITLE
    titles = []
    titleElements = browserobj.findMultiCSS(**params)
    for title in titleElements:
        titles.append(title.text)
    return titles

def verifyAlertPageChange(browserobj):
    titlesBeforePageChange = _getAlertPoliciesTitle(browserobj)
    browserobj.click(selector=CSS_ALERT_NEXT_PAGE_BUTTON)
    titlesAfterPageChange = _getAlertPoliciesTitle(browserobj)
    equal = compareStringLists(titlesBeforePageChange, titlesAfterPageChange)
    return not equal

def verifyAlertDetailsLinks(browserobj):
    rcode = True
    kwargs = {}

    # 'More details' button
    kwargs['titleSelector'] = CSS_SELECTOR_ALERT_POLICY_TITLE
    kwargs['buttonSelector'] = CSS_ALERT_DETAILS_MORE_DETAILS_BUTTON
    kwargs['verifyingTitleSelector'] = CSS_ALERT_DETAILS_MORE_DETAILS_TITLE
    rcode = rcode and _verifyAlertDetailsButton(browserobj, **kwargs)

    # Device button
    kwargs['titleSelector'] = CSS_ALERT_DETAILS_DEVICE_BUTTON
    kwargs['buttonSelector'] = CSS_ALERT_DETAILS_DEVICE_BUTTON
    kwargs['verifyingTitleSelector'] = CSS_ALERT_DETAILS_DEVICE_TITLE
    rcode = rcode and _verifyAlertDetailsButton(browserobj, **kwargs)

    # Protocol button
    kwargs['titleSelector'] = CSS_ALERT_DETAILS_PORTOCOL_BUTTON
    kwargs['buttonSelector'] = CSS_ALERT_DETAILS_PORTOCOL_BUTTON
    kwargs['verifyingTitleSelector'] = CSS_ALERT_DETAILS_PORTOCOL_TITLE

    params = {"selector" : CSS_ALERT_SEVERITY_DROPDOWN}
    browserobj.click(**params)
    time.sleep(1)
    params["selector"] = CSS_ALERT_SEVERITY_WARNING
    browserobj.click(**params)

    rcode = rcode and _verifyAlertDetailsButton(browserobj, **kwargs)

    return rcode

def _verifyAlertDetailsButton(browserobj, **kwargs):
    browserobj.click(selector=CSS_SELECTOR_ALERT_POLICY_TITLE)
    time.sleep(2)

    title = browserobj.getText(selector=kwargs['titleSelector'])

    browserobj.click(selector=kwargs['buttonSelector'])
    time.sleep(2)

    verifyingTitle = browserobj.getText(selector=kwargs['verifyingTitleSelector'])
    if not verifyingTitle: 
        print("Not able to find Title {}".format(kwargs['verifyingTitleSelector']))
        return False
    
    browserobj.goBack()
    time.sleep(2)

    return verifyingTitle in title

def verifyAlertDetailsPageInfo(browserobj):
    rcode = True
    params = {"selector" : CSS_ALERT_SEVERITY_DROPDOWN}
    browserobj.click(**params)
    time.sleep(1)
    params["selector"] = CSS_ALERT_SEVERITY_WARNING
    browserobj.click(**params)
    browserobj.click(selector=CSS_SELECTOR_ALERT_POLICY_TITLE)
    waitLoadProgressDone(browserobj)
    browserobj.click(selector=CSS_ALERT_DETAILS_MORE_DETAILS_BUTTON)
    waitLoadProgressDone(browserobj)

    rcode = rcode and verifyAlertNumbers(browserobj, selector=CSS_SELECTOR_ALTER_DETAILS_NUMBER)

    ipAddress = browserobj.getText(selector=CSS_ALERT_DETAILS_SRC_IP_ADDRESS)
    rcode = rcode and isValidIPv4Address(ipAddress)

    macAddress = browserobj.getText(selector=CSS_ALERT_DETAILS_MAC_ADDRESS)
    rcode = rcode and isValidMACAddress(macAddress)

    #rcode = rcode and _verifyAlertDetailsIoTScore(browserobj)
    rcode = rcode and _verifyTrafficInfo(browserobj)

    return rcode

def verifyAlertSourceIP(browserobj, src):
    browserobj.click(selector=CSS_SELECTOR_ALERT_POLICY_TITLE)
    waitLoadProgressDone(browserobj)
    browserobj.click(selector=CSS_ALERT_DETAILS_MORE_DETAILS_BUTTON)
    waitLoadProgressDone(browserobj)

    ipAddress = browserobj.getText(selector=CSS_ALERT_DETAILS_SRC_IP_ADDRESS)
    if isValidIPv4Address(ipAddress) and ipAddress == src:
        return True
    else:
        return False

def verifyAlertDestIP(browserobj, dest):
    browserobj.click(selector=CSS_SELECTOR_ALERT_POLICY_TITLE)
    waitLoadProgressDone(browserobj)

    ipAddress = browserobj.getText(selector=CSS_ALERT_DETAILS_DEST_IP_ADDRESS)
    if isValidIPv4Address(ipAddress) and ipAddress == dest:
        return True
    else:
        return False


def _verifyAlertDetailsIoTScore(browserobj):
    scoreText = browserobj.getText(selector=CSS_ALERT_DETAILS_IOT_SCORE)
    try:
        score = int(scoreText)
        if score < 0:
            print('Alert details page IoT score is smaller than 0')
            return False
    except:
        print('Alert details page IoT score is not a valid number')
        return False
    return True

def _verifyTrafficInfo(browserobj):
    params = {}
    params["selector"] = CSS_ALERT_DETAILS_TRAFFIC_INFO_CHIP
    rcode = True
    for e in browserobj.findMultiCSS(**params):
        browserobj.hoverElement(e, **params)
        time.sleep(1)
        text = browserobj.getText(selector=CSS_ALERT_DETAILS_TRAFFIC_TOOLTIP_TEXT)
        try:
            num = int(text)
            if num < 0:
                rcode = False
        except:
            print('Traffic info chip not showing number, ignored')
    return rcode


def verifyAlertNumbers (browserobj, selector=CSS_SELECTOR_ALERT_NUMBER):
    params = {}
    params["selector"] = selector
    for e in browserobj.findMultiCSS(**params):
        try:
            d = int(e.text)
        except ValueError:
            print(e.text + " is not an integer")
            return False
    return True

def verifyAlertExport(browserobj, filetype):
    browserobj.click(selector=CSS_SELECT_ALL_ALERTS_CHECKBOX)
    exportBtn = CSS_DOWNLOAD_SELECTED_INVENTORY_BUTTON
    messageSelector = CSS_DOWNLOAD_SELECTED_INVENTORY_INPROGRESS_MESSAGE
    params = {"selector": exportBtn, "waittype":"visibility", "timeout":10}
    rcode = browserobj.click(**params)
    if not rcode:
        print("Fail to click on export button")
        return False

    msg = browserobj.getText(selector=CSS_SELECTED_ALERTS_NUM_TEXT)
    nums = [int(s) for s in msg.split() if s.isdigit()]
    if len(nums) < 1:
        print('zbUIAlerts.py/verifyAlertExport: No numbers in CSS_SELECTED_ALERTS_NUM_TEXT.')
        return False
    elif nums[0] < 1:
        print(('zbUIAlerts.py/verifyAlertExport: CSS_SELECTED_ALERTS_NUM_TEXT shows an invalid count {}.'.format(nums[0])))
        return False
    successDom = browserobj.findSingleCSS(
        selector=CSS_DOWNLOAD_SELECTED_INVENTORY_SUCCESS_DOM,
        timeout=3,
        err_msg='CSS_DOWNLOAD_SELECTED_INVENTORY_SUCCESS_DOM not found'
    )
    if not successDom:
        return False
    return True


def verifyAlertsEntries (browserobj):
    params = {}
    params["selector"] = CSS_SELECTOR_ALERT_POLICY_TITLE
    alertLen = browserobj.findMultiCSS(**params)
    alertLen = [i.text[i.text.find("(")+1:i.text.find(")")] for i in alertLen]
    print (alertLen)
    params["selector"] = CSS_SELECTOR_ALERT_POLICY_DROPDOWN
    for e in browserobj.findMultiCSS(**params):
        e.click()
        time.sleep(2)
        e.click()
        time.sleep(2)
    return True

def clickAllAlertDropdownOptions (browserobj):
    params = {}
    params["selector"] = CSS_SELECTOR_ALERT_DROPDOWN
    for e in browserobj.findMultiCSS(**params):
        e.click()
        time.sleep(1)
        params["selector"] = CSS_SELECTOR_ALERT_DROPDOWN_OPTIONS
        for el in browserobj.findMultiCSS(**params):
            time.sleep(1)
            el.click()
            rcode = waitLoadProgressDone(browserobj)
            yield rcode
            e.click()
        time.sleep(1)
        browserobj.findSingleCSS(**params).send_keys(Keys.ESCAPE)


def filterStatusAlert(browserobj, status):
    params = {"selector": CSS_ALERT_STATUS_DROPDOWN, "waittype":"clickable", "timeout":3}
    browserobj.click(**params)

    if status.lower() == "pending":  
        css = CSS_ALERT_STATUS_PENDING
        cssPagePattern = CSS_ALERT_PAGE_PENDING
    if status.lower() == "resolved":  
        css = CSS_ALERT_STATUS_RESOLVED
        cssPagePattern = CSS_ALERT_PAGE_RESOLVE
    if status.lower() == "all":  
        css = CSS_ALERT_STATUS_ALL
        cssPagePattern = CSS_ALERT_PAGE_ALL
    if status.lower() == "ignored":  
        css = CSS_ALERT_STATUS_IGNORED
        cssPagePattern = CSS_ALERT_PAGE_IGNORE
    if status.lower() == "siem":  
        css = CSS_ALERT_STATUS_SENDTOSIEM
        cssPagePattern = CSS_ALERT_PAGE_SIEM
    if status.lower() == "workorder":  
        css = CSS_ALERT_STATUS_WORKORDERCREATED
        cssPagePattern = CSS_ALERT_PAGE_AIMS
    if status.lower() == "internal":  
        css = CSS_ALERT_STATUS_INTERNAL
        cssPagePattern = CSS_ALERT_PAGE_INTERNAL

    params = {"selector":css, "waittype":"clickable", "timeout":3}
    browserobj.click(**params)
    params = {"selector":cssPagePattern, "waittype":"visibility", "timeout":15}
    rcode = browserobj.findSingleCSS(**params)
    return rcode


def findAlertTotalCount(browserobj):
    params = {"selector": CSS_ALERT_COUNT_TOTAL, "waittype":"visibility", "timeout":30}
    rcode = browserobj.findSingleCSS(**params)
    match = re.search('\((\d+)\)', rcode.text)
    alertCount = int(match.group(1))
    return alertCount




def setAlertAction(host, browserobj, alertname, status, action, **kwargs):
    global alert_action_comment, alert_description, rule_name
    origAlertCount = None

    actions_payload = {
        'resolve': {
            'css': CSS_ALERT_ACTION_RESOLVE,
            'comment_input': CSS_ALERT_ACTION_RESOLVE_COMMENT,
            'button': CSS_ALERT_ACTION_RESOLVE_BUTTON,
            'status': 'resolved'
        },
        
        'block': {
            'css': CSS_ALERT_ACTION_BLOCK,
            'comment_input': CSS_ALERT_ACTION_COMMENT,
            'button': CSS_ALERT_ACTION_BLOCK_BUTTON
        },
        'siem': {
            'css': CSS_ALERT_ACTION_SIEM, #md-option[value='siem']
            'comment_input': CSS_ALERT_ACTION_COMMENT,
            'button': CSS_ALERT_ACTION_SIEM_BUTTON,
            'status': 'siem'
        },
        'aims': {
            'css': CSS_ALERT_ACTION_AIMS,
            'comment_input': CSS_ALERT_ACTION_COMMENT,
            'button': CSS_ALERT_ACTION_AIMS_BUTTON,
            'status': 'workorder'
        },
        'ignore': {
            'css': CSS_ALERT_ACTION_IGNORE,
            'comment_input': CSS_ALERT_ACTION_COMMENT,
            'button': None,
            'status': 'ignored'
        },
        'connectiv': {
            'css': CSS_ALERT_ACTION_CONNECTIV,
            'comment_input': CSS_ALERT_ACTION_COMMENT,
            'button': CSS_ALERT_ACTION_AIMS_BUTTON,
            'status': 'workorder'
        },

        'assign': {
            'css': CSS_ALERT_ACTION_ASSIGN,
            'comment_input': CSS_ALERT_ACTION_COMMENT_ASSIGN,
            'email': CSS_ALERT_EMAIL_FIELD,
            'button': CSS_ALERT_ACTION_ASSIGN_BUTTON
        },
        'add notes': {
            'css': CSS_ALERT_ACTION_ADD_NOTES,
            'comment_input': CSS_ALERT_NOTE_INPUT,
            'button': CSS_ALERT_ACTION_NOTE_BUTTON
        }
    }


    if action.lower() not in actions_payload:
        print(('Alert action {0} is not valid in setAlertAction function'.format(action.lower())))
        return False

    css = actions_payload[action.lower()]['css']
    button = actions_payload[action.lower()]['button']
    commentInput = actions_payload[action.lower()]['comment_input']


    if action.lower() != 'block' and action.lower() != 'assign' and action.lower() != 'add notes':
        _status = actions_payload[action.lower()]['status']
        filterStatusAlert(browserobj, status=_status)
        origAlertCount = findAlertTotalCount(browserobj)
        filterStatusAlert(browserobj, status=status)

    # find alertname
    params = {"selector": CSS_ALERT_NAME, "waittype":"clickable", "timeout":10}
    rcode = browserobj.findMultiCSS(**params)
    if not rcode:
        print("Alert page not able to find any alert")
        return False
    for name in rcode:
        if alertname.strip().lower() in alertname.lower():
            time.sleep(1)
            name.click()
            waitLoadProgressDone(browserobj)
            params = {"selector":CSS_ALERT_SINGLE, "waittype":"visibility", "timeout":3} # Do not set browserobj, it breaks everything
            rcode = browserobj.findMultiCSS(**params)
            if not rcode:
                print("No alerts found")
                return False
            alert = rcode[0]
            alert_description = browserobj.getText(selector=CSS_ALERT_DESCRIPTION)
            params = {"browserobj":alert, "selector":CSS_ALERT_SINGLE_CHECKBOX, "waittype":"visibility", "timeout":3}
            browserobj.click(**params)
            #Need to change the below part

        if action.lower() == 'aims' or action.lower() == 'firewall' or action.lower() == 'connectiv' or action.lower == 'resolve':
            params = {"browserobj":alert, "selector":CSS_ALERT_SINGLE_ACTION_DROPDOWN, "waittype":"visibility", "timeout":3}
            browserobj.click(**params)

        moi = browserobj.findSingleCSS(selector=CSS_ALERT_MORE_DETAILS)
        moi.click()
        waitLoadProgressDone(browserobj)
        params = {"selector":css, "waittype":"visibility", "timeout":5}
        browserobj.click(**params)
        time.sleep(1)
        alert_action_comment = 'zbat comment at {0}'.format(time.time())
        params = {"selector":commentInput, "text":alert_action_comment, "waittype":"visibility", "timeout":5}
        try:
            browserobj.sendKeys(**params)                                                       
        except:
            pass
 
        time.sleep(1)

        if action.lower() == 'aims':
            _setAIMSAlertActionConfig(browserobj)
        elif action.lower() == 'block':
            params = {"selector":button, "text":"zbat comment", "waittype":"visibility", "timeout":5}
            browserobj.click(**params)
            waitLoadProgressDone(browserobj)
            rule_name = browserobj.getText(selector=CSS_BLOCK_ACL_RULE_NAME)
        elif action.lower() == 'connectiv':
            if browserobj.findSingleCSS(selector=CSS_AIMS_ALERT_ACTION_PRIORITY_DROPDOWN, timeout=3) or browserobj.findSingleCSS(selector=CSS_AIMS_ALERT_ACTION_ASSIGNEE_DROPDOWN, timeout=3):
                print('zbUIAlerts/setAlertAction: Found priority or assignee dropdown in connectiv test for alert')
                return False
        elif action.lower() == 'resolve':
            res = _setResolveActionConfig(browserobj)
            if not res:
                print('zbUIAlerts.py/setAlertAction: Not able to configure resolve actions')
                return False
            params = {"selector":button, "text":"zbat comment", "waittype":"visibility", "timeout":5}
            browserobj.click(**params)
            waitLoadProgressDone(browserobj)
            host.gotoAlerts()
        elif action.lower() == 'add notes':
            params = {"selector":button, "text":"zbat comment", "waittype":"visibility", "timeout":5}
            browserobj.click(**params)
            waitLoadProgressDone(browserobj)
            alert_action_list = browserobj.findMultiCSS(selector=CSS_ALERT_ACTION_LIST)
            for alert in alert_action_list:
                if alert.text == alert_action_comment:
                    return True
            return False
        elif action.lower() == 'assign': #The assign option
            email = browserobj.findSingleCSS(selector=actions_payload[action.lower()]['email']) #Gets the email from the dictionary and enters it
            email_address = "zbatc"
            email.send_keys(email_address)
            params = {"selector" : CSS_ALERT_EMAIL_AUTOFILL}
            browserobj.findSingleCSS(**params).click()
            params = {"selector":button, "text":"zbat comment", "waittype":"visibility", "timeout":5}
            browserobj.click(**params)
            waitLoadProgressDone(browserobj)
            alert_action_list = browserobj.findMultiCSS(selector=CSS_ALERT_ACTION_LIST)
            time.sleep(1)
            for alert in alert_action_list:
                if re.search(alert_action_comment, alert.text) is not None:
                    return True
            return False
        #params = {"selector":button, "text":"zbat comment", "waittype":"visibility", "timeout":5}
        #browserobj.click(**params)
        #waitLoadProgressDone(browserobj)
        # certain alert action don't close modal.  Have to close it manually.
        if action.lower() in ["siem"]:
            params = {"selector":CSS_SENDTO_BUTTON, "waittype":"visibility", "timeout":5}
            browserobj.click(**params)
            params["selector"] = CSS_ALERT_SIEM_SENDTO
            browserobj.click(**params)

            alert_action_comment = 'zbat comment at {0}'.format(time.time())
            params = {"selector":commentInput, "text":alert_action_comment, "waittype":"visibility", "timeout":5}
            try:
                browserobj.sendKeys(**params)                                                       
            except:
                pass
            params = {"selector":button, "text":"zbat comment", "waittype":"visibility", "timeout":5}
            browserobj.click(**params)
            waitLoadProgressDone(browserobj)


            browserobj.goBack()

            exitActionModal(browserobj)
        break
 
    # calculating final count
    # there is no filter for block
    if action.lower() != 'block':
        _status = actions_payload[action.lower()]['status']
        rcode = filterStatusAlert(browserobj, status=_status)
        if not rcode:
            print("Not able to go to Alert {0} page.".format(action))
            return False

    # for special case like send to FW, we don't have filter for it, so no where to check count.  Just return true in this case    
    if not origAlertCount: return True

    nowAlertCount = findAlertTotalCount(browserobj)
    filterStatusAlert(browserobj, status=status)

    # compare count to make sure that it's decrement after action 
    if nowAlertCount == '':
        print("Alert count not found")
        return False

    if nowAlertCount == origAlertCount:
        print("Alert count did not change after resolve action.")
        return False
    else:
        return True

def verifyAlertActionEditPolicy(browserobj):
    try:
        _changePageSize(browserobj, 200)
        _expandAlertWithType(browserobj, 'policy_alert')
        _selectActionDropdown(browserobj)
        _selectEditPolicy(browserobj)
    except Exception as err:
        print(err)
        print('zbUIAlerts/verifyAlertActionEditPolicy: Alert page not able to open edit policy widget.')
        return False

    originalPolicyProfile = _capturePolicyStates(browserobj)

    newPolicyProfile = Policy_Profile()
    newPolicyProfile.set_severity('Info')
    newPolicyProfile.set_policy_name('Dummy name')
    newPolicyProfile.set_enabled(not originalPolicyProfile.enabled)
    newPolicyProfile.set_notify_on_black_list(not originalPolicyProfile.notify_on_black_list)
    newPolicyProfile.set_behavior(originalPolicyProfile.behavior)
    newPolicyProfile.set_weekly_schedule([
        True,
        False,
        False,
        True,
        False,
        False,
        True
    ])
    newPolicyProfile.set_protocols(['chrome'])
    notifying_emails = list(set(originalPolicyProfile.notifying_emails) - set(['zbat@zingbox.com'])) + ['zbat@zingbox.com']
    newPolicyProfile.set_notifying_emails(notifying_emails)
    try:
        _modifyPolicyProfile(browserobj, newPolicyProfile)
    except Exception as error:
        print('zbUIAlerts/verifyAlertActionEditPolicy: Not able to modify policy.')
        print(('Error: {}'.format(error)))
        return False

    try:
        _selectActionDropdown(browserobj)
        _selectEditPolicy(browserobj)
    except:
        print('zbUIAlerts/verifyAlertActionEditPolicy: Alert page not able to open edit policy widget.')
        return False

    updatedPolicyProfile = _capturePolicyStates(browserobj)

    # Restore original policy profile
    try:
        _modifyPolicyProfile(browserobj, originalPolicyProfile)
    except Exception as error:
        print('zbUIAlerts/verifyAlertActionEditPolicy: Not able to modify policy.')
        print(('Error: {}'.format(error)))
        return False

    # Check equality
    assert newPolicyProfile.equal(updatedPolicyProfile) == True
    assert originalPolicyProfile.equal(updatedPolicyProfile) == False

    return True

def _modifyPolicyProfile(browserobj, policy_profile):
    browserobj.click(selector=CSS_ALERT_POLICY_SEVERITY)
    time.sleep(1)
    selector = CSS_ALERT_POLICY_SEVERITY_OPTION.format(policy_profile.severity)
    browserobj.click(selector=selector)

    params = {}
    params["timeout"] = 3
    params["waittype"] = "visibility"
    params["selector"] = CSS_ALERT_POLICY_NAME
    name_input = browserobj.findSingleCSS(**params)
    if not name_input:
        raise Exception('zbUIAlerts/_modifyPolicyProfile: cannot find policy name input.')
    name_input.clear()
    name_input.send_keys(policy_profile.policy_name)
    browserobj.pressKey(key=Keys.TAB)

    selector = CSS_ALERT_POLICY_ENABLED
    enabled = browserobj.getAttribute(selector=selector, attribute='aria-checked')
    if policy_profile.enabled != bool(enabled == 'true'):
        browserobj.click(selector=selector)

    selector = CSS_ALERT_POLICY_NOTIFY_RADIO_BUTTON
    if policy_profile.notify_on_black_list == False:
        selector = CSS_ALERT_POLICY_NOTIFY_WHITELIST_RADIO_BUTTON
    params = {}
    params["selector"] = selector
    radio_btn = browserobj.findSingleCSS(**params)
    radio_btn.click()
    '''
    params["selector"] = CSS_ALERT_POLICY_REMOVE_TAGS
    tags = browserobj.findMultiCSS(**params)
    if tags:
        for tag in tags:
            tag.click()
            radio_btn.click()

    behaviors = [
        policy_profile.behavior['group_1'],
        policy_profile.behavior['group_2'],
        policy_profile.protocols
    ]
    options = [
        CSS_ALERT_POLICY_BEHAVIOR_GROUP_1_OPTION,
        CSS_ALERT_POLICY_BEHAVIOR_GROUP_2_OPTION,
        CSS_ALERT_POLICY_PROTOCOLS_OPTION
    ]
    params["selector"] = CSS_ALERT_POLICY_BEHAVIOR_INPUT
    inputFields = browserobj.findMultiCSS(**params)
    if inputFields:
        for inputField in inputFields:
            _inputBehaviors(browserobj, inputField, behaviors.pop(0), options.pop(0))
    '''
    time.sleep(3)
    radio_btn.click()
    params["selector"] = CSS_ALERT_POLICY_WORKING_DAYS_BUTTON
    elements = browserobj.findMultiCSS(**params)
    for i in range(0, len(elements)):
        element = elements[i]
        classes = str(element.get_attribute('class'))
        if bool(policy_profile.weekly_schedule[i]) != bool('active' in classes):
            element.click()

    params["selector"] = CSS_ALERT_POLICY_NOTIFY_EMAIL_INPUT
    email_input = browserobj.findSingleCSS(**params)
    if not email_input:
        raise Exception('zbUIAlerts/_modifyPolicyProfile: cannot find policy notify email input.')
    for email in policy_profile.notifying_emails:
        email_input.clear()
        email_input.send_keys(email)
        email_input.send_keys(Keys.ENTER)

    browserobj.click(selector=CSS_ALERT_POLICY_UPDATE_BUTTON)
    time.sleep(3)

def _inputBehaviors(browserobj, inputField, behaviors, option):
    if not inputField:
        raise Exception('zbUIAlerts/_modifyPolicyProfile: cannot find policy behavior input field.')
    for behavior in behaviors:
        inputField.send_keys(behavior)
        browserobj.click(selector=option)

def _expandAlert(browserobj):
    params = {"selector": CSS_ALERT_NAME}
    rcode = browserobj.findSingleCSS(**params)
    if not rcode:
        raise Exception('zbUIAlerts/_expandAlert: Alert page not able to find any alerts.')
    rcode.click()

def _expandAlertWithType(browserobj, alert_type='policy_alert'):
    alert_type_indicator_css = CSS_ALERT_ACTION_EDIT_POLICY
    if alert_type == 'threat_alert':
        alert_type_indicator_css = CSS_ALERT_ACTION_IGNORE

    params = {
        'selector': CSS_ALERT_NAME,
        'waittype': 'visibility',
        'timeout': 3
    }
    alert_names_btn = browserobj.findMultiCSS(**params)
    if not alert_names_btn:
        raise Exception('zbUIAlerts/_expandAlertWithType: Alert page not able to find any alerts.')
    for alert_name_btn in alert_names_btn:
        alert_name_btn.click()
        _selectActionDropdown(browserobj)
        params["selector"] = alert_type_indicator_css
        alert_type_indicator = browserobj.findSingleCSS(**params)
        kwargs = {"selector":CSS_ALERT_ACTION_RESOLVE, "waittype":"visibility", "timeout":5}
        browserobj.click(**kwargs)
        browserobj.pressKey(key=Keys.ESCAPE)
        time.sleep(1)
        if not alert_type_indicator:
            alert_name_btn.click()
            time.sleep(0.5)
            continue
        else:
            return
    raise Exception('zbUIAlerts/_expandAlertWithType: No alert with type {} can be expanded.'.format(alert_type))

def _selectActionDropdown(browserobj):
    params = {
        "selector": CSS_ALERT_SINGLE_ACTION_DROPDOWN,
        "waittype": "visibility",
        "timeout": 3
    }
    rcode = browserobj.findSingleCSS(**params)
    if not rcode:
        raise Exception('zbUIAlerts/_selectActionDropdown: Alert page not able to find any action dropdown.')
    rcode.click()

def _selectEditPolicy(browserobj):
    params = {
        "selector": CSS_ALERT_ACTION_EDIT_POLICY,
        "waittype": "visibility",
        "timeout": 3
    }
    rcode = browserobj.findSingleCSS(**params)
    if not rcode:
        raise Exception('zbUIAlerts/_selectEditPolicy: Alert page not able to find any edit policy button.')
    rcode.click()

def _capturePolicyStates(browserobj):
    policy_profile = Policy_Profile()

    severity = browserobj.getText(selector=CSS_ALERT_POLICY_SEVERITY)
    policy_profile.set_severity(severity)

    name = browserobj.getAttribute(selector=CSS_ALERT_POLICY_NAME, attribute='value')
    policy_profile.set_policy_name(str(name))

    enabled = browserobj.getAttribute(selector=CSS_ALERT_POLICY_ENABLED, attribute='aria-checked')
    policy_profile.set_enabled(enabled == 'true')

    notify_on_black_list = browserobj.getAttribute(selector=CSS_ALERT_POLICY_NOTIFY_RADIO_BUTTON, attribute='aria-checked')
    policy_profile.set_notify_on_black_list(notify_on_black_list == 'true')

    params = {}
    params["timeout"] = 3
    params["waittype"] = "visibility"
    params["selector"] = CSS_ALERT_POLICY_BEHAVIOR_GROUP_1
    group_1_behaviors = []
    behavior_elements = browserobj.findMultiCSS(**params)
    if behavior_elements:
        for element in behavior_elements:
            group_1_behaviors.append(str(element.text))

    params["selector"] = CSS_ALERT_POLICY_BEHAVIOR_GROUP_2
    group_2_behaviors = []
    behavior_elements = browserobj.findMultiCSS(**params)
    if behavior_elements:
        for element in behavior_elements:
            group_2_behaviors.append(str(element.text))
    behavior = {
        'group_1': group_1_behaviors,
        'group_2': group_2_behaviors
    }
    policy_profile.set_behavior(behavior)

    params["selector"] = CSS_ALERT_POLICY_PROTOCOLS
    protocols = []
    behavior_elements = browserobj.findMultiCSS(**params)
    if behavior_elements:
        for element in behavior_elements:
            protocols.append(str(element.text))
    policy_profile.set_protocols(protocols)

    params["selector"] = CSS_ALERT_POLICY_WORKING_DAYS_BUTTON
    weekly_schedule = []
    elements = browserobj.findMultiCSS(**params)
    for element in elements:
        classes = str(element.get_attribute('class'))
        weekly_schedule.append('active' in classes)
    policy_profile.set_weekly_schedule(weekly_schedule)

    '''
    params["selector"] = CSS_ALERT_POLICY_DURATION_SLIDER_THUMB
    percentages = []
    elements = browserobj.findMultiCSS(**params)
    for element in elements:
        style = str(element.get_attribute('style'))
        percentages.append(int(re.findall(r'\b\d+\b', style)[0]))
    policy_profile.set_duration_percentages(percentages[0], percentages[1])
    '''

    params["selector"] = CSS_ALERT_POLICY_NOTIFY_EMAIL
    emails = []
    email_elements = browserobj.findMultiCSS(**params)
    if email_elements:
        for email in email_elements:
            emails.append(str(email.text))
    policy_profile.set_notifying_emails(emails)

    return policy_profile

def exitActionModal(browserobj):
    #kwargs = {"selector": CSS_SELECTOR_OUTSIDE_ACTION_MODAL}
    kwargs = {"selector": CSS_ALERT_ACTION_CANCEL_BUTTON, "waittype":"clickable", "timeout": 5}
    rcode = browserobj.click(**kwargs)
    waitLoadProgressDone(browserobj)

def _setResolveActionConfig(browserobj):
    browserobj.click(
        selector=CSS_ALERT_RESOLVE_NO_ACTION_NEEDED_BTN,
        err_msg='zbUIAlerts.py/_setResolveActionConfig: Not able to click "No Action Needed" button.'
    )
    switches = browserobj.findMultiCSS(
        selector=CSS_ALERT_RESOLVE_ACTION_SWITCHES,
        err_msg='zbUIAlerts.py/_setResolveActionConfig: Not able to find any switches.'
    )
    if not switches:
        return False
    options = [True, True, False, False]
    random.shuffle(options)
    for switch in switches:
        option = options.pop()
        if option is True:
            switch.click()
    return True

def _setAIMSAlertActionConfig(browserobj):
    global alert_action_priority, alert_action_assignee
    # Select 'priority' and 'assigned to from dropdown
    browserobj.click(
        selector=CSS_AIMS_ALERT_ACTION_PRIORITY_DROPDOWN,
        err_msg='zbUIAlerts.py/_setAIMSAlertActionConfig: Not able to click priority dropdown CSS_AIMS_ALERT_ACTION_PRIORITY_DROPDOWN'
    )
    selector = CSS_AIMS_ALERT_ACTION_PRIORITY_OPTION
    alert_action_priority = browserobj.getText(
        selector=selector,
        err_msg='zbUIAlerts.py/_setAIMSAlertActionConfig: Not able to get text from priority dropdown CSS_AIMS_ALERT_ACTION_PRIORITY_OPTION'
    )
    browserobj.click(
        selector=selector,
        err_msg='zbUIAlerts.py/_setAIMSAlertActionConfig: Not able to click priority dropdown CSS_AIMS_ALERT_ACTION_PRIORITY_OPTION'
    )

    browserobj.click(
        selector=CSS_AIMS_ALERT_ACTION_ASSIGNEE_DROPDOWN,
        err_msg='zbUIAlerts.py/_setAIMSAlertActionConfig: Not able to click assignee dropdown CSS_AIMS_ALERT_ACTION_ASSIGNEE_DROPDOWN'
    )
    selector = CSS_AIMS_ALERT_ACTION_ASSIGNEE_OPTION
    alert_action_assignee = browserobj.getText(
        selector=selector,
        err_msg='zbUIAlerts.py/_setAIMSAlertActionConfig: Not able to get text from assignee dropdown CSS_AIMS_ALERT_ACTION_ASSIGNEE_OPTION'
    )
    browserobj.click(
        selector=selector,
        err_msg='zbUIAlerts.py/_setAIMSAlertActionConfig: Not able to click assignee dropdown CSS_AIMS_ALERT_ACTION_ASSIGNEE_OPTION'
    )

def _getLatestActionFromAIMSServer(**kwargs):
    server = kwargs['server']
    token = kwargs['token']
    facility = kwargs['facility']
    tag = kwargs['tag']
    earliest = '2010-01-01T00:00:00.000000'
    latest = datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%S.%f')

    obj = AIMS(server, token)
    result = obj.findWorkOrder(facility, tag, earliest, latest)

    if type(result) != list:
        print('Results from AIMS server is not in list format')
        return []

    return result[-1]

def _getLatestActionFromSIEMServer(**kwargs):
    base_url = 'https://{0}:{1}'.format(kwargs['host'], kwargs['port'])
    username = kwargs['splunk_username']
    password = kwargs['splunk_pwd']
    splunk_client = Splunk(base_url, username, password)
    result = splunk_client.search(limit=1)
    try:
        result = json.loads(result)
    except:
        print(('zbUIAlerts.py/_getLatestActionFromSIEMServer: Result from SIEM server is not in json string format {}'.format(result)))
        return {}
    if type(result) != dict:
        return {}
    return result

def _getLatestPolicyFromPANFW(**kwargs):
    host = kwargs['host']
    username = kwargs['panfw_username']
    password = kwargs['panfw_pwd']
    panfw_client = PanFW(host, username, password)
    policies = panfw_client.findSecurityPolicies()
    if type(policies) != list or len(policies) < 1:
        print(('zbUIAlerts.py/_getLatestPolicyFromPANFW: Result from PANFW is not in valid format or no records found {}'.format(policies)))
        return {}
    return policies[0]

def _getLatestConnectivSecurityEvent(**kwargs):
    uname = kwargs['connectiv_uname']
    pwd = kwargs['connectiv_pwd']
    client_id = kwargs['connectiv_client_id']
    client_secret = kwargs['connectiv_client_secret']
    client_url = kwargs['connectiv_client_url']
    connectiv = Connectiv(
      client_url,
      uname,
      pwd,
      client_id,
      client_secret
    )
    events = connectiv.getSecurityEvent()
    return events[0]


class Alerts():
    def __init__(self, **kwargs):
        self.params = kwargs
        self.selenium = Login(**kwargs).login()

    def gotoAlerts(self):
        url = urlparse(self.params["url"])
        rcode = self.selenium.getURL(url.scheme+'://'+url.netloc+'/policiesalerts/alerts')
        waitLoadProgressDone(self.selenium)

    def gotoAssetManagement(self):
        url = urlparse(self.params["url"])
        rcode = self.selenium.getURL(url.scheme+'://'+url.netloc+'/administration/assetmanagement')
        waitLoadProgressDone(self.selenium)

    def checkTimeSeries(self):
        self.gotoAlerts()
        # go through each time range
        for result in (clickEachTimerange(self.selenium)):
            if result:
                rcode = waitLoadProgressDone(self.selenium)
            else:
                return False
        return rcode


    def checkIoTDevice(self):
        kwargs = {}
        self.gotoAlerts()
        for result in (clickEachDevicesButton(self.selenium)):
            if not result:
                return False
        kwargs["selector"] = CSS_IOT_DEVICE_SELECTION
        self.selenium.click(selector=CSS_IOT_DEVICE_SELECTION)
        time.sleep(1)
        kwargs["selector"] = CSS_IOT_DEVICE_ALL_IOT
        self.selenium.click(selector=CSS_IOT_DEVICE_ALL_IOT)

        return True

    def checkSites(self):
        self.gotoAlerts()
        for result in (clickEachSite(self.selenium)):
            if not result:
                return False
        return True

    def checkAlertSeverity(self):
        self.gotoAlerts()
        for result in (clickAllAlertDropdownOptions(self.selenium)):
            if not result:
                return False
        return True

    def checkEntries(self):
        self.gotoAlerts()
        rcode = verifyAlertsEntries(self.selenium)
        return rcode

    # def checkEntryByName(self, names):
    #     self.gotoAlerts()     
    #     titlesNum = _getAlertPoliciesTitle(self.selenium)
    #     titles = [t[:t.find('(')-1].encode('ascii','ignore') for t in titlesNum]
    #     num = [ int(t[t.find('(')+1:t.find(')')].encode('ascii', 'ignore')) for t in titlesNum]

    #     titlesNew = dict(zip(titles, num))

    #     alertNums = []
    #     for name in names:
    #         if name in titlesNew:
    #             alertNums.append(titlesNew[name])
    #         else:
    #             alertNums.append(False)
    #     return alertNums

    def checkAlertNumbers(self):
        self.gotoAlerts()
        rcode = verifyAlertNumbers(self.selenium)
        return rcode

    def checkAlertExport(self):
        self.gotoAlerts()
        rcode = verifyAlertExport(self.selenium)
        return rcode

    def checkAlertDownload(self, filetype):
        self.gotoAlerts()
        rcode = _verifyAlertDownloads(self.selenium, filetype)
        return rcode
    def checkAlertListDownload(self, filetype):
        self.gotoAlerts()
        rcode = _verifyAlertListDownload(self.selenium, filetype)
        return rcode

    def checkAlertPagination(self):
        self.gotoAlerts()
        rcode = True
        rcode = rcode and verifyAlertRowsPerPage(self.selenium)
        rcode = rcode and verifyAlertPageChange(self.selenium)
        return rcode

    def checkAlertDetails(self):
        self.gotoAlerts()
        rcode = True
        rcode = rcode and verifyAlertDetailsLinks(self.selenium)
        rcode = rcode and verifyAlertDetailsPageInfo(self.selenium)
        return rcode

    def checkAlertActionAIMSDidSentToServer(self, **kwargs):
        self.configAlertAction('testing', action='aims', **kwargs)

        time.sleep(15)

        record = _getLatestActionFromAIMSServer(**kwargs)
        rcode = self._verifyAIMSServerRecord(record)

        return rcode

    def _verifyAIMSServerRecord(self, record):
        params = ['Notes', 'Priority', 'AssignedTo']
        values = [alert_action_comment, alert_action_priority, alert_action_assignee]
        for index, param in enumerate(params):
            if param not in record:
                print(('Param {0} not in latest record of AIMS server'.format(param)))
                return False
            if record[param] not in values[index]:
                print(('AIMS record value not match on param {0}'.format(param)))
                return False
        print('zbUIAlerts/_verifyAIMSServerRecord: AIMS record found!')
        print(('zbUIAlerts/_verifyAIMSServerRecord: Notes: {}'.format(alert_action_comment)))
        print(('zbUIAlerts/_verifyAIMSServerRecord: Priority: {}'.format(alert_action_priority)))
        print(('zbUIAlerts/_verifyAIMSServerRecord: AssignedTo: {}'.format(alert_action_assignee)))
        print(('zbUIAlerts/_verifyAIMSServerRecord: Record: {}'.format(record)))
        return True

    def checkAlertActionSIEMDidSentToServer(self, **kwargs):
        self.configAlertAction('testing', action='siem')
        time.sleep(15)

        record = _getLatestActionFromSIEMServer(**kwargs)
        rcode = self._verifySIEMServerRecord(record)

        return rcode

    def _verifySIEMServerRecord(self, record):
        if 'results' not in record:
            print('zbUIAlerts.py/_verifySIEMServerRecord: "results" key not in SIEM record')
            return False
        results = record['results']

        if type(results) != list or len(results) < 1:
            print('zbUIAlerts.py/_verifySIEMServerRecord: no results in SIEM record')
        result = results[0]

        if '_raw' not in result:
            print('zbUIAlerts.py/_verifySIEMServerRecord: "_raw" key not in SIEM result')
            return False
        raw_data = result['_raw']

        rcode = True
        rcode = rcode and alert_description in raw_data
        if rcode == True:
            print(('zbUIAlerts/_verifySIEMServerRecord: SIEM record found! Alert description "{}" is in record \n{}'.format(alert_description, raw_data)))
        else:
            print(('zbUIAlerts/_verifySIEMServerRecord: SIEM record not found! Alert description "{}" is not in record \n{}'.format(alert_description, raw_data)))

        return rcode

    def checkAlertActionBlockDidSentToServer(self, **kwargs):
        self.configAlertAction('testing', action='block')
        # It waits exceptionally long because it takes longer time for PANFW to record the ACL rule
        time.sleep(75)

        record = _getLatestPolicyFromPANFW(**kwargs)
        rcode = self._verifyPANFWServerRecord(record)

        return rcode

    def _verifyPANFWServerRecord(self, record):
        rcode = True
        rcode = rcode and rule_name in record
        if rcode == True:
            print(('zbUIAlerts/_verifyPANFWServerRecord: PANFW record found! rule name "{}" is in record \n{}'.format(rule_name, record)))
        else:
            print(('zbUIAlerts/_verifyPANFWServerRecord: PANFW record not found! rule name "{}" is not in record \n{}'.format(rule_name, record)))
        return rcode

    def checkAlertActionConnectivDidSentToServer(self, **kwargs):
        self.configAlertAction('testing', action='connectiv', **kwargs)
        time.sleep(15)
        record = _getLatestConnectivSecurityEvent(**kwargs)
        rcode = self._verifyConnectivSecurityEvent(record)
        return rcode

    def _verifyConnectivSecurityEvent(self, record):
        rcode = alert_action_comment == record['notes']
        if rcode == False:
            print(('zbUIAlerts/_verifyConnectivSecurityEvent: Connectiv record not found! alert comment "{}" is not in record \n{}'.format(alert_action_comment, record)))
        return rcode

    def checkAlertActionEditPolicy(self):
        self.gotoAlerts()
        rcode = True
        rcode = rcode and verifyAlertActionEditPolicy(self.selenium)
        return rcode

    def configAlertAction(self, alertName, currentStatus="pending", action="resolve", **kwargs):
        if action == 'aims':
            self.gotoAssetManagement()
            enableAIMS(self.selenium, **kwargs)
        elif action == 'connectiv':
            self.gotoAssetManagement()
            enableConnectiv(self.selenium, **kwargs)
        self.gotoAlerts()
        # filter alert to pending only
        filterStatusAlert(self.selenium, currentStatus)
        # find alertname, and resolve alert
        rcode = setAlertAction(self, self.selenium, alertName, currentStatus, action)
        return rcode 

    def close(self):
        if self.selenium:
            self.selenium.quit()
