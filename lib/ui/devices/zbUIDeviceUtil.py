#!/usr/bin/python
from ui.zbUIShared import clickSpecificTimerange, waitLoadProgressDone, checkFactory, clickUntilFind
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
import selenium.common.exceptions as selexcept
from ui.zbUISharedTable import click_and_verify_columns, create_header_dict
from ui.zbUIPolicies import Policies
from locator.devices import DeviceLocators, DeviceDetailLocators
import time
import logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class LocalFilter(object):
    def __init__(self, browserobj):
        """
        All functions in LocalFilter is called supposing the browser is in the page of device inventory
        :param browserobj:
        """
        self.selenium = browserobj

    def _get_to_filter_card(self):
        # this is to move the inventory table to the central page, so the local filter would be shown at the top of page
        self.selenium.findMultiCSS(selector=DeviceLocators.CSS_SELECTOR_DEVICE_ROW_ELEMENTS)
        for i in range(5):
            self.selenium.click(selector=DeviceLocators.CSS_SELECTOR_DEVICE_FILTER_ICON)
            if self.selenium.findSingleCSS(selector=DeviceLocators.CSS_FILTER_EDIT_OVERLAY, timeout=2):
                return True
        logger.error('Unable to click the filter icon on the page')
        return False

    def check_ui_elements(self):
        check_factory = checkFactory(self.selenium)
        if not self._get_to_filter_card():
            logger.error('Unable to get to filter edit card')
            return False
        check_factory.add_to_checklist(css=DeviceLocators.CSS_LOCAL_FILTER_CARD,
                                       element_name="filter card title",
                                       text="Create a filter for this table").\
            add_to_checklist(css=DeviceLocators.CSS_LOCAL_FILTER_RESET,
                             element_name="reset filter",
                             text="Reset filter").\
            add_to_checklist(css=DeviceLocators.CSS_SELECTOR_ADD_FILTER,
                             element_name="add a filter").\
            add_to_checklist(css=DeviceLocators.CSS_LOCAL_FILTER_SAVE,
                             element_name="save star in local filter").\
            add_to_checklist(css=DeviceLocators.CSS_LOCAL_FILTER_APPLY,
                             element_name="apply button")
        if not check_factory.check_all():
            return False
        self.selenium.findSingleCSS(selector=DeviceLocators.CSS_TABLE_NAME)
        return True

    def add_filter(self, filters_to_add, include=True, by="type in"):
        """
        This function will add local filters for the inventory page
        :param filters_to_add: a dictionary which contains one or multiple filters to add
               all of the filters are added by typing, instead of selections, unless specified with by param
        :return: true if successfully added, false otherwise
        """
        if not self._get_to_filter_card():
            logger.error('Unable to get to filter edit card')
            return False
        for filt, value in filters_to_add.items():
            self.selenium.click(selector=DeviceLocators.CSS_SELECTOR_ADD_FILTER)
            try:
                inputs = self.selenium.findMultiCSSNoHover(selector=".filter-option-group input")
                assert len(inputs) >= 2, "less than two inputs are found, unsure how to match filter input and value"
                filter_index = int(len(inputs) / 2) - 1
                # make a selection for the filter type
                inputs[2 * filter_index].click()
                filter_options = self.selenium.findMultiCSSNoHover(selector=DeviceLocators.CSS_FILTER_OPTION)
                try:
                    for filter_option in filter_options:
                        if filt in filter_option.text:
                            filter_option.click()
                            break
                except selexcept.StaleElementReferenceException as e:
                    logger.error(str(e))
                    logger.info("pass")
                    pass
                # renew the inputs elements in case they become stale
                time.sleep(0.5)
                inputs = self.selenium.findMultiCSSNoHover(selector=".filter-option-group input")
                if by == 'type in':
                    hover = ActionChains(self.selenium.driver).move_to_element(inputs[2 * filter_index + 1])
                    hover.perform()
                    if not clickUntilFind(self.selenium,
                                          inputs[2 * filter_index + 1],
                                          ".mat-checkbox-label",
                                          selector=".filter-option-group input",
                                          idx=2 * filter_index + 1):
                        logger.error("Cannot find the dropdown options")
                        return False

                    items = self.selenium.findMultiCSSNoHover(selector=".mat-checkbox-label")
                    for item in items:
                        if value in item.text:
                            item.click()
                            self.selenium.driver.find_element_by_tag_name('body').send_keys(Keys.ESCAPE)
                            break
                    time.sleep(1)
                else:
                    inputs[filter_index * 2 + 1].click()
                    filter_values = self.selenium.findMultiCSSNoHover(selector="mat-option.ng-star-inserted")
                    try:
                        for filter_value in filter_values:
                            if filter_value.text in value:
                                filter_value.click()
                                break
                        self.selenium.driver.find_element_by_tag_name('body').send_keys(Keys.ESCAPE)
                    except selexcept.StaleElementReferenceException as e:
                        logger.error(str(e))
                        logger.info('Unable to continue selecting filters, pass')
                        pass

                if not include:
                    exclude_btns = self.selenium.findMultiCSSNoHover(selector="mat-button-toggle:nth-of-type(2)")
                    if not exclude_btns:
                        logger.error('There is no include/exclude option for the filter: ' + filt)
                        return False
                    exclude_btns[filter_index].click()

            except Exception as e:
                logger.error("Failed to add filters by {}!".format(by))
                logger.error(str(e))
                return False

        apply_btn = self.selenium.findSingleCSSNoHover(selector=DeviceLocators.CSS_LOCAL_FILTER_APPLY)
        if not apply_btn:
            logger.error('Unable to apply the filter by{}!'.format(by))
            return False
        try:
            apply_btn.click()
        except Exception as e:
            logger.error(str(e))
            return False
        self.selenium.findSingleCSS(selector=DeviceLocators.CSS_TABLE_NAME) # Hover the mouse to other element.
        waitLoadProgressDone(self.selenium)
        return True

    def check_if_filter_added(self, filters_to_check):
        """
        Check if the filters are presented above the inventory table
        :param filters_to_check: a dict with key to be filter name, value to be filter value or a list of filter values
        :param include: whether the filter is to include sth or exclude sth.
        :return:
        """
        filter_tags = self.selenium.findMultiCSS(selector=".zt-filter-tags")
        try:
            for tag in filter_tags:
                info = tag.find_elements_by_tag_name("zing-tag-new-widget")
                tag_name = info[0].text
                if isinstance(filters_to_check[tag_name], list):
                    for tag_value in info[1:]:
                        assert tag_value.text.split('\n')[0] in filters_to_check[tag_name]
                        logger.info(
                            'Filter of {} with value {} is successfully added and shown on page'.format(tag_name,
                                                                                                        tag_value))
                else:
                    tag_value = info[1].text.split('\n')[0]
                    assert tag_value == filters_to_check[tag_name]
                    logger.info('Filter of {} with value {} is successfully added and shown on page'.format(tag_name,
                                                                                                            tag_value))
                del filters_to_check[tag_name]
        except Exception as e:
            logger.error(str(e))
            logger.error('Fail to check the exception!')
            return False
        if len(filters_to_check) != 0:
            logger.error('Part of the filters is not shown on the page')
        return True

    def reset_filters(self):
        return self.selenium.click(selector="zing-table i.zing_icon_reset")


