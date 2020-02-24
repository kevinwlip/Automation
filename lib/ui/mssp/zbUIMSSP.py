from urllib.parse import urlparse
from ui.login.zbUILoginCore import Login
from ui.zbUIShared import waitLoadProgressDone
import pdb, time

from common.zbCommon import convertByte
import collections

# Global CSS selectors
#Customers page
CSS_LINKED_NAME = "a[ng-bind='row.entity.tenantid || row.entity.username']"
CSS_NAME = "div[ng-bind='row.entity.tenantid || row.entity.username']"
CSS_MEDICAL_IOT_DEVICES = "div[ng-bind='row.entity.medIoTDevices']"
CSS_ALL_IOT_DEVICES = "div[ng-bind='row.entity.devices_total_IoT_devices']"
CSS_SITES = "div[ng-bind='row.entity.sites_length']"
CSS_INSPECTORS = "div[ng-bind='row.entity.inspectors_length']"
CSS_TOTAL_DATA = "div[ng-bind='row.entity.totalData | higherOrderBytes']"
CSS_CRITICAL_ALERTS = "div[ng-bind='row.entity.alert_high || 0']"
CSS_WARNING_ALERTS = "div[ng-bind='row.entity.alert_medium || 0']"
CSS_MEDIUM_RISK = "div[ng-bind='row.entity.risk_medium || 0']"
CSS_HIGH_RISK = "div[ng-bind='row.entity.risk_high || 0']"
CSS_SELECT_PAGE_DROPDOWN = "md-select[ng-model='ctrl.currentPage']"
CSS_SELECT_PAGE = "md-option[ng-repeat='page in ctrl.pageNums']"
CSS_CALENDAR_DROPDOWN = "button[ng-click='timerangeDropdownCtrl.openMenu($mdOpenMenu, $event)']"
CSS_ONE_DAY_SELECTION = "div[ng-click='timerangeDropdownCtrl.selectDateRange($index)']"

#Resellers page
CSS_RESELLER_NAME = "a[ng-click='grid.appScope.ctrl.goDetail(row)']"
CSS_ACTIVE_TRIALS = "div[ng-bind='row.entity.resellerObj.tenant_type.poc || 0']"
CSS_TRIAL_IOT_DEVICES = "div[ng-bind='row.entity.resellerObj.profile_type_poc.IoT || 0']"
CSS_ACTIVE_CUSTOMERS = "div[ng-bind='row.entity.resellerObj.tenant_type.paid || 0']"
CSS_CUSTOMER_IOT_DEVICES = "div[ng-bind='row.entity.resellerObj.profile_type_paid.IoT || 0']"

#Summary page
CSS_SUMMARY_CUSTOMERS = "md-card[class='portal-summary-card customer-risk _md flex'] >div>div>div>div"
CSS_SUMMARY_RISK_NUMBERS = "md-card[class='portal-summary-card device-risk _md flex'] >div>div>div>div"
CSS_SUMMARY_ALERT_NUMBERS = "div[class='alert-number']"
CSS_SUMMARY_DATA_USAGE = "md-card[class='portal-summary-card data-processed _md flex']>div>div>div"
CSS_SUMMARY_INSPECTORS = "md-card[class='portal-summary-card inspector-connectivity _md flex']>div>div>div[class='portal-summary-card-key-metric-value ng-binding']"
CSS_SUMMARY_CATEGORIES = "div[id='portal-summary-card-composition-metric-one-value']"
CSS_SUMMARY_PROFILES = "div[id='portal-summary-card-composition-metric-two-value']"
CSS_SUMMARY_ONLINE = "div[class='portal-summary-card-metric-value online align-left ng-binding']"
CSS_SUMMARY_OFFLINE = "div[class='portal-summary-card-metric-value offline ng-binding']"

CSS_ALERT_NAME = "div.event-reporter"
CSS_SHOW_MORE_BUTTON = "button[class='event-list-show-more md-button md-ink-ripple ng-binding']"

