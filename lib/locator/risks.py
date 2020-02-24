# Risks Page
class RisksVulnerabilitiesLoc(object):
    """ Element locators for Risks Vulnerabilites Page """
    # Menu to access Risks => vulnerabilities page
    CSS_RISKS_VULNERABILITIES = "ul[data-menu='risk'] li:nth-of-type(1)"
    CSS_RISKS_VULN_TITLE = "div[class='left']"
    CSS_RISKS_VULN_GLOBAL_FILTER = "zing-global-filter"
    CSS_RISKS_VULN_GLOBAL_FILTER_TEXT = ["All Sitesexpand_more", "All Devicesexpand_more"]

    CSS_RISKS_VULN_LIST = "zing-vulnerability-list"
    CSS_RISKS_VULN_SUMMARY_CARD = "mat-card[class='summary-left-card mat-card']"
    CSS_RISK_VULN_SUMMARY_CARD_SEVERITY_TABLE = "div[class='content-right table-severity']"
    CSS_RISKS_VULN_SUMMARY_CARD_SEVERITY_TEXT = ".zing-dashboard-link"
    CSS_RISKS_VULN_SUMMARY_CARD_VULNERABILITY_COUNT  = "td[class*='zing-nounderscore-link']"
    CSS_RISKS_VULN_SUMMARY_CARD_VULNERABILITY_NUM_TOTAL = "div[class='number zt_total_vuln_number']"
    CSS_RISKS_VULN_SUMMARY_CARD_VULNERABILITY_NUM_CONFIRMED = "div[class='zt_confirmed_vuln_number']"

    CSS_RISKS_VULN_STAT_NUMBER = "div[class='stat-number ng-binding']"
    CSS_RISKS_VULN_STAT_NAME = "div[class='stat-name']"
    CSS_RISKS_VULN_STAT_POTENTIAL = "div[class='stat-potential ng-scope layout-align-center-center layout-row']"
    CSS_RISKS_VULN_STAT_CONFIRMED = ".zt_confirmed_vuln_number.confirmed_vuln_number"
    CSS_RISKS_VULN_SUMMARY = "md-card[class='vulnerability-summary _md']"
    CSS_RISKS_VULN_TOP_PROFILE_TEXT = ["Top Vulnerable Profiles by Severity", \
            "arrow_drop_down", "Critical", "Low"]

    CSS_RISKS_VULN_TABLE = "mat-card[class='table-card mat-card']"
    CSS_RISKS_VULN_TABLE_HEADER = ["search","file_download", "filter_list", "view_column","Severity", "CVSS", "Vulnerability", "Confirmed", "Confirmed Instances", 
            "Potential Instances", "Vulnerable Profiles"]

    CSS_VULN_STAT_BLOCK = "mat-card[class='summary-left-card mat-card']"
    CSS_VULN_FILTER_CHIP = ".tag.mat-chip-color-low-blue"


class RisksRecallsLoc(object):
    """ Element locators for Risks Recalls Page """
    # Menu to access Risks => Recalls page
    CSS_RISKS_RECALL = "ul[data-menu='risk'] li:nth-of-type(2)"
    CSS_RISKS_RECALL_TITLE = "div[class='page-title-badget ng-star-inserted']"
    CSS_RISKS_RECALL_TABLE = "md-card[class='zingTable ng-isolate-scope _md zing-table-recallList flex']"
    CSS_RISKS_RECALL_TABLE_TITLE = "mat-card-content[class='mat-card-content']"
    CSS_RISKS_RECALL_TABLE_HEADER = "div[class='ag-header-container']"
    CSS_RISKS_RECALL_TABLE_HEADER_TEXT = ["Recall", "Status", "Affected", "Recalled Devices", "Recalled Profiles"]
