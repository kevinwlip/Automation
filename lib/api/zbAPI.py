#!/usr/bin/python

#######################################################################################
#  Author : Vinh Nguyen
#    Date : 3/18/17
#######################################################################################

import pdb, requests, jsondiff, json, re, os, sys
from datetime import datetime
from requests_toolbelt import MultipartEncoder
from common.zbHTTP import zbHTTP
from common.zb_logging import logger as logging
if sys.version_info < (3, 0):
    from ordereddict import OrderedDict
else:
    from collections import OrderedDict



class zbAPI(zbHTTP):

    '''
    Example:
        Class to do ZingBox's API related queries

        Note to update auth token when it expires.  
        Config at https://github.com/ZingBox/zingcloud/blob/master/nodejs/https/server/config/az-staging.yml 

    Attributes:

    '''

    def __init__(self, **kwargs):
        self.dict = {}
        self.dict["protocol"] = "https" if not "protocol" in kwargs else "http"
        if not "host" in kwargs:  
            self.dict["host"] = "staging.zingbox.com"
        else:
            self.dict["host"] = kwargs["host"]
        if not "version" in kwargs:  self.dict["version"] = "v0.3"
        if not "path" in kwargs:  self.dict["path"] = "api"

        zbHTTP.__init__(self, **self.dict)


    def _getAdminToken(self, host):
        if "testing" in host or "azure" in host:
            return os.environ['ZBAT_TEST_API_TOKEN']
        elif "dev0" in host and "cloud" in host:
            return os.environ['ZBAT_TEST_API_TOKEN']
        elif "staging" in host:
            return os.environ['ZBAT_STAGING_API_TOKEN']
        else:
            return os.environ['ZBAT_PROD_API_TOKEN']
            

    def _execApiCall(self, host, route, method='get', **kwargs):
        host = self.dict["host"] if not host else host
        url = self.dict["protocol"]+"://"+host+"/"+self.dict["version"]+"/"+route
        kwargs["auth"] = self._getAdminToken(host)
        print (kwargs)
        if method == 'get':
            return self.get(url, **kwargs)
        if method == 'post':
            return self.post(url, **kwargs)
        if method == 'delete':
            return self.delete(url, **kwargs)


    def topDevices(self, host=None, **kwargs):
        return self._execApiCall(host, "api/dashboard/devagg", **kwargs)


    def deviceSeries(self, host=None, **kwargs):
        return self._execApiCall(host, "api/dashboard/devseries", **kwargs)


    def topAppsProtocol(self, host=None, **kwargs):
        return self._execApiCall(host, "api/dashboard/appagg", **kwargs)


    def appSeries(self, host=None, **kwargs):
        return self._execApiCall(host, "api/dashboard/appseries", **kwargs)


    def riskAssessment(self, host=None, **kwargs):
        return self._execApiCall(host, "api/dashboard/stat", **kwargs)


    def networkSummary(self, host=None, **kwargs):
        return self._execApiCall(host, "api/dashboard/seriesagg", **kwargs)


    def deviceSubnet(self, host=None, **kwargs):
        return self._execApiCall(host, "api/dashboard/distribution", **kwargs)


    def trafficSeries(self, host=None, **kwargs):
        return self._execApiCall(host, "api/dashboard/series", **kwargs)
 

    def deviceCategory(self, host=None, **kwargs):
        return self._execApiCall(host, "api/dashboard/distribution", **kwargs)
 

    def deviceSummary(self, host=None, **kwargs):
        return self._execApiCall(host, "api/dashboard/devicesummary", **kwargs)
 

    def networkDestination(self, host=None, **kwargs):
        return self._execApiCall(host, "api/dashboard/destinationagg", **kwargs)


    def destReputation(self, host=None, **kwargs):
        return self._execApiCall(host, "api/dashboard/destinationreputation", **kwargs)


    def reportDownload(self, host=None, **kwargs):
        return self._execApiCall(host, "api/report/download", **kwargs)


    def otDeviceStat(self, host=None, **kwargs):
        return self._execApiCall(host, "api/otdashboard/stat", **kwargs)


    def otDeviceSeries(self, host=None, **kwargs):
        return self._execApiCall(host, "api/otdashboard/series", **kwargs)


    def otDeviceSeriesAgg(self, host=None, **kwargs):
        return self._execApiCall(host, "api/otdashboard/seriesagg", **kwargs)


    def otDeviceAgg(self, host=None, **kwargs):
        return self._execApiCall(host, "api/otdashboard/devagg", **kwargs)


    def otDeviceList(self, host=None, **kwargs):
        return self._execApiCall(host, "api/otdashboard/list", **kwargs)


    def whitelist(self, host=None, **kwargs):
        return self._execApiCall(host, "api/whitelist/getlist", **kwargs)


    def iotProfile(self, host=None, **kwargs):
        return self._execApiCall(host, "api/iotprofile/stats", **kwargs)


    def iotProfileCheckReport(self, host=None, **kwargs):
        return self._execApiCall(host, "api/iotdevicereport/checkreport", **kwargs)


    def iotProfileCreateReport(self, host=None, **kwargs):
        return self._execApiCall(host, "api/iotdevicereport/createreport", **kwargs)


    def iotProfileDownload(self, host=None, **kwargs):
        return self._execApiCall(host, "api/iotdevicereport/download", **kwargs)


    def iotInventorySeries(self, host=None, **kwargs):
        return self._execApiCall(host, "api/iotinventory/series", **kwargs)


    def iotInventoryList(self, host=None, **kwargs):
        return self._execApiCall(host, "api/iotinventory/list", **kwargs)


    def iotInventoryGeoDestList(self, host=None, **kwargs):
        return self._execApiCall(host, "api/iotinventory/geodestlist", **kwargs)


    def iotApplicationSeries(self, host=None, **kwargs):
        return self._execApiCall(host, "api/iotapplication/series", **kwargs)


    def iotApplicationList(self, host=None, **kwargs):
        return self._execApiCall(host, "api/iotapplication/list", **kwargs)


    def iotDeviceStat(self, host=None, **kwargs):
        return self._execApiCall(host, "api/iotdevice/stat", **kwargs)


    def iotDeviceDetail(self, host=None, **kwargs):
        return self._execApiCall(host, "api/iotdevice/seriesagg", **kwargs)


    def iotDeviceGeo(self, host=None, **kwargs):
        return self._execApiCall(host, "api/iotdevice/geoinfo", **kwargs)


    def iotDeviceNetwork(self, host=None, **kwargs):
        return self._execApiCall(host, "api/iotdevice/networkusage", **kwargs)


    def iotDeviceNetworkUsage(self, host=None, **kwargs):
        return self._execApiCall(host, "api/iotdevice/networkperiodagg", **kwargs)


    def iotDeviceNetworkMapping(self, host=None, **kwargs):
        return self._execApiCall(host, "api/iotdevice/networkmapping", **kwargs)


    def iotDeviceAnomalyMapping(self, host=None, **kwargs):
        return self._execApiCall(host, "api/iotdevice/anomalymapping", **kwargs)


    def iotAppDetail(self, host=None, **kwargs):
        return self._execApiCall(host, "api/iotappdetail/seriesagg", **kwargs)


    def iotAppDetailStat(self, host=None, **kwargs):
        return self._execApiCall(host, "api/iotappdetail/stat", **kwargs)


    def iotAppDetailSeries(self, host=None, **kwargs):
        return self._execApiCall(host, "api/iotappdetail/series", **kwargs)


    def iotAppDetailNetworkMapping(self, host=None, **kwargs):
        return self._execApiCall(host, "api/iotappdetail/networkmapping", **kwargs)


    def iotAppDetailGeoUsage(self, host=None, **kwargs):
        return self._execApiCall(host, "api/iotappdetail/geonetworkusage", **kwargs)


    def iotAppDetailGeoInfo(self, host=None, **kwargs):
        return self._execApiCall(host, "api/iotappdetail/geoinfo", **kwargs)

    def alertAssignees(self, host=None, **kwargs):
        return self._execApiCall(host, "api/alert/assignees", **kwargs)

    def alertRetrieve(self, host=None, **kwargs):
        return self._execApiCall(host, "api/alert/retrieve", **kwargs)


    def alertStat(self, host=None, **kwargs):
        return self._execApiCall(host, "api/alert/stat", **kwargs)


    def alertChartStat(self, host=None, **kwargs):
        return self._execApiCall(host, "api/alert/chartStat", **kwargs)


    def alertFeeds(self, host=None, **kwargs):
        return self._execApiCall(host, "api/alert/feeds", **kwargs)

    
    def alerts(self, host=None, **kwargs):
        return self._execApiCall(host, "api/alerts", method='post', **kwargs)

    
    def siteInspectorList(self, host=None, **kwargs):
        return self._execApiCall(host, "api/site/list", **kwargs)


    def siteInspectorSimpleList(self, host=None, **kwargs):
        return self._execApiCall(host, "api/site/simplelist", **kwargs)


    def inspectorDetail(self, host=None, **kwargs):
        return self._execApiCall(host, "api/inspector/tenantinspectors", **kwargs)


    def inspectorCpuMem(self, host=None, **kwargs):
        return self._execApiCall(host, "api/inspector/cpumem", **kwargs)


    def inspectorTrafficTrend(self, host=None, **kwargs):
        return self._execApiCall(host, "api/inspector/getTrafficTrend", **kwargs)


    def getTenantBlacklist(self, host=None, **kwargs):
        return self._execApiCall(host, "api/gettenantblacklist", **kwargs)


    def setTenantBlacklist(self, host=None, **kwargs):
        return self._execApiCall(host, "api/settenantblacklist", **kwargs)


    def auditLogs(self, host=None, **kwargs):
        return self._execApiCall(host, "zauth/logEvents", **kwargs)


    def msspPortalProfile(self, host=None, **kwargs):
        return self._execApiCall(host, "zauth/profile", **kwargs)


    def msspPortalGetTenant(self, host=None, **kwargs):
        return self._execApiCall(host, "api/tenants", **kwargs)


    def msspPortalTenantSummary(self, host=None, **kwargs):
        return self._execApiCall(host, "proxy/tenant/summary", **kwargs)


    def msspPortalTenantSelectedSummary(self, host=None, **kwargs):
        return self._execApiCall(host, "proxy/tenant/selectedsummary", **kwargs)


    def msspPortalTenantStat(self, host=None, **kwargs):
        return self._execApiCall(host, "api/channel/distributor/tenantstat", **kwargs)


    def msspPortalGetReseller(self, host=None, **kwargs):
        return self._execApiCall(host, "api/channel/reseller", **kwargs)


    def msspPortalDistributorTenants(self, host=None, **kwargs):
        return self._execApiCall(host, "api/channel/distributor/tenants", **kwargs)


    def msspPortalDistributorResellers(self, host=None, **kwargs):
        return self._execApiCall(host, "api/channel/distributor/resellers", **kwargs)


    def aboutGetLicense(self, host=None, **kwargs):
        return self._execApiCall(host, "api/about/getLicense", **kwargs)

    def userSettings(self, host=None, **kwargs):
        return self._execApiCall(host, "api/settings/tenant/users", **kwargs)

