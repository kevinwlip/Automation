#!/usr/bin/python


from urllib.parse import urlparse
from ui.login.zbUILoginCore import Login
from zbAPI import Ops
from ui.zbUIShared import waitLoadProgressDone
import time, pdb

# Global CSS for Administration > SIEM Integration
CSS_CARD = "md-card[class*=tint]"
CSS_SWITCH = "div.md-thumb"

CSS_PORT_INPUT = "input[name='port']"
CSS_SAVE_BUTTON = 'button[name="Save changes made"]'

CSS_SIEM_EDIT_BUTTON = "[ng-click='siemIntCtrl.editConfig()']"

CSS_SIEM_SWITCH_ON = 'md-switch[ng-model="siemIntCtrl.siemConfig.SIEM.enabled"][aria-checked="true"]'
CSS_SIEM_SWITCH_OFF = 'md-switch[ng-model="siemIntCtrl.siemConfig.SIEM.enabled"][aria-checked="false"]'

CSS_SIEM_DISCOVER_ON = 'md-checkbox[name="Toggle checkbox Discovered Devices"][aria-checked="true"]'
CSS_SIEM_DISCOVER_OFF = 'md-checkbox[name="Toggle checkbox Discovered Devices"][aria-checked="false"]'

CSS_SIEM_ALERTS_ON = 'md-checkbox[name="Toggle checkbox Alerts"][aria-checked="true"]'
CSS_SIEM_ALERTS_OFF = 'md-checkbox[name="Toggle checkbox Alerts"][aria-checked="false"]'
CSS_SIEM_ALERT_AUTO_MODE = 'md-radio-button[name="Auto Mode"]'
CSS_SIEM_ALERTS_MANUAL_MODE = 'md-radio-button[name="Manual Mode"]'

CSS_SIEM_INSPECTOR_DROPDOWN = 'md-select[placeholder="Select Inspector"]'
CSS_SIEM_INSPECTORS = 'md-option[ng-value=inspector] > div.md-text'

CSS_SIEM_IP_SELECT = 'input[placeholder="IP Address"]'
CSS_IP_ADDRESS_INPUT = "input[name='ip']"

CSS_SIEM_PROTOCOL_DROPDOWN = 'md-select[placeholder="Protocol"]'
CSS_SIEM_PROTOCOL_UDP = 'md-option[name="Choose the UDP protocol"]'
CSS_SIEM_PROTOCOL_TCP = 'md-option[name="Choose the TCP protocol"]'

req = Ops()

