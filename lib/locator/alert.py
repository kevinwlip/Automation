from selenium.webdriver.common.by import By
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class AlertListLocators(object):
    CSS_ALERT_INV_CARD_LIST = [
            ".alert-chart.ng-scope._md.layout-align-center-center.layout-row",
            "[ng-if='alertListCtrl.selectedAlertNumber']"
    ]
    CSS_EXPAND_ALERT = "[role='button'] .ng-binding[pwk-new-event='']"
    CSS_CLICK_ALERT = ".alert-row.layout-row.flex"
    CSS_ALERT_TITLE_NUMBER = ".title .ng-scope.ng-binding"
    CSS_IMPACTED_CATEGORY = ".alert-filter-input .alert-filter-input-autocomplete-impactedCategory .md-show-clear-button"
    """ Element locators for UI Dashboard """

class AlertDetailsLocators(object):
    CSS_ALERT_DETAIL_CARD_LIST=[
            ".mat-card .content",
            ".page-title-badget",
            ".ng-scope[ng-if='!alertListCtrl.loading']",
            ".alert-list-container .ng-scope[widget-type='alert-list']"
    ]

    CSS_ALERT_DETAIL_FEATURE_LIST=[
            ".mat-card .content",
            ".alert-head",
            ".impacted-device.ng-scope",
            ".device-detail-overall-ml.device-detail-overall._md",
            ".device-detail-overall-ml.device-detail-overall.secondary-card._md"
    ]

class VulnerabilityLocators(object):
    CSS_VULN_FEATURE_LIST=[
        "mat-card[class='summary-left-card mat-card']",
        ".content.zt-content .content-vuln-one",
        ".content.zt-content .table-severity",
        ".content.zt-content .content.vuln-dist-content",
        "zing-table[name='vulnerabilityList']"
    ]
    CSS_VULN_DETAIL_LIST= [
        "._md.summary-card",
        ".vulnerability-detail-page .table"
    ]
    CSS_VULN_DETAIL_CARD = "._md.summary-card"