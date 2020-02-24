#!/usr/bin/python

import argparse
from elasticsearch import Elasticsearch
from datetime import datetime, timedelta
from time import mktime
import requests
import time
import json
import os
import sys
import re
import subprocess
import urllib3
from requests.packages.urllib3.exceptions import InsecureRequestWarning

urllib3.disable_warnings()
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)


try:
    env = os.environ['ZBAT_HOME']
except:
    print 'Test cannot run.  Please export ZBAT_HOME.'
    sys.exit()

sys.path.append(env+'lib')
from zbConfig import defaultEnv

env = defaultEnv()
esConfig = env["elasticsearch"]

def usage():
    print (__file__ + " -d <device id> -c <configuration> -t <tenantid> -f <anything> -a <alert_type> -s <start time UTC> -e <end time UTC> -o outputfile")
    print ("examples:  ")
    print ("    timestamp inputs.      ==> -s 1494283879 -e 1495147879 notes: it is UTC timestamp")
    print ("    timestamp inputs.      ==> -s \"2017-06-25 02:30:00\" -e \"2017-06-25 05:30:00\" note: it is UTC time")
    print ("    look for last 10 hours ==> -s 10h -e now")
    print ("    look for last 3 days   ==> -s 3d -e now")
    print ("    look in production     ==> -c production")
    print ("    start last 30 days but end with last 28 days, ==> -s 30d -e 28d")
    
def getTenantId(str, config):
    path = os.environ['ZBAT_HOME']+"util/"
    if config == "production":
        proc =subprocess.Popen(["grep %s %stenant-customer-mapping.txt.ppp | cut -d' ' -f2 " % (str, path)], stdout=subprocess.PIPE, shell=True)
        (out, err) = proc.communicate()
        return out.decode("utf-8").strip()  
    elif config == "az-testing" or config == "testing":
        return os.environ['ZBAT_TENANT_INTERNAL_ID']
    else:
        print ("not yet support")
        return False
  

