import re, pdb
from ui.administration.zbUIAdministration import Administration
from ui.zbUIShared import checkFactory, clickSpecificTimerange
from locator.administration import AdministrationLoc
import selenium.common.exceptions as selexcept
import time

import logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

CSS_INSPECTOR_ADD_BUTTON = ".zt-add-icon"
CSS_INSPECTOR_DETAIL_BUTTON = ".zt-detail-actions"
CSS_INSPECTOR_DROPDOWN_ACTION_OPTION = ".zt-add-icon"
CSS_INSPECTOR_DROPDOWN_CREATE_SITE = ".zt-create-site-icon"
CSS_INSPECTOR_EXPAND_ALL = ".header-icons .zt-expand-icon"
CSS_INSPECTOR_COLLAPSE_ALL = ".header-icons .zt-collapse-icon"
CSS_INSPECTOR_INSPECTOR_NAME = ".zt-inspector-name"
CSS_INSPECTOR_SITE_NAME = ".zt-site-name"
CSS_INSPECTOR_INSPECTOR_NUMBER = ".zt-total-inspectors .total-sites"
CSS_INSPECTOR_SITE_NUMBER = ".zt-total-number-of-sites .total-sites"

CSS_CREATE_SITE_NAME = ".zt-create-site-name"
CSS_CREATE_SITE_ADDRESS = ".zt-create-site-address"
CSS_CREATE_SITE_SAVE_BUTTON = "zing-create-site .mat-button.primary"
CSS_SITE_CARD = ".zt-site-card"
CSS_CREATE_SITE_NAME_BAR = ".zt-create-site-name [matinput='']"
CSS_CREATE_SITE_ADDRESS_BAR = ".zt-create-site-address [matinput='']"

