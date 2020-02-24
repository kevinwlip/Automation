#!/usr/bin/python

import urllib3, requests, time, re, sys, pdb
from requests.packages.urllib3.exceptions import InsecureRequestWarning
from xml.dom import minidom

urllib3.disable_warnings()
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)


class Splunk:
	def __init__(self, baseurl, username, password):
		self.baseurl = baseurl
		self.username = username
		self.password = password
		self.headers = {'Authorization': 'Splunk %s' % self._getSessionKey()}
		self.verify = False
		

	def _getSessionKey(self):
		try:
			data = {'username': self.username, 'password': self.password}
			req = requests.post(self.baseurl+'/services/auth/login', verify=False, data=data, auth=(self.username, self.password))
			sessionkey = minidom.parseString(req.text).getElementsByTagName('sessionKey')[0].childNodes[0].nodeValue
			return sessionkey
		except Exception as e:
			sys.exit('Failing auth with Splunk.  Not able to obtain session key')


	def _buildQuery(self, queryDict, limit):
		''' Given a query dictionary, return a query string for Splunk '''
		queryList = []

		# special handling for search
		if 'search' in queryDict:
			queryList.append('search \"%s\"' % queryDict['search'])

		# handling for the rest of key pair
		for key,val in queryDict.items():
			if key in ['search', 'earliest', 'latest']: continue
			queryList.append('%s=%s' % (key,val))

		# special handling for time query key 'earliest' and 'latest'
		tList = []
		for tquery in ['earliest', 'latest']:
			if tquery in queryDict:
				tList.append('%s=%s' % (tquery, queryDict[tquery]))
		queryList.append(' '.join(tList))
		
		# join search string
		query = ' AND '.join(queryList)

		# add limit
		if limit: query = '%s | head %s' % (query, str(limit))
		return query


	def _searchStatus(self, sid):
		isNotDone = True
		for i in range(0,30):
			time.sleep(1)
			req = requests.get(self.baseurl+'/services/search/jobs/'+sid, headers=self.headers, verify=self.verify)
			isFailedStatus = re.search(r'isFailed">(\d+)', req.text)
			if isFailedStatus:
				if isFailedStatus.group(1) == '1':
					return False
			isDoneStatus = re.search(r'isDone">(\d+)', req.text)
			if isDoneStatus:
				if isDoneStatus.group(1) == '1':
					return True


	def _searchResult(self, sid):
		req = requests.get(self.baseurl+'/services/search/jobs/'+sid+'/results/?output_mode=json&count=0', headers=self.headers, verify=self.verify)
		return req.text if req.status_code == 200 else False
		


	def search(self, query=False, limit=False):
		# if no query param, set default
		if not query: query = 'search *'
		# if query param is dict, then build into string
		if isinstance(query, dict): query = self._buildQuery(query, limit)
		# if query param is string, no need to do anything
		if isinstance(query, str): pass

		data = [('search', query)]
		if limit is not False and type(limit) == int:
			data.append(('max_count', limit))
		req = requests.post(self.baseurl+'/services/search/jobs', headers=self.headers, data=data, verify=self.verify)
		sid = minidom.parseString(req.text).getElementsByTagName('sid')[0].childNodes[0].nodeValue

		# check search status
		rcode = self._searchStatus(sid)
		if not rcode:
			print("Failure with search")
			return False
		# get result
		result = self._searchResult(sid)
		if not result:
			print("Failure to obtain result")
			return False
		return result



'''
# testing
# example zingbox raw alert data
#INFO:siem-syslog:CEF:0|ZingBox|Inspector|1.0|ZingBox Alert:policy_alert|JW Low Alert level testing|3|dvcmac=88:c9:d0:ee:76:a7 src=192.168.10.234 shost=android-cef89a3962f9f1ed dst=224.0.0.251 dhost=multicast cs1Label=Description cs1=Detected established connections to multicast cs2Label=Values cs2=[{"label":"byte count","value":272},{"label":"packet count","value":2},{"label":"bytes received","value":0},{"label":"bytes transmitted","value":272},{"label":"applications","value":"UDP"}]
#INFO:siem-syslog:CEF:0|ZingBox|Inspector|1.0|asset|Asset Identification|1|dvc=192.168.10.212 dvcmac=4c:66:41:aa:50:d4 dvchost=Samsung-Galaxy-S7 cs1Label=Profile cs1=Android cs2Label=Category cs2=Smartphone or Tablet cs3Label=Type cs3=Non_IoT cs4Label=Vendor cs4=generic cs5Label=Model cs5=Android

d = {
	"search":"Asset Identification",
	"dvcmac":"88:c9:d0:ee:76:a7",
	"earliest":"12/11/2012:20:00:00",
	"latest":"12/11/2017:20:00:00"
}

d = {
	"search":"Asset Identification",
	"dvcmac":"88:c9:d0:ee:76:a7",
	"earliest":"-1h"
}

BASEURL = 'https://192.168.10.239:8089'
USERNAME = 'fill_me_in'
PASSWORD = 'fill_me_in'
obj = Splunk(BASEURL, USERNAME, PASSWORD)
print obj.search(query=d, limit=1)
'''
