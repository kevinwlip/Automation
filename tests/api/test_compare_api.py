#!/usr/bin/python

from __future__ import (absolute_import, division, print_function, unicode_literals)
from future.builtins import *

import pdb, json, sys, os, pytest, datetime, random, calendar, time, copy
if sys.version_info < (3, 0):
    from ordereddict import OrderedDict
else:
    from collections import OrderedDict

try:
    env = os.environ['ZBAT_HOME']
except:
    logging.critical('Test cannot run.  Please export ZBAT_HOME.')
    sys.exit()

if env+'lib' not in sys.path:
    sys.path.append(env+'lib')

from zbAPI import zbAPI, Ops
from zbConfig import defaultEnv
from common.zbCommon import traverse as compareDict
from zb_logging import logger as logging


# common variables
#==========================================================
env = defaultEnv()
username = env["username"]
siteTest = env["siteTest"]
siteCompare = env["siteCompare"]


tenantid = env["tenantid"]
deviceid = env["deviceid"]
device_id_risk = env["device_id_risk"]
appid = env["appid"]
timestrict = env["timestrict"]
comparestrict = env["comparestrict"]
datastrict = env["datastrict"]
compareNumberThreshold = int(env["compareNumberThreshold"])


timeFormat = '%Y-%m-%dT%H:%MZ'
ops = Ops()
req = zbAPI()
timenow = datetime.datetime.utcnow().strftime(timeFormat)
timestart = (datetime.datetime.utcnow() - datetime.timedelta(weeks=1)).strftime(timeFormat)

defaultParams = {
    "stime": timestart,
    "etime": "now",
    "tenantid": tenantid,
    "interval": "day",
    "filter_monitored": "yes",
    "direction": "all"
}

defaultIotFilter = ["IoT", "Non_IoT", "All"]
verticalOptions = ["Office"] #["Medical", "Office"] Change this back when we have medical devices

def checkInput(iotOption, myDict):
    if "All" != iotOption:
        myDict["filter_profile_type"] = iotOption
    if "IoT" == iotOption:
        # if testing-soho, might not have Medical devices, so do not set filter_profile_vertical
        #      this would query for any IoT devices
        # For any tenant other than testing-soho, then set this field
        if "testing-soho" not in tenantid:
            myDict["filter_profile_vertical"] = random.choice(verticalOptions)
    else:
        if "filter_profile_vertical" in myDict:
            del myDict["filter_profile_vertical"]
    return myDict

# this function is only needed for time series type API calls
def modifyTimeInterval(starttime):
    if starttime == "-1": 
        return "day"
        
    epoch_stime = calendar.timegm(time.strptime(starttime, timeFormat))
    epoch_now = calendar.timegm(time.gmtime())
    epoch_diff = epoch_now - epoch_stime
    # meaning the time range is 1day
    if epoch_diff > 80000 and epoch_diff < 90000:
        return "minutes"
    # meaning the time range is 1 week
    if epoch_diff > 560000 and epoch_diff < 610000:
        return "hour"
    # else return False
    return False

# this function is needed to see if time range is more than 6 months
def checkTimeGreaterThan(starttime, seconds="2592000"):
    # Always return True if starttime is "-1", it means time range filter is ALL.
    if starttime == "-1":  return True
    # calculate different between starttime and now.
    epoch_stime = calendar.timegm(time.strptime(starttime, timeFormat))
    epoch_now = calendar.timegm(time.gmtime())
    epoch_diff = epoch_now - epoch_stime
    return True if epoch_diff > seconds else False


# test fixtures
#===========================================================
@pytest.fixture(params=["usage", "destination", "session", "app"])
def inputTopDevices(request, genTimeFields):
    kwargs = copy.deepcopy(defaultParams)
    kwargs["outputtype"] = request.param
    kwargs.update(genTimeFields)
    return kwargs

@pytest.fixture(params=["usage", "device", "session"])
def inputTopApps(request, genTimeFields):
    kwargs = copy.deepcopy(defaultParams)
    kwargs["outputtype"] = request.param
    kwargs.update(genTimeFields)
    return kwargs

@pytest.fixture(params=["category", "os", "subnet"])
def inputDeviceCategory(request, genTimeFields):
    kwargs = copy.deepcopy(defaultParams)
    kwargs["type"] = request.param
    kwargs.update(genTimeFields)
    return kwargs

@pytest.fixture(params=["IoT", "Medical", "Non_IoT"])
def inputDistribution(request, genTimeFields):
    kwargs = copy.deepcopy(defaultParams)
    kwargs.update(genTimeFields)
    kwargs.pop("direction",None)
    if(request.param == "Medical"):
        kwargs["filter_profile_type"] = "IoT"
        kwargs["filter_profile_vertical"] = "Medical"
    else:
        kwargs["filter_profile_type"] = request.param
    kwargs["type"] = "device"
    kwargs["groupby"] = "category"
    
    return kwargs

@pytest.fixture()
def inputVulnDistribution(genTimeFields):
    kwargs = {}
    kwargs["groupby"] = "device"
    kwargs["status"] = "Total"
    kwargs["tenantid"] = tenantid
    kwargs["type"] = "vulnerability"
    return kwargs

@pytest.fixture()
def inputVulnStat(genTimeFields):
    kwargs = {}
    kwargs["tenantid"] = tenantid
    kwargs["type"] = "vulnerability"
    return kwargs

@pytest.fixture()
def inputVulnList(genTimeFields):
    kwargs = {}
    kwargs["groupby"] = "vulnerability"
    kwargs["tenantid"] = tenantid
    kwargs["type"] = "vulnerability"
    return kwargs


@pytest.fixture()
def inputDefault(genTimeFields):
    kwargs = copy.deepcopy(defaultParams)
    kwargs.update(genTimeFields)
    return kwargs

@pytest.fixture()
def inputOTDashboard(genTimeFields):
    kwargs = copy.deepcopy(defaultParams)
    kwargs.update(genTimeFields)
    # for test on production update static tenantid to unitedregional because it has OT data
    if os.environ["NODE_ENV"] in ["production"]:
        kwargs["tenantid"] = "unitedregional"
    return kwargs

@pytest.fixture()
def inputAlert(genTimeFields):
    kwargs = copy.deepcopy(defaultParams)
    if "filter_monitored" in kwargs:  del kwargs["filter_monitored"]
    if "interval" in kwargs: del kwargs["interval"]
    if "direction" in kwargs:  del kwargs["direction"]
    kwargs.update(genTimeFields)
    return kwargs

@pytest.fixture()
def inputAlertSpecial():
    kwargs = copy.deepcopy(defaultParams)
    stime = (datetime.datetime.utcnow() - datetime.timedelta(days=30)).strftime(timeFormat)
    etime = (datetime.datetime.utcnow() - datetime.timedelta(days=0)).strftime(timeFormat)
    interval = "day"
    kwargs["stime"] = stime;
    kwargs["etime"] = etime;
    if "filter_monitored" in kwargs:  del kwargs["filter_monitored"]
    if "interval" in kwargs: del kwargs["interval"]
    if "direction" in kwargs:  del kwargs["direction"]
    return kwargs

@pytest.fixture(params=['policy','systemSent','assignee'])
def inputSingleAlert(request):
    kwargs = {}
    kwargs["tenantid"] = tenantid
    kwargs["stime"] = "-1"
    kwargs["etime"] = "now"
    kwargs["groupBy"] = request.param
    kwargs["pagelength"] = "1000"
    kwargs["resolved"] = "no"
    kwargs["sortdirection"] = "desc"
    kwargs["sortfield"] = "date"
    kwargs["type"] = "policy_alert"
    # feeding in bogus alert id, which is ok, real alert get purged so cannot test reliably
    kwargs["data"] = {"alertIdList": ["abcdef012345678901fedcba"]}
    return kwargs

@pytest.fixture(params=["vertical", "category", "profile", "subprofile", "site"])
def inputIotProfile(request, genTimeFields):
    kwargs = copy.deepcopy(defaultParams)
    kwargs["outputtype"] = request.param
    kwargs.update(genTimeFields)
    return kwargs

@pytest.fixture()
def inputMssp(genTimeFields):
    kwargs = {}
    kwargs.update(genTimeFields)
    if "day" in kwargs["interval"]: kwargs["range"] = "7d"
    if "hour" in kwargs["interval"]: kwargs["range"] = "1d"
    if "minutes" in kwargs["interval"]: kwargs["range"] = "2h"
    del kwargs["interval"]
    return kwargs

