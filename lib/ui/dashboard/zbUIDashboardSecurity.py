from ui.login.zbUILoginCore import Login
from urllib.parse import urlparse
from ui.zbUIShared import waitLoadProgressDone, clickSpecificTimerange, waitSeriesGraphDone, verifyDataTimerange
from locator.dashboard import DashboardSecurityLoc
from selenium.webdriver.common.action_chains import ActionChains
import selenium.common.exceptions as selexcept

import time

import logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class DashBoardSecurity:
    def __init__(self, **kwargs):
        self.params = kwargs
        self.selenium = Login(**kwargs).login()

    def _go_to_security_page(self):
        if '/guardian/dashboard/security' in self.selenium.getCurrentURL():
            logger.info('Dashboard Security Page is reached')
            return True
        url = urlparse(self.params["url"])
        self.selenium.getURL(url.scheme + '://' + url.netloc + '/guardian/dashboard/security')
        waitLoadProgressDone(self.selenium)
        clickSpecificTimerange(self.selenium, specific="1 Month")
        security_tab = self.selenium.findSingleCSS(selector=DashboardSecurityLoc.CSS_ACTIVE)
        # Not sure if it is 'Security' Or 'security'
        if not security_tab or security_tab.text.lower() != 'security':
            logger.error('Unable to find Security Tab')
            return False
        logger.info('Dashboard Security Page is reached')
        return True

    def _show_more_cards(self):
        """
        This function will used to show all sites/categories/profiles
        :return:
        """
        show_more_btn = self.selenium.findSingleCSS(selector=DashboardSecurityLoc.CSS_SECURITY_SHOW_MORE_CARDS)

        if show_more_btn:
            show_more_btn.click()
            time.sleep(0.5)

        num_after_show_all = len(self.selenium.findMultiCSS(selector=DashboardSecurityLoc.CSS_CARDS_IN_GROUPING))
        return num_after_show_all

    def _find_card_section(self, card_title):
        """
        This function returns a webElement whose card title is consistent with the parameter
        :param card_title: specify the title of the card webElement to returned
        :return: webElement
        """
        cards_in_page = self.selenium.findMultiCSS(selector=DashboardSecurityLoc.CSS_CARD_SECTION)
        for card in cards_in_page:
            card_names = card.find_elements_by_class_name(DashboardSecurityLoc.CLASS_TITLE_A_IN_CARD)
            card_names.extend(card.find_elements_by_tag_name(DashboardSecurityLoc.CLASS_TITLE_B_IN_CARD))
            for card_name in card_names:
                if card_title in card_name.text:
                    if self.selenium.browser == 'firefox':
                        self.selenium.driver.execute_script("arguments[0].scrollIntoView(true);", card)
                    hover = ActionChains(self.selenium.driver).move_to_element(card)  # hovers first element instead
                    hover.perform()
                    return card
        return False

    def _click_to_choose_tab(self, tab_to_select):
        """
        this function is to choose active tab among sites, categories, profiles

        :return:
        """
        logger.info('Select Tab: ' + tab_to_select)
        tab_index = {
            'Sites': 1,
            'Categories': 2,
            'Profiles': 3
        }
        tab_index = tab_index[tab_to_select]
        self.selenium.click(selector=DashboardSecurityLoc.CSS_SELECT_SITES_PROFILES_CATEGORIES.format(tab_index))
        active_tab = self.selenium.findSingleCSS(selector=DashboardSecurityLoc.CSS_FIND_ACTIVE_TAB)
        if not active_tab or tab_to_select not in active_tab.text:
            logger.error('Fail to select ' + tab_to_select + ' Tab')
            return False
        waitLoadProgressDone(self.selenium)
        return True

    def _verify_num_all(self):
        logger.info('Verify whether total number on summary card '
                    'is equal to number of cards showing...')
        sum_card_nums = self.selenium.findMultiCSS(selector=DashboardSecurityLoc.CSS_SUM_CARD_IN_TAB)
        if not sum_card_nums:
            logger.error('Unable to find the numbers on the sum card')
            return False

        sum_val = sum_card_nums[0]
        sum_val = sum_val.text.strip('()')
        sum_val = int(sum_val)
        total_sum_val = self._show_more_cards()

        if sum_val != total_sum_val:
            logger.error('Numbers Not Match!')
            return False
        return True

    def _verify_tab_details(self, tab_type):
        """
        This function checks if every type of card has the expected elements.

        :param tab_type: Sites/Categories/Profiles
        :return:
        """
        card_list = self.selenium.findMultiCSS(selector=DashboardSecurityLoc.CSS_CARDS_IN_GROUPING)
        for enum, card in enumerate(card_list):
            if not card.find_element_by_class_name(DashboardSecurityLoc.CLASS_NAME_IN_TAB):
                logger.error('There is no card name on ' + str(enum) + ' ' + tab_type + ' card')
                return False
            if tab_type == 'Sites':
                if not card.find_element_by_class_name(DashboardSecurityLoc.CLASS_DEPLOY_STATUS_IN_TAB):
                    logger.error('There is no deploy-status on ' + str(enum) + ' Sites card')
                    return False
            if not card.find_element_by_class_name(DashboardSecurityLoc.CLASS_BUTTON_ROW_IN_TAB):
                logger.error('There is no button row on ' + str(enum) + ' ' + tab_type + ' card')
                return False
        return True

    def check_all_tabs_site_cate_prof(self):
        """
        check all three tabs of Sites, Categories and Profiles. Verify the card numbers
        and card details.

        :return:
        """
        if not self._go_to_security_page():
            logger.error('Unable to reach the security page')
            return False

        for tab in ['Sites', 'Categories', 'Profiles']:
            self._click_to_choose_tab(tab)
            logger.info('Start checking tab of ' + tab)

            # verify numbers
            if not self._verify_num_all():
                logger.error('Numbers in ' + tab + ' cards are not consistent')
                return False

            # verify card details
            if not self._verify_tab_details(tab):
                logger.error('Details for ' + tab + ' cards are not matched')
                return False
        return True

    def check_risk_assessment(self):
        if not self._go_to_security_page():
            logger.error('Unable to reach the security page')
            return False
        logger.info('Checking the card of Risk Assessment')

        # Obtain the risk_assessment card webElement
        risk_card = self._find_card_section('Risk Assessment')
        if not risk_card:
            logger.error('Unable to find Risk Assessment Card')
            return False

        # Check the gauge icon on the risk_assessment card
        if not risk_card.find_element_by_id(DashboardSecurityLoc.ID_GAUGE_ON_RISK_CARD):
            logger.error('Unable to find Risk Gauge')
            return False

        rows = risk_card.find_elements_by_class_name(DashboardSecurityLoc.CLASS_RISK_ROW_ON_RISK)
        cnt = 0
        for row in rows:
            if not row.find_element_by_class_name(DashboardSecurityLoc.CLASS_RISK_LEVEL_ICON_ON_RISK):
                logger.error('Unable to find risk level icons')
                return False

            risk_num = row.find_element_by_class_name(DashboardSecurityLoc.CLASS_RISK_NUM_ON_RISK)
            if not risk_num:
                logger.error('Unable to find risk numbers in this row')
                return False

            cnt = cnt + int(risk_num.text)

            if not row.find_element_by_class_name(DashboardSecurityLoc.CLASS_RISK_TEXT_DESCRIPTION):
                logger.error('Unable to find risk description in this row')
                return False
        try:
            risk_num_sum = risk_card.find_element_by_class_name(DashboardSecurityLoc.CLASS_TOTAL_NUMBER_RISK)
            risk_num_sum = int(risk_num_sum.text)
        except:
            logger.error('Unable to find total number of risky devices')
            return False

        if risk_num_sum != cnt:
            logger.error('Total devices is not the same as calculated')
            return False
        return True

    def check_network_summary(self):
        if not self._go_to_security_page():
            logger.error('Unable to reach the security page')
            return False
        logger.info('Checking the card of Network Summary')

        network_card = self._find_card_section('Network Summary')
        if not network_card:
            logger.error('Unable to find Network Summary Card')
            return False
        try:
            numerical_detail = network_card.find_element_by_class_name(DashboardSecurityLoc.CLASS_NUMERICAL_DETAIL_NETWORK)
            rows = numerical_detail.find_elements_by_class_name(DashboardSecurityLoc.CLASS_ROW_IN_TABLE)
            for row in rows:
                row.find_element_by_class_name(DashboardSecurityLoc.CLASS_COUNT_NETWORK)
                row.find_element_by_class_name(DashboardSecurityLoc.CLASS_ICON_NETWORK)
        except:
            logger.error('Unable to verify all details in Network Summary Card')
            return False
        return True

    def check_device_by(self):
        if not self._go_to_security_page():
            logger.error('Unable to reach the security page')
            return False
        logger.info('Checking the card of Devices')

        device_by_card = self._find_card_section('Devices by')
        if not device_by_card:
            logger.error('Unable to find Devices by Card')
            return False

        # check if 3 options available: Category/OS/VLAN
        for i in range(3):
            self.selenium.click(selector=DashboardSecurityLoc.CSS_SELECT_RANGE_DEVICE_BY)
            device_by_options = self.selenium.findMultiCSS(selector=DashboardSecurityLoc.CSS_SELECT_RANGE_OPTIONS_DEVICE_BY)
            device_by_options[i].click()

            # right top dots indicate active pages within this card
            dots_list = self.selenium.findMultiCSS(selector=DashboardSecurityLoc.CSS_DOTS_DEVICE_BY)
            active_dot = self.selenium.findSingleCSS(selector=DashboardSecurityLoc.CSS_DOT_ACTIVE_DEVICE_BY)
            if active_dot is not dots_list[0]:
                dots_list[0].click()
            waitLoadProgressDone(self.selenium)
            logger.info('Checking Device by ' + device_by_options[i].text)

            if not device_by_card.find_element_by_id(DashboardSecurityLoc.ID_DEVICE_PIE_CHART):
                logger.error('Pie chart is not found')
                return False

            if not device_by_card.find_element_by_class_name(DashboardSecurityLoc.CLASS_LAYOUT_COLUMN):
                logger.error('Table is not found')
                return False

            dots_list[1].click()
            time.sleep(0.5)

            if not device_by_card.find_element_by_class_name(DashboardSecurityLoc.CLASS_CATEGORY_LIST):
                logger.error('Table in detail is not found')
                return False
        return True

    def check_external_destinations(self):
        if not self._go_to_security_page():
            logger.error('Unable to reach the security page')
            return False
        logger.info('Checking the card of External Destinations')

        # Obtain the risk_assessment card webElement
        destinations_card = self._find_card_section('External Destinations')
        if not destinations_card:
            logger.error('Unable to find External Destinations Card')
            return False

        for i in range(3):
            self.selenium.click(selector=DashboardSecurityLoc.CSS_IN_OUT_BOUND_SELECT)
            dest_options = self.selenium.findMultiCSS(selector=DashboardSecurityLoc.CSS_DROPDOWN_OPTIONS)
            dest_options[i].click()
            waitLoadProgressDone(self.selenium)

            try:
                destinations_card.find_element_by_id(DashboardSecurityLoc.ID_GLOBAL_MAP)
            except selexcept.NoSuchAttributeException:
                logger.error('Unable to find the map in external destination card')
                return False
        return True

    def check_endpoint_protection(self):
        if not self._go_to_security_page():
            logger.error('Unable to reach the security page')
            return False
        logger.info('Checking the Endpoint Protection')

        # Obtain the risk_assessment card webElement
        ep_protection_card = self._find_card_section('Endpoint Protection')
        if not ep_protection_card:
            logger.error('Unable to find Endpoint Protection Card')
            return False

        try:
            ep_protection_card.find_element_by_class_name(DashboardSecurityLoc.CLASS_HIGH_CHARTS_GROUND)
            ep_protection_card.find_element_by_class_name(DashboardSecurityLoc.CLASS_ROW_IN_TABLE)
            ep_protection_card.find_element_by_class_name(DashboardSecurityLoc.CLASS_DOWNLOAD_ICON)
        except selexcept.NoSuchElementException:
            logger.error('Unable to verify details in Endpoint Protection Card')
            return False
        return True

    def check_device_management(self):
        if not self._go_to_security_page():
            logger.error('Unable to reach the security page')
            return False
        logger.info('Checking the Device Management Card')

        dev_manage_card = self._find_card_section('Device Management')
        if not dev_manage_card:
            logger.error('Unable to find Device Management Card')
            return False

        try:
            dev_manage_card.find_element_by_class_name(DashboardSecurityLoc.CLASS_HIGH_CHARTS_GROUND)
            dev_manage_card.find_element_by_class_name(DashboardSecurityLoc.CLASS_ROW_IN_TABLE)
        except selexcept.NoSuchElementException:
            logger.error('Unable to verify details in Device Management Card')
            return False
        return True

    def close(self):
        if self.selenium:
            self.selenium.quit()
















