#!/usr/bin/python

# global CSS parameters for SOC Dashboard
CSS_ALERT_SUMMARY = ".alert-total-wrap > div.alerts-item > span.number-text"
CSS_DATA_SUMMARY = ".data-total-wrap > div.data-item > div.data-item-inner > div.data-item-right > div.layout-row > span"
CSS_SERIES_BAR = "g.highcharts-series rect"
CSS_SITE_WIDGET = "md-card.carousel-item"
CSS_SITE_ALERT = "div.carousel-item-below > div.site-alerts > div > div.level-value"
CSS_SITE_ALERT_HIGH = 'div.alert-level.high > div'
CSS_SITE_ALERT_MED = 'div.alert-level.warning > div'
CSS_SITE_ALERT_LOW = 'div.alert-level.caution > div'
CSS_SITE_ALERT_INFO = 'div.alert-level.info > div'
CSS_SITE_STATUS = 'div.site-header  > div[ng-show="site.loaded"] > i[ng-if]'
CSS_SITE_MED_IOT = 'div[ng-bind="site.flashdata.devicesAgg.medIoTDevices"]'
CSS_SITE_ALL_IOT = 'div[ng-bind="site.flashdata.devicesAgg.total_IoT_devices || 0"]'
CSS_SITE_RISK_CRITICAL = 'div.risk-3.risk-level'
CSS_SITE_RISK_MED = 'div.risk-1.risk-level'
CSS_SITE_RISK_HIGH = 'div.risk-2.risk-level'
CSS_SITE_INSP_UPTIME = "span.primary.uptime"
CSS_SITE_INSP_DETAIL = "div.site-inspector-list > div.list-row > div.primary"
CSS_SITE_CPUMEM = 'div[ng-show="site.loaded"] > div > div > md-progress-linear[role="progressbar"]'
CSS_ALERT_WIDGET = "div.alert-list"
CSS_ALERT_TOTAL_COUNT = "div.alert-list-title.title.ng-binding"
CSS_TOP_DEVICES_WIDGET = "div.risk-assessment"
CSS_TOP_DEVICES_DATA = 'div[ng-repeat="item in socAppDeviceCtrl.devices"] > span'
CSS_TOP_DEVICES_DEST = 'div[ng-repeat="item in socAppDeviceCtrl.apps"] > span'
CSS_RISK_COUNT = "div.risk-number"
CSS_EXTERNAL_ENDPOINT_TOTAL_COUNT = "zing-map-base > div > md-card > md-card-title > .title-text > span.ng-binding.ng-scope"


