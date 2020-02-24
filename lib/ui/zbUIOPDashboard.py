#!/usr/bin/python
from urllib.parse import urlparse
from ui.zbUIShared import *
from ui.login.zbUILoginCore import Login
import time, pdb

# CSS_SELECTOR_CHIP_INPUT = "input.md-input[type='search']"
CSS_VIEW_TYPE_BOTTON = '.dashboard .viewtype-wrapper md-select.viewtype-selector'
CSS_VIEW_TYPE_SECURITY_OPTION = 'md-select-menu md-option[value="security"]'
CSS_VIEW_TYPE_OPERATIONAL_OPTION = 'md-select-menu md-option[value="operations"]'
CSS_PROFILES_FILTER = "button[ng-click = \"profileSelectorCtrl.setGroupingView('profile')\"]"
CSS_PROFILES_INTERVAL_FILTER = '.primary-selectors .date-selection button'
CSS_PROFILES_INTERVALS_BUTTON = 'md-menu-item.date-picker-item'
CSS_PROFILES_CARDS = '.category-listing-selector .card-row .card-outer .grouping-card.group'
CSS_PROFILE_PAGE_CARD_NAME = 'div.card-name'
CSS_PROFILE_PAGE_CARD_COUNT = 'span[ng-bind="item.count | prettyPrintNumber"]'
CSS_SHOW_MORE_PROFILES_BUTTON = '.category-listing-selector .card-outer[ng-click="categoryListingCtrl.toggleShowAll()"]'
CSS_VIEW_SIX_MONTH_BUTTON = '.zing-datepicker-wrap .quick-select-wrap button[name="Set the date range selector to Last Six Months"]'
CSS_VIEW_TIME_INTERVAL_BUTTON = '.zing-datepicker-wrap .layout-container .quick-select-wrap button'
CSS_DATE_DROPDOWN = ".date-selection"

CSS_IMAGE_DATA_BARS = "rect.highcharts-point.highcharts-color-0:not(.highcharts-null-point)"
CSS_IMAGE_DATA_COUNT = '.customized-legend .image-legend .number'
CSS_PATIENT_DATA_BARS = 'rect.highcharts-color-1.highcharts-point'
CSS_PATIENT_ZERO_BAR = "rect.highcharts-color-1.highcharts-point[height='0']"
CSS_PATIENT_DATA_COUNT = '.customized-legend .patient-legend .number'
CSS_TOOLTIP_NUMBER = 'div.tooltip span.text-container b' #'.highcharts-tooltip span b'
CSS_IMAGE_DATA_DEVICE_LINK = '#devices-graph .highcharts-axis-labels a'
CSS_DEVICE_INVENTORY_DEVICE_NAME = '.title-row span.md-headline'

CSS_AGG_DOTS = '#healthcare-graph-container .highcharts-series-group .highcharts-tracker path[fill="#42a9d2"]'
CSS_AGG_TOOLTIP_IMAGE_COUNT = '.highcharts-tooltip span'

VALID_CATEGORIES = [
    'X-Ray Machine',
    'MRI Machine',
    'UltraSound Machine',
    'PET Scanner',
    'Nuclear-Medicine Imager',
    'CT Scanner',
    'Infusion System'
]
CSS_CATEGORY_BUTTONS = '.category-carousel .category-item'
CSS_CATEGORY_NAME = '.category-carousel .category-item div.name'
CSS_CATEGORY_COUNT = '.category-carousel .category-item div.number'
CSS_PROFILE_CARD_NAME = '.category-profile-card p.card-desc'
CSS_PROFILE_CARD_COUNT = "div.big-number.ng-binding[ng-bind='healthcareDeviceConnectionChartCtrl.statData.total']" #'.category-profile-card .number-wrap h2.big-number'
CSS_SMALL_PROFILE_CARDS = ".profile-card-container .profile-card.clickable" #'.category-profile-card .profile-cards .profile-card'
CSS_SHOW_MORE_CARDS = '.category-profile-card .profile-cards .profile-card.show-toggle-card'

