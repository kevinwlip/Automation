from ui.administration.zbUIAdministration import Administration
from ui.zbUIShared import checkFactory, clickAndVerifyColumns, verifyTableEntries
from locator.administration import AdministrationLoc
from selenium.webdriver.common.keys import Keys

import logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

import pdb, time

class Notifications(Administration):
    def __init__(self, **kwargs):
        logger.info('Entering testing of Notification Page...')
        super(Notifications, self).__init__(**kwargs)

    def check_notification_setting(self):   # Smoke test on Notification page
        if not self._go_to_administration_page_by("Notifications"):
            logger.error('Unable to reach the Notifications Setting page')
            return False

        check_factory = checkFactory(self.selenium)

        check_factory.add_to_checklist(css=AdministrationLoc.CSS_PAGE_HEADER,
                                       element_name="Page Title",
                                       text="Notifications")\
                     .add_to_checklist(css=AdministrationLoc.CSS_NOTIFICATION_CONFIG_CARD,
                                       element_name="Notification Config Card")\
                     .add_to_checklist(css=AdministrationLoc.CSS_THREAT_DETECTION_CONFIG,
                                       element_name="Notification Config for Threat Detection")\
                     .add_to_checklist(css=AdministrationLoc.CSS_SYSTEM_ALERTS_CONFIG,
                                       element_name="Notification Config for System Alerts")\
                     .add_to_checklist(css=AdministrationLoc.CSS_SAVE_BUTTON_DISABLED,
                                       element_name="Save Button",
                                       text="Save")
        if not check_factory.check_all():
            return False

        titles = self.selenium.findMultiCSS(selector="zing-notify .content .title")
        titles_text = []
        for title in titles:
            titles_text.append(title.text.strip())
        for expected_title in ["Zingbox Threat Detection", "System Alerts", "Policies"]:
            assert expected_title in titles_text
        return True

    def reg_notification_setting(self):   # Regression test on Notification page
        if not self._go_to_administration_page_by("Notifications"):
            logger.error('Unable to reach the Notifications Setting page')
            return False

        try:
            self.remove_all_chips_x("threat")
            self.remove_all_chips_x("alert")
            self.select_save_button()
            self.selenium.refresh()
        except:
            pass


        def selects_options_inputs(self, field_value):   # Given 'field_value', select 'zbat testing' and 'quality engineer', makes sure no input duplicates occur
            chip_count = 0

            field, account_name1 = self.select_field_dropdown_option(field_value, account_name = "zbat testing")
            account_chips = self.selenium.findMultiCSSNoHover(selector=AdministrationLoc.CSS_ACCOUNT_CHIPS, timeout=0)
            chip_count += 1

            field, account_name2 = self.select_field_dropdown_option(field_value, account_name = "quality engineer")
            account_chips = self.selenium.findMultiCSSNoHover(selector=AdministrationLoc.CSS_ACCOUNT_CHIPS, timeout=0)
            chip_count += 1

            field.send_keys(account_name1)
            options_exist1 = self.selenium.findMultiCSSNoHover(selector=AdministrationLoc.CSS_DROPDOWN_ACCOUNT_OPTIONS, timeout=0)
            assert options_exist1 == False, "Should not find any account option named 'zbat testing'."

            field = self.select_field(field_value)
            field.clear()

            field.send_keys(account_name2)
            options_exist2 = self.selenium.findMultiCSSNoHover(selector=AdministrationLoc.CSS_DROPDOWN_ACCOUNT_OPTIONS, timeout=0)
            assert options_exist2 == False, "Should not find any account option named 'quality engineer'."

            field = self.select_field(field_value)
            field.clear()

            return chip_count

        save_button_disabled = self.selenium.findSingleCSSNoHover(selector=AdministrationLoc.CSS_SAVE_BUTTON_DISABLED, timeout=0)
        assert save_button_disabled.text == "Save", "Save button should be disabled"

        assert selects_options_inputs(self, "threat") + selects_options_inputs(self, "alert") == 4, "In the 'Threat Detection' and 'System Alerts' fields 4 chips are selected in total."

        self.select_save_button()

        #inconsistent
        #save_notification_banner = self.selenium.findSingleCSSNoHover(selector=AdministrationLoc.CSS_SAVE_NOTIFICATION_BANNER, timeout=30)
        #assert save_notification_banner.text == "Your notification settings have been saved.", "Notification banner with text should appear in top right"

        save_button_disabled = self.selenium.findSingleCSSNoHover(selector=AdministrationLoc.CSS_SAVE_BUTTON_DISABLED, timeout=3)
        assert save_button_disabled.text == "Save", "Save button should be disabled"

        self.selenium.refresh()
        time.sleep(5)

        account_chips = self.selenium.findMultiCSSNoHover(selector=AdministrationLoc.CSS_ACCOUNT_CHIPS, timeout=0)

        assert len(account_chips) == 4, "4 account chips should be saved."

        save_button_disabled = self.selenium.findSingleCSSNoHover(selector=AdministrationLoc.CSS_SAVE_BUTTON_DISABLED, timeout=0)
        assert save_button_disabled.text.lower() == "save", "Save button should be disabled"

        self.remove_all_chips_x("threat")
        self.remove_all_chips_x("alert")

        self.select_save_button()
        time.sleep(3)

        return True

    def select_field_dropdown_option(self, field_value, account_name):   # Given 'field_value' and 'account_name', select an account name from a field
        field = self.select_field(field_value)
        field.click()
        field.send_keys(account_name)
        time.sleep(2)
        field_dropdown_options = self.selenium.findMultiCSSNoHover(selector=AdministrationLoc.CSS_DROPDOWN_ACCOUNT_OPTIONS, timeout=0)
        if not field_dropdown_options:
            pdb.set_trace()
        for option in field_dropdown_options:   # Find 'zbat testing' account dropdown
            if account_name in option.text.lower():
                option.click()
                time.sleep(1)
                field.clear()
                break
            else:
                continue
        page_title = self.selenium.findSingleCSS(selector=".page-title-badget")
        page_title.click()   # Click on page title to refresh the input cursor
        return field, account_name

    def select_field(self, field_value):   # Given 'field_value', select either 'threat' of 'alert' fields on the Notification page
        if field_value == "threat":
            field = self.selenium.findSingleCSSNoHover(selector=AdministrationLoc.CSS_THREAT_DETECTION_CONFIG, timeout=0)
        elif field_value == "alert":
            field = self.selenium.findSingleCSSNoHover(selector=AdministrationLoc.CSS_SYSTEM_ALERTS_CONFIG, timeout=0)
        return field

    def select_save_button(self):   # Click on the 'Save' button
        save_button = self.selenium.findSingleCSSNoHover(selector=AdministrationLoc.CSS_SAVE_BUTTON_ENABLED, timeout=0)
        save_button.click()

    def remove_chip(self, chip_count = 0):   # Not used, but you can select which chip to close throughout all fields
        close_account_chip = self.selenium.findMultiCSSNoHover(selector=AdministrationLoc.CSS_CLOSE_ACCOUNT_CHIP, timeout=0)
        close_account_chip[chip_count].click()

    def remove_all_chips_x(self, field_value):   # Given 'field_value', remove every chip in the field by clicking 'X'
        if field_value == "threat":
            field = self.selenium.findSingleCSSNoHover(selector=AdministrationLoc.CSS_THREAT_DETECTION_CONFIG, timeout=0)
            chips_in_field = self.selenium.findMultiCSSNoHover(selector=".zt-threat-input .chip-icon", timeout=0)
        elif field_value == "alert":
            field = self.selenium.findSingleCSSNoHover(selector=AdministrationLoc.CSS_SYSTEM_ALERTS_CONFIG, timeout=0)
            chips_in_field = self.selenium.findMultiCSSNoHover(selector=".zt-system-input .chip-icon", timeout=0)
        for chip in chips_in_field:
            self.selenium.hoverElement(chip)
            chip.click()
            field.send_keys(Keys.ESCAPE)

    '''
    # 'field.send_keys(Keys.BACKSPACE)' is not working in the loop, UI issues
    def remove_all_chips_backspace(self, field_value):   # Given 'field_value', remove every chip in the field by backspacing
        if field_value == "threat":
            field = self.selenium.findSingleCSSNoHover(selector=AdministrationLoc.CSS_THREAT_DETECTION_CONFIG, timeout=0)
            chips_in_field = self.selenium.findMultiCSSNoHover(selector=".zt-threat-input .chip-icon", timeout=0)
        elif field_value == "alert":
            field = self.selenium.findSingleCSSNoHover(selector=AdministrationLoc.CSS_SYSTEM_ALERTS_CONFIG, timeout=0)
            chips_in_field = self.selenium.findMultiCSSNoHover(selector=".zt-system-input .chip-icon", timeout=0)
        field.click()
        field.send_keys(Keys.BACKSPACE)
        for chip in chips_in_field:
            field.send_keys(Keys.BACKSPACE)
    '''
