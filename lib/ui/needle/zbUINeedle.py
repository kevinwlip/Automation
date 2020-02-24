#!/usr/bin/python
# coding: utf8
import sys
import os
import pytest
import base64

try:
    zbathome = os.environ['ZBAT_HOME']
except:
    print('Test cannot run.  Please export ZBAT_HOME.')
    sys.exit()

if zbathome+'lib' not in sys.path:
    sys.path.append(zbathome+'lib')



from selenium.webdriver.common.by import By

from urllib.parse import urlparse
from ui.login.zbUILoginCore import Login
from ui.zbUIShared import *
from common.zbCommon import validateDataNotEmpty, rerunIfFail
from selenium.common.exceptions import StaleElementReferenceException
from datetime import datetime
import pdb, time, re
from common.zbConfig import defaultEnv, NUMBER_RETRIES, DELAY_SECONDS, SCREENSHOT_ON_FAIL
import pytest_needle

from needle.cases import import_from_string
from needle.engines.pil_engine import ImageDiff
from PIL import Image, ImageDraw, ImageColor
from selenium.webdriver.remote.webdriver import WebElement
from pytest_needle.exceptions import ImageMismatchException
if sys.version_info >= (3, 0):

    from io import BytesIO as IOClass

    # Ignoring since basetring is not redefined if running on python3
    # pylint: disable=W0622
    # pylint: disable=C0103
    str = str
    # pylint: enable=W0622
    # pylint: enable=C0103

else:
    try:
        from io import StringIO as IOClass
    except ImportError:
        from io import StringIO as IOClass

#Step 1: Install pytest-needle through pip
from pytest_needle.exceptions import ImageMismatchException

defaultConfig = defaultEnv()

#Visual comparing elements
CSS_DASHBOARD_CARDS = "md-card._md"
CSS_CATEGORY_LISTING = "[ng-if='!categoryListingCtrl.selectedEntity || categoryListingCtrl.editModeActive']"

CSS_DEVICE_DETAIL_PANELS = "md-card.device-detail-overall-ml.device-detail-overall" #".device-detail-overall-ml.device-detail-overall"
CSS_DEVICE_DETAIL_ELEMENTS = ".ng-binding[flex='']"
CSS_DEVICE_DETAIL_TITLES = "td.title"
DEVICEID = "cc:95:d7:6c:1f:0a" 
ALERTID = "Dj8uMv"

CSS_ALERT_DETAIL = "[ng-show='alertDetailCtrl.alert']"
CSS_ALERT_DEVICE_PANELS = ".device-detail-overall-ml"
#==============
CSS_GLOBAL_SEARCH_ICON = "i.material-icons.search-button" #"i.material-icons.search-button"
CSS_GLOBAL_SEARCH_FIELD = "input[id='autocompleteFieldID']"
CSS_GLOBAL_SEARCH_PICK_DEV = "[ng-click='globalSearchCtrl.openAll('devices')'][role='button']"
CSS_GLOBAL_SEARCH_PICK_ALERTS = "[ng-click='globalSearchCtrl.openAll('alerts')'][role='button']"
CSS_GLOBAL_SEARCH_PICK_VULN = "[ng-click='globalSearchCtrl.openAll('vulners')'][role='button']"

CSS_GLOBAL_SEARCH_DEVICES_DEVICE_NAME = ".group-item .device-iot-wraper"
CSS_GLOBAL_SEARCH_DEVICES_MAC_ADDRESS = "div[ng-bind-html='item.data.deviceid | cut:false:35 | highlight:globalSearchCtrl.searchText']"
CSS_GLOBAL_SEARCH_DEVICES_IP_ADDRESS = "div[ng-bind-html='item.data.connect_evtContent.ip | cut:false:20 | highlight:globalSearchCtrl.searchText']"
CSS_GLOBAL_SEARCH_DEVICES_IOT_PROFILE = "div[ng-bind-html='item.data.profileid | cut:false:20 | highlight:globalSearchCtrl.searchText']"

CSS_DEVICE_INVENTORY_DEVICE_NAME = "span.md-headline.ng-binding.ng-scope"
CSS_DEVICE_INVENTORY_MAC_ADDRESS = "li[ng-if = 'ctrl.mac'] > span.ng-binding"
CSS_DEVICE_INVENTORY_IOT_PROFILE = ".zing-word-breakall"
CSS_DEVICE_INVENTORY_IP_ADDRESS = "[flex='33'] span.ng-binding"

CSS_GLOBAL_SEARCH_ALERTS_DEVICE_NAME = "[ng-attr-title='{{item.data.msg.hostname}}']"
CSS_GLOBAL_SEARCH_ALERTS_MAC_ADDRESS = "[title='18:65:90:cd:88:0d'][flex='15']"
CSS_GLOBAL_SEARCH_ALERTS_IP_ADDRESS = "[ng-bind-html='item.data.msg.fromip | highlight:globalSearchCtrl.searchText']"
CSS_GLOBAL_SEARCH_ALERTS_NAME = "div[ng-bind-html='item.data.name | cut:false:13 | highlight:globalSearchCtrl.searchText']"