@pytest.fixture()
def inputDeviceDetail(genTimeFields):
    kwargs = {}
    kwargs.update(genTimeFields)
    return kwargs

@pytest.fixture()
def inputApplicationDetail(genTimeFields):
    kwargs = {}
    kwargs.update(genTimeFields)
    return kwargs

@pytest.fixture()
def inputInspector(genTimeFields):
    kwargs = {}
    kwargs.update(genTimeFields)
    if "day" in kwargs["interval"]: kwargs["range"] = "7d"
    if "hour" in kwargs["interval"]: kwargs["range"] = "1d"
    if "minutes" in kwargs["interval"]: kwargs["range"] = "2h"
    del kwargs["etime"]
    del kwargs["stime"]
    return kwargs

@pytest.fixture()
def input_device_risk(genTimeFields):
    kwargs = {}
    kwargs.update(genTimeFields)
    del kwargs["interval"]
    return kwargs

@pytest.fixture(scope="class", params=["2hour", "1day", "1week", "1month", "1year", "all"])
def genTimeFields(request):
    timeRange = request.param
    if "2hour" == timeRange:
        stime = (datetime.datetime.utcnow() - datetime.timedelta(hours=2)).strftime(timeFormat)
        #etime = (datetime.datetime.utcnow() - datetime.timedelta(hours=1)).strftime(timeFormat)
        etime = "now"
        interval = "minutes"
    if "1day" == timeRange:
        stime = (datetime.datetime.utcnow() - datetime.timedelta(days=1)).strftime(timeFormat)
        #etime = (datetime.datetime.utcnow() - datetime.timedelta(hours=2)).strftime(timeFormat)
        etime = "now"
        interval = "hour"
    if "1week" == timeRange:
        stime = (datetime.datetime.utcnow() - datetime.timedelta(weeks=1)).strftime(timeFormat)
        #etime = (datetime.datetime.utcnow() - datetime.timedelta(hours=2)).strftime(timeFormat)
        etime = "now"
        interval = "day"
    if "1month" == timeRange:
        stime = (datetime.datetime.utcnow() - datetime.timedelta(days=30)).strftime(timeFormat)
        #etime = (datetime.datetime.utcnow() - datetime.timedelta(hours=2)).strftime(timeFormat)
        etime = "now"
        interval = "day"
    if "1year" == timeRange:
        stime = (datetime.datetime.utcnow() - datetime.timedelta(days=365)).strftime(timeFormat)
        #etime = (datetime.datetime.utcnow() - datetime.timedelta(hours=2)).strftime(timeFormat)
        etime = "now"
        interval = "day"
    if "all" == timeRange:
        stime = "-1"
        #etime = (datetime.datetime.utcnow() - datetime.timedelta(hours=2)).strftime(timeFormat)
        etime = "now"
        interval = "day"
    return {"stime":stime, "etime":etime, "interval":interval}


#=========================================================
# generic functions
#=========================================================
def genericRunFunc(site, sitecompare, sitetenantid, api, checkData, **inputDict):
    j1,j2 = {},{}
    site1 = siteTest
    site2 = siteCompare
    # if sitetest is not set through command line arg, then use from config
    if site: site1 = site
    if sitecompare: site2 = sitecompare
    if sitetenantid: inputDict["tenantid"] = sitetenantid

    ts = datetime.datetime.now()
    j1 = api(host=site1, **inputDict)
    t1 = (datetime.datetime.now() - ts).total_seconds()
    logging.debug("Sitetest {0} got data {2}".format(site1, t1, repr(j1).encode('utf-8')))

    # if user did not input --sitetest, then by default use from zbConfig.py and run compare against siteCompare
    # or if user input --sitecompare, then use this as site to compare
    if not site or (site and sitecompare):
        ts = datetime.datetime.now()
        j2 = api(host=site2, **inputDict)
        t2 = (datetime.datetime.now() - ts).total_seconds()
        logging.debug("Sitetest {0} response time {1} got data {2}".format(site2, t2, repr(j2).encode('utf-8')))
        logging.info("site1={0} time1={1} site2={2} time2={3} timestrict={4}".format(site1, t1, site2, t2, timestrict))

    # checking validity of response data
    genericCheckData(site1, j1, site2, j2, checkData)
    return j1,j2


def genericCompareTime(site1, time1, site2, time2, timestrict):
    assert True == ops.timeCompare(time1, time2, strict=timestrict)


def genericCheckData(site1, data1, site2, data2, checkData):
    # checking validity of response data
    if checkData:
        exist1 = ops.dataExist(data1)
        exist2 = ops.dataExist(data2)

        if exist1:
            if not exist2:
                assert False, "Sitetest {} has data, but sitecompare {} does not.  Cannot compare".format(site1, site2)
        else:
            if exist2:
                assert False, "Sitetest {} missing valid response data.".format(site1)
            else:
                logging.error('Site: {0}\nData: {1}\nSite: {2}\nData: {3}'.format(site1, data1, site2, data2))
                assert False, "Both sites {} and {} does not have valid response data.".format(site1, site2)


def genericCompareFunc(site, sitecompare, sitetenantid, api, checkData, **inputDict):
    j1,j2 = genericRunFunc(site, sitecompare, sitetenantid, api, checkData, **inputDict)
    # if user did not input --sitetest, then by default use from zbConfig.py and run compare against siteCompare
    # or if user input --sitecompare, then use this as site to compare
    if not site or (site and sitecompare):
        if 'staging' in env['siteTest']:
            assert True == ops.compare(j1, j2, strict=comparestrict)
        else:
            assert True == compareDict(j1, j2, compareNumberThreshold)
                

def CompareWithIgnore(site, sitecompare, sitetenantid, api, checkData, ignore, **inputDict):
    j1,j2 = genericRunFunc(site, sitecompare, sitetenantid, api, checkData, **inputDict)
    # if user did not input --sitetest, then by default use from zbConfig.py and run compare against siteCompare
    # or if user input --sitecompare, then use this as site to compare
    
    if not site or (site and sitecompare):
        assert True == ops.compare(j1, j2, ignore=ignore, strict=comparestrict)


# tests class/function
#==========================================================

class Test_Whitelist:

    def test_whitelist(self, sitetest, sitecompare, sitetenantid):
        inputDict = {}
        inputDict["tenantid"] = tenantid
        checkData = False
        genericCompareFunc(sitetest, sitecompare, sitetenantid, req.whitelist, checkData, **inputDict)

class Test_ExecutiveDashboard: #Also includes new vulnerability page tests!!!!
    @pytest.mark.parametrize("filter_profile_type", defaultIotFilter)
    def test_compareExecApplication(self, sitetest, sitecompare, sitetenantid, filter_profile_type, inputIotProfile):
        inputDict = checkInput(filter_profile_type, inputIotProfile)
        checkData = True
        genericCompareFunc(sitetest, sitecompare, sitetenantid, req.executiveApplication, checkData, **inputDict)

    @pytest.mark.parametrize("filter_profile_type", defaultIotFilter)
    def test_compareExecDistribution(self, sitetest, sitecompare, sitetenantid, filter_profile_type, inputDistribution):
       
        inputDict = checkInput(filter_profile_type, inputDistribution)
        if "filter_profile_vertical" in inputDict:
            if inputDict["filter_profile_vertical"] == "Medical":
                pytest.skip()
        checkData = True
        genericCompareFunc(sitetest, sitecompare, sitetenantid, req.executiveDistribution, checkData, **inputDict)

    def test_compareExecSecurityDistribution(self, sitetest, sitecompare, sitetenantid, inputDefault):
        inputDict = inputDefault
        inputDict["type"] = "alerts"
        inputDict.pop("direction",None)
        checkData = True
        genericCompareFunc(sitetest, sitecompare, sitetenantid, req.executiveSecurityDistribution, checkData, **inputDict)

    def test_compareExecSecuritySeries(self, sitetest, sitecompare, sitetenantid, inputDefault):
        inputDict = inputDefault
        inputDict["type"] = "alerts"
        inputDict.pop("direction",None)
        checkData = True
        genericCompareFunc(sitetest, sitecompare, sitetenantid, req.executiveSecuritySeries, checkData, **inputDict)

    def test_compareExecVulnDistribution(self, sitetest, sitecompare, sitetenantid, inputVulnDistribution):
        inputDict = inputVulnDistribution
        checkData = True
        genericCompareFunc(sitetest, sitecompare, sitetenantid, req.executiveVulnDistribution, checkData, **inputDict)

    def test_compareExecVulnStat(self, sitetest, sitecompare, sitetenantid, inputVulnStat):
        inputDict = inputVulnStat
        checkData = True
        genericCompareFunc(sitetest, sitecompare, sitetenantid, req.executiveVulnStat, checkData, **inputDict)

    def test_compareExecVulnList(self, sitetest, sitecompare, sitetenantid, inputVulnList):
        inputDict = inputVulnList
        checkData = True
        genericCompareFunc(sitetest, sitecompare, sitetenantid, req.executiveVulnList, checkData, **inputDict)



