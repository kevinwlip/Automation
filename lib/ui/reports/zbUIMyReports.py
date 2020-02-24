#!/usr/bin/python

import re
import sys
import os
from urllib.parse import urlparse
from ui.login.zbUILoginCore import Login
from ui.zbUIShared import waitLoadProgressDone
from common.zbCommon import fuzzyRegexSearch
import time, pdb
from selenium.common.exceptions import WebDriverException, StaleElementReferenceException
from zbAPI import zbAPI
from common.zbFile import ReadFile


#tab-content-35 > div > md-content > zing-report-list > div > md-card > div:nth-child(2) > zing-list > div > div:nth-child(1) > div.list-row-content.list-slide-fade > div > div > div > div > div.sub-content.layout-align-space-between-stretch.layout-row > div:nth-child(2) > div:nth-child(1) > div.zing-text-align-right.ng-binding.flex-15

# CSS
CSS_REPORT_CONFIG_LIST = "md-select[ng-model='reportListCtrl.selectedConfig']"
CSS_REPORT_CONFIG_LIST_SELECT = "md-option[ng-repeat='item in reportListCtrl.reportConfigOptions'] > div.md-text"
CSS_SUMMARY_REPORT_ROWS = "div[class='report-row-header ng-scope SUMMARY_REPORT-report-row-header']"
CSS_ALERT_DEVICES = "div:nth-child(2) > div > div.zing-text-align-right.ng-binding"#"div[class='alert-number']"
CSS_TOTAL_ALERTS = "div.layout-align-space-between-stretch.layout-row > div.zing-text-align-right.ng-binding" #"div[ng-bind='item.alerts.low + item.alerts.medium + item.alerts.high']"
CSS_TOTAL_DEVICES ="div.sub-title.layout-align-space-between-center.layout-row > div:nth-child(3) > div.zing-text-align-right.ng-binding" #element 1,3,5...
CSS_IOT_DEVICES = "div[ng-bind='item.iotdevices']"
CSS_NONIOT_DEVICES = "div[ng-bind='item.noniotdevices']"
CSS_NEWIOT_DEVICES = "div[ng-bind='item.iotdevicesnew']"
CSS_NEWNONIOT_DEVICES = "div[ng-bind='item.noniotdevicesnew']"
CSS_DESTINATION_AND_APPS = " div:nth-child(4) > div:nth-child(1) > div.zing-text-align-right.ng-binding" #"div[class='zing-text-align-right text-strong ng-binding flex-45']" #destination element #0
CSS_DATA_USAGE = "span[class='text-strong ng-binding']"
CSS_VIEW_PDF = "div.zing-link.mr10"
CSS_CONNECT_VLAN = ".connectivity-report-summary-main-section-vlan div.connectivity-report-summary-main-section-number.ng-binding"
CSS_REPORT_ROW_COMPLETE = "div.report-row-header.ng-scope"
CSS_OPEN_REPORT_BUTTON = ".mr10[role='button'][tabindex='0']"

CSS_FREQUENCIES_DROPDOWN = '.report-list md-select[ng-model="reportListCtrl.frequency"]'
CSS_FREQUENCIES_WEEKLY_OPTION = 'md-option[value="WEEKLY"]'
rowsSelectorForReportType = {
	'connectivity': 'div.CONNECTIVITY_REPORT-report-row-header',
	'summary': 'div.SUMMARY_REPORT-report-row-header'
}

# Using these keyword to search Report image.
# Note that some words are truncate due to the fact that image parsing is not stable, 
# so I'm reducing word length to make less false positive
keywordsForReportType = {
	'connectivity': [  #NOTE: TESSERACT-OCR IS NOT GOOD WITH THICk LETTERING
		#'WEEKLY',
		'Connectivity Report',
		'Network Status',
		#'Total VLANs',
		#'Device Groups',
		'Total Devices',
		'oT Devices',
		'Inspectors',
		'Categories',
		#'Profiles',
		'Device Count',
		'VLAN Summary',
		'Monitoring',
		'First Seen',
		#'Last Seen'
	],
	'summary': [
		'WEEKLY',
		'SUMMARY',
		'SCOPE',
		'RISK ASSESSMENT',
		'High',
		'Medium',
		'Low',
		'SECURITY INCIDENTS',
		'Alerts',
		'Critical',
		#'Warning',
		#'Caution',
		'Info',
		'DEVICE DISCOVERY',
		'Devices',
		'Categories',
		#'NETWORK & APPS',
		'Applications',
		'DATA USAGE',
		'Data Usage',
		'DEVICES BY CATEGORY',
		'TOP 10 BY',
		'Destinations',
		'Applications',
		'SECURITY INCIDENTS'
	]
}

