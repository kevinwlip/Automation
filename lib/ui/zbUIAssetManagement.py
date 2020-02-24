

from common.zbSelenium import zbSelenium
from urllib.parse import urlparse
from ui.login.zbUILoginCore import Login
from ui.zbUIShared import clickEachTimerange, waitLoadProgressDone, waitSeriesGraphDone, verifyDataTimerange
from common.zbCommon import validateDataNotEmpty
from selenium.webdriver.common.keys import Keys
from zbAPI import zbAPI, Ops
import pdb, time, json


# Global CSS for Administration > Asset Management page
CSS_ASSET_MANAGE_SWITCH = "div.md-thumb"
CSS_CARD = "md-card[class*= tint]"
CSS_VENDOR_LABEL = "md-select[ng-model='assetManagementCtrl.assetConfig.provider']"
CSS_SELECT_VENDOR = "md-select[placeholder='Select vendor'] >  md-select-value"
CSS_AIMS_SERVER_INPUT = ".asset-management input#host"
CSS_AUTH_TOKEN_INPUT = ".asset-management input#auth_token"
CSS_TESTING_SOHO_SELECT = "md-option[value='564D29485CF37A7869FCF2090864B53F']"
CSS_CONNECT_BUTTON = "button[name='Test connect']"
CSS_CONNECTED_ICON = "span.connected-check"
CSS_SAVE_ASSET_CONFIG = "button[type='submit']"
CSS_CONFIRM_ASSET_CONFIG = "button.confirm"
CSS_SAVE_SERVICENOW = ".md-button.md-primary[type='button']"

CSS_MAIN_SWITCH_ON = 'md-switch[ng-model="assetManagementCtrl.assetConfig.enabled"][aria-checked="true"]'
CSS_MAIN_SWITCH_OFF = 'md-switch[ng-model="assetManagementCtrl.assetConfig.enabled"][aria-checked="false"]'

CSS_AIMS = ".vendor-icon-aims"
CSS_CONNECTIV = ".vendor-icon-connectiv"
CSS_NUVOLO = ".vendor-icon-nuvolo"
CSS_SERVICENOW = "[src='/static/images/asset-management/servicenowIcon.png']"

CSS_SWITCH_VENDOR = "[ng-click='assetManagementCtrl.switchVendor()']"
CSS_INSPECTOR_DROPDOWN = "md-select.inspector-select"
CSS_INSPECTORS = 'md-option[ng-repeat="inspector in assetManagementCtrl.inspectors"]'

CSS_CONNECTIV_USERNAME = ".asset-management input#username"
CSS_CONNECTIV_PWD = ".asset-management input#password"
CSS_CONNECTIV_CLIENT_ID = 'input[name="client_id"]'
CSS_CONNECTIV_CLIENT_SECRET = 'input[name="clientsecret"]'
CSS_CONNECTIV_CLIENT_URL = 'input[name="desturl"]'

CSS_NUVOLO_USERNAME = ".asset-management #username"
CSS_NUVOLO_PWD = ".asset-management #password"
CSS_NUVOLO_KEY = ".asset-management [name='source_key']"
CSS_NUVOLO_URL = ".asset-management [name='assetManagementCtrl.detailForm'] [name='desturl']"

CSS_SERVICENOW_EDIT = ".config-page .material-icons"
CSS_SERVICENOW_URL = ".asset-management .md-input[placeholder=' Your ServiceNow URL']"
CSS_SERVICENOW_USERNAME = ".asset-management .md-input[placeholder='Your ERS (External RESTful Services) Endpoint']"

CSS_SERVICENOW_PWD = ".asset-management .md-input[placeholder='Your ERS Password']"
CSS_SERVICENOW_TABLE = ".asset-management .md-input[placeholder='Enter Table']"
CSS_SERVICENOW_CATEGORY = ".asset-management .md-input[placeholder='Enter Category']"
CSS_SERVICENOW_PROFILE = ".asset-management .md-input[placeholder='Enter Profile']"

req = Ops()

def enableAIMS(browserobj, **aimsconfig):
	server = aimsconfig["server"]
	token = aimsconfig["token"]
	inspector = aimsconfig["inspector"]
	configSystem(browserobj, CSS_AIMS)
	_inputAIMSServer(browserobj, server, token)
	_selectInspector(browserobj, inspector)
	browserobj.click(selector=CSS_SAVE_ASSET_CONFIG)
	browserobj.click(selector=CSS_CONFIRM_ASSET_CONFIG)