class DeviceDataGenerator(object):
    def __init__(self, browserobj):
        """
        All methods of this functions are supposed to be called when the page is device inventory.
        :param browserobj:
        """
        self.selenium = browserobj

    def get_data_from_inventory(self, filter_column_type):
        """
        This function takes in a specific column_type for filtering, and returns a device name and a filter-pair
        <filter_column_type, filter_value> that are used for the following setting of filters.

        :param filter_column_type: either a string or a list of string, which indicates the columns that we would like
               to generate data
        :return: a list of data entry, containing device names and the specific values in relative to responding data
        """
        res = []
        if not isinstance(filter_column_type, list):
            filter_column_type = [filter_column_type]
        output = create_header_dict(self.selenium)
        for column in filter_column_type:
            data_entry = dict()
            possible_values = output[column]
            size = len(possible_values)
            for idx in range(size):
                if possible_values[idx].text is not None and possible_values[idx].text != "":
                    data_entry[column] = possible_values[idx].text
                    data_entry["Device Name"] = output["Device Name"][idx].text
                    res.append(data_entry)
                    break
        return res

    def get_device_names_from_inventory(self):
        device_names = []
        output = create_header_dict(self.selenium)
        for element in output["Device Name"]:
            device_names.append(element.text.strip())
        return device_names


