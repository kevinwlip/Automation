from urllib.parse import urlparse
from ui.login.zbUILoginCore import Login
from ui.zbUIShared import clickSpecificTimerange, clickUntilFind, waitLoadProgressDone, clickAllCheckboxes, \
    clickEachTimerange, waitSeriesGraphDone, verifyDataTimerange, verifyDevicesCount, resetAllDevAllSite, \
    verifyTableEntries, createHeaderDict, checkFactory, setDeviceDetailTab
from ui.zbUISharedTable import create_header_dict
from ui.devices.zbUIDeviceInventory import verifyLinkToDeviceDetail
from ui.devices.zbUIDeviceUtil import AlertWorkFlow
from locator.devices import DeviceLocators, DeviceDetailLocators
from locator.navigator import UISharedLoc
from selenium.webdriver.common.action_chains import ActionChains
import selenium.common.exceptions as selexcep
from selenium.webdriver.common.keys import Keys
import time



import logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class DeviceDetail(object):

    def __init__(self, **kwargs):
        self.params = kwargs
        self.selenium = Login(**kwargs).login()

    def _go_to_device_detail(self, **kwargs):
        # If already reach page, just scroll to top
        curr_url = self.selenium.getCurrentURL()
        if "/guardian/monitor/inventory/device" in curr_url:
            logger.info('Device Detail Page is reached')
            self.selenium.scroll_to_top_page()
            return True

        # reach device inventory page first
        url = urlparse(self.params["url"])
        self.selenium.getURL(url.scheme + '://' + url.netloc + '/guardian/monitor/inventory')
        waitLoadProgressDone(self.selenium)

        # 'All Devices', 'All IoT', 'Traditional IT', 'Medical IoT', 'other IoT', 'Traditional IoT'
        if "IoT" in kwargs and kwargs["IoT"]:
            resetAllDevAllSite(self.selenium, specific=[1, 1, 2])
        else:
            resetAllDevAllSite(self.selenium, specific=[1, 1, 1])

        clickSpecificTimerange(self.selenium, specific="1 Month")

        # click the device link
        if not verifyLinkToDeviceDetail(self.selenium, DeviceLocators.CSS_SELECTOR_DEVICE_NAMES):
            logger.error("Device Detail Page is not reached")
            return False
        else:
            logger.info("Device Detail Page is reached via device inventory link")
            return True

    def _go_to_specific_device_detail(self, device_name):
        """
        This function would check if the current page is the detail page for device with device_name given in the input.
        If it is, then returns True. If not, it will go to the device inventory first, and then look for the device
        name on the first page. If there is, then it clicks, checks the name and returns True. otherwise it returns False
        :param device_name: the device name whose detailed page is what we would like to reach.
        :return:
        """
        # If already reach the device detail page, just scroll to top, check if this is the device we want.
        curr_url = self.selenium.getCurrentURL()
        if "/guardian/monitor/inventory/device" in curr_url:
            self.selenium.scroll_to_top_page()
            device_name_tmp = self.selenium.findSingleCSS(selector=UISharedLoc.CSS_DEVICE_DETAIL_NAME)
            if device_name_tmp and device_name_tmp.text.strip() == device_name:
                logger.info("Already reaches the detail page of specified device: " + device_name)
                return True

        # If not reaches to the required page, reach device inventory page first
        url = urlparse(self.params["url"])
        self.selenium.getURL(url.scheme + '://' + url.netloc + '/guardian/monitor/inventory')
        waitLoadProgressDone(self.selenium)
        clickSpecificTimerange(self.selenium, specific="1 Month")

        # check the device names on device inventory page, and click the specified device link
        try:

            output = create_header_dict(self.selenium)
            elements = output["Device Name"]
            for e in elements:
                if e.text.strip() == device_name:
                    hover = ActionChains(self.selenium.driver).move_to_element(e)
                    hover.perform()
                    time.sleep(2)  # wait some time for hover to be finished
                    e.click()
                    waitLoadProgressDone(self.selenium)
                    device_name_tmp = self.selenium.findSingleCSS(selector=UISharedLoc.CSS_DEVICE_DETAIL_NAME, timeout=10)
                    if device_name_tmp and device_name_tmp.text.strip() == device_name:
                        logger.info("Successfully reaches the detail page of specified device: " + device_name)
                        return True
                    break
            logger.error('Unable to find the required device on the first page!')
            return False
        except Exception as e:
            logger.error(str(e))
            return False

    # This function checks the page of device detail of a traditional IT device
    def check_device_info_card(self):
        assert self._go_to_device_detail(IoT=False)
        check_factory = checkFactory(self.selenium)
        check_factory.add_to_checklist(css=DeviceDetailLocators.CSS_INFO_CARD,
                                       element_name='device info card')\
                     .add_to_checklist(css=DeviceDetailLocators.CSS_DEVICE_IMAGE,
                                       element_name='device image')\
                     .add_to_checklist(css=DeviceDetailLocators.CSS_DEVICE_ESSENTIAL_INFO,
                                       element_name='device info card with essential info')\
                     .add_to_checklist(css=DeviceDetailLocators.CSS_DEVICE_SECONDAYR_CARD,
                                       element_name='device info second card')\
                     .add_to_checklist(css=DeviceDetailLocators.CSS_SECURITY_PART,
                                       element_name='security part')

        assert check_factory.check_all()
        assert verifyTextDetail(self.selenium)
        return True

    def checkTimeSeries(self, time_series=['2 Hours', '1 Day', '1 Week'], strict=False):
        assert self._go_to_device_detail(IoT=False)
        # go through each time range
        for result in (clickEachTimerange(self.selenium, specific=time_series)):
            if not result:
                logger.error('Unable to click all time ranges')
                return False
            if not waitLoadProgressDone(self.selenium):
                logger.error('Unable to load device inventory in selected time range')
                return False
            data = waitSeriesGraphDone(self.selenium)
            if not data:
                logger.error('Traffic series did not find any data')
                return False
            if not verifyDataTimerange(result["time"], data, strict=self.params["comparestrict"]):
                logger.error("Traffic series for " + str(result["time"]) + " has only " + str(len(data)) + " bars.")
                if strict:
                    return False
        return True

    def checkNetworkTraffic(self):
        assert self._go_to_device_detail()
        return verifyNetworkTrafficVenn(self.selenium)

    def checkApplicationsAndProtocols(self):
        assert self._go_to_device_detail()
        return verifyApplicationAndProtocols(self.selenium)

    def checkNetworkUsageDiagram(self):
        assert self._go_to_device_detail()
        #rcode = verifyCategoryView(self.selenium)
        #if not rcode:
            #return False
        rcode = verifyDetailView(self.selenium)
        if not rcode:
            return False
        return True

    def check_network_traffic_circles(self, device_name="inspector-zbat4"):
        """
        This function takes a thorough test on the network traffic card in device detail page.
        :return:
        """
        # First, Go to the device detail page of device "inspector-zbat4"
        if not self._go_to_specific_device_detail(device_name=device_name):
            logger.error('Unable to go to the required device detail page, pass')
            return False
        logger.info("Device detail page of {} is reached!".format(device_name))

        # Go to the security Tab
        self.selenium.click(selector=DeviceDetailLocators.CSS_SECURITY_TAB)
        waitLoadProgressDone(self.selenium)

        # Secondly, for the big circular graph, collect all information of of circles,
        # including the device name they represent, and their protocal info, and updated
        # them in legend_map and protocal_map
        legend_map = dict()
        protocol_map = dict()
        for legend in ["vlan", "intranet", "domestic", "international"]:
            css_selector = DeviceDetailLocators.CSS_CIRCLE_BASE.format(legend)
            circles = self.selenium.findMultiCSS(selector=css_selector, timeout=5)
            if not circles:
                continue
            for circle in circles:
                device_traffic_circle = DeviceTrafficCircle(legend, circle_element=circle)
                device_traffic_circle.get_name_of_self(self.selenium, legend_map)
                device_traffic_circle.get_protocol_of_self(self.selenium, protocol_map)
        logger.info("Maps of legends to device names and protocols to device names are initialized!")

        # Thirdly, Check the legend filter
        # click on each of the legend filter, to get filtered result of devices,
        # and update the circles info in legend_map_cmp. If it matches with legend_map,
        # then it pass, else it return False
        legend_cmp = dict()
        for idx, legend in enumerate(["vlan", "intranet", "domestic", "international"]):
            # click the legend row to filter the devices showing as circles.
            self.selenium.click(selector=DeviceDetailLocators.CSS_LEGEND_ITERATION.format(idx + 1))
            time.sleep(2)
            css_selector = DeviceDetailLocators.CSS_CIRCLE_BASE.format(legend)
            circles = self.selenium.findMultiCSS(selector=css_selector, timeout=0.5)
            if not circles:
                continue
            for circle in circles:
                device_traffic_circle = DeviceTrafficCircle(legend, circle_element=circle)
                device_traffic_circle.get_name_of_self(self.selenium, legend_cmp)

        self.selenium.click(selector=DeviceDetailLocators.CSS_LEGEND_FILTER_RESET)  # reset
        if not _compare_maps(legend_map, legend_cmp):
            logger.error("The results of the legend filters have conflicts")
            return False
        logger.info("Legend filter has passed the check!")

        # Then, check the table below the graph to see if the legend data matches the graph
        self.selenium.click(selector=DeviceDetailLocators.CSS_AGGREGATION_LIST)
        rows = self.selenium.findMultiCSS(selector=DeviceDetailLocators.CSS_NO_HEADER_DATA_ROW)
        for row in rows:
            try:
                row_data = row.text.split('\n')
                legend_in_row = row_data[0].lower()
                number_in_row = int(row_data[1])
                if legend_in_row in legend_map:
                    assert len(legend_map[legend_in_row]) == number_in_row
            # empty rows
            except AttributeError:
                pass
        logger.info("Table of legends has passed the check!")

        # Next, check the local filter of the protocols
        for protocol, device_names_list in protocol_map.items():
            # click the protocol filter and filter the result with protocol
            self.params["selector"] = DeviceDetailLocators.CSS_PROTOCOL_FILTER
            self.params["text"] = protocol
            self.selenium.sendKeys(**self.params)
            self.params["text"] = Keys.ENTER
            self.selenium.sendKeys(**self.params)
            time.sleep(2)
            circles = self.selenium.findMultiCSS(selector=DeviceDetailLocators.CSS_CIRCLE_DEFAULT)
            if not circles:
                continue

            # there might be more circles in the filtering result, because the tooltip may not show the full content of
            # applications and protocols -- [AP-13410]
            if not len(circles) >= len(device_names_list):
                logger.error("The number of filtered results is less than the information in previous page")
                return False
            # check if all circles filtered by protocol has the legend recorded as device_legends_list
            for circle in circles:
                hover = ActionChains(self.selenium.driver).move_to_element(circle)
                hover.perform()
                conn_device_name = self.selenium.findSingleCSSNoHover(selector=DeviceDetailLocators.CSS_TOOLTIP_GROUP_ON_CIRCLE,
                                                                 timeout=3)
                try:
                    conn_device_name = conn_device_name.text
                except AttributeError:
                    conn_device_name = ""

                if conn_device_name in device_names_list:
                    logger.info("Device of {} is present as protocol is set to {}"
                                .format(conn_device_name, protocol))
                    device_names_list.remove(conn_device_name)
            assert len(device_names_list) == 0
            # clean up the previous filters
            self.selenium.click(selector=DeviceDetailLocators.CSS_PROTOCOL_FILTER_RESET)
        logger.info('Protocol Filter has passed the check!')

        # Finally, check the link of Explore Topology
        main_window = self.selenium.driver.current_window_handle
        self.selenium.click(selector=DeviceDetailLocators.CSS_EXPLORE_TOPOLOGY_LINK)
        self.selenium.driver.switch_to.window(self.selenium.driver.window_handles[1])
        curr_url = self.selenium.getCurrentURL()
        if "/v1build/topology" not in curr_url:
            logger.error('Fail to reach the topology page')
            return False
        waitLoadProgressDone(self.selenium)
        topology_device_name = self.selenium.findSingleCSS(selector=DeviceDetailLocators.CSS_TOPOLOGY_DEVICE_NAME)
        if device_name not in topology_device_name.text:
            logger.error("Device name is not correct on the topology page")
            return False
        self.selenium.driver.close()
        self.selenium.driver.switch_to.window(main_window)

        logger.info("Network Traffic Section has pass the check!")
        return True

    def check_resolve_and_reactivate_alert(self, device_name="inspector-zbat4"):
        """
        This function takes a thorough test on the network traffic card in device detail page.
        :return:
        """
        # First, Go to the device detail page of device "inspector-zbat4"
        if not self._go_to_specific_device_detail(device_name=device_name):
            logger.error('Unable to go to the required device detail page, pass')
            return False
        logger.info("Device detail page of {} is reached!".format(device_name))
        clickSpecificTimerange(self.selenium, specific="1 Month")
        alert_workflow = AlertWorkFlow(self.selenium)
        if not alert_workflow.resolve_and_reactivate_an_alert():
            logger.error("Unable to automate the workflow of resolve and activate an alert")
            return False
        logger.info('Successfully automate the alert work flow!')
        if not alert_workflow.verify_alert_link():
            logger.error("Unable to check the link to an alert of a link card")
            return False
        logger.info('Successfully verify the alert link!')
        return True

    def close(self):
        if self.selenium:
            self.selenium.quit()


