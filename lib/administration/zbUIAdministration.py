from ui.login.zbUILoginCore import Login
from urllib.parse import urlparse
from ui.zbUIShared import waitLoadProgressDone, clickAndVerifyColumns, verifyTableEntries, verify_inventory_top
from locator.navigator import UISharedLoc
from locator.administration import AdministrationLoc
import selenium.common.exceptions as selexcept

import time

import logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class Administration:
    def __init__(self, **kwargs):
        self.params = kwargs
        if "selenium" in kwargs:
            self.selenium = kwargs["selenium"]
        else:
            self.selenium = Login(**kwargs).login()
        href = "/guardian/administration/"
        self.href_mapping = {
            "User Accounts": href + "tenantaccounts?",
            "Notifications": href + "notifications?",
            "Sites and Inspectors": href + "inspectors?",
            "Active Probing": href + "snmpsettings?",
            "Report Configurations": href + "configlist?",
            "Audit Logs": href + "auditlogs?",
            "License": href + "license?"
        }

    def _go_to_administration_page_by(self, pageref):
        href = self.href_mapping[pageref]
        if href in self.selenium.getCurrentURL():
            logger.info('Have reached the page in ' + pageref)
            return True

        # hover on the administration menu item
        admin_element = self.selenium.findSingleCSS(selector=AdministrationLoc.CSS_NAV_ADMINISTRATION)
        if not admin_element:
            logger.error('Unable to find administration in navbar')
            return False
        self.selenium.hoverElement(admin_element)

        css_selector = AdministrationLoc.CSS_CLICK_TO_CHOOSE.format(href)
        if not self.selenium.click(selector=css_selector):
            logger.error('Unable to enter ' + pageref)
            return False

        # wait for the loading of the page to be finished.
        waitLoadProgressDone(self.selenium)
        logger.info('Reached the page of ' + pageref)
        return True

    def close(self):
        if self.selenium:
            self.selenium.quit()

