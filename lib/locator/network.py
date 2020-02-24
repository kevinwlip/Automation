from selenium.webdriver.common.by import By
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class NetworkSelectors:
    CSS_PAGE_TITLE = ".page-title-badget.ng-star-inserted"
    CSS_BLOCK_TITLE = ".zing-dialog-header"
    CSS_SUBNET_NAME = ".subnet-name"
    CSS_NETWORK_NAV = ".ng-star-inserted.nav-item[data-title='Network']"
    CSS_NETWORK_ACTIVE = ".zing-secondary-title.ng-scope"
    CSS_BULK_ELEMENTS = {
    ".zing-secondary-title",
    ".bubble-header",
    "[md-ink-ripple-checkbox='']",
    "[ng-mousedown='subnetBCtrl.save()'][name='Save changes made']",
    ".table-downloader.material-icons",
    ".add-circle[category='subnet config']",
    ".sorted-header"
    }