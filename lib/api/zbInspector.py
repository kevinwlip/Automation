#!/usr/bin/python


import pdb, time, json, math
from common.zbSSH import Shell, CLI
from common.zbLog import RemoteLog
from collections import OrderedDict

'''
Note that in order to this script to work with Inspector, you'll need to do some
preparing on Inspector.  Follow these steps:
	On Inspector, vi /etc/sudoer, /zingbox/backup/etc/sudoer
		1)  Comment out requiretty
				#Defaults    requiretty
		2) ADD THIS AT THE END OF THE FILE  Allow inspector group to not having to enter in password
				inspector ALL=(ALL) NOPASSWD: ALL 
		3)  When running command, enter the full path.  Example /usr/sbin/show_info.sh
'''

class Inspector():
	
	def __init__(self, **kwargs):
		#self.shell = Shell(**kwargs)
		self.shell = CLI(**kwargs)

	def runCommand(self, cmd):
		output, err = self.shell.runCommand(cmd)
		return output, err


	def getAIMSLog(self, lines=100):
		logname = '/var/log/messages'
		log = RemoteLog(shell=self.shell)
		log.grepLog(logname, 'aims')


	def getZFWLog(self, lines=100):
		logname = '/var/log/messages'
		log = RemoteLog(shell=self.shell)
		log.grepLog(logname, 'zfw')


	def getSIEMLog(self, lines=100):
		logname = '/var/log/messages'
		log = RemoteLog(shell=self.shell)
		log.grepLog(logname, 'siem')

	def clearCounter(self):
		output, err = self.runCommand("sudo service zingd restart")

	def showInfo(self):
		output, err = self.runCommand("/usr/sbin/show_info.sh")
		zingd = output[output.find("ZingD Info and Counters"):]
		# change the result into json
		zingdJSON = {}
		
		lines = zingd.split("\n")
		iterlines = iter(lines)
		next(iterlines)
		firstlevel = 2.0
		lastKeys = []
		
		for l in iterlines:
			currSpace = len(l) - len(l.lstrip(' '))
			if currSpace > 0:
				pair = [item.strip() for item in l.split(":")]
				key = pair[0]
				value = pair[1]
				
				currlevel = math.ceil(currSpace/firstlevel)
				if currlevel == 1:
					if value == "":
						zingdJSON[key] = {}
					else:
						zingdJSON[key] = value
					try:
						lastKeys[0] = key
					except:
						lastKeys.append(key)
				
				elif currlevel == 2:
					lastKey = lastKeys[0]
					if value == "":
						zingdJSON[lastKey][key] = {}
					else:
						zingdJSON[lastKey][key] = value

					try:
						lastKeys[1] = key
					except:
						lastKeys.append(key)
				
				elif currlevel == 3:
					lastKey = lastKeys[0]
					lastKey2 = lastKeys[1]
					if value == "":
						zingdJSON[lastKey][lastKey2][key] = {}
					else:
						zingdJSON[lastKey][lastKey2][key] = value

					try:
						lastKeys[2] = key
					except:
						lastKeys.append(key)
				
				elif currlevel == 4:
					lastKey = lastKeys[0]
					lastKey2 = lastKeys[1]
					lastKey3 = lastKeys[2]
					if value == "":
						zingdJSON[lastKey][lastKey2][lastKey3][key] = {}
					else:
						zingdJSON[lastKey][lastKey2][lastKey3][key] = value

					try:
						lastKeys[3] = key
					except:
						lastKeys.append(key)
				
				else:
					print(("{} not supported".format(currSpace)))
					return False
		return json.dumps(zingdJSON)


	def close(self):
		self.shell.close()



#test
#kwargs = {"hostname":"XX.XX.XX.XX", "username":"XXXXXX", "password":"XXXXXX"}
#ins = Inspector(**kwargs)
#info = ins.showInfo()
#print (info)
#ins.close()