class DeviceTrafficCircle(object):
    """
    An DeviceTrafficCircle object is used for storing all information for a circle, referring to a device detected
    from the network traffic. These information includes the name, legend and protocols of the device, as well as the
    css selector of the relative UI element.
    """
    def __init__(self, legend, **kwargs):
        self.name = None # The name is not assigned when initialized
        self.legend = legend
        self.css_base = DeviceDetailLocators.CSS_CIRCLE_BASE.format(legend)
        self.protocol = kwargs["protocol"] if "protocol" in kwargs else []
        if "circle_element" in kwargs:
            self.circle_element = kwargs["circle_element"]

    def get_name_of_self(self, browserobj, legend_map):
        """
        This function is only called when the page is at network traffic card of device inventory
        page. In this function, it moves the mouse to the element of the DeviceTrafficCircle object, get
        the popped-up tooltip, and then updates the device name of this object, also updates the legend as key,
        the device name as element in the value list.

        :param browserobj:
        :param legend_map: key: the legend of this DeviceTrafficCircle object; value: a list of DeviceTrafficCircle
        objects that has the corresponding legend.
        :return: True if the specified element has a device name on its tooltip. False otherwise.
        """
        if not self.circle_element:
            logger.critical('The circle object is not related to an actual element!')
            return False
        hover = ActionChains(browserobj.driver).move_to_element(self.circle_element)
        hover.perform()
        device_name = browserobj.findSingleCSSNoHover(selector=DeviceDetailLocators.CSS_TOOLTIP_GROUP_ON_CIRCLE,
                                                      timeout=3)
        try:
            self.name = device_name.text
        except AttributeError:
            self.name = ""

        if self.legend not in legend_map:
            legend_map[self.legend] = [self.name]
        else:
            legend_map[self.legend].append(self.name)
        return True

    def get_protocol_of_self(self, browserobj, protocol_map):
        """
        This function also updates the protocol_map with the key of different protocols found on the circle tooltips,
        and with the value of device names in corresponding to those circles.

        :param protocol_map: an empty map to be filled in this function
        """
        if not self.circle_element:
            logger.critical('The circle object is not related to an actual element!')
            return False
        hover = ActionChains(browserobj.driver).move_to_element(self.circle_element)
        hover.perform()
        tooltip = browserobj.findSingleCSSNoHover(selector=DeviceDetailLocators.CSS_TOOLTIP_ON_CIRCLE, timeout=3)
        if not tooltip:
            logger.error('Unable to find the right tooltip')
            return False
        groups = tooltip.find_elements_by_class_name("tooltip-group")
        for group in groups:
            try:
                title_element = group.find_element_by_class_name("title")
                title_text = title_element.text.strip()
                if title_text == "Protocols":
                    for value in group.find_elements_by_class_name("value"):
                        self.protocol.append(value.text.strip())
                        if value.text.strip() not in protocol_map:
                            protocol_map[value.text.strip()] = []
                        circles_for_protocol = protocol_map[value.text.strip()]
                        circles_for_protocol.append(self.name)
                    logger.info('The device referenced by this circle has the protocols of: ')
                    logger.info(str(self.protocol))
                    return True
            except selexcep.NoSuchElementException:
                pass
            except ValueError:
                pass
        logger.error('Unable to find the protocol info for this device')
        return False