class DeviceTooltip(object):
    def __init__(self, browserobj):
        """
        All functions in LocalFilter is called supposing the browser is in the page of device inventory
        :param browserobj:
        """
        self.selenium = browserobj

    def _hover_on_device_entry(self):
        self.selenium.click(selector=DeviceLocators.CSS_TABLE_NAME)
        output = create_header_dict(self.selenium)
        device_name_elements = output["Device Name"]
        device_name_ele = device_name_elements[0]
        hover = ActionChains(self.selenium.driver).move_to_element(device_name_ele)
        hover.perform()
        time.sleep(2)  # let the device name finishes loading
        if self.selenium.findSingleCSS(selector=DeviceLocators.CSS_DEVICE_TOOLTIP, timeout=2):
            return device_name_ele.text
        return False

    def check_tooltip_ui_elements(self):
        """
        This function is supposed to be called when the page is located at the device inventory page
        :return:
        """
        logger.info("Checking the UI elements of the device tooltip")
        device_name = self._hover_on_device_entry()
        if not device_name:
            logger.error("Unable to see the device tooltip after hover on the device name")
            return False
        check_factory = checkFactory(self.selenium)
        check_factory.add_to_checklist(css=DeviceLocators.CSS_DEVICE_WIDGET_TITLE,
                                       element_name="Device Name",
                                       text=device_name)\
                     .add_to_checklist(css=DeviceLocators.CSS_DEVICE_WIDGET_POLICY,
                                       element_name="Create Policy Button",
                                       text="CREATE POLICY")\
                     .add_to_checklist(css=DeviceLocators.CSS_DEVICE_WIDGET_RISK,
                                       element_name="The risk of device")\
                     .add_to_checklist(css=DeviceLocators.CSS_DEVICE_WIDGET_OS,
                                       element_name="The device OS")\
                     .add_to_checklist(css=DeviceLocators.CSS_DEVICE_WIDGET_PROFILE,
                                       element_name="Device Profile")\
                     .add_to_checklist(css=DeviceLocators.CSS_DEVICE_WIDGET_LAST_ACTIVITY,
                                       element_name="Last Activity")\
                     .add_to_checklist(css=DeviceLocators.CSS_DEVICE_WIDGET_IP,
                                       element_name="Device IP")\
                     .add_to_checklist(css=DeviceLocators.CSS_DEVICE_WIDGET_MACADDRESS,
                                       element_name="Device Mac Address")\
                     .add_to_checklist(css=DeviceLocators.CSS_DEVICE_WIDGET_TYPE,
                                       element_name="Device Types")
        assert check_factory.check_all()
        self.selenium.findSingleCSS(selector=DeviceLocators.CSS_TABLE_NAME)
        logger.info('The UI elements on device inventory tooltip are loaded as expected')
        return True

    def check_link_to_alerts_page(self):
        logger.info("Check the link to alerts page from the device tooltip")
        device_name = self._hover_on_device_entry()
        if not device_name:
            logger.error("Unable to see the device tooltip after hover on the device name")
            return False

        link = self.selenium.findSingleCSS(selector=DeviceLocators.CSS_DEVICE_TOOLTIP_ALERTS)
        if not link:
            logger.info("No alerts for this device, pass")
            return True
        link.click()
        self.selenium.click(selector=DeviceLocators.CSS_DEVICE_ALERTS_POPUP, timeout=1)
        waitLoadProgressDone(self.selenium)
        self.selenium.driver.switch_to.window(self.selenium.driver.window_handles[1])
        curr_url = self.selenium.getCurrentURL()
        if "/guardian/policies/alert?" not in curr_url:
            logger.error('Fail to reach the alert detail page')
            return False
        return True

    def add_check_remove_policy_from_device_inventory(self, cancel=False):
        """
        This function is supposed to be called when the page is located at the device inventory page.
        When this function ends, the page is located at the policy page, and the newly created policy
        will be deleted.
        :return:
        """
        logger.info("Add, Check and Remove the policy on this device from the device tooltip")
        device_name = self._hover_on_device_entry()
        if not device_name:
            logger.error("Unable to see the device tooltip after hover on the device name")
            return False
        self.selenium.click(selector=DeviceLocators.CSS_DEVICE_WIDGET_POLICY)
        waitLoadProgressDone(self.selenium)
        curr_url = self.selenium.getCurrentURL()
        if "/guardian/policies/new?" not in curr_url:
            logger.error('Create New Policy Page is not reached')
            return False
        logger.info('Creating a new policy now...')

        policy_toolbox = Policies(selenium=self.selenium)
        policyconfig = dict()
        policyconfig["severity"] = "Low"
        policyconfig["name"] = device_name + "_policy"
        policyconfig["notify"] = "blacklist"
        policyconfig["group1"] = ["Intranet"]
        policyconfig["group2"] = ["Virtual Machine"]
        policyconfig["apps"] = ["https", "100ye.com"]
        policyconfig["days"] = ["Mo", "Tu", "We", "Th", "Fr"]

        if not cancel:
            policy_toolbox.configAddPolicy(add=False, **policyconfig)
            waitLoadProgressDone(self.selenium)

            if not policy_toolbox.checkPolicyExist(device_name + "_policy"):
                logger.error('Unable to find the policy created: ' + device_name + "_policy")
                return False
            logger.info("The policy {} has been created".format(device_name + "_policy"))

            if not policy_toolbox.configDeletePolicy(device_name + "_policy"):
                logger.error('Unable to remove the policy created: ' + device_name + "_policy")
                return False
            logger.info("The policy {} has been deleted".format(device_name + "_policy"))
            return True
        else:
            self.selenium.click(selector=DeviceLocators.CSS_POLICY_CANCEL_BUTTON)
            waitLoadProgressDone(self.selenium)
            return not policy_toolbox.checkPolicyExist(device_name + "_policy")


