#!/usr/bin/python3


import xml.etree.cElementTree as ET
import pdb, time
from datetime import datetime
#from zbConfig import defaultEnv
from httpobs.scanner.local import scan



class MozillaObs:
	def scanHost(host):
		jsonList = []
		try:
			element = scan(host)
		except Exception as e:
			print (e)
			print ("Scan failed")
		print ("")
		print(("Result for: " + host))
		for key in element['tests']:
			print(("[" + key + "] Passed?: " + str(element['tests'][key]['pass']) +  "   Reason: " + element['tests'][key]["score_description"]))
		print("===============================")
		iter_num = 0
		for item in element['scan']:
			if(item != 'response_headers') and iter_num < 4:
				iter_num = iter_num + 1
				print((str(item) + " : " + str(element['scan'][item])))
		if(element['scan']['grade'] == 'F'):
			return False
		else:
			return True