CSS_DEVICE_USAGE_COUNT = '.total-number-wrapper span'
CSS_DEVICE_USAGE_TOGGLE_BTNS = '.device-list-card .toggle-row div.device-active-toggle'
CSS_DEVICE_ROW = '.healthcare-device-cards .device-list-card div.list-item.layout-row'
CSS_DEVICE_NAME = 'span[category="OT Devices"]'
CSS_DEVICE_IP = 'span[ng-bind="item.ip"]'
CSS_DEVICE_COLS_DATA = 'span.oneline-text'
CSS_DEVICE_INVENTORY_DEVICE_IP = '#device_overall_info > md-card > div > div.body.solid-border-top.layout-row > div:nth-child(3) > ul > li:nth-child(1) > span.ng-binding'#'md-card.device-detail-overall .flex-33[layout-align="space-between start"] ul li span.ng-binding'
CSS_DEVICE_INVENTORY_MISCELLANEOUS_DETAILS = '.flex-33[layout-align="start start"] ul li span.zing-word-breakall' # Includes vendor and location info
CSS_DEVICE_INVENTORY_LAST_ACTIVE_DATE = 'zing-device-overall .device-detail-overall div.date-text'

CSS_DEVICE_SORT_HEADER = '.healthcare-device-cards .device-list-card .header div.header-item'
CSS_DEVICE_SORT_UP_ARROW = '.device-list-card .header i[ng-show="healthCardCtrl[healthCardCtrl.selectedDeviceType.value].sortObj.order === -1"][aria-hidden="false"]'
CSS_DEVICE_SORT_DOWN_ARROW = '.device-list-card .header i[ng-show="healthCardCtrl[healthCardCtrl.selectedDeviceType.value].sortObj.order === 1"][aria-hidden="false"]'
CSS_DEVICE_SORT_NAMES = '.list-body-wrap span.name'
CSS_DEVICE_SORT_IPS = '.list-body-wrap span[ng-bind="item.ip"]'
CSS_DEVICE_SORT_VENDORS = '.device-list-card .list-body-wrap .oneline-text[ng-bind="item.vendor | cut:false:15:\' ...\'"]'
CSS_DEVICE_SORT_LOCATIONS = '.device-list-card .list-body-wrap .oneline-text[ng-bind="item.location| cut:false:12:\' ...\'"]'
CSS_DEVICE_SORT_ACTIVE_TIME = '.device-list-card .list-body-wrap .oneline-text[ng-bind="item.last_activity | dateWithTimezone:healthCardCtrl.timezone:\'MMM D, YYYY, HH:mm\'"]'

CSS_PROFILE_CARD_COUNT_USED = "span.ng-binding[ng-bind='healthCardCtrl.data.total_devices_in_use || 0']"
CSS_PROFILE_CARD_COUNT_NOT_USED = "span.ng-binding[ng-bind='healthCardCtrl.data.total_devices_not_in_use || 0']"

def _getProfiles(browserobj):
    cards = browserobj.findMultiCSS(selector=CSS_PROFILES_CARDS)
    if not cards:
        print('zbUIOPDashboard.py/_getProfiles: No profile cards found.')
        return False
    profiles = {}
    for card in cards:
        cardName = browserobj.getText(browserobj=card, selector=CSS_PROFILE_PAGE_CARD_NAME, timeout=3)
        cardCount = int(browserobj.getText(browserobj=card, selector=CSS_PROFILE_PAGE_CARD_COUNT, timeout=3).replace(',',''))
        profiles[cardName] = cardCount
    return profiles

def _verifyImagesCount(browserobj):
    waitLoadProgressDone(browserobj)
    totalCount = int(browserobj.getText(selector=CSS_IMAGE_DATA_COUNT))

    patient_legend = browserobj.findSingleCSS(selector=CSS_PATIENT_DATA_COUNT, timeout=5, err_msg='zbUIOPDashboard/_verifyImagesCount: Cannot find the patient legend')
    patient_legend.click() 

    bars = browserobj.findMultiCSS(selector=CSS_IMAGE_DATA_BARS, timeout=5, err_msg='zbUIOPDashboard/_verifyImagesCount: Cannot find any image data bars')

    zero_bars = browserobj.findMultiCSS(selector=CSS_PATIENT_ZERO_BAR) # bars with a height of zero

    count = 0
    for item in bars:
        if item in zero_bars:
            continue
        browserobj.hoverElement(item)
        time.sleep(0.4)
        barCount = int(browserobj.getTextNoHover(selector=CSS_TOOLTIP_NUMBER))
        if barCount == 0:
            print("ZERO DETECTED")
            continue
        count = count + barCount
    print("Got count: " + str(count))
    print("Listed count: " + str(totalCount))
    return count == totalCount

def _verifyImagesBarHidden(browserobj):
    browserobj.click(selector=CSS_IMAGE_DATA_COUNT)
    time.sleep(1)
    bars = browserobj.findMultiCSS(
        selector=CSS_IMAGE_DATA_BARS,
        timeout=3,
        waittype='visibility'
    )
    return not bars

