from datetime import datetime
from ui.login.zbUILoginCore import Login
from ui.zbUIShared import *
import time, pdb, re
from selenium.webdriver.common.action_chains import ActionChains
from urllib.parse import urlparse

CSS_INFUSION_CARD = "md-card.category-item[ng-repeat='fullCategory in healthCatCtrl.categories | limitTo : healthCatCtrl.pageSize : healthCatCtrl.curStart']"
CSS_CATEGORY_CARD = "md-card .flex.ng-binding"

CSS_DATA_MENU_BUTTON = "button[aria-label='Select date range']"
CSS_DATE_SELECTION_BUTTONS = "div.menu-selection-button"
CSS_GRAPH_BOTTOM_TEXT = "text[text-anchor='middle'][transform='translate(0,0)']"
CSS_DATA_SELECTION_TEXT = "span.ng-binding[style='']"
CSS_TIME_MENU ="md-menu.date-selection"
CSS_TIME_MENU_BUTTONS = "div.menu-selection-button"

CSS_PROFILE_CARD = "md-card.profile-card"
CSS_INFUSION_TOTAL = "[ng-bind='healthcareDeviceConnectionChartCtrl.statData.total']"
CSS_INFUSION_ACTIVENOW = "[ng-bind='healthcareDeviceConnectionChartCtrl.statData.active']"
CSS_INFUSION_USED = "[ng-bind='healthcareDeviceConnectionChartCtrl.statData.used']"
CSS_INFUSION_CONNECTED = "[ng-bind='healthcareDeviceConnectionChartCtrl.statData.connected']"

CSS_INFUSION_LINES = ".highcharts-tracker[stroke-width='22']"

CSS_INFUSION_DEVICE_CONNECTED_MARKERS = ".highcharts-series path[stroke='#42a9d2']"
CSS_INFUSION_DEVICE_USED_MARKERS = ".highcharts-series path[stroke='#7ED321']"

CSS_INFUSION_GRAPH_TOGGLE = ".highcharts-legend-item"





def verifyTimeGraph(browser):
	time_index = 0
	params = {}
	r_valid_time = True
	r_valid_graph = True
	params['selector'] = CSS_CATEGORY_CARD
	card_list = browser.findMultiCSS(**params)
	for card in card_list:
		if card.text == 'Infusion System':
			card.click()
			break

	old_node_1 = ''
	old_node_2 = ''
	while time_index < 5:
		try:
			time_list = []
			params['selector'] = CSS_TIME_MENU
			button = browser.findSingleCSS(**params)
			button.click()
			time.sleep(2)
			params['selector'] = CSS_TIME_MENU_BUTTONS
			buttons = browser.findMultiCSS(**params)
			buttons[time_index].click()
			time.sleep(2)
			params['selector'] = CSS_GRAPH_BOTTOM_TEXT
			bottom_texts = browser.findMultiCSS(**params)
			for texty in bottom_texts:  # This section parses the date labels on the time graph x-axis
				if time_index == 0:
					time_list.append((datetime.strptime(texty.text,"%H:%M"), float(texty.get_attribute('x'))))
				elif time_index == 1:
					try:
						time_list.append((datetime.strptime(texty.text,"%H:%M"), float(texty.get_attribute('x'))))
					except:
						temp = texty.find_element_by_css_selector("title")
						stringy = temp.get_attribute('innerHTML')
						time_list.append((datetime.strptime(stringy,"%H:%M"), float(texty.get_attribute('x'))))
				elif time_index == 2:
					time_list.append((datetime.strptime(texty.text,"%I%p, %m/%d"),float(texty.get_attribute('x'))))
				else:
					time_list.append((datetime.strptime(texty.text,"%m/%d"),float(texty.get_attribute('x'))))
			time_list = sorted(time_list, key=lambda x:x[1]) #Compares the first and last date label and gets their difference in time
			if time_list[-1][0] > time_list[0][0]:
				timedelta = time_list[-1][0] - time_list[0][0]
			else:
				timedelta = time_list[0][0] - time_list[-1][0]

			if time_index == 0:
				if 6400 <= timedelta.seconds <= 7200: #Difference between labels should between 6400 and 7200 in seconds (around two hours)
					pass
				else:
					print("2 hour mismatch")
					r_valid_time = False
			elif time_index == 1:
				print(time_list[-1][0])
				print(time_list[0][0])
				if timedelta.seconds <= 3600: #Difference between labels should be less than one hour because they have no date label
					pass
				else:
					print(timedelta.seconds)
					print("1 day mismatch")
					r_valid_time = False
			elif time_index == 2:
				if 5 <= timedelta.days < 7 or 5 <= abs(timedelta.days-365) <= 7: #difference should be between 5 and 7 days
					pass
				else:
					print("1 week mismatch")
					print(timedelta.days)
					r_valid_time = False
			elif time_index == 3:
				if 25 <= timedelta.days < 31 or 25 <= abs(timedelta.days-365) <= 31: #difference should be between 25 and 31 days
					pass
				else:
					print("1 month mismatch")
					print(timedelta.days)
					r_valid_time = False
			elif time_index == 4:
				if abs(timedelta.days) <= 2 or abs(timedelta.days-365) <= 2:  #difference should be between 0 and 2 days because they have no year label
					pass
				else:
					print("1 year mismatch")
					print(timedelta.days)
					r_valid_time = False

			time_index = time_index+1
		except Exception as e:
			print(e)
			return False

	return r_valid_time and r_valid_graph



