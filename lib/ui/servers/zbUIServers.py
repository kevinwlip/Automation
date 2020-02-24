from ui.login.zbUILoginCore import Login
from urllib.parse import urlparse
from ui.zbUIShared import waitLoadProgressDone, clickAndVerifyColumns, verify_inventory_top
from locator.navigator import UISharedLoc
from locator.servers import ServersLoc
import selenium.common.exceptions as selexcept

import time

import logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class Servers:
    def __init__(self, **kwargs):
        self.params = kwargs
        self.selenium = Login(**kwargs).login()

    def _go_to_servers_inventory_page(self):
        curr_url = self.selenium.getCurrentURL()
        # if already get to the Servers page, just return
        if "/guardian/monitor/serverinventory" in curr_url:
            logger.info('Server Inventory Page is reached')
            return True
        # else, click the nav bar to go to the servers page
        self.selenium.click(selector=ServersLoc.CSS_SERVERS_ENTRYPOINT)
        waitLoadProgressDone(self.selenium)
        if "/guardian/monitor/serverinventory" not in self.selenium.getCurrentURL():
            logger.error('Unable to reach the servers page')
            return False
        logger.info('Servers Page is reached')
        return True

    def check_server_highcharts(self):
        if not self._go_to_servers_inventory_page():
            logger.error('Unable to reach the Servers page')
            return False
        logger.info('Checking the high charts of the servers...')
        if not self.selenium.findSingleCSS(selector=UISharedLoc.CSS_X_GRID_HIGHCHARTS) or not self.selenium.findSingleCSS(selector=UISharedLoc.CSS_Y_GRID_HIGHCHARTS):
            logger.error('Traffic Charts is not loaded!')
            return False
        return True

    def check_server_inventory(self):
        if not self._go_to_servers_inventory_page():
            logger.error('Unable to reach the Servers page')
            return False
        logger.info('Checking the inventory of the servers...')
        inventory_card = self.selenium.findSingleCSS(selector=ServersLoc.CSS_INVENTORY_CARD, waittype='visibility')
        if not inventory_card:
            logger.error('Server Inventory is not found')
            return False

        table_title = self.selenium.findSingleCSS(selector=UISharedLoc.CSS_TABLE_NAME, waittype='visibility')
        if not table_title or 'Server Inventory' not in table_title.text:
            logger.error('Title of the Inventory is not Server Inventory!')
            return False

        if not verify_inventory_top(self.selenium):
            logger.error('Inventory top tools are not verified')
            return False

        if not clickAndVerifyColumns(self.selenium, verify_list=ServersLoc.column_list):
            logger.info('Unable to click and verify all column headers')
            return False
        return True

    def close(self):
        if self.selenium:
            self.selenium.quit()


