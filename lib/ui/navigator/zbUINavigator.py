from enum import Enum
from ui.login.zbUILoginCore import Login
from locator.navigator import NavMenuLoc
from locator.navigator import ToolBarLoc
from ui.zbUIShared import checkElement
import logging
import re, time, pdb
from urllib.parse import urlparse

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ZOOM_DIRECTION(Enum):
    IN = 'zoom_in',
    OUT = 'zoom_out'


class Navigator():

    def __init__(self, **kwargs):
        self.params = kwargs
        self.selenium = Login(**kwargs).login()
        self.baseurl = kwargs["url"]+'/'

    def verifyNavigatorMenu(self):
        kwargs = {}
        css_list = [NavMenuLoc.CSS_DASHBOARD,
                    NavMenuLoc.CSS_DEVICES,
                    NavMenuLoc.CSS_ALERTS,
                    NavMenuLoc.CSS_RISKS,
                    NavMenuLoc.CSS_REPORTS,
                    NavMenuLoc.CSS_SERVERS,
                    NavMenuLoc.CSS_PROTOCOLS,
                    NavMenuLoc.CSS_APPLICATIONS,
                    NavMenuLoc.CSS_NETWORK,
                    NavMenuLoc.CSS_PROFILES,
                    NavMenuLoc.CSS_POLICIES,
                    NavMenuLoc.CSS_INTEGRATIONS,
                    NavMenuLoc.CSS_ADMINISTRATION,
                    NavMenuLoc.CSS_LOGO,
                    ToolBarLoc.CSS_SEARCH_ICON,
                    ToolBarLoc.CSS_SEARCH_BAR,
                    ToolBarLoc.CSS_FEEDBACK_BUTTON,
                    ToolBarLoc.CSS_HELP_ICON,
                    ToolBarLoc.CSS_AVATAR,
                    ToolBarLoc.CSS_FILTER_SITE,
                    ToolBarLoc.CSS_FILTER_MONITORED,
                    ToolBarLoc.CSS_FILTER_DEVICES,
                    ToolBarLoc.CSS_FILTER_DURATION,
        ]
        for css in css_list:
            kwargs["selector"] = css
            ele = self.selenium.findSingleCSSNoHover(selector=css, timeout=0)
            checkElement(ele, css)
        return True

    def close(self):
        if self.selenium:
            self.selenium.quit()
