How to setup the Appspider testing automation in 6 easy steps:

Step 1: Install appspider on your designated windows slave machine (henceforth called machine A), the pro version is sufficient. Then install AutoIt3

Current Machine (172.31.19.182) info

User: automation

Password: ***

Step 2: Login to testing.zingbox.com on internet explorer. Make sure that saving sessions and caches are enabled

Step 3: Create a new testing config in appspider. Copy the attached scfg file into the config's folder under documents/appspider/scans/[config name]. Make sure it's the only config there. Config file is located in [efs server]/zbat/AppSpider/TestingServer.scfg.

Step 4: Create the traffic gen files that navigate throughout our website, as Appspider cannot crawl normally due to our website not using conventional links. This can be done via Appspider's internal Traffic Creator or via its supported traffic gen formats. Zip file containing traffic files are located in [efs server]/zbat/AppSpider/Testing_soho_traffic.zip

Step 5: Go to your jenkins master machine and designate Machine A as a slave agent as per this guide: https://wiki.Jenkins.Io/display/jenkins/step+by+step+guide+to+set+up+master+and+slave+machines+on+windows NOTE: MAKE SURE THE JENKINS AGENT IS RUNNING IN THE FOREGROUND AND NOT AS A SERVICE.

Step 5.5: Schedule the batch file to run as a Task with Task Scheduler on logon. Be sure to disable the "Kill task after 3 days option"

Step 6: Using jenkins, start a new job that runs the appspider scan job on windows. Be sure to restrict the node to the windows machine and set the job to "Run a windows batch command"
Use this command: 
""
appspidercmd -cfg documents/appspider/scans/[config name]
""

How to set up the EFS file sharing and automatic Appspider report parsing:

Step 1: Ask your network/cloud adminstrator for the URL of the QA EFS partition

Step 2: Using NFS4, mount the EFS onto a linux testing machine under the directory /mnt/efs/

Mount command: "fs-106507b9.efs.us-west-2.amazonaws.com:/ /mnt/efs nfs4 user,rw,exec,dev,suid,nfsvers=4.1,rsize=1048576,wsize=1048576,hard,timeo=600,retrans=2 0 0"

Step 3: Using Samba, turn the mounted EFS drive into a Samba share as per this guide:
https://zingbox.atlassian.net/wiki/spaces/QH/pages/338952193/AWS+EFS+Mirroring+Procedure

Step 4: On Windows, use Map Network Drive to mount the Samba share

Step 5: On the Windows machine, download SyncToy and use it to Sync the AppSpider scan reports from Documents/AppSpider/[Config Name] to the Samba share

Step 6: Start a Jenkins job to run the included test_Appspider script on the testing machine.