CSS_MOCK_REPORT_HEADING_NAME = 'zing-report-header .report-header .report-title'
CSS_MOCK_REPORT_HEADING_CALENDAR_NUM = 'zing-report-header .report-header .calendar-number'
CSS_MOCK_REPORT_HEADING_DATE = 'zing-report-header .report-header .report-time-range-title'
CSS_MOCK_REPORT_STATUS_DATE = '.report-pdf-page-content .connectivity-report-network-status-date'
CSS_MOCK_REPORT_STATUS_HEADING_NUMBERS = '.connectivity-report-summary-main-section .text-right'
CSS_MOCK_REPORT_STATUS_VLAN_NUMBERS = '.connectivity-report-summary-main-row .connectivity-report-summary-main-section-vlan .connectivity-report-summary-main-section-number'
CSS_MOCK_REPORT_STATUS_NUMBERS = '.connectivity-report-summary-main-row .connectivity-report-summary-main-section-number'
CSS_MOCK_REPORT_DEVICE_GROUP_ROWS = '.connectivity-report-summary-main-row div.connectivity-report-summary-main-section.connectivity-report-summary-main-section-groups'
CSS_MOCK_REPORT_DEVICE_GROUP_DISPLAY_NUM = 'div.connectivity-report-summary-main-section-number' # Search under CSS_MOCK_REPORT_DEVICE_GROUP_ROWS

CSS_MOCK_REPORT_INSPECTORS_AGG = 'g.highcharts-series-group' #'#highcharts-0 g.highcharts-series-group'
CSS_MOCK_REPORT_INSPECTORS_NAME_AND_COUNT = "[ng-repeat='inspector in ctrl.inspectorList'] .ng-binding" #'.device-count-left-card div.ng-binding'
CSS_MOCK_REPORT_CATEGORIES_AGG = 'g.highcharts-series-group'#'#highcharts-2 g.highcharts-series-group'
CSS_MOCK_REPORT_CATEGORIES_NAME_AND_COUNT = "[ng-repeat='category in ctrl.categoryGroup[item.value]'] .ng-binding" #'.device-count-middle-card div.ng-binding'
CSS_MOCK_REPORT_CATEGORIES = ".device-count-card-category-name"
CSS_MOCK_REPORT_PROFILES_AGG = 'g.highcharts-series-group'#'#highcharts-4 g.highcharts-series-group'
CSS_MOCK_REPORT_PROFILES_NAME_AND_COUNT = "[ng-repeat='profile in ctrl.profileGroup[item.value]'] .ng-binding" #'.device-count-right-card div.ng-binding'
CSS_MOCK_REPORT_PROFILES = ".device-count-card-profile-name"

CSS_MOCK_REPORT_VLANS_STATUS_COUNTS = '.connectivity-report-monitoring-header .connectivity-report-monitoring-stats div.ng-binding'
CSS_MOCK_REPORT_VLANS = '.connectivity-report-monitoring-table-vlan-column div.ng-binding'
CSS_MOCK_REPORT_VLANS_NUMERIC_INFO = '.connectivity-report-monitoring-table-generic-column.flex-10 div.ng-binding'
CSS_MOCK_REPORT_VLANS_DATE_INFO = '.connectivity-report-monitoring-table-generic-column.flex-15 div.ng-binding'

CSS_MOCK_SUMMARY_BARS = 'g.highcharts-series.highcharts-series-0 rect.highcharts-point.highcharts-color-0' #'#highcharts-0 .highcharts-series rect'
CSS_MOCK_SUMMARY_BARS_TOOLTIP = '#highcharts-0 div.highcharts-tooltip'
CSS_MOCK_SUMMARY_BARS_DATE = 'g.highcharts-axis-labels tspan'

CSS_MOCK_SUMMARY_SECURITY_INCIDENT_CARDS = '.device-discovery md-card'
CSS_MOCK_SUMMARY_SECURITY_INCIDENT_ALERT_TEXT = 'div.flex-80' # Search under CSS_MOCK_SUMMARY_SECURITY_INCIDENT_CARDS
CSS_MOCK_SUMMARY_SECURITY_INCIDENT_ALERT_NUMBER = '.alert-number' # Search under CSS_MOCK_SUMMARY_SECURITY_INCIDENT_CARDS

CSS_MOCK_SUMMARY_RISK_ASSESSMENT_NUMBERS = '.summary-first-box .bold-text'
CSS_MOCK_SUMMARY_ALERTS_TOTAL_COUNT = '.risk-number'
CSS_MOCK_SUMMARY_DEVICE_DISCOVERY_COUNT = '.report-item .zing-text-align-left'
CSS_MOCK_SUMMARY_VLAN_COUNT = 'div[ng-bind="summaryReportCtrl.dashboardSeriesaggData.vlans_subnets"]'
CSS_MOCK_SUMMARY_APPLICATIONS_COUNT = 'div[ng-bind="summaryReportCtrl.dashboardSeriesaggData.app_protocols"]'
CSS_MOCK_SUMMARY_DEVICE_CATEGORY_COUNT = '.zing-text-align-right.flex-25'
CSS_MOCK_SUMMARY_DEVICE_CATEGORY_PERCENTAGE = '.report-item .flex-30 div.flex-30.ng-binding'
CSS_MOCK_SUMMARY_DEVICE_DESTINATION_AND_APPLICATIONS_COUNT = '.report-item [layout-align="space-between"] div.right-text.flex-30'
CSS_MOCK_SUMMARY_DEVICE_DATA_USAGE_COUNT = '.report-item div.right-text.ng-binding.flex-40'

