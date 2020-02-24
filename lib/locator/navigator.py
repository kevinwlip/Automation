# Login, Navigator and Shared CSS
import collections

class UISharedLoc(object):
    """ global CSS parameters for Shared UI objects """
    CSS_CLICK_TO_SELECT_TIME = ".inner-content li[data-type='DURATION'] mat-icon"
    CSS_CLICK_TO_SELECT_SITE = ".inner-content li[data-type='SITE'] mat-icon"
    CSS_CLICK_TO_SELECT_MONITORED = ".inner-content li[data-type='FILTER_MONITORED'] mat-icon"
    CSS_CLICK_TO_SELECT_DEVICE = ".inner-content li[data-type='DEVICES'] mat-icon"
    CSS_GLOBAL_FILTER_OPTIONS = "zing-global-filter-menu li:nth-of-type({})"
    CSS_GLOBAL_TIMERANGE = "li .content-wrapper"

    CSS_DROPDOWN_TIMERANGE_BUTTON = "button[aria-label='Select date range'] > i.material-icons"
    CSS_DROPDOWN_TIMERANGE = collections.OrderedDict()
    CSS_DROPDOWN_TIMERANGE["2 Hour"] = "md-menu-content > md-menu-item.date-picker-item:nth-child(1)"
    CSS_DROPDOWN_TIMERANGE["1 Day"] = "md-menu-content > md-menu-item.date-picker-item:nth-child(2)"
    CSS_DROPDOWN_TIMERANGE["1 Week"] = "md-menu-content > md-menu-item.date-picker-item:nth-child(3)"
    CSS_DROPDOWN_TIMERANGE["1 Month"] = "md-menu-content > md-menu-item.date-picker-item:nth-child(4)"
    CSS_DROPDOWN_TIMERANGE["1 Year"] = "md-menu-content > md-menu-item.date-picker-item:nth-child(5)"
    CSS_DROPDOWN_TIMERANGE["ALL"] = "md-menu-content > md-menu-item.date-picker-item:nth-child(6)"

    CSS_PROGRESS_SPINNER = "md-progress-circular[role='progressbar'] > svg > path"
    CSS_SERIES_BAR = "g .highcharts-series rect"

    CSS_SITE_TAB = "button[ng-click=\"profileSelectorCtrl.setGroupingView('site')\"]"
    CSS_SHOW_ALL = "[ng-click='categoryListingCtrl.resetProfileCategoryFilters()']"
    CSS_CLEAR_FILTER = 'button[aria-label="Reset all filters to default"]'

    CSS_DEVICE_INVENTORY_HEADERS = ".ui-grid-header-cell-label.ng-binding"
    CSS_DEVICE_INVENTORY_DATA_BLANK = ".ui-grid-coluiGrid"

    CSS_SELECTOR_ALL_DEVICES_BUTTONS = "div.iot-tab.layout-align-space-between-stretch.layout-row > div"
    CSS_SELECTOR_IOT_DEVICES_MENU = "div.iot-tab.layout-align-space-between-stretch.layout-row > md-menu"
    CSS_SELECTOR_IOT_DEVICES_MENU_ENTRY = "md-menu-item.industry-menu-item > button"
    CSS_SELECTOR_ALL_DEVICES_NUMBER1 = "div.iot-box.layout-align-space-between-center.layout-row.active > div.ng-binding.ng-scope"
    CSS_SELECTOR_ALL_DEVICES_NUMBER2 = "div.table-title.layout-align-start-center.layout-row > div[aria-hidden='false']"
    CSS_SELECTOR_ALL_DEVICES_NUMBER3 = "div.pagination-wrap.layout-align-space-between-center.layout-row > span"

    CSS_SELECTOR_COLUMN_HEADER = "div[role='columnheader']"

    CSS_SELECTOR_DATE_TEXT = "div.date-text.ng-binding"
    CSS_SELECTOR_BLUE_NUMBER = "div.blue-number.ng-binding"
    CSS_SELECTOR_TOTAL_DATA = "div.total-data"
    CSS_SELECTOR_ENCRYPTED_PERCENTAGE = "div.desc-text.ng-binding"

    CSS_SELECTOR_NETWORK_USAGE_CHART_PATHS = "svg[aria-label='A chart.'] > g > path"

    CSS_SELECTOR_SITE_CHECKBOX = "md-option.ng-scope.md-checkbox-enabled.md-ink-ripple"

    CSS_BUTTON_ALL_DEVICE = "div.all"
    CSS_DROPDOWN_BUTTON_SITE = 'md-select[ng-model="ctrl.selectedSites"] > md-select-value > span.md-select-icon'
    CSS_SELECTOR_OUTSIDE_SITE_MODAL = "md-backdrop.md-select-backdrop"

    CSS_SELECTOR_PAGINATION_INPUT = "input.ui-grid-pager-control-input"
    CSS_SELECTOR_INVENTORY_ROW = "div.ui-grid-cell.ng-scope.ui-grid-coluiGrid-0005"
    CSS_SELECTOR_GENERAL_TEXT_ENTRY = "div.ui-grid-cell.ng-scope.ui-grid-coluiGrid-000"
    CSS_SELECTOR_CHEVRON_RIGHT_ICON = "ng-md-icon[icon='chevron_right']"
    CSS_SELECTOR_CLICKABLE_SORT_HEADER = ".ui-grid-header-cell-label" 

    CSS_TENANT_NAME = "span.tenant-name"

    CSS_SORT_UP_ARROW = ".zt-custom-sort-down-label"
    CSS_SORT_DOWN_ARROW = ".zt-custom-sort-up-label"

    CSS_SORT_UP_ARROW_V1 = ".ui-grid-icon-up-dir"
    CSS_SORT_DOWN_ARROW_V1 =".ui-grid-icon-down-dir"


    CSS_DEVICE_LINK = 'div.ui-grid-row .ui-grid-coluiGrid-000E div.ng-scope a'
    CSS_DEVICE_LINK_SUPERUSER = 'div.ui-grid-row .ui-grid-coluiGrid-000F div.ng-scope a'
    CSS_DEVICE_LINK_NORMALUSER = 'div.ui-grid-row .ui-grid-coluiGrid-000E div.ng-scope a'

    CSS_DEVICE_DETAIL_NAME = "div.device-title-column span.md-headline"
    CSS_DEVICE_DETAIL_NAME2 = 'span.internal-hostname'
    CSS_APP_DETAIL_NAME = 'span[ng-if="ctrl.overallData.name"]'

    CSS_SELECTOR_SITE_DROPDOWN_UNSELECTED_OPTIONS = 'md-option[ng-value=site][aria-selected=false'
    CSS_SELECTOR_SITE_DROPDOWN = 'md-select[ng-model="ctrl.selectedSites"] > md-select-value'
    CSS_SELECTOR_SITE_ALL_DISABLE = 'md-checkbox[ng-model="ctrl.allSitesSelected"][aria-checked=true]'
    CSS_SELECTOR_SITE_ALL_ENABLE = 'md-checkbox[ng-model="ctrl.allSitesSelected"][aria-checked=false]'

    CSS_FROM_TO_TIMERANGE = '.fromto'
    CSS_GLOBAL_SEARCH_ICON = 'i[ng-show="!globalSearchCtrl.activeSearch"]'
    CSS_GLOBAL_SEARCH_TEXTBOX = 'input[aria-label="Search Device, or Alert"]'
    CSS_GLOBAL_SEARCH_MATCHES = 'li[md-virtual-repeat="item in $mdAutocompleteCtrl.matches"]'

    CSS_FILTER_ALL_CARD = "div.grouping-card.all.selected"
    CSS_SITE_ALL = "div.grouping-card.site"

    CSS_OT_CATEGORY_BUTTONS = '.category-carousel .category-item'

    CSS_TABLE_NAME = '.table-title'
    CSS_INVENTORY_SEARCH_ICON = "[name='search_toggle'][tooltip-text='Search']"

    CSS_GRAPH_TAB_OPTIONS = ".device-detail-tab" #1 is Alerts, 2 is Security, 3 is Operational
    CSS_ALERT_DATE_SELECTOR = "button[ng-disabled='alertTimerangeDropdownCtrl.isDisabled']"
    CSS_ALERT_CATEGORY_SELECTOR = "button[ng-disabled='alertCategoryDropdownCtrl.isDisabled']"
    CSS_ALERT_DATE_ENTRIES = "md-menu-item.date-picker-item[ng-repeat='dateitem in alertTimerangeDropdownCtrl.dateRangeTypes']"
    CSS_ALERT_ENTRY_TEXT = collections.OrderedDict()
    CSS_ALERT_ENTRY_TEXT["1D"] = 0
    CSS_ALERT_ENTRY_TEXT["1W"] = 1
    CSS_ALERT_ENTRY_TEXT["1M"] = 2
    CSS_ALERT_ENTRY_TEXT["6M"] = 3
    CSS_ALERT_ENTRY_TEXT["ALL"] = 4
    CSS_ALERT_CATEGORY_ENTRIES = "md-menu-item.date-picker-item[ng-if='alertitem.enable']"
    CSS_ALERT_ENTRY_CATE = collections.OrderedDict()
    CSS_ALERT_ENTRY_CATE["Active Alerts"] = 0
    CSS_ALERT_ENTRY_CATE["Resolved"] = 1
    CSS_ALERT_ENTRY_CATE["Assigned"] = 2
    CSS_ALERT_ENTRY_CATE["Sent to other systems"] = 3
    CSS_ALERT_ENTRY_CATE["All"] = 4
    CSS_ALERT_ENTRY_CATE["Internal Review"] = 5

    CSS_SELECTOR_VIEW_COLUMN = "[icon='view_column']"
    CSS_SELECTOR_VIEW_COLUMN_EXPER = ".zt-column-icon"
    CSS_SELECTOR_VIEW_COLUMN_UNCHECKED_CHECKBOX = "[role='checkbox'][aria-checked='false']"
    CSS_SELECTOR_VIEW_COLUMN_CARD = "md-card.table-column-card[layout='column']"
    CSS_SELECTOR_VIEW_COLUMN_CHECKED_CHECKBOX = "[role='checkbox'][aria-checked='true']"

    CSS_SELECTOR_VIEW_COLUMN_CHECKED_CHECKBOX_NEW = ".zt-item .mat-checkbox-checked.mat-checkbox"
    CSS_SELECTOR_VIEW_COLUMN_CHECKBOX_NEW = ".zt-item mat-checkbox"

    must_list = ['Type', 'Status', 'Device Name', 'IP Address',
                 'MAC address', 'Category', 'Profile', 'Site',
                 'Location', 'Vendor', 'Model', 'Description', "Risk"
                 ]

    CSS_X_GRID_HIGHCHARTS = '.highcharts-xaxis-grid'
    CSS_Y_GRID_HIGHCHARTS = '.highcharts-yaxis-grid'


