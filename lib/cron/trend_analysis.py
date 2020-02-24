
import json
import subprocess
import pdb
import time
import datetime
import os
from elasticsearch import Elasticsearch, client
es = Elasticsearch("192.168.20.67:9200")

es_index = client.IndicesClient(es)
tenants = ["bmcc", "baycare", "brainerdbaptist", "unitedregional", "waubonsee", "beaconhealthsystem", "staging-unitedregional"]

timeranges = ["1D","1W"]

Bearer = os.environ["ZBAT_PROD_API_TOKEN"]

master_time = datetime.datetime.utcnow().strftime("%Y/%m/%d %H:%M")
mas_time = datetime.datetime.utcnow()


mapping = '''
{
   "settings" : {
       "number_of_shards" : 1
   },
   "mappings" : {
       "trend_analysis" : {
           "properties" : {
               "timestamp" : {"type" : "date"},
               "category_count":    { "type": "integer"  },
               "profile_count":    { "type": "integer"  },
               "device_all_count":    { "type": "integer"  },
               "device_iot_all_count":    { "type": "integer"  },
               "device_iot_medical_count":    { "type": "integer"  },
               "interval":    { "type": "keyword"  },
               "site_id":     { "type": "keyword"  },
               "tenant":      { "type": "keyword" },  
               "timerange":      { "type": "keyword" }

           }
       }
   }
}
'''

up_mapping = '''
{
       "trend_analysis" : {
           "properties" : {
               "timestamp" : {"type" : "date"},
               "category_count":    { "type": "integer"  },
               "profile_count":    { "type": "integer"  },
               "device_all_count":    { "type": "integer"  },
               "device_iot_all_count":    { "type": "integer"  },
               "device_iot_medical_count":    { "type": "integer"  },
               "interval":    { "type": "keyword"  },
               "site_id":     { "type": "keyword"  },
               "tenant":      { "type": "keyword" },  
               "timerange":      { "type": "keyword" }

           }
       }
   
}
'''
try:
    es_index.create(index="tenant_trend_analysis2", body=mapping)
except:
    es_index.put_mapping(index="tenant_trend_analysis2", doc_type="trend_analysis", body=up_mapping)



