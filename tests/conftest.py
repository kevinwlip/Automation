# content of conftest.py
import sys
import os
import ast
import pytest
import pdb
import time
import shutil
import random
import copy
import re

try:
    nodeEnv = os.environ['NODE_ENV']
    zbathome = os.environ['ZBAT_HOME']
    print ("ZBAT_HOME is %s" % zbathome)
except:
    print ('Test cannot run.  Please export NODE_ENV.')
    print ('Test cannot run.  Please export ZBAT_HOME.')
    sys.exit()

if zbathome+'lib' not in sys.path:
    sys.path.append(zbathome+'lib')

from common.zbConfig import defaultEnv

#================================
# Setting up default parameters
#================================
env = defaultEnv()
ui_portal = env["uiportal"]
if not ui_portal: print ('UI portal value not set in zbCommon.py'); sys.exit()
seleniumhost = env["remoteSeleniumServer"]
username = env["username"]
password = env["password"]
comparestrict = env["comparestrict"]
tenantid = env["tenantid"]
siteTest = env["siteTest"]

# global variables
br = None
GLOBAL_PARAMS = {
    "url": ui_portal,
    "host": seleniumhost,
    "username": username, 
    "password": password,
    "comparestrict": comparestrict
}

NUMBER_RETRIES = 0
DELAY_SECONDS = 5
SCREENSHOT_ON_FAIL = True
TG_HOST = env["trafficGenHost"]
TG_UNAME = env["trafficGenUname"]
TG_PWD = env["trafficGenPwd"]
TG_PORT = env["trafficGenPort"]
TG_INTF1 = env["trafficGenPort1"]
TG_INTF2 = env["trafficGenPort2"]
REDIS_HOST = env["redisHost"]
REDIS_TESTING_TENANT = os.environ['ZBAT_TENANT_INTERNAL_ID']
ALERT_NOTIFY_POLICY_ID = '5a26f42fc8272f0b00c5ef2f'
BLACKLIST_POLICY_ID = '5a26f11ed28fae0f000daba0'
WHITELIST_POLICY_ID = '5a26f169c8272f0b00c5ef1a'
if 'staging' in nodeEnv:
    ALERT_NOTIFY_POLICY_ID = '5a26f45b9849c50d000b857e'
    BLACKLIST_POLICY_ID = '5a26f27162a0720b00f89bee'
    WHITELIST_POLICY_ID = '5a26f2b762a0720b00f89bef'

#=============================
# Pytest command line input params
#==============================
def pytest_addoption(parser):
    parser.addoption("--uiportal", action="store", default=None,
        help = "ZingBox UI Testing URL. No tenantid is included or needed. Like testing-soho.zingbox.com")

    parser.addoption("--sitetest", action="store", default=None,
        help="ZingBox URL.  For API example demo.zingbox.com.  For UI example dev004.cloud.zingbox.com.  Test will only be run on this site.")

    parser.addoption("--sitecompare", action="store", default=None,
        help="ZingBox URL to compare against.  --sitecompare must be use in conjunction with --sitetest and --sitetenantid")

    parser.addoption("--sitetenantid", action="store", default=None,
        help="Enter sitetenantid.  For example healtcare.")

    parser.addoption("--loginuser", action="store", default=None,
        help="For UI test, passing in loginuser will login as this username")

    parser.addoption("--loginpwd", action="store", default=None,
        help="For UI test, passing in loginpwd will login with this password")

    parser.addoption("--remoteserver", action="store", default=None,
        help="Indicate selenium server to run test on.  Useful to indicate local selenium like 127.0.0.1:4444")

    parser.addoption("--forceall", action="store_true", default=False,
        help="If force to have all tests, the system will check API, Kibana and Kafka regardless of the individual results.")

    
#======================
# Fixtures
#=======================
# fixture to run first before any test
@pytest.fixture(scope="session", autouse=True)
def runfirst(request):
    # delete all screenshots files from artifacts dir
    time.sleep(random.randint(0,9))
    folder = zbathome+'artifacts/'
    folder_download = zbathome+'artifacts/download/'
    folder_report = ['CMMS', 'Summary', 'Connectivity', 'New Device']

    path = zbathome+'artifacts/'

    for report in folder_report:
        if os.path.isdir(folder+report):
            for file in os.listdir(folder+report):
                file_path = os.path.join(folder+report, file)
                try:
                    if os.path.isfile(file_path):
                        os.unlink(file_path)
                except Exception as e:
                    print(e)
                # pass

    if not os.path.exists(folder):
        try:
            os.makedirs(folder)
        except:
            pass
    if not os.path.exists(folder_download):
        try:
            os.makedirs(folder_download)
        except:
            pass
    else:    
        for thefile in os.listdir(folder):
            filepath = os.path.join(folder, thefile)
            try:
                if os.path.isfile(filepath):
                    os.unlink(filepath)
                #elif os.path.isdir(filepath): shutil.rmtree(filepath)
            except Exception as e:
                pass


