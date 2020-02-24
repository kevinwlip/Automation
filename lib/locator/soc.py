from selenium.webdriver.common.by import By
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SOCSelectors:
    URL = "https://testing.zingbox.com/v1build/soc"
    CSS_SOC_BOLD_BAR = ".alert-total-wrap"
    CSS_SOC_RIGHT_BAR = ".data-total-wrap"
    CSS_SOC_CHART_CONTAINER = ".chart"
    CSS_SOC_CHART_BAR = ".highcharts-series .highcharts-point"
    CSS_SOC_ALERT_LIST = ".alert-list"
    CSS_SOC_MAP = ".map"

    CSS_PATH = "path"

    check_left_top = ["CRITICAL","WARNING","CAUTION","INFO"]
    check_right_top = ["NEW DEVICES", "TOTAL DEVICES", "VLANS", "APPS", "TOTAL DEVICE DATA", "ENCRYPTED", "CLOUD TRAFFIC"]
    check_chart = []
    check_inspectors = ["INSPECTOR", "OFFLINE", "NOT DEPLOYED", "LIVE"]
    check_alerts = ["Alerts"]
    check_map = ["External Destinations"]