def verifyTextDetail(browserobj):
    params = {}
    params["selector"] = DeviceDetailLocators.CSS_SELECTOR_GENERAL_TEXT_DETAIL
    info = browserobj.findMultiCSS(**params)
    for e in info:
        logger.info(e.text)
        if "".join(e.text.split()) == "":
            pass
        else:
            return True
    return False


def verifyNetworkTrafficVenn(browserobj):
    title = browserobj.findSingleCSS(selector=DeviceDetailLocators.CSS_TRAFFIC_NETWORK_CARD)
    assert title.text == 'Network Traffic'

    link_to_tolology = browserobj.findSingleCSS(selector=DeviceDetailLocators.CSS_EXPLORE_TOPOLOGY_LINK)
    assert 'Explore Topology' in link_to_tolology.text

    check_factory = checkFactory(browserobj)
    # check if the network traffic visualization is of type 1 (centralized graph) or of type 2 (right graph)
    if browserobj.findSingleCSS(selector=DeviceDetailLocators.CSS_TOPOLOGY_GRAPH):
        logger.info('Check if the network traffic card is loaded as type 1')
        check_factory.add_to_checklist(css=DeviceDetailLocators.CSS_TRAFFIC_NETWORK_CARD,
                                       element_name='Network Traffic card title',
                                       text='Network Traffic') \
            .add_to_checklist(css=DeviceDetailLocators.CSS_LEGEND_TITLE,
                              element_name='Legend Title',
                              text='Legend') \
            .add_to_checklist(css=DeviceDetailLocators.CSS_LEGEND_GROUP,
                              element_name='Legend Group') \
            .add_to_checklist(css=DeviceDetailLocators.CSS_FILTER_FORM,
                              element_name='Filter Form') \
            .add_to_checklist(css=DeviceDetailLocators.CSS_RESET_FILTER,
                              element_name='Reset Filters',
                              text='Reset Filters') \
            .add_to_checklist(css=DeviceDetailLocators.GROUP_FILTER,
                              element_name='Alerts Filter')
        assert check_factory.check_all()

        # check if all legend row has it icon and its text
        legend_rows = browserobj.findMultiCSS(selector=DeviceDetailLocators.CSS_LEGEND_ROW)
        for row in legend_rows:
            try:
                row.find_element_by_class_name('circle')
                row.find_element_by_class_name('legend-text')
            except selexcep.NoSuchElementException as e:
                logger.error('Exception: {}'.format(str(e)))
                logger.error('Legend Row is Not Completed!')
                return False

        # check table below network traffic
        agg_list_headers = browserobj.findMultiCSS(selector=DeviceDetailLocators.CSS_AGGREGATION_LIST)
        for header in agg_list_headers:
            header.click()
            if not browserobj.findSingleCSS(selector=DeviceDetailLocators.CSS_AGGREGATION_DATA_ROW):
                return False
    else:
        logger.info('Check if the network traffic card is loaded as type 2')
        check_factory.add_to_checklist(css=DeviceDetailLocators.CSS_OUTER_CIRCLE,
                              element_name='visualization of traffic data') \
                     .add_to_checklist(css=DeviceDetailLocators.CSS_STATISTICS_COLUMN,
                              element_name='Network Traffic statistics')
    return True