@pytest.fixture(scope="module")
def uiportal(request):
    return request.config.getoption("--uiportal")


# handle command line passed in parametr --sitetest.  This is used in UI or API test to overide the site that you want to test.
@pytest.fixture(scope="module")
def sitetest(request):
    return request.config.getoption("--sitetest")

# handle command line passed in parametr --sitecompare.  This is used in UI or API test to overide the compare site that you want to test against.
@pytest.fixture(scope="module")
def sitecompare(request):
    return request.config.getoption("--sitecompare")

# handle command line passed in parametr --sitetenantid.  This is used in UI or API test to overide the tenantid that you want to test.
@pytest.fixture(scope="module")
def sitetenantid(request):
    return request.config.getoption("--sitetenantid")

# handle command line passed in parameter --username, pass in specific username for UI test
@pytest.fixture(scope="module")
def loginuser(request):
    return request.config.getoption("--loginuser")

# handle command line passed in parameter --loginpwd, pass in specific loginpwd for UI test
@pytest.fixture(scope="module")
def loginpwd(request):
    return request.config.getoption("--loginpwd")

# handle command line passed in parameter --remoteserver to indicate the selenium server you want to pass in
@pytest.fixture(scope="module")
def remoteserver(request):
    return request.config.getoption("--remoteserver")

# handle command line passed in parameter --forceall.  This is used for rule_engine_1 and rule_engine_2 tests
# where you want to force whitebox check of things like Kibana, Redis, Kafka
@pytest.fixture(scope="module")
def forceall(request):
    return True if request.config.getoption("--forceall") else False

#handle building up default parameters structure
@pytest.fixture(scope="module", params=['chrome'])
def browser_payload(request, remoteserver, sitetest):
    kwargs = copy.deepcopy(GLOBAL_PARAMS)
    kwargs['browser'] = request.param

    if remoteserver: kwargs['host'] = remoteserver
    if sitetest: kwargs['url'] = sitetest
    return kwargs

@pytest.fixture(scope="module", params=['internet explorer', 'firefox', 'chrome', 'edge', 'chromeipad'])
def browser_payload_smoke(request, remoteserver, sitetest, sitetenantid, loginuser, loginpwd):
    kwargs = copy.deepcopy(GLOBAL_PARAMS)
    kwargs['browser'] = request.param

    if remoteserver: kwargs['host'] = remoteserver
    if sitetest: 
        # if user command line input param for sitetest is not in format of https://testing.zingbox.com/login?tenant=testing-soho
        #     then build up that string based on zbConfig config param of siteTest and tenantid
        if 'http' not in sitetest:
            sitetest = 'https://'+sitetest+'/login'
        if 'tenantid=' not in sitetest:
            if sitetenantid:
                sitetest = sitetest+'?tenantid='+sitetenantid
            else:
                sitetest = sitetest+'?tenantid='+tenantid
        kwargs['url'] = sitetest
    if loginuser: kwargs['username'] = loginuser
    if loginpwd: kwargs['password'] = loginpwd
    return kwargs


@pytest.fixture(scope="module")
def policyTestsConfig():
    config = {}
    config['trafficGenHost'] = TG_HOST
    config['trafficGenUname'] = TG_UNAME
    config['trafficGenPwd'] = TG_PWD
    config['trafficGenPort'] = TG_PORT
    config['redisHost'] = REDIS_HOST
    config['alertNotifyPolicyId'] = ALERT_NOTIFY_POLICY_ID
    config['blacklistPolicyId'] = BLACKLIST_POLICY_ID
    config['whitelistPolicyId'] = WHITELIST_POLICY_ID
    return config

# handle create selenium object
@pytest.fixture(scope="module")
def browser_factory(browser_payload, request):
    def create_browser(class_name, config={}, custom_payload={}, single_br=True):
        global br
        payload = browser_payload.copy()
        payload.update(custom_payload)
        if br and single_br:
            tear_down()
        try:
            br = class_name(**payload)
        except Exception as err:
            print('conftest.py/create_browser: Exception caught during browser initialization. {}'.format(err))
            print (class_name)
            assert 0
        return {"selenium":br, "config":config}
    def tear_down():
        global br
        # tearing down
        print ("All test finished.  Tearing down {}".format(br))
        if br:
            br.close()
            br = None
    request.addfinalizer(tear_down)
    return create_browser