def main():
    global Bearer
    for tenant in tenants:
        ts = datetime.datetime.utcnow()
        #Alert Count
        delta = datetime.timedelta(days=7)
        tss = ts - delta
        st = tss.strftime('%Y-%m-%dT%H:%MZ')

        delta = datetime.timedelta(days=30)
        tss = ts - delta
        st_month = tss.strftime('%Y-%m-%dT%H:%MZ')

        if "staging" in tenant:
            Bearer = os.environ["ZBAT_STAGING_API_TOKEN"]

        if "-" in tenant:
            tenner = tenant.split("-")
            tenant_url = tenner[0]
            tenant_ten = tenner[1]
        else:
            tenant_url = tenant
            tenant_ten = tenant
        #Gets both Internal and Total alert counts
        cmd = "curl 'https://"+tenant_url+".zingbox.com/v0.3/api/alert/stat?review=true&etime=now&stime="+st_month+"&tenantid="+tenant_ten+"&type=policy_alert' -H 'Pragma: no-cache' -H 'Accept-Encoding: gzip, deflate, br' -H 'Accept-Language: en-US,en;q=0.9,zh-CN;q=0.8,zh;q=0.7' -H 'User-Agent: Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Ubuntu Chromium/71.0.3578.98 Chrome/71.0.3578.98 Safari/537.36' -H 'Accept: application/json, text/plain, */*' -H 'Referer: https://testing.zingbox.com/policiesalerts/alerts?interval=all' -H 'Authorization: "+Bearer+"' -H 'Connection: keep-alive' -H 'Cache-Control: no-cache' --compressed"
        #print cmd
        output_json = {}
        output_json["tenant"] = tenant
        output_json["timestamp"] = mas_time
        try:
          temp_json = json.loads( subprocess.check_output(cmd, shell=True) )
          output_json["alert_total"] = temp_json["stat"]["total"]
        except:
          print(cmd)
          output_json["alert_total"] = 0
          print("Error: invalid JSON.")
          print(temp_json)
          pass

        cmd = "curl 'https://"+tenant_url+".zingbox.com/v0.3/api/alert/stat?review=true&etime=now&stime="+st+"&tenantid="+tenant_ten+"&type=policy_alert' -H 'Pragma: no-cache' -H 'Accept-Encoding: gzip, deflate, br' -H 'Accept-Language: en-US,en;q=0.9,zh-CN;q=0.8,zh;q=0.7' -H 'User-Agent: Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Ubuntu Chromium/71.0.3578.98 Chrome/71.0.3578.98 Safari/537.36' -H 'Accept: application/json, text/plain, */*' -H 'Referer: https://testing.zingbox.com/policiesalerts/alerts?interval=all' -H 'Authorization: "+Bearer+"' -H 'Connection: keep-alive' -H 'Cache-Control: no-cache' --compressed"

        
        try:
          temp_json = json.loads( subprocess.check_output(cmd, shell=True) )
          output_json["alert_internalreview"] = temp_json["stat"]["active"]
        except:
          try:
            output_json["alert_internalreview"] = temp_json["stat"]["total"]
          except:
            print(cmd)
            print("Error: invalid JSON.")
            print(temp_json)
            pass

        res = es.index(index="tenant_trend_analysis2", doc_type="trend_analysis", id=str((ts - datetime.datetime(1970,1,1)).total_seconds()) + "_" + tenant + "_alerts", body=output_json, request_timeout=30)   
        print(output_json)

        for timerange in timeranges:
            ts = datetime.datetime.utcnow()
            output_json = {}
            output_json["tenant"] = tenant
            output_json["timestamp"] = mas_time
            output_json["timerange"] = timerange
            #if timerange == "2H":
                #output_json["interval"] = "minute"
                #delta = datetime.timedelta(hours=2)
                #tss = ts - delta
                #st = tss.strftime('%Y-%m-%dT%H:%MZ')
            if timerange == "1D":
                output_json["interval"] = "hour"
                delta = datetime.timedelta(days=1)
                tss = ts - delta
                st = tss.strftime('%Y-%m-%dT%H:%MZ')
            elif timerange == "1W":
                output_json["interval"] = "day"
                delta = datetime.timedelta(days=6)
                tss = ts - delta
                st = tss.strftime('%Y-%m-%dT%H:%MZ')
            #elif timerange == "1M":
                #output_json["interval"] = "day"
                #delta = datetime.timedelta(days=30)
               # tss = ts - delta
               # st = tss.strftime('%Y-%m-%dT%H:%MZ')
            #elif timerange == "1Y":
              #  output_json["interval"] = "day"
              #  delta = datetime.timedelta(days=365)
              #  tss = ts - delta
               # st = tss.strftime('%Y-%m-%dT%H:%MZ')
            #elif timerange == "ALL":
                #output_json["interval"] = "day"
                #st = -1

            batcmd= "curl 'https://"+tenant_url+".zingbox.com/v0.3/api/iotprofile/stats?etime=now&filter_monitored=yes&interval="+ output_json["interval"] + "&outputtype=site&stime="+ st +"&tenantid="+tenant_ten+"' -H 'Pragma: no-cache' -H 'Accept-Encoding: gzip, deflate, br' -H 'Accept-Language: en-US,en;q=0.9' -H 'User-Agent: Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.132 Safari/537.36' -H 'Accept: application/json, text/plain, */*' -H 'Authorization: " + Bearer + "' -H 'Connection: keep-alive' -H 'Cache-Control: no-cache' --compressed"
            temp = subprocess.check_output(batcmd, shell=True)
            input_json = json.loads( temp)


            for x in input_json["list"]:
                ts = datetime.datetime.utcnow()
                site_id = x["id"]
                _devices = 0
                _category_count = 0
                _iot_total_count = 0
                _iot_medical_count = 0
                _iot_office_count = 0
                for y in x["risk"]:
                    _devices += y["devices"]
                output_json["site_id"] = site_id
                output_json["device_all_count"] = _devices

                cmd = "curl 'https://"+tenant_url+".zingbox.com/v0.3/api/iotprofile/stats?etime=now&filter_monitored=yes&interval="+ output_json["interval"] + "&outputtype=category&siteids="+site_id+"&stime="+ st +"&tenantid="+tenant_ten+"' -H 'Authorization: " + Bearer + "' -H 'Accept-Encoding: gzip, deflate, br' -H 'Accept-Language: en-US,en;q=0.9,zh-CN;q=0.8,zh;q=0.7' -H 'User-Agent: Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Ubuntu Chromium/64.0.3282.167 Chrome/64.0.3282.167 Safari/537.36' -H 'Accept: application/json, text/plain, */*' -H 'Connection: keep-alive' --compressed"
                try:
                    temp_json = json.loads( subprocess.check_output(cmd, shell=True) )

                except:
                    print(cmd)
                    print("Error: invalid JSON.")
                    pass

                for item in temp_json['list']:
                    _category_count += 1


                output_json["category_count"] = _category_count



                cmd = "curl 'https://"+tenant_url+".zingbox.com/v0.3/api/iotprofile/stats?etime=now&filter_monitored=yes&filter_profile_type=IoT&interval=" + output_json["interval"] + "&outputtype=vertical&siteids="+site_id+"&stime="+ st +"&tenantid="+tenant_ten+"' -H 'Authorization: " + Bearer + "' -H 'Accept-Encoding: gzip, deflate, br' -H 'Accept-Language: en-US,en;q=0.9,zh-CN;q=0.8,zh;q=0.7' -H 'User-Agent: Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Ubuntu Chromium/64.0.3282.167 Chrome/64.0.3282.167 Safari/537.36' -H 'Accept: application/json, text/plain, */*' -H 'Connection: keep-alive' --compressed"
                try:
                    temp_json = json.loads( subprocess.check_output(cmd, shell=True) )
                except:
                    print(cmd)
                    print("Error: invalid JSON.")
                    pass


                for item in temp_json["list"]:
                    count = 0
                    for it in item["risk"]:
                        count += it["devices"]
                    if item["id"] == "Medical":
                        _iot_medical_count += count
                    _iot_total_count += count


                cmd = "curl 'https://"+tenant_url+".zingbox.com/v0.3/api/iotprofile/stats?etime=now&filter_monitored=yes&filter_profile_type=IoT&filter_profile_vertical=Office&interval=" + output_json["interval"] + "&outputtype=vertical&siteids="+site_id+"&stime="+ st +"&tenantid="+tenant_ten+"' -H 'Authorization: " + Bearer + "' -H 'Accept-Encoding: gzip, deflate, br' -H 'Accept-Language: en-US,en;q=0.9,zh-CN;q=0.8,zh;q=0.7' -H 'User-Agent: Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Ubuntu Chromium/64.0.3282.167 Chrome/64.0.3282.167 Safari/537.36' -H 'Accept: application/json, text/plain, */*' -H 'Connection: keep-alive' --compressed"

                try:
                    temp_json = json.loads( subprocess.check_output(cmd, shell=True) )
                except:
                    print(cmd)
                    print("Error: invalid JSON.")
                    pass

                for item in temp_json["list"]:
                    count = 0
                    for it in item["risk"]:
                        count += it["devices"]
                        _iot_office_count += count


                output_json["device_iot_office_count"] = _iot_office_count
                output_json["device_iot_medical_count"] = _iot_medical_count
                output_json["device_iot_all_count"] = _iot_total_count

                cmd = "curl 'https://"+tenant_url+".zingbox.com/v0.3/api/iotprofile/stats?etime=now&filter_monitored=yes&interval=" + output_json["interval"] + "&outputtype=profile&siteids="+site_id+"&stime="+ st +"&tenantid="+tenant_ten+"' -H 'Authorization: " + Bearer + "' -H 'Accept-Encoding: gzip, deflate, br' -H 'Accept-Language: en-US,en;q=0.9,zh-CN;q=0.8,zh;q=0.7' -H 'Accept: application/json, text/plain, */*' -H 'Referer: https://"+tenant+".zingbox.com/?interval=oneday&filter_monitored=yes&direction=all' -H 'Connection: keep-alive' --compressed"
                output_json["profile_count"] = 0
                temp_json = json.loads(subprocess.check_output(cmd, shell=True) )

                for item in temp_json["list"]:
                    output_json["profile_count"] += 1

                res = es.index(index="tenant_trend_analysis2", doc_type="trend_analysis", id=str((ts - datetime.datetime(1970,1,1)).total_seconds()) + "_" + tenant + "_" + site_id, body=output_json, request_timeout=30) 
                
                #print output_json


if __name__== "__main__":
    main()


"""
curl -XPUT '192.168.20.67:9200/tenant_trend_analysis?pretty' -H 'Content-Type: application/json' -d'
{
   "settings" : {
       "number_of_shards" : 1
   },
   "mappings" : {
       "trend_analysis" : {
           "properties" : {
               "category_count":    { "type": "integer"  },
               "profile_count":    { "type": "integer"  },
               "device_all_count":    { "type": "integer"  },
               "device_iot_all_count":    { "type": "integer"  },
               "device_iot_medical_count":    { "type": "integer"  },
               "interval":    { "type": "text"  },
               "site_id":     { "type": "text"  },
               "tenant":      { "type": "text" },  
               "timerange":      { "type": "text" },

           }
       }
   }
}
'



               "timestamp":  {
                 "type":   "date",
                 "format": "strict_date_optional_time||epoch_millis"
               }
"""

