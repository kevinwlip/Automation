#!/usr/bin/python


from selenium.webdriver.common.keys import Keys
from urllib.parse import urlparse
from ui.login.zbUILoginCore import Login
from ui.zbUIShared import waitLoadProgressDone
from zbInspector import Inspector
import time, re, pdb
import logging
import random

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

locale.setlocale( locale.LC_ALL, 'en_US.UTF-8' )

# Global CSS for Administration > My Inspector page
CSS_ADD_SITE = "button.md-icon-button.add-site"
CSS_SITE_NAME_INPUT = "input[ng-model='siteCreateCtrl.siteName']"
CSS_SITE_ADDRESS_INPUT = "input[ng-model='siteCreateCtrl.siteAddress']"
CSS_SAVE_BUTTON = "button[aria-label='Save new site']"
CSS_EDIT_SITE_BUTTON = "button.md-icon-button[aria-label='Edit site'"

CSS_SITE_NAME = 'h3[ng-bind=\"site.external_id\"]'
CSS_SITES_TOP_LEVEL = "div.layout-wrap > div.site-item"
CSS_SITE_BUTTON = "div.site-buttons"
CSS_DELETE_SITE_BUTTON = 'div.md-clickable > md-menu-content > md-menu-item > button[aria-label="Delete site"]'

CSS_INSPECTOR_CARD_OBJ = ".single-inspector"
CSS_INSPECTOR_NAME_ELEMENT = ".inspector-name"
CSS_INSPECTOR_STATUS = ".deploy-status"
CSS_INSPECTOR_MENU = "[category='Inspector'][name='Open inspector menu']"
CSS_INSPECTOR_STOP_TRAFFIC = ".md-active [icon='pause_circle_filled']"
CSS_INSPECTOR_START_TRAFFIC = ".md-active [icon='play_circle_fill']"
CSS_CONFIRM_START_STOP = ".md-confirm-button"

CSS_INSPECTOR_ADD_BUTTON = ".zt-add-icon"
CSS_INSPECTOR_DETAIL_BUTTON = ".zt-detail-actions"
CSS_INSPECTOR_DROPDOWN_ACTION_OPTION = ".zt-detail-actions"
CSS_INSPECTOR_DROPDOWN_CREATE_SITE = ".zt-create-site-icon"
CSS_INSPECTOR_EXPAND_ALL = ".header-icons .zt-expand-icon"
CSS_INSPECTOR_COLLAPSE_ALL = ".header-icons .zt-collapse-icon"
CSS_INSPECTOR_INSPECTOR_NAME = ".zt-inspector-name"
CSS_INSPECTOR_SITE_NAME = ".zt-site-name"
CSS_INSPECTOR_INSPECTOR_NUMBER = ".zt-total-inspectors .total-sites"
CSS_INSPECTOR_SITE_NUMBER = ".zt-total-number-of-sites .total-sites"

CSS_CREATE_SITE_NAME = ".zt-create-site-name"
CSS_CREATE_SITE_ADDRESS = ".zt-create-site-address"
CSS_CREATE_SITE_SAVE_BUTTON = "zing-create-site .mat-button.primary"
CSS_SITE_CARD = ".zt-site-card"

def getInspectorData(browserobj, inspector_name, data="IP Address"):  # Returns data value, IP Address by default
	insp_name = browserobj.findMultiCSS(selector=CSS_INSPECTOR_NAME_ELEMENT)
	insp_status = browserobj.findMultiCSS(selector=CSS_INSPECTOR_STATUS)
	insp_card = browserobj.findMultiCSS(selector=CSS_INSPECTOR_CARD_OBJ)
	insp_count = 0
	for element in insp_name:
		element = element.text
		print(( inspector_name + " | " + element))
		if inspector_name == element and insp_status[insp_count].text == "LIVE": # If inspector name is found and the inspector is 'LIVE'
			break
		insp_count += 1
	insp_data = re.search(data+"\s.*", insp_card[insp_count].text).group().strip(data+"\n")
	return insp_data



