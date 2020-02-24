#!/usr/bin/python
import sys
import os
import pytest
import copy

try:
    zbathome = os.environ['ZBAT_HOME']
except:
    print 'Test cannot run.  Please export ZBAT_HOME.'
    sys.exit()

if zbathome+'lib' not in sys.path:
    sys.path.append(zbathome+'lib')
    
from common.zbCommon import rerunIfFail
from conftest import NUMBER_RETRIES, DELAY_SECONDS, SCREENSHOT_ON_FAIL
from zbConfig import defaultEnv
from common.zbOpenVAS import OpenVAS

defaultConfig = defaultEnv()
initConfig = {'username':defaultConfig["openvasUserName"], 'password':defaultConfig["openvasPassword"], 'hostname':defaultConfig["openvasIP"], 'port':defaultConfig["openvasPort"]}
deviceDict = {"Enterprise ZingCloud Scan" : "enterprise.zingbox.com", "Enterprise Inspector Scan":"192.168.20.37"}
inputList = ["Enterprise ZingCloud Scan", "Enterprise Inspector Scan"]

class Test_OpenVAS():
    @pytest.mark.parametrize("device", inputList)
    def test_VulnScanDevices(self, device):
        test = OpenVAS()
        assert rerunIfFail(function=test.run_main({device:deviceDict[device]}, initConfig), number=NUMBER_RETRIES, delay=DELAY_SECONDS) == True