def verifyApplicationAndProtocols(browserobj):
    tabs = browserobj.findMultiCSS(selector=DeviceDetailLocators.CSS_APPLICATION_TAB)
    check_factory = checkFactory(browserobj)
    for tab in tabs:
        check_factory.clear_all()
        if 'Applications' in tab.text:
            # check the Applications Tab
            tab.click()
            check_factory.add_to_checklist(css=DeviceDetailLocators.CSS_APPLICATION_TABLE,
                                           element_name='application table')
            assert check_factory.check_all()
        if 'Protocols' in tab.text:
            # check the Protocols tab
            tab.click()
            check_factory.add_to_checklist(css=DeviceDetailLocators.CSS_PROTOCOL_APP_STAT,
                                           element_name='protocol card statistics')
            assert check_factory.check_all()
            num_of_rows = browserobj.findMultiCSS(selector=DeviceDetailLocators.CSS_NETWORK_DETAIL_ROW)
            num_of_bars = browserobj.findMultiCSS(selector=DeviceDetailLocators.CSS_NETWORK_DETAIL_BAR)
            assert num_of_bars == num_of_rows

        return True


def _compare_maps(dictA, dictB):
    if not len(dictA) == len(dictB):
        logger.error('The lengths of the two dictionaries are not matched')
        return False
    for key, valueA in dictA.items():
        if not dictB[key]:
            return False
        if not len(valueA) == len(dictB[key]):
            return False
        for item in valueA:
            if item not in dictB[key]:
                return False
    return True

