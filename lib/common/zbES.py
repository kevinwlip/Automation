#!/user/bin/python2.7

################################################################################
#  Author : Vinh Nguyen
# Purpose : Contain python class related to ElasticSearch 
################################################################################


import requests, pdb, re, sys, os, json, time
from datetime import datetime
from elasticsearch import Elasticsearch

def checkTraffic(stime, snorts, MAC, tenantid):
    ES = zbES()
    kwargs = {}
    kwargs['tenant'] = tenantid
    kwargs['start'] = str(stime)
    kwargs['end'] = 'now'
    kwargs['config'] = os.environ['NODE_ENV']
    kwargs['outfile'] = 'esresult.txt'

    outfile = ES.searchHits(**kwargs)
    snortCheck = ES.checkMatch(outfile, snorts, MAC)
    return snortCheck

def findIndex(l, item, match):
    try:
        idx = l.index(item)
        # if the item already find, find the next one
        if match[idx]:
            # Python functions pass by value (won't change origianl list)
            l[idx]=None
            return findIndex(l, item, match)
        else:
            return idx
    except:
        return -1


class zbES():
    def __init__(self):
        pass    

    # response handling
    def checkResponse(self, response):
        if response.status_code == 200:
            return True
        if response.status_code != 200:
            print("Got %s %s %s" % (response.status_code, response.request.url, response.text))
            if response.status_code == 403:
                return False    
            else:
                sys.exit(0)

    # find list of indices
    def getIndices(self, host, pattern):
        self.es = host
        r = requests.get(self.es+'_cat/indices?v/')
        self.checkResponse(r)

        indices = []
        for line in r.text.splitlines():
            temp = line.split()
            idx = [i for i, item in enumerate(temp) if re.search(pattern, item)]
            for i in idx:
                indices.append(temp[i])

        indices.sort()
        return indices


    # find count for each indices
    def getIndexCount(self, indexList, type, pattern):
        pattern = re.compile(pattern)
        for index in indexList:
            result = {}
            result['index'] = index

            m = pattern.search(index)
            if not m:
                continue

            r = requests.get(self.es+index+'/'+type+'/_count?')
            if self.checkResponse(r):
                count = r.json()['count']
                result['count'] = str(count)
                yield result    


    # query ES
    def searchES(self, **kwargs):
        host = kwargs['host']
        index = kwargs['index']
        body = kwargs['body']

        if type(host) == list:
            es = Elasticsearch(host)
        else:
            es = Elasticsearch([host])

        res = es.search(index=index, body=body)
        if len(res) > 0:
            return res
        else:
            return {}

    # find snort hits by alert message
    def searchHits(self, **kwargs):
        elasticsearch = os.environ['ZBAT_HOME']+"util/jxia-get-events-tools2.py"
        cmd = "python "+elasticsearch+" -a evt_alert"

        if 'deviceid' in kwargs:
            deviceid = kwargs['deviceid']
            cmd += " -d "+deviceid
        
        if 'config' in kwargs:
            config = kwargs['config']
            cmd += " -c "+config

        if 'tenant' in kwargs:
            tenant = kwargs['tenant']
            cmd += " -t "+tenant
        
        if 'anything' in kwargs:
            anything = kwargs['anything']
            cmd += " -f "+anything
        
        if 'start' in kwargs:
            start = kwargs['start']
            cmd += " -s "+start
        
        if 'end' in kwargs:
            end = kwargs['end']
            cmd += " -e "+end
        
        if 'outfile' in kwargs:
            outfile = os.environ['ZBAT_HOME']+"util/"+kwargs['outfile']
            cmd += " -o "+outfile   

        if not (start and end and outfile and config):
            print ("start time, end time, output file and configuration should not be empty")
            return False

        os.system(cmd)
        
        outfile = os.environ['ZBAT_HOME']+"util/"+kwargs['outfile']
        return outfile

    def checkMatch(self, outfile, alerts, devices=None):
        print ("checking Kibana...")
        fileObj = open(outfile, 'rb')
        result = fileObj.read()
        fileObj.close()
        hits = [r for r in result.split("\n") if r != ""]
        if devices is not None:
            hits = [json.loads(h) for h in hits if h != "" and json.loads(h)['_source']['iotDevid'] in devices]
        else:
            hits = [json.loads(h) for h in hits if h != ""]
        os.system("rm "+outfile)
        
        match = [False for i in range(len(alerts))]
        for h in hits:
            msg = h['_source']['evtContent']['msg']
            
            # strip markers in message
            idx = msg.find(" extract=true")
            if idx != -1:
                msg = msg[:idx]
            idx = msg.find(" fastpath=true")
            if idx != -1:
                msg = msg[:idx]
            msg = msg.replace(',', '')
            
            idx = findIndex(alerts, msg, match)
            if (idx != -1) and not match[idx]:
                match[idx] = True

                if all(match):
                    return True
        
        print ("\n\nsnort hits not found:")
        for i in range(len(match)):
            if match[i] == False:
                print((alerts[i]))
        return False


# test
'''
kwargs = {}
# kwargs['deviceid'] = 'aa:bb:cc:dd:01:01'
kwargs['tenant'] = 'testing-soho'
kwargs['start'] = '5d'
kwargs['end'] = 'now'
kwargs['config'] = 'az-testing'
kwargs['outfile'] = 'esresult.txt'
'''
'''
ES = zbES()
MAC = ['aa:bb:cc:dd:01:01', 'aa:bb:cc:dd:01:02']
snortHits = ['ZB ETERNALBLUE_MS17-010_EchoResponse', 'ZB DOUBLEPULSAR.InjectionResponse', 'ZB DOUBLEPULSAR.PingResponse', 'ZB DOUBLEPULSAR.BeaconResponse', 'ZB ETERNALBLUE_MS17-010_SMB_RemoteExecution', 'ZB WannaCry.Dropper', 'ZB ETERNALBLUE_MS17-010_SMB_RemoteExecution', 'ZB ETERNALBLUE_MS17-010_SMB_RemoteExecution_v2']
# result = ES.searchHits(['ZB WannaCry.Dropper extract=true fastpath=true', 'ZB ETERNALBLUE_MS17-010_SMB_RemoteExecution extract=true fastpath=true'], MAC, **kwargs)
result = ES.checkMatch("/Users/huangyuning/Documents/zbat/util/esresult.txt", snortHits, MAC)
print ("test result: {}".format(result))
'''
