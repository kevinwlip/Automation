class DashboardSummaryLoc(object):
    """ Element locators for UI Dashboard Executive Summary """
    # This identifies the current active tab
    CSS_DASHBOARD_NGSTAR_INSERTED_ACTIVE = "li[class='active ng-star-inserted']"
    # This identifies the inactive tab and other elements on the page, 29 in total
    CSS_DASHBOARD_NGSTAR_INSERTED = "li[class='ng-star-inserted']"
    # These are partial elements found with CSS_DASHBOARD_NGSTAR_INSERTED.
    CSS_DASHBOARD_NGSTAR_INSERTED_LIST = ["inventory","security", "operational", "total discovered devices", \
            "total monitored devices", "active alerts to date", "vulnerabilities to date", "all devices"]
    CSS_DASHBOARD_SUBNETS = "a[pageid='subnets']"
    CSS_DASHBOARD_RISK_SCORE = "div[class='inner zing-tooltip-text']"
    CSS_DASHBOARD_TABLES = "table[class='mat-table']"
    
    # Global Filters
    CSS_DASHBOARD_GLOBAL_FILTER_RESET_UNABLE = '.content .filter-icon'
    CSS_DASHBOARD_GLOBAL_FILTER_RESET_ABLE = '.content .reset.filter-icon'
    CSS_DASHBOARD_GLOBAL_FILTERS= '.content .filter-control li'
    CSS_DASHBOARD_GLOBAL_FILTER_ELEMENTS = 'div.content-wrapper'
    CSS_DASHBOARD_GLOBAL_FILTER_CHIPS = 'mat-chip.mat-chip.mat-primary'

    # Top Bar
    bar_list = ["Total Discovered Devices", "Total Monitored Devices", "Subnets", "Risk Score", "Active Alerts to Date", "Vulnerabilities to Date"]
    CSS_DASHBOARD_TOP_BAR = ".dashboard-card-content zing-dashboard-overall ul"
    CSS_DASHBOARD_TOP_BAR_ENTRIES = "ul .inner"
    CSS_DASHBOARD_DEVICE_CELL_DEVICES = ".mat-cell .devices"
    CSS_DASHBOARD_DEVICE_CELL_PROFILES = ".mat-cell.mat-column-profiles"

    # Devices Section
    CSS_DEVICES_CARD = "zing-dashboard-devices zing-dashboard-card-template"
    CSS_DASHBOARD_TITLE_DEVICES = "zing-dashboard-devices"
    CSS_DASHBOARD_DEVICES_LIST = ["Devices", "Device Distribution by Type", "All devices", \
            "Type", "Devices", "Categories", "Profiles", "Devices at Risk"]
    CSS_DASHBOARD_DEVICES_CHART = "div[class='chart']"
    CSS_DASHBOARD_DEVICES_CHART_TOOLTIP = "zing-dashboard-devices-tooltip"
    CSS_DASHBOARD_DEVICES_CHART_NON_IOT = ".non_iot.pie"
    CSS_DASHBOARD_DEVICES_CHART_OTHER_IOT = ".iot.pie"
    CSS_DASHBOARD_DEVICE_CARD_DEVICE_NUM = ".devices .text"

    # Sites Section
    CSS_DASHBOARD_TITLE_SITES = "zing-dashboard-sites zing-dashboard-card-template"
    CSS_DASHBOARD_SITES_TABLE_LIST = ["Site Name", "Inspectors", "Monitored Devices", \
            "Discovered Devices","Risk Score","Subnets"]

    CSS_DASHBOARD_SITES_NUMBERS = ".inner a .number"
    CSS_DASHBOARD_TABLE_INSPECTOR_NUMBERS = ".mat-column-inspectors a.zing-dashboard-link"
    CSS_DASHBOARD_SITES_MONITORED = ".cdk-column-monitoredDevices.mat-cell"
    CSS_DASHBOARD_SITES_DISCOVERED = ".cdk-column-discoveredDevices.mat-cell"
    CSS_DASHBOARD_SITES_PAGINATION_LABEL = "zing-dashboard-sites .mat-paginator-range-label"
    CSS_DASHBOARD_SITES_RISK_SCORE = ".cdk-column-riskScore a"
    CSS_INSPECTOR_TITLE_CHECK_BRIEF = ".zt-number-of-sites"
    CSS_DASHBOARD_TABLE_INSPECTOR_NAMES = ".cdk-column-name .zing-dashboard-link"

    # Applications and Protocols Section
    CSS_DASHBOARD_APPLICATIONS = "zing-dashboard-app-protocols"
    CSS_DASHBOARD_APPLICATIONS_TEXT = ["Applications", "expand_more"]
    CSS_DASHBOARD_APPLICATIONS_TABLE = "zing-dashboard-app-list"
    CSS_DASHBOARD_APPLICATIONS_TABLE_LIST = ["Application", "Application Category", "Used by Devices"]
    CSS_DASHBOARD_EXPAND_ICON = "zing-dashboard-app-protocols > div > div > div > mat-icon"
    CSS_DASHBOARD_BUTTON_PROTOCOLS = "button[class='mat-menu-item ng-star-inserted']"
    CSS_DASHBOARD_PROTOCOLS = ".app-protocols-container"
    CSS_DASHBOARD_APP_DROPDOWN = ".zt-app-dropdown"
    CSS_DASHBOARD_COLUMN_HEADERS = ".app-protocols-container [role='columnheader']"
    CSS_DASHBOARD_APP_SUBTITLE = ".app-protocols-container .sub-title.zt-app-description"
    CSS_DASHBOARD_APP_LINK = ".app-protocols-container zing-dashboard-app-list .zing-dashboard-link"
    CSS_DASHBOARD_APP_CLICKMORE = "[pageid='newapplications']"


    # Network Segments Section
    CSS_DASHBOARD_NETWORK_SEGMENTS = "zing-dashboard-vlans-summary"

    # Risk Overview Section
    CSS_DASHBOARD_RISK_OVERVIEW = "zing-dashboard-risk-score-trend"
    CSS_DASHBOARD_RISK_RECTANGLES = ".block"
    CSS_DASHBOARD_RISK_OVERLAY = "zing-dashboard-risk-score-trend-dialog"
    CSS_DASHBOARD_RISK_OVERLAY_DATE = "zing-dashboard-risk-score-trend-dialog .header"
    CSS_DASHBOARD_RISK_OVERLAY_RISK_SCORE = "zing-dashboard-risk-score-trend-dialog .risk-score"
    CSS_DASHBOARD_RISK_OVERLAY_DETAIL_BLOCK = ".cdk-overlay-pane zing-dashboard-risk-score-trend-dialog .detail-table div"
    CSS_DASHBOARD_RISK_OVERLAY_LAST_RECT = ".block.last"
    CSS_DASHBOARD_RISK_OVERLAY_ALERT_NUM = ".cdk-overlay-container [pageid='alerts']"
    CSS_DASHBOARD_RISK_OVERLAY_VULN_NUM = ".cdk-overlay-container [pageid='vulnerabilities']"
    CSS_DASHBOARD_RISK_OVERLAY_GENERIC = ".cdk-overlay-container zing-dashboard-risk-score-trend-dialog tr"

    # Alerts Section
    CSS_DASHBOARD_ALERTS = "zing-dashboard-alerts"

    # Vulnerabilities Section
    CSS_DASHBOARD_VULNERABILITIES = "zing-dashboard-vulnerabilities"
    CSS_DASHBOARD_TOP_BAR = "zing-page-badget"

    #VLAN Section
    CSS_DASHBOARD_VLAN_TITLE = "zing-dashboard-vlans-summary .title-wrap .title"
    CSS_DASHBOARD_VLAN_SUBNET = "zing-dashboard-vlans-summary [pageid='subnets'] .numbers"
    CSS_DASHBOARD_VLAN_NUMBERS = "zing-dashboard-vlans-summary .numbers"
    CSS_DASHBOARD_VLAN_MED_NUM = "zing-dashboard-vlans-summary .medical"
    CSS_DASHBOARD_VLAN_MED_CHART = "zing-dashboard-vlans-summary .others"
    CSS_DASHBOARD_VLAN_CAPTIONS = "zing-dashboard-vlans-summary .caption"

    #Top Bar
    bar_list = ["Discovered Devices", "Monitored Devices", "Subnets", "Risk Score", "Active Alerts", "Vulnerabilities"]
    CSS_DASHBOARD_TOP_BAR = ".dashboard-card-content zing-dashboard-overall ul"
    CSS_DASHBOARD_TOP_BAR_ENTRIES = "ul .inner"
    CSS_DASHBOARD_DEVICE_CELL_DEVICES = ".mat-cell .devices"
    CSS_DASHBOARD_DEVICE_CELL_PROFILES = ".mat-cell.mat-column-profiles"

    CSS_DASHBOARD_VULN_CARD_TITLE = "zing-dashboard-vulnerabilities .title"
    CSS_DASHBOARD_VULN_CARD_TO_DATE = "zing-dashboard-vulnerabilities .title-wrap[zingclickablelink=''] .number"
    CSS_DASHBOARD_VULN_CARD_DEVICES = "zing-dashboard-vulnerabilities [zingclickablelink=''] .number"
    CSS_DASHBOARD_VULN_CARD_LINKS = "zing-dashboard-vulnerabilities .zing-dashboard-link[zingclickablelink='']"
    CSS_DASHBOARD_VULN_CARD_CAT_LINK = "zing-dashboard-vulnerabilities .clipped .link-text.zing-dashboard-link"

    CSS_DASHBOARD_ALERTS_CARD_TITLE = "zing-dashboard-alerts .title"
    CSS_DASHBOARD_ALERTS_CARD_BIG_NUMBER = "zing-dashboard-alerts .title-wrap[zingclickablelink='']"
    CSS_DASHBOARD_ALERTS_CARD_FILTER_LINKS = "zing-dashboard-alerts .hover-content"
    CSS_DASHBOARD_ALERTS_CARD_FILTER_LINK_LINKS = "zing-dashboard-alerts .hover-content [zingclickablelink='']"

    CSS_DASHBOARD_PROTOCOL_DROPDOWN = "#zt-app-menu-protocols"
    CSS_DASHBOARD_PROTOCOLS_IN_NUM = ".zt-protocol-in-link-text1"
    CSS_DASHBOARD_PROTOCOLS_OUT_NUM = ".zt-protocol-out-link-text1"
    CSS_DASHBOARD_PROTOCOLS_IN_BAR = ".total-in"
    CSS_DASHBOARD_PROTOCOLS_OUT_BAR = ".total-out"