def _isValidText(browserobj, selector, errMsg='zbUIMyReports/_isValidText: invalid text.', strict=True, fromobj=None):
	texts = browserobj.findMultiCSSFromBrowserobj(browserobj=fromobj, selector=selector, timeout=3)
	if not texts:
		print(('zbUIMyReports/_isValidText: text not found. ({})'.format(selector)))
		return strict == False
	for text in texts:
		text = text.text
		if not text or text == '':
			print(('zbUIMyReports/_isValidText: text is {}'.format(text)))
			print(errMsg)
			return False
	return True

def _isValidCount(browserobj, selector, errMsg='zbUIMyReports/_isValidCount: invalid count {}.', strict=True, fromobj=None):
	numbers = browserobj.findMultiCSSFromBrowserobj(browserobj=fromobj, selector=selector, timeout=3)
	if not numbers:
		print(('zbUIMyReports/_isValidCount: text not found. ({})'.format(selector)))
		return strict == False
	for number in numbers:
		number = number.text
		if number.isdigit() is False or int(number) < 0:
			print(('zbUIMyReports/_isValidCount: number is {}'.format(number)))
			print((errMsg + ' ' + selector))
			return False
	return True

def checkHeadingInfo(browserobj):
	rcode = True
	rcode = rcode and _isValidText(
		browserobj,
		CSS_MOCK_REPORT_HEADING_NAME,
		'zbUIMyReports/checkHeadingInfo: report heading name is invalid.'
	)
	rcode = rcode and _isValidCount(
		browserobj,
		CSS_MOCK_REPORT_HEADING_CALENDAR_NUM,
		'zbUIMyReports/checkHeadingInfo: report heading calendar number is invalid.'
	)
	rcode = rcode and _isValidText(
		browserobj,
		CSS_MOCK_REPORT_HEADING_DATE,
		'zbUIMyReports/checkHeadingInfo: report heading date is invalid.'
	)
	return rcode

def checkNetworkStatus(browserobj):
	rcode = True
	date = browserobj.getText(selector=CSS_MOCK_REPORT_STATUS_DATE)
	if not date or date == '':
		print('zbUIMyReports/checkNetworkStatus: report network status date not found.')
		return False
	match = re.search(r'(\S+ \d+, \d+)', date)
	if match is None:
		print('zbUIMyReports/checkNetworkStatus: report network status date not in format "Sept 30, 2017".')
		return False

	# Check network status heading numbers
	rcode = rcode and _isValidCount(
		browserobj,
		CSS_MOCK_REPORT_STATUS_HEADING_NUMBERS,
		'zbUIMyReports/checkNetworkStatus: report network status heading number is not a valid number.'
	)

	# Check network status vlan counts
	rcode = rcode and _isValidCount(
		browserobj,
		CSS_MOCK_REPORT_STATUS_VLAN_NUMBERS,
		'zbUIMyReports/checkNetworkStatus: report network status vlan number is not a valid number.'
	)
	totalVlanCount = browserobj.getText(selector=CSS_MOCK_REPORT_STATUS_HEADING_NUMBERS)
	vlanCounts = browserobj.findMultiCSS(selector=CSS_MOCK_REPORT_STATUS_VLAN_NUMBERS)
	if not vlanCounts:
		print('zbUIMyReports/checkNetworkStatus: vlan counts does not exist (CSS_MOCK_REPORT_STATUS_VLAN_NUMBERS).')
		return False
	totalSum = 0
	for vlanCount in vlanCounts:
		totalSum = totalSum + int(vlanCount.text)
	if int(totalVlanCount) != int(totalSum):
		print(('zbUIMyReports/checkNetworkStatus: vlan counts does not sum up to total count {}.'.format(totalVlanCount)))
		return False

	# Check other numbers in network status
	rcode = rcode and _isValidCount(
		browserobj,
		CSS_MOCK_REPORT_STATUS_NUMBERS,
		'zbUIMyReports/checkNetworkStatus: report network status number is not a valid number.'
	)

	# Check if categories and profiles reflect correct number
	deviceGroupRows = browserobj.findMultiCSS(selector=CSS_MOCK_REPORT_DEVICE_GROUP_ROWS)
	if not deviceGroupRows or len(deviceGroupRows) < 2:
		print('zbUIMyReports/checkNetworkStatus: Missing device group categories or profiles rows.')
		return False
	categoriesDisplayNum = browserobj.getText(browserobj=deviceGroupRows[0], selector=CSS_MOCK_REPORT_DEVICE_GROUP_DISPLAY_NUM)
	profilesDisplayNum = browserobj.getText(browserobj=deviceGroupRows[1], selector=CSS_MOCK_REPORT_DEVICE_GROUP_DISPLAY_NUM)
	categories = browserobj.findMultiCSS(selector=CSS_MOCK_REPORT_CATEGORIES)
	profiles = browserobj.findMultiCSS(selector=CSS_MOCK_REPORT_PROFILES)
	if not categories:
		categories = []
	if not profiles:
		profiles = []
	if int(categoriesDisplayNum) != len(categories): #/2:
		print(('zbUIMyReports/checkNetworkStatus: Categories count {} does not match display value {}.'.format(len(categories), categoriesDisplayNum)))
		rcode = False
	if int(profilesDisplayNum) != len(profiles): #/2:
		print(('zbUIMyReports/checkNetworkStatus: Profiles count {} does not match display value {}.'.format(len(profiles), profilesDisplayNum)))
		rcode = False
	return rcode