class LoginLoc(object):
    """ Element locators for UI Login Page """
    CSS_USERNAME_FIELD = "input[ng-model='ctrl.username']"
    CSS_PASSWORD_FIELD = "input[ng-model='ctrl.password']"
    CSS_NEXT_BUTTON = ".login-bottom-section [ng-click='ctrl.ssoNext()']"
    CSS_LOGIN_BUTTON = ".login-bottom-section [ng-click='ctrl.loginRequest()']"
    CSS_LOGIN_FAILED = "div.fn-error"
    CSS_OUTLOOK_EMAIL_FIELD = "[name='loginfmt'][type='email']"
    CSS_OUTLOOK_PASSWORD_FIELD = "[name='passwd'][type='password']"
    CSS_OUTLOOK_SUBMIT_BUTTON = "[type='submit']"
    CSS_OUTLOOK_NO_BUTTON = "[type='button'][value='No']"
    CSS_SERIES_BAR = "g.highcharts-series rect"
    CSS_SERIES_NO_DATA = "g.highcharts-no-data"

    CSS_INSPECTOR_ONBOARD_PAGE = "md-content.onboarding-inspector-content"

    CSS_USER_PROFILE ="[aria-label='User Profile'] .ng-scope" #"[category='User Profile']"
    CSS_LOG_OUT = "[ng-click='ctrl.logout()']"

    CSS_2FA_FIELD = "[name='smsCode']"
    CSS_REMEMBER_TOKEN = "[aria-label='Trust this computer for 24 hours']"
    CSS_2FA_LOGIN = "[ng-click='ctrl.verifyFromLogin(ctrl.smsCode)']"

    CSS_GET_STARTED_BUTTON = "button.primary"

    CSS_DEVICE_INVENTORY_HEADERS = ".ui-grid-header-cell-label.ng-binding"
    CSS_DEVICE_INVENTORY_DATA_BLANK = ".ui-grid-coluiGrid"