if __name__ == "__main__":

    scriptPath = os.path.dirname(os.path.realpath(__file__))

    parser = argparse.ArgumentParser()
    parser.add_argument("-d", "--deviceid", help="device mac address")
    parser.add_argument("-c", "--config", help="configuration. demo, production, az-testing")
    parser.add_argument("-t", "--tenant", help="external tenant")    
    parser.add_argument("-a", "--alerttype", help="alert type. evt_ttsd, evt_alert, evt_upload etc")    
    parser.add_argument("-f", "--anything", help="anything such as IP, port, or name")
    parser.add_argument("-s", "--start", help="timestamp started")
    parser.add_argument("-e", "--end", help="timestamp ended")
    parser.add_argument("-o", "--outfile", help="output file")
    
    args = parser.parse_args()

    if not (args.start and args.end and args.outfile and args.config):
        usage()
        sys.exit(1)

    outFP = open("%s" % args.outfile, 'w')

    if not args.deviceid :
        deviceid = "00:00:00:00:00:00"
    else :
        deviceid = args.deviceid

    if (not re.match("[0-9a-f]{2}([-:])[0-9a-f]{2}(\\1[0-9a-f]{2}){4}$", deviceid) ) and (deviceid != "00:00:00:00:00:00"):
        print ("Error: invalid device id.  " + deviceid)
        usage()
        sys.exit(2)
    
    if not args.tenant :
        tenantId = "ALL"
    else :
        tenantId = getTenantId(args.tenant, args.config)
        if tenantId =="" :
            print ("Error: invalid tenant. " + args.tenant)
            usage()
            sys.exit(3)

    if not args.alerttype :
        alerttype = "ALL"
    else :
        alerttype = args.alerttype

    curTime = time.time()
    if args.end=="now" :
        args.end = curTime
    
    match = re.search(r"^(\d+)([dh])$", str(args.end))
    if match :
        if match.group(2) == "h":
            args.end = curTime - int(match.group(1))*60*60
        else :
            args.end = curTime - int(match.group(1))*60*60*24
    else :
        match = re.search(r"^(\d+)-(\d+)-(\d+)\s+(\d+):(\d+):(\d+)$", str(args.end))
	if match:
            s = datetime.strptime(args.end, '%Y-%m-%d %H:%M:%S')
            args.end = time.mktime(s.timetuple())
        else :
            args.end = float(args.end)
            
    match = re.search(r"^(\d+)([dh])$", str(args.start))
    if match :
        if match.group(2) == "h":
            args.start = curTime - int(match.group(1))*60*60
        else :
            args.start = curTime - int(match.group(1))*60*60*24
    else :
        match = re.search(r"^(\d+)-(\d+)-(\d+)\s+(\d+):(\d+):(\d+)$", str(args.start))
	if match:
            s = datetime.strptime(args.start, '%Y-%m-%d %H:%M:%S')
            args.start = time.mktime(s.timetuple())
        else :
            args.start = float(args.start)

                    
    #print ("deviceid = " + args.deviceid + " start %f end %f " % (args.start, args.end) )
        args.start = float(args.start)

                    
    #print ("deviceid = " + args.deviceid + " start %f end %f " % (args.start, args.end) )

    print ("info:: time window start = %.4f, end = %.4f " %(args.start, args.end))
    if (args.end - args.start)/60/60/24 >=21:
        print ("Error: time window is too long.")
        usage()
        sys.exit(3)
        
    #es_query = { "query": { "bool": { "must": [ ] } } }
    #term = {"term": {"evtType": "evt_alert"}}
    #es_query["query"]["bool"]["must"].append(term)

    # for device
    es_query = { "query": { "filtered": { "query":{"query_string":{"query":"*"}}, "filter": { "bool": { "must": [ ] } } } } }

    if (args.anything) :
        es_query["query"]["filtered"]["query"]["query_string"]["query"] = "\"" + args.anything + "\""

    if( deviceid!="00:00:00:00:00:00" ) :
        term = { "fquery": { "query": { "query_string": { "query":"iotDevid"":(\""+deviceid+"\")" } } } }
        es_query["query"]["filtered"]["filter"]["bool"]["must"].append(term)
        
    if tenantId != "ALL":
        term = { "fquery": { "query": { "query_string": { "query":"tenantid"":(\""+tenantId+"\")" } } } }
        es_query["query"]["filtered"]["filter"]["bool"]["must"].append(term)

    if alerttype != "ALL":
        term = { "fquery": { "query": { "query_string": { "query":"evtType"":(\""+alerttype+"\")" } } } }
        es_query["query"]["filtered"]["filter"]["bool"]["must"].append(term)
        
    term = { "range": { "@timestamp": { "from": args.start*1000, "to": args.end*1000 } } }
    es_query["query"]["filtered"]["filter"]["bool"]["must"].append(term)
                    

    indices = ""

    dateBeg = datetime.fromtimestamp(args.start).date()
    dateEnd = datetime.fromtimestamp(args.end).date()
    dateDelta = dateEnd - dateBeg

    for n in range( dateDelta.days+1 ): 
        date_str = '.'.join(str(dateBeg + timedelta(days=(n))).split('-'))
        indices += 'logstash-' + date_str + ","
    indices = indices[:len(indices)-1]
    raw = ""

    result_set={}

    # with open(os.environ['ZCENVS']+'/'+'zc-envs.json', 'r') as stream:
        # conf = json.loads(stream.read())
    conf = {}
    conf["elasticsearch"] = esConfig
    es = Elasticsearch(conf["elasticsearch"], sniff_on_start=False)
   
    print ("debug....  indices = " + indices)
    print ("debug .... es_query =  " +  json.dumps(es_query) )
    rs = es.search(index=indices, body=json.dumps(es_query).replace("'", '"'), search_type="scan", scroll="3m", request_timeout=30)
    #base_url = "http://" + conf["elasticsearch"][0]["host"] + ":" + str(80) + "/" + conf["elasticsearch"][0]["url_prefix"]
    base_url = "https://" + conf["elasticsearch"][0]["host"] + ":" + str(conf["elasticsearch"][0]["port"]) + "/" + conf["elasticsearch"][0]["url_prefix"]

    print ("debug .... base_url = " + base_url)

    raw_results = []
    scroll_context = rs['_scroll_id']
    total_count = 0
    # run until there's no more results

    current_results_size = 1
    current_time = time.time()
    while current_results_size > 0:
        payload = {"scroll_id": scroll_context, 'scroll': '2m'}
        r = requests.get(base_url + "/_search/scroll", params=payload, verify=False)

        #print "----- debug -----";
        # print (str(r.text))
        rTextUnicode = r.text.encode('utf-8')

        temp_scroll_result = json.loads(rTextUnicode)
        current_results_size = len(temp_scroll_result['hits']['hits'])
        scroll_context = temp_scroll_result["_scroll_id"]

        raw_results.append(temp_scroll_result['hits']['hits'])
        total_count += current_results_size
        #print(str(total_count) + " hits")
        #print(str(time.time() - current_time) + "seconds")
    
    
        for query_result in raw_results:
            for alert in query_result:
                try:
                    outFP.write( json.dumps(alert, sort_keys=True) )
                    outFP.write("\n")
                except:
                    sigrev = 0

        raw_results = []

    outFP.close()
