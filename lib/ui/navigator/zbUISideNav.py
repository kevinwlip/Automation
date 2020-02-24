from ui.login.zbUILoginCore import Login
import pdb,time,string,random
from selenium.common.exceptions import WebDriverException
from urllib.parse import urlparse

CSS_MENU_PARENT_NODE = "div[ng-if='!item.analyticsLabel']"
CSS_PARENT_NODE_PAGENAME = "span[class='pageName ng-binding ng-scope']"
CSS_CHILD_NODE_PAGENAME = "span[class='ng-binding ng-scope']"
#CSS_MENU_CHILD_NODES = "md-list[data-section='" + childNode[i] + "'] > div[class='md-1-line clickable ng-scope']"

CSS_BOTTOM_MENU_LIVE_CHAT = ".sidenav-body .bottom-section [action='Interact'] button"
CSS_BOTTOM_MENU_HELP_CENTER = ".sidenav-body .bottom-section [name='Navigate to help center'] button"
CSS_BOTTOM_MENU_WHATS_NEW = ".sidenav-body .bottom-section [name='Navigate to release notes'] button"

CSS_LIVE_CHAT_WELCOME = "#slaask-widget-header-title"
CSS_HELP_CENTER_WELCOME = ".search-welcome"
CSS_WHATS_NEW_RELEASE = ".article-list-item"
CSS_HELP_CENTER_FOOTER = "div.footer-inner [title='Home']"

CSS_LIVE_CHAT_BOX = "#slaask-input"
CSS_LIVE_CHAT_SEND = "#slaask-send-input-trigger"
CSS_CONVO_TEXT = "div[class='conversation-text']"

CSS_EMOJI_BUTTON_PANEL = "#slaask-emoji-button"
CSS_EMOJI_HEART = "[src='https://cdn.slaask.com/emoji/heart.png']"
CSS_CONVO_HEART = ".slaask-emoji-big"

CSS_PAPER_CLIP = "#slaask-paperclip"
CSS_SCREEN_SHOT = "#slaask-file-btn-screenshot"
CSS_SCREEN_SHOT_CLOUD = ".slaask-emoji[src='https://cdn.slaask.com/emoji/cloud.png']"
CSS_UPLOAD_FILE = "#slaask-file-btn-file"

CSS_EXIT_LIVE_CHAT = "#slaask-widget-header-cross"
CSS_HEADER_MENU = "button[name='Toggle header menu']"
CSS_LOG_OUT = "button[name='Log out of the application'][ng-click='ctrl.logout()']"