class Test_Dashboard:

    @pytest.mark.skipif(os.environ["NODE_ENV"] in ["staging"], reason="Skip since test result not consistent due to env diff.")
    @pytest.mark.parametrize("filter_profile_type", defaultIotFilter)
    def test_compareTopDevices(self, sitetest, sitecompare, sitetenantid, inputTopDevices, filter_profile_type):
        inputDict = checkInput(filter_profile_type, inputTopDevices)

        site1 = siteTest
        site2 = siteCompare
        # if sitetest is not set through command line arg, then use from config
        if sitetest: site1 = sitetest
        if sitetenantid: inputDict["tenantid"] = sitetenantid

        # querying Top Devices from site1
        ts = datetime.datetime.now()
        j1 = req.topDevices(host=site1, **inputDict)
        t1 = (datetime.datetime.now() - ts).total_seconds()

        ts2 = datetime.datetime.now()
        j2 = req.topDevices(host=site2, **inputDict)
        t2 = (datetime.datetime.now() - ts2).total_seconds()

        # querying Series for each device
        ts = datetime.datetime.now()
        d1 = {}     
        for dev in json.loads(j1)["agg"]:
            # time.sleep(3)
            d1[dev["key"]] = req.deviceSeries(host=site1, key=dev["key"], **inputDict)

        # querying for specific device detail info
        i1 = {}     
        for dev in json.loads(j1)["agg"]:
            # time.sleep(3)
            i1[dev["key"]] = req.iotDeviceDetail(host=site1, deviceid=dev["key"], **inputDict)

        t1 += (datetime.datetime.now() - ts).total_seconds()
        logging.debug('site1={0} t1={1} j1={2} d1={3}'.format(site1, t1, j1, d1))


        # only run comparison to site2 if test did not configure siteurl
        if not sitetest or (sitetest and sitecompare):
            # if sitecompare given from command line, then use it
            if sitecompare: site2 = sitecompare
            # querying Top Devices from site2
            genericCheckData(site1, j1, site2, j2, True)
            # querying Series for each device
            ts2 = datetime.datetime.now()
            d2 = {}     
            for dev in json.loads(j2)["agg"]:
                # time.sleep(3)
                d2[dev["key"]] = req.deviceSeries(host=site2, key=dev["key"], **inputDict)

            # querying for specific device detail info
            i2 = {}     
            for dev in json.loads(j2)["agg"]:
                # time.sleep(3)
                i2[dev["key"]] = req.iotDeviceDetail(host=site2, deviceid=dev["key"], **inputDict)

            t2 += (datetime.datetime.now() - ts2).total_seconds()
            logging.debug('site2={0} t2={1} j2={2} d2={3}'.format(site2, t2, j2, d2))

            # Assert test result
            if os.environ["NODE_ENV"] in ["production"]:
                # only do the following comparison if on Production-Candidate.  
                # Don't do this on Testing since too much false positive
                assert True == compareDict(j1, j2, compareNumberThreshold) 
                assert True == compareDict(d1, d2, compareNumberThreshold) 
                assert True == compareDict(i1, i2, compareNumberThreshold) 
            assert True == ops.timeCompare(t1, t2, strict=timestrict)


    @pytest.mark.skipif(os.environ["NODE_ENV"] in ["staging"], reason="Skip since test result not consistent due to env diff.")
    @pytest.mark.parametrize("filter_profile_type", defaultIotFilter)
    def test_compareTopApps(self, sitetest, sitecompare, sitetenantid, inputTopApps, filter_profile_type):
        inputDict = checkInput(filter_profile_type, inputTopApps)

        site1 = siteTest
        site2 = siteCompare
        # if sitetest is not set through command line arg, then use from config
        if sitetest: site1 = sitetest
        if sitetenantid: inputDict["tenantid"] = sitetenantid

        # querying Top Apps from site1
        ts = datetime.datetime.now()
        j1 = req.topAppsProtocol(host=site1, **inputDict)
        t1 = (datetime.datetime.now() - ts).total_seconds()

        ts2 = datetime.datetime.now()
        j2 = req.topAppsProtocol(host=site2, **inputDict)
        t2 = (datetime.datetime.now() - ts2).total_seconds()


        # querying Series for each device
        ts = datetime.datetime.now()
        d1 = {}
        for dev in json.loads(j1)["agg"]:
            d1[dev["key"]] = req.appSeries(host=site1, key=dev["key"], **inputDict)

        # querying for specific app detail info
        i1 = {}     
        for dev in json.loads(j1)["agg"]:
            i1[dev["key"]] = req.iotAppDetail(host=site1, appid=dev["key"], **inputDict)

        t1 += (datetime.datetime.now() - ts).total_seconds()
        logging.debug('site1={0} t1={1} j1={2} d1={3}'.format(site1, t1, j1, d1))

        # only run comparison to site2 if test did not configure siteurl
        if not sitetest or (sitetest and sitecompare):
            # if sitecompare given from command line, then use it
            if sitecompare: site2 = sitecompare
            # querying Top Apps from site2
            genericCheckData(site1, j1, site2, j2, True)
            # querying Series for each device
            ts2 = datetime.datetime.now()
            d2 = {}     
            for dev in json.loads(j2)["agg"]:
                d2[dev["key"]] = req.appSeries(host=site2, key=dev["key"], **inputDict)

            # querying for specific app detail info
            i2 = {}     
            for dev in json.loads(j2)["agg"]:
                i2[dev["key"]] = req.iotAppDetail(host=site2, appid=dev["key"], **inputDict)

            t2 += (datetime.datetime.now() - ts2).total_seconds()
            logging.debug('site2={0} t2={1} j2={2} d2={3}'.format(site2, t2, j2, d2))

            # Assert test result
            if os.environ["NODE_ENV"] in ["production"]:
                # only do the following comparison if on Production-Candidate.  
                # Don't do this on Testing since too much false positive
                assert True == compareDict(j1, j2, compareNumberThreshold) 
                assert True == compareDict(d1, d2, compareNumberThreshold) 
                assert True == compareDict(i1, i2, compareNumberThreshold) 
            assert True == ops.timeCompare(t1, t2, strict=timestrict)


    @pytest.mark.parametrize("filter_profile_type", defaultIotFilter)
    def test_compareRiskAssessment(self, sitetest, sitecompare, sitetenantid, inputDefault, filter_profile_type):
        inputDict = checkInput(filter_profile_type, inputDefault)
        checkData = False
        genericCompareFunc(sitetest, sitecompare, sitetenantid, req.riskAssessment, checkData, **inputDict)



    @pytest.mark.parametrize("filter_profile_type", defaultIotFilter)
    def test_compareNetworkSummary(self, sitetest, sitecompare, sitetenantid, inputDefault, filter_profile_type):
        inputDict = checkInput(filter_profile_type, inputDefault)
        checkData = True
        genericCompareFunc(sitetest, sitecompare, sitetenantid, req.networkSummary, checkData, **inputDict)


    @pytest.mark.parametrize("filter_profile_type", defaultIotFilter)
    def test_compareTrafficSeries(self, sitetest, sitecompare, sitetenantid, inputDefault, filter_profile_type):
        inputDict = checkInput(filter_profile_type, inputDefault)

        # for large series chart, we need to modify interval
        interval = modifyTimeInterval(inputDict["stime"])
        if interval: inputDict["interval"] = interval

        checkData = True
        genericCompareFunc(sitetest, sitecompare, sitetenantid, req.trafficSeries, checkData, **inputDict)


    @pytest.mark.skipif(os.environ["NODE_ENV"] in ["staging"], reason="Skip since test result not consistent due to env diff.")
    @pytest.mark.parametrize("filter_profile_type", defaultIotFilter)
    def test_compareDeviceCategory(self, sitetest, sitecompare, sitetenantid, inputDeviceCategory, filter_profile_type):
        inputDict = checkInput(filter_profile_type, inputDeviceCategory)
        checkData = True
        genericCompareFunc(sitetest, sitecompare, sitetenantid, req.deviceCategory, checkData, **inputDict)


    @pytest.mark.parametrize("filter_profile_type", defaultIotFilter)
    def test_compareDeviceSummary(self, sitetest, sitecompare, sitetenantid, inputDefault, filter_profile_type):
        inputDict = checkInput(filter_profile_type, inputDefault)
        checkData = True
        genericCompareFunc(sitetest, sitecompare, sitetenantid, req.deviceSummary, checkData, **inputDict)


    @pytest.mark.skipif(os.environ["NODE_ENV"] in ["staging"], reason="Skip since test result not consistent due to env diff.")
    @pytest.mark.parametrize("filter_profile_type", defaultIotFilter)
    def test_compareDeviceSubnetVLAN(self, sitetest, sitecompare, sitetenantid, inputDefault, filter_profile_type):
        inputDict = checkInput(filter_profile_type, inputDefault)
        inputDefault["type"] = "subnet"
        checkData = True
        genericCompareFunc(sitetest, sitecompare, sitetenantid, req.deviceSubnet, checkData, **inputDict)


    @pytest.mark.parametrize("filter_profile_type", defaultIotFilter)
    def test_compareExternalEndpoint(self, sitetest, sitecompare, sitetenantid, inputDefault, filter_profile_type):
        inputDict = checkInput(filter_profile_type, inputDefault)
        inputDefault["groupbycountry"] = "no"
        checkData = True
        genericCompareFunc(sitetest, sitecompare, sitetenantid, req.networkDestination, checkData, **inputDict)


    @pytest.mark.parametrize("filter_profile_type", defaultIotFilter)
    def test_compareExternalEndpointGeoMap(self, sitetest, sitecompare, sitetenantid, inputDefault, filter_profile_type):
        inputDict = checkInput(filter_profile_type, inputDefault)
        inputDefault["groupbycountry"] = "yes"
        checkData = True
        genericCompareFunc(sitetest, sitecompare, sitetenantid, req.networkDestination, checkData, **inputDict)


    @pytest.mark.parametrize("filter_profile_type", defaultIotFilter)
    def test_compareExternalEndpointMalicious(self, sitetest, sitecompare, sitetenantid, inputDefault, filter_profile_type):
        inputDict = checkInput(filter_profile_type, inputDefault)

        inputDefault["groupbycountry"] = "yes"
        inputDefault["malicious"] = "yes"

        checkData = True
        genericCompareFunc(sitetest, sitecompare, sitetenantid, req.networkDestination, checkData, **inputDict)


    def test_compareSuspiciousDest(self, sitetest, sitecompare, sitetenantid, inputDefault):
        inputDict = {}
        inputDict["country"] = "US"
        inputDict["direction"] = inputDefault["direction"] 
        inputDict["stime"] = inputDefault["stime"] 
        inputDict["etime"] = inputDefault["etime"] 
        inputDict["filter_monitored"] = inputDefault["filter_monitored"] 
        inputDict["interval"] = inputDefault["interval"] 
        inputDict["tenantid"] = inputDefault["tenantid"] 

        # For 2hour and 1day, not making data restriction, because in some case there are no suspicious destination for such short time range
        checkData = True if checkTimeGreaterThan(inputDict["stime"], 1209600) else False
        genericCompareFunc(sitetest, sitecompare, sitetenantid, req.destReputation, checkData, **inputDict)


    @pytest.mark.skipif(os.environ["NODE_ENV"] in ["staging"], reason="Skip since test result not consistent due to env diff.")
    @pytest.mark.parametrize("filter_profile_type", ["IoT", "Non_IoT", "All"])
    def test_compareIotProfile(self, sitetest, sitecompare, sitetenantid, filter_profile_type, inputIotProfile):
        inputDict = checkInput(filter_profile_type, inputIotProfile)
        checkData = True
        genericCompareFunc(sitetest, sitecompare, sitetenantid, req.iotProfile, checkData, **inputDict)




