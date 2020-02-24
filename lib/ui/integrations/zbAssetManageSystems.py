from ui.integrations.zbUIIntegration import Integration
from locator.integration import IntegrationAsset

from common.zbConfig import defaultEnv
import logging
import time

env = defaultEnv()
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class AssetManagementSystems(Integration):
    def __init__(self, **kwargs):
        logger.info('Entering testing of Asset Management Systems Page...')
        super(AssetManagementSystems, self).__init__(**kwargs)

    def check_asset_configuration(self):
        self._go_to_integration_page_by("Asset Management Systems")
        logger.info("Start the checking for asset configuration")
        for vendor in IntegrationAsset.asset_list:
            if not globals()["config_" + vendor](self.selenium):
                return False
        return True

    def check_servicenow_integration(self):
        self._go_to_integration_page_by("Asset Management Systems")
        logger.info("Start the checking for ServiceNow Integration")

        servicenowedit = self.selenium.findSingleCSS(selector=IntegrationAsset.CSS_SERVICENOW_EDIT, timeout=3)
        if not servicenowedit:
            return False
        servicenowedit.click()
        time.sleep(2)

        _click_clear_send_keys(self.selenium, IntegrationAsset.CSS_SERVICENOW_URL, env["servicenow_url"])
        _click_clear_send_keys(self.selenium, IntegrationAsset.CSS_SERVICENOW_USERNAME, env["servicenow_uname"])
        _click_clear_send_keys(self.selenium, IntegrationAsset.CSS_SERVICENOW_PWD, env["servicenow_pwd"])
        _click_clear_send_keys(self.selenium, IntegrationAsset.CSS_SERVICENOW_TABLE, env["servicenow_table"])
        _click_clear_send_keys(self.selenium, IntegrationAsset.CSS_SERVICENOW_CATEGORY, env['servicenow_category'])
        _click_clear_send_keys(self.selenium, IntegrationAsset.CSS_SERVICENOW_PROFILE, env["servicenow_profile"])

        # Submit setting
        self.selenium.click(selector=IntegrationAsset.CSS_SERVICENOW_SAVE)
        self.selenium.click(selector=IntegrationAsset.CSS_DISABLE_ASSET_SWITCH, timeout=5)
        return True


def _click_clear_send_keys(browserobj, css_selector, key_text):
    element = browserobj.findSingleCSS(selector=css_selector)
    element.click()
    element.clear()
    element.send_keys(key_text)
    time.sleep(1)


def _enter_config_page(browserobj, vendor):
    if not browserobj.findSingleCSS(selector=IntegrationAsset.CSS_ASSET_CONFIGURATION, timeout=5):
        logger.error("Fail to load the asset configuration section!")
        return False
    vendor_icon_css = IntegrationAsset.CSS_VENDOR_ICON + vendor
    browserobj.click(selector=vendor_icon_css)
    if not browserobj.findSingleCSS(selector=IntegrationAsset.CSS_EDIT_ASSET_DETAIL_TITLE, timeout=10):
        logger.error("Unable to reach the vendor detail configuration page")
        return False
    logger.info("Vendor detail page of {} is successfully reached.".format(vendor))
    return True


def _submit_and_confirm_vendor_config(browserobj, vendor):
    # Submit setting
    browserobj.click(selector=IntegrationAsset.CSS_ASSET_SAVE_BUTTON)
    browserobj.click(selector=IntegrationAsset.CSS_CONFIRM_TO_SAVE, timeout=2)

    # confirm setting
    confirm_page = browserobj.findSingleCSS(selector=IntegrationAsset.CSS_ASSET_CONFIRM, timeout=10)
    if not confirm_page:
        logger.error("Fail to reach the confirm page of vendor")
        return False

    if not confirm_page.find_element_by_css_selector(IntegrationAsset.CSS_VENDOR_CONFIRM.format(vendor)):
        logger.error("Fail to find the updated Asset Management Vendor")
        return False

    logger.info("Configuration on {} successfully pass the check".format(vendor))
    browserobj.click(selector=IntegrationAsset.CSS_DISABLE_ASSET_SWITCH, timeout=5)
    return True


def config_aims(browserobj):
    if not _enter_config_page(browserobj, "aims"):
        return False
    _click_clear_send_keys(browserobj, IntegrationAsset.CSS_ASSET_AIMS_HOST, env["aimsServer"])
    _click_clear_send_keys(browserobj, IntegrationAsset.CSS_ASSET_AIMS_TOKEN, env["aimsServer"])

    forward_inspector = browserobj.findSingleCSS(selector=".inspector-select")
    forward_inspector.click()
    md_options = browserobj.findMultiCSS(selector='[aria-hidden="false"] [category="AIMS Integration"]',
                                         waittype="visibility")
    md_options[0].click()
    time.sleep(2)

    data_import_freq = browserobj.findSingleCSS(selector='[name="frequency"]')
    data_import_freq.click()
    md_options = browserobj.findMultiCSS(selector='[aria-hidden="false"] [category="AIMS Integration"]',
                                         waittype="visibility")
    md_options[0].click()
    time.sleep(2)

    # confirm setting
    assert _submit_and_confirm_vendor_config(browserobj, "aims")
    return True


def config_connectiv(browserobj):
    if not _enter_config_page(browserobj, "connectiv"):
        return False

    _click_clear_send_keys(browserobj, IntegrationAsset.CSS_CONNECTIV_UNAME, env["connectiv_uname"])
    _click_clear_send_keys(browserobj, IntegrationAsset.CSS_CONNECTIV_PWD, env["connectiv_pwd"])
    _click_clear_send_keys(browserobj, IntegrationAsset.CSS_CONNECTIV_CLIENT_ID, env["connectiv_client_id"])
    _click_clear_send_keys(browserobj, IntegrationAsset.CSS_CONNECTIV_CLIENT_SECRET, env["connectiv_client_secret"])
    _click_clear_send_keys(browserobj, IntegrationAsset.CSS_CONNECTIV_URL, env["connectiv_client_url"])

    # confirm setting
    assert _submit_and_confirm_vendor_config(browserobj, "connectiv")
    return True


def config_nuvolo(browserobj):
    if not _enter_config_page(browserobj, "nuvolo"):
        return False

    _click_clear_send_keys(browserobj, IntegrationAsset.CSS_NUVOLO_UNAME, env["nuvolo_uname"])
    _click_clear_send_keys(browserobj, IntegrationAsset.CSS_NUVOLO_PWD, env["nuvolo_pwd"])
    _click_clear_send_keys(browserobj, IntegrationAsset.CSS_NUVOLO_SOURCE_KEY, env["nuvolo_key"])
    _click_clear_send_keys(browserobj, IntegrationAsset.CSS_NUVOLO_URL, env["nuvolo_url"])

    # confirm setting
    assert _submit_and_confirm_vendor_config(browserobj, "nuvolo")
    return True