def verifyCategoryView(browserobj):
    params = {}
    params["selector"] = DeviceDetailLocators.CSS_SELECTOR_CATEGORY_VIEW_BUTTON
    browserobj.click(**params)
    waitLoadProgressDone(browserobj)

    check_factory = checkFactory(browserobj)
    check_factory.add_to_checklist(css=DeviceDetailLocators.CSS_CATEGORY_HEADING,
                                   element_name='headers of category table')
    assert check_factory.check_all()

    rows = browserobj.findMultiCSS(selector=DeviceDetailLocators.CSS_CATEGORY_ROW)
    if not rows:
        logger.info("No data is found below the rows, pass")
        return True
    for row in rows:
        try:
            row.find_element_by_class_name('row-title')
            assert browserobj.findSingleCSS(selector=DeviceDetailLocators.CSS_CATEGORY_CIRCLE_IN_ROW)
        except selexcep.NoSuchElementException as e:
            logger.error('The row in category table is not complete')
            logger.error(str(e))
            return False
        except AssertionError as e:
            logger.error(str(e))
            return False
    return True

def verifyDetailView(browserobj):
    params = {}
    params["selector"] = DeviceDetailLocators.CSS_SELECTOR_DETAIL_VIEW_BUTTON
    browserobj.click(**params)
    waitLoadProgressDone(browserobj)
    params["selector"] = DeviceDetailLocators.CSS_SELECTOR_NETWORK_USAGE_CHART_PATHS
    if len(browserobj.findMultiCSS(**params)) == 0:
        return False
    return True
