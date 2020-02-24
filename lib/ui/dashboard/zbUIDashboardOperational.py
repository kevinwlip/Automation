from ui.login.zbUILoginCore import Login
from urllib.parse import urlparse
from ui.zbUIShared import waitLoadProgressDone, clickSpecificTimerange, waitSeriesGraphDone, verifyDataTimerange
from locator.dashboard import DashboardSecurityLoc, DashboardOperationalLoc
import selenium.common.exceptions as selexcept

import time

import logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class DashBoardOperational:
    def __init__(self, **kwargs):
        self.params = kwargs
        self.selenium = Login(**kwargs).login()

    def _go_to_operational_page(self):
        curr_url = self.selenium.getCurrentURL()
        # if already get to the operational page, just return
        if "/guardian/dashboard/operational" in curr_url:
            logger.info('Dashboard Operational Page is reached')
            return True
        # else, redirect to that page
        url = urlparse(self.params["url"])
        self.selenium.getURL(url.scheme + '://' + url.netloc + '/guardian/dashboard/operational')
        waitLoadProgressDone(self.selenium)
        clickSpecificTimerange(self.selenium, specific="1 Month")
        operation_tab = self.selenium.findSingleCSS(selector=DashboardSecurityLoc.CSS_ACTIVE)
        if not operation_tab or operation_tab.text.lower() != 'operational':
            logger.error('Unable to find Operational Tab')
            return False
        logger.info('Dashboard Operational Page is reached')
        return True

    def check_device_items(self):
        if not self._go_to_operational_page():
            logger.error('Unable to reach the Operational page')
            return False
        logger.info('Checking the category list of device items...')

        items = self.selenium.findMultiCSS(selector=DashboardOperationalLoc.CSS_CATEGORY_DEVICE_CARD)
        for item in items:
            names = item.find_elements_by_class_name('name')
            if not names or len(names) is 0:
                logger.error('Unable to find the category item name')
                return False
            numbers = item.find_elements_by_class_name('number')
            if not numbers or len(numbers) is 0:
                logger.info('Unable to find the category item number')
                return "Empty" in names[0].text
        logger.info('Category List of device items pass the check')
        return True

    def check_category_profile_card(self):
        if not self._go_to_operational_page():
            logger.error('Unable to reach the Operational page')
            return False
        logger.info('Checking the category profile card...')
        card = self.selenium.findSingleCSS(selector=DashboardOperationalLoc.CSS_CATEGORY_PROFILE_LIST, timeout=10)
        categories = card.find_elements_by_class_name('category')
        if not categories or len(categories) is 0:
            logger.error('the category section is not found')
            return False
        profile_sec = card.find_elements_by_class_name('profile')
        if not profile_sec or len(profile_sec) is 0:
            logger.error('the profile section is not found')
            return False

        profile_cards = profile_sec[0].find_elements_by_class_name('profile-card')
        if not profile_cards or len(profile_cards) is 0:
            return False
        logger.info('Category profile card has passed the test')
        return True

    def check_image_charts(self):
        if not self._go_to_operational_page():
            logger.error('Unable to reach the Operational page')
            return False
        logger.info('Checking the image chart section...')
        charts = self.selenium.findMultiCSS(selector=DashboardOperationalLoc.CSS_RECT_HIGHCHARTS)
        if not charts or len(charts) < 2:
            return False
        logger.info('image charts has been verified')
        return True

    def check_healthcare_device_usage(self):
        if not self._go_to_operational_page():
            logger.error('Unable to reach the operational page')
            return False
        logger.info('Checking the Device Usage Card...')

        device_usage_card = self.selenium.findSingleCSS(selector=DashboardOperationalLoc.CSS_HEALTH_USAGE_CARDS)
        if not device_usage_card:
            logger.error('Unable to find device usage card')
            return False
        try:
            device_usage_card.find_element_by_class_name('title')
        except selexcept.NoSuchElementException:
            logger.error('Not showing name of this card !')
            return False

        total_nums = device_usage_card.find_elements_by_class_name('total-number-wrapper')
        if not total_nums or len(total_nums) < 2:
            logger.error('Device usage card are not complete in numbers')
            return False

        toggle_devices = device_usage_card.find_elements_by_class_name('device-active-toggle')
        if not toggle_devices or len(toggle_devices) < 2:
            logger.error('Unable to find devices used / not used infomation')
            return False

        for dev in toggle_devices:
            try:
                dev.click()
            except selexcept.ElementClickInterceptedException as e:
                logger.error('Possible Failure to click toggle device: {}'.format(str(e)))
                pass
            time.sleep(1.5)
            if not self.selenium.findSingleCSS(selector=DashboardOperationalLoc.CSS_HEADER_ROW):
                logger.error('There is no table headers in current table')
                return False
        logger.info('Device Usage Card has passed the check')
        return True

    def check_image_patient_data(self):
        if not self._go_to_operational_page():
            logger.error('Unable to reach the operational page')
            return False
        logger.info('Checking the image and patient data...')

        image_patient_data = self.selenium.findSingleCSS(selector=DashboardOperationalLoc.CSS_HEALTHCARE_CATEGORY_DEVICE)
        if not image_patient_data:
            logger.error('Unable to find the Image & Patient Data Section')
            return False
        total_images = image_patient_data.find_elements_by_class_name('image-legend')
        if not total_images or len(total_images) == 0:
            logger.error('There is no number indicating total images')
            return False
        case_studies = image_patient_data.find_elements_by_class_name('patient-legend')
        if not case_studies or len(case_studies) == 0:
            logger.error('There is no number indicating case studies')
            return False
        avg_time_per_case = image_patient_data.find_elements_by_class_name('case-legend')
        if not avg_time_per_case or len(avg_time_per_case) == 0:
            logger.error('There is not number indicating the average scanning time')
            return False

        charts = image_patient_data.find_elements_by_class_name('highcharts-plot-background')
        if not charts or len(charts) == 0:
            logger.error('There is not chart in display')
            return False
        logger.info('Pass the check of image patient data!')
        return True

    def check_image_scan_analysis(self):
        if not self._go_to_operational_page():
            logger.error('Unable to reach the operational page')
            return False
        logger.info('Checking the image scan analysis...')

        image_scan_card = self.selenium.findSingleCSS(selector=DashboardOperationalLoc.CSS_HEALTH_BODY)
        if not image_scan_card:
            logging.error('Unable to find the image scan analysis page')
            return False

        body_stat_wrapper = image_scan_card.find_elements_by_class_name('body-stat-wrapper')
        if not body_stat_wrapper or len(body_stat_wrapper) == 0:
            logging.error('Unable to find the body status wrapper')
            return False

        body_diagram = body_stat_wrapper[0].find_elements_by_tag_name('svg')
        if not body_diagram or len(body_diagram) == 0:
            logging.error('Unable to show the body diagram')
            return False
        body_statistics = body_stat_wrapper[0].find_elements_by_class_name('body-stat')

        if not body_statistics or len(body_statistics) == 0:
            logging.error('Unable to show the body statistics')
            return False

        body_stat_images = image_scan_card.find_elements_by_class_name('svg-container')
        if not body_stat_images or len(body_stat_images) == 0:
            logging.error('Unable to show the graphic body data')
            return False

        category_labels = body_stat_images[0].find_elements_by_class_name('category-label')
        if not category_labels or len(category_labels) == 0:
            logging.error('Unable to show the category labels of the graphical data')
            return False
        logging.info('Pass all the checks for image scan analysis')
        return True

    def close(self):
        if self.selenium:
            self.selenium.quit()