from urllib.parse import urlparse
from selenium.common.exceptions import StaleElementReferenceException
from ui.login.zbUILoginCore import Login
from common.zbCommon import validateDataNotEmpty
from ui.zbUIShared import waitLoadProgressDone
from locator.soc import SOCSelectors
import time, pdb
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SOCDashboard():

	def __init__(self, **kwargs):
		self.params = kwargs

		if "browserInstance" not in kwargs:
			self.selenium = Login(**kwargs).login()
		else:
			self.selenium = kwargs["browserInstance"]

		url = urlparse(self.params["url"])
		rcode = self.selenium.getURL(url.scheme+'://'+url.netloc+'/soc')
		time.sleep(2)
		if rcode: waitLoadProgressDone(self.selenium)

	def checkSmoke(self):
		rcode = self.selenium.findSingleCSS(selector=SOCSelectors.CSS_SOC_BOLD_BAR)
		for l in SOCSelectors.check_left_top:
			if l not in rcode.text:
				logging.critical("SOC top left bar missing label {}".format(l))
				return False
		rcode = self.selenium.findSingleCSS(selector=SOCSelectors.CSS_SOC_RIGHT_BAR)
		for r in SOCSelectors.check_right_top:
			if r not in rcode.text:
				logging.critical("SOC top right bar missing label {}".format(r))
				return False
		
		'''
		Element doesn't exist
		try:
			rcode = self.selenium.findSingleCSS(selector=SOCSelectors.CSS_SOC_CHART_CONTAINER)
			rcode2 = self.selenium.findSingleCSS(browserobj=rcode,selector=SOCSelectors.CSS_SOC_CHART_BAR)
			if not rcode or not rcode2:
				logging.critical("SOC missing chart elements")
				return False
		except:
			logging.critical("SOC missing chart elements")
			assert False
		'''
		rcode = self.selenium.findSingleCSS(selector=SOCSelectors.CSS_SOC_ALERT_LIST)
		for word in SOCSelectors.check_alerts:
			if word not in rcode.text:
				logging.critical("SOC missing alert label {}".format(word))
				return False
		rcode = self.selenium.findSingleCSS(selector=SOCSelectors.CSS_SOC_MAP)
		for word in SOCSelectors.check_map:
			if word not in rcode.text:
				logging.critical("SOC missing map label {}".format(word))
				return False
		rcode2 = self.selenium.findSingleCSS(browserobj=rcode,selector=SOCSelectors.CSS_PATH)
		if not rcode2:
			logging.critical("SOC missing map elements")
			return False
		return True










	def checkAlertSummary(self):
		resultDict = {}
		self.params["selector"] = CSS_ALERT_SUMMARY
		self.params["waittype"] = "visibility"
		result = self.selenium.findMultiCSS(**self.params)

		if not result:
			print("Alert Summary missing data for selector "+self.params["selector"])
			return False
		else:
			for i in range (0, 3):
				field = result[i].text
				if i == 0: resultDict["critical"] = field
				if i == 1: resultDict["warning"] = field
				if i == 2: resultDict["caution"] = field
				if i == 3: resultDict["info"] = field

		print("Alert Summary is "+str(resultDict))
		result = validateDataNotEmpty(resultDict)		
		return result

	def checkDataSummary(self):
		#if iteration >= 3: return False

		resultDict = {}
		self.params["selector"] = CSS_DATA_SUMMARY
		self.params["waittype"] = "visibility"
		result = self.selenium.findMultiCSS(**self.params)
		if not result:
			print("Data Summary missing data for selector "+self.params["selector"])
			return False
		else:
			for i in range(0, 5):
				field = result[i].text
				if i == 0: resultDict["newdevice"] = field
				if i == 1: resultDict["totaldevice"] = field
				if i == 2: resultDict["vlan"] = field
				if i == 3: resultDict["app"] = field
				if i == 4: resultDict["data"] = field

		print("Data Summary is "+str(resultDict))
		result = validateDataNotEmpty(resultDict)
		return result



	def checkSeriesGraphWidget(self):
		resultDict = {}
		self.params["selector"] = CSS_SERIES_BAR
		self.params["waittype"] = "located"
		result = self.selenium.findMultiCSS(**self.params)

		if not result:
			return False
		else:
			if len(result) <= 0:
				print("Series graph missing data for selector "+self.params["selector"])
				return False
			else:
				resultDict["totalbar"] = len(result)

		print("Series graph is "+str(resultDict))
		result = validateDataNotEmpty(resultDict)
		return result


	def checkSiteWidget(self):
		resultDict = {}

		selectors = [CSS_SITE_WIDGET,
					CSS_SITE_ALERT,
					CSS_SITE_ALERT_HIGH,
					CSS_SITE_ALERT_MED,
					CSS_SITE_ALERT_LOW,
					CSS_SITE_ALERT_INFO,
					CSS_SITE_STATUS,
					CSS_SITE_MED_IOT,
					CSS_SITE_ALL_IOT,
					CSS_SITE_RISK_CRITICAL,
					CSS_SITE_RISK_MED,
					CSS_SITE_RISK_HIGH,
					CSS_SITE_INSP_UPTIME,
					CSS_SITE_INSP_DETAIL,
					CSS_TOP_DEVICES_DATA]
		
		for selector in selectors:
			self.params["selector"] = selector
			self.params["waittype"] = "located"
			for i in range(0,3):
				try:
					result = self.selenium.findSingleCSS(**self.params)
					#waitLoadProgressDone(self.selenium)
					break
				except StaleElementReferenceException:
					pass

			if not result:
				print("Site card missing data for selector "+selector)
				return False
			else:
				if selector == CSS_SITE_WIDGET: keyname = "name"
				if selector == CSS_SITE_ALERT:  keyname = "alert"
				if selector == CSS_SITE_ALERT_HIGH:  keyname = "alerthigh"
				if selector == CSS_SITE_ALERT_MED:  keyname = "alertmedium"
				if selector == CSS_SITE_ALERT_LOW:  keyname = "alertlow"
				if selector == CSS_SITE_ALERT_INFO:  keyname = "alertinfo"
				if selector == CSS_SITE_STATUS:  keyname = "status"
				if selector == CSS_SITE_MED_IOT:  keyname = "medical"
				if selector == CSS_SITE_ALL_IOT:  keyname = "alliot"
				if selector == CSS_SITE_RISK_CRITICAL:  keyname = "riskcritical"
				if selector == CSS_SITE_RISK_MED:  keyname = "riskmed"
				if selector == CSS_SITE_RISK_HIGH:  keyname = "riskhigh"
				if selector == CSS_SITE_INSP_UPTIME:  keyname = "inspuptime"
				if selector == CSS_SITE_INSP_DETAIL:  keyname = "inspdetail"
				if selector == CSS_SITE_CPUMEM:  keyname = "cpumem"
				resultDict[keyname] = result.text

		print("Site widget is "+str(resultDict))
		result = validateDataNotEmpty(resultDict)
		return result


	def checkAlertWidget(self): 
		resultDict = {}
		self.params["selector"] = CSS_ALERT_WIDGET
		self.params["waittype"] = "visibility"
		result = self.selenium.findSingleCSS(**self.params)
		if not result:
			print("Alert widget missing data for selector "+self.params["selector"])
			return False
		else:
			text = result.text
			resultDict["total"] = text

		print("Alert widget is "+str(resultDict))
		result = validateDataNotEmpty(resultDict)
		return result


	def checkTopDevicesWidget(self):
		self.params["selector"] = CSS_TOP_DEVICES_WIDGET
		self.params["waittype"] = "visibility"
		result = self.selenium.findSingleCSS(**self.params)

		if result:
			self.params["selector"] =CSS_TOP_DEVICES_DATA
			resultData = self.selenium.findMultiCSS(**self.params)

		if result:
			self.params["selector"] =CSS_TOP_DEVICES_DEST
			resultDest = self.selenium.findMultiCSS(**self.params)

		if not result:
			print("Top Devices widget missing data for selector "+self.params["selector"])
			return False
		else:
			counter = 1
			dataDict = {}
			for data in resultData:
				dataDict[str(counter)] = data.text
				counter += 1

			counter = 1
			destDict = {}
			for dest in resultDest:
				destDict[str(counter)] = dest.text
				counter += 1
				
		print("Top Devices data is "+str(resultData))
		print("Top Devices destination is "+str(resultDest))
		result = validateDataNotEmpty(dataDict) and validateDataNotEmpty(destDict)
		return result


	def checkExternalEndpointWidget(self):
		resultDict = {}
		self.params["selector"] = CSS_EXTERNAL_ENDPOINT_TOTAL_COUNT
		self.params["waittype"] = "visibility"
		result = self.selenium.findSingleCSS(**self.params)
		if not result:
			print("External Endpoint missing data for selector "+self.params["selector"])
			return False
		else:
			text = result.text
			resultDict["total"] = text

		print("External Endpoint is "+str(resultDict))
		result = validateDataNotEmpty(resultDict)
		return result

	def close(self):
		if self.selenium:
			self.selenium.quit()