class SIEMIntegration():

	def __init__(self, **kwargs):
		self.params = kwargs
		self.selenium = Login(**kwargs).login()

		rcode = self.selenium.getURL(kwargs["url"]+'/')
		if rcode: waitLoadProgressDone(self.selenium)


	def gotoSIEMIntegration(self, **kwargs):
		req.delete_request(kwargs['tenantid'], 'SIEM', kwargs['site'])

		url = urlparse(self.params["url"])
		rcode = self.selenium.getURL(url.scheme+'://'+url.netloc+'/administration/integrations/siemIntegration')


	def verifySIEMIntegration(self, **kwargs):
		rcode = self.gotoSIEMIntegration(**kwargs)
		rcode = self.configAddSIEM(**kwargs)
		return rcode

	def configEditSIEM(self):
		self.selenium.click(selector=CSS_SIEM_EDIT_BUTTON)
		waitLoadProgressDone(self.selenium)

	def configEnableSIEM(self):
		# check if switch is on, then turn off to start clean
		#kwargs = {"selector":CSS_SIEM_SWITCH_ON, "waittype":"visibility", "timeout":3}
		#rcode = self.selenium.click(**kwargs)

		# check if switch is off, then turn on
		kwargs = {"selector":CSS_SIEM_SWITCH_OFF, "waittype":"visibility", "timeout":3}
		rcode = self.selenium.click(**kwargs)

		# save
		self.configSaveSIEM()

		# check to switch is on
		self.gotoSIEMIntegration()
		kwargs = {"selector":CSS_SIEM_SWITCH_ON, "waittype":"visibility", "timeout":3}
		rcode = self.selenium.findSingleCSS(**kwargs)
		if not rcode:
			print("Fail to enable SIEM")
			return False
		return True

	def turnOn(self):
		# check if switch is off, then turn on
		kwargs = {"selector":CSS_SIEM_SWITCH_OFF, "waittype":"visibility", "timeout":3}
		rcode = self.selenium.click(**kwargs)


	def configDisableSIEM(self):
		# check if switch is off, then turn on, to start clean
		#kwargs = {"selector":CSS_SIEM_SWITCH_OFF, "waittype":"visibility", "timeout":3}
		#rcode = self.selenium.click(**kwargs)

		# check if switch is on, then turn off
		kwargs = {"selector":CSS_SIEM_SWITCH_ON, "waittype":"visibility", "timeout":3}
		rcode = self.selenium.click(**kwargs)

		# save
		self.configSaveSIEM()

		# check to switch is off
		self.gotoSIEMIntegration()
		kwargs = {"selector":CSS_SIEM_SWITCH_OFF, "waittype":"visibility", "timeout":3}
		rcode = self.selenium.findSingleCSS(**kwargs)
		if not rcode:
			print("Fail to disable SIEM")
			return False
		return True


	def configSaveSIEM(self):
		kwargs = {"selector":CSS_SAVE_BUTTON, "waittype":"visibility", "timeout":3}
		rcode = self.selenium.click(**kwargs)
		time.sleep(2)
		return True


	def configAddSIEM(self, **siemconfig):
		timeout = 3
		inputs = {
			"discover": True,
			"alert": True,
			"alertmode": "Auto",
			"port": "514",
			"protocol": "UDP"
		}

		# enable SIEM
		#rcode = self.configEnableSIEM()
		self.turnOn()

		# enable edit mode
		self.configEditSIEM()
		# configure Discover mode
		discover = siemconfig["discover"] if "discover" in siemconfig else inputs["discover"]
		if discover:
			kwargs = {"selector":CSS_SIEM_DISCOVER_OFF, "waittype":"visibility", "timeout":timeout}
			rcode = self.selenium.click(**kwargs)
		else:
			kwargs = {"selector":CSS_SIEM_DISCOVER_ON, "waittype":"visibility", "timeout":timeout}
			rcode = self.selenium.click(**kwargs)

		# configure Alerts mode
		alert = siemconfig["alert"] if "alert" in siemconfig else inputs["alert"]
		if alert:
			kwargs = {"selector":CSS_SIEM_ALERTS_OFF, "waittype":"visibility", "timeout":timeout}
			rcode = self.selenium.click(**kwargs)
			# configure alert mode
			alertmode = siemconfig["alertmode"] if "alertmode" in siemconfig else inputs["alertmode"]
			if alertmode == "Auto":
				kwargs = {"selector":CSS_SIEM_ALERT_AUTO_MODE, "waittype":"visibility", "timeout":timeout}
				rcode = self.selenium.click(**kwargs)
			if alertmode == "Manual":
				kwargs = {"selector":CSS_SIEM_ALERTS_MANUAL_MODE, "waittype":"visibility", "timeout":timeout}
				rcode = self.selenium.click(**kwargs)
		else:
			kwargs = {"selector":CSS_SIEM_INSPECTOR_DROPDOWN, "waittype":"visibility", "timeout":timeout}
			rcode = self.selenium.click(**kwargs)

		# configure Inspector
		inspector = siemconfig["inspector"]
		if inspector:
			kwargs = {"selector":CSS_SIEM_INSPECTOR_DROPDOWN, "waittype":"visibility", "timeout":timeout}
			rcode = self.selenium.click(**kwargs)
			kwargs = {"selector":CSS_SIEM_INSPECTORS, "waittype":"visibility", "timeout":timeout}
			rcode = self.selenium.findMultiCSS(**kwargs)
			for insp in rcode:
				if insp.text.strip() == inspector.strip():
					insp.click()
					time.sleep(1)
					break

		# configure Address (siem server ip address)
		address = siemconfig["address"] if "address" in siemconfig else inputs["address"]		
		kwargs = {"selector":CSS_IP_ADDRESS_INPUT, "waittype":"visibility", "timeout":timeout}
		rcode = self.selenium.findSingleCSS(**kwargs)
		rcode.clear()
		time.sleep(1)
		rcode.send_keys(address)
		time.sleep(1)


		# configure Port
		port = siemconfig["port"] if "port" in siemconfig else inputs["port"]
		kwargs = {"selector":CSS_PORT_INPUT, "waittype":"visibility", "timeout":timeout}
		rcode = self.selenium.findSingleCSS(**kwargs)
		rcode.clear()
		time.sleep(1)
		rcode.send_keys(port)
		time.sleep(1)

		# configure Protocol
		protocol = siemconfig["protocol"] if "protocol" in siemconfig else inputs["protocol"]
		kwargs = {"selector":CSS_SIEM_PROTOCOL_DROPDOWN, "waittype":"visibility", "timeout":timeout}
		rcode = self.selenium.click(**kwargs)
		if protocol == "UDP":
			kwargs = {"selector":CSS_SIEM_PROTOCOL_UDP, "waittype":"visibility", "timeout":timeout}
			rcode = self.selenium.click(**kwargs)
		if protocol == "TCP":
			kwargs = {"selector":CSS_SIEM_PROTOCOL_TCP, "waittype":"visibility", "timeout":timeout}
			rcode = self.selenium.click(**kwargs)

		# save
		kwargs["selector"] = CSS_SAVE_BUTTON
		rcode = self.selenium.findSingleCSS(**kwargs)
		rcode.click()
		time.sleep(1)

		return True

	def close(self):
		if self.selenium:
			self.selenium.quit()
