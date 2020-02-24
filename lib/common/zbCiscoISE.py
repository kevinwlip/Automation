#!/usr/bin/python


import urllib3, requests, pdb
from requests.packages.urllib3.exceptions import InsecureRequestWarning
from datetime import datetime, timedelta

urllib3.disable_warnings()
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)



class CiscoISE:
	def __init__(self, host, username, password):
		self.host = host
		self.username = username
		self.password = password
		self.baseurl = 'https://%s:9060/ers/config/endpoint/' % (host)

	def queryAllEndpoints(self):
		""" Query all endpoints/devices and returns the response status code """
		url = self.baseurl
		headers = {"Accept":"application/json", "Content-Type":"application/json"}
		response = requests.get(url, auth=(self.username, self.password), headers=headers, verify=False)
		if response.status_code != 200:
			print(('Status:', response.status_code, 'Headers:', response.headers, 'Error Response:',response.json()))
			return False
		print("Endpoint data in JSON format")
		print("===============================")	
		print(response.json())
		print("===============================")
		return response

	def queryAnEndpoint(self, endpoint):
		""" Query an endpoint/device by their ID and returns the response status code """
		url = self.baseurl+endpoint
		headers = {"Accept":"application/json", "Content-Type":"application/json"}
		response = requests.get(url, auth=(self.username, self.password), headers=headers, verify=False)
		if response.status_code != 200:
			print(('Status:', response.status_code, 'Headers:', response.headers, 'Error Response:',response.json()))
			return False
		print("Endpoint data in JSON format")
		print("===============================")	
		print(response.json())
		print("===============================")
		return response

	def findEndpointContent(self, endpoint, test_key, test_value):
		""" Find the endpoint with the test key and test value from the queryAnEndpoint() result """
		foundDict = {}
		testDict = {}
		testDict[test_key] = test_value

		response = self.queryAnEndpoint(endpoint)
		if not response:
			print('Not able to find the endpoint.')
			return False

		for key, value in response.json()['ERSEndPoint']['customAttributes']['customAttributes'].items():			
			foundDict[key] = value
			if foundDict == testDict:
				print("The key-value pair for the endpoint was found")
				return foundDict if len(foundDict) > 0 else False
			
			print("The key-value pair for the endpoint was not found")
			return False

'''
# testing
HOST = '192.168.20.65'
ENDPOINT = 'f1f6e550-1122-11e8-a535-02425dbb044f'
USERNAME = 'ENTER USERNAME HERE WHEN TESTING'
PASSWORD = 'ENTER PASSWORD HERE WHEN TESTING'

TEST_KEY = 'ZingBoxProfile'
TEST_VALUE = 'Cisco Systems Device'

obj = CiscoISE(HOST, USERNAME, PASSWORD)
result = obj.findEndpointContent(ENDPOINT, TEST_KEY, TEST_VALUE)
#result = obj.queryAnEndpoint(ENDPOINT)
#result = obj.queryAllEndpoints()

print result
'''