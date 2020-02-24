class AdministrationLoc(object):
    CSS_NAV_ADMINISTRATION = "[data-title='Administration']"
    CSS_CLICK_TO_CHOOSE = '.nav-menu li a[href*="{}"]'
    CSS_PAGE_HEADER = "zing-page-badget .page-title-badget"
    CSS_PAGE_NAVIGATION = ".zing-table-tenantAccounts .pagination-wrap"

    # User Account Page
    user_account_column_list = ["Full Name", "Email (Username)", "Role", "Sites", "Last Login", "Last Login Location",
                                "Two-Factor Authentication", "Access Keys", "Vulnerability Scan"]
    search_item_list = ["Full Name", "Email (Username)", "Role", "Sites",
                        "Two-Factor Authentication", "Vulnerability Scan"]
    CSS_ADMIN_SETTING_HEADER = ".account-config-content h2"
    CSS_ADMIN_SETTING_CONTENT = ".account-config-content p"
    CSS_PASSWORD_EXPIRATION = ".account-config-content div:nth-of-type(2) h3"
    CSS_PW_EXPIRATION_SELECTION = ".account-config-content div:nth-of-type(2) md-select"

    CSS_IDLE_TIMEOUT = ".account-config-content div:nth-of-type(3) h3"
    CSS_IDLE_TIMEOUT_SELECTION = ".account-config-content div:nth-of-type(3) md-select"
    CSS_SAVE_BUTTON = "button.md-primary"
    CSS_CANCEL_BUTTON = "a.cancel"
    CSS_2FA_SETTING = ".account-config-content div:nth-of-type(4) h3"
    CSS_VULNERABILITY_SCANNING_SETTING = ".account-config-content div:nth-of-type(5) h3"
    CSS_REMOTE_DEBUGGING_SETTING = ".account-config-content div:nth-of-type(6) h3"
    CSS_SSO_SETTING = ".account-config-content div:nth-of-type(7) h3"

    CSS_TABLE_HEADER = ".zing-table-tenantAccounts .table-title"
    CSS_SEARCH_ICON = ".zing-table-tenantAccounts [icon='search']"
    CSS_VIEW_COLUMN_ICON = ".zing-table-tenantAccounts [icon='view_column']"
    CSS_ADD_ICON = ".zing-table-tenantAccounts [icon='add']"
    CSS_SETTING_ICON = ".zing-table-tenantAccounts i.material-icons.dp24"
    CSS_TEXT_BELOW_TABLE = ".zing-table-tenantAccounts span.text"
    CSS_INVITED_USER_ACCOUNTS = ".zing-table-inviteUserAccounts .table-title"
    CSS_INVITED_USER_TABLE_SEARCH = ".zing-table-inviteUserAccounts [icon='search']"
    CSS_INVITED_USER_TABLE_TEXT_BELOW = ".zing-table-inviteUserAccounts span.text"
    CSS_INVITED_USER_TABLE_PAGE_NAV = ".zing-table-inviteUserAccounts .pagination-wrap"

    CSS_EULA_POPUP = ".eula-popup"
    CSS_TENTH_PAGE = '.page[data-page-number="10"]'
    CSS_ACCEPT_EULA = 'zing-button-widget'
    CSS_WELCOME_TEXT = '.welcome-text'
    CSS_REGISTER_NAME = "input#firstname"
    CSS_REGISTER_LAST_NAME = "input#lastname"

    # Notifications Page
    CSS_NOTIFICATION_CONFIG_CARD = "zing-notify .mat-card"
    CSS_THREAT_DETECTION_CONFIG = ".zt-threat-input .mat-chip-input"
    CSS_SYSTEM_ALERTS_CONFIG = ".zt-system-input .mat-chip-input"
    CSS_DROPDOWN_ACCOUNT_OPTIONS = ".mat-option-text"
    CSS_ACCOUNT_CHIPS = ".mat-chip"
    CSS_CLOSE_ACCOUNT_CHIP = ".zing_icon_close .chip-icon"
    CSS_SAVE_BUTTON_ENABLED = ".zt-save-button"
    CSS_SAVE_BUTTON_DISABLED = ".zt-save-button"
    CSS_SAVE_NOTIFICATION_BANNER = ".notification-bar-text-action"

    # My Inspector Page
    CSS_INSPECTOR_SITE_OVERVIEW = ".summary-section"

    CSS_SELECT_SITES = ".inspector-management-bar md-select-value"      
    CSS_TOTAL_SITES_NUM = ".zt-total-number-of-sites .total-sites"
    CSS_INSPECTOR_MANAGEMENT_TRAFFIC = ".inspector-management-bar .total-traffic-text"      
    CSS_TOTAL_SITES_TITLE = ".zt-total-number-of-sites .sub-title-site"
    CSS_INSPECTOR_MANAGEMENT_ICONS = ".inspector-management-bar .layout-row:nth-of-type(3) button"      
    CSS_TOTAL_INSPECTORS_NUM = ".zt-total-inspectors .total-sites"
    icons_list = ["view_module", "show_chart", "add", "Download inspector", "settings"]     
    CSS_TOTAL_INSPECTORS_TITLE = ".zt-total-inspectors .sub-title-site"
    CSS_SITE_ITEM = ".site-item"        

    CSS_TOTAL_CONNECTED_INSPECT_NUM = ".zt-total-connected-inspectors .total-sites"
    CSS_TOTAL_CONNECTED_INSPECT_TITLE = ".zt-total-connected-inspectors .sub-title-site"
    CSS_TOTAL_DISCONNECTED_INSPECT_NUM = ".zt-total-disconnected-inspectors .total-sites"
    CSS_TOTAL_DISCONNECTED_INSPECT_TITLE = ".zt-total-disconnected-inspectors .sub-title-site"
    CSS_CLOUD_TRAFFIC_SIZE = ".zt-total-site-cloud-traffic"
    CSS_CLOUD_TRAFFIC_TITLE = ".spec-padding-cloud .sub-title-site"
    CSS_ANALYZED_TRAFFIC_SIZE = ".zt-total-site-analyzed-traffic .total-sites"
    CSS_ANALYZED_TRAFFIC_TITLE = ".zt-total-site-analyzed-traffic .sub-title-site"

    CSS_SITE_ITEM = ".site-main"
    CSS_SITE_ITEM_NUMBER = ".site-main .siteln .siteln"
    CSS_DOWNLOAD_INSPECTOR_ICON = ".zt-download-inspector.addicon"
    CSS_ADD_INSPECTOR_ICON = ".zt-create-site-icon.addicon"

    CSS_SITE_NUMBER_ABOVE_TABLE = ".zt-number-of-sites .siteln"
    CSS_SITE_SECTION_CONTENT = ".site-description.zt-site-card"
    CSS_SITE_CONNECTED_STATUS = ".zt-site-connected-status"
    CSS_SITE_NAME = ".zt-site-name"
    CSS_SITE_INSPECTOR_NUM = ".zt-number-of-inspectors"
    CSS_SITE_INSPECTOR_DISCONNECTED_NUM = ".dis-insp.inspector-denom"
    CSS_SITE_MONITORED_DEVICES = ".zt-site-monitored-devices"
    CSS_SITE_DISCOVERED_DEVICES = ".zt-site-discovered-devices"
    CSS_SITE_RISK_SCORE = ".zt-site-risk-score"
    CSS_SITE_SUBNET = ".zt-site-subnet"
    CSS_SITE_TRAFFIC = ".zt-site-traffic"
    CSS_SITE_SHARE_ICON = ".icon-share .zt-add-icon"
    CSS_SITE_EXPAND_ICON = ".icon-share .zt-expand-icon"
    CSS_SITE_COLLAPSE_ICON = ".zt-collapse-icon"
    CSS_INSPECTOR_EXPANDED_DETAIL = ".mat-expanded zing-inspector-detail"

    CSS_INSPECTOR_CLOUD_ICON = "i.material-icons"
    CSS_INSPECTOR_NAME = '.insp-name'
    CSS_INSPECTOR_COUNT = '.insp-count'
    CSS_INSPECTOR_STATUS = '.active-status'
    CSS_INSPECTOR_REFRESH_ICON = ' .zt-refresh-icon'
    CSS_INSPECTOR_MORE_ICON = '.zt-more-icon'
    CSS_INSPECTOR_SUMMARY = '.zt-inspector-summary'

    # Active Probing Page
    CSS_PROBE_CARD_TITLE = "md-title"
    CSS_EDIT_TOOLS = ".edit-part"
    CSS_DESCRIPTION_PROBING = ".description"
    CSS_PROBING_TYPE = ".group-title"
    CSS_PROPERTY_TITLES = "p.property-title"
    CSS_PROPERTY_VALUES = "p.property-title~p, p.property-title~div"
    CSS_EDIT_PANEL_BUTTON = ".edit-part .material-icons"
    CSS_PROBE_DROPDOWN = ".md-select-value"
    CSS_PROBE_DROP_OPTS = ".md-clickable ._md [role='option']"
    

    # Report Config Page
    report_config_list = ["Status", "Report Name", "Template", "Scope", "Frequency", "Next Report On", "Created by", "Date"]
    CSS_REPORT_TABLE_TITLE = ".report-config-list .table-title"
    CSS_REPORT_TABLE_SEARCH = ".report-config-list [icon='search']"
    CSS_REPORT_TABLE_VIEW_COLUMN = ".report-config-list [icon='view_column']"
    CSS_REPORT_TABLE_ADD = ".report-config-list [icon='add']"
    CSS_REPORT_TABLE_BELOW_TEXT = ".report-config-list span.text"
    CSS_REPORT_TABLE_PAGE_NAV = ".report-config-list .pagination-wrap"

    # Audit Log Page
    audit_log_column_list = ["Time", "Activity", "User", "Description"]
    CSS_AUDIT_LOG_TITLE = ".title .title" #".zingTable .table-title"
    CSS_DATE_DROPDOWN = ".content .filter-control"
    CSS_DATE_DROPDOWN_OPTS = ".options .ng-star-inserted"
    CSS_AUDIT_LOG_VIEW_COLUMN_ICON = ".zt-column-icon"
    CSS_AUDIT_LOG_HEADER = ".customHeaderLabel"
    CSS_AUDIT_LOG_DOWNLOADER = ".material-icons.download-icon"
    CSS_TEXT_BELOW_AUDIT_LOG = "zing-table-paginator"
    CSS_AUDIT_LOG_PAGENATION = ".zt-page-selection"
    CSS_COLUMN_EVT_1 = "[col-id='eventType']"
    CSS_COLUMN_TIME_1 = "[col-id='timestamp']"
    CSS_COLUMN_USERNAME_1 = "[col-id='username']"
    CSS_COLUMN_DESCRIPTION_1 = "[col-id='description']"


    # License Page
    license_column_list = ["Product/Service", "Quantity", "Start Date", "Expiration Date", "Usage"]
    CSS_LICENSE_ACTIVE_TAB = ".mat-tab-labels .mat-tab-label-active"
    CSS_ALL_TABS = ".mat-tab-labels .mat-tab-label"
    CSS_LICENSE_HEADERS = "div.header-item"
    CSS_LICENSE_PAGE = '.page'
    CSS_LICENSE_PAGE_CONTENT = ".padded"
    CSS_LICENSE_CARD_TITLE = '.mat-card-title'
