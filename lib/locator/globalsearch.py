from selenium.webdriver.common.by import By
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class globalLocators:
    SearchResultOrder = ["Devices", "Alerts", "Vulnerabilities", "External Destinations"]
    CSS_SEARCH_RESULT_CARDS = ".global-search-result ._md"
    CSS_SEARCH_ITEM = ".search-item"
    CSS_CARD_TITLE = "[aria-hidden='false'] .search-header .search-type"
    CSS_VIEW_ALL = ".search-header .zing-link[role='button']"
    CSS_OTHER_SEARCH_ITEM = ".search-content .search-item"
