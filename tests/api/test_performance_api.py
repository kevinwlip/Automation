#!/usr/bin/python

import pdb, json, sys, os, pytest
from datetime import datetime

try:
    env = os.environ['ZBAT_HOME']
except:
    print 'Test cannot run.  Please export ZBAT_HOME.'
    sys.exit()

if env+'lib' not in sys.path:
    sys.path.append(env+'lib')
    
from zbConfig import defaultEnv
from common.zbJmeter import zbJmeter

# To add test, just add the profile to Jmeter script Perf_All_API.jmx, and enter in test attributes here
commonLatency = "5"
longLatency = "10"
minBodySize = "200"
testattr = {
    "DashboardProfile": {"jmeterName":"ip", "maxLatency":commonLatency, "minBodySize":minBodySize},
    "DashboardSeries": {"jmeterName":"ds", "maxLatency":commonLatency, "minBodySize":minBodySize},
    "RiskAssessment": {"jmeterName":"ra", "maxLatency":commonLatency, "minBodySize":minBodySize},
    "NetworkSummary": {"jmeterName":"ns", "maxLatency":commonLatency, "minBodySize":minBodySize},
    "DeviceSubnetVLAN": {"jmeterName":"dv", "maxLatency":commonLatency, "minBodySize":"150"},
    "ExternalEndpoint": {"jmeterName":"ee", "maxLatency":commonLatency, "minBodySize":"100"},
    "TopDevices": {"jmeterName":"td", "maxLatency":longLatency, "minBodySize":minBodySize},
    "TopApplications": {"jmeterName":"ta", "maxLatency":commonLatency, "minBodySize":"150"},
    "DeviceInventorySeries": {"jmeterName":"is", "maxLatency":commonLatency, "minBodySize":minBodySize},
    "DeviceInventorySankeyChart": {"jmeterName":"dis", "maxLatency":longLatency, "minBodySize":"1000"},
    "DeviceInventoryUniqDest": {"jmeterName":"did", "maxLatency":longLatency, "minBodySize":minBodySize},
    "DeviceInventoryApplications": {"jmeterName":"dia", "maxLatency":longLatency, "minBodySize":minBodySize}
}

# common variables
#==========================================================
env = defaultEnv()
dut = env["siteTest"]
tenantid = env["tenantid"]
timestrict = env["timestrict"]
comparestrict = env["comparestrict"]

jmeterScript = env["zbat_home"]+"3p/jmeter/Perf_All_API.jmx"
jmeterLogLoc = env["zbat_home"]+"3p/jmeter/log/"

if os.environ['NODE_ENV'] == "testing": 
    authToken = os.environ['ZBAT_TEST_API_TOKEN'].split()
    authToken = authToken[1]
else:
    authToken = os.environ['ZBAT_PROD_API_TOKEN'].split()
    authToken = authToken[1]


# pytest fixtures
#=============================================
@pytest.fixture()
def jmeter():
    obj = zbJmeter()
    return obj


# pytests
#==============================================
class Test_Latency:

    pytestmark = [pytest.mark.perftest, pytest.mark.slowtest]

    @pytest.mark.parametrize("gettest", testattr.keys())
    def test_latency_api(self, sitetest, jmeter, gettest):
        # determine if test against site from configuration or from command line option
        testurl = sitetest if sitetest else dut

        # generating log name
        datetime.now().strftime('%s')
        jmeterLog = jmeterLogLoc+gettest+'_jmeterlog_'+str(datetime.now().strftime('%s'))+'.jtl'
        if os.path.exists(jmeterLog): os.remove(jmeterLog)
        # setting variables
        kwargs = {}
        kwargs["jmeterprofile"] = jmeterScript
        kwargs["log"] = jmeterLog
        kwargs["maxLatency"] = testattr[gettest]["maxLatency"]
        kwargs["serveroptions"] = "-JauthToken=%s" % (authToken)
        kwargs["options"] = "-Jtest-to-run=%s -Jserver=%s -Jmaxlatency=%s -Jminbodysize=%s -Jforce-etime-now=yes -Jsimuser=%s -Jiteration=%s" % (testattr[gettest]["jmeterName"], testurl, str(int(testattr[gettest]["maxLatency"])*1000), str(testattr[gettest]["minBodySize"]), "1", "1")
        # running the test, create log file
        output = jmeter.run(**kwargs)
        # parse the log file
        result = jmeter.parseXmlLog(kwargs["log"])
        # remove the log file generated from 'output'
        if os.path.exists(kwargs["log"]): os.remove(kwargs["log"])
        # verifying results
        for verdict in jmeter.checkFail(result):
            assert True == verdict["pass"], "Message "+" ".join(verdict["messages"])+"\n"+verdict["log"]