#Customer details page
CSS_DETAILS_NAME = "div[class='title ng-binding']"
CSS_DETAILS_MED_IOT = "div[ng-bind='portalCustomerDetailCtrl.data.devicesAgg.medIoTDevices']"
CSS_DETAILS_ALL_IOT = "div[ng-bind='portalCustomerDetailCtrl.data.devicesAgg.total_IoT_devices']"
CSS_DETAILS_SITES = "div[ng-bind='portalCustomerDetailTabsCtrl.tabData.siteList.length || 0']"
CSS_DETAILS_DATA_USAGE = "div[ng-bind='portalCustomerDetailCtrl.data.traffic | higherOrderBytes']"
CSS_DETAILS_CRITICAL_ALERTS = "div[class='alert-widget level4 high layout-align-space-between-center layout-row'] >div>div[class='alert-number']"
CSS_DETAILS_WARNING_ALERTS = "div[class='alert-widget level4 medium layout-align-space-between-center layout-row'] >div>div[class='alert-number']"

#Dashboard
CSS_DASHBOARD_ICON = "i[class='material-icons']"
CSS_DASHBOARD_IOT_SELECT_BUTTON = "button[class='selector-menu-button md-button md-ink-ripple layout-align-space-between-center layout-row']"
CSS_DASHBOARD_ALL_IOT_DEVICES = "button[aria-label='Open IOT selector']>[class='iot-number ng-binding ng-scope']"
CSS_DASHBOARD_SITES = "span[ng-if='categoryListingCtrl.siteListData']"
CSS_DASHBOARD_DATA = "div[ng-bind='summaryCtrl.numericalData.encrypted.total || 0 | higherOrderBytesNum']"
CSS_DASHBOARD_HIGH_RISK = "div.risk-number.high"
CSS_DASHBOARD_MEDIUM_RISK = "div.risk-number.medium"
CSS_ALERTS_SEVERITY_SELECTION = "md-select[ng-model='alertListCtrl.filter.severity']"
CSS_SEVERITY_SELECT = "div[class='alert-description']"
CSS_ALERTS = "span[ng-if='!alertListCtrl.loading']"

# User
CSS_USER_LINK = "zing-user-card.user-card-mssp"

