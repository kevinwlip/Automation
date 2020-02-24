from ui.administration.zbUIAdministration import Administration
from ui.zbUIShared import checkFactory
from locator.administration import AdministrationLoc
import selenium.common.exceptions as selexcept
from selenium.webdriver.common.keys import Keys
import pdb, time

import logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ActiveProbe(Administration):
    def __init__(self, **kwargs):
        logger.info('Entering testing of Active Probing...')
        super(ActiveProbe, self).__init__(**kwargs)

    def reg_active_probing(self):
        CheckSets = [
        ["Every hour", "Every 2 hours", "Every 4 hours", "Every day", "Every week"],
        ["Manual probing"],
        ["SNMPv2","SNMPv3"],
        ["No authentication and no privacy (noAuthNoPriv)", "Authentication and no privacy (AuthNoPriv)","Authentication and privacy (AuthPriv)"],
        ["MD5","SHA"]
        ]
        if not self._go_to_administration_page_by("Active Probing"):
            logger.error('Unable to reach Active Probing page')
            return False

        self.selenium.click(selector=AdministrationLoc.CSS_EDIT_PANEL_BUTTON)
        time.sleep(2)
        rcode = self.selenium.findMultiCSS(selector=AdministrationLoc.CSS_PROBE_DROPDOWN)
        for ind,rx in enumerate(rcode):
            meme = self.selenium.findMultiCSS(selector=AdministrationLoc.CSS_PROBE_DROPDOWN)
            try:
                meme[ind].click()
            except:
                meme[ind].find_element_by_xpath("..").click()
            rz = self.selenium.findMultiCSS(selector=AdministrationLoc.CSS_PROBE_DROP_OPTS)
            if  len(rz) != len(CheckSets[ind]):
                logger.critical("Some Dropdown items have missed")
                return False
            for r in rz:
               if r.text not in CheckSets[ind]:
                logger.critical(r.text)
                logger.critical("Dropdown menus have changed")
                return False
            rz[-1].click()
            try:
                rz[-1].click()
            except:
                pass

            #self.selenium.findSingleCSS(selector="body").send_keys(Keys.ESCAPE)

            if not rz:
                logger.critical("Dropdown menus are missing")
                return False

        return True



    def check_active_probing(self):
        if not self._go_to_administration_page_by("Active Probing"):
            logger.error('Unable to reach Active Probing page')
            return False

        check_factory = checkFactory(self.selenium)

        check_factory.add_to_checklist(css=AdministrationLoc.CSS_PAGE_HEADER,
                                       element_name="Page Title",
                                       text="Active Probing")\
                     .add_to_checklist(css=AdministrationLoc.CSS_PROBE_CARD_TITLE,
                                       element_name="Card title")\
                     .add_to_checklist(css=AdministrationLoc.CSS_EDIT_TOOLS,
                                       element_name="Edit Tools")\
                     .add_to_checklist(css=AdministrationLoc.CSS_DESCRIPTION_PROBING,
                                       element_name='Explanation for Probing')\
                     .add_to_checklist(css=AdministrationLoc.CSS_PROBING_TYPE,
                                       element_name="Probing Types")
        assert check_factory.check_all()

        property_titles = self.selenium.findMultiCSS(selector=AdministrationLoc.CSS_PROPERTY_TITLES)
        property_values = self.selenium.findMultiCSS(selector=AdministrationLoc.CSS_PROPERTY_VALUES)
        assert len(property_titles) == len(property_values), "Number of property titles and property values not match"
        return True