@pytest.mark.skipif(os.environ["NODE_ENV"] in ["staging"], reason="Skip since test result not consistent due to env diff.")
class Test_OTDashboard:


    def test_compareOTDeviceStat(self, sitetest, sitecompare, sitetenantid, inputOTDashboard):
        inputDict = inputOTDashboard
        checkData = True
        genericCompareFunc(sitetest, sitecompare, sitetenantid, req.otDeviceStat, checkData, **inputDict)

    @pytest.mark.skipif(os.environ["NODE_ENV"] in ["testing"], reason="Skip since Testing environment might not have OT data for 1 day range.")
    def test_compareOTDeviceSeries(self, sitetest, sitecompare, sitetenantid, inputOTDashboard):
        inputDict = inputOTDashboard
        # inputDict['filter_profile_category'] = 'X-Ray Machine'
        if 'filter_monitored' in inputDict:
            del inputDict['filter_monitored']
        checkData = True
        genericCompareFunc(sitetest, sitecompare, sitetenantid, req.otDeviceSeries, checkData, **inputDict)

    @pytest.mark.skipif(os.environ["NODE_ENV"] in ["testing"], reason="Skip since Testing environment might not have OT data for 1 day range.")
    def test_compareOTDeviceSeriesAgg(self, sitetest, sitecompare, sitetenantid, inputOTDashboard):
        inputDict = inputOTDashboard
        checkData = True
        genericCompareFunc(sitetest, sitecompare, sitetenantid, req.otDeviceSeriesAgg, checkData, **inputDict)

    @pytest.mark.skipif(os.environ["NODE_ENV"] in ["testing"], reason="Skip since Testing environment might not have OT data for 1 day range.")
    def test_compareOTDeviceAgg(self, sitetest, sitecompare, sitetenantid, inputOTDashboard):
        inputDict = inputOTDashboard
        checkData = True
        genericCompareFunc(sitetest, sitecompare, sitetenantid, req.otDeviceAgg, checkData, **inputDict)

    @pytest.mark.skipif(os.environ["NODE_ENV"] in ["testing"], reason="Skip since Testing environment might not have OT data for 1 day range.")
    def test_compareOTDeviceList(self, sitetest, sitecompare, sitetenantid, inputOTDashboard):
        inputDict = inputOTDashboard
        checkData = True
        genericCompareFunc(sitetest, sitecompare, sitetenantid, req.otDeviceList, checkData, **inputDict)


