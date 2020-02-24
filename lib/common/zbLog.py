#!/usr/bin/python


import logging, pdb
from .zbSSH import Shell
from .zbCommon import iterItem


class RemoteLog():
	''' Class SSH to a remote system and retrieve logs.  
	Can pass in shell object or can start new ssh'''
	def __init__(self, shell=None, **kwargs):
		if not shell:
			self.hostname = kwargs['hostname']
			self.username = kwargs['username']
			self.password = kwargs['password']
			self.shell = Shell(**kwargs)
		else:
			self.shell = shell


	def getLogLatest(self, logfile, lines=100):
		for logname in (iterItem(logfile)):
			command = 'tail -f %s %s' % (str(lines), logname)
			yield self.getLog(logname, command)


	def grepLog(self, logfile, greptext):
		grepstring = '|'.join(greptext) if type(greptext) == list else greptext
		for logname in (iterItem(logfile)):
			command = 'grep -E %s %s' % (grepstring, logname)
			yield self.getLog(logname, command)


	def getLog(self, logname, command):
		logging.info('Shell command: %s' % command)
		(output,err) = self.shell.exec_command(command)
		return output if not err else False


	def closeConnection(self):
		self.shell.close()