class NavMenuLoc(object):
    """ Element locators for UI Navigation Menu """
    CSS_DASHBOARD = "a[data-title='Dashboard']"
    CSS_DEVICES = "a[data-title='Devices']"
    CSS_ALERTS = "div[data-title='Alerts']"
    CSS_RISKS = "div[data-title='Risks']"
    CSS_REPORTS = "a[data-title='Reports']"
    CSS_SERVERS = "a[data-title='Servers']"
    CSS_PROTOCOLS = "a[data-title='Protocols']"
    CSS_APPLICATIONS = "a[data-title='Applications']"
    CSS_NETWORK = "a[data-title='Network']"
    CSS_PROFILES = "a[data-title='Profiles']"
    CSS_POLICIES = "a[data-title='Policies']"
    CSS_INTEGRATIONS = "[data-title='Integrations']"
    CSS_ADMINISTRATION = "[data-title='Administration']"
    CSS_LOGO = "div[class='sidenav-header']"

    # Currently there are 4 arrows on the left panel, need to loop through 
    CSS_LEFTPANEL_ARROW = "i[class='more zing_icon_menuarrowright']"


class ToolBarLoc(object):
    """ Element locators for UI Top Toolbar """
    CSS_SEARCH_ICON = "i[class='zing_icon_search']"
    CSS_SEARCH_BAR = "div[class='global-search']"
    CSS_FEEDBACK_BUTTON = "button.mat-button.prime-2"
    CSS_HELP_ICON = "i.zing_icon_help" #"i[class='zing_icon_help']"
    CSS_AVATAR = "div.avatar"
    CSS_FILTER_SITE = "li[data-type='SITE']"
    CSS_FILTER_MONITORED = "li[data-type='FILTER_MONITORED']"
    CSS_FILTER_DEVICES = "li[data-type='DEVICES']"
    CSS_FILTER_DURATION = "li[data-type='DURATION']"