<<<<<<< HEAD
    CSS_DASHBOARD_PROTOCOLS_BIG_NUMBER = ".zt-protocol-number"
    CSS_DASHBOARD_PROTOCOLS_LINK = ".zt-protocol-description-protocol"
=======
    CSS_DASHBOARD_PROTOCOLS_BIG_NUMBER = ".zt-wrapper .content .sub-title"
    CSS_DASHBOARD_PROTOCOLS_LINK = ".zt-protocol-description-protocol" 
>>>>>>> b74543e49fe147fc382916fd41dee6949c9e36b7


class DashboardSecurityLoc(object):
    """ Element locators for UI Dashboard Security """
    CSS_ACTIVE = "zing-dashboard-tabs .active"
    CSS_SECURITY_SHOW_MORE_CARDS = '[ng-if="!categoryListingCtrl.showingAll"]'
    CSS_CARDS_IN_GROUPING = ".grouping-card.group"
    CSS_CARD_SECTION = "md-card._md"
    CSS_SELECT_SITES_PROFILES_CATEGORIES = 'div.md-subheader-inner button:nth-of-type({})'
    CSS_FIND_ACTIVE_TAB = "button.card-type-button.selected"
    CSS_SUM_CARD_IN_TAB = ".grouping-card.all .ng-scope"

    CLASS_NAME_IN_TAB = 'card-name'
    CLASS_DEPLOY_STATUS_IN_TAB = 'deploy-status'
    CLASS_BUTTON_ROW_IN_TAB = 'button-row'

    CLASS_TITLE_A_IN_CARD = 'item-title'
    CLASS_TITLE_B_IN_CARD = 'md-card-title'

    ID_GAUGE_ON_RISK_CARD = 'gaugeDivNew'
    CLASS_RISK_ROW_ON_RISK = 'risk-row'
    CLASS_RISK_LEVEL_ICON_ON_RISK = 'risk-level-icon'
    CLASS_RISK_NUM_ON_RISK = 'risk-number'
    CLASS_RISK_TEXT_DESCRIPTION = 'risk-text-description'
    CLASS_TOTAL_NUMBER_RISK = 'total-number'

    CLASS_NUMERICAL_DETAIL_NETWORK = 'numerical-detail'
    CLASS_DATA_ENCRYP_NETWORK = 'data-encryption'
    CLASS_ROW_IN_TABLE = "layout-row"
    CLASS_COUNT_NETWORK = "count"
    CLASS_ICON_NETWORK = "icon"

    CSS_SELECT_RANGE_DEVICE_BY = "md-card-title md-menu svg"
    CSS_SELECT_RANGE_OPTIONS_DEVICE_BY = '.md-open-menu-container[aria-hidden="false"] button'
    CSS_DOTS_DEVICE_BY = ".carousel_dots div"
    CSS_DOT_ACTIVE_DEVICE_BY = ".dot_chart.active"
    ID_DEVICE_PIE_CHART = "devices-pie-chart"
    CLASS_LAYOUT_COLUMN = 'layout-column'
    CLASS_CATEGORY_LIST = "category_listing"

    CSS_IN_OUT_BOUND_SELECT = 'md-card-title md-select-value'
    CSS_DROPDOWN_OPTIONS = '.md-active md-option'
    ID_GLOBAL_MAP = 'mapSVG'

    CLASS_HIGH_CHARTS_GROUND = "highcharts-background"
    CLASS_DOWNLOAD_ICON = "downloadicon"


