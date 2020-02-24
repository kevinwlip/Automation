import time
import os
from datetime import datetime
from zbAlertsAPI import checkAlert, checkNewAlert
from zbConfig import devices
from zbKafka import createKafka, checkTtsd, checkTagged
from common.zbAWS import syncAWS
from common.zbES import checkTraffic
from common.zbTrafficGenerator import replayPcap
from common.zbRedis import deleteSubduedAlert

def verifyBlacklist(TG_HOST, TG_PORT, TG_INTF1, TG_INTF2, TG_UNAME, TG_PWD, REDIS_HOST, REDIS_PWD, REDIS_TESTING_TENANT, siteTest, tenantid, forceall=False, **policyTestsConfig):
    # clean up subdued alerts
    deleteSubduedAlert(REDIS_HOST, REDIS_PWD, REDIS_TESTING_TENANT, devID=devices["Rebeccas-MBP"]["deviceid"], alertID=policyTestsConfig['blacklistPolicyId'])

    # policy name
    name = "zbat blacklist test don't delete"
    flows = [["192.168.10.209", "40.100.162.178"]]

    # precheck for alert
    alertPre = checkAlert(siteTest, tenantid, name)

    syncAWS(TG_HOST, TG_PORT, TG_UNAME, TG_PWD)

    # get Kafka offset before replay
    taggedKafka = createKafka("tagged")
    taggedStart = taggedKafka.getOffset()
    ttsdKafka = createKafka("analytics_ttsd")
    ttsdStart = ttsdKafka.getOffset()

    # tcpreplay
    intf = {'intf1': TG_INTF1, 'intf2': TG_INTF2, 'server-client': False}
    if not replayPcap("pcaps/normal/ESPN.pcap", intf, None, None, TG_HOST, TG_PORT, TG_UNAME, TG_PWD):
        print ("pcap replay failure")
        return False
    print(("replay {} successfully\nWait for 5 minutes for alert processing".format(file)))
    print(("current time: {}".format(datetime.now())))
    time.sleep(300)

    # check alert in API
    print ("\n===== API check =====")
    alertCheck = checkNewAlert(name, alertPre, siteTest, tenantid, flows)

    if alertCheck and not forceall:
        print ("\n\nalerts found in API")
        print(("alertCheck: {}".format(alertCheck)))
        return True

    # check Kafka
    print ("\n====== Kafka check =====")
    taggedKafka = createKafka("tagged")
    ttsdKafka = createKafka("analytics_ttsd")
    taggedStop = taggedKafka.getOffset()
    ttsdStop = ttsdKafka.getOffset()

    # note: becuase we are always using ESPN without rewriting here, so we can input the local/remote IPs directly
    ttsdCheck = checkTtsd(ttsdKafka, ttsdStart, ttsdStop, flows)
    taggedCheck = checkTagged(taggedKafka, taggedStart, taggedStop, [devices["Rebeccas-MBP"]["deviceid"]], name)
    print(("\n\nalertCheck: {}\nttsdCheck: {}\ntaggedCheck: {}".format(alertCheck, ttsdCheck, taggedCheck)))

    return alertCheck and ttsdCheck and taggedCheck

