from selenium.webdriver.common.by import By
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class DeviceLocators(object):
    # global CSS parameters for Device Inventory page
    CSS_DEVICE_ENTRY_POINT = "i.zing_icon_device"
    CSS_DEVICE_TABLE = ".table-card.mat-card"
    CSS_INVENTORY_HEADER = ".ag-header-cell-sortable"
    CSS_INVENTORY_HEADER_TIGHT = "app-loading-overlay > div.zt-table-header"
    CSS_COLUMN_ALL_CELLS = ".ag-cell"
    CSS_PAGE_HEADER = "zing-page-badget .page-title-badget"
    CSS_TABLE_NAME = ".table-card.mat-card .title"
    CSS_TABLE_VIEW_COLUMN = ".zt-column-icon"
    CSS_SELECTOR_STATUS_CELL_ICON = ".ag-cell-value status-connection-renderer"
    CSS_SELECTOR_RISK_LEVEL_ICON = "zing-risk-widget"
    CSS_SELECTOR_PROTECTION_ICON = "svg.round-progress"
    CSS_SELECTOR_BASELINE_ICON = "img.baseline"
    CSS_SELECTOR_DEVICE_ICON = "div.ui-grid-cell-contents > div.iot-image-container > img"
    CSS_SELECTOR_DEVICE_NAME = ".zing-link"
    CSS_SELECTOR_FILTER_APP_TAG = ".zt-filter-tags .mat-chip-color-low-blue .text"

    COLUMN_NEED_TEXT = ['E']
    COLUMN_HANDLE_TEXT = ['E']

    # Device Type Pie Diagram
    CSS_PIE_GRAPH_PAGES = '.mat-paginator-range-label'
    CSS_PIE_GRAPH_HEADERS = 'th.mat-header-cell'
    CSS_PIE_GRAPH_PIE_SECTION = ".dashboard-card-content path.pie"
    CSS_PIE_GRAPH_INDEX = ".dashboard-card-content .breadcrumb"
    CSS_PIE_GRAPH_GO_BACK = "zing-dashboard-devices path+text"
    CSS_PIE_TABLE_ROW = ".mat-table tbody tr"
    CSS_PIE_GRAPH_NEXTPAGE = ".dashboard-card-content .mat-paginator-navigation-next"
    CSS_PIE_HOVER_TOOLTIP = "zing-dashboard-devices-tooltip .mat-tooltip"

    CSS_EXPORT_BUTTON = ".zt-download-icon"
    CSS_SEARCH_ICON = ".material-icons.search-icon"
    CSS_SEARCH_DIALOG = "zing-table-search mat-form-field input"

    CSS_DOWNLOAD_COUNT_MESSAGE = ".zt-selected-count"

    CSS_INVENTORY_CHECKBOX = ".ag-selection-checkbox:not(.ag-hidden) .ag-icon-checkbox-unchecked " #".zt-ag-grid span.ag-selection-checkbox" #'.zingTable div.ui-grid-selection-row-header-buttons'

    CSS_DOWNLOAD_INPROGRESS_MESSAGE = 'mat-progress-spinner svg circle'

    CSS_SELECTED_INVENTORY_NUM_TEXT = '.zingTable .selection-bar .selected-text'
    CSS_DOWNLOAD_SELECTED_INVENTORY_BUTTON = '.zb-table-selection-bar .group-left .zb-table-download-selected'
    CSS_DOWNLOAD_SELECTED_INVENTORY_INPROGRESS_MESSAGE = 'div.download-in-progress'
    CSS_DOWNLOAD_SELECTED_INVENTORY_SUCCESS_DOM = '.zing-qa-hidden-dom'

    # Widgets when hovering over element entries
    CSS_DEVICE_TOOLTIP = "zing-device-tooltip"
    CSS_DEVICE_WIDGET_TITLE = "zing-device-tooltip .title-text"
    CSS_DEVICE_WIDGET_POLICY = ".zt-create-policy"
    CSS_DEVICE_WIDGET_RISK = ".zt-risk"
    CSS_DEVICE_WIDGET_OS = "p.zt-device-os"
    CSS_DEVICE_WIDGET_PROFILE = ".profile-type-container"
    CSS_DEVICE_WIDGET_LAST_ACTIVITY = ".last-activity"
    CSS_DEVICE_WIDGET_IP = ".zt-device-ip"
    CSS_DEVICE_WIDGET_MACADDRESS = ".zt-device-mac"
    CSS_DEVICE_WIDGET_TYPE = '.zt-profile-type'
    CSS_POLICY_CANCEL_BUTTON = "zing-button-widget[aria-label='cancel']"
    CSS_DEVICE_TOOLTIP_ALERTS = ".zt-alert-link"
    CSS_DEVICE_ALERTS_POPUP = "a.mat-menu-item"

    # More Device Inventory Page stuff
    CSS_SELECTOR_DEVICE_ROW_ELEMENTS = "[name='inventory'] .ag-center-cols-container .ag-row"
    CSS_SELECTOR_DEVICE_CHECKBOXES = "ng-md-icon[name='select_button_click'] svg"
    CSS_SELECTOR_DEVICE_BULK_EDIT_BUTTON = '.zingTable .zing-hide-for-readonly i[title=\'Edit\']'
    CSS_SELECTOR_PAGE_NAVIGATOR = ".zt-page-selection"
    CSS_SELECTOR_PAGE_OPTIONS = '[ng-repeat="page in ctrl.pageNums"]'

    # Bulk editing stuff
    originalData = [True, "Camera", "Dropcam", "ZingBox", "Original Model", "Original Land",
                    "This is the OG description"]
    alteredData = [False, "generic", "Huawei Device", "YAKUMO Enterprise", "XiaoMi", "ZBAT Test Land",
                   "This is a zbat testing description, please ignore"]
    CSS_SELECTOR_BULK_MENU_TITLE = 'div.bulk-editing-title-text'
    CSS_SELECTOR_BULK_IOT = 'div > div > div > div > div > #bulk-editing-iot-icon'
    CSS_SELECTOR_BULK_NON_IOT = 'div > div > div > div > div > #bulk-editing-non-iot-icon'
    CSS_SELECTOR_BULK_EDITING_CATEGORY = 'div.bulk-editing-category input[role=\'combobox\']'
    CSS_SELECTOR_BULK_EDITING_PROFILE = 'div.bulk-editing-profile input[role=\'combobox\']'
    CSS_SELECTOR_BULK_EDITING_VENDOR = 'div.bulk-editing-vendor input[role=\'combobox\']'
    CSS_SELECTOR_BULK_EDITING_MODEL = 'div.bulk-editing-model input[role=\'combobox\']'
    CSS_SELECTOR_BULK_EDITING_LOCATION = 'div.bulk-editing-location input[role=\'combobox\']'
    CSS_SELECTOR_BULK_EDITING_TAGS = 'div.bulk-editing-tags input[role=\'combobox\']'
    CSS_SELECTOR_BULK_EDITING_DESCRIPTION = 'div.bulk-editing-description textarea'
    CSS_SELECTOR_BULK_EDITING_CLOSE = 'i.material-icons.close'
    CSS_SELECTOR_DEVICE_NAMES = "[name='inventory'] .ag-cell-wrapper .zing-link" #'a.ng-binding.ng-isolate-scope'
    CSS_SELECTOR_ALT_DEVICE_EDIT_BUTTON = "[name='Edut Devices'] span.ng-scope"
    CSS_SELECTOR_DEVINV_SEARCH = 'input#table-search'
    CSS_SELECTOR_SEARCH_TOGGLE = '[name=\'search_toggle\'][tooltip-text=\'Search\'] svg'
    CSS_SELECTOR_SEARCH_CLEAR = "ng-md-icon[icon='close']"
    CSS_SELECTOR_SEARCH_COUNT = ".pagination-wrap"
    CSS_SELECTOR_IOT_IMAGE = 'div > .iot-image-container'
    CSS_SELECTOR_COLUMN_FILTER_BUTTON = 'ng-md-icon[ns-popover-trigger=\'click\']'
    CSS_SELECTOR_DEVICE_COLUMN_HEADER = '.ui-grid-header-cell-label'
    CSS_SELECTOR_BULK_EDITING_OK_BUTTON = '.submit'
    CSS_SELECTOR_BULK_EDITING_CONFIRM_YES = 'md-dialog button.md-raised[ng-click=\'bulkEditingModalCtrl.bulkEdit()\']'

    # Device Inventory Local Filters
    CSS_SELECTOR_DEVICE_FILTER_ICON = "a.space-out.filter-list"
    CSS_SELECTOR_ADD_FILTER = "a.add-a-filter"
    CSS_FILTER_EDIT_OVERLAY = ".filter-select-overlay"
    CSS_LOCAL_FILTER_SAVE = "i.zing_save_active"
    CSS_LOCAL_FILTER_APPLY = "button.mat-button.secondary"
    CSS_LOCAL_FILTER_RESET = "a.zt-reset-button"
    CSS_LOCAL_FILTER_CARD = ".filter-select-overlay .title span"
    CSS_CLICK_TO_SELECT_FILTER = ".zing_icon_expand"
    CSS_FILTER_OPTION = ".option-list .mat-option-text"
    CSS_FILTER_VALUE = ".filter-option-group input+span"
    CSS_SEARCH_TAG = ".zt-search-field-tag"
    CSS_SEARCH_TAG_X = ".zt-search-field-tag mat-icon"

    CSS_SELECTOR_DEVICE_FILTER_CATEGORY_FIELD = "[placeholder='Category']"
    CSS_SELECTOR_DEVICE_FILTER_PROFILE_FIELD = "[placeholder='Profile']"
    CSS_SELECTOR_DEVICE_FILTER_VENDOR_FIELD = "[placeholder='Vendor']"
    CSS_SELECTOR_DEVICE_FILTER_TAG_FIELD = "[placeholder='Asset Tag']"
    CSS_SELECTOR_DEVICE_FILTER_MODEL_FIELD = "[placeholder='Model']"
    CSS_SELECTOR_DEVICE_FILTER_LOCATION_FIELD = "[placeholder='Location']"
    CSS_SELECTOR_DEVICE_FILTER_DESCRIPTION_FIELD = "[placeholder='Description']"
    CSS_SELECTOR_FILTER_APPLY = "button.apply"
    CSS_SELECTOR_CLEAR_FILTER_BUTTON = "[role='button'][name='Close Filter list chips']"
    CSS_RESET_MENU_BUTTON = "[name='Open reset menu']"

    CSS_SELECTOR_DEVICE_GENERAL_SORT = [["Device Name", "Profile", "IP Address", "MAC Address", "Category"],
                                        ["Confidence Score", "Description", "Type", "Vendor", "Model", "OS"],
                                        ["OS Support", "Location", "DHCP", "Source", "Risk", "SMB Version"],
                                        ["Last Activity", "Internet Access", "Protocols", "International Access",
                                         "Countries", "First Seen"]]

    CSS_SELECTOR_DEVICE_TEXT_COLUMNS_NEO = ["Device Name", "Profile", "Vendor", "Model", "OS", "Category",
                                            "Description",
                                            "Location", "Wire-Wireless", "Endpoint Protection", "Asset Tag", "AET"]
    filtered_columns_list = [["Profile", "Vendor", "Model", "IP Address", "Subnet"],
                             ["MAC Address", "Category", "Description", "Location"]]

    TEST_DEVICE = "Rhombus-Camera"


