import json
import time
from zbAPI import zbAPI
from common.zbCommon import difference

# input: JSON obj, key: local or remote
def findIP(obj, key):
    if key == "local":
        try:
            local = obj['msg']['localip']
        except:
            local = "null"
        if local == "null":
            values = obj['msg']['values']
            for val in values:
                if val['label'] == "local IP" or val['label'] == "local IPs":
                    local = val['value']
                    if len(local) == 1:
                        local = local[0]
        if local == "null":
            return False
        else:
            return local
    
    elif key == "remote":
        try:
            remote = obj['msg']['toip']
        except:
            remote = "null"
        if remote == "null":
            values = obj['msg']['values']
            for val in values:
                if val['label'] == "remote IP" or val['label'] == "remote IPs":
                    remote = val['value']
                    if len(remote) == 1:
                        remote = remote[0]
        if remote == "null":
            return False
        else:
            return remote
    else:
        print ("unvalid key for findIP")
        return False

def callAPI(API, tenantid, mode, alertname):
    inputAlert = {}
    inputAlert["etime"] = "now"
    inputAlert["offset"] = "0"
    inputAlert["pagelength"] = "50"
    inputAlert["sortdirection"] = "desc"
    inputAlert["sortfield"] = "date"
    inputAlert["stime"] = -1
    inputAlert["tenantid"] = tenantid
    inputAlert["type"] = "policy_alert"
    if mode == "alert":
        inputAlert["resolved"] = "no"
    elif mode == "review":
        inputAlert["review"] = True
    retrieve = API.alertRetrieve(**inputAlert)
    retrieve = json.loads(retrieve)

    curr = []
    time = []
    for item in retrieve['items']:
        if item['name'] == alertname:
            curr.append(item)
            time.append(item['date'])
    return (curr, time)


def checkAlert(siteTest, tenantid, alertname):
    print ("\nGetting current alerts and numbers...")
    kwargs = {}
    kwargs["host"] = siteTest
    API = zbAPI(**kwargs)
    
    curr = None
    time = None
    curr, time = callAPI(API, tenantid, "alert", alertname)
    if len(curr) == 0:
        curr, time = callAPI(API, tenantid, "review", alertname)

    print(("Current alerts info for {}: \nnum: {}".format(alertname, len(curr))))
    print(("time: {}".format(time)))
    return curr

def checkNewAlert(alertname, pre, siteTest, tenantid, flows):
    # check for alert
    post = checkAlert(siteTest, tenantid, alertname)
    match = [False for _ in range(len(flows))]
    # check by differences in json post - pre
    change = difference(pre, post)
    # match source/dest
    if len(change) > 0:
        for c in change:
            c = json.loads(c)
            local = findIP(c, "local")
            remote = findIP(c, "remote")
            if local != False and remote != False:
                print(("local, remote: {}".format([local, remote])))
                print(("target flow: {}".format(flows)))
                if [local, remote] in flows:
                    idx = flows.index([local, remote])
                    if not match[idx]:
                        match[idx] = True
                        if all(m for m in match):
                            return True

    print(("API alert number check False: "+str(alertname)))
    return False
