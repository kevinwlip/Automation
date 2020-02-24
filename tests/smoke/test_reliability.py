import requests
import pytest
import os, sys, pdb
from zb_logging import logger as logging
import datetime

try:
    env = os.environ['ZBAT_HOME']
except:
    logging.critical('Test cannot run.  Please export ZBAT_HOME.')
    sys.exit()

if env+'lib' not in sys.path:
    sys.path.append(env+'lib')

from zbAPI import zbAPI, Ops
from zbConfig import defaultEnv

@pytest.mark.flaky
@pytest.mark.parametrize("tenant",["zbat4", "soho", "pinnaclehealth", "baycare", "allinahealth"])
def test_APIResponse(tenant):
    master_time = datetime.datetime.utcnow().strftime("%Y/%m/%d %H:%M")
    start_time = (datetime.datetime.utcnow() - datetime.timedelta(hours=2)).strftime("%Y/%m/%d %H:%M")
    dankheader = {}
    dankheader["Authorization"] = os.environ["ZBAT_PROD_API_TOKEN"]
    req = "https://"+tenant+".zingbox.com/v0.3/api/dashboard/devicesummary?direction=all&etime=now&filter_monitored=yes&interval=hour&stime="+start_time+"&tenantid=" + tenant
    result = requests.get(req, headers=dankheader)
    print(result)
    print("Response time: " + str(result.elapsed.total_seconds() ))
    print("Run_Date: " + master_time)
    if result.status_code >= 400:
        assert False

    assert True

