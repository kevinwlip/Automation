#!/usr/bin/python

from urllib.parse import urlparse
from ui.login.zbUILoginCore import Login
from ui.zbUIShared import waitLoadProgressDone
from selenium.webdriver.common.keys import Keys
from zbAPI import Ops
import time, pdb, json

CSS_SAVE_BUTTON = ".md-primary.md-button"

CSS_INSPECTOR_DROPDOWN = "md-select.inspector-select"
CSS_INSPECTORS =".md-clickable md-option.ng-scope[ng-value='inspector.inspectorid'] div.md-text.ng-binding"

CSS_CISCO = "[src='/static/images/asset-management/ciscoIcon.png']"

CSS_CISCO_EDIT = ".asset-management .edit-part .material-icons"
CSS_CISCO_HOST = ".asset-management .md-input[placeholder='IP Address or Hostname']"
CSS_CISCO_USERNAME = ".asset-management .md-input[placeholder='Your ERS (External RESTful Services) Endpoint']"
CSS_CISCO_PWD = ".asset-management .md-input[placeholder='Your ERS Password']"
CSS_CISCO_PROFILE = 'input[placeholder="Zingbox Profile Attribute"]'
CSS_CISCO_QUARANTINE = "[aria-checked='false'][aria-label='Quarantine devices through ISE']"

req = Ops()

def enableCiscoISE(browserobj, **iseconfig):
	ise_host = iseconfig["ise_host"]
	ise_uname = iseconfig["ise_uname"]
	ise_pwd = iseconfig["ise_pwd"]
	ise_profile = iseconfig["ise_profile"]
	inspector = iseconfig["inspector"]
	_configCiscoISE(browserobj)
	_inputISEInfo(browserobj, ise_host, ise_uname, ise_pwd, ise_profile)
	_selectInspector(browserobj, inspector)
	_selectQuarantineDevices(browserobj, True)
	browserobj.click(selector=CSS_SAVE_BUTTON)

def _configCiscoISE(browserobj):
	iseedit = browserobj.findSingleCSS(selector=CSS_CISCO_EDIT, timeout=3)
	if iseedit is not None:
		iseedit.click()

def _selectInspector(browserobj, inspector):
	browserobj.click(selector=CSS_INSPECTOR_DROPDOWN)
	rcode = browserobj.findMultiCSS(selector=CSS_INSPECTORS)
	if not rcode:
		raise Exception("zbUIAssetManagement/selectInspector: Asset Management cannot find inspector " + str(inspector))
	for insp in rcode:
		if inspector.strip() in insp.text.strip():
			insp.click()
			time.sleep(1)
			return
	raise Exception("zbUIAssetManagement/selectInspector: Unable to find target inspector " + str(inspector))

def _inputISEInfo(browserobj, ise_host, ise_uname, ise_pwd, ise_profile):
	if type(ise_host) != str or type(ise_uname) != str or type(ise_pwd) != str or type(ise_profile) != str:
		raise Exception('zbUIAssetManagement/inputConnectivClientInfo: client_id, secret and url must be in str type.')
	sendKey(browserobj, CSS_CISCO_HOST, ise_host)
	sendKey(browserobj, CSS_CISCO_USERNAME, ise_uname)
	sendKey(browserobj, CSS_CISCO_PWD, ise_pwd)
	#sendKey(browserobj, CSS_CISCO_PROFILE, ise_profile)


def _selectQuarantineDevices(browserobj, selected):
	unchecked_quarantine = browserobj.findSingleCSS(selector=CSS_CISCO_QUARANTINE, timeout=3)
	if unchecked_quarantine and selected == True:
		unchecked_quarantine.click()


def sendKey(browserobj, selector, text):
	_input = browserobj.findSingleCSS(selector=selector)
	if not _input:
		raise Exception('zbUIAssetManagement/sendKey: cannot find input {}.'.format(selector))
	_input.send_keys(Keys.DELETE)
	_input.clear()
	_input.send_keys(text)



class ISEIntegration():

	def __init__(self, **kwargs):
		self.params = kwargs
		self.selenium = Login(**kwargs).login()

		rcode = self.selenium.getURL(kwargs["url"]+'/')
		if rcode: waitLoadProgressDone(self.selenium)

	def gotoIntegrationConfigurations(self, integrations_url, **kwargs):
		req.delete_request(kwargs['tenantid'], 'ises', kwargs['site'])

		url = urlparse(self.params["url"])
		rcode = self.selenium.getURL(url.scheme+'://'+url.netloc+integrations_url)

	def verifyCiscoISE(self, **iseconfig):
		ise_path = '/administration/integrations/networkAccessControl'
		self.gotoIntegrationConfigurations(ise_path, **iseconfig)
		browserobj = self.selenium
		try:
			enableCiscoISE(browserobj, **iseconfig)
		except Exception as error:
			print('zbUIAssetManagement/verifyCiscoISE: Not able to configure Cisco ISE.')
			print(('Error: {}'.format(error)))
			return False
		return True

	def close(self):
		if self.selenium:
			self.selenium.quit()