def _verifyPatientsCount(browserobj):
    waitLoadProgressDone(browserobj)
    time.sleep(3)
    totalCount = int(browserobj.getText(selector=CSS_PATIENT_DATA_COUNT))

    image_legend = browserobj.findSingleCSS(selector=CSS_IMAGE_DATA_COUNT, timeout=5, err_msg='zbUIOPDashboard/_verifyPatientsCount: Cannot find the image legend')
    image_legend.click()

    bars = browserobj.findMultiCSS(selector=CSS_PATIENT_DATA_BARS, timeout=5, err_msg='zbUIOPDashboard/_verifyPatientsCount: Cannot find any patient data bars')
    
    zero_bars = browserobj.findMultiCSS(selector=CSS_PATIENT_ZERO_BAR) # bars with a height of zero

    count = 0
    for item in bars:
        if item in zero_bars:
            continue
        browserobj.hoverElement(item)
        time.sleep(0.3)
        barCount = int(browserobj.getTextNoHover(selector=CSS_TOOLTIP_NUMBER))
        count += barCount
    return count == totalCount

def _verifyPatientsBarHidden(browserobj):
    browserobj.click(selector=CSS_PATIENT_DATA_COUNT)
    time.sleep(1)
    bars = browserobj.findMultiCSS(
        selector=CSS_PATIENT_DATA_BARS,
        timeout=3,
        waittype='visibility'
    )
    return not bars

def _verifyImageDataDeviceLink(browserobj):
    element = browserobj.findSingleCSS(
        selector=CSS_IMAGE_DATA_DEVICE_LINK,
        timeout=3
    )
    if not element:
        print('zbUIOPDashboard.py/_verifyImageDataDeviceLink: No clickable device link.')
        return True
    deviceName = browserobj.getText(selector=CSS_IMAGE_DATA_DEVICE_LINK)
    browserobj.click(selector=CSS_IMAGE_DATA_DEVICE_LINK)
    browserobj.switchToLatestWindow()
    waitLoadProgressDone(browserobj)
    inventoryPageDeviceName = browserobj.getText(selector=CSS_DEVICE_INVENTORY_DEVICE_NAME)
    return deviceName in inventoryPageDeviceName

def _verifyAggData(browserobj):
    intervals = browserobj.findMultiCSS(selector=CSS_VIEW_TIME_INTERVAL_BUTTON)
    for interval in intervals:
        interval.click()
        waitLoadProgressDone(browserobj)
        dots = browserobj.findMultiCSS(selector=CSS_AGG_DOTS)
        if not dots:
            print('zbUIOPDashboard.py/_verifyAggData: Cannot find any agg data')
            return False
        for dot in dots:
            browserobj.hoverElement(dot)
            text = browserobj.getAttribute(selector=CSS_AGG_TOOLTIP_IMAGE_COUNT, attribute='innerHTML')
            try:
                num = int(text[text.rfind('>')+1:])
                if num < 0:
                    raise Exception('zbUIOPDashboard.py/_verifyAggData: agg image count smaller than 0.')
            except Exception as err:
                print('zbUIOPDashboard.py/_verifyAggData: invalid agg image count.')
                print(err)
                return False
    return True