class SideNav():

    def __init__(self, **kwargs):
        self.params = kwargs
        self.selenium = Login(**kwargs).login()

    def verifySideNav(self):
        kwargs = {}
        childNodes = ["monitor","policiesalerts","reports","administration"]

        #finds parent nodes
        kwargs["selector"] = CSS_MENU_PARENT_NODE
        parentNodes = self.selenium.findMultiCSS(**kwargs)
        
        #Opens up single parent node
        for i in range(0,len(parentNodes)):
            parentNodeName = parentNodes[i].text
            parentNodes[i].click()
            time.sleep(1)

            #selects all child nodes based on the parent node
            kwargs["selector"] = "md-list[data-section=" + childNodes[i] + "]>div>div>md-list-item>a>button>div>div>span[class='md-body-2 flex']"
            rcode = self.selenium.findMultiCSS(**kwargs)
            for i in rcode:
                i.click()
                childNodeName = i.text
                time.sleep(1)

                kwargs["selector"] = CSS_PARENT_NODE_PAGENAME
                parentPageName = self.selenium.findSingleCSS(**kwargs)
                parentPageName = parentPageName.text

                kwargs["selector"] = CSS_CHILD_NODE_PAGENAME
                childPageName = self.selenium.findSingleCSS(**kwargs)
                childPageName = childPageName.text

                if parentNodeName[:6] != parentPageName[:6]:
                    print("Side nav did not open to correct page/ parent pagename did not match")
                    print(parentNodeName[:6] + " != " + parentPageName[:6])
                    return False

                if childNodeName[:6] != childPageName[:6]:
                    print("Side nav did not open to correct page/ child pagename did not match")
                    print(childNodeName[:6] + " != " + childPageName[:6])
                    return False
        #everything passed
        return True

    def verifyLiveChat(self):
            # Click the Live Chat Button
        kwargs = {}
        
        kwargs["selector"] = CSS_BOTTOM_MENU_LIVE_CHAT
        tester = self.selenium.findSingleCSS(**kwargs)
        tester.click()

        # Verify Chat Box Title
        kwargs["selector"] = CSS_LIVE_CHAT_WELCOME
        tester = self.selenium.findSingleCSS(**kwargs)
        tester = tester.text
        if "ZingBox Support" in tester is False:
            print("Live Chat Not Found")
            return False
        
        # Enter Text Message
        kwargs["selector"] = CSS_LIVE_CHAT_BOX
        randomString = 'zbat_test'+''.join([random.choice(string.ascii_letters + string.digits) for n in range(32)])
        import pdb; pdb.set_trace()
        kwargs["text"] = randomString
        inputChatMsg = self.selenium.sendKeys(**kwargs)

        # Click Emoji Icon/Panel
        kwargs["selector"] = CSS_EMOJI_BUTTON_PANEL
        tester = self.selenium.findSingleCSS(**kwargs)
        tester.click()

        # Click Heart
        kwargs["selector"] = CSS_EMOJI_HEART
        tester = self.selenium.findSingleCSS(**kwargs)
        tester.click()
        
        # Click Send
        kwargs["selector"] = CSS_LIVE_CHAT_SEND
        tester = self.selenium.findSingleCSS(**kwargs)
        tester.click() # ERROR OCCURS HERE, CANNOT CLICK SEND, CANNOT PROCEED THE TEST CASE
        time.sleep(5)
        return False

        # Verify Message and Heart In Chat
        kwargs["selector"] = CSS_CONVO_TEXT
        tester = self.selenium.findMultiCSS(**kwargs)
        for e in tester:
            if randomString in e.text and CSS_CONVO_HEART in e.text is False:
                print ("Conversation Message Not Found")
                return False
        
        # Click Paperclip for a Screenshot
        kwargs["selector"] = CSS_PAPER_CLIP
        tester = self.selenium.findSingleCSS(**kwargs)
        tester.click()

        # Click Screenshot
        kwargs["selector"] = CSS_SCREEN_SHOT
        tester = self.selenium.findSingleCSS(**kwargs)
        tester.click()

        # Verify Screenshot Uploading
        kwargs["selector"] = CSS_SCREEN_SHOT_CLOUD
        tester = self.selenium.findSingleCSS(**kwargs)
        tester = tester.text
        if "Uploading screenshot" in tester is False:
            print("Could not upload Screen Shot")
            return False        
        
        # Click Paperclip to Upload File 
        kwargs["selector"] = CSS_PAPER_CLIP
        tester = self.selenium.findSingleCSS(**kwargs)
        tester.click()

        # Click and Verify Upload File
        kwargs["selector"] = CSS_UPLOAD_FILE
        tester = self.selenium.findSingleCSS(**kwargs)
        try:
            tester.click()
        except WebDriverException:
            print ("Upload File is not clickable")
            return False
        
        # Click 'X' to Exit the Live Chat
        kwargs["selector"] = CSS_EXIT_LIVE_CHAT
        tester = self.selenium.findSingleCSS(**kwargs)
        tester.click()

        # Re-open the Live Chat Window
        kwargs["selector"] = CSS_BOTTOM_MENU_LIVE_CHAT
        tester = self.selenium.findSingleCSS(**kwargs)
        tester.click()
                
        # Verify Chat Box Title
        kwargs["selector"] = CSS_LIVE_CHAT_WELCOME
        tester = self.selenium.findSingleCSS(**kwargs)
        tester = tester.text
        if "ZingBox Support" in tester is False:
            print("Live Chat Not Found")
            return False

        # Click on Header Menu
        kwargs["selector"] = CSS_HEADER_MENU
        tester = self.selenium.findSingleCSS(**kwargs)
        tester.click()

        # Click on 'Log Out'
        kwargs["selector"] = CSS_LOG_OUT
        tester = self.selenium.findSingleCSS(**kwargs)
        tester.click()

        return True

    def verifyHelpCenter(self):
        # Click the Help Center button
        kwargs = {}             
                
        kwargs["selector"] = CSS_BOTTOM_MENU_HELP_CENTER
        tester = self.selenium.findSingleCSS(**kwargs)
        tester.click()

        # Verify the footer
        self.selenium.switchToLatestWindow()
        kwargs["selector"] = CSS_HELP_CENTER_FOOTER
        tester = self.selenium.findSingleCSS(**kwargs)
        tester = tester.text
        if "Help Center | ZingBox" in tester is False:
            print("Help Center Footer Not Found")
            return False        

        # Verify the title
        kwargs["selector"] = CSS_HELP_CENTER_WELCOME 
        tester = self.selenium.findSingleCSS(**kwargs)
        tester = tester.text

        return "how can we help?" in tester 
        
    def verifyWhatsNew(self):
        # Click the Whats New button
        kwargs = {}
        
        kwargs["selector"] = CSS_BOTTOM_MENU_WHATS_NEW
        tester = self.selenium.findSingleCSS(**kwargs)
        tester.click()
        
        # Verify the footer
        self.selenium.switchToLatestWindow()
        kwargs["selector"] = CSS_HELP_CENTER_FOOTER
        tester = self.selenium.findSingleCSS(**kwargs)
        tester = tester.text
        if "Help Center | ZingBox" in tester is False:
            print("Help Center Footer Not Found")
            return False        

        # Verify Release Page
        kwargs["selector"] = CSS_WHATS_NEW_RELEASE
        tester = self.selenium.findSingleCSS(**kwargs)
        tester = tester.text

        return "Release Updates" in tester

    def close(self):
        if self.selenium:
            self.selenium.quit()