class AlertWorkFlow(object):
    """
    All the operations below are with the assumption that the page is located at the device detail page.
    """
    def __init__(self, browserobj):
        """
        All functions in LocalFilter is called supposing the browser is in the page of device inventory
        :param browserobj:
        """
        self.selenium = browserobj

    def _resolve_alert(self):
        """
        this function assumes the page displays the alert inventory of device detail page under
        security tab.
        :return: alert name if there is an alert successfully resolved. False otherwise.
        """
        first_alert = self.selenium.findSingleCSS(selector=DeviceDetailLocators.CSS_RISK_ALERT_CARD)
        if not first_alert:
            logger.error("There is no alert card in this page!")
            return False
        alert_name = first_alert.find_element_by_class_name("item-header-name").text
        self.selenium.click(selector=DeviceDetailLocators.CSS_ALERT_ACTION_BTN)
        options = self.selenium.findMultiCSSNoHover(selector=DeviceDetailLocators.CSS_ALERT_OPTION_BTN)
        for option in options:
            try:
                if "Resolve" in option.text:
                    option.click()
                    break
            except AttributeError:
                pass
        resolve_card = self.selenium.findSingleCSS(selector=DeviceDetailLocators.CSS_RESOLVE_CARD, timeout=2)
        if not resolve_card:
            logger.error("Unable to reach the resolve card!")
            return False

        if self.selenium.findSingleCSS(selector=DeviceDetailLocators.CSS_RESOLVE_TYPE_NO_ACTION, waittype="clickable"):
            self.selenium.click(selector=DeviceDetailLocators.CSS_RESOLVE_TYPE_NO_ACTION)
            self.selenium.sendKeys(selector=DeviceDetailLocators.CSS_RESOLVE_CARD_REASON, text="ZBAT Testing: resolve an alert")
            self.selenium.click(selector=DeviceDetailLocators.CSS_RESOLVE_CARD_SUBMIT)
            return alert_name
        return False

    def _reactivate_alert_in_place(self, alert_name):
        """
        This function will directly reactivate the alerts after it is resolved. The operations
        happened on the page of device details, instead of security alert page.
        :param alert_name: the name of alert to reactivate
        :return: True if successfully reactivated. False otherwise.
        """
        alerts = self.selenium.findMultiCSS(selector=DeviceDetailLocators.CSS_RISK_ALERT_CARD)
        for alert in alerts:
            try:
                alert_title = alert.find_element_by_class_name("item-header-name").text
                if alert_title == alert_name:
                    self.selenium.click(selector=DeviceDetailLocators.CSS_ALERT_ACTION_BTN)
                    options = self.selenium.findMultiCSSNoHover(selector=DeviceDetailLocators.CSS_ALERT_OPTION_BTN)
                    for option in options:
                        try:
                            if "Mark as Active" in option.text:
                                option.click()
                                if self.selenium.findSingleCSS(selector=DeviceDetailLocators.CSS_REACTIVATE_CARD_COMMENT):
                                    self.selenium.sendKeys(selector=DeviceDetailLocators.CSS_REACTIVATE_CARD_COMMENT,
                                                           text="ZBAT Testing: reactive an alert")
                                    self.selenium.click(selector=DeviceDetailLocators.CSS_REACTIVATE_CARD_SUBMIT)
                                    return True
                        except AttributeError:
                            pass
            except selexcept.NoSuchElementException as e:
                logger.error("e")
                logger.info("skip this card")
                pass
            except AttributeError:
                pass
        return False

    def resolve_and_reactivate_an_alert(self):
        """
        This function assumes the first alert card under the device inventory is always in active status,
        and it will resolve the active alert first, and then mark it back as active.

        :return: True if finish the process of resolve and reactivate. False otherwise
        """
        # Go to the security Tab
        self.selenium.click(selector=DeviceDetailLocators.CSS_ALERTS_TAB)
        waitLoadProgressDone(self.selenium)
        self.selenium.click(selector=DeviceDetailLocators.CSS_ACTIVE_ALERTS)
        logger.info("Alerts Tab is reached. Verifying the workflow of resolving and reactivating an alert...")
        alert_name = self._resolve_alert()
        if not alert_name:
            logger.error("Unable to resolve the alert")
            return False
        if not self._reactivate_alert_in_place(alert_name):
            logger.error("cannot reactivate the alert: {}".format(alert_name))
            return False
        logger.info("The workflow of resolving and reactivating an alert is verified!")
        return True

    def verify_alert_link(self):
        self.selenium.click(selector=DeviceDetailLocators.CSS_ALERTS_TAB)
        waitLoadProgressDone(self.selenium)
        self.selenium.click(selector=DeviceDetailLocators.CSS_ACTIVE_ALERTS)
        logger.info("Alerts Tab is reached. Verifying the link to alert details on the alert card...")

        first_alert = self.selenium.findSingleCSS(selector=DeviceDetailLocators.CSS_RISK_ALERT_CARD)
        if not first_alert:
            logger.error("There is no alert card in this page!")
            return False
        main_window = self.selenium.driver.current_window_handle

        try:
            alert_link = first_alert.find_element_by_tag_name("a")
            alert_link.click()
        except selexcept.ElementClickInterceptedException as e:
            logger.error(str(e))
            logger.info("Potential Failure in click, pass")
        self.selenium.driver.switch_to.window(self.selenium.driver.window_handles[1])
        curr_url = self.selenium.getCurrentURL()
        if "/guardian/policies/alert?" not in curr_url:
            logger.error('Fail to reach the alert detail page')
            return False
        logger.info("The link to alert details on the alert card passes the check!")
        self.selenium.driver.close()
        self.selenium.driver.switch_to.window(main_window)
        return True










