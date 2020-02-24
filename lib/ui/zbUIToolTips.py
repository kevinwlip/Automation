#!/usr/bin/python

from urllib.parse import urlparse
from ui.login.zbUILoginCore import Login
from ui.zbUIShared import waitLoadProgressDone, selectSingleSite, createHeaderDict
from common.zbCommon import isValidMACAddress
import time, pdb

#Shared
CSS_TOOLTIPS_TITLE = "h3.title-text.ng-binding"
CSS_TOOLTIPS_TODAYS_ACTV_NUMS = "h3.big-number"
CSS_TOOLTIPS_ALERTS_DROPDOWN = "ng-md-icon[ng-if='!alertMiniCtrl.isopen']>svg"
CSS_TOOLTIP_CREATE_POLICY = "button.md-primary.zing-hide-for-readonly"
CSS_TOOLTIP_POLICY_TITLE = "div[class='title layout-align-space-between-center layout-row']"
CSS_CANCEL_POLICY_BUTTON = "button[class='md-button md-ink-ripple grey-button']"

#Dashboard
CSS_TOOLTIPS_CRITICAL_ALERTS = "div[class='alert-widget level4 high layout-align-start-center layout-row']>div>div.alert-number"
CSS_TOOLTIPS_WARNING_ALERTS = "div[class='alert-widget level4 medium layout-align-start-center layout-row']>div>div.alert-number"

CSS_SITES = "div[class='multiselect-circle']>i.material-icons.ng-scope"
CSS_SITE_ALERTS = "span[ng-bind = 'item.alertCount']"
CSS_TOP_DEVICES_NAMES = "[ng-click='dashNetworkCtrl.navigate(item.key)'][name='Navigate to item key from the Devices widget']" 
CSS_TOP_APPS_NAMES = "[ng-click='dashNetworkCtrl.navigate(item.key)'][name='Navigate to item key from the Protocols widget']" #"span[category='Dashboard Apps/Protocols list']"

#Device Inventory
CSS_TOOLTIP_IP = "p[ng-bind='ctrl.data.ip']"
CSS_TOOLTIP_DEVICE_PROFILE = "span.ng-binding.flex-60"
CSS_TOOLTIPS_MAC= "p[ng-bind='ctrl.filteredDeviceId']"

CSS_IP_ADDRESS = "div[ng-repeat='col in colContainer.renderedColumns track by col.colDef.name'] > div > span" #element 1
CSS_DEVICE_PROFILE = "div[ng-repeat='col in colContainer.renderedColumns track by col.colDef.name'] > div > span" #element 2

CSS_DATA = "[ng-bind='ctrl.activityData.data || 0 | higherOrderBytesNum']"
CSS_DATA_USAGE = "[ng-bind='ctrl.activityData.data || 0 | higherOrderBytesNum']"
CSS_POLICY_GROUP_INPUT = "span[ng-if='!$chip.category']>strong.ng-binding"

#Applications
CSS_APPLICATION_NAME = "a.ng-binding"
CSS_POLICY_PROTOCOL_INPUT = "span[ng-if='!$chip.category']>strong.ng-binding"

CSS_NO_TRAFFIC_LABEL = "div.no-traffic-label"