def verifySeriesGraph(browser):
	rcode = True
	params = {}

	params['selector'] = CSS_CATEGORY_CARD
	card_list = browser.findMultiCSS(**params)
	for card in card_list:
		if card.text == 'Infusion System':
			card.click()
			break
	
	params['selector'] = CSS_TIME_MENU
	button = browser.findSingleCSS(**params)
	button.click()
	waitLoadProgressDone(browser)
	
	params['selector'] = CSS_TIME_MENU_BUTTONS
	buttons = browser.findMultiCSS(**params)
	buttons[4].click()
	waitLoadProgressDone(browser)
	
	params['selector'] = CSS_INFUSION_TOTAL
	element = browser.findSingleCSS(**params)
	try:
		int(element.text)
	except:
		print("Total Count is invalid")
		rcode = False

	params['selector'] = CSS_INFUSION_ACTIVENOW
	element = browser.findSingleCSS(**params)
	try:
		int(element.text)
	except:
		print("Active Now is invalid")
		rcode = False

	params['selector'] = CSS_INFUSION_USED
	element = browser.findSingleCSS(**params)
	try:
		int(element.text)
	except:
		print("Used Count is invalid")
		rcode = False

	params['selector'] = CSS_INFUSION_CONNECTED
	element = browser.findSingleCSS(**params)
	try:
		int(element.text)
	except:
		print("Connected Count is invalid")
		rcode = False

	params['selector'] = CSS_INFUSION_DEVICE_CONNECTED_MARKERS 
	element = browser.findSingleCSS(**params)
	if element == False:
		print("Connected Graph doesn't exist and thus is invalid")
		rcode = False

	params['selector'] = CSS_INFUSION_DEVICE_USED_MARKERS
	element = browser.findSingleCSS(**params)
	if element == False:
		print("Used Graph doesn't exist and thus is invalid")
		rcode = False

	params['selector'] = CSS_INFUSION_GRAPH_TOGGLE
	buttons = browser.findMultiCSS(**params)
	for button in buttons:
		button.click()

	params['selector'] = CSS_INFUSION_LINES
	lines = browser.findMultiCSS(**params)
	for line in lines:
		if line.get_attribute('visibility') != 'hidden':
			rcode = False
			print("Lines not turning invisible")

	params['selector'] = CSS_INFUSION_GRAPH_TOGGLE
	buttons = browser.findMultiCSS(**params)
	for button in buttons:
		button.click()

	params['selector'] = CSS_INFUSION_LINES
	lines = browser.findMultiCSS(**params)
	for line in lines:
		if line.get_attribute('visibility') != 'visible':
			rcode = False
			print("Lines not becoming visible again")
	return rcode





