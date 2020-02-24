#!/usr/bin/python
# coding: utf8
import sys
import os

try:
    zbathome = os.environ['ZBAT_HOME']
except:
    print('Test cannot run.  Please export ZBAT_HOME.')
    sys.exit()

if zbathome+'lib' not in sys.path:
    sys.path.append(zbathome+'lib')

from urllib.parse import urlparse
from ui.login.zbUILoginCore import Login
from ui.zbUIShared import *
import time, pdb
from common.zbConfig import defaultEnv
import pytest_needle

#Step 1: Install pytest-needle through pip

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
    def assert_screenshot(self, file_path, element_or_selector=None, threshold=90, exclude=None):
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
                self.get_screenshot_as_image(element, exclude=exclude).save(baseline_image)
                return True
            except Exception as e:
                print(e)

                #return False


        # Get fresh screenshot
        #if not os.path.isdir(self.output_dir):
            #self._create_dir(self.output_dir)
        fresh_image = self.get_screenshot_as_image(element, exclude=exclude)
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
CSS_LIGHT_MODE_SELECT = "div.mat-menu-content .ng-star-inserted[mat-menu-item='']"
CSS_V2_DASHBOARD_CARDS = "mat-card.mat-card"
CSS_V2_SIDEBAR = "[role='navigation']"
CSS_V2_SIDEBAR_ELEMENTS = ""
CSS_V2_SIDEBAR_SUBELEMENTS = ""
CSS_UNIVERSAL_CARDS = ""
CSS_V2_SECURITY_ALL = ".content_body"
CSS_GET_STARTED_BUTTON = "button.primary"
CSS_V2_SEC_CARDS = "md-card._md"
CSS_V2_SEC_SELECTORS = ".md-subheader-content .card-type-button[type='button']"
CSS_AVATAR_ALTER = "div.avatar"

class Needle_GE_Login():
    def __init__(self, **kwargs):
        self.params = kwargs
        self.mypage = Login(**kwargs)
        self.selenium = self.mypage.gotoLoginPage()

    def test_login_page(self, needles, is_baseline, threshold=0):
        self.selenium = self.mypage.gotoLoginPage()
        needles.baseline_dir = zbathome + "/artifacts/needle_screenshots/baseline/"
        needles.output_dir = zbathome + "/artifacts/needle_screenshots/"
        ans = True
        needles.engine_class = 'imagemagick'
        needles.driver = self.selenium.driver
        needles.save_baseline = is_baseline
        ganks = self.selenium.findSingleCSS(selector = CSS_V2_SEC_CARDS)
        #needles.driver.execute_script("arguments[0].scrollIntoView();", ganks)
        file_path = "_" + self.selenium.driver.capabilities["browserName"] + '_DASHBOARD_V2_LOGIN'
        baseline_image = os.path.join(needles.baseline_dir, '%s.png' % file_path)
        try:
            if needles.assert_screenshot(file_path, ganks, threshold) == False:
                ans = False
        except Exception as e: #It doesn't have a visible image
            pass
        return ans
    def close(self):
        if self.selenium:
            self.selenium.quit()