def _verifyGlobalData(browserobj, **kwargs):
    categoryBtns = browserobj.findMultiCSS(selector=CSS_CATEGORY_BUTTONS)
    if not categoryBtns:
        print('zbUIOPDashboard.py/_verifyGlobalData: Cannot find any category buttons.')
        return False
    rcode = True
    for btn in categoryBtns:
        btn.click()
        waitLoadProgressDone(browserobj)
        time.sleep(10)

        nameOnButton = browserobj.getText(browserobj=btn, selector=CSS_CATEGORY_NAME)
        nameOnProfileCard = browserobj.getText(selector=CSS_PROFILE_CARD_NAME)
        countOnButton = int(browserobj.getText(browserobj=btn, selector=CSS_CATEGORY_COUNT))
        
        countFound = False
        countAttempts = 0
        while countFound == False:
            try:
                if countAttempts == 10:
                    break
                time.sleep(1)
                countOnProfileCard = int(browserobj.getText(selector=CSS_PROFILE_CARD_COUNT))
                countFound = True
            except:
                countAttempts += 1
                print(("Will try again to find the count on the Profile Card loop 1, this was attempt: {}").format(countAttempts))
                pass

        if countOnProfileCard == 0:
            countFound2 = False
            countAttempts2 = 0
            while countFound2 == False:
                try:
                    if countAttempts2 == 10:
                        break
                    time.sleep(1)
                    countOnProfileCard = int(browserobj.getText(selector=CSS_PROFILE_CARD_COUNT_USED)) + int(browserobj.getText(selector=CSS_PROFILE_CARD_COUNT_NOT_USED))
                    countFound2 = True
                except:
                    countAttempts2 += 1
                    print(("Will try again to find the count on the Profile Card loop 2, this was attempt: {}").format(countAttempts2))
                    pass

        if nameOnButton != nameOnProfileCard or countOnButton != countOnProfileCard:
            print('zbUIOPDashboard.py/_verifyGlobalData: name or count on button and profile card does not match.')
            print(('name: {} {}'.format(nameOnButton, nameOnProfileCard)))
            print(('count: {} {}'.format(countOnButton, countOnProfileCard)))
            for i in range(3):
                if i == 2:
                    return False
                browserobj.refresh()
                waitLoadProgressDone(browserobj)
                btn.click()
                waitLoadProgressDone(browserobj)
                try:
                    countOnProfileCard = int(browserobj.getText(selector=CSS_PROFILE_CARD_COUNT_USED)) + int(browserobj.getText(selector=CSS_PROFILE_CARD_COUNT_NOT_USED))
                    if countOnButton == countOnProfileCard:
                        break
                except:
                    print("Still cannot get countOnButton == countOnProfileCard")
        if nameOnButton not in VALID_CATEGORIES:
            print(('zbUIOPDashboard.py/_verifyGlobalData: category name {} is not in valid categories list {}.'.format(nameOnButton, VALID_CATEGORIES)))
            return False
        rcode = rcode and _verifyProfileCardCounts(browserobj, countOnButton, **kwargs)
    return rcode

def _verifyProfileCardCounts(browserobj, totalCount, **kwargs):
    profiles = kwargs['profiles'] if 'profiles' in kwargs else {}
    showMoreBtn = browserobj.findSingleCSS(selector=CSS_SHOW_MORE_CARDS, timeout=5)
    if showMoreBtn:
        showMoreBtn.click()
    cards = browserobj.findMultiCSS(selector=CSS_SMALL_PROFILE_CARDS)
    if not cards:
        print('zbUIOPDashboard.py/_verifyProfileCardCounts: No profile cards found.')
        return False
    count = 0
    for index, card in enumerate(cards):
        if index == 0:
            text = browserobj.getText(browserobj=card, selector='div')
            profileCardCount = int(text[text.rfind('(') + 1: text.rfind(')')])
            if profileCardCount != totalCount:
                print(('zbUIOPDashboard.py/_verifyProfileCardCounts: Profile card total count {} does not match category total count {}.'.format(profileCardCount, totalCount)))
                return False
        else:
            try:
                text = browserobj.getText(browserobj=card, selector='div')
                profileCardCount = int(text[text.rfind('(') + 1: text.rfind(')')])
                profileName = text[:text.rfind('(')-1]
                count = count + profileCardCount
                if profileName not in profiles:
                    print(('zbUIOPDashboard.py/_verifyProfileCardCounts: profile {} cannot found profile page.'.format(profileName)))
                    return False
                elif profiles.get(profileName, 0) != profileCardCount:
                    print(('zbUIOPDashboard.py/_verifyProfileCardCounts: profile name {} profile card count {} is different from that of profile page.'.format(profileName, profileCardCount)))
                    return False
            except:
                pass
    if count != totalCount:
        print(('zbUIOPDashboard.py/_verifyProfileCardCounts: profile cards count {} is different from total count {}.'.format(count, totalCount)))
        return False
    return True

def _verifyDeviceUsageData(browserobj):
    rcode = True
    rcode = rcode and _verifyDeviceUsageCount(browserobj)
    waitLoadProgressDone(browserobj)
    rcode = rcode and _verifyDeviceUsageDetails(browserobj)
    return rcode

def _verifyDeviceUsageCount(browserobj):
    counts = browserobj.findMultiCSS(selector=CSS_DEVICE_USAGE_COUNT)
    toggles = browserobj.findMultiCSS(selector=CSS_DEVICE_USAGE_TOGGLE_BTNS)
    if not counts or not toggles:
        print('zbUIOPDashboard.py/_verifyDeviceUsageCount: Cannot found device usage counts.')
        return False
    for index, count in enumerate(counts):
        toggleText = toggles[index].text
        countOnToggle = int(toggleText[toggleText.rfind('(')+1: toggleText.rfind(')')])
        if int(count.text) != countOnToggle:
            print(('zbUIOPDashboard.py/_verifyDeviceUsageCount: Count not match {} {}.'.format(int(count.text), countOnToggle)))
            return False
    return True