def checkNetworkStatusDeviceCounts(browserobj):
	rcode = True
	rcode = rcode and _checkDeviceCounts(browserobj, CSS_MOCK_REPORT_INSPECTORS_AGG, CSS_MOCK_REPORT_INSPECTORS_NAME_AND_COUNT)
	rcode = rcode and _checkDeviceCounts(browserobj, CSS_MOCK_REPORT_CATEGORIES_AGG, CSS_MOCK_REPORT_CATEGORIES_NAME_AND_COUNT)
	rcode = rcode and _checkDeviceCounts(browserobj, CSS_MOCK_REPORT_PROFILES_AGG, CSS_MOCK_REPORT_PROFILES_NAME_AND_COUNT)
	return rcode

def _checkDeviceCounts(browserobj, aggSelector, nameAndCountSelector):
	aggChart = browserobj.findSingleCSS(selector=aggSelector)
	if not aggChart:
		print('zbUIMyReports/_checkDeviceCounts: agg chart not found.')
		return False
	nameAndCount = browserobj.findMultiCSS(selector=nameAndCountSelector)
	previousCount = sys.maxsize

	for name, count in zip(nameAndCount[0::2], nameAndCount[1::2]):
		if name.text == '':
			print(('zbUIMyReports/_checkDeviceCounts: name {} is empty.'.format(name.text)))
			return False
		count = count.text
		if count == '' or count.isdigit() is False or int(count) < 0:
			print(('zbUIMyReports/_checkDeviceCounts: count {} is not valid.'.format(count)))
			return False
		# skip this check because categories are sorted by category type and resets desc order
		'''
		count = int(count)
		if count > previousCount:
			print('zbUIMyReports/_checkDeviceCounts: count {} is not in descending order {}, {}.'.format(previousCount, count))
			return False
		previousCount = count
		'''
	return True

def checkVLANSummary(browserobj):
	rcode = True
	rcode = rcode and _checkVlanCount(browserobj)
	rcode = rcode and _checkVlans(browserobj)
	rcode = rcode and _checkVlanNumericInfo(browserobj)
	rcode = rcode and _checkVlanDateInfo(browserobj)
	return rcode

def _checkVlanCount(browserobj):
	rcode = True
	rcode = rcode and _isValidCount(
		browserobj,
		CSS_MOCK_REPORT_VLANS_STATUS_COUNTS,
		'zbUIMyReports/_checkVlanCount: count is not valid.'
	)
	counts = browserobj.findMultiCSS(selector=CSS_MOCK_REPORT_VLANS_STATUS_COUNTS)
	totalCount = int(counts[-1].text)
	if totalCount == 0:
		return True
	vlans = browserobj.findMultiCSS(selector=CSS_MOCK_REPORT_VLANS)
	if not vlans or len(vlans) != totalCount:
		print(('zbUIMyReports/_checkVlanCount: total vlan count {} does not match displayed value {}.'.format(len(vlans), totalCount)))
		return False
	return rcode

def _checkVlans(browserobj):
	vlans = browserobj.findMultiCSS(selector=CSS_MOCK_REPORT_VLANS)
	if not vlans:
		print('zbUIMyReports/_checkVlans: no vlans found.')
		# No vlan is also ok.
		return True
	for vlan in vlans:
		vlan = vlan.text
		match = re.search(r'(\d+\.\d+\.\d+\.\d+\/\d)', vlan)
		if match is None:
			print('zbUIMyReports/_checkVlans: vlan not in format "10.14.210.0/23".')
			return False
	return True

def _checkVlanNumericInfo(browserobj):
	return _isValidCount(
		browserobj,
		CSS_MOCK_REPORT_VLANS_NUMERIC_INFO,
		'zbUIMyReports/_checkVlanNumericInfo: count is not valid.',
		strict=False
	)

def _checkVlanDateInfo(browserobj):
	# Check first seen and latest seen info
	dateInfo = browserobj.findMultiCSS(selector=CSS_MOCK_REPORT_VLANS_DATE_INFO)
	if not dateInfo:
		print('zbUIMyReports/_checkVlanDateInfo: vlan date info not found.')
		# No numeric info when no vlan.
		return True
	for date in dateInfo:
		date = date.text
		if date == '':
			print('zbUIMyReports/_checkVlanDateInfo: date is empty')
			return False
		match = re.search(r'(\d+\-\S+\-\d+\ \d+\:\d+\ \S+)', date)
		if match is None:
			print('zbUIMyReports/_checkVlans: vlan not in format "2017-Apr-17 06:04 am".')
			return False
	return True