class MSSP():

	def __init__(self, **kwargs):
		self.params = kwargs
		self.url = urlparse(kwargs["url"])
		self.selenium = Login(**kwargs).login()
		waitLoadProgressDone(self.selenium)



	def verifyMSSPCustomers(self,timeRange):
		kwargs = {}

		urlpath = '/portal-customers'
		if 'testing' in self.url.netloc or 'staging' in self.url.netloc:
			urlpath = '/#portal-customers'
		rcode = self.selenium.getURL('http://'+self.url.netloc+urlpath)
		waitLoadProgressDone(self.selenium)

		kwargs["selector"] = CSS_CALENDAR_DROPDOWN
		rcode = self.selenium.findSingleCSS(**kwargs)
		rcode.click()
		time.sleep(1)

		kwargs["selector"] = CSS_ONE_DAY_SELECTION
		rcode = self.selenium.findMultiCSS(**kwargs)
		if timeRange == "2H":
			rcode[0].click()
		elif timeRange == "1D":
			rcode[1].click()
		elif timeRange == "1W":
			rcode[2].click()
		elif timeRange == "1M":
			rcode[3].click()
		elif timeRange == "6M":
			rcode[4].click()	


		customersDict = collections.OrderedDict()
		summaryMedIoTDevices = 0
		summaryAllIoTDevices = 0
		summarySites = 0
		summaryInspectors = 0
		summaryTotalData = 0
		summaryCriticalAlerts = 0
		summaryWarningAlerts = 0
		summaryMediumRisk = 0
		summaryHighRisk = 0
		links = False

		kwargs["selector"]= CSS_SELECT_PAGE_DROPDOWN
		rcode = self.selenium.findSingleCSS(**kwargs)
		rcode.click()
		time.sleep(5)
		kwargs["selector"] = CSS_SELECT_PAGE
		page = self.selenium.findMultiCSS(**kwargs)
		leng = len(page)
		for k in range(0,leng):
		
			page[k].click()
			time.sleep(2)

			if links == True:
				name = []
				
				kwargs= {"selector": CSS_LINKED_NAME, "waittype":"visibility", "timeout":3}
				linked = self.selenium.findSingleCSS(**kwargs)
				name.append(linked)

				kwargs= {"selector": CSS_NAME, "waittype":"visibility", "timeout":3}
				unlinked = self.selenium.findMultiCSS(**kwargs)
				for i in unlinked:
					name.append(i)
				length = len(name)
			else:
				kwargs= {"selector": CSS_NAME, "waittype":"visibility", "timeout":3}
				name = self.selenium.findMultiCSS(**kwargs)
				length = 0 if not name else len(name)
				#length = len(name)

			for i in range(0,length):
				rcode = name[i].text
				customersDict[rcode] = {} 
				#time.sleep(2)

				kwargs["selector"] = CSS_MEDICAL_IOT_DEVICES
				medIoTDevices = self.selenium.findMultiCSS(**kwargs)
				customersDict[rcode]["Medical IoT Devices"] = medIoTDevices[i].text
				summaryMedIoTDevices = summaryMedIoTDevices + int(medIoTDevices[i].text)
				#print summaryMedIoTDevices

				kwargs["selector"] = CSS_ALL_IOT_DEVICES
				allIoTDevices = self.selenium.findMultiCSS(**kwargs)
				customersDict[rcode]["All Iot Devices"] = allIoTDevices[i].text
				summaryAllIoTDevices = summaryAllIoTDevices + int(allIoTDevices[i].text) 

				kwargs["selector"] = CSS_SITES
				sites = self.selenium.findMultiCSS(**kwargs)
				customersDict[rcode]["Sites"] = sites[i].text
				summarySites = summarySites + int(sites[i].text)

				kwargs["selector"] = CSS_INSPECTORS
				inspectors = self.selenium.findMultiCSS(**kwargs)
				customersDict[rcode]["Inspectors"] = inspectors[i].text
				summaryInspectors = summaryInspectors + int(inspectors[i].text)

				kwargs["selector"] = CSS_TOTAL_DATA
				totalData = self.selenium.findMultiCSS(**kwargs)
				customersDict[rcode]["Total Data"] = totalData[i].text
				totalData = totalData[i].text
				dataSize = totalData[totalData.find(" ") + 1:len(totalData)]
				totalData = float(totalData[0:totalData.find(" ")])
				
				checkSize = ["B","KB","MB","GB","TB","PB","EB","ZB","YB"]
				index = checkSize.index(dataSize) 
				totalData = totalData * 1024 ** index

				summaryTotalData = summaryTotalData + totalData

				kwargs["selector"] = CSS_CRITICAL_ALERTS
				criticalAlerts = self.selenium.findMultiCSS(**kwargs)
				customersDict[rcode]["Critical Alerts"] = criticalAlerts[i].text
				summaryCriticalAlerts = summaryCriticalAlerts + int(criticalAlerts[i].text)

				kwargs["selector"] = CSS_WARNING_ALERTS
				warningAlerts = self.selenium.findMultiCSS(**kwargs)
				customersDict[rcode]["Warning Alerts"] = warningAlerts[i].text
				summaryWarningAlerts = summaryWarningAlerts + int(warningAlerts[i].text)

				kwargs["selector"] = CSS_MEDIUM_RISK
				mediumRisk = self.selenium.findMultiCSS(**kwargs)
				customersDict[rcode]["Medium Risk"] = mediumRisk[i].text
				summaryMediumRisk = summaryMediumRisk + int(mediumRisk[i].text)

				kwargs["selector"] = CSS_HIGH_RISK
				highRisk = self.selenium.findMultiCSS(**kwargs)
				customersDict[rcode]["High Risk"] = highRisk[i].text
				summaryHighRisk = summaryHighRisk + int(highRisk[i].text)

			kwargs["selector"] = CSS_SELECT_PAGE_DROPDOWN
			rcode = self.selenium.findSingleCSS(**kwargs)
			rcode.click()
			time.sleep(2)
			links = False
		customersDict["Summary"] = {}
		customersDict["Summary"]["Summary Medical Iot Devices"] = summaryMedIoTDevices
		customersDict["Summary"]["Summary All Iot Devices"] = summaryAllIoTDevices
		customersDict["Summary"]["Summary Sites"] = summarySites
		customersDict["Summary"]["Summary Inspectors"] = summaryInspectors
		customersDict["Summary"]["Summary Total Data"] = summaryTotalData 
		customersDict["Summary"]["Summary Critical Alerts"] = summaryCriticalAlerts
		customersDict["Summary"]["Summary Warning Alerts"] = summaryWarningAlerts
		customersDict["Summary"]["Summary Medium Risk"] = summaryMediumRisk
		customersDict["Summary"]["Summary High Risk"] = summaryHighRisk

		print(customersDict)

		return self.verifyMSSPSummary(customersDict,timeRange)

	def verifyMSSPResellers(self):
		gotFailures = False
		kwargs = {}

		urlpath = '/#portal-resellers' if 'testing' in self.url.netloc else '/portal-resellers'
		rcode = self.selenium.getURL('http://'+self.url.netloc+urlpath)
		waitLoadProgressDone(self.selenium)

		summaryActiveTrials = 0
		summaryTrialIoT = 0
		summaryCustomerIoT = 0
		summaryActiveCustomers = 0
		kwargs["selector"] = CSS_RESELLER_NAME
		name = self.selenium.findMultiCSS(**kwargs)

		
		ResellersDict = collections.OrderedDict()
		for i in range(0,len(name)):
			rcode = name[i].text
			ResellersDict[rcode] = {} 

			kwargs["selector"] = CSS_ACTIVE_TRIALS
			activeTrials = self.selenium.findMultiCSS(**kwargs)
			ResellersDict[rcode]["Active Trials"] = activeTrials[i].text	
			summaryActiveTrials = summaryActiveTrials + int(activeTrials[i].text)

			kwargs["selector"] = CSS_TRIAL_IOT_DEVICES
			trialIoTDevices = self.selenium.findMultiCSS(**kwargs)
			ResellersDict[rcode]["Trial IoT Devices"] = trialIoTDevices[i].text
			summaryTrialIoT = summaryTrialIoT + int(trialIoTDevices[i].text)

			kwargs["selector"] = CSS_ACTIVE_CUSTOMERS
			activeCustomers = self.selenium.findMultiCSS(**kwargs)
			ResellersDict[rcode]["Active Customers"] = activeCustomers[i].text
			summaryActiveCustomers = summaryActiveCustomers + int(activeCustomers[i].text)

			kwargs["selector"] = CSS_CUSTOMER_IOT_DEVICES
			customerIoTDevices = self.selenium.findMultiCSS(**kwargs)
			ResellersDict[rcode]["Customer IoT Devices"] = customerIoTDevices[i].text
			summaryCustomerIoT = summaryCustomerIoT + int(customerIoTDevices[i].text)

		ResellersDict["Summary"] = {}
		ResellersDict["Summary"]["Summary Active Trials"] = summaryActiveTrials
		ResellersDict["Summary"]["Summary Trial IoT Devices"] = summaryTrialIoT
		ResellersDict["Summary"]["Summary Active Customers"] = summaryActiveCustomers
		ResellersDict["Summary"]["Summary Customer IoT Devices"] = summaryCustomerIoT

		if ResellersDict["Summary"]["Summary Active Trials"] <= 0:
			print("Unexpected total for Active trials in Resellers page")
			gotFailures = True
		if ResellersDict["Summary"]["Summary Trial IoT Devices"] <=0:
			print("Unexpected total for Trial IoT Devices in Resellers page")
			gotFailures = True
		if ResellersDict["Summary"]["Summary Active Customers"] <= 0:
			print("Unexpected total for Active Customers in Resellers page")
			gotFailures = True
		if ResellersDict["Summary"]["Summary Customer IoT Devices"] <= 0:
			print("Unexpected total for Customer IoT Devices in Resellers page")
			return False

		if gotFailures:
			print(ResellersDict)
			return False
		else:
			return True


	def verifyMSSPSummary(self,customersDict=None,timeRange=None):
		gotFailures = False
		kwargs = {}

		urlpath = '/#mssp' if 'testing' in self.url.netloc else '/mssp'
		rcode = self.selenium.getURL('http://'+self.url.netloc+urlpath)
		waitLoadProgressDone(self.selenium)

		kwargs["selector"] = CSS_CALENDAR_DROPDOWN
		rcode = self.selenium.findSingleCSS(**kwargs)
		rcode.click()
		time.sleep(1)

		kwargs["selector"] = CSS_ONE_DAY_SELECTION
		rcode = self.selenium.findMultiCSS(**kwargs)
		if timeRange == "2H":
			rcode[0].click()
		elif timeRange == "1D":
			rcode[1].click()
		elif timeRange == "1W":
			rcode[2].click()
		elif timeRange == "1M":
			rcode[3].click()
		elif timeRange == "6M":
			rcode[4].click()	
		waitLoadProgressDone(self.selenium)


		kwargs["selector"] = CSS_SUMMARY_CUSTOMERS
		customerNumbers = self.selenium.findMultiCSS(**kwargs)
		for i in customerNumbers:
			i = int(i.text)
			if i < 0:
				print("Unexpected number in Customers")
				gotFailures = True

		kwargs["selector"] = CSS_SUMMARY_RISK_NUMBERS
		riskNumbers = self.selenium.findMultiCSS(**kwargs)
		for i in riskNumbers:
			i = int(i.text)
			if i < 0:
				print("Unexpected number in Risk")
				gotFailures = True
		highRisk = int(riskNumbers[0].text)
		mediumRisk = int(riskNumbers[1].text)

		kwargs["selector"] = CSS_SUMMARY_ALERT_NUMBERS
		alertNumbers = self.selenium.findMultiCSS(**kwargs)
		for i in alertNumbers:
			i = int(i.text)
			if i < 0:
				print("Unexpected number in Alerts")
				gotFailures = True
		criticalAlerts = int(alertNumbers[0].text)
		warningAlerts = int(alertNumbers[1].text)

		kwargs["selector"] = CSS_SUMMARY_CATEGORIES
		categories = self.selenium.findSingleCSS(**kwargs)
		if int(categories.text) < 0:
			print("Unexpected number in Categories")
			gotFailures = True

		kwargs["selector"] = CSS_SUMMARY_PROFILES
		profiles = self.selenium.findSingleCSS(**kwargs)
		if int(profiles.text) < 0:
			print("Unexpected number in Profiles")
			gotFailures = True

		kwargs["selector"] = CSS_SUMMARY_DATA_USAGE
		dataUsage = self.selenium.findSingleCSS(**kwargs)
		dataUsage = dataUsage.text
		dataSize = dataUsage[dataUsage.find(" ") + 1:len(dataUsage)]
		dataUsage = float(dataUsage[0:dataUsage.find(" ")])

		checkSize = ["B","KB","MB","GB","TB","PB","EB","ZB","YB"]
		index = checkSize.index(dataSize) 
		dataUsage = dataUsage * 1024 ** index
		diffPercent = int((abs(customersDict["Summary"]["Summary Total Data"] - dataUsage) / dataUsage) * 100)

		kwargs["selector"] = CSS_SUMMARY_INSPECTORS
		inspectors = self.selenium.findSingleCSS(**kwargs)
		inspectors = int(inspectors.text)
		if inspectors< 0:
			print("Unexpected number in 'Inspectors'")
			gotFailures = True

		kwargs["selector"] = CSS_SUMMARY_OFFLINE
		offline = self.selenium.findSingleCSS(**kwargs)
		if int(offline.text) < 0:
			print("Unexpected number in 'Offline'")
			gotFailures = True

		kwargs["selector"] = CSS_SUMMARY_ONLINE
		online = self.selenium.findSingleCSS(**kwargs)	
		if int(online.text) < 0:
			print("Unexpected number in 'Online'")
			gotFailures = True


		if customersDict != None:

			if customersDict["Summary"]["Summary Critical Alerts"] != criticalAlerts:
				print("Critical Alerts %s does not match customers page sum %s" % (str(criticalAlerts), str(customersDict["Summary"]["Summary Critical Alerts"])))
				gotFailures = True
			if customersDict["Summary"]["Summary Warning Alerts"] != warningAlerts:
				print("Warning Alerts %s does not match customers page sum %s" % (str(warningAlerts), str(customersDict["Summary"]["Summary Warning Alerts"])))
				gotFailures = True
			if diffPercent > 5:
				print("Data Usage %s does not match customers page sum %s" % (str(dataUsage), str(customersDict["Summary"]["Summary Total Data"])))
				gotFailures = True
			if customersDict["Summary"]["Summary High Risk"] != highRisk:
				print("High Risk %s does not match customers page sum %s" % (str(highRisk), str(customersDict["Summary"]["Summary High Risk"])))
				gotFailures = True
			if customersDict["Summary"]["Summary Medium Risk"] != mediumRisk:
				print("Medium Risk %s does not match customers page sum %s" % (str(mediumRisk), str(customersDict["Summary"]["Summary Medium Risk"])))
				gotFailures = True
			if customersDict["Summary"]["Summary Inspectors"] != inspectors:
				print("Inspectors %s does not match customers page sum %s" % (str(inspectors), str(customersDict["Summary"]["Summary Inspectors"])))
				gotFailures = True

		kwargs["selector"] = CSS_SHOW_MORE_BUTTON
		rcode = self.selenium.findSingleCSS(**kwargs)
		rcode.click()
		waitLoadProgressDone(self.selenium)

		kwargs["selector"] = CSS_ALERT_NAME
		alertName = self.selenium.findMultiCSS(**kwargs)
		for i in alertName:
			if i not in alertName:
				print("Alert name is not in customers page")
				gotFailures = True

		return False if gotFailures else True


	def verifyCustomerDetail(self):
		gotFailures = False
		kwargs = {}

		urlpath = '/#portal-customers' if 'testing' in self.url.netloc else '/portal-customers'
		rcode = self.selenium.getURL('http://'+self.url.netloc+urlpath)
		waitLoadProgressDone(self.selenium)

		kwargs= {"selector": CSS_LINKED_NAME, "waittype":"visibility", "timeout":3}
		name = self.selenium.findSingleCSS(**kwargs)
		name = name.text

		kwargs["selector"] = CSS_MEDICAL_IOT_DEVICES
		medIoTDevices = self.selenium.findSingleCSS(**kwargs)
		medIoTDevices = int(medIoTDevices.text)
		
		kwargs["selector"] = CSS_ALL_IOT_DEVICES
		allIoTDevices = self.selenium.findSingleCSS(**kwargs)
		allIoTDevices = int(allIoTDevices.text)

		kwargs["selector"] = CSS_SITES
		sites = self.selenium.findSingleCSS(**kwargs)
		sites = int(sites.text)

		kwargs["selector"] = CSS_TOTAL_DATA
		totalData = self.selenium.findSingleCSS(**kwargs)
		totalDataByte = convertByte(totalData.text)

		kwargs["selector"] = CSS_CRITICAL_ALERTS
		criticalAlerts = self.selenium.findSingleCSS(**kwargs)
		criticalAlerts = int(criticalAlerts.text)

		kwargs["selector"] = CSS_WARNING_ALERTS
		warningAlerts = self.selenium.findSingleCSS(**kwargs)
		warningAlerts = int(warningAlerts.text)

		kwargs["selector"] = CSS_LINKED_NAME
		rcode = self.selenium.findSingleCSS(**kwargs)
		rcode.click()

		kwargs["selector"] = CSS_DETAILS_NAME
		detailName = self.selenium.findSingleCSS(**kwargs)

		kwargs["selector"] = CSS_DETAILS_MED_IOT
		detailMedIoT = self.selenium.findSingleCSS(**kwargs)

		kwargs["selector"] = CSS_DETAILS_ALL_IOT
		detailAllIoT = self.selenium.findSingleCSS(**kwargs)

		kwargs["selector"] = CSS_DETAILS_SITES
		detailSites = self.selenium.findSingleCSS(**kwargs)

		kwargs["selector"] = CSS_DETAILS_DATA_USAGE
		detailData = self.selenium.findSingleCSS(**kwargs)
		detailDataByte = convertByte(detailData.text)

		kwargs["selector"] = CSS_DETAILS_CRITICAL_ALERTS
		detailCritical = self.selenium.findSingleCSS(**kwargs)

		kwargs["selector"] = CSS_DETAILS_WARNING_ALERTS
		detailWarning = self.selenium.findSingleCSS(**kwargs)

		if detailName.text != name:
			print("Name in details does not match the customers page")
			gotFailures = True
		if int(detailMedIoT.text) != medIoTDevices:
			print("Customer %s detail.  Medical IoT devices %s does not match the customers page %s" % (name, str(medIoTDevices), detailMedIoT.text))
			gotFailures = True
		if int(detailAllIoT.text) != allIoTDevices:
			print("Customer %s detail.  All IoT devices %s does not match the customers page %s" % (name, str(allIoTDevices), detailAllIoT.text))
			gotFailures = True
		if int(detailSites.text) != sites:
			print("Customer %s detail.  Sites %s do not matcht the customers page %s" % (name, str(sites), detailSites.text))
			gotFailures = True
		if abs(detailDataByte - totalDataByte)/totalDataByte * 100 > 5:
			print("Customer %s detail.  Data Usage %s does not match the customers page %s" % (name, str(totalData), detailData.text))
			gotFailures = True
		if int(detailCritical.text) != criticalAlerts:
			print("Customer %s detail.  Critical alerts %s do not match the customers page %s" % (name, str(criticalAlerts), detailCritical.text))
			gotFailures = True
		if int(detailWarning.text) != warningAlerts:
			print("Customer %s detail.  Warning alerts %s do not match the customers page %s" % (name, str(warningAlerts), detailWarning.text))
			gotFailures = True

		return False if gotFailures else True


	def verifyMSSPDashboard(self):
		gotFailures = False
		kwargs = {}

		urlpath = '/#portal-customers' if 'testing' in self.url.netloc else '/portal-customers'
		rcode = self.selenium.getURL(self.url.scheme+'://'+self.url.netloc+urlpath)
		for i in range(0,3):
			kwargs = {"selector":CSS_USER_LINK, "timeout":5}
			if self.selenium.findSingleCSS(**kwargs):
				break
			rcode = self.selenium.getURL(self.url.scheme+'://'+self.url.netloc+urlpath)
		waitLoadProgressDone(self.selenium)

		kwargs= {"selector": CSS_LINKED_NAME, "waittype":"visibility", "timeout":3}
		name = self.selenium.findSingleCSS(**kwargs)
		name = name.text

		kwargs["selector"] = CSS_MEDICAL_IOT_DEVICES
		medIoTDevices = self.selenium.findSingleCSS(**kwargs)
		medIoTDevices = int(medIoTDevices.text)
		
		kwargs["selector"] = CSS_ALL_IOT_DEVICES
		allIoTDevices = self.selenium.findSingleCSS(**kwargs)
		allIoTDevices = int(allIoTDevices.text)

		kwargs["selector"] = CSS_SITES
		sites = self.selenium.findSingleCSS(**kwargs)
		sites = int(sites.text)

		kwargs["selector"] = CSS_TOTAL_DATA
		totalData = self.selenium.findSingleCSS(**kwargs)
		totalData = totalData.text

		kwargs["selector"] = CSS_CRITICAL_ALERTS
		criticalAlerts = self.selenium.findSingleCSS(**kwargs)
		criticalAlerts = int(criticalAlerts.text)

		kwargs["selector"] = CSS_WARNING_ALERTS
		warningAlerts = self.selenium.findSingleCSS(**kwargs)
		warningAlerts = int(warningAlerts.text)

		kwargs["selector"] = CSS_MEDIUM_RISK
		mediumRisk = self.selenium.findSingleCSS(**kwargs)
		mediumRisk = int(mediumRisk.text)

		kwargs["selector"] = CSS_HIGH_RISK
		highRisk = self.selenium.findSingleCSS(**kwargs)
		highRisk = int(highRisk.text)

		url = urlparse(self.params["url"])
		rcode = self.selenium.getURL(url.scheme+'://'+url.netloc+'/')	
		
		kwargs["selector"] = CSS_DASHBOARD_IOT_SELECT_BUTTON
		rcode = self.selenium.findSingleCSS(**kwargs)
		rcode.click()
		waitLoadProgressDone(self.selenium)

		kwargs["selector"] = CSS_DASHBOARD_ALL_IOT_DEVICES
		dashboardAllIoT = self.selenium.findSingleCSS(**kwargs)
		dashboardAllIoT = int(dashboardAllIoT.text)

		kwargs["selector"] = CSS_DASHBOARD_SITES
		dashboardSites = self.selenium.findSingleCSS(**kwargs)
		dashboardSites = dashboardSites.text
		dashboardSites = int(dashboardSites[dashboardSites.find("(")+1:dashboardSites.find(")")])

		kwargs["selector"] = CSS_DASHBOARD_DATA
		dashboardData = self.selenium.findSingleCSS(**kwargs)
		dashboardData = float(dashboardData.text)

		kwargs["selector"] = CSS_DASHBOARD_HIGH_RISK
		dashboardHighRisk = self.selenium.findSingleCSS(**kwargs)
		dashboardHighRisk = int(dashboardHighRisk.text)

		kwargs["selector"] = CSS_DASHBOARD_MEDIUM_RISK
		dashboardMediumRisk = self.selenium.findSingleCSS(**kwargs)
		dashboardMediumRisk = int(dashboardMediumRisk.text)

		url = urlparse(self.params["url"])
		rcode = self.selenium.getURL(url.scheme+'://'+url.netloc+'/policiesalerts/alerts?interval=oneday')

		kwargs["selector"] = CSS_ALERTS_SEVERITY_SELECTION
		rcode = self.selenium.findSingleCSS(**kwargs)
		rcode.click()
		waitLoadProgressDone(self.selenium)

		kwargs["selector"] = CSS_SEVERITY_SELECT
		rcode = self.selenium.findMultiCSS(**kwargs)
		rcode[4].click()
		waitLoadProgressDone(self.selenium)
		
		kwargs= {"selector": CSS_ALERTS, "waittype":"visibility", "timeout":3}
		dashboardCritical = self.selenium.findSingleCSS(**kwargs)
		dashboardCritical = dashboardCritical.text	
		dashboardCritical = int(dashboardCritical[dashboardCritical.find("(")+1:dashboardCritical.find(")")])
		
		kwargs["selector"] = CSS_ALERTS_SEVERITY_SELECTION
		rcode = self.selenium.findSingleCSS(**kwargs)
		rcode.click()
		waitLoadProgressDone(self.selenium)

		kwargs["selector"] = CSS_SEVERITY_SELECT
		rcode = self.selenium.findMultiCSS(**kwargs)
		rcode[6].click()
		waitLoadProgressDone(self.selenium)

		kwargs["selector"] = CSS_ALERTS
		dashboardWarning = self.selenium.findSingleCSS(**kwargs)
		dashboardWarning = dashboardWarning.text	
		dashboardWarning = int(dashboardWarning[dashboardWarning.find("(")+1:dashboardWarning.find(")")])

		if allIoTDevices != dashboardAllIoT:
			print("Customer All IoT Devices %s does not match in dashboard %s" % (str(allIoTDevices), str(dashboardAllIoT)))
			gotFailures = True
		if sites != dashboardSites:
			print("Customer Sites %s do not match in dashboard %s" % (str(sites), str(dashboardSites)))
			gotFailures = True
		if totalData != dashboardData:
			print("Customer Total data %s does not match in dashboard %s" % (str(totalData), str(dashboardData)))
			gotFailures = True
		if highRisk != dashboardHighRisk:
			print("Customer High Risk %s does not match in dashboard %s" % (str(highRisk), str(dashboardHighRisk)))
			gotFailures = True
		if mediumRisk != dashboardMediumRisk:
			print("Customer Medium Risk %s does not match in dashboard %s" % (str(mediumRisk), str(dashboardMediumRisk)))
			gotFailures = True
		if criticalAlerts != dashboardCritical:
			print("Customer Critical Alerts %s do not match in dashboard %s" % (str(criticalAlerts), str(dashboardCritical)))
			gotFailures = True
		if warningAlerts != dashboardWarning:
			print("Customer Warning Alerts %s do not match in dashboard %s" % (str(warningAlerts), str(dashboardWarning)))
			gotFailures = True

		return False if gotFailures else True

	def close(self):
		if self.selenium:
			self.selenium.quit()
