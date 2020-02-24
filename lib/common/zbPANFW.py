#!/usr/bin/python

'''
Prior to running this module, install pandevice through command
pip install pandevice
pip install --upgrade pandevice
'''

import re, os, json, pdb, subprocess
#from subprocess import check_output


class PanFW:
	def __init__(self, host, username, password):
		self.host = host
		self.username = username
		self.password = password


	def findLatestCommits(self):
		panXpathCommand = '<show><jobs><all/></jobs></show>'
		systemCommand = 'panxapi.py -l %s:%s -h %s -jo %s' % (self.username, self.password, self.host, panXpathCommand)
		output = self._runCommand(systemCommand)
		if output:
			if 'response' not in output:
				print('PanFW: No response field from "show jobs all" output')
				return []
			response = output['response']

			if 'result' not in response:
				print('PanFW: No result field from "show jobs all" output["response"]')
				return []
			result = response['result']

			if 'job' not in result:
				print('PanFW: No job field from "show jobs all" output["response"]["result"]')
				return []
			return result['job']
		print('PanFW: No output from "show jobs all"')
		return []

	def findSecurityPolicies(self):
		panXpathCommand= '<show><running><security-policy/></running></show>'
		systemCommand = 'panxapi.py -l %s:%s -h %s -jo %s' % (self.username, self.password, self.host, panXpathCommand)
		output = self._runCommand(systemCommand)
		if output:
			if 'response' not in output:
				print('PanFW: No response field from "show running security-policy" output')
				return []
			response = output['response']

			if 'result' not in response:
				print('PanFW: No result field from "show running security-policy" output["response"]')
				return []
			result = response['result']

			if 'member' not in result:
				print('PanFW: No member field from "show running security-policy" output["response"]["result"]')
				return []
			policies = result['member']
			return policies
		return []


	def _runCommand(self, command):
		if isinstance(command, str):
			command = command.split(' ')

		process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
		returncode = process.wait()
		output = process.stdout.read()

		match = re.findall(r'op: success', output)
		if match:
			output = output[output.find('{'):]
			output = re.sub(r'\n', '', output)
			output = json.loads(output)
			return output
		return False
		
'''
# test
HOST = '192.168.10.23'
USERNAME = 'admin'
PASSWORD = 'admin'
obj = PanFW(HOST, USERNAME, PASSWORD)
result = obj.findLatestCommits()
# result = obj.findSecurityPolicies()
import pdb; pdb.set_trace()
'''
