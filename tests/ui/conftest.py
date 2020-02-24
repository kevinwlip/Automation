# content of conftest.py
import sys
import os
import ast
import pytest
import pdb
import time
import shutil
import random
import copy

try:
    zbathome = os.environ['ZBAT_HOME']
    print(("ZBAT_HOME is %s" % zbathome))
except:
    print ('Test cannot run.  Please export ZBAT_HOME.')
    sys.exit()

if zbathome+'lib' not in sys.path:
    sys.path.append(zbathome+'lib')
    
from common.zbConfig import defaultEnv

#================================
# Setting up default parameters
#================================
env = defaultEnv()
uiportal = env["uiportal"]
if not uiportal: print ('UI portal value not set in zbCommon.py'); sys.exit()
seleniumhost = env["remoteSeleniumServer"]
username = env["username"]
password = env["password"]
comparestrict = env["comparestrict"]
tenantid = env["tenantid"]
siteTest = env["siteTest"]

# global variables
br = None
GLOBAL_PARAMS = {
    "url": uiportal,
    "host": seleniumhost,
    "username": username, 
    "password": password,
    "comparestrict": comparestrict
}


# hanle building up default parameters structure
@pytest.fixture(scope="module", params=['internet explorer', 'firefox', 'chrome', 'edge', 'chromeipad'])
def browser_payload(request, remoteserver, sitetest, sitetenantid, loginuser, loginpwd, uiportal):
    kwargs = copy.deepcopy(GLOBAL_PARAMS)
    kwargs['browser'] = request.param

    if remoteserver:
        kwargs['host'] = remoteserver
    if uiportal:
        if 'http' not in uiportal:
            uiportal = 'https://'+uiportal+'/login'
            kwargs['url'] = uiportal
    elif sitetest:
        # if user command line input param for sitetest is not in format of https://testing.zingbox.com/login?tenant=testing-soho
        #     then build up that string based on zbConfig config param of siteTest and tenantid
        if 'http' not in sitetest:
            sitetest = 'https://'+sitetest+'/login'
        if 'tenantid=' not in sitetest:
            if sitetenantid:
                sitetest = sitetest+'?tenantid='+sitetenantid
            else:
                sitetest = sitetest+'?tenantid='+tenantid
        kwargs['url'] = sitetest
    if loginuser: kwargs['username'] = loginuser
    if loginpwd: kwargs['password'] = loginpwd
    return kwargs
