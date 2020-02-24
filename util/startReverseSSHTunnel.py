#!/usr/bin/python

import re
from subprocess import call, check_output

'''
This script is meant for crontab to be running every 5 minutes
It brings up reverse SSH tunnel if not present.
These tunnels are required for operation of ZBAT

To configure crontab
	crontab -e
	# add entry
	*/5 * * * * python /home/automation/startReverseSSHTunnel.py

This script requires that you've already setup certificate for ssh.  If you haven't here are the steps:
1)  On local host generate a private/public key pair.  Name your cert 'zbat' and leave passphrase empty
	ssh-keygen -t rsa -b 2048 -v
2)  Copy public key over to remote host.  This is the same thing as copy the content of zbat.pub into remote host file .ssh/authorized_keys
	ssh-copy-id -i .ssh/zbat.pub automation@zbat001.cloud.zingbox.com
'''

sshTunnelMapping = 	[
			"22443:192.168.10.23:443",   # connection for panfw
			"22089:192.168.10.40:8089",  # connection for splunk
			"22022:192.168.20.184:22",   # connection for traffic generator
			"22094:192.168.10.40:9400",  # connection for openvas
			"22044:192.168.10.63:4444"   # connection to Window Laptop (selenium for IE11)
			]

# hosts list and corresponding certificate to use for authentication between this host and remote userHosts
userHosts = ["automation@zbat001.azure.zingbox.com", "automation@zbat001.cloud.zingbox.com"]
certs = ["/home/automation/.ssh/zbat.pem", "/home/automation/.ssh/zbat2.pem"]

# for each host, start all the reverse SSH tunnel mapping
for i in xrange(0, len(userHosts)):
    for mapping in sshTunnelMapping:

        # For each host, increment the mapping port from 22xxx to 23xxx, 24xxx, etc...
        if i > 0:
            tempmapping = list(mapping)
            tempmapping[1] = 2+i
            mapping = ''.join(str(v) for v in tempmapping)

        # search for existing tunnel
        try:
            grepCommand = ["ps", "-fC", "ssh"]
            output = check_output(grepCommand)
        except Exception as e:
            output = "not found"
            pass

        # start tunnel if none existing
        rePattern = re.compile(mapping + ' ' + userHosts[i])
        if not re.search(rePattern, output):
            command = ["ssh", "-R", mapping, userHosts[i], "-i", certs[i], "-fNT"]
            print(' '.join(command))
            call(command)
