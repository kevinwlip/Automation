#!/usr/bin/python

import os, time, re, pdb
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.alert import Alert
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver  import DesiredCapabilities
from selenium.common.exceptions import TimeoutException
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def get_downloaded_files(driver):

  if not driver.current_url.startswith("chrome://downloads"):
    driver.get("chrome://downloads/")

  return driver.execute_script( \
    "return downloads.Manager.get().items_   "
    #"  .filter(e => e.state === 'COMPLETE')  "
    "  .map(e => e.filePath || e.file_path); " )


def get_file_content(driver, path):
    elem = driver.execute_script( \
        "var input = window.document.createElement('INPUT'); "
        "input.setAttribute('type', 'file'); "
        "input.hidden = true; "
        "input.onchange = function (e) { e.stopPropagation() }; "
        "return window.document.documentElement.appendChild(input); " )

    elem._execute('sendKeysToElement', {'value': [ path ], 'text': path})

    result = driver.execute_async_script( \
        "var input = arguments[0], callback = arguments[1]; "
        "var reader = new FileReader(); "
        "reader.onload = function (ev) { callback(reader.result) }; "
        "reader.onerror = function (ex) { callback(ex.message) }; "
        "reader.readAsDataURL(input.files[0]); "
        "input.remove(); "
        , elem)

    return result

class zbWebDriverWait(WebDriverWait): #A multielement friendly version

    def multiUntil(self, selenium, browserobjs, method, message=''): #Should also be responsible for switching contexts
        """Calls the method provided with the driver as an argument until the \
        return value does not evaluate to ``False``.
        :param method: callable(WebDriver)
        :param message: optional message for :exc:`TimeoutException`
        :returns: the result of the last call to `method`
        :raises: :exc:`selenium.common.exceptions.TimeoutException` if timeout occurs
        """
        screen = None
        stacktrace = None
        end_time = time.time() + self._timeout
        while True:
            for index,obj in enumerate(browserobjs):
                if obj != False:
                    try:
                        if index != 0:
                            selenium.driver.switch_to.frame(obj)
                        else:
                            selenium.driver.switch_to.default_content()
                        value = method(selenium.driver)
                        if value:
                            return obj
                    except self._ignored_exceptions as exc:
                        screen = getattr(exc, 'screen', None)
                        stacktrace = getattr(exc, 'stacktrace', None)
                time.sleep(self._poll)
            if time.time() > end_time:
                break
        raise TimeoutException(message, screen, stacktrace)