class ToolTips():

	def __init__(self, **kwargs):
		self.params = kwargs
		self.selenium = Login(**kwargs).login()

		#rcode = self.selenium.getURL(kwargs["url"]+'/')
		#if rcode: waitLoadProgressDone(self.selenium)

	def verifyDashboardAlertsToolTips(self):
		kwargs = {}
		#url = urlparse(self.params["url"])
		#rcode = self.selenium.getURL(url.scheme+'://'+url.netloc+'')
		
		#Gets the total alerts on site
		kwargs = {"selector": CSS_SITE_ALERTS, "timeout": 10}
		siteAlerts = self.selenium.findSingleCSS(**kwargs)
		# handle case when there are no alerts to find, then just skip and return True for test
		if not siteAlerts:
			print("Dashboard site card does not have alert.  Skip test")
			return True

		siteAlerts = int(siteAlerts.text)

		#Gets the critical alerts in tooltip
		kwargs["selector"] = CSS_TOOLTIPS_CRITICAL_ALERTS
		critical = self.selenium.findSingleCSS(**kwargs)
		critical = int(critical.text)

		#Gets the warnining alerts in tooltip
		kwargs["selector"] = CSS_TOOLTIPS_WARNING_ALERTS
		warning = self.selenium.findSingleCSS(**kwargs)
		warning = int(warning.text)

		totalAlerts = critical + warning

		#Checks to see if alerts sum up correctly
		if siteAlerts != totalAlerts:
			print("Total alerts do not match with tooltip")
			return False

		return True


	def verifyDashboardTopDevicesToolTips(self):
		kwargs = {}
		url = urlparse(self.params["url"])
		rcode = self.selenium.getURL(url.scheme+'://'+url.netloc+'')
		waitLoadProgressDone(self.selenium)

		#Clicks the first site
		selectSingleSite(self.selenium)

		self.selenium.click(selector="[aria-label='Select date range']")
		time.sleep(1)
		self.selenium.click(selector="[md-svg-src='images/icon-calendar-month.svg']")
		waitLoadProgressDone(self.selenium)

		#Selects the first hostname and opens up tooltip	
		kwargs["selector"] = CSS_TOP_DEVICES_NAMES
		deviceName = self.selenium.findSingleCSS(**kwargs)
		self.selenium.hoverElement(deviceName)
		deviceName = deviceName.text

		return self.verifyDevicesToolTip(deviceName)


	def verifyDashboardTopAppsToolTips(self):
		kwargs = {}
		url = urlparse(self.params["url"])
		rcode = self.selenium.getURL(url.scheme+'://'+url.netloc+'')
		waitLoadProgressDone(self.selenium)
		selectSingleSite(self.selenium)

		self.selenium.click(selector="[aria-label='Select date range']")
		time.sleep(1)
		dateitems = self.selenium.findMultiCSS(selector=".date-picker-item[ng-repeat='dateitem in profileSelectorCtrl.activeList']");
		dateitems[3].click()
		waitLoadProgressDone(self.selenium)

		#Selects the first hostname and opens up tooltip	
		kwargs["selector"] = CSS_TOP_APPS_NAMES
		appName = self.selenium.findSingleCSS(**kwargs)
		self.selenium.hoverElement(appName)
		appName = appName.text

		return self.verifyAppsProtocolToolTip(appName)


	def verifyDeviceInventoryToolTips(self):
		kwargs = {}
		url = urlparse(self.params["url"])
		rcode = self.selenium.getURL(url.scheme+'://'+url.netloc+'/monitor/inventory')
		waitLoadProgressDone(self.selenium)

		#if not clickAllCheckboxes(self.selenium):
			#return False
		headers = createHeaderDict(self.selenium)

		ipAddress = headers["IP Address"]
		ipAddress = ipAddress[5].text


		deviceProf = headers["Profile"]
		deviceProf = deviceProf[5].text

		deviceName = headers["Device Name"][5]
		deviceName = self.selenium.findSingleCSS(browserobj=deviceName,selector=".ui-grid-cell-contents .ng-binding")
		self.selenium.hoverElement(deviceName)
		time.sleep(5)
		deviceName = deviceName.text
		try:
			kwargs["selector"] = CSS_DATA
			kwargs["waittype"] = "visibility" 
			data = self.selenium.findSingleCSS(**kwargs)
			data = data.text
			#data = data[0:data.find(" ")]
			data = float(data)
		except Exception as e:
			print(("Device with IP {} got an unexpected value: {}.\n{}".format(ipAddress, data, e)))
			return False

		#kwargs["selector"] = CSS_DEVICE_LINK

		

		try:
			kwargs["selector"] = CSS_DATA_USAGE
			data_usage = self.selenium.findSingleCSS(**kwargs)
			data_usage = data_usage.text
			#data_usage = data_usage[0:data_usage.find(" ")]
			data_usage = float(data_usage)
		except Exception as e:
			print(("Device with IP {} got an unexpected value: {}.\n{}".format(ipAddress, data_usage, e)))
			return False

		return self.verifyDevicesToolTip(deviceName, ipAddress, deviceProf, data_usage)


	def verifyApplicationsToolTips(self):
		kwargs = {}
		url = urlparse(self.params["url"])
		rcode = self.selenium.getURL(url.scheme+'://'+url.netloc+'/monitor/applications')
		waitLoadProgressDone(self.selenium)

		kwargs["selector"] = CSS_APPLICATION_NAME
		appName = self.selenium.findSingleCSS(**kwargs)
		appName = appName.text

		return self.verifyAppsProtocolToolTip(appName)


	def verifyDevicesToolTip(self, deviceName, ipAddress=None, deviceProf=None, data_usage=None, apps=None):
		# wait a few seconds for the tooltip to load
		time.sleep(3)
		kwargs = {}

		#Gets the title from tooltip
		kwargs["selector"] = CSS_TOOLTIPS_TITLE
		titleName = self.selenium.findSingleCSS(**kwargs)
		titleName = titleName.text

		#Device profile from tooltip
		kwargs["selector"] = CSS_TOOLTIP_DEVICE_PROFILE
		deviceProfTT = self.selenium.findSingleCSS(**kwargs)
		deviceProfTT = deviceProfTT.text

		#Gets the MAC form tooltip
		kwargs["selector"] = CSS_TOOLTIPS_MAC
		macAddTT = self.selenium.findSingleCSS(**kwargs)
		macAddTT = macAddTT.text

		#IP address from tooltip
		kwargs["selector"] = CSS_TOOLTIP_IP
		ipTT = self.selenium.findSingleCSS(**kwargs)
		ipTT = ipTT.text

		#Gets the three 'Todays Activity' Numbers
		kwargs["selector"] = CSS_TOOLTIPS_TODAYS_ACTV_NUMS
		rcode = self.selenium.findMultiCSS(**kwargs)
		destinationsTT = int(rcode[0].text)
		dataUsageTT = float(rcode[1].text)
		appsProtocolsTT = int(rcode[2].text)

		if titleName == "unknown":
			if deviceName != macAddTT:
				print("Title in tooltip is not correct")
			pass	
		elif titleName != deviceName:
			# check if deviceName has '...'
			isok = False
			if '...' in deviceName:
				if deviceName.replace('...','').strip() in titleName:
					isok = True
			if not isok:
				print("Device name {} did not match title {} in tooltip".format(deviceName, titleName))
				return False

		if destinationsTT < 0:
			print("Unexpected number {} for destinations in tooltips".format(destinationsTT))
			return False

		if dataUsageTT < 0:
			print("Unexpected number {} for data usage in tooltips".format(dataUsageTT))
			return False

		if appsProtocolsTT < 0:
			print("Unexpected number {} for apps/protocols in tooltips".format(appsProtocolsTT))
			return False

		#Checks the alert dropdown
		kwargs = {"selector": CSS_TOOLTIPS_ALERTS_DROPDOWN, "waittype":"clickable", "timeout":5}
		try:
			alertArrow = self.selenium.findSingleCSS(**kwargs)
		except:
			# handle intermittent exception for finding this element
			pass
		if alertArrow:
			alertArrow.click()
		else:
			print("This device doesn not have alert.  skip.")
			pass
		#Create policy from tooltip
		kwargs["selector"] = CSS_TOOLTIP_CREATE_POLICY
		rcode = self.selenium.findSingleCSSNoHover(**kwargs)
		rcode.click()
		waitLoadProgressDone(self.selenium)

		#Checks if policy opens from tooltip
		kwargs["selector"] = CSS_TOOLTIP_POLICY_TITLE
		rcode = self.selenium.findSingleCSS(**kwargs)
		if not rcode:
			print("Policy Editor did not appear")
			return False

		#Check if the title matches the name in group#1	
		groupName = self.selenium.findMultiCSS(selector=CSS_POLICY_GROUP_INPUT, waittype="located", timeout=3)
		groupName = groupName[-1].text

		if groupName != deviceName:
			if groupName != ipTT:
				# check if deviceName has '...'
				isok = False
				if '...' in deviceName:
					if deviceName.replace('...','').strip() in groupName:
						isok = True
				if not isok:
					print("Group name {} in policy editor did not match host name".format(groupName))
					return False
		
		#Used only for verifying device inventory
		if ipAddress != None:

			if ipAddress != ipTT:
				print(ipTT)
				print("IP address {} does not match tooltip".format(ipAddress))
				return False

			if deviceProf != deviceProf:
				print("Device profile {} does not match tooltip".format(deviceProf))	
				return False

			if apps and apps != appsProtocolsTT:
				print("Applications {} does not match tooltip".format(apps))
				return False	

			if deviceName != titleName:
				if isValidMACAddress(deviceName) and titleName == "unknown":
					pass
				else:
					print("Device name {} does not match tooltip name {}".format(deviceName, titleName))
					return False
		return True


	def verifyAppsProtocolToolTip(self, appName):
		kwargs = {}

		#Gets the title of the tooltip
		kwargs["selector"] = CSS_TOOLTIPS_TITLE
		titleName = self.selenium.findSingleCSS(**kwargs)
		titleName = titleName.text

		if appName != titleName:
			print("Title name did not match protocol name")
			return False

		#Gets the three 'Todays Activity' Numbers
		self.selenium.hoverElement(self.selenium.findSingleCSS(**kwargs))
		time.sleep(5)
		kwargs["selector"] = CSS_TOOLTIPS_TODAYS_ACTV_NUMS
		rcode = self.selenium.findMultiCSS(**kwargs)
		destinationsTT = int(rcode[0].text)
		dataUsageTT = float(rcode[1].text)
		appsProtocolsTT = int(rcode[2].text)

		if destinationsTT < 0:
			print("Unexpected number for destinations in tooltips")
			return False

		if dataUsageTT < 0:
			print("Unexpected number for data usage in tooltips")
			return False

		if appsProtocolsTT < 0:
			print("Unexpected number for apps/protocols in tooltips")
			return False
		
		#Create policy from tooltip
		kwargs["selector"] = CSS_TOOLTIP_CREATE_POLICY
		rcode = self.selenium.findSingleCSS(**kwargs)
		rcode.click()

		#Checks if policy opens from tooltip
		kwargs["selector"] = CSS_TOOLTIP_POLICY_TITLE
		rcode = self.selenium.findSingleCSS(**kwargs)
		if not rcode:
			print("Policy Editor did not appear")
			return False

		#Checks if the App/protocol name matches the protocol name on dashboard	
		kwargs["selector"] = CSS_POLICY_PROTOCOL_INPUT
		policyName = self.selenium.findSingleCSS(**kwargs)
		policyName = policyName.text

		if policyName != appName:
			print("App/Protocol name in policy editor did not match host name")	
			return False

		return True

	def close(self):
		if self.selenium:
			self.selenium.quit()
