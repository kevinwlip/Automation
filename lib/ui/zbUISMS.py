
import json
from common.zbSelenium import zbSelenium
from ui.zbUITextNowLogin import Login
from ui.zbUIShared import waitLoadProgressDone

CSS_SIDE_BAR_CURRENT_PHONE_NUMBER = '#sidebar .recent-list li.current'
CSS_MESSAGE_TEXT = 'pre'


class SMS():

    def __init__(self, **kwargs):
        self.params = kwargs
        self.username = self.params["username"]
        self.apiportal = self.params["apiportal"]
        self.baseurl = kwargs["url"]+'/'

    def login(self):
        self.sms = Login(**self.params)
        self.selenium = self.sms.login()
        rcode = self.selenium.getURL(self.baseurl)
        if rcode: waitLoadProgressDone(self.selenium)

    def verifySMSSent(self, alert_name, alert_description):
        ret = True
        self.login()
        try:
            ret = ret and self._verifyReceivingZingBoxSMS(alert_name, alert_description)
        except:
            print('External endpoint widget test failed')
            self.close()
            ret = False
        self.close()
        return ret

    def _verifyReceivingZingBoxSMS(self, alert_name, alert_description):
        api = self.apiportal + '/{}/'.format(self.username) + 'messages'
        print(('Querying SMS api {} '.format(api)))
        self.selenium.getURL(api)
        text = self.selenium.getText(selector=CSS_MESSAGE_TEXT)

        if text is None:
            print('SMS api returns nothing')
            return False

        response_json = json.loads(text)
        if 'messages' not in response_json:
            print('SMS api returns payload without messages field')
            return False

        messages = response_json['messages']
        if len(messages) < 1:
            print('No message found')
            return False

        for message in messages:
            print('\n\n\n')
            print(('zbUISMS/_verifyReceivingZingBoxSMS: Finding SMS with description: {}'.format(alert_description)))
            message = message['message']
            if alert_name in message or alert_description in message:
                print(('zbUISMS/_verifyReceivingZingBoxSMS: Alert name "{}" or description "{}" found!'.format(alert_name, alert_description)))
                print(('zbUISMS/_verifyReceivingZingBoxSMS: SMS body is "{}"'.format(message)))
                return True
            print(('zbUISMS/_verifyReceivingZingBoxSMS: Description "{}" not in this SMS.'.format(alert_description)))
        return False

    def close(self):
        try:
            if self.selenium:
                self.selenium.close()
        except:
            pass