class zbSelenium():

    def __init__(self, **kwargs):
        import common.zbCommon
        self.usingV2 = True
        # self.usingV2 = False
        self.downloadFilepath = os.environ['ZBAT_HOME'] + "artifacts/"
        if "usingV2" in kwargs:
            common.zbCommon.usingV2 = bool(kwargs["usingV2"])
        else:
            common.zbCommon.usingV2 = False
        if "browserInstance" in kwargs:
            # if browser already created, then use it
            self.driver = kwargs["browserInstance"]
        else:
            # if browser driver not create yet, then start creating
            # default to Chrome if browser type not given
            self.browser = kwargs["browser"] if "browser" in kwargs else "chrome"
            # default to local webdriver if remote host not given
            self.host = kwargs["host"] if "host" in kwargs else "127.0.0.1:4444"
            if os.environ.get("DOCKER_MACHINE", 'false') == 'false':
                if self.browser == 'internet explorer':
                    desired_capabilities = {
                        "browserName": self.browser,
                        "version": "",
                        "platform": "WINDOWS",
                        "ensureCleanSession": True,
                        "requireWindowFocus": True,  # this is needed do not change
                        "ignoreProtectedModeSettings": True,
                        "browserTimeout": 300,  # browser will timeout in seconds
                        "timeout": 60000   # each session will timeout in milliseconds
                    }
                elif self.browser == 'edge':
                    desired_capabilities = {
                        "browserName": "MicrosoftEdge",
                        "version": "",
                        "platform": "WINDOWS",
                        "browserTimeout": 300,
                        "ensureCleanSession": True,
                        "requireWindowFocus": True,  # this is needed do not change
                    }
                elif self.browser == 'firefox':
                    desired_capabilities = DesiredCapabilities.FIREFOX
                    desired_capabilities["javascriptEnabled"] = True
                elif self.browser == "chromeipad": #Adds the slew of options to have chrome render in iPad mode
                    options = webdriver.ChromeOptions()
                    options.add_argument("user-agent=Mozilla/5.0 (iPad; CPU OS 11_0 like Mac OS X) AppleWebKit/603.1.30 (KHTML, like Gecko) CriOS/60.0.3112.72 Mobile/15A5327g Safari/602.1")
                    mobile_emulation = {"deviceName": "iPad" }
                    options.add_experimental_option("mobileEmulation", mobile_emulation)
                    desired_capabilities = options.to_capabilities()
                    desired_capabilities["browserName"] = "chrome"
                    desired_capabilities["javascriptEnabled"] = True                 
                else:
                    options = webdriver.ChromeOptions()
                    options.add_argument("--incognito")
                    options.add_experimental_option('w3c', False)
                    options.add_experimental_option('prefs', {"profile.default_content_settings.popups":0})
                    #options.add_experimental_option('prefs', {'download.default_directory':self.downloadFilepath, "profile.default_content_settings.popups":0})
                    desired_capabilities = options.to_capabilities()
                    desired_capabilities["browserName"] = self.browser
                    desired_capabilities["javascriptEnabled"] = True
                    desired_capabilities["ensureCleanSession"] = False

            # this is for Docker container
            else:
                options = webdriver.ChromeOptions()
                options.add_argument('--no-sandbox')
                options.add_argument('--headless')
                options.add_argument("--disable-gpu")
                desired_capabilities = options.to_capabilities()

            self.driver = webdriver.Remote(
                command_executor = "http://"+self.host+"/wd/hub",
                desired_capabilities = desired_capabilities
            )
                
            if self.browser in ['chrome','firefox','edge','chromeipad']: 
                self.driver.set_window_size(1920, 1080)
            else:
                self.driver.maximize_window()

    def getURL(self, url):
        try:
            self.driver.get(url)
            return True
        except Exception as e:
            logger.error(f"{e}")
            return False

    def waitCSS(self, **kwargs):
        timeout = kwargs["timeout"] if "timeout" in kwargs else 3
        mydriver = kwargs["browserobj"] if "browserobj" in kwargs else self.driver
        wait = zbWebDriverWait(mydriver, timeout)
        wait_m = mydriver
        if "iframe" in kwargs:
            wait_i = kwargs["iframe"]
        else:
            wait_i = False

        waittype = kwargs["waittype"] if "waittype" in kwargs else "located"

        try:
            if waittype == "located":
                obj = wait.multiUntil(self,(wait_m, wait_i), EC.presence_of_element_located((By.CSS_SELECTOR, kwargs["selector"])))
                return obj
            if waittype == "clickable":
                obj = wait.multiUntil(self,(wait_m, wait_i),EC.element_to_be_clickable((By.CSS_SELECTOR, kwargs["selector"])))
                return obj
            if waittype == "visibility":
                obj = wait.multiUntil(self,(wait_m, wait_i),EC.visibility_of_element_located((By.CSS_SELECTOR, kwargs["selector"])))
                return obj
            if waittype == "invisibility":
                obj = wait.multiUntil(self,(wait_m, wait_i),EC.invisibility_of_element_located((By.CSS_SELECTOR, kwargs["selector"])))
                return obj
        except Exception as e:
            self.assertAction(**kwargs)
            return False

    def hoverElement(self, webElement, **kwargs):
        mydriver = kwargs["browserobj"] if "browserobj" in kwargs else self.driver
        if self.browser == 'firefox':
            self.driver.execute_script("arguments[0].scrollIntoView(true);", webElement) 
        hover = ActionChains(mydriver).move_to_element(webElement)
        hover.perform()

    def pressKey(self, **kwargs):
        mydriver = kwargs["browserobj"] if "browserobj" in kwargs else self.driver
        key = kwargs['key']
        action = ActionChains(mydriver)
        action = action.key_down(key)
        action = action.key_up(key)
        action.perform()

    def acceptAlert(self, **kwargs):
        mydriver = kwargs["browserobj"] if "browserobj" in kwargs else self.driver
        # window_before = mydriver.window_handles[0]
        Alert(mydriver).dismiss()
        # mydriver.switch_to.window(window_before)

    def getAttribute(self, **kwargs):
        if 'selector' not in kwargs or 'attribute' not in kwargs:
            logger.error('zbSelenium/getAttribute: missing argument selector or attribute')
            return None
        element = self.findSingleCSS(**kwargs)
        attribute = kwargs['attribute']
        return element.get_attribute(attribute)

    # required even when browser auto-switches to new tab because references old tab
    def switchToLatestWindow(self, **kwargs):
        mydriver = kwargs["browserobj"] if "browserobj" in kwargs else self.driver
        mydriver.switch_to.window(mydriver.window_handles[-1])

    def switchToEarliestWindow(self, **kwargs):
        mydriver = kwargs["browserobj"] if "browserobj" in kwargs else self.driver
        mydriver.switch_to.window(mydriver.window_handles[0])

    def iFrameHandle(self, **kwargs):
        is_iframe = 0
        try:
            is_iframe  = self.driver.find_element_by_css_selector("iframe")
        except:
            is_iframe = False
        return is_iframe

    def findSingleCSSWaitLoop(self, err_msg='element not found', retry_count=1,retry_delay=1.0,**kwargs):
        foundit = False
        count = 0
        while (not foundit and count < retry_count):
            try:
                foundit = self.findSingleCSSNoHover(**kwargs)
            except:
                pass
            count = count + 1
            time.sleep(retry_delay)
        return foundit
        
    def findSingleCSS(self, err_msg='element not found', **kwargs):
        self.driver.switch_to.default_content()
        if "browserobj" in kwargs: #We are looking in a known object
            mydriver = kwargs["browserobj"]
        else:
            mydriver = self.driver

        myFrame = self.iFrameHandle()
        kwargs["iframe"] = myFrame
        if not self.waitCSS(**kwargs):
            logger.info(f'wait {kwargs["selector"]}')
            logger.info(f'zbSelenium/findSingleCSS: {err_msg}')
            return False
        # mydriver = self.driver
        try:
            result = mydriver.find_element_by_css_selector(kwargs["selector"])
        except:
            result = False

        if result:
            # scroll into view
            if "browserobj" in kwargs:
                if self.browser == 'firefox':
                    self.driver.execute_script("arguments[0].scrollIntoView(true);", mydriver)
                hover = ActionChains(self.driver).move_to_element(result)
            else:
                if self.browser == 'firefox':
                    mydriver.execute_script("arguments[0].scrollIntoView(true);", result)  
                hover = ActionChains(mydriver).move_to_element(result)

            if result.is_displayed():
                try:
                    hover.perform()
                except:
                    logger.info('Unable to hover. Pass instead')
                    return result
        else:
            logger.info(f'{kwargs["selector"]}')
            logger.info(f'zbSelenium/findSingleCSS: {err_msg}')

        return result
        
    def findSingleCSSNoHover(self, err_msg='element not found', **kwargs):
        self.driver.switch_to.default_content()
        if "browserobj" in kwargs:
            mydriver = kwargs["browserobj"]
        else:
            mydriver = self.driver

        myFrame = self.iFrameHandle()
        kwargs["iframe"] = myFrame
        if not self.waitCSS(**kwargs):
            logger.error(f'wait {kwargs["selector"]}')
            logger.error(f'zbSelenium/findSingleCSSNoHover: {err_msg}')
            return False

        try:
            result = mydriver.find_element_by_css_selector(kwargs["selector"])
        except:
            logger.error(kwargs["selector"])
            logger.error(f'zbSelenium/findSingleCSS: {err_msg}')
            result = False
        return result

    def findSingleXpathNoHover(self, err_msg='element not found', **kwargs):
        self.driver.switch_to.default_content()
        if "browserobj" in kwargs:
            mydriver = kwargs["browserobj"]
        else:
            mydriver = self.driver

        myFrame = self.iFrameHandle()
        kwargs["iframe"] = myFrame
        if not self.waitCSS(**kwargs):
            logger.error(f'wait {kwargs["selector"]}')
            logger.error(f'zbSelenium/findSingleXpathNoHover: {err_msg}')
            return False

        try:
            result = mydriver.find_element_by_xpath(kwargs["selector"])
        except:
            logger.error((kwargs["selector"]))
            logger.error(f'zbSelenium/findSingleXpathNoHover: {err_msg}')
            result = False

        return result

    def findSingleVisibleCSS(self, err_msg='element not found', **kwargs):
        self.driver.switch_to.default_content()
        if "browserobj" in kwargs:
            mydriver = kwargs["browserobj"]
        else:
            mydriver = self.driver

        myFrame = self.iFrameHandle()
        kwargs["iframe"] = myFrame
        if not self.waitCSS(**kwargs):
            logger.info(f'wait {kwargs["selector"]}')
            logger.info(f'zbSelenium/findSingleVisibleCSS: {err_msg}')
            return False
        results = mydriver.find_elements_by_css_selector(kwargs["selector"])
        result = False
        for res in results:
            if res.is_displayed():
                result = res
                break

        if result:
            # scroll into view
            if "browserobj" in kwargs:
                if self.browser == 'firefox':
                    self.driver.execute_script("arguments[0].scrollIntoView(true);", mydriver)
                hover = ActionChains(self.driver).move_to_element(mydriver)
            else:
                if self.browser == 'firefox':
                    mydriver.execute_script("arguments[0].scrollIntoView(true);", result)  
                hover = ActionChains(mydriver).move_to_element(result)      
            hover.perform()
        else:
            logger.error(f'zbSelenium/findVisibleSingleCSS: {err_msg}')
            logger.error((kwargs["selector"]))
        return result

    def findMultiCSS(self, err_msg='elements not found', hover=True, **kwargs):
        self.driver.switch_to.default_content()
        if "browserobj" in kwargs:
            mydriver = kwargs["browserobj"]
        else:
            mydriver = self.driver

        myFrame = self.iFrameHandle()
        kwargs["iframe"] = myFrame
        if not self.waitCSS(**kwargs):
            logger.info(f'wait {kwargs["selector"]}')
            logger.info(f'zbSelenium/findMultiCSS: {err_msg}')
            return False
        # mydriver = self.driver
        result = mydriver.find_elements_by_css_selector(kwargs["selector"])
        try:
            if result and hover:
                # scroll into view
                if "browserobj" in kwargs:
                    if self.browser == 'firefox':
                        self.driver.execute_script("arguments[0].scrollIntoView(true);", mydriver)
                    hover = ActionChains(self.driver).move_to_element(mydriver)
                else:
                    if self.browser == 'firefox':
                        mydriver.execute_script("arguments[0].scrollIntoView(true);", result[len(result)-1])  
                    hover = ActionChains(mydriver).move_to_element(result[len(result)-1])
                hover.perform()
            else:
                logger.info((kwargs["selector"]))
                logger.info(f'zbSelenium/findMultiCSS: {err_msg}')
        except Exception as e:
            logger.error(f'zbSelenium/findMultiCS' + f"{e}")
        return result



    def findVisibleMultiCSS(self, err_msg='elements not found', **kwargs):
        self.driver.switch_to.default_content()
        if "browserobj" in kwargs:
            mydriver = kwargs["browserobj"]
        else:
            mydriver = self.driver

        myFrame = self.iFrameHandle()
        kwargs["iframe"] = myFrame
        if not self.waitCSS(**kwargs):
            logger.error(f'wait {kwargs["selector"]}')
            logger.error(f'zbSelenium/findVisibleMultiCSS: {err_msg}')
            return False
        mydriver = self.driver
        result = mydriver.find_elements_by_css_selector(kwargs["selector"])
        try:
            if result: 
                # scroll into view
                if "browserobj" in kwargs:
                    if self.browser == 'firefox':
                        self.driver.execute_script("arguments[0].scrollIntoView(true);", mydriver)
                else:
                    if self.browser == 'firefox':
                        mydriver.execute_script("arguments[0].scrollIntoView(true);", result[len(result)-1])  
            else:
                logger.error((kwargs["selector"]))
                logger.error(f'zbSelenium/findVisibleMultiCSS: {err_msg}')
        except Exception as e:
            logger.error(f"{e}")
        
        if "text" in kwargs:
            result2 = []
            for r in result:
                if kwargs["text"] in r.text:
                    result2.append(r)
            return result2

        result3 = []
        for r in result:
            if r.is_displayed():
                result3.append(r)
        return result3


    def findMultiCSSNoHover(self, err_msg='elements not found', **kwargs):
        self.driver.switch_to.default_content()
        if "browserobj" in kwargs:
            mydriver = kwargs["browserobj"]
        else:
            mydriver = self.driver

        myFrame = self.iFrameHandle()
        kwargs["iframe"] = myFrame
        if not self.waitCSS(**kwargs):
            logger.error(f'wait {kwargs["selector"]}')
            logger.error(f'zbSelenium/findMultiCSSNoHover: {err_msg}')
            return False
        mydriver = self.driver
        result = mydriver.find_elements_by_css_selector(kwargs["selector"])
        try:
            if result: 
                # scroll into view
                if "browserobj" in kwargs:
                    if self.browser == 'firefox':
                        self.driver.execute_script("arguments[0].scrollIntoView(true);", mydriver)
                else:
                    if self.browser == 'firefox':
                        mydriver.execute_script("arguments[0].scrollIntoView(true);", result[len(result)-1])  
            else:
                logger.error((kwargs["selector"]))
                logger.error(f'zbSelenium/findMultiCSSNoHover: {err_msg}')
        except Exception as e:
            logger.error(f"{e}")
        return result

    def findTopMultiCSS(self, err_msg='elements not found', **kwargs):
        self.driver.switch_to.default_content()
        if "browserobj" in kwargs:
            mydriver = kwargs["browserobj"]
        else:
            mydriver = self.driver

        myFrame = self.iFrameHandle()
        kwargs["iframe"] = myFrame
        if not self.waitCSS(**kwargs):
            logger.error(f'wait {kwargs["selector"]}')
            logger.error(f'zbSelenium/findTopMultiCSS: {err_msg}')
            return False

        result = mydriver.find_elements_by_css_selector(kwargs["selector"])
        try:
            if result:
                # scroll into view
                if "browserobj" in kwargs:
                    if self.browser == 'firefox':
                        self.driver.execute_script("arguments[0].scrollIntoView(true);", mydriver)
                    hover = ActionChains(self.driver).move_to_element(mydriver)
                else:
                    if self.browser == 'firefox':
                        mydriver.execute_script("arguments[0].scrollIntoView(true);", result[0]) 
                    hover = ActionChains(mydriver).move_to_element(result[0]) # hovers first element instead
                hover.perform()
            else:
                logger.error((kwargs["selector"]))
                logger.error(('zbSelenium/findTopMultiCSS: {}'.format(err_msg)))
        except Exception as e:
            logger.error(f"{e}")
        return result

    def findMultiCSSFromBrowserobj(self, browserobj=None, err_msg='elements not found', **kwargs):
        if browserobj is None:
            browserobj = self.driver

        if not self.waitCSS(**kwargs):
            logger.error(f'zbSelenium/findMultiCSSFromBrowserobj: {err_msg}')
            return False

        result = browserobj.find_elements_by_css_selector(kwargs["selector"])
        return result

    def sendKeys(self, err_msg='element not found', **kwargs):
        element = self.findSingleCSSNoHover(**kwargs)
        text = kwargs["text"]

        if not element:
            logger.error(f'zbSelenium/sendKeys: {err_msg}')
            return False
        try:
            element.send_keys(text)
            return True
        except Exception as e:
            logger.error(f"{e}")
            logger.error(f'zbSelenium/sendKeys: {err_msg}')
            return False


    def sendKeysOnly(self, key, err_msg='unable to send key'):
        try:
            self.driver.send_keys(key)
            return True
        except Exception as e:
            logger.error(f"{e}")
            logger.error(f'zbSelenium/sendKeyOnly: {err_msg}')
            return False



    def click(self, err_msg='unable to click', **kwargs):
        element = self.findSingleCSS(**kwargs)
        if not element:
            logger.error(f'zbSelenium/click: {err_msg}')
            return False
        try:
            try:
                element.click()
            except Exception as e:
                logger.info("CLICK FAILED")
                logger.info(f"Exception: {str(e)}")
                #element.send_keys("\n")
            # add a little time delay after click to a different page.
            #   if don't wait here, and following functions perform element search
            #   then likely get a StaleElement assertion because page hasn't load yet
            time.sleep(2)
            return True
        except Exception as e:
            logger.error(f"{e}")
            logger.error(f'zbSelenium/click: {err_msg}')
            return False

    def getText(self, err_msg='unable to get text', **kwargs):
        element = self.findSingleCSS(**kwargs)
        if not element:
            logger.error(f'zbSelenium/getText: {err_msg}')
            return False

        try:
            text = element.text
            return text
        except Exception as e:
            logger.error(f"{e}")
            logger.error(f'zbSelenium/getText: {err_msg}')
            return False

    def getTextNoHover(self, err_msg='unable to get text', **kwargs):
        element = self.findSingleCSSNoHover(**kwargs)
        if not element:
            logger.error(f'zbSelenium/getText: {err_msg}')
            return False

        try:
            text = element.text
            return text
        except Exception as e:
            logger.error(f"{e}")
            logger.error(f'zbSelenium/getText: {err_msg}')
            return False

    def moveMouse(self, xoffset=10, yoffset=10):
        actions = ActionChains(self.driver)
        actions.move_by_offset(xoffset, yoffset)
        actions.perform()


    def screenshot(self, filename="screenshot.png"):
        self.driver.save_screenshot(filename)

    def refresh(self):
        self.driver.refresh()

    def goBack(self):
        self.driver.execute_script("window.history.go(-1)")

    def getCurrentURL(self):
        return self.driver.current_url

    def assertAction(self, **kwargs):
        if "screenshot" in kwargs:  
            if kwargs["screenshot"] == True:
                self.screenshot()
            else:
                self.screenshot(kwargs["screenshot"])
        
    def scrollToBottomPage(self):
        # self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight)")
        self.driver.find_element_by_tag_name('body').send_keys(Keys.CONTROL + Keys.END)

    def scroll_to_top_page(self):
        #self.driver.execute_script("arguments[0].scrollIntoView(true);", webElement)
        self.driver.find_element_by_tag_name('body').send_keys(Keys.CONTROL + Keys.HOME)
        time.sleep(0.2)


    def scroll_to_element(self, **kwargs):
        element = self.driver.find_element_by_css_selector(kwargs['selector'])
        element.location_once_scrolled_into_view
    
    def executeScript(self, input, browserobj = None, err_msg='script cannot be executed', **kwargs):
        if browserobj is None:
            browserobj = self.driver
        logger.info(type(kwargs["selector"]))
        if type(kwargs["selector"]) is webdriver.remote.webelement.WebElement:
            element = kwargs
        else:
            element = self.findSingleCSS(**kwargs)
        if not element:
            logger.error(f'zbSelenium/executeScript: No element provided {err_msg}')
            return False

        try:
            browserobj.execute_script(input, element)
            return True
        except Exception as e:
            logger.error(f"{e}")
            logger.error(f'zbSelenium/executeScript: Element not accessible {err_msg}')
            return False

    def is_current_url(self, url):
        return url in self.driver.current_url

    def current_url(self):
        return self.driver.current_url

    def quit(self):
        try:
            self.driver.quit()
            return True
        except Exception as e:
            logger.error(f"{e}")
            return False