class Test_Monitor:

    @pytest.mark.parametrize("filter_profile_type", ["IoT", "Non_IoT", "All"])
    def test_compareDeviceInventory(self, sitetest, sitecompare, sitetenantid, filter_profile_type, inputDefault):
        inputDict = checkInput(filter_profile_type, inputDefault)

        # for large series chart, we need to modify interval
        interval = modifyTimeInterval(inputDict["stime"])
        if interval: inputDict["interval"] = interval

        checkData = True
        genericCompareFunc(sitetest, sitecompare, sitetenantid, req.iotInventorySeries, checkData, **inputDict)


    @pytest.mark.parametrize("filter_profile_type", ["IoT", "Non_IoT", "All"])
    @pytest.mark.parametrize("page", ["1"])
    def test_compareDeviceList(self, sitetest, sitecompare, sitetenantid, filter_profile_type, page, inputDefault):
        inputDict = checkInput(filter_profile_type, inputDefault)
        inputDict["page"] =page
        inputDict["pagelength"] = "25"

        checkData = True
        ignore = ["datetime"]
        genericCompareFunc(sitetest, sitecompare, sitetenantid, req.iotInventorySeries, checkData, **inputDict)
        #CompareWithIgnore(sitetest, sitecompare, sitetenantid, req.iotInventoryList, checkData, ignore, **inputDict)


    @pytest.mark.skipif(os.environ["NODE_ENV"] not in ["production"], reason="Device Inventory Geo List too slow to load on testing/staging")
    def test_compareDeviceGeoList(self, sitetest, sitecompare, sitetenantid, inputDefault):
        inputDict = inputDefault
        inputDict["page"] = "1"
        inputDict["pagelength"] = "25"
        inputDict["sortfield"] = "risk_level"
        inputDict["malicious"] = "yes"
        inputDict["country"] = "US"

        checkData = True
        ignore = ["datetime"]
        CompareWithIgnore(sitetest, sitecompare, sitetenantid, req.iotInventoryGeoDestList, checkData, ignore, **inputDict)


    @pytest.mark.skipif(os.environ["NODE_ENV"] not in ["production"], reason="Application Inventory too slow to load on testing/staging")
    # commenting out filter_profile_type since it's not applicable for Application page.  Leaving it here because it might be a valid filter later.
    #@pytest.mark.parametrize("filter_profile_type", ["IoT", "Non_IoT", "All"])
    @pytest.mark.parametrize("page", ["1", "2"])
    #def test_compareApplicationInventory(self, filter_profile_type, page, inputDefault):
    #   inputDefault = checkInput(filter_profile_type, inputDefault)
    def test_compareApplicationInventory(self, sitetest, sitecompare, sitetenantid, page, inputDefault):
        inputDict = inputDefault
        inputDict["page"] =page
        checkData = True
        genericCompareFunc(sitetest, sitecompare, sitetenantid, req.iotApplicationSeries, checkData, **inputDict)


    @pytest.mark.parametrize("filter_profile_type", ["IoT", "Non_IoT", "All"])
    @pytest.mark.parametrize("page", ["1"])
    def test_compareApplicationList(self, sitetest, sitecompare, sitetenantid, filter_profile_type, page, inputDefault):
        inputDict = checkInput(filter_profile_type, inputDefault)
        inputDict["page"] = page
        inputDict["pagelength"] = "25"
        checkData = True
        genericCompareFunc(sitetest, sitecompare, sitetenantid, req.iotApplicationList, checkData, **inputDict)


class Test_Alert:


    @pytest.mark.parametrize("resolve", ["notresolve", "resolve"])
    def test_compareAlertStat(self, sitetest, sitecompare, sitetenantid, resolve, inputAlert):
        if "resolve" == resolve:
            inputAlert["resolve"] = "yes"
        else:
            inputAlert["resolve"] = "no"
        checkData = True
        genericCompareFunc(sitetest, sitecompare, sitetenantid, req.alertStat, checkData, **inputAlert)

    def test_compareAlertAssignees(self, sitetest, sitecompare, sitetenantid, inputAlert):
        checkData = True
        genericCompareFunc(sitetest, sitecompare, sitetenantid, req.alertAssignees, checkData, **inputAlert)

    @pytest.mark.parametrize("resolve", ["notresolve", "resolve"])
    def test_compareAlertChartStat(self, sitetest, sitecompare, sitetenantid, resolve, inputAlert):
        if "resolve" == resolve:
            inputAlert["resolve"] = "yes"
        else:
            inputAlert["resolve"] = "no"

        
        checkData = False
        ignore = ["datetime"]
        CompareWithIgnore(sitetest, sitecompare, sitetenantid, req.alertChartStat, checkData, ignore, **inputAlert)


    @pytest.mark.parametrize("filter_profile_type", ["IoT", "Non_IoT", "All"])
    def test_compareAlertRetrieve(self, sitetest, sitecompare, sitetenantid, filter_profile_type, inputAlert):
        inputAlert = checkInput(filter_profile_type, inputAlert)
        inputAlert["resolve"] = random.choice(["no", "yes"])
        inputAlert["dismissed"] = random.choice(["false", "true"])
        inputAlert["sortdirection"] = random.choice(["asc", "desc"])
        inputAlert["type"] = "system_alert"
        inputAlert["offset"] = "0"
        inputAlert["pagelength"] = "50"
        inputAlert["sortfield"] = "date"
        inputAlert["siteids"] = "0"

        checkData = False
        ignore = ["datetime"]
        CompareWithIgnore(sitetest, sitecompare, sitetenantid, req.alertRetrieve, checkData, ignore, **inputAlert)

    @pytest.mark.skipif(os.environ["NODE_ENV"] not in ["production"], reason="This test should only be run on production.")
    @pytest.mark.parametrize("sitetenantid2",["baycare", "allinahealth", "pinnaclehealth"])
    def test_compareAlertSankeyChart(self, sitetenantid2,  inputAlertSpecial):
        #inputAlert = checkInput(["All"], inputAlertSpecial)
        inputAlert = inputAlertSpecial
        sitetest2 = sitetenantid2 + ".zingbox.com"
        inputAlert["sortdirection"] = "desc"
        inputAlert["groupby"] = "policy"
        inputAlert["type"] = "policy_alert"
        inputAlert["pagelength"] = "1000"
        inputAlert["sortfield"] = "date"
        inputAlert["tenantid"] = sitetenantid2
        checkData = False
        ignore = ["datetime"]
        muh_data = req.alertRetrieve(host=sitetest2,**inputAlert)
        items = muh_data.encode('ascii','ignore')
        item = json.loads(items)["items"][0]
        inputy = {}
        inputy["alertid"] = item["id"]
        inputy["tenantid"] = sitetenantid2
        output = req.alertSankeyChart(host=sitetest2,**inputy)
        #print(output)
        if json.loads(output)["item"] == None:
            assert False
            
        assert True


    def test_compareAlertFeeds(self, sitetest, sitecompare, sitetenantid, inputAlert):
        site1 = siteTest
        site2 = siteCompare

       # skipping test for 1month or more, because we have too many alerts on Testing env, and python
        # http request is running out of memory.
        if checkTimeGreaterThan(inputAlert["stime"], seconds=3600*24*28):
            pytest.skip("Skipping on Testing env for 6months, due to too many test alerts")

        checkData = True
        ignore = []
        CompareWithIgnore(sitetest, sitecompare, sitetenantid, req.alertFeeds, checkData, ignore, **inputAlert)


    def test_compareSingleAlert(self, sitetest, sitecompare, sitetenantid, inputSingleAlert):
        site1 = siteTest
        site2 = siteCompare

        checkData = False
        ignore = []
        CompareWithIgnore(sitetest, sitecompare, sitetenantid, req.alerts, checkData, ignore, **inputSingleAlert)