CSS_PEAK_UTILIZATION_TITLE = ".healthcare-device-utilization .title"
CSS_PEAK_UTILIZATION_TOOLTIP = ".healthcare-device-utilization [zing-tooltip='']"
CSS_PEAK_UTILIZATION_BUBBLE = "svg.healthcare-device-utilization-bubble"
CSS_PEAK_UTILIZATION_BUBBLE_TEXT = "text.liquidFillGaugeText"
CSS_PEAK_UTILIZATION_TOP_TEXT = ".healthcare-device-utilization .top-text"
CSS_PEAK_UTILIZATION_BOTTOM_TEXT = ".healthcare-device-utilization .down-text"



def verifyPeakUtilization(browser):
	waitLoadProgressDone(browser)
	time.sleep(3)

	rcode = True
	params = {}

	params['selector'] = CSS_PEAK_UTILIZATION_TITLE
	element = browser.findSingleCSS(**params)
	if element == False:
		print("### The Peak Utilization title could not be found ###")
		rcode = False

	params['selector'] = CSS_PEAK_UTILIZATION_TOOLTIP
	element = browser.findSingleCSS(**params)
	tooltip = browser.hoverElement(element)
	if tooltip == False:
		print("### The Tooltip could not be hovered on ###")
		rcode = False

	params['selector'] = CSS_PEAK_UTILIZATION_BUBBLE
	element = browser.findSingleCSS(**params)
	if element == False:
		print("### The bubble diagram could not be found ###")
		rcode = False

	params['selector'] = CSS_PEAK_UTILIZATION_BUBBLE_TEXT
	element = browser.findSingleCSS(**params)
	if element == False:
		print("### The bubble text could not be found ###")
		rcode = False
	bubbletext = re.search(r'\d+%', element.text)
	if bubbletext == False:
		print(("### The bubble text is currently {}".format(bubbletext.group(0))))
		print("### The text should be a number with the percentage symbol, regex: '\d+%' ###")
		return False

	params['selector'] = CSS_PEAK_UTILIZATION_TOP_TEXT
	element = browser.findMultiCSS(**params)
	if element[0].text != "Concurrent Device(s) Used":
		print("### 'Concurrent Device(s) Used' text not found ###")
		return False
	if element[1].text != "Peak Time":
		print("### 'Peak Time' text not found ###")
		return False

	params['selector'] = CSS_PEAK_UTILIZATION_BOTTOM_TEXT
	element = browser.findMultiCSS(**params)
	bottomtext1 = re.search(r'\d+', element[0].text)
	if bottomtext1 == False:
		print(("### The bottom text is currently {}".format(bottomtext1.group(0))))
		print("### The text under 'Concurrent Device(s) Used' does not match, regex: '\d+' ###")
		return False
	bottomtext2 = re.search(r'\d{1,2}:\d{2}\s\w+\s\d+,\s\d+', element[1].text)
	if bottomtext2 == False:
		print(("### The bottom text is currently {}".format(bottomtext2.group(0))))
		print("### The text under 'Peak Time' does not match, regex: '\d{1,2}:\d{2}\s\w+\s\d+,\s\d+' ###")
		return False

	return rcode