def verifyWhitelist(TG_HOST, TG_PORT, TG_INTF1, TG_INTF2, TG_UNAME, TG_PWD, REDIS_HOST, REDIS_PWD, REDIS_TESTING_TENANT, siteTest, tenantid, forceall=None, **policyTestsConfig):
    # clean up subdued alerts
    newMAC = 'aa:bb:81:01:01:05'
    newIP = '81.1.1.5'
    IPs = [['192.168.10.209', newIP]]
    MACs = [[devices["Rebeccas-MBP"]["deviceid"], newMAC]]
    deleteSubduedAlert(REDIS_HOST, REDIS_PWD, REDIS_TESTING_TENANT, devID=newMAC, alertID=policyTestsConfig['whitelistPolicyId'])

    # policy name
    name = "zbat whitelist test don't delete"
    flows = [[newIP, "40.100.162.178"]]

    # precheck for alert 
    alertPre = checkAlert(siteTest, tenantid, name)

    # sync pcaps from AWS
    syncAWS(TG_HOST, TG_PORT, TG_UNAME, TG_PWD)

    # get Kafka offset before replay
    taggedKafka = createKafka("tagged")
    taggedStart = taggedKafka.getOffset()
    ttsdKafka = createKafka("analytics_ttsd")
    ttsdStart = ttsdKafka.getOffset()

    # tcpreplay
    intf = {'intf1': TG_INTF1, 'intf2': TG_INTF2, 'server-client': False}
    if not replayPcap("pcaps/normal/ESPN.pcap", intf, IPs, MACs, TG_HOST, TG_PORT, TG_UNAME, TG_PWD):
        print ("pcap replay failure")
        return False
    print(("replay {} successfully\nWait for 5 minutes for alert processing".format(file)))
    print(("current time: {}".format(datetime.now())))
    time.sleep(300)

    print ("\n===== API check =====")
    alertCheck = checkNewAlert(name, alertPre, siteTest, tenantid, flows)

    if alertCheck and not forceall:
        print ("\n\nalerts found in API")
        print(("alertCheck: {}".format(alertCheck)))
        return True

    # check Kafka
    print ("\n====== Kafka check ======")
    taggedKafka = createKafka("tagged")
    ttsdKafka = createKafka("analytics_ttsd")
    taggedStop = taggedKafka.getOffset()
    ttsdStop = ttsdKafka.getOffset()

    # note: becuase we are always using ESPN here, so we can input the remote IPs directly
    ttsdCheck = checkTtsd(ttsdKafka, ttsdStart, ttsdStop, flows)
    taggedCheck = checkTagged(taggedKafka, taggedStart, taggedStop, [newMAC], name)

    print(("\n\nalertCheck: {}\nttsdCheck: {}\ntaggedCheck: {}".format(alertCheck, ttsdCheck, taggedCheck)))

    return alertCheck and ttsdCheck and taggedCheck

# check threat by file
def verifyThreat(alertname, info, siteTest, tenantid, forceall=None):
    alertPre = info[0]
    stime = info[1]
    taggedStart = info[2]
    ttsdStart = info[3]
    mapping = info[4]
    MAC = info[5]
    flows = info[6]

    snorts = None
    for m in mapping:
        if m['published'] == alertname:
            snorts = m['snort-hits'].split("\n")
            break   
    
    # alert check
    print ("\n====== API check ======")
    alertCheck = checkNewAlert(alertname, alertPre, siteTest, tenantid, flows)

    if alertCheck and not forceall:
        print ("\n\nalerts found in API")
        print(("alertCheck: {}".format(alertCheck)))
        return True
    
    # if the alert Check does not pass: whitebox testing -> check Kibana (snort)
    print ("\n===== Kibana check ======")
    snortCheck = None

    if len(snorts)==0:
        print ("no published snort hits")
        snortCheck = True

    else:
        snortCheck = checkTraffic(stime, snorts, MAC, tenantid)

    if not snortCheck and not forceall:
        print ("\n\ntraffic is not received in Kibana cloud")
        print(("alertCheck: {}\nsnortCheck: {}".format(alertCheck, snortCheck)))
        return False
    
    # if the alert arrive the cloud: whitebox testing -> check Kafka
    print ("\n===== Kafka check =====")
    taggedKafka = createKafka("tagged")
    ttsdKafka = createKafka("analytics_ttsd")
    taggedStop = taggedKafka.getOffset()
    ttsdStop = ttsdKafka.getOffset()

    ttsdCheck = checkTtsd(ttsdKafka, ttsdStart, ttsdStop, flows)
    taggedCheck = checkTagged(taggedKafka, taggedStart, taggedStop, MAC, alertname)
    print(("\n\nalertCheck: {}\nsnortCheck: {}\nttsdCheck: {}\ntaggedCheck: {}".format(alertCheck, snortCheck, ttsdCheck, taggedCheck)))

    return alertCheck and snortCheck and ttsdCheck and taggedCheck
