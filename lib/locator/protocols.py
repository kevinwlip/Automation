
from selenium.webdriver.common.by import By
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ProtocolPage:
    chklist = ["Profiles","Number of Devices","Sessions","Protocol","Data Usage"]
    CSS_PROTOCOLS_NAV = "[data-title='Protocols']"
    CSS_GRAPH_BAR = ".highcharts-point"
    CSS_TOP_BAR = ".table-top-container .filter-bar"
    CSS_TABLE_HEADER = ".zt-table-header .customHeaderLabel" #".ui-grid-header-cell-label"
    CSS_TITLE = ".title-wrap .title"
    CSS_BULK_PROTOCOLS_LIST = {
        "zing-page-badget .filter-control .control[data-type='DURATION']", #".date",
        ".zt-search-icon", #".clickable.space-out[icon='search']",
        ".page-title-badget",
        "zing-protocols .table-card" #".zing-table-applications"
    }

class ProtocolDetail:
    CSS_DETAIL_SELECTOR = ".ui-grid-cell-contents.ng-scope [zing-tooltip-card='']"
    CSS_HEADER = ".page-title-badget.ng-star-inserted"
    CSS_BULK_CHECK = {
        ".body",
        ".date-range-wrap",
        "md-card._md.protocol-pie-chart-wrapper",
        ".protocol-detail-network-split._md",
        ".google-sankey-wrap"
    }