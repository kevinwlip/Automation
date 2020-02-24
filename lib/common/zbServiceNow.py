#!/usr/bin/python


import urllib3, requests, pdb
from requests.packages.urllib3.exceptions import InsecureRequestWarning
from datetime import datetime, timedelta

urllib3.disable_warnings()
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)



class ServiceNow:
	def __init__(self, dev, username, password):
		self.dev = dev
		self.username = username
		self.password = password
		self.baseurl = 'https://%s.service-now.com/api/now/table/' % (dev)

	def queryAllDevices(self, table_name):
		""" Query all devices in the designated table and returns the response status code """
		url = self.baseurl+table_name
		headers = {"Accept":"application/json", "Content-Type":"application/json"}
		response = requests.get(url, auth=(self.username, self.password), headers=headers, verify=False)
		if response.status_code != 200:
			print(('Status:', response.status_code, 'Headers:', response.headers, 'Error Response:',response.json()))
			return False
		print("Device data in JSON format")
		print("===============================")	
		print(response.json())
		print("===============================")
		return response

	def findDevices(self, table_name, earliest, latest):
		""" Find all devices in the table within a specified time frame """
		foundList = []
		timeformat = '%Y-%m-%d %H:%M:%S'
		earliestDatetimeObj = datetime.strptime(earliest, timeformat)
		latestDatetimeObj = datetime.strptime(latest, timeformat)

		response = self.queryAllDevices(table_name)
		if not response:
			print('Not able to find the specified table.')
			return False

		for item in response.json()['result']:
			if item['sys_class_name'] == str(table_name):
				workOrderRequestTime = datetime.strptime(item['sys_updated_on'], timeformat)
				if workOrderRequestTime >= earliestDatetimeObj and workOrderRequestTime <= latestDatetimeObj:
					foundList.append(item)

		return foundList if len(foundList) > 0 else False

'''
# testing
DEV = 'dev11967'
TABLE_NAME = 'u_medical_devices' # Remember the 'u_' for all tables
USERNAME = 'ENTER USERNAME HERE WHEN TESTING'
PASSWORD = 'ENTER PASSWORD HERE WHEN TESTING'

TENMINAGO = datetime.utcnow() - timedelta(minutes=10)
EARLIEST = '2010-01-01 00:00:00'
#EARLIEST = TENMINAGO.strftime('%Y-%m-%d %H:%M:%S')
LATEST = datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')

obj = ServiceNow(DEV, USERNAME, PASSWORD)
result = obj.findDevices(TABLE_NAME, EARLIEST, LATEST)
#result = obj.queryAllDevices(TABLE_NAME)

print result
'''