CSS_ALERT_DETAILS_PAGE_ALERT_NAME = ".md-headline"
CSS_ALERT_DETAILS_PAGE_ALERT_CARD = "[zing-tooltip-card=''] [ng-bind='alertDetailCtrl.alert.hostnameCombine']"
CSS_ALERT_DETAILS_PAGE_TOOLTIP_DETAILS = ".item-tooltip .detail-breakdown .flex-70"
CSS_ALERT_DETAILS_PAGE_IP_MATCH = "[ng-bind='alertDetailCtrl.alert.hostnameCombine']"
#==============

class ZBatNeedle(pytest_needle.driver.NeedleDriver):
    def __init__(self, driver, **kwargs):

        self.options = kwargs
        self.driver = driver

        #Step 3: Modify the constructor of needle to disable resizing functions that break selenium at odd times
        # Set viewport position, size
       #self.driver.set_window_position(0, 0)
        #self.set_viewport()

    #Step 2: Modify assert_screenshot and  function to fit zbat scheme. An example of this can be found in zbUINeedle.py
    def get_screenshot(self, element=None,iFrame=None):
        """Returns screenshot image
        :param WebElement element: Crop image to element (Optional)
        :return:
        """

        stream = IOClass(base64.b64decode(self.driver.get_screenshot_as_base64().encode('ascii')))
        image = Image.open(stream).convert('RGB')
        if isinstance(element, WebElement):
            window_size = self._get_window_size()
            image_size = image.size
            # Get dimensions of element
            dimensions = self._get_element_dimensions(element)

            if not image_size == (dimensions['width'], dimensions['height']):
                ratio = self._get_ratio(image_size, window_size)
                if iFrame:
                    self.driver.switch_to_default_content()
                    jank = self.driver.find_element_by_css_selector("iframe")
                    iFrame = self._get_element_dimensions(jank)
                    #iFrame['left'] += int(element.get_attribute('offsetLeft'))
                    #iFrame['top'] += int(element.get_attribute('offsetTop'))
                    self.driver.switch_to_frame(jank)
                ele_rect = list(self._get_element_rect(element))
                if iFrame:
                    ele_rect[0] = (ele_rect[0]) * ratio + iFrame['left']
                    ele_rect[1] = (ele_rect[1]) * ratio + iFrame['top']
                    ele_rect[2] = (ele_rect[2]) * ratio +  iFrame['left']
                    ele_rect[3] = (ele_rect[3]) * ratio + iFrame['top'] 
                return image.crop([point * ratio for point in ele_rect])
        return image
    def get_screenshot_as_image(self, element=None, exclude=None, iFrame=None):
        """
        :param WebElement element: Crop image to element (Optional)
        :param list exclude: Elements to exclude
        :return:
        """

        image = self.get_screenshot(element,iFrame=iFrame)

        # Mask elements in exclude if element is not included
        if isinstance(exclude, (list, tuple)) and exclude and not element:

            # Gather all elements to exclude
            elements = [self._find_element(element) for element in exclude]
            elements = [element for element in elements if element]

            canvas = ImageDraw.Draw(image)

            window_size = self._get_window_size()

            image_size = image.size

            ratio = self._get_ratio(image_size, window_size)

            ele_rect = self._get_element_rect(ele)
            if iFrame:
                ele_rect[0] = (ele_rect[0]  + iFrame['left']) * ratio
                ele_rect[1] = (ele_rect[1]+  iFrame['top']) * ratio 
                ele_rect[2] = (ele_rect[2]+  iFrame['left']) * ratio 
                ele_rect[3] = (ele_rect[3]+ iFrame['top']) * ratio 
            for ele in elements:
                canvas.rectangle(ele_rect,
                                 fill=ImageColor.getrgb('black'))
            del canvas
        return image
    def assert_screenshot(self, file_path, element_or_selector=None, threshold=90, exclude=None,iFrame=None):
        """Fail if new fresh image is too dissimilar from the baseline image

        .. note:: From needle
            https://github.com/python-needle/needle/blob/master/needle/cases.py#L161

        :param str file_path: File name for baseline image
        :param element_or_selector: WebElement or tuple containing selector ex. ('id', 'mainPage')
        :param threshold: Distance threshold
        :param list exclude: Elements or element selectors for areas to exclude
        :return:
        """
        print(file_path)
        element = self._find_element(element_or_selector)
        self.baseline_dir = zbathome + "/artifacts/needle_screenshots/baseline"
        self.output_dir = zbathome + "/artifacts/needle_screenshots/"
        # Get baseline screenshot
        #
        baseline_image = os.path.join(self.baseline_dir, '%s.png' % file_path) \
            if isinstance(file_path, str) else Image.open(file_path).convert('RGB')
        # Take screenshot and exit if in baseline saving mode
        if self.save_baseline:
            try:
                self._create_dir(self.baseline_dir)
                self.get_screenshot_as_image(element, exclude=exclude,iFrame=iFrame).save(baseline_image)
                return True
            except Exception as e:
                print(e)

                #return False
        # Get fresh screenshot
        #if not os.path.isdir(self.output_dir):
            #self._create_dir(self.output_dir)
        fresh_image = self.get_screenshot_as_image(element, exclude=exclude,iFrame=iFrame)
        fresh_image_file = os.path.join(self.output_dir, '%s.png' % file_path)
        fresh_image.save(fresh_image_file)

        # Error if there is not a baseline image to compare
        if not self.save_baseline and not isinstance(file_path, str) and not os.path.exists(baseline_image):
            raise IOError('The baseline screenshot %s does not exist. You might want to '
                          're-run this test in baseline-saving mode.' % baseline_image)
            return False

        # Compare images
        if isinstance(baseline_image, str):
            try:
                self.engine.assertSameFiles(fresh_image_file, baseline_image, threshold)
            except AssertionError as err:
                msg = err.message if hasattr(err, "message") else err.args[0] if err.args else ""
                args = err.args[1:] if len(err.args) > 1 else []
                print(err)
                #raise ImageMismatchException(msg, baseline_image, fresh_image_file, args)
                return False
            finally:
                if self.cleanup_on_success:
                    os.remove(fresh_image_file)
        else:

            diff = ImageDiff(fresh_image, baseline_image)
            distance = abs(diff.get_distance())

            if distance > threshold:
                #pytest.fail('Fail: New screenshot did not match the baseline (by a distance of %.2f)' % distance)
                print(('Fail: New screenshot did not match the baseline (by a distance of %.2f)' % distance))
                return False
            else:
                print(('Pass: New screenshot did not match the baseline (by a distance of %.2f)' % distance))

        print(('The baseline screenshot %s has passed.' % baseline_image))
        return True


