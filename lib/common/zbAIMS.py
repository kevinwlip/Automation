#!/usr/bin/python


import urllib3, requests, pdb
from requests.packages.urllib3.exceptions import InsecureRequestWarning
from datetime import datetime, timedelta

urllib3.disable_warnings()
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)


class AIMS:
	def __init__(self, host, clientid):
		self.host = host
		self.clientid = clientid
		self.baseurl = 'https://%s/AIMSUtilityService/AIMS.api' % host


	def _queryAllWorkorder(self, facility):
		url = self.baseurl+'/WorkOrders/Query'
		data = {'ClientID': self.clientid, 'StartingFacility':facility};
		response = requests.post(url, data=data, verify=False)
		return response if response.status_code == 200 else False


	def findWorkOrder(self, facility, tag, earliest, latest):
		foundList = []
		timeformat = '%Y-%m-%dT%H:%M:%S.%f'
		earliestDatetimeObj = datetime.strptime(earliest, timeformat)
		latestDatetimeObj = datetime.strptime(latest, timeformat)
		# query all workorders
		response = self._queryAllWorkorder(facility)
		if not response:
			print('Not able to find work order.')
			return False

		for item in response.json()['Data']:
			if item['TagNumber'] == str(tag):
				workOrderRequestTime = datetime.strptime(item['RequestDateTime'], timeformat)
				if workOrderRequestTime >= earliestDatetimeObj and workOrderRequestTime <= latestDatetimeObj:
					foundList.append(item)
			
		return foundList if len(foundList) > 0 else False




'''
# testing
HOST = 'zingboxdemo.aimsasp.net'
FACILITY = 'SOUTH'
CLIENTID = '1F1596D1-E0D8-4415-A5F0-3DE6218DDBA3'
TAG = '1002'
#EARLIEST = (datetime.utcnow()-timedelta(minutes=10)).strftime('%Y-%m-%dT%H:%M:%S.%f')
EARLIEST = '2010-01-01T00:00:00.000000'
LATEST = datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%S.%f')

obj = AIMS(HOST, CLIENTID)
result = obj.findWorkOrder(FACILITY, TAG, EARLIEST, LATEST)
'''