def enableConnectiv(browserobj, **connectivconfig):
	connectiv_uname = connectivconfig["connectiv_uname"]
	connectiv_pwd = connectivconfig["connectiv_pwd"]
	client_id = connectivconfig["connectiv_client_id"]
	client_secret = connectivconfig["connectiv_client_secret"]
	client_url = connectivconfig["connectiv_client_url"]
	configSystem(browserobj, CSS_CONNECTIV)
	_inputConnectivUserInfo(browserobj, connectiv_uname, connectiv_pwd)
	_inputConnectivClientInfo(browserobj, client_id, client_secret, client_url)
	browserobj.click(selector=CSS_SAVE_ASSET_CONFIG)
	browserobj.click(selector=CSS_CONFIRM_ASSET_CONFIG)

def enableNuvolo(browserobj, **nuvoloconfig):
	nuvolo_uname = nuvoloconfig["nuvolo_uname"]
	nuvolo_pwd = nuvoloconfig["nuvolo_pwd"]
	nuvolo_key = nuvoloconfig["nuvolo_key"]
	nuvolo_url = nuvoloconfig["nuvolo_url"]
	configSystem(browserobj, CSS_NUVOLO)
	_inputNuvoloUserInfo(browserobj, nuvolo_uname, nuvolo_pwd)
	_inputNuvoloClientInfo(browserobj, nuvolo_key, nuvolo_url)
	browserobj.click(selector=CSS_SAVE_ASSET_CONFIG)
	browserobj.click(selector=CSS_CONFIRM_ASSET_CONFIG)

def enableServiceNow(browserobj, **servicenowconfig):
	servicenow_url = servicenowconfig["servicenow_url"]
	servicenow_uname = servicenowconfig["servicenow_uname"]
	servicenow_pwd = servicenowconfig["servicenow_pwd"]
	servicenow_table = servicenowconfig["servicenow_table"]
	servicenow_category = servicenowconfig["servicenow_category"]
	servicenow_profile = servicenowconfig["servicenow_profile"]
	configServiceNow(browserobj)
	_inputServiceNowUserInfo(browserobj, servicenow_url, servicenow_uname, servicenow_pwd)
	_inputServiceNowTableInfo(browserobj, servicenow_table, servicenow_category, servicenow_profile)
	browserobj.click(selector=CSS_SAVE_SERVICENOW)

def configSystem(browserobj, vendorCSS):
	# If I see 'Switch Vendor', click it
	switchvendor = browserobj.findSingleCSS(selector=CSS_SWITCH_VENDOR, timeout=3)
	if switchvendor:
		switchvendor.click()
	# If I see the specified vendor icon, click it
	vendorCSS = browserobj.findSingleCSS(selector=vendorCSS, timeout=3)
	if vendorCSS:
		vendorCSS.click()

def configServiceNow(browserobj):
	servicenowedit = browserobj.findSingleCSS(selector=CSS_SERVICENOW_EDIT, timeout=3)
	if servicenowedit:
		servicenowedit.click()

def _inputAIMSServer(browserobj, serverIP, serverToken):
	if type(serverIP) != str or type(serverToken) != str:
		raise Exception('zbUIAssetManagement/inputAIMSServer: serverIP and serverToken must be in str type.')
	sendKey(browserobj, CSS_AIMS_SERVER_INPUT, serverIP)
	sendKey(browserobj, CSS_AUTH_TOKEN_INPUT, serverToken)

def _selectInspector(browserobj, inspector):
	browserobj.click(selector=CSS_INSPECTOR_DROPDOWN)
	rcode = browserobj.findMultiCSS(selector=CSS_INSPECTORS, waittype="visibility")
	if not rcode:
		raise Exception("zbUIAssetManagement/selectInspector: Asset Management cannot find inspector " + str(inspector))
	for insp in rcode:
		if inspector.strip() in insp.text.strip():
			insp.click()
			time.sleep(1)
			return
	raise Exception("zbUIAssetManagement/selectInspector: Unable to find target inspector " + str(inspector))

def _inputConnectivUserInfo(browserobj, connectiv_username, connectiv_pwd):
	if type(connectiv_username) != str or type(connectiv_pwd) != str:
		raise Exception('zbUIAssetManagement/inputConnectivUserInfo: username and password must be in str type.')
	sendKey(browserobj, CSS_CONNECTIV_USERNAME, connectiv_username)
	sendKey(browserobj, CSS_CONNECTIV_PWD, connectiv_pwd)

def _inputConnectivClientInfo(browserobj, client_id, client_secret, client_url):
	if type(client_id) != str or type(client_secret) != str or type(client_url) != str:
		raise Exception('zbUIAssetManagement/inputConnectivClientInfo: client_id, secret and url must be in str type.')
	sendKey(browserobj, CSS_CONNECTIV_CLIENT_ID, client_id)
	sendKey(browserobj, CSS_CONNECTIV_CLIENT_SECRET, client_secret)
	sendKey(browserobj, CSS_CONNECTIV_CLIENT_URL, client_url)