'''
@pytest.fixture(scope=module)
def get_driver(request):
    """Parameters required to start UI test cases"""
    # account = request.config.getoption("--account")
    browser = request.config.getoption("--browser")
    # stackname = request.config.getoption("--stack")
    #  customername = request.config.getoption("--customer")
    # ui_automation = request.config.getoption("--ui")

    environment_params = zbConfig.defaultEnv()
    # print("environment_params: {}".format(environment_params))

    # webdriver_endpoint = f"http://{environment_params['onprem_host']}:4444/wd/hub"
    webdriver_endpoint = f"http://{environment_params['siteTest']}"
    url = environment_params["siteTest"]
    if browser == 'chrome':
        options = webdriver.ChromeOptions()
        options.add_argument("--start-maximized")
        browser = webdriver.Chrome(options=options)
        browser.set_window_size(1440, 900)
        browser.get(webdriver_endpoint)
        # browser.get(url)
        return browser
    elif browser == 'remote':
        browser = webdriver.Remote(command_executor=webdriver_endpoint,
                                   desired_capabilities=DesiredCapabilities.CHROME)
        browser.set_window_size(1440, 900)
        browser.get(url)
        return browser
    elif browser == 'firefox':
        browser = webdriver.Remote(command_executor=webdriver_endpoint,
                                   desired_capabilities=DesiredCapabilities.FIREFOX)
        browser.set_window_size(1440, 900)
        browser.get(url)
        return browser
    else:
        logging.error("Chrome is the only browser supported as of now")
'''


@pytest.fixture(scope="module")
def browser_factory_smoke(browser_payload_smoke, request):
    def create_browser(class_name, config={}, custom_payload={}):
        global br
        payload = browser_payload_smoke.copy()
        payload.update(custom_payload)
        if br:
            tear_down()
        try:
            br = class_name(**payload)
        except Exception as err:
            print('conftest.py/create_browser: Exception caught during browser initialization. {}'.format(err))
            print (class_name)
            assert 0
        return {"selenium":br, "config":config}
    def tear_down():
        global br
        # tearing down
        print ("All test finished.  Tearing down {}".format(br))
        if br:
            br.close()
            br = None
    request.addfinalizer(tear_down)
    return create_browser

# handle create selenium object for bdd tests
@pytest.fixture(scope="module")
def browser_factory_bdd(request, remoteserver, sitetest, params = 'chrome'):
    request.param = params
    kwargs = copy.deepcopy(GLOBAL_PARAMS)
    kwargs['browser'] = request.param

    if remoteserver: kwargs['host'] = remoteserver
    if sitetest: kwargs['url'] = sitetest
    
    not_needed_in_guardian = {'username', 'password', 'comparestrict'}
    for item in not_needed_in_guardian:
        kwargs.pop(item, None) 

    def create_browser(class_name, config={}, custom_payload={}):
        global br
        payload = kwargs.copy()
        payload.update(custom_payload)
        if br:
            tear_down()
        try:
            br = class_name(**payload)
        except Exception as err:
            print('conftest.py/create_browser: Exception caught during browser initialization. {}'.format(err))
            print (class_name)
            assert 0
        return br

    def tear_down():
        global br
        # tearing down
        print ("All test finished.  Tearing down {}".format(br))
        if br:
            br.close()
            br = None

    request.addfinalizer(tear_down)
    return create_browser