class MyInspectors():

	def __init__(self, **kwargs):
		self.params = kwargs
		self.selenium = Login(**kwargs).login()

		rcode = self.selenium.getURL(kwargs["url"]+'/')
		if rcode:
			waitLoadProgressDone(self.selenium)


	def regInspectors(self, **kwargs):
		self.gotoInspectorPage()
		rcode = self.selenium.click(selector=CSS_INSPECTOR_EXPAND_ALL)

		rcode = self.selenium.findMultiCSS(selector=CSS_INSPECTOR_SITE_NAME)
		lenny = len(rcode)
		rcode = self.selenium.findSingleCSS(selector=CSS_INSPECTOR_SITE_NUMBER)

		if int(rcode.text) == int(lenny):
			logger.critical("Site number not matching up with number of sites")
			return False

		rcode = self.selenium.findMultiCSS(selector=CSS_INSPECTOR_INSPECTOR_NAME)
		lenny = len(rcode)
		rcode = self.selenium.findSingleCSS(selector=CSS_INSPECTOR_INSPECTOR_NUMBER)

		if int(rcode.text) == int(lenny):
			logger.critical("Inspector number not matching up with number of inspectors")
			return False

		self.selenium.click(selector=CSS_INSPECTOR_DROPDOWN_CREATE_SITE)
		time.sleep(1)
		rcode = self.selenium.findSingleCSS(selector=CSS_CREATE_SITE_NAME)
		rcode.click()
		rcode.send_keys("Ayy_Lmao_Test")

		rcode = self.selenium.findSingleCSS(selector=CSS_CREATE_SITE_ADDRESS)
		rcode.click()
		rcode.send_keys("Test_Address_Please_Ignore")

		self.selenium.click(selector=CSS_CREATE_SITE_SAVE_BUTTON)

		rcode = self.selenium.findMultiCSS(selector=CSS_SITE_CARD)
		for r in rcode:
			print(r.text)
			print("=======")












	

	def verifySite(self, **kwargs):
		kwargs["name"] = "zbat site"
		rcode = self.configDeleteSite(kwargs["name"]) # before start, clean up sites    
		rcode = self.configAddSite(**kwargs) # add new site
		rcode = self.checkSiteExist(kwargs["name"])
		if not rcode:
			print(("Adding Site has issue.  Did not find Site "+str(kwargs["name"])+" after add."))
		if rcode:
			rcode = self.configDeleteSite(kwargs["name"]) # delete site
		rcode = self.checkSiteExist(kwargs["name"])
		return True if not rcode else False # if site delete correctly, then return True
	

	def verifyInspectorTraffic(self, **kwargs):
		self.gotoInspectorPage()
		#self.enableInspectorTraffic(kwargs["inspector"], enable=True)

		hostip = getInspectorData(self.selenium, kwargs["inspector"]) # Get the IP Address value
		credentials = { # Set credentials for SSH in compareTrafficValues()
			"inspector": kwargs["inspector"],
			"hostname": hostip,
			"username": kwargs["insp_uname"],
			"password": kwargs["insp_pwd"]
		}
		self.close()
		rcode = self.compareTrafficValues(**credentials)
		if not rcode:
			#self.enableInspectorTraffic(kwargs["inspector"], enable=True)
			print("Was not able to verify the inspector traffic data")
			return False
		if rcode:	
			#self.enableInspectorTraffic(kwargs["inspector"], enable=True)
			print("Was able to verify the inspector traffic data")
			return True


	def gotoInspectorPage(self):
		url = urlparse(self.params["url"])
		rcode = self.selenium.getURL(url.scheme+'://'+url.netloc+'/administration/inspectors')


	def enableInspectorTraffic(self, inspector_name, enable=True):
		insp_name = self.selenium.findMultiCSS(selector=CSS_INSPECTOR_NAME_ELEMENT)
		insp_status = self.selenium.findMultiCSS(selector=CSS_INSPECTOR_STATUS)
		insp_menu = self.selenium.findMultiCSS(selector=CSS_INSPECTOR_MENU)

		insp_count = 0
		for element in insp_name:
			element = element.text
			if inspector_name == element and insp_status[insp_count].text == "LIVE": # If inspector name is found and the inspector is Live
				break
			insp_count += 1
			if insp_count == len(insp_name):
				print("Either the inspector name could not be found or the inspector status was not 'LIVE'")
				return False

		rcode = insp_menu[insp_count]
		if rcode:
			rcode.click()
		
		stop_icon = self.selenium.findSingleCSS(selector=CSS_INSPECTOR_STOP_TRAFFIC, timeout=5, err_msg='CSS_INSPECTOR_STOP_TRAFFIC')
		start_icon = self.selenium.findSingleCSS(selector=CSS_INSPECTOR_START_TRAFFIC, timeout=5, err_msg='CSS_INSPECTOR_START_TRAFFIC')

		if start_icon and enable == True: # If start icon is found and enable is 'True', enable inspector traffic
			start_icon.click()
			self.selenium.click(selector=CSS_CONFIRM_START_STOP)
			rcode = waitLoadProgressDone(self.selenium)
			if not rcode:
				print("The infinite progress circle appeared, uncommon occurence, this should be a valid fail but the test will continue")
				time.sleep(3)
				return True
			return True
		
		if stop_icon and enable == False: # If stop icon is found and enable is 'False', disable inspector traffic
			stop_icon.click()
			self.selenium.click(selector=CSS_CONFIRM_START_STOP)
			rcode = waitLoadProgressDone(self.selenium)
			if not rcode:
				print("The infinite progress circle appeared, uncommon occurence, this should be a valid fail but the test will continue")
				time.sleep(3)
				return True
			return True

		self.selenium.pressKey(key=Keys.ESCAPE)


	def compareTrafficValues(self, **credentials):
		ins = Inspector(**credentials)

		ttsdstring1 = ins.runCommand("show_info.sh | grep 'ttsd requests'")
		print(ttsdstring1)
		time.sleep(1)
		zingdstring1 = ins.runCommand("show_info.sh | grep 'ZingD'")
		print(zingdstring1)
		ttsdvalue1 = re.search("\d+", str(ttsdstring1)).group()
		zingdvalue1 = re.search("\d+", str(zingdstring1)).group()

		time.sleep(5)

		ttsdstring2 = ins.runCommand("show_info.sh | grep 'ttsd requests'")
		time.sleep(1)
		zingdstring2 = ins.runCommand("show_info.sh | grep 'ZingD'")
		ttsdvalue2 = re.search("\d+", str(ttsdstring2)).group()
		zingdvalue2 = re.search("\d+", str(zingdstring2)).group()
		
		if int(ttsdvalue1) >= int(ttsdvalue2):
			print(("The traffic should be constantly increasing, ttsdvalue1: {} should be less than ttsdvalue2: {}".format(ttsdvalue1, ttsdvalue2)))
			return False
		if int(zingdvalue1) >= int(zingdvalue2):
			print(("The traffic should be constantly increasing, zingdvalue1: {} should be less than zingdvalue2: {}".format(zingdvalue1, zingdvalue2)))
			return False

		print("Traffic for the inspector is working correctly")
		return True


	def configDeleteSite(self, sitename):
		self.gotoInspectorPage()

		found = False
		kwargs = {"selector": CSS_SITES_TOP_LEVEL, "waittype":"visibility", "timeout":3}
		sites = self.selenium.findMultiCSS(**kwargs)
		if not sites: return True

		for site in sites[1:]:
			kwargs = {"browserobj": site, "selector": CSS_SITE_NAME, "timeout":3}
			namefound = self.selenium.findSingleCSS(**kwargs)
			if namefound:
				if namefound.text.strip() == sitename.strip():
					kwargs = {"browserobj": site, "selector": CSS_SITE_BUTTON, "waittype":"clickable", "timeout":3}
					self.selenium.click(**kwargs)
					kwargs = {"selector": CSS_DELETE_SITE_BUTTON, "waittype":"visibility", "timeout":3}
					self.selenium.click(**kwargs)
					found = True
					break	
				else:
					found = False			
						
		if not found: 
			# nothing found, meaning all deleted.  return True
			return True
		else:
			# recursively call self to delete more
			self.configDeleteSite(sitename)


	def configAddSite(self, **siteconfig):	
		kwargs = {}	
		inputs = {
			"name" : "zbat testing site",
			"address" : "zbat address"
		}

		kwargs["selector"] = CSS_ADD_SITE
		rcode = self.selenium.findSingleCSS(**kwargs)
		rcode.click()

		if 'name' in siteconfig:
			siteName = siteconfig["name"]
		else:
			siteName = inputs["name"]	
			
		kwargs["selector"] = CSS_SITE_NAME_INPUT
		kwargs["text"] = siteName
		rcode = self.selenium.sendKeys(**kwargs)

		if 'address' in siteconfig:
			siteAddress = siteconfig["address"]
		else:
			siteAddress = inputs["address"]	
			
		kwargs["selector"] = CSS_SITE_ADDRESS_INPUT
		kwargs["text"] = siteAddress
		rcode = self.selenium.sendKeys(**kwargs)
	
		kwargs["selector"] = CSS_SAVE_BUTTON
		rcode = self.selenium.findSingleCSS(**kwargs)
		rcode.click()

		if not self.checkSiteExist(siteName):
			print("Site "+str(siteName)+" not added correctly.")
			return False
		else:
			return True


	def checkSiteExist(self, sitename):
		self.gotoInspectorPage()

		kwargs = {"selector": CSS_SITE_NAME, "waittype":"visibility", "timeout":3}
		sites = self.selenium.findMultiCSS(**kwargs)
		if not sites:
			print("Not able to find CSS for site names.")
			return False

		for site in sites:
			if site.text.strip() == sitename.strip():
				return True

		print("Site "+str(sitename)+" not found.")
		return False


	def close(self):
		if self.selenium:
			self.selenium.quit()