def checkBarChart(browserobj):
	bars = browserobj.findMultiCSS(selector=CSS_MOCK_SUMMARY_BARS)
	if not bars:
		print('zbUIMyReports/checkBarChart: No data usage bars found.')
		return False
	tooltipTextHeadings = ['Tx', 'Rx', 'Total']
	for bar in bars:
		browserobj.hoverElement(bar)
		tooltipText = browserobj.getText(selector=CSS_MOCK_SUMMARY_BARS_TOOLTIP)
		match = re.search(r'(\S+ \d+, \d+)', tooltipText)
		if not match:
			print(('zbUIMyReports/checkBarChart: Tooltip text date is invalid. ({})'.format(tooltipText)))
			return False
		for heading in tooltipTextHeadings:
			match = re.search(r'({}\:\ \d+\S+)'.format(heading), tooltipText)
			if not match:
				print(('zbUIMyReports/checkBarChart: Tooltip text is invalid. ({})'.format(tooltipText)))
				return False
	# Check dates as well
	dates = browserobj.findMultiCSS(selector=CSS_MOCK_SUMMARY_BARS_DATE)
	if not dates:
		print('zbUIMyReports/checkBarChart: No dates found in x-axis.')
		return False
	for date in dates:
		date = date.text
		match = re.search(r'(\d\S+, \d+/\d+)', date)
		if not match:
			print(('zbUIMyReports/checkBarChart: dates in x-axis {} does not match format "12am, 08/10".'.format(date)))
			return False
	return True

def checkSecurityIncidents(browserobj):
	rcode = True
	cards = browserobj.findMultiCSS(selector=CSS_MOCK_SUMMARY_SECURITY_INCIDENT_CARDS)
	if not cards:
		print('zbUIMyReports/checkSecurityIncidents: No security incident cards found.')
		return False
	for card in cards:
		rcode =  rcode and _isValidText(
			browserobj,
			CSS_MOCK_SUMMARY_SECURITY_INCIDENT_ALERT_TEXT,
			'zbUIMyReports/checkSecurityIncidents: incident text is invalid.',
			strict=False,
			fromobj=card
		)
		alertNumber = browserobj.getText(browserobj=card, selector=CSS_MOCK_SUMMARY_SECURITY_INCIDENT_ALERT_NUMBER)
		if int(alertNumber) != 0:
			alerts = browserobj.findMultiCSSFromBrowserobj(browserobj=card, selector=CSS_MOCK_SUMMARY_SECURITY_INCIDENT_ALERT_TEXT)
			rcode = rcode and len(alerts) == int(alertNumber)
	return rcode

def checkSummaryNumbers(browserobj):
	rcode = True
	rcode = rcode and _checkRiskAssessmentNumbers(browserobj)
	rcode = rcode and _checkSecurityIncidentsNumbers(browserobj)
	rcode = rcode and _checkNetworkAndAppsNumbers(browserobj)
	rcode = rcode and _checkDeviceDiscoveryNumbers(browserobj)
	rcode = rcode and _checkDeviceDiscoveryTop10s(browserobj)
	return rcode

def _checkRiskAssessmentNumbers(browserobj):
	return _isValidCount(
		browserobj,
		CSS_MOCK_SUMMARY_RISK_ASSESSMENT_NUMBERS,
		'zbUIMyReports/_checkRiskAssessment: count is not valid.',
	)

def _checkSecurityIncidentsNumbers(browserobj):
	rcode = True
	rcode = rcode and _isValidCount(
		browserobj,
		CSS_MOCK_SUMMARY_ALERTS_TOTAL_COUNT,
		'zbUIMyReports/_checkSecurityIncidentsNumbers: alerts count is not valid.'
	)
	rcode = rcode and _isValidCount(
		browserobj,
		CSS_MOCK_SUMMARY_SECURITY_INCIDENT_ALERT_NUMBER,
		'zbUIMyReports/_checkSecurityIncidentsNumbers: count is not valid.',
	)
	# Check sum
	total = int(browserobj.getText(selector=CSS_MOCK_SUMMARY_ALERTS_TOTAL_COUNT))
	alertCounts = browserobj.findMultiCSS(selector=CSS_MOCK_SUMMARY_SECURITY_INCIDENT_ALERT_NUMBER)
	for count in alertCounts:
		count = int(count.text)
		total = total - count
		if total == 0:
			break
	if total != 0:
		rcode = False
	return rcode

def _checkNetworkAndAppsNumbers(browserobj):
	rcode = True
	rcode = rcode and _isValidCount(
		browserobj,
		CSS_MOCK_SUMMARY_VLAN_COUNT,
		'zbUIMyReports/_checkNetworkAndAppsNumbers: vlan count is not valid.'
	)
	rcode = rcode and _isValidCount(
		browserobj,
		CSS_MOCK_SUMMARY_APPLICATIONS_COUNT,
		'zbUIMyReports/_checkNetworkAndAppsNumbers: application count is not valid.'
	)
	return rcode