#=================================
# Dynamic marking tests based on test name
#==================================
def pytest_collection_modifyitems(items):
    for item in items:
        # browser
        if "chrome" in item.nodeid:
            item.add_marker(pytest.mark.chrome)
        if "firefox" in item.nodeid:
            item.add_marker(pytest.mark.firefox)
        if "internet explorer" in item.nodeid:
            item.add_marker(pytest.mark.ie)
        if "edge" in item.nodeid:
            item.add_marker(pytest.mark.edge)
        if "chromeipad" in item.nodeid:
            item.add_marker(pytest.mark.chromeipad)
        
        '''
        # Disable these markings for now, it's not used.
        # dashboard markings
        if re.search('site', item.nodeid, re.IGNORECASE):
            item.add_marker(pytest.mark.site)
        if re.search('tenant', item.nodeid, re.IGNORECASE):
            item.add_marker(pytest.mark.tenant)
        if re.search('inspector', item.nodeid, re.IGNORECASE):
            item.add_marker(pytest.mark.inspector)
        if re.search('enforcement', item.nodeid, re.IGNORECASE):
            item.add_marker(pytest.mark.enforcement)
            item.add_marker(pytest.mark.integration)
        if re.search('AssetManagement', item.nodeid, re.IGNORECASE):
            item.add_marker(pytest.mark.integration)
        if re.search('aims', item.nodeid, re.IGNORECASE):
            item.add_marker(pytest.mark.aims)
            item.add_marker(pytest.mark.integration)
        if re.search('siem', item.nodeid, re.IGNORECASE):
            item.add_marker(pytest.mark.siem)
            item.add_marker(pytest.mark.integration)
        if re.search('connectiv', item.nodeid, re.IGNORECASE):
            item.add_marker(pytest.mark.connectiv)
            item.add_marker(pytest.mark.integration)
        if re.search('ciscoise', item.nodeid, re.IGNORECASE):
            item.add_marker(pytest.mark.ise)
            item.add_marker(pytest.mark.integration)
        if re.search('servicenow', item.nodeid, re.IGNORECASE):
            item.add_marker(pytest.mark.servicenow)
            item.add_marker(pytest.mark.integration)
        if re.search('notify', item.nodeid, re.IGNORECASE):
            item.add_marker(pytest.mark.notify)
        if re.search('email', item.nodeid, re.IGNORECASE):
            item.add_marker(pytest.mark.email)
        if re.search('sms', item.nodeid, re.IGNORECASE):
            item.add_marker(pytest.mark.sms)
        if re.search('alert', item.nodeid, re.IGNORECASE):
            item.add_marker(pytest.mark.alert)
        if re.search('action', item.nodeid, re.IGNORECASE):
            item.add_marker(pytest.mark.action)
        if re.search('export', item.nodeid, re.IGNORECASE):
            item.add_marker(pytest.mark.export)
        if re.search('dashboard', item.nodeid, re.IGNORECASE):
            item.add_marker(pytest.mark.dashboard)
        if re.search('OTDashboard', item.nodeid, re.IGNORECASE):
            item.add_marker(pytest.mark.ot)
        if re.search('monitor', item.nodeid, re.IGNORECASE):
            item.add_marker(pytest.mark.monitor)
        if re.search('device', item.nodeid, re.IGNORECASE):
            item.add_marker(pytest.mark.device)
        if re.search('application', item.nodeid, re.IGNORECASE):
            item.add_marker(pytest.mark.application)
        if re.search('profile', item.nodeid, re.IGNORECASE):
            item.add_marker(pytest.mark.profile)
        if re.search('inventory', item.nodeid, re.IGNORECASE):
            item.add_marker(pytest.mark.inventory)
        if re.search('list', item.nodeid, re.IGNORECASE):
            item.add_marker(pytest.mark.list)
        if re.search('summary', item.nodeid, re.IGNORECASE):
            item.add_marker(pytest.mark.summary)
        if re.search('detail', item.nodeid, re.IGNORECASE):
            item.add_marker(pytest.mark.detail)
        if re.search('administration', item.nodeid, re.IGNORECASE):
            item.add_marker(pytest.mark.administration)
        if re.search('log', item.nodeid, re.IGNORECASE):
            item.add_marker(pytest.mark.log)
        if re.search('audit', item.nodeid, re.IGNORECASE):
            item.add_marker(pytest.mark.audit)
        if re.search('system', item.nodeid, re.IGNORECASE):
            item.add_marker(pytest.mark.system)
        if re.search('traffic', item.nodeid, re.IGNORECASE):
            item.add_marker(pytest.mark.traffic)
        if re.search('series', item.nodeid, re.IGNORECASE):
            item.add_marker(pytest.mark.series)
        if re.search('report', item.nodeid, re.IGNORECASE):
            item.add_marker(pytest.mark.report)
        if re.search('side_navigation', item.nodeid, re.IGNORECASE):
            item.add_marker(pytest.mark.sidenavigation)
        if re.search('tooltip|tool_tip', item.nodeid, re.IGNORECASE):
            item.add_marker(pytest.mark.tooltip)
        if re.search('password', item.nodeid, re.IGNORECASE):
            item.add_marker(pytest.mark.password)
        if re.search('login', item.nodeid, re.IGNORECASE):
            item.add_marker(pytest.mark.login)
        if re.search('widget', item.nodeid, re.IGNORECASE):
            item.add_marker(pytest.mark.widget)

        # network marking
        if re.search('vpn', item.nodeid, re.IGNORECASE):
            item.add_marker(pytest.mark.vpn)
        if re.search('network', item.nodeid, re.IGNORECASE):
            item.add_marker(pytest.mark.network)
        if re.search('vlan', item.nodeid, re.IGNORECASE):
            item.add_marker(pytest.mark.vlan)
        if re.search('subnet', item.nodeid, re.IGNORECASE):
            item.add_marker(pytest.mark.subnet)
        if re.search('session', item.nodeid, re.IGNORECASE):
            item.add_marker(pytest.mark.session)
        if re.search('connect', item.nodeid, re.IGNORECASE):
            item.add_marker(pytest.mark.connect)

        # iot marking
        if re.search('iot', item.nodeid, re.IGNORECASE):
            if re.search('noniot', item.nodeid, re.IGNORECASE):
                item.add_marker(pytest.mark.noniot)
            else:
                item.add_marker(pytest.mark.iot)

        # operation marking
        if re.search('api', item.nodeid, re.IGNORECASE):
            item.add_marker(pytest.mark.api)
        if re.search('config', item.nodeid, re.IGNORECASE):
            item.add_marker(pytest.mark.config)
        if re.search('edit', item.nodeid, re.IGNORECASE):
            item.add_marker(pytest.mark.edit)
        if re.search('search', item.nodeid, re.IGNORECASE):
            item.add_marker(pytest.mark.search)

        # portal 
        if re.search('mssp', item.nodeid, re.IGNORECASE):
            item.add_marker(pytest.mark.mssp)
        if re.search('soc', item.nodeid, re.IGNORECASE):
            item.add_marker(pytest.mark.soc)

        # onboarding
        if re.search('onboard', item.nodeid, re.IGNORECASE):
            item.add_marker(pytest.mark.onboard)
        if re.search('user', item.nodeid, re.IGNORECASE):
            item.add_marker(pytest.mark.user)
        if re.search('distributor', item.nodeid, re.IGNORECASE):
            item.add_marker(pytest.mark.distributor)
        if re.search('reseller', item.nodeid, re.IGNORECASE):
            item.add_marker(pytest.mark.reseller)
        if re.search('customer', item.nodeid, re.IGNORECASE):
            item.add_marker(pytest.mark.customer)
        if re.search('account', item.nodeid, re.IGNORECASE):
            item.add_marker(pytest.mark.account)

        # policy, threat
        if re.search('policies|policy', item.nodeid, re.IGNORECASE):
            item.add_marker(pytest.mark.policy)
            item.add_marker(pytest.mark.ruleengine1)
            item.add_marker(pytest.mark.ruleengine)
        if re.search('blacklist|whitelist', item.nodeid, re.IGNORECASE):
            item.add_marker(pytest.mark.policy)
        if re.search('threat', item.nodeid, re.IGNORECASE):
            item.add_marker(pytest.mark.threat)
            item.add_marker(pytest.mark.ruleengine2)
            item.add_marker(pytest.mark.ruleengine)
        if re.search('mlvisualization|machine|learning|anomaly', item.nodeid, re.IGNORECASE):
            item.add_marker(pytest.mark.ml)
        if re.search('risk', item.nodeid, re.IGNORECASE):
            item.add_marker(pytest.mark.risk)

        # test type
        if re.search('integration', item.nodeid, re.IGNORECASE):
            item.add_marker(pytest.mark.integration)
        if re.search('smoke', item.nodeid, re.IGNORECASE):
            item.add_marker(pytest.mark.smoke)
        if re.search('perf', item.nodeid, re.IGNORECASE):
            item.add_marker(pytest.mark.perf)
        if re.search('scale', item.nodeid, re.IGNORECASE):
            item.add_marker(pytest.mark.scale)
        if re.search('latency', item.nodeid, re.IGNORECASE):
            item.add_marker(pytest.mark.latency)
        if re.search('needle', item.nodeid, re.IGNORECASE):
            item.add_marker(pytest.mark.needle)

        # time
        if re.search('minute', item.nodeid, re.IGNORECASE):
            item.add_marker(pytest.mark.minute)
        if re.search('day', item.nodeid, re.IGNORECASE):
            item.add_marker(pytest.mark.day)
        if re.search('month', item.nodeid, re.IGNORECASE):
            item.add_marker(pytest.mark.month)
        if re.search('year', item.nodeid, re.IGNORECASE):
            item.add_marker(pytest.mark.year)
        if re.search('all', item.nodeid, re.IGNORECASE):
            item.add_marker(pytest.mark.all)
        '''