class Needle_GE:
    def __init__(self, **kwargs):
        self.params = kwargs
        self.selenium = Login(**kwargs).login()
        if '--usingGE' in sys.argv:
            self.isGE = True
        else:
            self.usingGE = False
        self.selenium.click(selector=CSS_AVATAR_ALTER)
        jl = self.selenium.findMultiCSS(selector=CSS_LIGHT_MODE_SELECT)
        for j in jl:
            if j.text == "Light theme":
                j.click()
                #self.selenium.executeScript("argument[0].click()",j)
                waitLoadProgressDone(self.selenium)
                return
        self.selenium.driver.refresh()
        #self.selenium.executeScript("argument[0].click()",selector=CSS_AVATAR_ALTER)
    def GEUrlParse(self):
        myurl = self.selenium.driver.current_url
        if(self.isGE):
            meme = myurl.index("guardian")
            myurl = self.selenium.driver.current_url[:meme] + "meme" + self.selenium.driver.current_url[meme:]


    def gotoDashboard(self):
        #url =  urlparse(self.selenium.driver.current_url)
        url =  urlparse(self.selenium.driver.current_url)
        if "ge_mssp" in os.environ["NODE_ENV"]:
            rcode = self.selenium.getURL(url.scheme+"://"+url.netloc+"/mssp/dashboard/summary")
        else:
            rcode = self.selenium.getURL(url.scheme+"://"+url.netloc+"/#ge_guardian/dashboard/summary")
        waitLoadProgressDone(self.selenium)
    def gotoSecurityDashboard(self):
        url =  urlparse(self.selenium.driver.current_url)
        rcode = self.selenium.getURL(url.scheme+"://"+url.netloc+"/#ge_guardian/dashboard/security")
        waitLoadProgressDone(self.selenium)
    def gotoOperationalDashboard(self):
        url =  urlparse(self.selenium.driver.current_url)
        rcode = self.selenium.getURL(url.scheme+"://"+url.netloc+"/#ge_guardian/dashboard/operational")
        waitLoadProgressDone(self.selenium)
    def gotoMSSPCustomer(self):
        url =  urlparse(self.selenium.driver.current_url)
        rcode = self.selenium.getURL(url.scheme+"://"+url.netloc+"/mssp/customers")
        waitLoadProgressDone(self.selenium)
    def gotoDeviceInventory(self):
        url =  urlparse(self.selenium.driver.current_url)
        self.selenium.click(selector = "[data-title='Devices']")
        #rcode = self.selenium.getURL(url.scheme+"://"+url.netloc+"/#ge_guardian/monitor/inventory")
        waitLoadProgressDone(self.selenium)
    def gotoVulnerabilities(self):
        url =  urlparse(self.selenium.driver.current_url)
        self.selenium.click(selector = "[data-title='Vulnerabilities']")
        #rcode = self.selenium.getURL(url.scheme+"://"+url.netloc+"/#ge_guardian/risks/vulnerabilities")
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
        #file_path = "_" + self.selenium.driver.capabilities["browserName"] + '_DASHBOARD_TEST_SHOT'
        #needles.assert_screenshot(file_path, self.selenium, threshold)
        for index, thing in enumerate(lol_cards):           
            #needles.driver.execute_script("arguments[0].scrollIntoView(true);", thing)
            self.selenium.hoverElement(thing)
            file_path = "_" + self.selenium.driver.capabilities["browserName"] + '_DASHBOARD_V2_CARD_' + str(index)
            baseline_image = os.path.join(needles.baseline_dir, '%s.png' % file_path)
            #if not os.path.exists(baseline_image):
            try:
                if needles.assert_screenshot(file_path, thing, threshold) == False:
                    ans = False
            except Exception as e: #It doesn't have a visible image
                continue
        return ans
    def test_mssp_customer(self, needles,is_baseline,threshold=0):
        self.lockdownV2()
        self.gotoMSSPCustomer()
        needles.baseline_dir = zbathome + "/artifacts/needle_screenshots/baseline/"
        needles.output_dir = zbathome + "/artifacts/needle_screenshots/"
        ans = True
        needles.engine_class = 'imagemagick'
        needles.driver = self.selenium.driver
        needles.save_baseline = is_baseline
        mssp_cards = self.selenium.findMultiCSSNoHover(selector=".mat-card")
        for index, thing in enumerate(mssp_cards):
            self.selenium.hoverElement(thing)
            file_path = "_" + self.selenium.driver.capabilities["browserName"] + '_CUSTOMER_MSSP_CARD_' + str(index)
            baseline_image = os.path.join(needles.baseline_dir, '%s.png' % file_path)
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
        groups = self.selenium.findMultiCSS(selector=CSS_V2_SEC_SELECTORS)
        for index2,group in enumerate(groups):
            newgrp = self.selenium.findMultiCSS(selector=CSS_V2_SEC_SELECTORS)
            newgrp[index2].click()
            waitLoadProgressDone(self.selenium)
            newurl = urlparse(self.selenium.driver.current_url)
            #rcode = self.selenium.getURL(newurl.scheme+"://"+ newurl.netloc+ newurl.path+ newurl.query+"&dashboard_type=security&selectedGrouping=" + group)
            waitLoadProgressDone(self.selenium)
            lol_cards = self.selenium.findMultiCSSNoHover(selector=CSS_V2_SEC_CARDS)
            for index, thing in enumerate(lol_cards):           
                #needles.driver.execute_script("arguments[0].scrollIntoView(true);", thing)
                file_path = "_" + self.selenium.driver.capabilities["browserName"] + '_DASHBOARD_V2_SEC_CARD_' + names[index2] + str(index)
                baseline_image = os.path.join(needles.baseline_dir, '%s.png' % file_path)
                #if not os.path.exists(baseline_image):
                try:
                    if needles.assert_screenshot(file_path, thing, threshold) == False:
                        ans = False
                except Exception as e: #It doesn't have a visible image
                    continue
    def test_operational_dashboard(self, needles, is_baseline, threshold=0):
        names = ["SITE","CATEGORY","PROFILE"]
        self.lockdownV2()
        self.gotoSecurityDashboard()
        needles.baseline_dir = zbathome + "/artifacts/needle_screenshots/baseline/"
        needles.output_dir = zbathome + "/artifacts/needle_screenshots/"
        ans = True
        needles.engine_class = 'imagemagick'
        needles.driver = self.selenium.driver
        needles.save_baseline = is_baseline
        groups = self.selenium.findMultiCSS(selector=CSS_V2_SEC_SELECTORS)
        for index2,group in enumerate(groups):
            newgrp = self.selenium.findMultiCSS(selector=CSS_V2_SEC_SELECTORS)
            newgrp[index2].click()
            waitLoadProgressDone(self.selenium)
            newurl = urlparse(self.selenium.driver.current_url)
            #rcode = self.selenium.getURL(newurl.scheme+"://"+ newurl.netloc+ newurl.path+ newurl.query+"&dashboard_type=security&selectedGrouping=" + group)
            waitLoadProgressDone(self.selenium)
            lol_cards = self.selenium.findMultiCSSNoHover(selector=CSS_V2_SEC_CARDS)
            for index, thing in enumerate(lol_cards):           
                #needles.driver.execute_script("arguments[0].scrollIntoView(true);", thing)
                file_path = "_" + self.selenium.driver.capabilities["browserName"] + '_DASHBOARD_V2_OP_CARD_' + names[index2] + str(index)
                baseline_image = os.path.join(needles.baseline_dir, '%s.png' % file_path)
                #if not os.path.exists(baseline_image):
                try:
                    if needles.assert_screenshot(file_path, thing, threshold) == False:
                        ans = False
                except Exception as e: #It doesn't have a visible image
                    continue
        return ans
    def test_alert_page(self, needles, is_baseline, threshold=0):
        CSS_ALERT_WIDGETS = "md-card"
        self.lockdownV2()
        url =  urlparse(self.selenium.driver.current_url)
        #rcode = self.selenium.getURL(url.scheme+"://"+url.netloc+"/#ge_guardian/policies/alerts")
        self.selenium.click(selector = "[data-title='Alerts']")
        waitLoadProgressDone(self.selenium)
        needles.baseline_dir = zbathome + "/artifacts/needle_screenshots/baseline/"
        needles.output_dir = zbathome + "/artifacts/needle_screenshots/"
        ans = True
        needles.engine_class = 'imagemagick'
        needles.driver = self.selenium.driver
        needles.save_baseline = is_baseline
        groups = self.selenium.findVisibleMultiCSS(selector="md-card")
        for index2,group in enumerate(groups):
            if group.is_displayed():
                self.selenium.driver.execute_script("arguments[0].scrollIntoView(true);", group)        
                #needles.driver.execute_script("arguments[0].scrollIntoView(true);", group)
                file_path = "_" + self.selenium.driver.capabilities["browserName"] + '_DASHBOARD_V2_ALERT_PAGE_' + str(index2)
                baseline_image = os.path.join(needles.baseline_dir, '%s.png' % file_path)
                #if not os.path.exists(baseline_image):
                try:
                    if needles.assert_screenshot(file_path, group, threshold) == False:
                        ans = False
                except Exception as e: #It doesn't have a visible image
                    continue
        return ans

    def test_sidebar(self, needles, is_baseline, threshold=0):
        self.gotoDashboard()
        needles.baseline_dir = zbathome + "/artifacts/needle_screenshots/baseline/"
        needles.output_dir = zbathome + "/artifacts/needle_screenshots/"
        ans = True
        needles.engine_class = 'imagemagick'
        needles.driver = self.selenium.driver
        #needles.viewport_size = (1920, 1080)
        #needles.set_viewport()
        needles.save_baseline = is_baseline

        barshot = "zing-left-nav"
        sidebar_slots = "div.ng-star-inserted a.ng-star-inserted"

        stuff = self.selenium.findMultiCSS(selector=sidebar_slots, waittype='visibility')

        try:
            print(len(stuff))
        except Exception as e:
            print(e)
            return False

        for index, thing in enumerate(stuff):
            memes = self.selenium.findMultiCSS(selector=sidebar_slots, waittype='visibility')
            memes[index].click()
            time.sleep(1)
            self.selenium.hoverElement(thing)
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

    def test_device_inv(self, needles, is_baseline, threshold=0):
        CSS_DEV_INV_TOP = "mat-card.mat-card"
        CSS_INV_PANEL = "[name='inventory']"
        self.lockdownV2()
        self.gotoDeviceInventory()
        needles.baseline_dir = zbathome + "/artifacts/needle_screenshots/baseline/"
        needles.output_dir = zbathome + "/artifacts/needle_screenshots/"
        ans = True
        needles.engine_class = 'imagemagick'
        needles.driver = self.selenium.driver
        needles.save_baseline = is_baseline
        janks = self.selenium.findVisibleMultiCSS(selector=CSS_DEV_INV_TOP)
        ganks = self.selenium.findSingleCSS(selector = CSS_INV_PANEL)
        self.selenium.hoverElement(janks[0])
        #needles.driver.execute_script("arguments[0].scrollIntoView(true);", janks[0])
        file_path = "_" + self.selenium.driver.capabilities["browserName"] + '_DASHBOARD_V2_DEV_INV_TOP'
        baseline_image = os.path.join(needles.baseline_dir, '%s.png' % file_path)
        try:
            if needles.assert_screenshot(file_path, janks[0], threshold) == False:
                ans = False
        except Exception as e: #It doesn't have a visible image
            pass
        #self.selenium.hoverElement(janks[1])
        #needles.driver.execute_script("arguments[0].scrollIntoView(true);", janks[1])
        file_path = "_" + self.selenium.driver.capabilities["browserName"] + '_DASHBOARD_V2_DEV_INV_MID'
        baseline_image = os.path.join(needles.baseline_dir, '%s.png' % file_path)
        try:
            if needles.assert_screenshot(file_path, janks[1], threshold) == False:
                ans = False
        except Exception as e: #It doesn't have a visible image
            pass
        #self.selenium.hoverElement(janks[2])
        #needles.driver.execute_script("arguments[0].scrollIntoView(true);", ganks)
        file_path = "_" + self.selenium.driver.capabilities["browserName"] + '_DASHBOARD_V2_DEV_INV_TABLE'
        baseline_image = os.path.join(needles.baseline_dir, '%s.png' % file_path)
        try:
            if needles.assert_screenshot(file_path, ganks, threshold) == False:
                ans = False
        except Exception as e: #It doesn't have a visible image
            pass
        return ans

    def test_vulnerabilities(self, needles, is_baseline, threshold=0):
        CSS_ALERT_WIDGETS = "md-card"
        self.lockdownV2()
        self.gotoVulnerabilities()
        needles.baseline_dir = zbathome + "/artifacts/needle_screenshots/baseline/"
        needles.output_dir = zbathome + "/artifacts/needle_screenshots/"
        ans = True
        needles.engine_class = 'imagemagick'
        needles.driver = self.selenium.driver
        needles.save_baseline = is_baseline
        groups = self.selenium.findMultiCSS(selector=".vulnerability-list md-card._md")
        for index, thing in enumerate(groups):
            time.sleep(1)           
            #needles.driver.execute_script("arguments[0].scrollIntoView(true);", thing)
            file_path = "_" + self.selenium.driver.capabilities["browserName"] + '_DASHBOARD_V2_VULN_PAGE_' + str(index)
            baseline_image = os.path.join(needles.baseline_dir, '%s.png' % file_path)
                #if not os.path.exists(baseline_image):
            try:
                if needles.assert_screenshot(file_path, thing, threshold) == False:
                    ans = False
            except Exception as e: #It doesn't have a visible image
                pass
        return ans
        
    def test_device(self, needles, is_baseline, threshold=0):
        pass

    def close(self):
        if self.selenium:
            self.selenium.quit()