class SitesAndInspectors(Administration):
    def __init__(self, **kwargs):
        logger.info('Entering testing of My Inspectors...')
        super(SitesAndInspectors, self).__init__(**kwargs)
        self.check_factory = checkFactory(self.selenium)


    def regInspectors(self, **kwargs):
        if not self._go_to_administration_page_by("Sites and Inspectors"):
            logger.error('Unable to reach Sites and Inspectors page')
            return False
        logger.info("Sites and Inspectors Page has been reached")
        rcode = self.selenium.click(selector=CSS_INSPECTOR_EXPAND_ALL)

        rcode = self.selenium.findMultiCSS(selector=CSS_INSPECTOR_SITE_NAME)
        lenny = len(rcode)
        rcode = self.selenium.findSingleCSS(selector=CSS_INSPECTOR_SITE_NUMBER)

        if int(rcode.text) != int(lenny):
            logger.critical("Site number not matching up with number of sites")
            print(lenny)
            print(rcode.text)
            return False

        rcode = self.selenium.findMultiCSS(selector=CSS_INSPECTOR_INSPECTOR_NAME)
        lenny = len(rcode)
        rcode = self.selenium.findSingleCSS(selector=CSS_INSPECTOR_INSPECTOR_NUMBER)

        if int(rcode.text) != int(lenny):
            logger.critical("Inspector number not matching up with number of inspectors")
            return False

        self.selenium.click(selector=CSS_INSPECTOR_DROPDOWN_CREATE_SITE)
        time.sleep(1)
        rcode = self.selenium.findSingleCSS(selector=CSS_CREATE_SITE_NAME)
        rcode.click()
        rcode = self.selenium.findSingleCSS(selector=CSS_CREATE_SITE_NAME_BAR)
        rcode.send_keys("Ayy_Lmao_Test")

        rcode = self.selenium.findSingleCSS(selector=CSS_CREATE_SITE_ADDRESS)
        rcode.click()
        rcode = self.selenium.findSingleCSS(selector=CSS_CREATE_SITE_ADDRESS_BAR)
        rcode.send_keys("Test_Address_Please_Ignore")

        self.selenium.click(selector=CSS_CREATE_SITE_SAVE_BUTTON)
        tempy = ''
        rcode = self.selenium.findMultiCSS(selector=CSS_SITE_CARD)
        for r in rcode:
            print(r.text)
            print("=======")
        for r in rcode:
            if "Ayy_Lmao_Test" in r.text:
                tempy = r

        rcode = self.selenium.findSingleCSS(browserobj=tempy,selector=CSS_INSPECTOR_DROPDOWN_ACTION_OPTION)
        rcode.click()
        rcode = self.selenium.findMultiCSS(selector=".mat-menu-item")
        for rc in rcode:
            if "Edit Site" in rc.text:
                time.sleep(1)
                rc.click()
                break

        time.sleep(1)
        rcode = self.selenium.findSingleCSS(selector=CSS_CREATE_SITE_NAME)
        rcode.click()
        time.sleep(1)
        rcode = self.selenium.findSingleCSS(selector=CSS_CREATE_SITE_NAME_BAR)
        rcode.send_keys("_Altered")

        rcode = self.selenium.findSingleCSS(selector=CSS_CREATE_SITE_ADDRESS)
        rcode.click()
        rcode = self.selenium.findSingleCSS(selector=CSS_CREATE_SITE_ADDRESS_BAR)
        rcode.send_keys("_Ayy_Lmao")

        self.selenium.click(selector=CSS_CREATE_SITE_SAVE_BUTTON)
        izzet = False
        rcode = self.selenium.findMultiCSS(selector=CSS_SITE_CARD)
        for r in rcode:
            if "Ayy_Lmao_Test_Altered" in r.text:
                izzet = True
        if not izzet:
            logger.critical("Edit site test has failed")
            return False

        tempy = ''
        rcode = self.selenium.findMultiCSS(selector=CSS_SITE_CARD)
        for r in rcode:
            if "Ayy_Lmao_Test_Altered" in r.text:
                tempy = r

        rcode = self.selenium.findSingleCSS(browserobj=tempy,selector=CSS_INSPECTOR_DROPDOWN_ACTION_OPTION)
        rcode.click()
        time.sleep(1)
        rcode = self.selenium.findMultiCSS(selector=".mat-menu-item")
        for rc in rcode:
            if "Delete Site" in rc.text:
                rc.click()
                break
        time.sleep(1)
        self.selenium.click(selector=".zt-delete-site .mat-button")
        izzet = True
        rcode = self.selenium.findMultiCSS(selector=CSS_SITE_CARD)
        for r in rcode:
            if "Ayy_Lmao_Test_Altered" in r.text:
                izzet = False
        if not izzet:
            logger.critical("Delete site test has failed")
            return False

        return True

    def _check_overview_card(self):
        """
        This internal function is only used within this class. It checks ui elements in the overview section,
        and return the numbers of sites/connected/disconnected inspectors.
        :return: a dict to record the numbers of sites & connected & disconnected inspectors.
        """
        self.check_factory.add_to_checklist(css=AdministrationLoc.CSS_PAGE_HEADER,
                                            element_name="Page Title",
                                            text="Sites And Inspectors") \
            .add_to_checklist(css=AdministrationLoc.CSS_INSPECTOR_SITE_OVERVIEW,
                              element_name="overview section of inspectors and sites") \
            .add_to_checklist(css=AdministrationLoc.CSS_TOTAL_SITES_NUM,
                              element_name="Total Number of sites") \
            .add_to_checklist(css=AdministrationLoc.CSS_TOTAL_SITES_TITLE,
                              element_name="Sites",
                              text="Sites") \
            .add_to_checklist(css=AdministrationLoc.CSS_TOTAL_INSPECTORS_NUM,
                              element_name="Total number of inspectors") \
            .add_to_checklist(css=AdministrationLoc.CSS_TOTAL_INSPECTORS_TITLE,
                              element_name="Inspectors",
                              text="Inspectors") \
            .add_to_checklist(css=AdministrationLoc.CSS_TOTAL_CONNECTED_INSPECT_NUM,
                              element_name="Connected Inspector Number") \
            .add_to_checklist(css=AdministrationLoc.CSS_TOTAL_CONNECTED_INSPECT_TITLE,
                              element_name="Connected Inspectors",
                              text="cloud\nConnected") \
            .add_to_checklist(css=AdministrationLoc.CSS_TOTAL_DISCONNECTED_INSPECT_NUM,
                              element_name="Disconnected Inspector Number") \
            .add_to_checklist(css=AdministrationLoc.CSS_TOTAL_DISCONNECTED_INSPECT_TITLE,
                              element_name="Disconnected Inspectors",
                              text="cloud_off\nDisconnected") \
            .add_to_checklist(css=AdministrationLoc.CSS_CLOUD_TRAFFIC_SIZE,
                              element_name="Total Amount of Zingcloud Traffic") \
            .add_to_checklist(css=AdministrationLoc.CSS_CLOUD_TRAFFIC_TITLE,
                              element_name="Zingbox Cloud Traffic",
                              text="Zingbox Cloud Traffic") \
            .add_to_checklist(css=AdministrationLoc.CSS_ANALYZED_TRAFFIC_SIZE,
                              element_name="Total Amount of Analyzed Traffic") \
            .add_to_checklist(css=AdministrationLoc.CSS_ANALYZED_TRAFFIC_TITLE,
                              element_name="Analyzed Traffic",
                              text="Analyzed Traffic")
        if not self.check_factory.check_all():
            logger.error("Fail to pass the check of Overview section")
            return False
        self.check_factory.clear_all()

        result = dict()
        try:
            result["site_num"] = int(
                self.selenium.findSingleCSS(
                    selector=AdministrationLoc.CSS_TOTAL_SITES_NUM
                ).text
            )
            result["conn_insp_num"] = int(
                self.selenium.findSingleCSS(
                    selector=AdministrationLoc.CSS_TOTAL_CONNECTED_INSPECT_NUM
                ).text
            )
            result["disconn_insp_num"] = int(
                self.selenium.findSingleCSS(
                    selector=AdministrationLoc.CSS_TOTAL_DISCONNECTED_INSPECT_NUM
                ).text
            )
        except ValueError as e:
            logger.error(str(e))
            return False
        return result

    def _check_sites_top_bar(self):
        """
        This function is used internally. It checks the ui element on top bar above the site list, and return the number
        of sites shown at the title of the site list.
        """

        self.check_factory.add_to_checklist(css=AdministrationLoc.CSS_SITE_ITEM,
                                            element_name="Sites Title",
                                            text="Sites") \
            .add_to_checklist(css=AdministrationLoc.CSS_SITE_ITEM_NUMBER,
                              element_name="Sites Number") \
            .add_to_checklist(css=AdministrationLoc.CSS_DOWNLOAD_INSPECTOR_ICON,
                              element_name="Icon to Download Inspector Info") \
            .add_to_checklist(css=AdministrationLoc.CSS_ADD_INSPECTOR_ICON,
                              element_name="Icon to Add Inspector Info")

        if not self.check_factory.check_all():
            logger.error('Top Bar above Sites List does not pass the check')
            return False
        self.check_factory.clear_all()

        try:
            site_num = int(self.selenium.findSingleCSS(selector=AdministrationLoc.CSS_SITE_NUMBER_ABOVE_TABLE).text)
        except ValueError as e:
            logger.error(str(e))
            return False
        return site_num

    def _check_inspector_section(self, inspector_section):
        inspector_check_factory = checkFactory(self.selenium, check_scope=inspector_section)
        inspector_check_factory.add_to_checklist(css=AdministrationLoc.CSS_INSPECTOR_CLOUD_ICON,
                                                 element_name="cloud icon") \
            .add_to_checklist(css=AdministrationLoc.CSS_INSPECTOR_COUNT,
                              element_name="inspector count") \
            .add_to_checklist(css=AdministrationLoc.CSS_INSPECTOR_NAME,
                              element_name="inspector name") \
            .add_to_checklist(css=AdministrationLoc.CSS_INSPECTOR_STATUS,
                              element_name="inspector status") \
            .add_to_checklist(css=AdministrationLoc.CSS_INSPECTOR_REFRESH_ICON,
                              element_name="inspector refresh button") \
            .add_to_checklist(css=AdministrationLoc.CSS_INSPECTOR_MORE_ICON,
                              element_name="inspector more icon") \
            .add_to_checklist(css=AdministrationLoc.CSS_INSPECTOR_SUMMARY,
                              element_name="inspector summary")

        if not inspector_check_factory.check_all():
            return False
        inspector_check_factory.clear_all()
        logger.info("All content on this inspector section are loaded")
        return True

    def _check_site_section(self, site_section):
        """
        This function will check the ui elements on a single site section in the site aggregation list.
        :param site_section: the ui element of the site section to be checked.
        :return: A dict contains the number of connected inspectors and disconnected inspectors.
         False if there are ui elements missing.
        """
        site_check_factory = checkFactory(self.selenium, check_scope=site_section)
        site_check_factory.add_to_checklist(css=AdministrationLoc.CSS_SITE_CONNECTED_STATUS,
                                            element_name="Connected Status of Sites",
                                            text="cloud") \
            .add_to_checklist(css=AdministrationLoc.CSS_SITE_NAME,
                              element_name="Name of Site") \
            .add_to_checklist(css=AdministrationLoc.CSS_SITE_INSPECTOR_NUM,
                              element_name="Number of connected inspectors") \
            .add_to_checklist(css=AdministrationLoc.CSS_SITE_MONITORED_DEVICES,
                              element_name="Number of monitored devices") \
            .add_to_checklist(css=AdministrationLoc.CSS_SITE_DISCOVERED_DEVICES,
                              element_name="Number of discovered devices") \
            .add_to_checklist(css=AdministrationLoc.CSS_SITE_RISK_SCORE,
                              element_name="Risk Score") \
            .add_to_checklist(css=AdministrationLoc.CSS_SITE_SUBNET,
                              element_name="Subnets") \
            .add_to_checklist(css=AdministrationLoc.CSS_SITE_TRAFFIC,
                              element_name="Analyzed Traffic") \
            .add_to_checklist(css=AdministrationLoc.CSS_SITE_SHARE_ICON,
                              element_name="share icon",
                              text="more_horiz") \
            .add_to_checklist(css=AdministrationLoc.CSS_SITE_EXPAND_ICON,
                              element_name="expand icon",
                              text="expand_more")

        if not site_check_factory.check_all():
            logger.error("Cannot find all elements in the site section")
            return False
        site_check_factory.clear_all()

        # get the data for insp_info
        insp_info = dict()
        disconn_insp_num = 0
        conn_insp_num = 0
        try:
            insp_info_section = self.selenium.findSingleCSS(
                selector=AdministrationLoc.CSS_SITE_INSPECTOR_NUM,
                browserobj=site_section)
            insp_info_text = self.selenium.findSingleCSS(
                selector=AdministrationLoc.CSS_SITE_INSPECTOR_DISCONNECTED_NUM,
                browserobj=insp_info_section)
            if insp_info_text:
                insp_info_text = insp_info_text.text
                insp_info_text = insp_info_text.split(' ')
                disconn_insp_num = int(insp_info_text[0].strip())
                insp_num = int(insp_info_text[2].strip())
                conn_insp_num = insp_num - disconn_insp_num
        except Exception as e:
            logger.error(str(e))
            return False
        insp_info["disconn_insp_num"] = disconn_insp_num
        insp_info["conn_insp_num"] = conn_insp_num

        # Check each section of inspectors
        if conn_insp_num + disconn_insp_num > 0:
            expand_icon = self.selenium.findSingleCSS(selector=AdministrationLoc.CSS_SITE_EXPAND_ICON,
                                                      browserobj=site_section)
            expand_icon.click()
            time.sleep(2)
            inspector_sections = self.selenium.findMultiCSS(selector=AdministrationLoc.CSS_INSPECTOR_EXPANDED_DETAIL)
            assert len(inspector_sections) == conn_insp_num + disconn_insp_num

            for inspector_section in inspector_sections:
                if not self._check_inspector_section(inspector_section):
                    logger.error("Not showing complete inspector section!")
                    return False
            self.selenium.click(selector=AdministrationLoc.CSS_SITE_COLLAPSE_ICON)
            time.sleep(2)

        logger.info("The UI elements of this section is successfully verified!")
        return insp_info

    def check_sites_inventory(self):
        if not self._go_to_administration_page_by("Sites and Inspectors"):
            logger.error('Unable to reach Sites and Inspectors page')
            return False
        logger.info("Sites and Inspectors Page has been reached")
        clickSpecificTimerange(self.selenium, specific="1 Week")
        logger.info("Time range has been set to 1 Week!")

        # Wait for the loading of the page
        if not self.selenium.findSingleCSS(selector=AdministrationLoc.CSS_SITE_SECTION_CONTENT, timeout=20):
            logger.error("Page content is not loaded")
            return False
        logger.info("Page loading is finished")

        site_info = self._check_overview_card()
        if not site_info:
            return False
        logger.info("Overview card is verified")

        site_num = self._check_sites_top_bar()
        if not site_num:
            return False
        logger.info("Sites top bar is verified")

        # Check if the site number matches the site elements
        site_elements = self.selenium.findMultiCSSNoHover(selector=AdministrationLoc.CSS_SITE_SECTION_CONTENT)
        if site_num is not len(site_elements) or site_num is not site_info["site_num"]:
            logger.error(
                "There are {} sites shown in the overview card, \n"
                "but {} sites are shown in the title of sites list, \n"
                "and {} sites are found by looking up CSS selectors".format(
                    site_num,
                    len(site_elements),
                    site_info["site_num"]
                )
            )
            return False
        logger.info("Number of sites is verified")

        # verify content of every site section, as well as the inspector numbers.
        disc_insp = 0
        conn_insp = 0
        for site_section in site_elements:
            insp_info = self._check_site_section(site_section)
            if not insp_info:
                logger.error("The site content does not load completely")
                return False
            conn_insp += insp_info["conn_insp_num"]
            disc_insp += insp_info["disconn_insp_num"]
        logger.info("Content of every site section is verified")

        if conn_insp is not site_info["conn_insp_num"] or disc_insp is not site_info["disconn_insp_num"]:
            logger.error(
                "Connected Site Number shown on overview dashboard is {}; \n "
                "Connected Site Number found from site list is {}; \n"
                "Disconnected Site Number shown on overview dashboard is {}; \n"
                "Disconnected Site Number found from site list is {}".format(
                    site_info["conn_insp_num"],
                    conn_insp,
                    site_info["disconn_insp_num"],
                    disc_insp
                )
            )
            return False
        logger.info("Numbers of inspectors have passed the check")
        return True

