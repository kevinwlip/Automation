class ProfileLoc(object):
    CSS_PROFILES_ENTRYPOINT="[data-title='Profiles']"
    CSS_PROFILE_TABLE = ".table-card.mat-card"
    CSS_PAGE_HEADER="zing-page-badget .page-title-badget"
    CSS_TABLE_NAME = ".table-card.mat-card .title"
    CSS_VIEW_COLUMN = ".zt-column-icon" #".table-header-card a:nth-of-type(1)"
    CSS_VIEW_COLUMN_CARD = ".column-selection-overlay"
    CSS_VIEW_COLUMN_CARD_BOXES = ".column-selection-overlay .mat-checkbox-layout"
    CSS_COLUMN_ALL_CELLS = ".ag-cell"
    CSS_INVENTORY_HEADER = ".ag-header-cell-sortable"
    CSS_TOTAL_ROWS_IN_TABLE = ".ag-center-cols-container .ag-row"
    CSS_ICON_DOWNLOADER = ".material-icons.download-icon"
    CSS_TEXT_BELOW = "zing-table-paginator"
    CSS_TABLE_PAGENATION = ".zt-page-selection"
    CSS_TOTAL_PAGES = ".paginator-right-element"
    CSS_NEXT_PAGES = ".zt-next-page-button"

    column_list = ["Profile Name", "Category", "Number of Devices", "First Seen On",
                   "Newest Device", "Device Type", "ACL Rule Sets"]

    CSS_SELECTOR_DEVICE_GENERAL_SORT = [["Profile Name", "Category", "Number of Devices", "First Seen On"],
                                        ["Newest Device", "Device Type", "ACL Rule Sets"]]
    
    CSS_ACL_BREADCRUMB = ".zb-breadcrumb-route-to-acl"
    CSS_ACL_CARD_TITLE = ".zb-acl-ruleset-title"
    CSS_ACL_CARD_BLOCK = ".zb-acl-ruleset-content .group"
    CSS_ACL_LINK = "acl-policy-count-renderer"

