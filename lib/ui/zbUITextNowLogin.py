import time
from common.zbSelenium import zbSelenium

CSS_USERNAME_FIELD = ".uikit-text-field__input[name='username']"
CSS_PASSWORD_FIELD = ".uikit-text-field__input[name='password']"
CSS_LOGIN_BUTTON = ".uikit-button[type='submit']"
CSS_LOGOUT = '#logout'
CSS_LOGOUT_CONFIRM = 'button.primary'

class Login():
    def __init__(self, **kwargs):
        self.params = kwargs
        if "browser" not in kwargs:  self.params["browser"] = "chrome"
        # If there are no existing browser object, then create new, else reuse
        self.selenium = kwargs["browserInstance"] if "browserInstance" in kwargs else zbSelenium(**self.params)


    def login(self):
        """Login to dashboard"""
        rcode = self.selenium.getURL(self.params["url"])

        if rcode:
            self.params["selector"] = CSS_USERNAME_FIELD
            self.params["text"] = self.params["username"]
            rcode = self.selenium.sendKeys(**self.params)

        if rcode:
            self.params["selector"] = CSS_PASSWORD_FIELD
            self.params["text"] = self.params["password"]
            rcode = self.selenium.sendKeys(**self.params)

        if rcode:
            self.params["selector"] = CSS_LOGIN_BUTTON
            rcode = self.selenium.click(**self.params)

        time.sleep(5) # FIXME: This is a hack to leave some time for TextNow to do all the redirects
            
        return self.selenium if rcode else False

    def logout(self):
        rcode = self.selenium.click(selector=CSS_LOGOUT)
        if rcode:
            rcode = self.selenium.click(selector=CSS_LOGIN_BUTTON)

    def close(self):
        if self.selenium:
            self.selenium.quit()