def checkElementInBounds(webElement, browserObj):
    pass

CSS_V1_LOGO = "[ng-src='static/images/partner-logo/zingbox-logo-text.png']"
CSS_AVATAR_ICON = "[aria-label='User Profile'] [layout='row']"
CSS_V2_SELECT = "[category='Try new']"
CSS_V2_DASHBOARD_CARDS = "mat-card.mat-card"
CSS_V2_SIDEBAR = "[role='navigation']"
CSS_V2_SECURITY_ALL = ".content_body"
CSS_GET_STARTED_BUTTON = "button.primary"
CSS_V2_SEC_CARDS = "md-card._md"
CSS_V2_SEC_SELECTORS = ".md-subheader-content .card-type-button[type='button']"
CSS_CARDS = "md-card._md"
class Needle_V2():
    def __init__(self, **kwargs):
        self.params = kwargs
        self.selenium = Login(**kwargs).login()
        if '--usingGE' in sys.argv:
            self.isGE = True
        else:
            self.usingGE = False
    def GEUrlParse(self, myurl):
        myurl = self.selenium.driver.current_url
        if(self.isGE):
            meme = myurl.index("guardian")
            myurl = self.selenium.driver.current_url[:meme] + "meme" + self.selenium.driver.current_url[meme:]

    def gotoGeneric(self, input):
        url =  urlparse(self.selenium.driver.current_url)
        rcode = self.selenium.getURL(url.scheme+"://"+url.netloc+"/guardian/"+input)
        waitLoadProgressDone(self.selenium)

    def gotoDashboard(self):
        url =  urlparse(self.selenium.driver.current_url)
        rcode = self.selenium.getURL(url.scheme+"://"+url.netloc+"/guardian/dashboard/summary")
        waitLoadProgressDone(self.selenium)
    def gotoSecurityDashboard(self):
        url =  urlparse(self.selenium.driver.current_url)
        rcode = self.selenium.getURL(url.scheme+"://"+url.netloc+"/guardian/dashboard/security")
        waitLoadProgressDone(self.selenium)
    def lockdownV2(self):
        rcode = self.selenium.findSingleCSS(selector=CSS_V1_LOGO, timeout=3)
        if rcode:
            self.selenium.click(selector=CSS_AVATAR_ICON)
            time.sleep(1)
            self.selenium.click(selector=CSS_V2_SELECT)
            waitLoadProgressDone(self.selenium)

        if not self.selenium.click(selector="[ng-click='tryitDialogCtrl.close()']", timeout=5):
            time.sleep(2)
            beta_message = CSS_GET_STARTED_BUTTON
            self.selenium.click(selector=beta_message, timeout=5)


    def test_executive_dashboard(self,needles, is_baseline, threshold=0):
        self.lockdownV2()
        self.gotoDashboard()
        needles.baseline_dir = zbathome + "/artifacts/needle_screenshots/baseline/"
        needles.output_dir = zbathome + "/artifacts/needle_screenshots/"
        ans = True
        needles.engine_class = 'imagemagick'
        needles.driver = self.selenium.driver
        needles.save_baseline = is_baseline
        lol_cards = self.selenium.findMultiCSSNoHover(selector=CSS_V2_DASHBOARD_CARDS)
        for index, thing in enumerate(lol_cards):           
            needles.driver.execute_script("arguments[0].scrollIntoView(true);", thing)
            file_path = "_" + self.selenium.driver.capabilities["browserName"] + '_DASHBOARD_V2_CARD_' + str(index)
            baseline_image = os.path.join(needles.baseline_dir, '%s.png' % file_path)
            #if not os.path.exists(baseline_image):
            try:
                if needles.assert_screenshot(file_path, thing, threshold) == False:
                    ans = False
            except Exception as e: #It doesn't have a visible image
                continue
        return ans

    def test_security_dashboard(self, needles, is_baseline, threshold=0):
        names = ["SITE","CATEGORY","PROFILE"]
        self.lockdownV2()
        self.gotoSecurityDashboard()
        needles.baseline_dir = zbathome + "/artifacts/needle_screenshots/baseline/"
        needles.output_dir = zbathome + "/artifacts/needle_screenshots/"
        ans = True
        needles.engine_class = 'imagemagick'
        needles.driver = self.selenium.driver
        needles.save_baseline = is_baseline
        iFrame = self.selenium.findSingleCSSNoHover(selector="iframe")
        iFrameD = needles._get_element_dimensions(iFrame)
        groups = self.selenium.findMultiCSS(selector=CSS_V2_SEC_SELECTORS)
        for index2,group in enumerate(groups):
            newgrp = self.selenium.findMultiCSS(selector=CSS_V2_SEC_SELECTORS)
            newgrp[index2].click()
            waitLoadProgressDone(self.selenium)
            newurl = urlparse(self.selenium.driver.current_url)
            #rcode = self.selenium.getURL(newurl.scheme+"://"+ newurl.netloc+ newurl.path+ newurl.query+"&dashboard_type=security&selectedGrouping=" + group)
            waitLoadProgressDone(self.selenium)
            lol_cards = self.selenium.findMultiCSS(selector=CSS_V2_SEC_CARDS)
            for index, thing in enumerate(lol_cards):           
                needles.driver.execute_script("arguments[0].scrollIntoView(true);", thing)
                file_path = "_" + self.selenium.driver.capabilities["browserName"] + '_DASHBOARD_V2_SEC_CARD_' + names[index2] + str(index)
                baseline_image = os.path.join(needles.baseline_dir, '%s.png' % file_path)
                #if not os.path.exists(baseline_image):
                try:
                    if needles.assert_screenshot(file_path, thing, threshold, iFrame=iFrameD) == False:
                        ans = False
                except Exception as e: #It doesn't have a visible image
                    continue
        return ans

    def test_sidebar(self, needles, is_baseline, threshold=0):
        self.gotoDashboard()
        self.lockdownV2()
        needles.baseline_dir = zbathome + "/artifacts/needle_screenshots/baseline/"
        needles.output_dir = zbathome + "/artifacts/needle_screenshots/"
        ans = True
        needles.engine_class = 'imagemagick'
        needles.driver = self.selenium.driver
        #needles.viewport_size = (1920, 1080)
        #needles.set_viewport()
        needles.save_baseline = is_baseline

        barshot = "zing-left-nav"
        sidebar_slots = "div.ng-star-inserted .nav-item[_ngcontent-c2='']"

        stuff = self.selenium.findMultiCSS(selector=sidebar_slots, waittype='visibility')

        try:
            print(len(stuff))
        except Exception as e:
            print(e)
            return False

        for index, thing in enumerate(stuff):
            thing.click()
            time.sleep(1)
            #needles.driver.execute_script("arguments[0].scrollIntoView(true);", thing)
            file_path = "_" + self.selenium.driver.capabilities["browserName"] + '_SIDEBAR_V2_SHOT_' + str(index)
            baseline_image = os.path.join(needles.baseline_dir, '%s.png' % file_path)
            #if not os.path.exists(baseline_image):
            bar_whole = self.selenium.findSingleCSS(selector=barshot)
            try:
                if needles.assert_screenshot(file_path, bar_whole, threshold) == False:
                    ans = False
            except Exception as e: #It doesn't have a visible image
                continue
        return ans

    def test_devices(self,needles, is_baseline, threshold=0):
        CSS_DEV_INV_TOP = "mat-card.mat-card"
        CSS_INV_PANEL = "[name='inventory']"
        self.lockdownV2()
        self.gotoGeneric("monitor/inventory")
        needles.baseline_dir = zbathome + "/artifacts/needle_screenshots/baseline/"
        needles.output_dir = zbathome + "/artifacts/needle_screenshots/"
        ans = True
        needles.engine_class = 'imagemagick'
        needles.driver = self.selenium.driver
        needles.save_baseline = is_baseline
        iFrame = self.selenium.findSingleCSS(selector="iframe")
        iFrameD = needles._get_element_dimensions(iFrame)
        janks = self.selenium.findVisibleMultiCSS(selector=CSS_DEV_INV_TOP)
        ganks = self.selenium.findSingleCSS(selector = CSS_INV_PANEL)
        self.selenium.hoverElement(janks[0])
        #needles.driver.execute_script("arguments[0].scrollIntoView(true);", janks[0])
        file_path = "_" + self.selenium.driver.capabilities["browserName"] + '_DASHBOARD_V2_DEV_INV_TOP'
        baseline_image = os.path.join(needles.baseline_dir, '%s.png' % file_path)
        try:
            if needles.assert_screenshot(file_path, janks[0], threshold, iFrame=iFrameD) == False:
                ans = False
        except Exception as e: #It doesn't have a visible image
            pass
        #self.selenium.hoverElement(janks[1])
        #needles.driver.execute_script("arguments[0].scrollIntoView(true);", janks[1])
        file_path = "_" + self.selenium.driver.capabilities["browserName"] + '_DASHBOARD_V2_DEV_INV_MID'
        baseline_image = os.path.join(needles.baseline_dir, '%s.png' % file_path)
        try:
            if needles.assert_screenshot(file_path, janks[1], threshold, iFrame=iFrameD) == False:
                ans = False
        except Exception as e: #It doesn't have a visible image
            pass
        #self.selenium.hoverElement(janks[2])
        #needles.driver.execute_script("arguments[0].scrollIntoView(true);", ganks)
        file_path = "_" + self.selenium.driver.capabilities["browserName"] + '_DASHBOARD_V2_DEV_INV_TABLE'
        baseline_image = os.path.join(needles.baseline_dir, '%s.png' % file_path)
        try:
            if needles.assert_screenshot(file_path, ganks, threshold, iFrame=iFrameD) == False:
                ans = False
        except Exception as e: #It doesn't have a visible image
            pass

        self.gotoGeneric("monitor/inventory/device/VTJGc2RHVmtYMThxK3BvL3VYSWRSYkF4cHZKV1pEYk9GMGh0d2RIc1RSWkV1QnlscGxoZk5la2h6VFlnTmM5TA")
        iFrame = self.selenium.findSingleCSS(selector="iframe")
        iFrameD = needles._get_element_dimensions(iFrame)
        CSS_DEVICES_CARDS = "md-card._md"
        for index, entity in enumerate(self.selenium.findMultiCSS(selector=CSS_DEVICES_CARDS)):
            needles.driver.execute_script("arguments[0].scrollIntoView(true);", entity)
            file_path = "_" + self.selenium.driver.capabilities["browserName"] + '_DASHBOARD_DEVICE_DETAIL_' + str(index)
            baseline_image = os.path.join(needles.baseline_dir, '%s.png' % file_path)
            try:
                if needles.assert_screenshot(file_path, entity, threshold, iFrame=iFrameD) == False:
                    ans = False
            except Exception as e: #It doesn't have a visible image
                continue
        return ans

    def test_alerts(self,needles, is_baseline, threshold=0):
        CSS_ALERT_CARDS = "md-card._md"
        CSS_DETAILS_GRAPH = ".graph-selector"
        self.lockdownV2()
        self.gotoGeneric("policies/alerts")
        needles.baseline_dir = zbathome + "/artifacts/needle_screenshots/baseline/"
        needles.output_dir = zbathome + "/artifacts/needle_screenshots/"
        ans = True
        needles.engine_class = 'imagemagick'
        needles.driver = self.selenium.driver
        needles.save_baseline = is_baseline
        iFrame = self.selenium.findSingleCSS(selector="iframe")
        iFrameD = needles._get_element_dimensions(iFrame)
        things = self.selenium.findMultiCSS(selector = CSS_ALERT_CARDS)
        for index, thing in enumerate(things):
            needles.driver.execute_script("arguments[0].scrollIntoView(true);", thing)
            file_path = "_" + self.selenium.driver.capabilities["browserName"] + '_DASHBOARD_ALERT_OVERVIEW_' + str(index)
            baseline_image = os.path.join(needles.baseline_dir, '%s.png' % file_path)
            try:
                if needles.assert_screenshot(file_path, thing, threshold, iFrame=iFrameD) == False:
                    ans = False
            except Exception as e: #It doesn't have a visible image
                continue
        self.gotoGeneric("policies/alert/?review=false&id=PvrtYwb")
        iFrame = self.selenium.findSingleCSS(selector="iframe")
        iFrameD = needles._get_element_dimensions(iFrame)
        things = self.selenium.findMultiCSS(selector = CSS_ALERT_CARDS)
        for index, thing in enumerate(things):
            needles.driver.execute_script("arguments[0].scrollIntoView(true);", thing)
            file_path = "_" + self.selenium.driver.capabilities["browserName"] + '_DASHBOARD_ALERT_DETAIL_' + str(index)
            baseline_image = os.path.join(needles.baseline_dir, '%s.png' % file_path)
            try:
                if needles.assert_screenshot(file_path, thing, threshold, iFrame=iFrameD) == False:
                    ans = False
            except Exception as e: #It doesn't have a visible image
                continue
        newthing = self.selenium.findSingleCSSNoHover(selector=CSS_DETAILS_GRAPH)
        needles.driver.execute_script("arguments[0].scrollIntoView(true);", newthing)
        file_path = "_" + self.selenium.driver.capabilities["browserName"] + '_DASHBOARD_ALERT_GRAPH'
        baseline_image = os.path.join(needles.baseline_dir, '%s.png' % file_path)
        try:
            if needles.assert_screenshot(file_path, newthing, threshold, iFrame=iFrameD) == False:
                ans = False
        except Exception as e: #It doesn't have a visible image
            pass
        return ans

    def test_integrations(self,needles, is_baseline, threshold=0):
        self.lockdownV2()
        self.gotoGeneric("integrations/all")
        needles.baseline_dir = zbathome + "/artifacts/needle_screenshots/baseline/"
        needles.output_dir = zbathome + "/artifacts/needle_screenshots/"
        ans = True
        #needles.engine_class = 'imagemagick'
        needles.driver = self.selenium.driver
        needles.save_baseline = is_baseline
        iFrame = self.selenium.findSingleCSS(selector="iframe")
        iFrameD = needles._get_element_dimensions(iFrame)
        print(iFrameD)
        integratez = self.selenium.findVisibleMultiCSS(selector=".boxwrap md-card")
        for index,integrate in enumerate(integratez[:8]):
            meme = self.selenium.findVisibleMultiCSS(selector=".boxwrap md-card")
            needles.driver.execute_script("arguments[0].scrollIntoView(true);", meme[index])
            try:
                meme[index].click()
            except: 
                pdb.set_trace()
            waitLoadProgressDone(self.selenium)
            time.sleep(5)
            iFrame = self.selenium.findSingleCSS(selector="iframe")
            iFrameD = needles._get_element_dimensions(iFrame)
            subcards = self.selenium.findMultiCSS(selector=CSS_CARDS)
            for index2, sub in enumerate(subcards):
                file_path = "_" + self.selenium.driver.capabilities["browserName"] + '_DASHBOARD_SUBINTEGRATION_CARD_' + str(index2) + "_" + str(index)
                baseline_image = os.path.join(needles.baseline_dir, '%s.png' % file_path)
                try:
                    if needles.assert_screenshot(file_path, sub, threshold,iFrame=iFrameD) == False:
                        ans = False
                except Exception as e: #It doesn't have a visible image
                    continue
            self.gotoGeneric("integrations/all")
            iFrame = self.selenium.findSingleCSS(selector="iframe")
            iFrameD = needles._get_element_dimensions(iFrame)
            meme = self.selenium.findVisibleMultiCSS(selector=".boxwrap md-card")
            file_path = "_" + self.selenium.driver.capabilities["browserName"] + '_DASHBOARD_INTEGRATION_CARD_' + str(index)
            baseline_image = os.path.join(needles.baseline_dir, '%s.png' % file_path)
            try:
                if needles.assert_screenshot(file_path, meme[index], threshold,iFrame=iFrameD) == False:
                    ans = False
            except Exception as e: #It doesn't have a visible image
                continue
        return ans

    def test_administration(self,needles, is_baseline, threshold=0):
        self.lockdownV2()
        needles.baseline_dir = zbathome + "/artifacts/needle_screenshots/baseline/"
        needles.output_dir = zbathome + "/artifacts/needle_screenshots/"
        ans = True
        #needles.engine_class = 'imagemagick'
        needles.driver = self.selenium.driver
        needles.save_baseline = is_baseline
        admin_list = ["administration/notifications","administration/inspectors","administration/snmpsettings","administration/license"]
        for index,page in enumerate(admin_list):
            self.gotoGeneric(page)
            cards = self.selenium.findMultiCSS(selector=CSS_CARDS)
            if cards==False:
                cards = self.selenium.findMultiCSS(selector="mat-card")
            if(page == "administration/license"):
                tabs = self.selenium.findMultiCSS(selector="[role='tab']")
                for tab in tabs:
                    needles.driver.execute_script("arguments[0].scrollIntoView(true);", card)
                    file_path = "_" + self.selenium.driver.capabilities["browserName"] + '_DASHBOARD_ADMIN_CARD_' + admin_list[index][15:] + str(index2)
                    baseline_image = os.path.join(needles.baseline_dir, '%s.png' % file_path)
                    try:
                        if needles.assert_screenshot(file_path, card, threshold,iFrame=True) == False:
                            ans = False
                    except Exception as e: #It doesn't have a visible image
                        continue

            for index2,card in enumerate(cards):
                needles.driver.execute_script("arguments[0].scrollIntoView(true);", card)
                file_path = "_" + self.selenium.driver.capabilities["browserName"] + '_DASHBOARD_ADMIN_CARD_' + admin_list[index][15:] + str(index2)
                baseline_image = os.path.join(needles.baseline_dir, '%s.png' % file_path)
                try:
                    if needles.assert_screenshot(file_path, card, threshold,iFrame=True) == False:
                        ans = False
                except Exception as e: #It doesn't have a visible image
                    continue
        return ans


    def close(self):
        if self.selenium:
            self.selenium.quit()