def _verifyDeviceUsageDetails(browserobj):
    row = browserobj.findSingleCSS(selector=CSS_DEVICE_ROW)
    if not row:
        print('zbUIOPDashboard.py/_verifyDeviceUsageDetails: No device details row, will ignore this test.')
        return True
    deviceName = browserobj.getText(browserobj=row, selector=CSS_DEVICE_NAME)
    deviceIP = browserobj.getText(browserobj=row, selector=CSS_DEVICE_IP)
    cols = browserobj.findMultiCSSFromBrowserobj(browserobj=row, selector=CSS_DEVICE_COLS_DATA)
    deviceVendor = cols[0].text.replace(' ...', '')
    deviceLocation = cols[1].text.replace(' ...', '')
    deviceDate = cols[2].text.replace(' ...', '')
    browserobj.click(selector=CSS_DEVICE_NAME)
    time.sleep(5)
    waitLoadProgressDone(browserobj)
    detailsDeviceName = browserobj.getText(selector=CSS_DEVICE_INVENTORY_DEVICE_NAME)
    detailsDeviceIP = browserobj.getText(selector=CSS_DEVICE_INVENTORY_DEVICE_IP)
    details = []
    detailsObjs = browserobj.findMultiCSS(selector=CSS_DEVICE_INVENTORY_MISCELLANEOUS_DETAILS)
    for detailsObj in detailsObjs:
        details.append(detailsObj.text)
    if deviceName != detailsDeviceName:
        print(('zbUIOPDashboard.py/_verifyDeviceUsageDetails: Device names not match {} {}'.format(deviceName, detailsDeviceName)))
        return False
    elif deviceIP != detailsDeviceIP:
        print(('DeviceIP: ' + deviceIP + " | Device Details IP: " + detailsDeviceIP))
        print(('zbUIOPDashboard.py/_verifyDeviceUsageDetails: Device IP not match {} {}'.format(deviceIP, detailsDeviceIP)))
        return False
    vendorFound = False
    locationFound = False
    for detail in details:
        if deviceVendor in detail:
            vendorFound = True
        if deviceLocation in detail:
            locationFound = True
    if vendorFound == False or locationFound == False:
        print(('zbUIOPDashboard.py/_verifyDeviceUsageDetails: Device vendor or location not found {} {} {}'.format(deviceVendor, deviceLocation, detail)))
        return False

    '''
    # disabling date check since last activity on OT Dashboard is specific to DICOM and doesn't need to match up with Device Detail last activity
    # Verify date
    detailsDate = browserobj.getText(selector=CSS_DEVICE_INVENTORY_LAST_ACTIVE_DATE)
    try:
        deviceDate = parser.parse(deviceDate)

        _time = '{hour}:{minute}'.format(
            hour=str(deviceDate.hour).zfill(2),
            minute=str(deviceDate.minute).zfill(2)
        )
        _date = '{month}/{day}/{year}'.format(
            month=str(deviceDate.month).zfill(2),
            day=str(deviceDate.day).zfill(2),
            year=str(deviceDate.year).zfill(4)
        )

        if _time not in detailsDate or _date not in detailsDate:
            print('zbUIOPDashboard.py/_verifyDeviceUsageDetails: Device details last active time not correct. {}, but shown {} {}'.format(detailsDate, _time, _date))
            return False
    except:
        # OT Dashboard gave unknown file format, do exact comparison with Detail page
        if deviceDate != detailsDate:
            print('zbUIOPDashboard.py/_verifyDeviceUsageDetails: Device details last active time not correct. {}, but shown {}'.format(detailsDate, deviceDate))
            return False
    '''
    
    return True

def _verifyDeviceSorting(browserobj):
    sortButtons = browserobj.findMultiCSS(selector=CSS_DEVICE_SORT_HEADER)
    for index, sortButton in enumerate(sortButtons):
        if not clickUntilFind(browserobj, sortButton, CSS_DEVICE_SORT_UP_ARROW):
            print("Cannot find column up arrow button")
            return False
        data = _getSortedDataForIndex(browserobj, index)
        validateSortOrder('ascending', data)

        if not clickUntilFind(browserobj, sortButton, CSS_DEVICE_SORT_DOWN_ARROW):
            print("Cannot find column down arrow button")
            return False
        data = _getSortedDataForIndex(browserobj, index)
        validateSortOrder('descending', data)
    return True