#New ones

    def internalOnboardingGetImageList(self, host=None, **kwargs):
        return self._execApiCall(host, "api/onboarding/getImageList", **kwargs)

    def internalOnboardingGetImageOrder(self, host=None, **kwargs):
        return self._execApiCall(host, "api/onboarding/getImageOrder", **kwargs)

    def onboardingCheckInternalTenantId(self, host=None, **kwargs):
        return self._execApiCall(host, "api/onboarding/checkInternaltenantid", **kwargs)

    def tenantMapping(self, host=None, **kwargs):
        return self._execApiCall(host, "api/tenantmapping", **kwargs)

    def tenantReverseMapping(self, host=None, **kwargs):
        return self._execApiCall(host, "api/tenantReverseMapping", **kwargs)

    def third_party_config(self, host=None, **kwargs): #add api tes in Ops?
        return self._execApiCall(host, "api/thirdparty/config", **kwargs)

    def delete_third_party_config(self, host=None, **kwargs):
        return self._execApiCall(host, "api/thirdparty/config", method='delete', **kwargs)

    def thirdparty_all_config(self, host=None, **kwargs):
        return self._execApiCall(host, "api/thirdparty/allconfig", **kwargs)

    def tenants(self, host=None, **kwargs):
        return self._execApiCall(host, "api/tenants", **kwargs)

    def getSiteIdMap(self, host=None, **kwargs):
        return self._execApiCall(host, "api/getSiteIdMap", **kwargs)

    def getFlaggedDests(self, host=None, **kwargs):
        return self._execApiCall(host, "api/getFlaggedDests", **kwargs)
     
    def iot_device_risk(self, host=None, **kwargs):
        return self._execApiCall(host, "api/iotdevice/risk/retrieve", **kwargs)

    def iot_device_internal_risk(self, host=None, **kwargs):
        return self._execApiCall(host, "api/iotdevice/internalRisk/retrieve", **kwargs)

    def ot_dashboard_iv_series(self, host=None, **kwargs):
        return self._execApiCall(host, "api/ivdashboard/series", **kwargs)

    def set_snmp_configuration(self, host=None, **kwargs):
        return self._execApiCall(host, "api/thirdparty/config", method='post', **kwargs)

    def executiveApplication(self, host=None, **kwargs):
        return self._execApiCall(host, "api/execdashboard/application", **kwargs)

    def executiveSecuritySeries(self, host=None, **kwargs):
        return self._execApiCall(host, "api/execdashboard/securityseries", **kwargs)

    def executiveSecurityDistribution(self, host=None, **kwargs):
        return self._execApiCall(host, "api/execdashboard/securitydistribution", **kwargs)

    def executiveDistribution(self, host=None, **kwargs):
        return self._execApiCall(host, "api/execdashboard/distribution",**kwargs)

    def executiveStat(self, host=None, **kwargs):
        return self._execApiCall(host, "api/execdashboard/stat",**kwargs)

    def executiveVulnDistribution(self, host=None, **kwargs):
        return self._execApiCall(host, "api/execdashboard/vulnerabilitydistribution",**kwargs)

    def executiveVulnStat(self, host=None, **kwargs):
        return self._execApiCall(host, "api/execdashboard/vulnerabilitystat",**kwargs)

    def executiveVulnList(self, host=None, **kwargs):
        return self._execApiCall(host, "api/execdashboard/vulnerabilitylist",**kwargs)

    def alertSankeyChart(self, host=None, **kwargs):
        return self._execApiCall(host, "api/alert/sankeyChart",**kwargs)