CSS_DEVICE_USAGE_DISTRIBUTION_TITLE = ".healthcare-distribution-chart .title"
CSS_DEVICE_USAGE_DISTRIBUTION_X_AXIS = ".healthcare-distribution-chart .x.axis-label"
CSS_DEVICE_USAGE_DISTRIBUTION_X_VALUE = ".healthcare-distribution-chart .x .tick"
CSS_DEVICE_USAGE_DISTRIBUTION_Y_AXIS = ".healthcare-distribution-chart .y.axis-label"
CSS_DEVICE_USAGE_DISTRIBUTION_Y_VALUE = ".healthcare-distribution-chart .y .tick"
CSS_CONNECTION_CHART_DEVICES_USED = ".healthcare-device-connection-chart .big-number .big-number[ng-bind='healthcareDeviceConnectionChartCtrl.statData.used']"
CSS_DEVICE_USAGE_DISTRIBUTION_VIEWS = ".healthcare-distribution-chart .switch-unit"
CSS_DEVICE_USAGE_DISTRIBUTION_POINTS = ".healthcare-distribution-chart circle.dot"
CSS_DEVICE_USAGE_DISTRIBUTION_POINTS_HOVERED = "circle.hovered-dot"
CSS_DEVICE_USAGE_DISTRIBUTION_POINTS_SELECTED = ".healthcare-distribution-chart circle.selected-dot.dot"
CSS_DEVICE_USAGE_DISTRIBUTION_TOOLTIP = "#otNodeTooltip"
CSS_DEVICE_USAGE_DISTRIBUTION_TOOLTIP_LINK = ".healthcare-distribution-chart .zing-shadow-box .zing-link"
CSS_DEVICE_USAGE_DISTRIBUTION_DEVICE_INV_NUM = ".zingTable .table-title"
CSS_DEVICE_USAGE_DISTRIBUTION_DEVICE_INV_LABEL = ".filter-inner .single-chip .content"



def verifyDeviceUsage(browser):
	""" Check the Title and the X-axis values """
	waitLoadProgressDone(browser)
	time.sleep(3)

	params = {"selector": CSS_DEVICE_USAGE_DISTRIBUTION_TITLE, "timeout":10}
	element = browser.findSingleCSS(**params)
	if element == False:
		print("### The Device Usage Distribution title could not be found ###")
		return False

	params = {"selector": CSS_DEVICE_USAGE_DISTRIBUTION_X_AXIS, "timeout":5}
	element = browser.findSingleCSS(**params)
	if element.text != "Operation hours":
		print("### 'Operation hours' text not found ###")
		return False

	params = {"selector": CSS_DEVICE_USAGE_DISTRIBUTION_X_VALUE, "timeout":5}
	element = browser.findMultiCSS(**params)
	if element[0].text != "0":
		print("### 'Operation hours' text not found ###")
		return False

	xnum = re.search(r'\d+', element[1].text)
	if xnum == False:
		print(("### The x-axis number is currently {}".format(xnum.group(0))))
		print("### The x-axis number text does not match, regex: '\d+' ###")
		return False

def verifyDeviceUsagePercentView(browser):
	""" Click on the Percentage View and check the Y-axis values which should change """
	waitLoadProgressDone(browser)

	for i in range(5):
		try:
			params = {"selector": CSS_DEVICE_USAGE_DISTRIBUTION_VIEWS, "timeout":10}
			element = browser.findMultiCSS(**params)
			click_percent = element[1].click()
			if click_percent != False:
				print("### SUCCESS!!! Able to click on the percentage view ###")
				break
		except:
			print("### Not able to click on the percentage view ###")

	params = {"selector": CSS_DEVICE_USAGE_DISTRIBUTION_Y_AXIS, "timeout":5}
	element = browser.findSingleCSS(**params)
	if element.text != "Percentage of devices":
		print("### 'Percentage of devices' text not found ###")
		return False

	params = {"selector": CSS_DEVICE_USAGE_DISTRIBUTION_Y_VALUE, "timeout":5}
	element = browser.findSingleCSS(**params)
	ynum = re.search(r'\d+(.\d+)?%', element.text)
	if ynum == False:
		print(("### The y-axis number is currently {}".format(ynum.group(0))))
		print("### The y-axis number text does not match, regex: '\d+' ###")
		return False

