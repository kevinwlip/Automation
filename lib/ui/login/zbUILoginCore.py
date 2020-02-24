from common.zbSelenium import zbSelenium
from ui.zbUIShared import waitLoadProgressDone
from selenium.webdriver.common.keys import Keys
from locator.login import LoginPageLoc
import logging, time, pdb
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class Login(object):
    def __init__(self, **kwargs):
        self.params = kwargs
        if "browser" not in kwargs:
            self.params["browser"] = "chrome"
        # If there are no existing browser object, then create new, else reuse
        self.selenium = kwargs["browserInstance"] if "browserInstance" in kwargs else zbSelenium(**self.params)

    def gotoLoginPage(self):
        if self.selenium.getCurrentURL() == self.params["url"]:
            self.selenium.scroll_to_top_page()
            return self.selenium
        if self.selenium.getURL(self.params["url"]):
            waitLoadProgressDone(self.selenium)
            return self.selenium
        else:
            return False

    def login(self):
        logger.info("Standard logging in user's account...")
        # login_type can be only 'standard'
        username = self.params['username']
        password = self.params['password']

        if not self.gotoLoginPage():
            logger.error('Unable to get to the login page!')
            return False

        # Standard login for internal user
        if not self.selenium.findSingleCSS(selector=LoginPageLoc.CSS_LOGIN_BUTTON, timeout=1):
            logger.error('Unable to get the login button')
            return False

        self.params["selector"] = LoginPageLoc.CSS_USERNAME_FIELD
        self.params["text"] = username
        self.selenium.sendKeys(**self.params)

        self.params["selector"] = LoginPageLoc.CSS_PASSWORD_FIELD
        self.params["text"] = password
        self.selenium.sendKeys(**self.params)

        self.params["selector"] = LoginPageLoc.CSS_LOGIN_BUTTON
        # normal login don't work no good on these browsers
        if self.params["browser"] in ["chromeipad", "internet explorer"]:
            self.params["text"] = Keys.ENTER
            rcode = self.selenium.sendKeys(**self.params)
        else:
            rcode = self.selenium.click(**self.params)

        if not rcode:
            logger.error('Unable to click the login button')
            return False

        waitLoadProgressDone(self.selenium)
        if not self.selenium.findSingleCSS(selector=LoginPageLoc.CSS_V2_LOGO):
            logger.error('Unable to Reach V2 home page, Login Failed!')
            return False
        logging.info('Login Successfully!')
        return self.selenium

    def check_basic_login_ui(self):
        logger.info("Checking the page of standard login...")
        if not self.gotoLoginPage():
            logger.error('Unable to get to the login page!')
        time.sleep(2)

        login_card = self.selenium.findSingleCSS(selector='md-content.login')
        if not login_card:
            logger.error('Fail to find login card!')
            return False

        logo = self.selenium.findSingleCSS(selector='img.ng-scope')
        if not logo:
            logger.error('Fail to find login zingbox logo!')
            return False

        labels = login_card.find_elements_by_class_name('label-offset')
        if not labels or len(labels) != 2 or labels[0].text != 'Email (Username)' or labels[1].text != 'Password':
            logger.error('Fail to find the input prompts')
            return False

        inputs = login_card.find_elements_by_tag_name('input')
        if not inputs or len(inputs) != 2:
            logger.error('Unable to find input place for user name and password!')
            return False

        if not self.selenium.findSingleCSS(selector='.login-button'):
            logger.error('Unable to find login button')
            return False
        if not self.selenium.findSingleCSS(selector='.forgot-password'):
            logger.error('Unable to find forgot password')
            return False
        if not self.selenium.findSingleCSS(selector='.no-account'):
            logger.error('Unable to find no-account note')
            return False
        logger.info('Pass the check for login page!')
        return True

    def logout(self):
        logger.info('logging out from the current account...')
        if not self.selenium.click(selector=LoginPageLoc.CSS_AVATAR, timeout=3):
            logger.error('Unable to click Avatar icon')
            return False
        if not self.selenium.click(selector=LoginPageLoc.CSS_LOG_OUT, timeout=3):
            logger.error('Unable to click Preference')
            return False
        waitLoadProgressDone(self.selenium)
        return True

    def close(self):
        if self.selenium:
            self.selenium.quit()