def _getSortedDataForIndex(browserobj, index):
    selector = ''
    if index == 0:
        selector = CSS_DEVICE_SORT_NAMES
    elif index == 1:
        selector = CSS_DEVICE_SORT_IPS
    elif index == 2:
        selector = CSS_DEVICE_SORT_VENDORS
    elif index == 3:
        selector = CSS_DEVICE_SORT_LOCATIONS
    elif index == 4:
        selector = CSS_DEVICE_SORT_ACTIVE_TIME
    data = _getSortedData(browserobj, selector)
    return data

def _getSortedData(browserobj, selector):
    data = browserobj.findMultiCSSFromBrowserobj(selector=selector, timeout=3)
    if not data:
        return []
    return data



class OPDashboard():

    def __init__(self, **kwargs):
        self.params = kwargs
        self.selenium = Login(**kwargs).login()

    def gotoOPDashboard(self):
        url = urlparse(self.params["url"])
        rcode = self.selenium.getURL(url.scheme+'://'+url.netloc)
        waitLoadProgressDone(self.selenium)
        self.selenium.click(selector=CSS_VIEW_TYPE_BOTTON)
        self.selenium.click(selector=CSS_VIEW_TYPE_OPERATIONAL_OPTION)
        for time in clickEachDashboardTimerange(self.selenium, specific='1 Day'): pass
        waitLoadProgressDone(self.selenium)

    def gotoProfiles(self):
        url = urlparse(self.params["url"])
        self.selenium.click(selector=CSS_VIEW_TYPE_BOTTON)
        self.selenium.click(selector=CSS_VIEW_TYPE_SECURITY_OPTION)
        self.selenium.click(selector=CSS_PROFILES_FILTER)
        self.selenium.click(selector=CSS_PROFILES_INTERVAL_FILTER)
        intervals = self.selenium.findMultiCSS(selector=CSS_PROFILES_INTERVALS_BUTTON)
        intervals[-1].click()
        waitLoadProgressDone(self.selenium)
        time.sleep(2)
        showMoreBtn = self.selenium.findSingleCSS(
            selector=CSS_SHOW_MORE_PROFILES_BUTTON,
            timeout=5
        )
        if showMoreBtn:
            showMoreBtn.click()
        waitLoadProgressDone(self.selenium)

    def verifyImageData(self):
        self.gotoOPDashboard()
        selectOTDashboardCategory(self.selenium, 'X-Ray Machine')
        rcode = _verifyImagesCount(self.selenium)
        rcode = rcode and _verifyImagesBarHidden(self.selenium)
        return rcode

    def verifyPatientData(self):
        self.gotoOPDashboard()
        selectOTDashboardCategory(self.selenium, 'X-Ray Machine')
        rcode = _verifyPatientsCount(self.selenium)
        rcode = rcode and _verifyPatientsBarHidden(self.selenium)
        return rcode

    def verifyImageDataDeviceLink(self):
        self.gotoOPDashboard()
        selectOTDashboardCategory(self.selenium, 'X-Ray Machine')
        rcode = _verifyImageDataDeviceLink(self.selenium)
        return rcode

    def verifyAggData(self):
        self.gotoOPDashboard()
        selectOTDashboardCategory(self.selenium, 'X-Ray Machine')
        rcode = _verifyAggData(self.selenium)
        return rcode

    def verifyGlobalData(self):
        self.gotoProfiles()
        profiles = _getProfiles(self.selenium)
        if not profiles:
            print('zbUIOPDashboard.py/verifyGlobalData: No profiles found.')
        self.gotoOPDashboard()
        rcode = _verifyGlobalData(
            self.selenium,
            profiles=profiles
        )
        return rcode

    def verifyDeviceUsageData(self):
        self.gotoOPDashboard()
        selectOTDashboardCategory(self.selenium, 'X-Ray Machine')
        rcode = _verifyDeviceUsageData(self.selenium)
        return rcode

    def verifyDeviceSorting(self):
        self.gotoOPDashboard()
        selectOTDashboardCategory(self.selenium, 'X-Ray Machine')
        rcode = _verifyDeviceSorting(self.selenium)
        return rcode

    def close(self):
        if self.selenium:
            self.selenium.quit()