def verifyDeviceUsageNumView(browser):
	""" Click on the Numerical View and check the Y-axis values which should change """
	waitLoadProgressDone(browser)

	for i in range(5):
		try:
			params = {"selector": CSS_DEVICE_USAGE_DISTRIBUTION_VIEWS, "timeout":10}
			element = browser.findMultiCSS(**params)
			click_num = element[0].click()
			if click_num != False:
				print("### SUCCESS!!! Able to click on the numerical view ###")
				break
		except:
			print("### Not able to click on the numercial view ###")

	params = {"selector": CSS_DEVICE_USAGE_DISTRIBUTION_Y_AXIS, "timeout":5}
	element = browser.findSingleCSS(**params)
	if element.text != "Number of devices":
		print("### 'Number of devices' text not found ###")
		return False

	params = {"selector": CSS_DEVICE_USAGE_DISTRIBUTION_Y_VALUE, "timeout":5}
	element = browser.findSingleCSS(**params)
	ynum = re.search(r'\d+', element.text)
	if ynum == False:
		print(("### The y-axis number is currently {}".format(ynum.group(0))))
		print("### The y-axis number text does not match, regex: '\d+' ###")
		return False

	return True

def verifyDeviceUsagePointsSelection(browser):
	""" Check that the points on the graph are functioning correctly, able to go to the IV Pump Device Page, and values are consistent """
	waitLoadProgressDone(browser)
	time.sleep(5)

	params = {"selector":CSS_DEVICE_USAGE_DISTRIBUTION_POINTS, "timeout":10}
	point = browser.findMultiCSS(**params)
	if point == False:
		print("### The Device Usage points could not be found ###")
		return False

	for i in range(25): # Selenium has a difficult time clicking on first point, Repeat to click up to 25 times, if needed
		try:
			time.sleep(0.3)
			browser.hoverElement(point[0])
			params = {"selector":CSS_DEVICE_USAGE_DISTRIBUTION_POINTS_HOVERED, "timeout":3}
			pointhovered = browser.findSingleCSSNoHover(**params)
			action = ActionChains(browser.driver)
			action.move_to_element_with_offset(point[0],5,5)
			action.pause(1)
			action.click()
			action.perform()
			

			params = {"selector":CSS_DEVICE_USAGE_DISTRIBUTION_POINTS_SELECTED, "timeout":3}
			pointselected = browser.findMultiCSS(**params)
			if pointselected[0] != False:
				print("### SUCCESS!!! Able to click on the first point ###")
				break
		except Exception as E:
			print(E)
			print("### Not able to click on the first point ###")
	
	if point[0] != point[-1]:
		for i in range(25):  # Selenium has a less difficult time clicking on last point,  still repeat to click up to 25 times, if needed
			try:
				time.sleep(0.5)
				browser.hoverElement(point[-1])
				params = {"selector":CSS_DEVICE_USAGE_DISTRIBUTION_POINTS_HOVERED, "timeout":3}
				pointhovered = browser.findSingleCSSNoHover(**params)
				action = ActionChains(browser.driver)
				action.move_to_element_with_offset(point[-1],5,5)
				action.pause(1)
				action.click()
				action.perform()
				params = {"selector":CSS_DEVICE_USAGE_DISTRIBUTION_POINTS_SELECTED, "timeout":3}
				pointselected = browser.findMultiCSS(**params)
				if pointselected[-1] != False:
					print("### SUCCESS!!! Able to click on the last point ###")
					break
			except:
				print("### Not able to click on the last point ###")
	
	time.sleep(3)
	params = {"selector":CSS_DEVICE_USAGE_DISTRIBUTION_TOOLTIP, "timeout":3}
	element = browser.findSingleCSS(**params)
	if element == False:
		print("### The Device Usage tooltip could not be found ###")
		return False
	tooltip_time_range = re.search(r'between \d+(.\d+)? - \d+(.\d+)? hours', element.text)
	if tooltip_time_range == False:
		print(("### The tooltip time range is currently {}".format(tooltip_time_range.group(0))))
		print("### The tooltip time range text does not match, regex: '\d+' ###")
		return False

	params = {"selector":CSS_DEVICE_USAGE_DISTRIBUTION_TOOLTIP_LINK, "timeout":3}
	element = browser.findSingleCSS(**params)
	if element == False:
		print("### The Device Usage Device tooltip link could not be found ###")
		return False
	tooltip_link = element
	tooltip_num = int(element.text)

	params = {"selector":CSS_CONNECTION_CHART_DEVICES_USED, "timeout":3}
	element = browser.findSingleCSS(**params)
	if element == False:
		print("### The number of devices used in the Connection Chart could not be found ###")
		return False
	dev_used = int(element.text)

	if tooltip_num > 5:
		print(tooltip_num)
		print(dev_used)
		if tooltip_num - 5 >= dev_used or tooltip_num + 5 <= dev_used:
			print("### The Device Used value is outside the range of the Tooltip Number by more than 5")
			return False

	tooltip_link.click()
	waitLoadProgressDone(browser)
	time.sleep(5)

	params = {"selector":CSS_DEVICE_USAGE_DISTRIBUTION_DEVICE_INV_NUM, "timeout":15}
	element = browser.findSingleCSS(**params)
	if element == False:
		print("### The Device Usage Device Inventory number could not be found ###")
		return False
	dev_inv_num = re.search(r'\d+', element.text)

	if int(dev_inv_num.group()) != tooltip_num:
		print("### The Device Inventory Number is not equal to the Tooltip Number ###")
		return False

	params = {"selector":CSS_DEVICE_USAGE_DISTRIBUTION_DEVICE_INV_LABEL, "timeout":10}
	element = browser.findSingleCSS(**params)
	if element == False:
		print("### The Device Usage Device Inventory label could not be found ###")
		return False
	label_time_range = re.search(r'between \d+(.\d+)? - \d+(.\d+)? hours', element.text)

	if label_time_range == False:
		print(("### The tooltip time range is currently {}".format(label_time_range.group(0))))
		print("### The tooltip time range text does not match, regex: '\d+' ###")
		return False

	if tooltip_time_range.group() != label_time_range.group():
		print("tooltip time: " + tooltip_time_range)
		print("labeltime: " + label_time_range)
		print("### The time range in the previous page's tooltip does not match the time range in the label ###")
		return False

	return True

