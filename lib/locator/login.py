class LoginPageLoc(object):
    """ Element locators for Three Kinds of Login Page """
    # global CSS parameters for Login Page

    CSS_USERNAME_FIELD = "input[ng-model='ctrl.username']"
    CSS_PASSWORD_FIELD = "input[ng-model='ctrl.password']"
    CSS_NEXT_BUTTON = ".login-bottom-section [ng-click='ctrl.ssoNext()']"
    CSS_LOGIN_BUTTON = ".login-bottom-section [ng-click='ctrl.loginRequest()']"
    CSS_LOGIN_FAILED = "div.fn-error"
    CSS_OUTLOOK_EMAIL_FIELD = "[name='loginfmt'][type='email']"
    CSS_OUTLOOK_PASSWORD_FIELD = "[name='passwd'][type='password']"
    CSS_OUTLOOK_SUBMIT_BUTTON = "[type='submit']"
    CSS_OUTLOOK_NO_BUTTON = "[type='button'][value='No']"
    CSS_SERIES_BAR = "g.highcharts-series rect"
    CSS_SERIES_NO_DATA = "g.highcharts-no-data"
    CSS_OUTLOOK_EMAIL_ACCOUNT = '.table[tabindex="0"]'
    CSS_OUTLOOK_EMAIL_OTHER = '#otherTile'

    CSS_V2_LOGO = "[alt='Zingbox logo']"
    CSS_LOGIN_GE_LOGO = "img.ng-scope"
    CSS_V1_LOGO = "[ng-src='static/images/partner-logo/zingbox-logo-text.png']"
    CSS_DIALOG_BUTTON_3_PENDO_GUIDE = "#pendo-guide-container ._pendo-clode-guide"
    CSS_DIALOG_BUTTON_2_GETSTARTED = "button.primary"

    CSS_AVATAR = ".avatar"
    CSS_INSPECTOR_ONBOARD_PAGE = "md-content.onboarding-inspector-content"
    CSS_DIALOG_BUTTON_1_TRYIT = "[aria-label='show more tryit close'][ng-click='tryitDialogCtrl.tryit()'] span.ng-scope"

    CSS_USER_PROFILE = "[aria-label='User Profile'] .ng-scope"  # "[category='User Profile']"
    CSS_2FA_FIELD = "[name='smsCode']"
    CSS_REMEMBER_TOKEN = "[aria-label='Trust this computer for 24 hours']"
    CSS_2FA_LOGIN = "[ng-click='ctrl.verifyFromLogin(ctrl.smsCode)']"
    CSS_TRYIT_BUTTON = ".tryit-banner-button[ng-click='ctrl.tryit();']"

    CSS_GET_STARTED_BUTTON = "button.primary"
    CSS_2FA_SET_UP_WITHOUT_INFO = "[ng-show=\"ctrl.loginInfo.twoFAStep === 'SETUP' && !ctrl.twofaSteps.startInfo\"][aria-hidden='false']"
    CSS_2FA_SET_UP_WITH_INFO = ".sms-valid._md"
    CSS_2FA_INFO_GET_STARTED = ".zing-button[name='2FA Start']"
    CSS_INPUT_NEW_PHONE = "[aria-hidden='false'] [name='phoneForm'] [ng-model='ctrl.userPhone.phoneNumber']"
    CSS_TWO_FA_NEXT = ".button-container [name='2FA Next Step']"
    CSS_TWO_FA_VERIFY = ".button-container [name='verify code']"
    CSS_TWO_FA_AUTH = ".button-container [name='2fa auth']"

    CSS_NAVBAR_APPLICATION = "[data-title='Administration']"
    CSS_USER_ACCOUNT = "[data-menu='setting'] li:nth-of-type(1) a"
    CSS_TWO_FA_SWITCH = ".twofa-toggle .md-primary"
    CSS_TWO_FA_START = "[ng-click='ctrl.twofaSteps.startInfo = true'][aria-label='twofa authentication start']"
    CSS_TWO_FA_PASSWORD = "input[ng-model='ctrl.password']"
    CSS_CONFIRM_PASSOWORD_BUTTON = "button[ng-click='ctrl.checkPassword()']"
    CSS_CHANGE_PHONE_NUMBER = ".sms-form [ng-click='ctrl.changePhone()']"
    CSS_LOG_OUT = ".mat-menu-content a:nth-of-type(4)"