class Test_Administration:

    def test_compareSiteInspectorList(self, sitetest, sitecompare, sitetenantid):
        inputDict = {}
        inputDict["tenantid"] = defaultParams["tenantid"]
        checkData = True
        genericCompareFunc(sitetest, sitecompare, sitetenantid, req.siteInspectorList, checkData, **inputDict)


    def test_compareSiteInspectorSimpleList(self, sitetest, sitecompare, sitetenantid):
        inputDict = {}
        inputDict["tenantid"] = defaultParams["tenantid"]
        checkData = True
        genericCompareFunc(sitetest, sitecompare, sitetenantid, req.siteInspectorSimpleList, checkData, **inputDict)


    @pytest.mark.skip('Until bug fix. API call for cpumem broken')
    def test_compareInspectorDetail(self, sitetest, sitecompare, sitetenantid):
        inputDict = {}
        inputDict["tenantid"] = defaultParams["tenantid"]

        inputDictCpuMem = {}
        inputDictCpuMem["tenantid"] = defaultParams["tenantid"]
        inputDictCpuMem["stime"] = defaultParams["stime"]
        inputDictCpuMem["etime"] = defaultParams["etime"]
        inputDictCpuMem["interval"] = "1d"

        site1 = siteTest
        site2 = siteCompare
        # if sitetest is not set through command line arg, then use from config
        if sitetest: site1 = sitetest
        if sitetenantid: inputDictCpuMem["tenantid"] = sitetenantid

        ts = datetime.datetime.now()
        j1 = req.inspectorDetail(host=site1, **inputDict)
        # querying cpu/mem for each inspector
        d1 = {}     
        for dev in json.loads(j1)["inspectors"]:
            d1[dev["inspectorid"]] = req.inspectorCpuMem(host=site1, routerid=dev["inspectorid"], **inputDictCpuMem)
        t1 = (datetime.datetime.now() - ts).total_seconds()
        logging.debug('site1={0} t1={1} j1={2} d1={3}'.format(site1, t1, j1, d1))

        if not sitetest or (sitetest and sitecompare):
            # if sitecompare given from command line, then use it
            if sitecompare: site2 = sitecompare
            ts = datetime.datetime.now()
            j2 = req.inspectorDetail(host=site2, **inputDict)
            genericCheckData(site1, j1, site2, j2, True)
            # querying cpu/mem for each inspector
            d2 = {}     
            for dev in json.loads(j2)["inspectors"]:
                d2[dev["inspectorid"]] = req.inspectorCpuMem(host=site2, routerid=dev["inspectorid"], **inputDictCpuMem)
            t2 = (datetime.datetime.now() - ts).total_seconds()
            logging.debug('site2={0} t2={1} j2={2} d2={3}'.format(site2, t2, j2, d2))

            assert True == ops.compare(j1, j2,  ignore=["datetime"], strict=comparestrict) 
            assert True == ops.compare(d1, d2, strict=timestrict) 
            assert True == ops.timeCompare(t1, t2, strict=timestrict)

    def test_compareInspectorTrafficTrend(self, sitetest, sitecompare, sitetenantid, inputInspector):
        inputDict = inputInspector
        inputDict["tenantid"] = defaultParams["tenantid"]
        inputDict["interval"] = "1d"
        checkData = True
        genericCompareFunc(sitetest, sitecompare, sitetenantid, req.inspectorTrafficTrend, checkData, **inputDict)


    @pytest.mark.parametrize("page", ["1"])
    @pytest.mark.parametrize("sortfield", ["timestamp"])
    def test_compareAuditLogs(self, sitetest, sitecompare, sitetenantid, page, sortfield):
        inputDict = {}
        inputDict["tenantid"] = defaultParams["tenantid"]
        inputDict["stime"] = defaultParams["stime"]
        inputDict["etime"] = defaultParams["etime"]
        inputDict["sortdirection"] = random.choice(["asc", "desc"])
        inputDict["sortfield"] = sortfield
        inputDict["page"] = page
        inputDict["pagelength"] = "25"
        checkData = True
        genericCompareFunc(sitetest, sitecompare, sitetenantid, req.auditLogs, checkData, **inputDict)

    def test_compare_integration_config(self, sitetest, sitecompare, sitetenantid):
        inputDict = {}
        inputDict["tenantid"] = defaultParams["tenantid"]
        checkData = True
        genericCompareFunc(sitetest, sitecompare, sitetenantid, req.thirdparty_all_config, checkData, **inputDict)



@pytest.mark.skipif(os.environ["NODE_ENV"] not in ["production"], reason="MSSP portal only on production")
class Test_MSSP:

    def test_compareTotalCustomer(self, sitetest, sitecompare, inputMssp):
        maxCount = 5
        inputDict = {}
        inputDict["tenantid"] = "all"

        site1 = siteTest
        site2 = siteCompare
        # if sitetest is not set through command line arg, then use from config
        if sitetest: site1 = sitetest

        ts = datetime.datetime.now()
        j1 = req.msspPortalGetTenant(host=site1, **inputDict)
        # querying for each tenant detail
        d1 = {}
        count = 0       
        for tenant in json.loads(j1)["items"]:
            d1[tenant["doc"]["externaltenantid"]] = req.msspPortalTenantSummary(host=site1, tenantid=tenant["doc"]["externaltenantid"], **inputMssp)
            count +=1
            if count >= maxCount: break
        t1 = (datetime.datetime.now() - ts).total_seconds()
        logging.debug('site1={0} t1={1} j1={2} d1={3}'.format(site1, t1, j1, d1))

        if not sitetest or (sitetest and sitecompare):
            # if sitecompare given from command line, then use it
            if sitecompare: site2 = sitecompare
            ts = datetime.datetime.now()
            j2 = req.msspPortalGetTenant(host=site2, **inputDict)
            genericCheckData(site1, j1, site2, j2, True)
            # querying for each tenant detail
            d2 = {} 
            count = 0   
            for tenant in json.loads(j2)["items"]:
                d2[tenant["doc"]["externaltenantid"]] = req.msspPortalTenantSummary(host=site2, tenantid=tenant["doc"]["externaltenantid"], **inputMssp)
                count +=1
                if count >= maxCount: break
            t2 = (datetime.datetime.now() - ts).total_seconds()
            logging.debug('site2={0} t2={1} j2={2} d2={3}'.format(site2, t2, j2, d2))

            assert True == compareDict(j1, j2, compareNumberThreshold) 
            assert True == ops.compare(d1, d2, ignore=["datetime"], strict=timestrict)
            assert True == ops.timeCompare(t1, t2, strict=timestrict)

    def test_compareMSSPProfile(self, sitetest, sitecompare, sitetenantid, inputMssp):
        inputDict = inputMssp
        inputDict["tenantid"] = defaultParams["tenantid"]
        inputDict["username"] = username
        checkData = False
        genericCompareFunc(sitetest, sitecompare, sitetenantid, req.msspPortalProfile, checkData, **inputDict)


    def test_compareTenantDetail(self, sitetest, sitecompare, sitetenantid, inputMssp):

        # Note that MSSP Portal's tenant detail also contain an API call to api/alert/retrieve
        #   However, we're not testing here.  That is because that call is already cover in another test_compareAlertRetrieve
        #   So it doesn't make sense to call it again here.

        inputDict = inputMssp
        inputDict["tenantid"] = defaultParams["tenantid"]

        site1 = siteTest
        site2 = siteCompare
        # if sitetest is not set through command line arg, then use from config
        if sitetest: site1 = sitetest
        if sitetenantid: inputDict["tenantid"] = sitetenantid

        ts = datetime.datetime.now()
        j1 = req.msspPortalTenantSummary(host=site1, **inputMssp)
        t1 = (datetime.datetime.now() - ts).total_seconds()

        ts2 = datetime.datetime.now()
        j2 = req.msspPortalTenantSummary(host=site2, **inputMssp)
        t2 = (datetime.datetime.now() - ts2).total_seconds()

        # querying for each site detail
        ts = datetime.datetime.now()
        d1 = {} 
        for apires in json.loads(j1):
            if apires["api"] == 'site/simplelist':
                for site in apires["list"]:
                    d1[site["siteid"]] = req.msspPortalTenantSummary(host=site1, siteids=site["siteid"], **inputMssp)
        t1 += (datetime.datetime.now() - ts).total_seconds()
        logging.debug('site1={0} t1={1} j1={2} d1={3}'.format(site1, t1, j1, d1))

        if not sitetest or (sitetest and sitecompare):
            # if sitecompare given from command line, then use it
            if sitecompare: site2 = sitecompare
            genericCheckData(site1, j1, site2, j2, True)
            # querying for each site detail
            ts2 = datetime.datetime.now()
            d2 = {} 
            for apires in json.loads(j2):
                if apires["api"] == 'site/simplelist':
                    for site in apires["list"]:
                        d2[site["siteid"]] = req.msspPortalTenantSummary(host=site2, siteids=site["siteid"], **inputMssp)
            t2 += (datetime.datetime.now() - ts2).total_seconds()
            logging.debug('site2={0} t2={1} j2={2} d2={3}'.format(site2, t2, j2, d2))

            compareNumberThreshold = 50
            assert True == compareDict(j1, j2, compareNumberThreshold) 
            assert True == ops.compare(d1, d2, ignore=["datetime"], strict=timestrict) 
            assert True == ops.timeCompare(t1, t2, strict=timestrict)

    def test_compareTenantSelectedSummary(self, sitetest, sitecompare, sitetenantid, inputMssp):
        inputDict = inputMssp
        inputDict["tenantid"] = defaultParams["tenantid"]
        inputDict["stats"] = "tenantinspectors,seriesagg,devicesummary"
        
        site1 = siteTest
        site2 = siteCompare
        # if sitetest is not set through command line arg, then use from config
        if sitetest: site1 = sitetest
        if sitetenantid: inputDict["tenantid"] = sitetenantid

        ts = datetime.datetime.now()
        j1 = req.msspPortalTenantSelectedSummary(host=site1, **inputDict)
        for summary in json.loads(j1):
            if not ops.dataExist(json.dumps(summary)): assert False, "Error, missing data in response "+str(summary)
        t1 = (datetime.datetime.now() - ts).total_seconds()
        logging.debug('site1={0} t1={1} j1={2}'.format(site1, t1, j1))

        if not sitetest or (sitetest and sitecompare):
            # if sitecompare given from command line, then use it
            if sitecompare: site2 = sitecompare
            ts = datetime.datetime.now()
            j2 = req.msspPortalTenantSelectedSummary(host=site2, **inputDict)
            for summary in json.loads(j2):
                if not ops.dataExist(json.dumps(summary)): assert False, "Error, missing data in response "+str(summary)
            t2 = (datetime.datetime.now() - ts).total_seconds()
            logging.debug('site2={0} t2={1} j2={2}'.format(site2, t2, j2))

            assert True == compareDict(j1, j2, compareNumberThreshold)
            assert True == ops.timeCompare(t1, t2, strict=timestrict)


    def test_compareDistributorTenants(self, sitetest, sitecompare, sitetenantid, inputMssp):
        inputDict = inputMssp
        inputDict["tenantid"] = defaultParams["tenantid"]
        checkData = True
        genericCompareFunc(sitetest, sitecompare, sitetenantid, req.msspPortalDistributorTenants, checkData, **inputDict)


    def test_compareTenantStat(self, sitetest, sitecompare, sitetenantid, inputMssp):
        inputDict = inputMssp
        inputDict["tenantid"] = defaultParams["tenantid"]
        checkData = True
        genericCompareFunc(sitetest, sitecompare, sitetenantid, req.msspPortalTenantStat, timestrict, **inputDict)


    @pytest.mark.skip('Skipping MSSP tests, API call returns nothing currently')
    def test_compareDistributorResellers(self, sitetest, sitecompare, sitetenantid, inputMssp):
        maxCount = 5
        inputDict = inputMssp
        inputDict["tenantid"] = defaultParams["tenantid"]

        site1 = siteTest
        site2 = siteCompare
        # if sitetest is not set through command line arg, then use from config
        if sitetest: site1 = sitetest
        if sitetenantid: inputDict["tenantid"] = sitetenantid

        ts = datetime.datetime.now()
        j1 = req.msspPortalDistributorResellers(host=site1, **inputMssp)
        # querying for each reseller detail
        d1 = {}
        count = 0
        for reseller in json.loads(j1)["items"]:
            d1[reseller["_id"]] = req.msspPortalGetReseller(host=site1, reseller=reseller["name"], **inputMssp)
            count +=1
            if count >= maxCount: break
        t1 = (datetime.datetime.now() - ts).total_seconds()

        logging.debug('site1={0} t1={1} j1={2} d1={3}'.format(site1, t1, j1, d1))

        if not sitetest or (sitetest and sitecompare):
            # if sitecompare given from command line, then use it
            if sitecompare: site2 = sitecompare
            ts = datetime.datetime.now()
            j2 = req.msspPortalDistributorResellers(host=site2, **inputMssp)
            genericCheckData(site1, j1, site2, j2, True)
            # querying for each reseller detail
            d2 = {}
            count = 0
            for reseller in json.loads(j2)["items"]:
                d2[reseller["_id"]] = req.msspPortalGetReseller(host=site2, reseller=reseller["name"], **inputMssp)
                count +=1
                if count >= maxCount: break
            t2 = (datetime.datetime.now() - ts).total_seconds()
            logging.debug('site2={0} t2={1} j2={2} d2={3}'.format(site2, t2, j2, d2))

            assert True == compareDict(j1, j2, compareNumberThreshold)
            assert True == ops.compare(d1, d2, strict=timestrict)
            assert True == ops.timeCompare(t1, t2, strict=timestrict)