class Ops():

    '''
    Example:
        Class that contains common operations that is perform on API results

    Attributes:
        ignore can take value of "datetime"

    '''

    def __init__(self):
        pass

    # Compare:  return True is result match, False if not
    def compare(self, r1, r2, ignore=[], strict=True):
        
        # make sure that response is not error http code
        if isinstance(r1, int):
            if int(r1) != 200:
                logging.error("Received invalid {} code".format(r1))
                return False
        if isinstance(r2, int):
            if int(r2) != 200:
                logging.error("Received invalid {} code".format(r2))
                return False        

        if False == strict:
            return True

        try:
            r1 = json.loads(r1, object_pairs_hook=OrderedDict)
            r2 = json.loads(r2, object_pairs_hook=OrderedDict)
        except TypeError as e:
            if type(r1) == dict and type(r2) == dict:
                pass
            else:
                logging.error("Unable to parse data.  Got error {0}".format(e))
        except Exception as e:
            logging.error("Unable to parse data.  Got error {0}".format(e))
            return False

        if r1 == r2:
            return True
        else:
            r1Text = str(r1)
            r2Text = str(r2)

            # closer inspection to see if there is a mismatch.  Unique sort and compare.
            diff = set(sorted(r1Text.split())) - set(sorted(r2Text.split()))
            if len(diff) > 0:
                # go through things that can be ignored
                realdiff = []
                for item in diff:
                    matched = False

                    for ig in ignore:
                        if ig == "datetime": rp = r'\d{4}-\d{2}-\d{2}(T|\ )\d{2}:\d{2}:\d{2}'
                        if ig == "number": rp = r'\d+[\)\]\,]*'
                        if ig == "url": rp = r'[\w\.]+'
                        p = re.compile(rp)
                        m = p.search(item)
                        if m: matched = True
                    # if didn't match anything in ignore list, then it's a real valid diff
                    if not matched: realdiff.append(item)

                if len(realdiff) > 0:
                    logging.error("Data not matching at {0}".format(realdiff))
                    return False

            logging.info("Originally found mismatch, but after closer inspection, it is a false alarm")
            return True

    def dataExist(self, data, strict=True):
        try:
            dataJson = json.loads(data)
        except Exception as e:
            logging.error("Unable to parse {0}".format(data))
            logging.error("Got error {}".format(e))
            return False

        # if strict Flag is not on, then return True if there are any valid data
        if not strict:
            if any(dataJson): return True

        if "agg" in dataJson:
            cValue = 1
            if "topmaliciousdestinaions" in dataJson["agg"]:
                if len(dataJson["agg"]["topmaliciousdestinaions"]) >= cValue:
                    return True
                else:
                    logging.error("agg data {0} got issue, length less-than-or-equal to ".format(cValue))
                    return False

            if len(dataJson["agg"]) >= cValue:
                return True
            else:
                logging.error("agg data {0} got issue, length less-than-or-equal to {1}".format(data, cValue))

        if "list" in dataJson:
            cValue = 1
            if len(dataJson["list"]) >= cValue:
                return True
            else:
                logging.error("list data {0} got issue, length less-than-or-equal to {1}".format(data, cValue))

        if "series" in dataJson:
            cValue = 1
            if len(dataJson["series"]["data"]) >= cValue:
                return True
            else:
                logging.error("series data {0} got issue, length less-than-or-equal to {1}".format(data, cValue))

        if "items" in dataJson:
            cValue = 1
            if len(dataJson["items"]) >= cValue:
                return True
            else:
                logging.error("items data {0} got issue, length less-than-or-equal to {1}".format(data, cValue))

        if "distributions" in dataJson:
            cValue = 1
            if len(dataJson["distributions"]) >= cValue:
                return True
            else:
                logging.error("distributions data {0} got issue, length less-than-or-equal to {1}".format(data, cValue))

        if "inspectors" in dataJson:
            cValue = 1
            if len(dataJson["inspectors"]) >= cValue:
                return True
            else:
                logging.error("Inspector data {0} got issue, length less-than-or-equal to {1}".format(data, cValue))

        if "stat" in dataJson:
            if any(dataJson):
                return True
            else:
                logging.error("Stat data {0} does not have any values.".format(data))

        if "geo_location" in dataJson:
            if any(dataJson["geo_location"]):
                return True
            else:
                logging.error("geo_location data {0} does not have any values.".format(data))

        if "networkusage" in dataJson:
            cValue = 1
            if len(dataJson["networkusage"]) >= cValue:
                return True
            else:
                logging.error("networkusage data {0} does not have any values.".format(data))

        if "periodagg" in dataJson:
            cValue = 1
            if len(dataJson["periodagg"]) >= cValue:
                return True
            else:
                logging.error("periodagg data {0} does not have any values.".format(data))

        if "network_connectivity" in dataJson:
            cValue = 1
            if "geo_ip_mapping" in dataJson["network_connectivity"]:
                if len(dataJson["network_connectivity"]["geo_ip_mapping"]) >= cValue:
                    return True
            if "subnet_geo_mapping" in dataJson["network_connectivity"]:
                if len(dataJson["network_connectivity"]["subnet_geo_mapping"]) >= cValue:
                    return True
            logging.error("sankey chart {0} does not have any values.".format(data))

        if "products" in dataJson:
            cValue = 1
            if len(dataJson["products"]) >= cValue:
                return True
            else:
                logging.error("About section not returning any product data.")

        if "alerts" in dataJson:
            if isinstance(dataJson["alerts"], list):
                return True
            else:
                logging.error("Alert feeds not returning any alert data")

        if "tenant_num" in dataJson:
            if isinstance(dataJson["tenant_num"], int):
                return True

        if "cloud_traffic" in dataJson:
            if isinstance(dataJson["cloud_traffic"], list):
                return True
            else:
                logging.error("Inspector traffic trend does not returning any cloud traffic data.")

        if "mapping" in dataJson:
            mapping = dataJson['mapping']
            if 'application' in mapping and \
                'protocol' in mapping and \
                'internal' in mapping and \
                'external' in mapping and \
                'payload' in mapping:
                return True
            else:
                logging.error("Anomaly map is missing some required keys.")

        if "settings" in dataJson:
            if isinstance(dataJson["settings"], dict):
                return True
            else:
                logging.error("Setting does not return any data")

        if "assignees" in dataJson:
            if isinstance(dataJson["assignees"], list):
                return True
            else:
                logging.error("Alert assignees not returning any alert assignee data")

        if "conf" in dataJson:
            cValue = 1
            if len(dataJson["conf"]) >= cValue:
                return True
            else:
                logging.error("Integration config {0} does not have any values.".format(data))

        if len(dataJson) >= 6:
            return True

        if "imageList" in dataJson:
            if any(dataJson):
                return True
            else:
                logging.error("Imagelist data {0} does not have any values.".format(data))

        if "isUnique" in dataJson:
            if any(dataJson):
                return True
            else:
                logging.error("Internal tenant id data {0} does not have any values.".format(data))

        if "internaltenantid" in dataJson:
            if os.environ["NODE_ENV"] == "production":
                internal_id = os.environ["ZBAT_PRODUCTION_TENANT_INTERNAL_ID"]
            elif os.environ["NODE_ENV"] == "testing":
                internal_id = os.environ["ZBAT_TENANT_INTERNAL_ID"]
            elif os.environ["NODE_ENV"] == "staging":
                internal_id = os.environ["ZBAT_STAGING_TENANT_INTERNAL_ID"]
            print (os.environ["ZBAT_TENANT_INTERNAL_ID"])
            if(dataJson["api"] == "tenantmapping" and dataJson["internaltenantid"] == internal_id):
                return True
            else:
                logging.error("Tenant mapping data {0} is missing.".format(data))

        if "externaltenantid" in dataJson:
            if(dataJson["api"] == "tenantReverseMapping" and dataJson["externaltenantid"] != ""):
                return True
            else:
                logging.error("Tenant mapping data {0} is missing.".format(data))

        if "sites" in dataJson:
            if(len(dataJson["sites"]) > 0 and dataJson["api"] == "getSiteIdMap"):
                return True
            else:
                logging.error("Site ID Mapping is missing.")

        if "dests" in dataJson:
            if("host" in dataJson["dests"][0] and "flag" in dataJson["dests"][0] and "description" in dataJson["dests"][0]):
                return True
            else:
                logging.error("Flagged destinations is not returning correctly.")

        if "application" in dataJson:
            cValue = 1
            if len(dataJson["application"]) >= cValue:
                return True
            else:
                logging.error("Application data {0} does not have any values.".format(data))

        if "distribution" in dataJson:
            cValue = 1
            if len(dataJson["distribution"]) >= cValue:
                return True
            else:
                logging.error("Distribution data {0} does not have any values.".format(data))

        if "securityDistribution" in dataJson:
            cValue = 1
            if len(dataJson["securityDistribution"]) >= cValue:
                return True
            else:
                logging.error("Security Distribution data {0} does not have any values.".format(data))
                
        if "securitySeries" in dataJson:
            cValue = 1
            if len(dataJson["securitySeries"]) >= cValue:
                return True
            else:
                logging.error("Security Series data {0} does not have any values.".format(data))

        if "vulnerabilitystat" in dataJson:
            cValue = 1
            if len(dataJson["vulnerabilitystat"]) >= cValue:
                return True
            else:
                logging.error("Vulnerability Stat data {0} does not have any values.".format(data))

        if "vulnerabilitylist" in dataJson:
            cValue = 1
            if len(dataJson["vulnerabilitylist"]) >= cValue:
                return True
            else:
                logging.error("Vulnerability List data {0} does not have any values.".format(data))

        if "vulnerabilitydistribution" in dataJson:
            cValue = 1
            if len(dataJson["vulnerabilitydistribution"]) >= cValue:
                return True
            else:
                logging.error("Vulnerability Distribution data {0} does not have any values.".format(data))


        print("CANCER: " + str(dataJson) )
        return False


    def timeCompare(self, t1, t2, maxDiffPerc=15, minImprovement=0, strict=True):
        '''
        t1 is time of the improved build
        t2 is from baseline build
        '''
        # skip if strict is False
        if False == strict:
            return True
        
        # if both time are sub 5 seconds, it's good enough, and does not need to be compared.
        if t1 <= 1 and t2 <= 1:
            return True
            
        if t1 <= t2:
            diffPercentage = int(round(((t2-t1)/t2)*100))
            if int(minImprovement) > diffPercentage:
                logging.error("Time t1 {0}, t2 {1}, improve {2} percent, not meet requirement of {3} percent.".format(t1, t2, diffPercentage, minImprovement))
                return False

            return True
        else:
            diffPercentage = int(round(((t1-t2)/t2)*100))
            if int(maxDiffPerc) >= diffPercentage:
                return True
            else:
                logging.error("Time t1 {0} slower than t2 {1} by {2} percent, not meet requirement of {3} percent variation.".format(t1, t2, diffPercentage, maxDiffPerc))
                return False

    def delete_request(self, tenantid, system_type, host):
        delete_config = {
                'tenantid':tenantid,
                'system_type':system_type
                }

        rcode = zbAPI().delete_third_party_config(host=host, **delete_config)
        if 'thirdparty/removeThirdPartyConf' not in rcode:
            print("failed to remove {0} configuration".format(system_type))
        else: print("Reset {0} configuration".format(system_type))

        rcode = zbAPI().third_party_config(host=host, **delete_config)
        if not json.loads(rcode)['conf']:
            print("Reset {0} configuration successful".format(system_type))
        else: print("Configuration not reset")
'''
#test
kwargs = {
    "direction": "all",
    "stime": "2017-03-09T23:07",
    "etime": "now",
    "filter_monitored": "yes",
    "interval": "day",
    "outputtype": "destination",
    "tenantid": "baycare"
}

req = zbAPI()
ts = datetime.now()
j1 = json.loads(req.topDevicesDestination(**kwargs))
tt = (datetime.now() - ts).total_seconds()
print (tt)
'''