class Needle:
    def __init__(self, **kwargs):
        self.params = kwargs
        self.selenium = Login(**kwargs).login()

    def gotoDashboard(self):
        url = urlparse(self.params["url"])
        rcode = self.selenium.getURL(url.scheme+'://'+url.netloc)
        waitLoadProgressDone(self.selenium)


    def gotoVulnerability(self):
        url = urlparse(self.params["url"])
        rcode = self.selenium.getURL(url.scheme+'://'+url.netloc+"/policiesalerts/vulnerabilities")
        waitLoadProgressDone(self.selenium)

    
    def test_example_element(self, needles):
        needles.driver = self.selenium.driver
        needles.driver.get('https://www.google.com')
        file_path = 'search_field'
        baseline_image = os.path.join(needles.baseline_dir, '%s.png' % file_path)
        if not os.path.exists(baseline_image):
            needles.save_baseline = True
        return needles.assert_screenshot('search_field', (By.ID, 'tsf'))

    def test_global_search_elements(self, needles, is_baseline, threshold=0):
        needles.baseline_dir = zbathome + "/artifacts/needle_screenshots/baseline/"
        needles.output_dir = zbathome + "/artifacts/needle_screenshots/"
        ans = True
        needles.engine_class = 'imagemagick'
        needles.driver = self.selenium.driver

        self.selenium.click(selector=CSS_GLOBAL_SEARCH_ICON)
        time.sleep(1)
        rcode = self.selenium.findSingleCSS(selector=CSS_GLOBAL_SEARCH_FIELD)
        rcode.send_keys("ai")
        self.selenium.click()

        needles.save_baseline = is_baseline
        return ans

    def test_sidebar_elements(self, needles, is_baseline, threshold=0):
        self.gotoDashboard()
        needles.baseline_dir = zbathome + "/artifacts/needle_screenshots/baseline/"
        needles.output_dir = zbathome + "/artifacts/needle_screenshots/"
        ans = True
        needles.engine_class = 'imagemagick'
        needles.driver = self.selenium.driver
        #needles.viewport_size = (1920, 1080)
        #needles.set_viewport()
        needles.save_baseline = is_baseline

        barshot = "[md-is-open='ctrl.sidenavIsOpen']"
        sidebar_slots = ".md-body-2.ng-binding"

        stuff = self.selenium.findMultiCSS(selector=sidebar_slots, waittype='visibility')

        try:
            print(len(stuff))
        except Exception as e:
            print(e)
            return False

        for index, thing in enumerate(stuff):
            thing.click()
            time.sleep(1)
            #needles.driver.execute_script("arguments[0].scrollIntoView(true);", thing)
            file_path = "_" + self.selenium.driver.capabilities["browserName"] + '_SIDEBAR_SHOT_' + str(index)
            baseline_image = os.path.join(needles.baseline_dir, '%s.png' % file_path)
            #if not os.path.exists(baseline_image):
            bar_whole = self.selenium.findSingleCSS(selector=barshot)
            try:
                if needles.assert_screenshot(file_path, bar_whole, threshold) == False:
                    ans = False
            except Exception as e: #It doesn't have a visible image
                continue
        return ans

    def test_vulnerability_elements(self, needles, is_baseline, threshold=0):
        self.gotoVulnerability()
        needles.baseline_dir = zbathome + "/artifacts/needle_screenshots/baseline/"
        needles.output_dir = zbathome + "/artifacts/needle_screenshots/"
        ans = True
        needles.engine_class = 'imagemagick'
        needles.driver = self.selenium.driver
        #needles.viewport_size = (1920, 1080)
        #needles.set_viewport()
        needles.save_baseline = is_baseline
        stuff = self.selenium.findVisibleMultiCSS(selector="md-card")
        for index, thing in enumerate(stuff):
            needles.driver.execute_script("arguments[0].scrollIntoView(true);", thing)
            file_path = "_" + self.selenium.driver.capabilities["browserName"] + '_VULNERABILITY_CARD_' + str(index)
            baseline_image = os.path.join(needles.baseline_dir, '%s.png' % file_path)
            #if not os.path.exists(baseline_image):
            try:
                if needles.assert_screenshot(file_path, thing, threshold) == False:
                    ans = False
            except Exception as e: #It doesn't have a visible image
                continue

        return ans


    def test_dashboard_elements(self, needles, is_baseline, threshold=0):

        self.gotoDashboard()
        needles.baseline_dir = zbathome + "/artifacts/needle_screenshots/baseline/"
        needles.output_dir = zbathome + "/artifacts/needle_screenshots/"
        ans = True
        needles.engine_class = 'imagemagick'
        needles.driver = self.selenium.driver
        #needles.viewport_size = (1920, 1080)
        #needles.set_viewport()
        needles.save_baseline = is_baseline

        stuff = self.selenium.findMultiCSS(selector=CSS_DASHBOARD_CARDS, waittype='visibility')

        try:
            print(len(stuff))
        except Exception as e:
            print(e)
            return False

        for index, thing in enumerate(stuff):
            # index 5 is External Endpoint widget.  we will sip test of this widget
            if index ==5:
                continue
            needles.driver.execute_script("arguments[0].scrollIntoView(true);", thing)
            file_path = "_" + self.selenium.driver.capabilities["browserName"] + '_DASHBOARD_CARD_' + str(index)
            baseline_image = os.path.join(needles.baseline_dir, '%s.png' % file_path)
            #if not os.path.exists(baseline_image):
            try:
                if needles.assert_screenshot(file_path, thing, threshold) == False:
                    ans = False
            except Exception as e: #It doesn't have a visible image
                continue
        return ans


    def test_device_detail_elements(self, needles, is_baseline, threshold=0):

        url = urlparse(self.params["url"])
        needles.baseline_dir = zbathome + "/artifacts/needle_screenshots/baseline/"
        needles.output_dir = zbathome + "/artifacts/needle_screenshots/"

        rcode = self.selenium.getURL(url.scheme+'://'+url.netloc+'/detail/device/'+DEVICEID)

        if rcode:
            waitLoadProgressDone(self.selenium)
        else:
            return False

        ans = True
        needles.engine_class = 'imagemagick'
        needles.driver = self.selenium.driver
        #needles.viewport_size = (1920, 1080)
        #needles.set_viewport()
        needles.save_baseline = is_baseline

        stuff = self.selenium.findMultiCSS(selector=CSS_DEVICE_DETAIL_PANELS)

        try:
            print(len(stuff))
        except Exception as e:
            print(e)
            return False

        for index, thing in enumerate(stuff):

            needles.driver.execute_script("arguments[0].scrollIntoView(true);", thing)
            file_path = "_" + self.selenium.driver.capabilities["browserName"] +"_"  + DEVICEID + "_" + 'DEVICE_DETAIL_PANEL_' + str(index)
            baseline_image = os.path.join(needles.baseline_dir, '%s.png' % file_path)
            #if not os.path.exists(baseline_image):
            try:
                if needles.assert_screenshot(file_path, thing, threshold) == False:
                    ans = False
            except Exception as e: #It doesn't have a visible image
                continue
        return ans

    def test_alert_detail_elements(self, needles, is_baseline, threshold=0):

        url = urlparse(self.params["url"])
        rcode = self.selenium.getURL(url.scheme+'://'+url.netloc+'/policiesalerts/alert?review=false&id='+ALERTID )
        needles.baseline_dir = zbathome + "/artifacts/needle_screenshots/baseline/"
        needles.output_dir = zbathome + "/artifacts/needle_screenshots/"
        if rcode:
            waitLoadProgressDone(self.selenium)
        else:
            return False

        ans = True
        needles.engine_class = 'imagemagick'
        needles.driver = self.selenium.driver
        #needles.viewport_size = (1920, 1080)
        #needles.set_viewport()
        needles.save_baseline = is_baseline

        stuff = self.selenium.findMultiCSS(selector=CSS_ALERT_DETAIL,waittype='visibility')
        try:
            print(len(stuff))
        except Exception as e:
            print(e)
            return False

        for index, thing in enumerate(stuff):
            needles.driver.execute_script("arguments[0].scrollIntoView(true);", thing)
            file_path = "_" + self.selenium.driver.capabilities["browserName"] +"_"  + ALERTID + "_" +  'ALERT_PANEL_' + str(index)
            baseline_image = os.path.join(needles.baseline_dir, '%s.png' % file_path)
            #if not os.path.exists(baseline_image):
            try:
                if needles.assert_screenshot(file_path, thing, threshold) == False:
                    ans = False
            except Exception as e: #It doesn't have a visible image
                continue

        stuff = self.selenium.findMultiCSS(selector=CSS_ALERT_DEVICE_PANELS,waittype='visibility')

        try:
            print(len(stuff))
        except Exception as e:
            print(e)
            return False

        for index, thing in enumerate(stuff):
            needles.driver.execute_script("arguments[0].scrollIntoView(true);", thing)
            file_path = "_" + self.selenium.driver.capabilities["browserName"] +"_"  + ALERTID + "_" +  'ALERT_DETAIL_PANEL_' + str(index)
            baseline_image = os.path.join(needles.baseline_dir, '%s.png' % file_path)
            #if not os.path.exists(baseline_image):
            try:
                if needles.assert_screenshot(file_path, thing, threshold) == False:
                    print("Failed")
                    ans = False
            except Exception as e: #It doesn't have a visible image
                continue
        return ans



    def close(self):
        if self.selenium:
            self.selenium.quit()




    