def _inputNuvoloUserInfo(browserobj, nuvolo_username, nuvolo_pwd):
	if type(nuvolo_username) != str or type(nuvolo_pwd) != str:
		raise Exception('zbUIAssetManagement/inputNuvoloUserInfo: username and password must be in str type.')
	sendKey(browserobj, CSS_NUVOLO_USERNAME, nuvolo_username)
	sendKey(browserobj, CSS_NUVOLO_PWD, nuvolo_pwd)

def _inputNuvoloClientInfo(browserobj, nuvolo_key, nuvolo_url):
	if type(nuvolo_key) != str or type(nuvolo_url) != str:
		raise Exception('zbUIAssetManagement/inputNuvoloClientInfo: key and url must be in str type.')
	sendKey(browserobj, CSS_NUVOLO_KEY, nuvolo_key)
	sendKey(browserobj, CSS_NUVOLO_URL, nuvolo_url)

def _inputServiceNowUserInfo(browserobj, servicenow_url, servicenow_uname, servicenow_pwd):
	if type(servicenow_url) != str or type(servicenow_uname) != str or type(servicenow_pwd) != str:
		raise Exception('zbUIAssetManagement/inputConnectivUserInfo: username and password must be in str type.')
	sendKey(browserobj, CSS_SERVICENOW_URL, servicenow_url)
	sendKey(browserobj, CSS_SERVICENOW_USERNAME, servicenow_uname)
	sendKey(browserobj, CSS_SERVICENOW_PWD, servicenow_pwd)

def _inputServiceNowTableInfo(browserobj, servicenow_table, servicenow_category, servicenow_profile):
	if type(servicenow_table) != str or type(servicenow_category) != str or type(servicenow_profile) != str:
		raise Exception('zbUIAssetManagement/inputConnectivUserInfo: username and password must be in str type.')
	sendKey(browserobj, CSS_SERVICENOW_TABLE, servicenow_table)
	sendKey(browserobj, CSS_SERVICENOW_CATEGORY, servicenow_category)
	sendKey(browserobj, CSS_SERVICENOW_PROFILE, servicenow_profile)

def sendKey(browserobj, selector, text):
	_input = browserobj.findSingleCSS(selector=selector)
	if not _input:
		raise Exception('zbUIAssetManagement/sendKey: cannot find input {}.'.format(selector))
	_input.send_keys(Keys.DELETE)
	_input.clear()
	_input.send_keys(text)