class Infusion():
	def __init__(self, **kwargs):
		self.params = kwargs
		self.selenium = Login(**kwargs).login()
	def gotoInfusion(self):
		params = {}
		url = urlparse(self.params["url"])
		rcode = self.selenium.getURL(url.scheme+'://'+url.netloc+'/?dashboard_type=operations')
		if rcode:
			waitLoadProgressDone(self.selenium)
		else:
			return False
		params['selector'] = CSS_CATEGORY_CARD
		card_list = self.selenium.findMultiCSS(**params)
		for card in card_list:
			if card.text == 'Infusion System':
				card.click()
				break

	def checkTimeSeries(self):
		self.gotoInfusion()
		return verifyTimeGraph(self.selenium)

	def checkSeriesGraph(self):
		self.gotoInfusion()
		return verifySeriesGraph(self.selenium)

	def checkPeakUtilization(self):
		self.gotoInfusion()
		return verifyPeakUtilization(self.selenium)

	def checkDeviceUsageView(self):
		self.gotoInfusion()
		verifyDeviceUsage(self.selenium)
		verifyDeviceUsagePercentView(self.selenium)
		verifyDeviceUsage(self.selenium)
		return verifyDeviceUsageNumView(self.selenium)

	def checkDeviceUsagePoints(self):
		self.gotoInfusion()
		return verifyDeviceUsagePointsSelection(self.selenium)


	def close(self):
		if self.selenium:
			self.selenium.quit()









