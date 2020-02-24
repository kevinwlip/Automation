from ui.login.zbUILoginCore import Login
from ui.zbUIShared import waitLoadProgressDone
from locator.integration import IntegrationSelectors


import logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class Integration:
    def __init__(self, **kwargs):
        self.params = kwargs
        if "selenium" in kwargs:
            self.selenium = kwargs["selenium"]
        else:
            self.selenium = Login(**kwargs).login()
        href = "/guardian/integrations/"
        self.href_mapping = {
            "All": href + "all?",
            "Asset Management Systems": href + "assetmanagement?",
            "SIEM": href + "siemintegration?",
            "Network Access Control (NAC)": href + "networkaccesscontrol?",
            "Vulnerability Scanning": href + "vulnerabilityIntegration?",
            "Firewalls": href + "firewallintegration?",
            "Security Automation and Orchestration": href + "phantomintegration?",
            "Network Management": href + "primesintegration?",
            "Wireless Network Controllers": href + "wlanIntegration?",
            "Managed Security Services": href + "symantecIntegration?"
        }

    def _go_to_integration_page_by(self, pageref):
        href = self.href_mapping[pageref]
        if href in self.selenium.getCurrentURL():
            logger.info('Have reached the page in ' + pageref)
            return True

        # hover on the Integrations menu item
        integration_element = self.selenium.findSingleCSS(selector=IntegrationSelectors.CSS_INTEGRATION_NAV)
        if not integration_element:
            logger.error('Unable to find integration in nav bar')
            return False
        self.selenium.hoverElement(integration_element)

        css_selector = IntegrationSelectors.CSS_CLICK_TO_CHOOSE.format(href)
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

