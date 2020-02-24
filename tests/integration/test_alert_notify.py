import os, sys, time, re, pytest
from datetime import datetime

try:
    nodeEnv = os.environ['NODE_ENV']
    env = os.environ['ZBAT_HOME']
    kafka_producer = os.environ['KAFKA_PRODUCER']
    zbat_tenant_id = os.environ['ZBAT_TENANT_INTERNAL_ID']
    if 'staging' in nodeEnv:
        zbat_tenant_id = os.environ['ZBAT_STAGING_TENANT_INTERNAL_ID']
    # O365 credentials
    email_account = os.environ['ZBAT_GMAIL_ACCOUNT'] #os.environ['ZBAT_O365_EMAIL_ACCOUNT']
    email_pwd = os.environ['ZBAT_GMAIL_PWD']#os.environ['ZBAT_O365_EMAIL_PWD']
    # Textnow credentials
    text_now_username = os.environ["ZBAT_TEXT_NOW_UNAME"]
    text_now_pwd = os.environ["ZBAT_TEXT_NOW_PWD"]
    # Ring Central credentials
    ring_central_account = os.environ['RING_CENTRAL_ACCOUNT']
    ring_central_ext = os.environ['RING_CENTRAL_EXT']
    ring_central_pwd = os.environ['RING_CENTRAL_PWD']
    ring_central_auth = os.environ['RING_CENTRAL_AUTH_TOKEN']
    # zingbox login
    account = os.environ['ZBAT_O365_EMAIL_ACCOUNT']
    account_pwd = os.environ['ZBAT_O365_EMAIL_PWD']


except:
    print('Test cannot run.  Please export ZBAT_HOME, KAFKA_PRODUCER, ZBAT_TENANT_INTERNAL_ID, ZBAT_O365_EMAIL_ACCOUNT, ZBAT_O365_EMAIL_PWD, ZBAT_TEXT_NOW_UNAME, ZBAT_TEXT_NOW_PWD.')
    sys.exit()

if env+'lib' not in sys.path:
    sys.path.append(env+'lib')

from zbConfig import defaultEnv
from urlparse import urlparse
from zbUIUserAccounts import UserAccounts
from zbKafka import zbKafka
from common.zbEmail import Email_Client
from zbUISMS import SMS
from zbUIShared import *
from common.zbSelenium import zbSelenium
from common.zbCommon import rerunIfFail
from zbUIUserAccounts import UserAccounts
from ring_central import RingCentral


# common variables
#==========================================================
env = defaultEnv()
uiportal = env["sms_uiportal"]
apiportal = env["sms_apiportal"]
if not uiportal: print 'UI portal value not set in zbCommon.py'; sys.exit()
seleniumhost = env["remoteSeleniumServer"]
comparestrict = env["comparestrict"]

# global variables
NUMBER_RETRIES = 1
DELAY_SECONDS = 5


# fixture
@pytest.fixture(scope="module")
def browser(request):
    kwargs = {"url":uiportal, "host":seleniumhost, "apiportal": apiportal, "username":text_now_username, "password":text_now_pwd, "comparestrict":comparestrict, "screenshot":True}
    # providing fixture which is browser object
    br = SMS(**kwargs)
    yield br
    # tearing down
    print "All test finished.  Tearing down"
    br.close()


@pytest.fixture(scope="module", params=["threat"]) #"policy", policy no longer notify with SMS
def generate_alert(request, policyTestsConfig):
    alert_type = request.param
    kwars = {}
    kwars['alert_type'] = '{0}_alert'.format(alert_type)

    # Add your custom keyword arguments, for example
    kwars['tenantid'] = zbat_tenant_id
    if alert_type == 'policy':
        kwars['ruleid'] = policyTestsConfig['alertNotifyPolicyId']

    alert_name = "Automated zbat {0} alert name at unix time {1}".format(alert_type, time.time())
    alert_description = "Automated zbat {0} alert description at unix time {1}".format(alert_type, time.time())
    kwars['name'] = alert_name
    kwars['description'] = alert_description

    # enable SMS
    if alert_type:
        ui = UserAccounts(url=env["uiportal"], username=account, password=account_pwd, host=seleniumhost)
        ui.toggleSMS("qa@zingbox.com", True)
        ui.logout()
        ui.close()
        print('Enabled SMS')

    kafka = zbKafka()
    response = kafka.sendAlert(**kwars)
    print('========2')

    print('Alert name: {}'.format(alert_name))
    print('Alert description: {}'.format(alert_description))
    print('response: {}'.format(response))

    # Leave time for server to send email and sms
    print ("Sleep a minute to wait for server to send email or sms")
    time.sleep(60)

    # disable SMS
    if alert_type:
        ui = UserAccounts(url=env["uiportal"], username=account, password=account_pwd, host= seleniumhost)
        ui.toggleSMS("qa@zingbox.com", False)
        ui.logout()
        ui.close()
        print('Disabled SMS')

    return kwars