def _checkDeviceDiscoveryNumbers(browserobj):
	rcode = True
	rcode = rcode and _isValidCount(
		browserobj,
		CSS_MOCK_SUMMARY_DEVICE_CATEGORY_COUNT,
		'zbUIMyReports/_checkDeviceDiscoveryNumbers: device category count is not valid.'
	)
	# Check percentage
	percentages = browserobj.findMultiCSS(selector=CSS_MOCK_SUMMARY_DEVICE_CATEGORY_PERCENTAGE)
	if not percentages:
		print('zbUIMyReports/_checkDeviceDiscoveryNumbers: device category percentages not found.')
		return False
	for percentage in percentages:
		percentage = percentage.text
		match = re.search(r'(\d+%)', percentage)
		if not match:
			print(('zbUIMyReports/_checkDeviceDiscoveryNumbers: device category percentage {} does not match format "10%"'.format(percentage)))
			return False
	return rcode

def _checkDeviceDiscoveryTop10s(browserobj):
	rcode = True
	# Check top 10 data usage
	counts = browserobj.findMultiCSS(selector=CSS_MOCK_SUMMARY_DEVICE_DATA_USAGE_COUNT)
	if not counts:
		print('zbUIMyReports/_checkDeviceDiscoveryTop10s: device data usage counts not found.')
		return False
	for count in counts:
		count = count.text
		match = re.search(r'(\d+\.\d+  \S+)', count)
		if not match:
			print(('zbUIMyReports/_checkDeviceDiscoveryNumbers: device data usage {} does not match format "15.63 GB"'.format(count)))
			return False
	# Check top 10 destination and applications
	counts = browserobj.findMultiCSS(selector=CSS_MOCK_SUMMARY_DEVICE_DESTINATION_AND_APPLICATIONS_COUNT)
	if not counts:
		print('zbUIMyReports/_checkDeviceDiscoveryTop10s: device destination and applications counts not found.')
		return False
	if len(counts) % 10 != 0:
		print('zbUIMyReports/_checkDeviceDiscoveryTop10s: device destination and applications numbers count is not a power of 10.')
		return False
	rcode = rcode and _isValidCount(
		browserobj,
		CSS_MOCK_SUMMARY_DEVICE_DESTINATION_AND_APPLICATIONS_COUNT,
		'zbUIMyReports/_checkDeviceDiscoveryNumbers: device destination and applications count is not valid.'
	)
	return rcode

def downloadReport(reportId, **kwargs):
	req = zbAPI()
	params = {
		'tenantid': kwargs['tenantid'],
		'id': reportId
	}
	response = req.reportDownload(host=kwargs['host'], stream=True, **params)
	filePath = kwargs['filePath'] + '/tests/report-{}-{}.pdf'.format(kwargs['tenantid'], kwargs['reportType'])

	deleteReport(filePath)
	with open(filePath, 'wb') as f:
		for chunk in response.iter_content(chunk_size=1024):
			if chunk:
				f.write(chunk)
	return filePath

def verifyReport(filePath, reportType):
	success=True
	missingwords=[]
	reader = ReadFile()
	content = reader.parseScannedPDF(filePath)
	deleteReport(filePath)
	keywords = keywordsForReportType[reportType]
	compactcontent = "".join(content.split())
	for word in keywords:
		if fuzzyRegexSearch(compactcontent,"(?i)"+"".join(word.split()),5) is None:
			missingwords.append(word)
			success=False

	if not success:
		print(('zbUIMyReports.py/verifyReport: keyword {} not in report {}'.format(str(missingwords), content)))
		return False
	return True

def deleteReport(filePath):
	if os.path.exists(filePath):
		os.remove(filePath)

