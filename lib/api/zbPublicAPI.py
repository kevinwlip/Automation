import json
import subprocess
import pdb
import time
import datetime
import os
import csv, random
import requests
import sys


'''
curl 'https://staging.zingbox.com/v0.3/api/iotdevicereport/createreport?etime=now&filter_monitored=yes&interval=hour&stime=2018-10-11T21:58Z&tenantid=soho' -H 'Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJzdWIiOiI1YjY4ZTUyYmQ4OWY2MTEwMDBkM2ZiMzAiLCJlbWFpbCI6ImthaXlpLmh1YW5nQHppbmdib3guY29tIiwianRpIjoiYlhXNHVteXhmSiIsInN5c2FkbWluIjpmYWxzZSwiaXNsb2NrZWQiOmZhbHNlLCJ3YWxrdGhyb3VnaCI6bnVsbCwic2NvcGUiOnsic29obyI6eyJvd25lciI6dHJ1ZSwiYWRtaW4iOnRydWUsInNpdGVzIjpbImFsbCJdfSwiYmF5Y2FyZSI6eyJvd25lciI6ZmFsc2UsImFkbWluIjp0cnVlLCJzaXRlcyI6WyJhbGwiXX19LCJyaWQiOm51bGwsInVzZXJFeHBpcmF0aW9uRGF0ZSI6bnVsbCwibGFzdGxvZ2luIjp7ImxvY2F0aW9uIjp7InJhbmdlIjpbODU1MDcwOTc2LDg1NTA3MTIzMV0sImNvdW50cnkiOiJVUyIsInJlZ2lvbiI6IkNBIiwiY2l0eSI6IlNhbiBKb3NlIiwibGwiOlszNy4zNDIyLC0xMjEuODgzM10sIm1ldHJvIjo4MDd9LCJ0aW1lc3RhbXAiOiIyMDE4LTEwLTEyVDIxOjI4OjE5LjYxMloiLCJpcCI6IjUwLjI0Ny44OS4yMDEifSwidXNlcnBpYyI6bnVsbCwiZGVmYXVsdHRlbmFudCI6InNvaG8iLCJvcmdhbml6YXRpb24iOm51bGwsImluZHVzdHJ5IjpudWxsLCJqb2J0aXRsZSI6bnVsbCwicGhvbmUiOiI0MzI0MjM0MzIiLCJmaXJzdG5hbWUiOiJLYWl5aSIsImxhc3RuYW1lIjoiSHVhbmciLCJhZGRyZXNzIjp7ImNvdW50cnkiOiJVUyIsInN0cmVldCI6ImVbZHNwZjBwW29zYSIsImNpdHkiOiJGcmVtb250Iiwic3RhdGUiOiJDQSJ9LCJ0aW1lem9uZSI6IkNhbmFkYS9QYWNpZmljIiwiaWRsZVRpbWVvdXQiOm51bGwsImlzVGVybUFjY2VwdGVkIjpudWxsLCJjZWxscGhvbmUiOm51bGwsImFsZXJ0Tm90aWZ5UHJlZiI6bnVsbCwiaW50bGNvZGUiOm51bGwsIkVVTEFBY2NlcHRlZCI6dHJ1ZSwiRVVMQUFjY2VwdFRpbWVzdGFtcCI6IjIwMTgtMDgtMDdUMDA6MTc6NDcuMjc4WiIsIkZJTkFMRVVMQSI6bnVsbCwiRklOQUxFVUxBVGltZXN0YW1wIjpudWxsLCJtc3NwIjpudWxsLCJkaXN0cmlidXRvciI6bnVsbCwicmVzZWxsZXIiOm51bGwsImRpc2FibGVBbGVydFNvdW5kIjpudWxsLCJ0d29GQSI6bnVsbCwiYWNjZXNzS2V5cyI6IkNyZWF0ZWQiLCJjb21wYW55cGljIjpudWxsLCJjaGFuZ2VQYXNzd29yZFRpbWUiOjE1MzM2MDEwNjcsImZ1bGxuYW1lIjoiS2FpeWkgSHVhbmciLCJuYW1lIjoiS2FpeWkgSHVhbmciLCJpYXQiOjE1MzkzODE1MjksImV4cCI6MTU0MDI0NTUyOSwiaXNzIjoiemluZ2JveCJ9.ZmrkxIGY5KEQ4cyChUCCGgw2ZH8vUuSktGHJFiWkEnc' -H 'Accept-Encoding: gzip, deflate, br' -H 'Accept-Language: en-US,en;q=0.9,zh-CN;q=0.8,zh;q=0.7' -H 'User-Agent: Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Ubuntu Chromium/69.0.3497.81 Chrome/69.0.3497.81 Safari/537.36' -H 'Accept: application/json, text/plain, */*' -H 'Referer: https://staging.zingbox.com/monitor/inventory?page=1&pagelength=25' -H 'Cookie: _ga=GA1.2.2076885826.1533057660; slaask-token-115c13d1f8cff0b97360c2f06bf7cef7=iabsk6kdm6qp5s126lwlwhys9qj75m3bc1inkn9ga0t8h; route=1a479735e1aa2c96dd659731c7db982b; em_cdn_uid=t%3D1533329563049%26u%3D899912ab48994a5289d4f69183839b58; _ga=GA1.3.2076885826.1533057660; _pk_id.241.700d=c962eb765d737bf5.1534789410.9.1536856633.1536856484.; _gid=GA1.2.407694320.1539016600; _gid=GA1.3.407694320.1539016600; _pk_ses.91.700d=*; _pk_id.91.700d=c962eb765d737bf5.1533316617.27.1539380348.1539376157.; _gat_gtag_UA_113137765_1=1; _pk_ses..700d=*' -H 'Connection: keep-alive' --compressed
'''
master_time = datetime.datetime.utcnow().strftime("%Y/%m/%d %H:%M")
purebool = True
cand_dict = { 
    "soho" : {"X-Key-Id": "1862443210:f7c60984ca635d11f7a7cfb6b481ddee4a38a3d4d97c873de1368f4807cfb914", 'X-Access-Key': "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJzdWIiOiI1OWU2YmU1OGMyY2Q1N2MzNDUwMzVjNGQiLCJlbWFpbCI6ImFkbWluQHNvaG8uY29tIiwianRpIjoieEJkOVRTR2hodyIsInNjb3BlIjp7InNvaG8iOnsiZGVmYXVsdCI6dHJ1ZSwiYWRtaW4iOnRydWUsIm93bmVyIjp0cnVlfX0sInRlbmFudGlkIjoic29obyIsInVybFBhdHRlcm4iOiIvcHViL3Y0LjAvIiwiaWF0IjoxNTQ3MDgzMjEwLCJleHAiOjE4NjI0NDMyMTAsImlzcyI6Inppbmdib3gifQ.zT6wVpUR3AA22CBkXs8-Onpz4rLeU6Va5je3IlBJWuU"},
    "baycare" : {"X-Key-Id":"1853803273:9387c21a69668cb821461875d60dd29e571ec3297e9ae656a6e6b3362f6c1a62", 'X-Access-Key':"eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJzdWIiOiI1YjY4ZTUyYmQ4OWY2MTEwMDBkM2ZiMzAiLCJlbWFpbCI6ImthaXlpLmh1YW5nQHppbmdib3guY29tIiwianRpIjoiXzVBcnpKNW5mNiIsInN5c2FkbWluIjpmYWxzZSwiaXNsb2NrZWQiOmZhbHNlLCJ3YWxrdGhyb3VnaCI6bnVsbCwic2NvcGUiOnsiYmF5Y2FyZSI6eyJvd25lciI6ZmFsc2UsImFkbWluIjp0cnVlLCJzaXRlcyI6WyJhbGwiXX19LCJyaWQiOm51bGwsInVzZXJFeHBpcmF0aW9uRGF0ZSI6bnVsbCwibGFzdGxvZ2luIjp7ImxvY2F0aW9uIjp7InJhbmdlIjpbODU1MDcwOTc2LDg1NTA3MTIzMV0sImNvdW50cnkiOiJVUyIsInJlZ2lvbiI6IkNBIiwiY2l0eSI6IlNhbiBKb3NlIiwibGwiOlszNy4zNDIyLC0xMjEuODgzM10sIm1ldHJvIjo4MDd9LCJ0aW1lc3RhbXAiOiIyMDE4LTEwLTAyVDAxOjIxOjAxLjg3OVoiLCJpcCI6IjUwLjI0Ny44OS4yMDEifSwidXNlcnBpYyI6bnVsbCwiZGVmYXVsdHRlbmFudCI6InNvaG8iLCJvcmdhbml6YXRpb24iOm51bGwsImluZHVzdHJ5IjpudWxsLCJqb2J0aXRsZSI6bnVsbCwicGhvbmUiOiI0MzI0MjM0MzIiLCJmaXJzdG5hbWUiOiJLYWl5aSIsImxhc3RuYW1lIjoiSHVhbmciLCJhZGRyZXNzIjp7ImNvdW50cnkiOiJVUyIsInN0cmVldCI6ImVbZHNwZjBwW29zYSIsImNpdHkiOiJGcmVtb250Iiwic3RhdGUiOiJDQSJ9LCJ0aW1lem9uZSI6IkNhbmFkYS9QYWNpZmljIiwiaWRsZVRpbWVvdXQiOm51bGwsImlzVGVybUFjY2VwdGVkIjpudWxsLCJjZWxscGhvbmUiOm51bGwsImFsZXJ0Tm90aWZ5UHJlZiI6bnVsbCwiaW50bGNvZGUiOm51bGwsIkVVTEFBY2NlcHRlZCI6dHJ1ZSwiRVVMQUFjY2VwdFRpbWVzdGFtcCI6IjIwMTgtMDgtMDdUMDA6MTc6NDcuMjc4WiIsIkZJTkFMRVVMQSI6bnVsbCwiRklOQUxFVUxBVGltZXN0YW1wIjpudWxsLCJtc3NwIjpudWxsLCJkaXN0cmlidXRvciI6bnVsbCwicmVzZWxsZXIiOm51bGwsImRpc2FibGVBbGVydFNvdW5kIjpudWxsLCJ0d29GQSI6bnVsbCwiYWNjZXNzS2V5cyI6IkNyZWF0ZWQiLCJjb21wYW55cGljIjpudWxsLCJjaGFuZ2VQYXNzd29yZFRpbWUiOjE1MzM2MDEwNjcsImZ1bGxuYW1lIjoiS2FpeWkgSHVhbmciLCJuYW1lIjoiS2FpeWkgSHVhbmciLCJ0ZW5hbnRpZCI6ImJheWNhcmUiLCJpYXQiOjE1Mzg0NDMyNzMsImV4cCI6MTg1MzgwMzI3MywiaXNzIjoiemluZ2JveCJ9.xN4N5E-dqTTtwRtuqYdVa3ZsieBdTAU0rh_u6IXL-cs"}

}