class Test_Device_Detail:

    def test_compareDeviceDetailStat(self, sitetest, sitecompare, sitetenantid):
        inputDict = {}
        inputDict["deviceid"] = deviceid
        inputDict["tenantid"] = tenantid
        checkData = True
        ignore = ["datetime"]
        CompareWithIgnore(sitetest, sitecompare, sitetenantid, req.iotDeviceStat, checkData, ignore, **inputDict)


    def test_compareDeviceDetailSeries(self, sitetest, sitecompare, sitetenantid, inputDeviceDetail):
        inputDict = inputDeviceDetail
        inputDict["deviceid"] = deviceid
        inputDict["tenantid"] = tenantid
        checkData = True
        ignore = ["datetime"]
        CompareWithIgnore(sitetest, sitecompare, sitetenantid, req.iotDeviceDetail, checkData, ignore, **inputDict)


    def test_compareDeviceDetailGeoInfo(self, sitetest, sitecompare, sitetenantid, inputDeviceDetail):
        inputDict = inputDeviceDetail
        inputDict["deviceid"] = deviceid
        inputDict["tenantid"] = tenantid
        checkData = True
        genericCompareFunc(sitetest, sitecompare, sitetenantid, req.iotDeviceGeo, checkData, **inputDict)


    @pytest.mark.parametrize("filtertype", ["ip", "app"])
    def test_compareDeviceDetailNetwork(self, sitetest, sitecompare, sitetenantid, filtertype, inputDeviceDetail):
        inputDict = inputDeviceDetail
        inputDict["deviceid"] = deviceid
        inputDict["tenantid"] = tenantid
        inputDict["type"] = filtertype

        # skipping test for 6month, because we have too many alerts on Testing env, and python
        # http request is running out of memory.
        if checkTimeGreaterThan(inputDict["stime"], seconds=3600*24*180) and os.environ["NODE_ENV"] not in ["production"]:
            pytest.skip("Skipping on Testing env for 6months, due to to timeout for this call")

        checkData = True
        ignore = ["number", "url"]
        CompareWithIgnore(sitetest, sitecompare, sitetenantid, req.iotDeviceNetwork, checkData, ignore, **inputDict)


    @pytest.mark.skipif(os.environ["NODE_ENV"] not in ["production"], reason="Device Detail Network Usage too slow to load on testing/staging")
    @pytest.mark.parametrize("filtertype", ["urlcategory", "subnet"])
    def test_compareDeviceDetailNetworkUsage(self, sitetest, sitecompare, sitetenantid, filtertype, inputDeviceDetail):
        inputDict = inputDeviceDetail
        inputDict["deviceid"] = deviceid
        inputDict["tenantid"] = tenantid
        inputDict["type"] = filtertype

        # skipping test for 2 hour.  We need to remove this once performance bug is fixed.
        if not checkTimeGreaterThan(inputDict["stime"], seconds=3600*3):
            pytest.skip("Skipping for 2hours test, since might not have traffic data")

        checkData = True
        ignore = ["number"]
        CompareWithIgnore(sitetest, sitecompare, sitetenantid, req.iotDeviceNetworkUsage, checkData, ignore, **inputDict)


    @pytest.mark.skipif(os.environ["NODE_ENV"] not in ["production"], reason="Sankey chart too slow to load on testing/staging")
    def test_compareDeviceDetailSankeyChart(self, sitetest, sitecompare, sitetenantid, inputDeviceDetail):
        inputDict = inputDeviceDetail
        inputDict["deviceid"] = deviceid
        inputDict["tenantid"] = tenantid

        checkData = True
        ignore = ["url"]
        CompareWithIgnore(sitetest, sitecompare, sitetenantid, req.iotDeviceNetworkMapping, checkData, ignore, **inputDict)

    def test_compareDeviceDetailAnomalyMapping(self, sitetest, sitecompare, sitetenantid):
        inputDict = {}
        inputDict["deviceid"] = deviceid
        inputDict["tenantid"] = tenantid

        checkData = True
        ignore = []
        CompareWithIgnore(sitetest, sitecompare, sitetenantid, req.iotDeviceAnomalyMapping, checkData, ignore, **inputDict)

    def test_compare_device_detail_risk(self, sitetest, sitecompare, sitetenantid, input_device_risk):
        inputDict = input_device_risk
        inputDict["deviceid"] = device_id_risk
        inputDict["tenantid"] = tenantid

        if not checkTimeGreaterThan(inputDict["stime"], seconds=3600*25):
            pytest.skip("Skipping for 2hours and 1 day, since might not have traffic data")

        checkData = True
        genericCompareFunc(sitetest, sitecompare, sitetenantid, req.iot_device_risk, checkData, **inputDict)

    def test_compare_device_detail_internal_risk(self, sitetest, sitecompare, sitetenantid, input_device_risk):
        inputDict = input_device_risk
        inputDict["deviceid"] = device_id_risk
        inputDict["tenantid"] = tenantid

        if not checkTimeGreaterThan(inputDict["stime"], seconds=3600*25):
            pytest.skip("Skipping for 2hours and 1 day, since might not have traffic data")

        checkData = True
        genericCompareFunc(sitetest, sitecompare, sitetenantid, req.iot_device_internal_risk, checkData, **inputDict)