# Business logic
#==========================================================
def received_email(email_name, alert_description):
    ret = False
    email_client = Email_Client(host='imap.gmail.com', email=email_account, pwd=email_pwd) #email_account, email_pwd
    emails = email_client.getEmails(search_key='Since', search_value=datetime.today().strftime('%d-%b-%Y'))
    #search_key='Recent' might be better option
    print emails
    for email in emails:
        print('\n\n\n')
        print('test_alert_notify/received_email: Finding email with description: {}'.format(alert_description))
        # email_body = email.getBody()

        # if alert_description in email_body:
        if alert_description in email['body']:
            print('test_alert_notify/received_email: Description {} found!'.format(alert_description))
            print('test_alert_notify/received_email: Email body {}'.format(email['body']))
            ret = True
            # ret = ret and _verify_link_exists_in_email(email.getBody())
            ret = ret and _verify_link_exists_in_email(email['body'])
            break
            
        print('test_alert_notify/received_email: Description "{}" not in this email.'.format(alert_description))
    return ret


def _verify_link_exists_in_email(email_body):
    # look into email body to see if there is a link back to view alert
    return True if re.search(r"(http).*(policiesalerts/alert)", email_body) else False


def received_sms_old(alert_name, alert_description, browser):
    ret = rerunIfFail(function=browser.verifySMSSent(alert_name, alert_description), selenium=None, screenshot=False, testname='test_alert_notify[sms]' ,number=NUMBER_RETRIES, delay=DELAY_SECONDS)
    return ret


def received_sms(alert_name, alert_description, sms_service):
    ret = False
    sms_query = {
            'availability': 'Alive',
            'direction': 'Inbound',
            'page': 1,
            'perPage': 10,
            'messageType': 'SMS',
            'distinctConversations': True #will retrieve latest message from each number
    }

    rcode = sms_service.get_sms(**sms_query)
    if isinstance(rcode, int):
         logging.error('Retrieve message list failed with error code: ' + str(rcode))
         ret = False

    #if alert_name or alert_description in rcode in loop then ret = rcode[index][to][message]
    for record in rcode['records']:
        if alert_name in record['subject'] or alert_description in record['subject']:
            garbage_string = 'Test SMS using a RingCentral Developer account - '
            print('ring_central/get_sms: Alert name "{}" or description "{}" found!'.format(alert_name, alert_description))
            print('ring_central/get_sms: SMS body is "{}"'.format(record['subject'].replace(garbage_string, '')))
            ret = True
            break

    if not ret:
        print('SMS notification matching Alert name "{}" or description "{}" not found'.format(alert_name, alert_description))

    return ret



# pytests
#==============================================
class Test_AlertNotification:

    @pytest.mark.skip #SMS has been disabled on testing
    #policy alerts will no longer generate SMS notifications
    @pytest.mark.skipif(os.environ["NODE_ENV"] not in ["testing"], reason="Alert SMS and email test only available in testing environment")
    @pytest.mark.parametrize("medium", ["SMS"] )#SKIPPED BECAUSE KEEP FAILING, "email"]) # O365 no longer support python2.7 now require OAuth2.0 with Microsoft app

    def test_alert_notify(self, generate_alert, medium):
        rcode = True

        alert_name = generate_alert['name']
        alert_description = generate_alert['description']

        sms_auth = {
                'username': ring_central_account,
                'extension': ring_central_ext,
                'password': ring_central_pwd,
                'auth': ring_central_auth
            }

        if medium == 'email':
            rcode = rcode and received_email(alert_name, alert_description)
        elif medium == 'SMS':
            # rcode = rcode and received_sms(alert_name, alert_description, browser) #old code for TextNow
            ring_central = RingCentral(env['ring_central_api'], **sms_auth)
            rcode = rcode and received_sms(alert_name, alert_description, ring_central)

        assert True == rcode
