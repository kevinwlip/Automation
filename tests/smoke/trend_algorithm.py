import json
import subprocess
import pdb
import time
from datetime import datetime
import os, sys
import pytest
from elasticsearch import Elasticsearch

try:
    zbathome = os.environ['ZBAT_HOME']
except:
    print 'Test cannot run.  Please export ZBAT_HOME.'
    sys.exit()

if zbathome+'lib' not in sys.path:
    sys.path.append(zbathome+'lib')

from cron.trend_analysis import main



future_weight = 0.2
error_margin = 0.25
PAGINATION = 100
error_margin_alert = 0.4

es = Elasticsearch("192.168.20.67:9200", request_timeout=60, max_retries=2, retry_on_timeout=True)

office_only_list = ("waubonsee", "brainerdbaptist")

@pytest.fixture(scope="session", autouse=True)
def do_something():
    main()



@pytest.mark.parametrize("tenant", 
    [
    #"bmcc", 
    "baycare", 
    "brainerdbaptist", 
    "unitedregional", 
    "waubonsee", 
    "allinahealth",
    "pinnaclehealth",
    "staging-unitedregional"
    ])
def test_Algorithm_Alert(tenant):
    dominance = True
    ten_list = []

    #Command to fetch the alerts from ES
    res = es.search(index="tenant_trend_analysis2", body={"size":PAGINATION, "query" : {"bool" : { "must" : [ {"match" :{"tenant" : tenant}}, {"exists" :{"field" : "alert_total"}}  ] } }, "sort": {"timestamp" : {"order" : "asc"}} })
    worklist = res['hits']['hits']
    print worklist

    for hit in worklist:
        temp = hit["_source"]["tenant"]
        if temp == tenant:
            ten_list.append(hit)
    rolling_average = 0
    for hit in ten_list:
        master_time = datetime.utcnow()
        try:
            nume = hit["_source"]["alert_total"]
        except:
            print "End of existing data set"
            break
        if rolling_average == 0: #sometimes zero alerts will fail the test

            rolling_average = nume
        else:
            if abs(nume - rolling_average)/rolling_average > error_margin_alert:
                #
                if ( master_time- datetime.strptime(hit["_source"]["timestamp"], '%Y-%m-%dT%H:%M:%S.%f') ).total_seconds()  < 6 * 3600:
                    print hit
                    print ("Error: Drastic change exceeding tolerance detected")
                    print ("Error on value: " + str(nume) + " Rolling average: " + str(rolling_average) + "On Total Alerts on date " + hit["_source"]["timestamp"])
                    dominance = False
            else:
                pass
                #print ("Pass: value: " + str(nume) + " Rolling average: " + str(rolling_average))
            rolling_average = (1-future_weight) * rolling_average + future_weight * nume
        if rolling_average < 1:
            print "Error: Rolling average has become too low"
            print ("Error on value: " + str(nume) + " Rolling average: " + str(rolling_average) + "On Total Alerts on date " + hit["_source"]["timestamp"])
            dominance = False
            break
    rolling_average = 0
    for hit in ten_list:

        master_time = datetime.utcnow()
        try:
            nume = hit["_source"]["alert_internalreview"]
        except:
            print "End of existing data set"
            break
        if rolling_average == 0:
            rolling_average = nume
        else:
            if abs(nume - rolling_average)/rolling_average > error_margin_alert:
                #
                if ( master_time- datetime.strptime(hit["_source"]["timestamp"], '%Y-%m-%dT%H:%M:%S.%f') ).total_seconds()  < 6 * 3600:
                    print hit
                    print ("Error: Drastic change exceeding tolerance detected")
                    print ("Error on value: " + str(nume) + " Rolling average: " + str(rolling_average) + "On Total Alerts on date " + hit["_source"]["timestamp"])
                    dominance = False
            else:
                pass
                #print ("Pass: value: " + str(nume) + " Rolling average: " + str(rolling_average))
            rolling_average = (1-future_weight) * rolling_average + future_weight * nume
        if rolling_average < 1:
            print "Error: Rolling average has become too low"
            print ("Error on value: " + str(nume) + " Rolling average: " + str(rolling_average) + "On Total Alerts on date " + hit["_source"]["timestamp"])
            dominance = False
            break
    assert dominance

@pytest.mark.parametrize("tenant", 
    [
    #"bmcc", 
    "baycare", 
    "brainerdbaptist", 
    "unitedregional", 
    "waubonsee", 
    "beaconhealthsystem",
    "allinahealth",
    "staging-unitedregional",
    "pinnaclehealth",
    ])

@pytest.mark.parametrize("trending_element", ["device_all_count","device_iot_medical_count","device_iot_all_count","category_count","profile_count","device_iot_office_count"])

@pytest.mark.parametrize("timerange", ["1D", "1W"])
def test_Algorithm(tenant, trending_element, timerange):
    if (trending_element == 'device_iot_medical_count' and tenant in office_only_list) or (trending_element == 'device_iot_office_count' and tenant not in office_only_list):
        pytest.skip("Invaid Parameter combination: Facility mismatch")
    dominance = True
    site_list = {}

    res = es.search(index="tenant_trend_analysis2", body={"size":PAGINATION*10, "query" : {"bool" : { "must" : [ {"match" :{"tenant" : tenant}}, {"match" :{"timerange" : timerange}}  ] } }, "sort": {"timestamp" : {"order" : "asc"}} })
    
    #worklist = sorted(res['hits']['hits'], key = lambda x: x["_source"]["timestamp"])
    worklist = res['hits']['hits']
    for hit in worklist:
        temp = hit["_source"]["site_id"]
        if temp not in site_list:
            site_list[temp] = []
        site_list[temp].append(hit)

    for site in site_list:
        rolling_average = 0
        for hit in site_list[site]:
            master_time = datetime.utcnow()
            try:
                nume = hit["_source"][trending_element]
            except:
                print "End of existing data set"
                break
            if rolling_average == 0:
                rolling_average = nume
            else:
                if abs(nume - rolling_average)/rolling_average > error_margin:
                    #
                    if ( master_time- datetime.strptime(hit["_source"]["timestamp"], '%Y-%m-%dT%H:%M:%S.%f') ).total_seconds()  < 6 * 3600:
                        print hit
                        print ("Error: value: " + str(nume) + " Rolling average: " + str(rolling_average))
                        dominance = False
                else:
                    pass
                    #print ("Pass: value: " + str(nume) + " Rolling average: " + str(rolling_average))
            rolling_average = (1-future_weight) * rolling_average + future_weight * nume
            if rolling_average < 1:
                print "Error: Rolling average has become too low"
                dominance = False
                break
    assert dominance