class MyReports():

	def __init__(self, **kwargs):
		self.params = kwargs
		self.selenium = Login(**kwargs).login()

		rcode = self.selenium.getURL(kwargs["url"]+'/')
		if rcode: waitLoadProgressDone(self.selenium)


	def gotoMyReports(self):
		url = urlparse(self.params["url"])
		rcode = self.selenium.getURL(url.scheme+'://'+url.netloc+'/reports/reports')
		waitLoadProgressDone(self.selenium)

	def gotoMyReportsConnectivMockedPage(self):
		url = urlparse(self.params["url"])
		rcode = self.selenium.getURL(url.scheme+'://'+url.netloc+'/connectivity-report.html?reportPageView=true')
		waitLoadProgressDone(self.selenium)

	def gotoMyReportsSummaryMockedPage(self):
		url = urlparse(self.params["url"])
		rcode = self.selenium.getURL(url.scheme+'://'+url.netloc+'/summary-report.html?reportPageView=true')
		waitLoadProgressDone(self.selenium)

	def verifyMyReports(self):
		self.gotoMyReports()
		kwargs = {}
		temp = {}
		#opens up dropdown menu
		kwargs["selector"] = CSS_REPORT_CONFIG_LIST
		rcode = self.selenium.findSingleCSS(**kwargs)
		rcode.click()

		#loops through each selection in dropdown
		kwargs["selector"] = CSS_REPORT_CONFIG_LIST_SELECT
		dropdown= self.selenium.findMultiCSS(**kwargs)


		
		maxloop = len(dropdown) if len(dropdown) < 3 else 3
		for i in range(0,maxloop):
			isConnectivity = False
			time.sleep(1)
			if "test" != dropdown[i].text[0:4]: #Band-aid for the Discovery Report Issue
				continue

			dropdown[i].click()
	
			#Gets the four alert categories and sums them up 
			time.sleep(1)

			alerts = 0
			kwargs["waittype"] = "visibility"
			kwargs["waittime"] = 1
			kwargs["selector"] = CSS_ALERT_DEVICES
			rcode = self.selenium.findMultiCSS(**kwargs)
			
			temp["selector"] = CSS_CONNECT_VLAN
			temp["waittime"] = 1
			rcode2 = self.selenium.findMultiCSS(**temp)

			if(rcode == False and rcode2 == False):
				temp["selector"] = CSS_OPEN_REPORT_BUTTON
				temp["waittime"] = 5
				trial = self.selenium.findSingleCSS(**temp)
				row = trial.find_element_by_xpath("..")
				clicky = row.find_element_by_xpath("..")
				clicky.click()

			rcode = self.selenium.findMultiCSS(**kwargs)
			kwargs["waittime"] = 10


			if rcode != False:
				for i in range(0,4):
					alerts = int(rcode[i].text) + alerts
				if alerts == 0: #total alert at 0 does not show
					pass 
				elif alerts != 0:
					#if alerts do not sum to 0 then the it tries to check if it matches total
					try:
						kwargs["selector"] = CSS_TOTAL_ALERTS
						rcode = self.selenium.findMultiCSS(**kwargs)
						totalAlerts = int(rcode[0].text)
						if alerts != totalAlerts:
							print("Sum of alerts are off")
							print("Sum: " + str(alerts) + " || Total: " + str(totalAlerts)) 
							return False
					except ValueError:
						print("Unable to find total alerts")
						return False
			else:
				isConnectivity = True
				kwargs["selector"] = CSS_CONNECT_VLAN
				rcode = self.selenium.findMultiCSS(**kwargs)
				vlans = 0
				total = int(rcode[0].text)
				for r in rcode[1:5]:
					vlans += int(r.text)
				if vlans != total:
					print("connectivity report Vlans not adding up")
					return False

			if isConnectivity:
				#CSS_TOTAL_DEVICES = "zing-connectivity-report-summary-main > div.connectivity-report-summary-main-header.layout-align-space-between-stretch.layout-row > div:nth-child(3) > div > div"
				#CSS_IOT_DEVICES = "zing-connectivity-report-summary-main > div.connectivity-report-summary-main-content > div:nth-child(1) > div:nth-child(3) > div > div"
				#CSS_NONIOT_DEVICES = "zing-connectivity-report-summary-main > div.connectivity-report-summary-main-content > div:nth-child(3) > div:nth-child(3) > div > div"

				kwargs["selector"] = CSS_REPORT_CONFIG_LIST
				rcode = self.selenium.findSingleCSS(**kwargs)
				rcode.click()
				continue
			else:
				CSS_TOTAL_DEVICES ="div.sub-title.layout-align-space-between-center.layout-row > div:nth-child(3) > div.zing-text-align-right.ng-binding" #element 1,3,5...
				CSS_IOT_DEVICES = "div[ng-bind='item.iotdevices']"
				CSS_NONIOT_DEVICES = "div[ng-bind='item.noniotdevices']"


			#Gets the total devices
			kwargs["selector"] = CSS_TOTAL_DEVICES
			rcode = self.selenium.findMultiCSS(**kwargs)
			totalDevices = int(rcode[0].text)

			#gets the ioT devices
			kwargs["selector"] = CSS_IOT_DEVICES
			rcode = self.selenium.findMultiCSS(**kwargs)
			iotdevices = int(rcode[0].text)
			if iotdevices < 0:
				print("IOT devices has an unexpected number")
				return False
			
			#gets the non iot devices
			kwargs["selector"] = CSS_NONIOT_DEVICES
			rcode = self.selenium.findMultiCSS(**kwargs)
			noniotdevices = int(rcode[0].text)
			if noniotdevices < 0:
				print("Non-IOT devices has an unexpected number")
				return False




			
			total = (iotdevices + noniotdevices) 

			#checks to see if the total error margin is too small by value
			errorMargin = abs(total - totalDevices) 

			#checks to see if the total is 90% accurate to the actual total	
			adjustedTotalHigh = totalDevices + (total * .1)
			adjustedTotalLow = totalDevices - (total * .1) 

			if total > adjustedTotalHigh and errorMargin > 3:
				print("Total number of devices is too high")
				return False
			if total < adjustedTotalLow and errorMargin > 3:
				print("Total number of devices is too low")
				return False

			#checks the new IOT devices	
			kwargs["selector"] = CSS_NEWIOT_DEVICES
			rcode = self.selenium.findMultiCSS(**kwargs)
			newiotdevices = int(rcode[0].text)
			if newiotdevices < 0:
				print("New IOT devices has an unexpected number")
				return False
			
			#checks the new non-IOT devices
			kwargs["selector"] = CSS_NEWNONIOT_DEVICES
			rcode = self.selenium.findMultiCSS(**kwargs)
			newnoniotdevices = int(rcode[0].text)
			if newnoniotdevices < 0:
				print("New non-IOT devices has an unexpected number")
				return False	
			
			#checks the destinations
			kwargs["selector"] = CSS_DESTINATION_AND_APPS
			rcode = self.selenium.findMultiCSS(**kwargs)
			destinations = rcode[0].text
			destinations = destinations.replace(',', '')
			destinations = int(destinations)
			if destinations < 0:
				print("Number of destinations has an unexpected number")
				return False	

			#checks the applications	
			#kwargs["selector"] = CSS_DESTINATION_AND_APPS
			#rcode = self.selenium.findMultiCSS(**kwargs)
			#applications = int(rcode[1].text)
			#if applications < 0:
				#print "Number of applications has an unexpected number"
				#return False	

			#checks the data usage
			kwargs["selector"] = CSS_DATA_USAGE
			rcode = self.selenium.findMultiCSS(**kwargs)
			dataUsage = float(rcode[0].text)
			if dataUsage < 0:
				print("Data usage has an unexpected number")
				return False	

			#clicks open the dropdown list again33+
			kwargs["selector"] = CSS_REPORT_CONFIG_LIST
			rcode = self.selenium.findSingleCSS(**kwargs)
			rcode.click()


		return True


	def verifyMyReportsPDF(self):
		self.gotoMyReports()	
		kwargs = {}
		
		#opens up dropdown menu
		kwargs["selector"] = CSS_REPORT_CONFIG_LIST
		rcode = self.selenium.findSingleCSS(**kwargs)
		rcode.click()

		#loops through each selection in dropdown
		kwargs["selector"] = CSS_REPORT_CONFIG_LIST_SELECT
		dropdown= self.selenium.findMultiCSS(**kwargs)
		maxloop = len(dropdown) if len(dropdown) < 3 else 3

		
		for i in range(0,maxloop):
			if "test" != dropdown[i].text[0:4]: #Band-aid for the Discovery Report Issue
				continue
			time.sleep(1)
			dropdown[i].click()
			time.sleep(1)
			kwargs["selector"] = CSS_VIEW_PDF
			rcode = self.selenium.findMultiCSS(**kwargs)
			try:
				rcode[0].click()
			except StaleElementReferenceException:
				# stale element in UI meaning object has been deleted.
				# can break out of loop now
				break
			except WebDriverException:
				print("View PDF is not clickable")
				return False

			self.selenium.goBack()
			time.sleep(1)
			kwargs["selector"] = CSS_REPORT_CONFIG_LIST
			rcode = self.selenium.findSingleCSS(**kwargs)
			rcode.click()
			kwargs["selector"] = CSS_REPORT_CONFIG_LIST_SELECT
			dropdown= self.selenium.findMultiCSS(**kwargs)
		
		return True

	def verifyMyReportsConnectivMockedPage(self):
		self.gotoMyReportsConnectivMockedPage()
		rcode = True
		rcode = rcode and checkHeadingInfo(self.selenium)
		rcode = rcode and checkNetworkStatus(self.selenium)
		rcode = rcode and checkNetworkStatusDeviceCounts(self.selenium)
		rcode = rcode and checkVLANSummary(self.selenium)
		return rcode

	def verifyMyReportsSummaryMockedPage(self):
		self.gotoMyReportsSummaryMockedPage()
		rcode = True
		rcode = rcode and checkHeadingInfo(self.selenium)
		rcode = rcode and checkBarChart(self.selenium)
		rcode = rcode and checkSummaryNumbers(self.selenium)
		rcode = rcode and checkSecurityIncidents(self.selenium)
		return rcode

	def verifyMyReportsLatestPDF(self, **kwargs):
		reportType = kwargs['reportType']
		self.gotoMyReports()
		self.selenium.click(selector=CSS_FREQUENCIES_DROPDOWN)
		self.selenium.click(selector=CSS_FREQUENCIES_WEEKLY_OPTION)
		row = self.selenium.findSingleCSS(selector=rowsSelectorForReportType[reportType])
		if not row:
			print(('zbUIMyReports.py/verifyMyReportsLatestPDF: No rows found for {} report type'.format(reportType)))
			return False
		self.selenium.click(browserobj=row, selector=CSS_VIEW_PDF)
		currentUrl = self.selenium.driver.current_url
		reportId = currentUrl[currentUrl.find('reportspdf')+11:currentUrl.find('?')]
		fileName = downloadReport(reportId, **kwargs)
		time.sleep(10)
		return verifyReport(fileName, reportType)

	def close(self):
		if self.selenium:
			self.selenium.quit()