class PublicAPI:
    def __init__(self):
        self.permaCSV = None

    def get_device_inventory_csv(self,tenantid):
        if self.permaCSV == None:
            dankheader = {}
            #dankheader = cand_dict[tenantid]
            dankheader["Authorization"] = os.environ["ZBAT_STAGING_API_TOKEN"]
            for n in range(4):
                start_creation = requests.get("https://staging.zingbox.com/v0.3/api/iotdevicereport/createreport?etime=now&filter_monitored=yes&interval=day&stime=-1&tenantid=" + tenantid, headers=dankheader)
                print(("https://staging.zingbox.com/v0.3/api/iotdevicereport/createreport?etime=now&filter_monitored=yes&interval=day&stime=-1&tenantid=" + tenantid))
                returned = start_creation.json()
                fileKey = returned["file"]["fileKey"]
                print(fileKey)
                if fileKey != None:
                    break
            if returned["file"]["status"] == "NOTEXIST":
                for n in range(4):
                    file_status = requests.get("https://staging.zingbox.com/v0.3/api/iotdevicereport/checkreport?bucket=zreports&filekey=" +fileKey+"&tenantid=" + tenantid, headers=dankheader)
                    if file_status.json()["file"]["status"] == "EXIST":
                        break
            response = requests.get("https://staging.zingbox.com/v0.3/api/iotdevicereport/download?bucket=zreports&filekey="+fileKey+"&tenantid=" + tenantid, headers=dankheader)
            self.permaCSV = csv.reader(response.text.split("\n"), delimiter=',', quotechar='\"')
        return self.permaCSV


    def verifyDeviceInventoryAPI(self,tenantid):
        no_diff = True
        def sortfunc(e):
            return e["deviceid"]
        def sortfunc2(e):
            return e["mac_address"]
        floodreader = self.get_device_inventory_csv(tenantid)
        permarow = []
        firstrow = True
        megajson=[]
        for row in floodreader:
            appendex = {}
            if firstrow:
                permarow = row
                firstrow=False
                for  i,ele in enumerate(permarow):
                    permarow[i] = ele.lower().replace(' ', '_')
                continue
            for index, element in enumerate(row):
                if element != '':
                    appendex[permarow[index]] = element
            megajson.append(appendex)
        meme = "https://staging.zingbox.com/pub/v4.0/device/list?customerid=" + tenantid
        print(meme)
        print(cand_dict[tenantid])
        floodcaller = requests.get(meme, headers=cand_dict[tenantid])
        print(floodcaller.json())
        gigajson = floodcaller.json()["devices"]
        gigajson.sort(key=sortfunc)
        megajson.sort(key=sortfunc2)
        x = iter(megajson)
        y = iter(gigajson)
        for ele in megajson:
            name = ele["mac_address"]
            testy = next(y)
            if(testy["deviceid"] == name):
                if testy["hostname"] != ele["hostname"]:
                    print((ele, testy))
                    no_diff = False
                continue
        return no_diff

    def verifyDeviceAPI(self,tenantid,sample):
        testCSV = self.get_device_inventory_csv(tenantid)
        no_diff = True
        firstrow = True
        megajson=[]
        for row in testCSV:
            appendex = {}
            if firstrow:
                permarow = row
                firstrow=False
                for  i,ele in enumerate(permarow):
                    permarow[i] = ele.lower().replace(' ', '_')
                continue
            for index, element in enumerate(row):
                if element != '':
                    appendex[permarow[index]] = element
            megajson.append(appendex)
        for x in range(sample):
            y = random.randint(0,len(megajson))
            testy = megajson[y]
            meme = "https://staging.zingbox.com/pub/v4.0/device?customerid=" + tenantid + "&deviceid=" + testy["mac_address"]
            caller = requests.get(meme, headers=cand_dict[tenantid])
            api_res = caller.json()
            print(api_res)
            print(testy)

            for entry in testy:
                if entry in api_res and entry == 'status':
                    no_diff = False
                    print(testy)
                    break
                if entry in api_res and entry != 'last_activity':
                    if type(api_res[entry]) == int:
                        tester = int(testy[entry])
                    else:
                        tester = testy[entry]
                    if tester != api_res[entry]:
                        print(entry +" : " + str(testy[entry]) + " VS " + entry + " : " + str(api_res[entry]))
                        print("oh no")
                        no_diff = False
        return no_diff

    def verifyDeviceIP(self,tenantid,sample):
        testCSV = self.get_device_inventory_csv(tenantid)
        firstrow = True
        no_diff = True
        megajson=[]
        for row in testCSV:
            appendex = {}
            if firstrow:
                permarow = row
                firstrow=False
                for  i,ele in enumerate(permarow):
                    permarow[i] = ele.lower().replace(' ', '_')
                continue
            for index, element in enumerate(row):
                if element != '':
                    appendex[permarow[index]] = element
            megajson.append(appendex)
        for x in range(sample):
            y = random.randint(0,len(megajson))
            testy = megajson[y]
            meme = "https://staging.zingbox.com/pub/v4.0/device?customerid=" + tenantid + "&deviceip=" + testy["ip_address"]
            caller = requests.get(meme, headers=cand_dict[tenantid])
            api_res = caller.json()

            for entry in testy:
                if entry in api_res and entry == 'status':
                    no_diff = False
                    print(testy)
                    break
                if entry in api_res and entry != 'last_activity':
                    if type(api_res[entry]) == int:
                        tester = int(testy[entry])
                    else:
                        tester = testy[entry]
                    if tester != api_res[entry]:
                        print(entry +" : " + str(testy[entry]) + " VS " + entry + " : " + str(api_res[entry]))
                        print("oh no")
                        no_diff = False
        return no_diff