class DashboardOperationalLoc(object):
    """ Element locators for UI Dashboard Operational """
    CSS_CATEGORY_DEVICE_CARD = "#category-card-wrapper md-card"
    CSS_CATEGORY_PROFILE_LIST = '.category-profile-card'
    CSS_RECT_HIGHCHARTS = 'rect.highcharts-background'
    CSS_HEALTH_USAGE_CARDS = '.healthcare-device-cards'
    CSS_HEADER_ROW = '.header.layout-row'
    CSS_HEALTHCARE_CATEGORY_DEVICE = '.healthcare-category-devices'
    CSS_HEALTH_BODY = '.healthcare-body'


class DashboardInventoryLoc(object):
    """ Element locators for UI Dashboard Inventory """
    CSS_ACTIVE = 'zing-dashboard-tabs .active'

    # Devices Card
    CSS_DEVICES_CARD_TITLE = 'zing-dashboard-devices .zt-title .title'
    CSS_DEVICES_PIE_OTHER_IOT = '.pie.iot'
    CSS_DEVICES_PIE_NON_IOT = '.pie.non_iot'
    CSS_DEVICES_PIE_TITLE = '.chart .label'
    CSS_DEVICES_TABLE_TITLE = 'li span'
    CSS_DEVICES_TABLE_HEADER1 = ".mat-sort-header-button[aria-label='Change sorting for name']"
    CSS_DEVICES_TABLE_HEADER2 = ".mat-sort-header-button[aria-label='Change sorting for devices']"
    CSS_DEVICES_TABLE_HEADER3 = ".mat-sort-header-button[aria-label='Change sorting for categories']"
    CSS_DEVICES_TABLE_HEADER4 = ".mat-sort-header-button[aria-label='Change sorting for profiles']"
    CSS_DEVICES_TABLE_HEADER5 = ".mat-sort-header-button[aria-label='Change sorting for riskyDevices']"
    CSS_DEVICES_TABLE_TYPE1 = ".type.non_iot"
    CSS_DEVICES_TABLE_TYPE2 = ".type.iot.other"
    CSS_DEVICES_TABLE_TYPE3 = ".type.iot.medical"
    CSS_DEVICES_TABLE_COL_VALUES1 = ".devices a.text"
    CSS_DEVICES_TABLE_COL_VALUES2 = "td.mat-column-categories"
    CSS_DEVICES_TABLE_COL_VALUES3 = "td.mat-column-profiles"
    CSS_DEVICES_TABLE_COL_VALUES4 = "td.mat-column-riskyDevices"
    CSS_DEVICES_TABLE_PAGINATION_LABEL = ".mat-paginator-range-label"
    CSS_DEVICES_TABLE_PREVIOUS_PAGE = ".mat-paginator-navigation-previous"
    CSS_DEVICES_TABLE_NEXT_PAGE = ".mat-paginator-navigation-next"

    # Device Categories Card
    CSS_DEVICE_CATEGORIES_CARD_TITLE = '.title .zt-title'
    CSS_DEVICE_CATEGORIES_SORTING = '.zt-title-sort'
    CSS_DEVICE_CATEGORIES_EXPAND = '.zt-expand-icon'
    CSS_DEVICE_CATEGORIES_SHOW_MORE = '.zt-load-more'
    CSS_DEVICES_CATEGORY_IMAGES = '.zt-image.image'
    CSS_DEVICES_CATEGORY_NAMES = '.zt-category-name'
    CSS_DEVICES_CATEGORY_SUBTITLES = '.cluster .sub-title'
    CSS_DEVICES_CATEGORY_RISK_SCORE_SUBTITLES = '.risk-score .sub-title'
    CSS_DEVICES_CATEGORY_TOTAL_DEVICES = '.zt-total-device'
    CSS_DEVICES_CATEGORY_TOTAL_PROFILES = '.zt-total-profile'
    CSS_DEVICES_CATEGORY_TOTAL_RISK_SCORES = '.zt-risk-score'
    CSS_DEVICES_CATEGORY_TOTAL_RISK_ICONS = '.ml-risk-level-icon'

    # Device Categories Details Card, need to add these in later

    # Subnets Card
    CSS_SUBNETS_CARD_TITLE = '.zt-title .title'
    CSS_SUBNETS_CARD_LEGENDS = '.legend.zt-legends .ng-star-inserted'