class AssetManagement():

	def __init__(self, **kwargs):
		self.params = kwargs
		self.selenium = Login(**kwargs).login()

		rcode = self.selenium.getURL(kwargs["url"]+'/')
		if rcode: waitLoadProgressDone(self.selenium)

	def verifyAssetManagement(self, **kwargs):
		self.gotoIntegrationConfigurations()		
		rcode = self.configAddAIMS(**kwargs)
		return rcode

	def gotoIntegrationConfigurations(self, integrations_url, system_type, **kwargs):
		req.delete_request(kwargs['tenantid'], system_type, kwargs['site'])

		url = urlparse(self.params["url"])
		rcode = self.selenium.getURL(url.scheme+'://'+url.netloc+integrations_url)

	def configEnableAIMS(self):
		# check if switch is off, then turn on
		kwargs = {"selector":CSS_MAIN_SWITCH_OFF, "waittype":"visibility", "timeout":3}
		rcode = self.selenium.click(**kwargs)

		# save
		self.configSaveAIMS()

		# check to switch is on
		self.gotoIntegrationConfigurations()
		kwargs = {"selector":CSS_MAIN_SWITCH_ON, "waittype":"visibility", "timeout":3}
		rcode = self.selenium.findSingleCSS(**kwargs)
		if not rcode:
			print("Fail to enable AIMS")
			return False
		return True

	def configDisableAIMS(self):
		# check if switch is on, then turn off
		kwargs = {"selector":CSS_MAIN_SWITCH_ON, "waittype":"visibility", "timeout":3}
		rcode = self.selenium.click(**kwargs)

		# save
		self.configSaveAIMS()

		# check to switch is off
		self.gotoIntegrationConfigurations()
		kwargs = {"selector":CSS_MAIN_SWITCH_OFF, "waittype":"visibility", "timeout":3}
		rcode = self.selenium.findSingleCSS(**kwargs)
		if not rcode:
			print("Fail to disable AIMS")
			return False
		return True

	def configSaveAIMS(self):
		kwargs = {"selector":CSS_SAVE_ASSET_CONFIG, "waittype":"visibility", "timeout":3}
		rcode = self.selenium.click(**kwargs)
		time.sleep(2)
		return True

	def configAddAIMS(self, **aimsconfig):
		timeout = 3

		inputs = aimsconfig

		required_params = ['server', 'token', 'inspector']
		for param in required_params:
			if param not in inputs:
				print(('Parameter {0} is not in aimsconfig, please check for the configuration passed in {1}'.format(param, aimsconfig)))
				return False
		
		self.configEnableAIMS()

		# configure server
		server = inputs["server"]
		kwargs = {"selector":CSS_AIMS_SERVER_INPUT, "waittype":"visibility", "timeout":timeout}
		rcode = self.selenium.findSingleCSS(**kwargs)
		rcode.clear()
		rcode.send_keys(server)
		time.sleep(1)

		# configure token
		token = inputs["token"]
		kwargs = {"selector":CSS_AUTH_TOKEN_INPUT, "waittype":"visibility", "timeout":timeout}
		rcode = self.selenium.click(**kwargs)
		rcode = self.selenium.findSingleCSS(**kwargs)
		rcode.clear()
		rcode.send_keys(token)
		time.sleep(1)
		
		# configure inspector
		inspector = inputs["inspector"]
		kwargs = {"selector":CSS_INSPECTOR_DROPDOWN, "waittype":"visibility", "timeout":timeout}
		rcode = self.selenium.click(**kwargs)
		kwargs = {"selector":CSS_INSPECTORS, "waittype":"visibility", "timeout":timeout}
		rcode = self.selenium.findMultiCSS(**kwargs)
		if not rcode:
			print("Asset Management cannot find inspector "+str(inspector))
			return False
		for insp in rcode:
			if inspector.strip() in insp.text.strip():
				insp.click()
				time.sleep(1)
				break

		# test connection
		kwargs = {"selector":CSS_CONNECT_BUTTON, "waittype":"visibility", "timeout":timeout}
		rcode = self.selenium.click(**kwargs)

		kwargs = {"selector":CSS_CONNECTED_ICON, "waittype":"visibility", "timeout":timeout}
		rcode = self.selenium.waitCSS(**kwargs)
		if not rcode:
			print("AIMS fail connection test")
			return False

		# save config
		kwargs = {"selector":CSS_SAVE_ASSET_CONFIG, "waittype":"visibility", "timeout":timeout}
		rcode = self.selenium.click(**kwargs)
		time.sleep(1)

		return True

	def verifyAIMS(self, **aimsconfig):
		aims_path = '/administration/integrations/assetmanagement'
		self.gotoIntegrationConfigurations(aims_path, system_type='AIMS', **aimsconfig)
		browserobj = self.selenium
		try:
			enableAIMS(browserobj, **aimsconfig)
		except Exception as error:
			print('zbUIAssetManagement/verifyAIMS: Not able to configure AIMS.')
			print(('Error: {}'.format(error)))
			return False
		time.sleep(5)
		return True

	def verifyConnectiv(self, **connectivconfig):
		connectiv_path = '/administration/integrations/assetmanagement'
		self.gotoIntegrationConfigurations(connectiv_path, system_type='CONNECTIV', **connectivconfig)
		browserobj = self.selenium
		try:
			enableConnectiv(browserobj, **connectivconfig)
		except Exception as error:
			print('zbUIAssetManagement/verifyConnectiv: Not able to configure Connectiv.')
			print(('Error: {}'.format(error)))
			return False
		return True

	def verifyNuvolo(self, **nuvoloconfig):
		nuvolo_path = '/administration/integrations/assetmanagement'
		self.gotoIntegrationConfigurations(nuvolo_path, system_type='nuvolo', **nuvoloconfig)
		browserobj = self.selenium
		try:
			enableNuvolo(browserobj, **nuvoloconfig)
		except Exception as error:
			print('zbUIAssetManagement/verifyNuvolo: Not able to configure Nuvolo.')
			print(('Error: {}'.format(error)))
			return False
		return True

	def verifyServiceNow(self, **servicenowconfig):
		servicenow_path = '/administration/integrations/assetmanagement'
		self.gotoIntegrationConfigurations(servicenow_path, system_type='SERVICENOW', **servicenowconfig)
		browserobj = self.selenium
		try:
			enableServiceNow(browserobj, **servicenowconfig)
		except Exception as error:
			print('zbUIAssetManagement/verifyServiceNow: Not able to configure ServiceNow.')
			print(('Error: {}'.format(error)))
			return False
		return True

	def close(self):
		if self.selenium:
			self.selenium.quit()