class Test_Application_Detail:

    def test_compareApplicationDetailStat(self, sitetest, sitecompare, sitetenantid):
        inputDict = {}
        inputDict["appid"] = appid
        inputDict["tenantid"] = tenantid

        checkData = True
        ignore = ["datetime"]
        CompareWithIgnore(sitetest, sitecompare, sitetenantid, req.iotAppDetailStat, checkData, ignore, **inputDict)


    def test_compareApplicationDetailActivity(self, sitetest, sitecompare, sitetenantid, inputApplicationDetail):
        inputDict = inputApplicationDetail
        inputDict["appid"] = appid
        inputDict["tenantid"] = tenantid

        checkData = True
        genericCompareFunc(sitetest, sitecompare, sitetenantid, req.iotAppDetail, checkData, **inputDict)


    def test_compareApplicationDetailSeries(self, sitetest, sitecompare, sitetenantid, inputApplicationDetail):
        inputDict = inputApplicationDetail
        inputDict["appid"] = appid
        inputDict["tenantid"] = tenantid

        checkData = True
        ignore = ["datetime"]
        CompareWithIgnore(sitetest, sitecompare, sitetenantid, req.iotAppDetailSeries, checkData, ignore, **inputDict)


    @pytest.mark.skipif(os.environ["NODE_ENV"] not in ["production"], reason="Sankey chart too slow to load on testing/staging")
    def test_compareApplicationDetailSankeyChart(self, sitetest, sitecompare, sitetenantid, inputApplicationDetail):
        inputDict = inputApplicationDetail
        inputDict["appid"] = appid
        inputDict["tenantid"] = tenantid

        # skipping test for 1month or greater.  We need to remove this once performance bug is fixed.
        if checkTimeGreaterThan(inputDict["stime"], seconds=3600*24*30):
            pytest.skip("Until bug fix, skipping test for timerange 6months")

        checkData = True
        ignore = ["number"]
        CompareWithIgnore(sitetest, sitecompare, sitetenantid, req.iotAppDetailNetworkMapping, checkData, ignore, **inputDict)


    @pytest.mark.skipif(os.environ["NODE_ENV"] not in ["production"], reason="App Detail Geo Usage too slow to load on testing/staging")
    def test_compareApplicationDetailGeoUsage(self, sitetest, sitecompare, sitetenantid, inputApplicationDetail):
        inputDict = inputApplicationDetail
        inputDict["appid"] = appid
        inputDict["tenantid"] = tenantid

        # skipping test for 1month or greater.  We need to remove this once performance bug is fixed.
        if checkTimeGreaterThan(inputDict["stime"], seconds=3600*24*30):
            pytest.skip("Until bug fix, skipping test for timerange 6months")

        checkData = True
        ignore = ["number"]
        CompareWithIgnore(sitetest, sitecompare, sitetenantid, req.iotAppDetailGeoUsage, checkData, ignore, **inputDict)
 

    @pytest.mark.skipif(os.environ["NODE_ENV"] not in ["production"], reason="Application Detail Network too slow to load on testing/staging")
    def test_compareApplicationDetailNetwork(self, sitetest, sitecompare, sitetenantid, inputApplicationDetail):
        inputDict = inputApplicationDetail
        inputDict["appid"] = appid
        inputDict["tenantid"] = tenantid

        # skipping test for 1month or greater.  We need to remove this once performance bug is fixed.
        if checkTimeGreaterThan(inputDict["stime"], seconds=3600*24*30):
            pytest.skip("Until bug fix, skipping test for timerange 6months")

        checkData = True
        genericCompareFunc(sitetest, sitecompare, sitetenantid, req.iotAppDetailGeoInfo, checkData, **inputDict)



class Test_Customer_Detail:

    #@pytest.mark.skip(reason="License has not been deployed in production")
    def test_compareLicense(self, sitetest, sitecompare, sitetenantid):
        inputDict = {}
        inputDict["tenantid"] = tenantid

        checkData = True
        ignore = []
        CompareWithIgnore(sitetest, sitecompare, sitetenantid, req.aboutGetLicense, checkData, ignore, **inputDict)


    def test_userSettings(self, sitetest, sitecompare, sitetenantid):
        inputDict = {}
        inputDict["tenantid"] = tenantid

        checkData = True
        ignore = []
        CompareWithIgnore(sitetest, sitecompare, sitetenantid, req.userSettings, checkData, ignore, **inputDict)

class Test_Internal_API:

    def test_onboardingGetImageList(self, sitetest, sitecompare, sitetenantid):
        inputDict = {}
        inputDict["tenantid"] = tenantid
        checkData = True
        if inputDict["tenantid"] == "soho":
            inputDict["tenantid"] = "baycare"
        ignore = []
        CompareWithIgnore(sitetest, sitecompare, sitetenantid, req.internalOnboardingGetImageList, checkData, ignore, **inputDict)

    @pytest.mark.bugs #AP-6617
    def test_onboardingGetImageOrder(self, sitetest, sitecompare, sitetenantid):
        inputDict = {}
        inputDict["dryrun"] = "{type: 'string', required: false, enum: [\"true\",\"false\"]}"
        inputDict["tenantid"] = "soho" #"KTKdJPQheZ2a_d_Dkgbv8r7kqKHQnoVb"
        checkData = True
        ignore = []
        CompareWithIgnore(sitetest, sitecompare, sitetenantid, req.internalOnboardingGetImageOrder, checkData, ignore, **inputDict)

    def test_onboardingInternalTenantId(self, sitetest, sitecompare, sitetenantid):
        inputDict = {}
        inputDict["internaltenantid"] = os.environ["ZBAT_TENANT_INTERNAL_ID"]
        checkData = True
        ignore = []
        CompareWithIgnore(sitetest, sitecompare, sitetenantid, req.onboardingCheckInternalTenantId, checkData, ignore, **inputDict)

    def test_tenantMapping(self, sitetest, sitecompare, sitetenantid):
        inputDict = {}
        inputDict["tenantid"] = tenantid
        checkData = True
        ignore = []
        CompareWithIgnore(sitetest, sitecompare, sitetenantid, req.tenantMapping, checkData, ignore, **inputDict)

    def test_tenantReverseMapping(self, sitetest, sitecompare, sitetenantid):
        inputDict = {}
        if os.environ["NODE_ENV"] == "production":
            inputDict["internaltenantid"] = os.environ["ZBAT_PRODUCTION_TENANT_INTERNAL_ID"]
        elif os.environ["NODE_ENV"] == "testing":
            inputDict["internaltenantid"] = os.environ["ZBAT_TENANT_INTERNAL_ID"]
        elif os.environ["NODE_ENV"] == "staging":
            inputDict["internaltenantid"] = os.environ["ZBAT_STAGING_TENANT_INTERNAL_ID"]
        checkData = True
        ignore = []
        CompareWithIgnore(sitetest, sitecompare, sitetenantid, req.tenantReverseMapping, checkData, ignore, **inputDict)

    def test_tenants(self, sitetest, sitecompare, sitetenantid):
        inputDict = {}
        inputDict["tenantid"] = "all"

        checkData = True
        ignore = []
        CompareWithIgnore(sitetest, sitecompare, sitetenantid, req.tenants, checkData, ignore, **inputDict)

    def test_getSiteIdMap(self, sitetest, sitecompare, sitetenantid):
        inputDict = {}
        checkData = True
        ignore = []
        CompareWithIgnore(sitetest, sitecompare, sitetenantid, req.getSiteIdMap, checkData, ignore, **inputDict)
        
    def test_getFlaggedDests(self, sitetest, sitecompare, sitetenantid):
        inputDict = {}
        checkData = True
        ignore = []
        CompareWithIgnore(sitetest, sitecompare, sitetenantid, req.getFlaggedDests, checkData, ignore, **inputDict)