class DeviceDetailLocators:
    CSS_INFO_CARD = "#device_overall_info"
    CSS_DEVICE_IMAGE = '#device_overall_info .device-image'
    CSS_DEVICE_ESSENTIAL_INFO = '#device_overall_info .device-essential-info'
    CSS_DEVICE_SECONDAYR_CARD = '.device-detail-overall.secondary-card'
    CSS_SECURITY_PART = '.security-part'
    CSS_SELECTOR_GENERAL_TEXT_DETAIL = "td.ng-binding"
    CSS_TRAFFIC_NETWORK_CARD = '.device-traffic-network-loader .md-headline'
    CSS_EXPLORE_TOPOLOGY_LINK = '.explore-topology'
    CSS_TOPOLOGY_GRAPH = '#deviceTopologySVG'
    CSS_LEGEND_TITLE = '.legend-title'
    CSS_LEGEND_GROUP = '.legend-group'
    CSS_LEGEND_ROW = '.legend-row'
    CSS_LEGEND_ITERATION = ".legend-row:nth-of-type({}) .legend-text"
    CSS_FILTER_FORM = '[name="devieDetailNetworkTopologyCtrl.filterForm"]'
    CSS_RESET_FILTER = 'div.reset-filter'
    GROUP_FILTER = '.grouped-filter.alert-filter'
    CSS_AGGREGATION_LIST = '.network-agg-list .toggle-row div.group-toggle'
    CSS_AGGREGATION_DATA_ROW = '.network-agg-list .data-row'
    CSS_NO_HEADER_DATA_ROW = ".view-list .data-row"
    CSS_OUTER_CIRCLE = '.circle-outer'

    CSS_CIRCLE_BASE = "circle.circle.default.{}"
    CSS_CIRCLE_DEFAULT = "circle.circle.default"
    CSS_TOOLTIP_GROUP_ON_CIRCLE = '.zing-shadow-box .tooltip-group:nth-of-type(1)'
    CSS_TOOLTIP_ON_CIRCLE = '[id="topologyTooltip"] .zing-shadow-box'
    CSS_LEGEND_FILTER_RESET = "#deviceCircle .device-text"
    CSS_PROTOCOL_FILTER = ".grouped-filter input:nth-of-type(1)"
    CSS_PROTOCOL_FILTER_RESET = "div.reset-filter"
    CSS_TOPOLOGY_DEVICE_NAME = ".info .name"


    CSS_STATISTICS_COLUMN = '.app-stat .layout-column'
    CSS_APPLICATION_TAB = '.application-tabs md-tab-item'
    CSS_APPLICATION_PIE = 'zing-device-app-pie-table .app-pie'
    CSS_APPLICATION_TABLE = 'zing-device-app-pie-table .app-table'
    CSS_PROTOCOL_APP_STAT = "#device-network .app-stat"
    CSS_NETWORK_DETAIL_ROW = '#network-detail > div[layout="row"]'
    CSS_NETWORK_DETAIL_BAR = '#network-detail .md-bar2'
    CSS_CATEGORY_HEADING = 'zing-category-bubble .heading-row'
    CSS_CATEGORY_ROW = 'zing-category-bubble .item-row'
    CSS_CATEGORY_CIRCLE_IN_ROW = 'zing-category-bubble .item-row .circle-row'

    CSS_SELECTOR_CATEGORY_VIEW_BUTTON = 'div[name="Open category view"] > div'
    CSS_SELECTOR_DETAIL_VIEW_BUTTON = "div[name='Open device view']"
    CSS_SELECTOR_NETWORK_USAGE_CHART_PATHS = '#google-sankey-multiple svg g'

    CSS_SECURITY_TAB = ".device-detail-tab[action='Security']"
    CSS_ALERTS_TAB = ".device-detail-tab[action='Alerts']"
    CSS_RISK_ALERT_CARD = ".risk-alert-card"
    CSS_ALERT_ACTION_BTN = ".alert-action-dropdown button"
    CSS_ALERT_OPTION_BTN = "md-menu-item button.md-button"
    CSS_RESOLVE_CARD = "md-dialog .alert-resolve"
    CSS_RESOLVE_TYPE_NO_ACTION = 'md-radio-button:nth-of-type(2)'
    CSS_RESOLVE_CARD_REASON = 'input[name="reason"]'
    CSS_RESOLVE_CARD_SUBMIT = ".zing-button.zing-button-blue"
    CSS_REACTIVATE_CARD_COMMENT = 'input[name="comment"]'
    CSS_REACTIVATE_CARD_SUBMIT = 'button[type="submit"]'
    CSS_ACTIVE_ALERTS = 'zing-historical-alerts .filter-item:nth-of-type(1)'




