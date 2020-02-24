from ui.administration.zbUIAdministration import Administration
from ui.zbUIShared import waitLoadProgressDone, clickAndVerifyColumns, verifyTableEntries
from locator.administration import AdministrationLoc
import os
import selenium.common.exceptions as selexcept

import logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class License(Administration):
    def __init__(self, **kwargs):
        logger.info('Entering testing of License Page...')
        super(License, self).__init__(**kwargs)

    def _click_to_choose_tab(self, str):
        active_tab = self.selenium.findSingleCSS(selector=AdministrationLoc.CSS_LICENSE_ACTIVE_TAB)
        if str in active_tab.text:
            return True

        tabs = self.selenium.findMultiCSS(selector=AdministrationLoc.CSS_ALL_TABS)
        if not tabs:
            logger.error('Unable to find any tabs')
            return False
        for tab in tabs:
            if str in tab.text:
                try:
                    tab.click()
                except selexcept.ElementClickInterceptedException as e:
                    logger.error('Possible Failure to click the tab: {}'.format(str(e)))
                waitLoadProgressDone(self.selenium)
                return True
        logger.error('Specified Tab to click not found')
        return False

    def check_license_page(self):
        if not self._go_to_administration_page_by("License"):
            logger.error('Unable to reach the License Page')
            return False

        assert self._click_to_choose_tab('License')

        page_title = self.selenium.findSingleCSS(selector=AdministrationLoc.CSS_PAGE_HEADER)
        if not page_title or "License" not in page_title.text:
            logger.error('Wrong page title of License')
            return False

        assert self._check_title('License')

        headers = self.selenium.findMultiCSS(selector=AdministrationLoc.CSS_LICENSE_HEADERS)

        if not headers:
            if os.environ['NODE_ENV'] == 'testing':
                logger.info('testing environment has no license, pass')
                return True
            else:
                logger.error('License Table Not Found')
                return False

        header_collection = []
        for header in headers:
            header_collection.append(header.text)
        if os.environ['NODE_ENV'] == "testing":
            logger.info('No license in testing environment, pass')
            return True

        for column_name in AdministrationLoc.license_column_list:
            if column_name not in header_collection:
                logger.error('Column of {} is not shown!'.format(column_name))
                return False
        logger.info('License Tab Pass the check')
        return True

    def check_EULA_page(self):
        if not self._go_to_administration_page_by("License"):
            logger.error('Unable to reach the License Log Page')
            return False

        assert self._click_to_choose_tab('EULA')
        assert self._check_title('End User License Agreement')
        assert self.selenium.findMultiCSS(selector=AdministrationLoc.CSS_LICENSE_PAGE), "Page content not found"
        return True

    def check_private_policy_page(self):
        if not self._go_to_administration_page_by("License"):
            logger.error('Unable to reach the License Log Page')
            return False

        assert self._click_to_choose_tab("Privacy Policy")
        assert self._check_title("Privacy Policy")
        assert self.selenium.findSingleCSS(selector=AdministrationLoc.CSS_LICENSE_PAGE_CONTENT), "Page Content not found"
        return True

    def _check_title(self, title):
        card_title = self.selenium.findSingleCSS(selector=AdministrationLoc.CSS_LICENSE_CARD_TITLE)
        if not card_title or title not in card_title.text:
            logger.error('Wrong table title of {}'.format(title))
            return False
        return True








