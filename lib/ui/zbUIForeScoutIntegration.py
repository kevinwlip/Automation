#!/usr/bin/python

from urllib.parse import urlparse
from ui.login.zbUILoginCore import Login
from ui.zbUIShared import waitLoadProgressDone
from ui.zbUIAssetManagement import sendKey
from zbAPI import Ops
import time, pdb, time, json

CSS_FORESCOUT_EDIT = "[config-name='forescout'] .material-icons"
CSS_FORESCOUT_SAVE = "[config-name='forescout'] .md-primary.md-raised"

CSS_FORESCOUT_HOST = "[config-name='forescout'] .md-input[placeholder='IP Address or Hostname']"
CSS_FORESCOUT_USER = ".md-input[placeholder='Your Forescout Username']"
CSS_FORESCOUT_ACCOUNT = ".md-input[placeholder='Your Forescout Account']"
CSS_FORESCOUT_PWD = ".md-input[placeholder='Your Forescout Password']"
CSS_FORESCOUT_INSPECTOR_DROPDOWN = "[config-name='forescout'] md-select.inspector-select"
CSS_FORESCOUT_INSPECTORS = ".md-clickable md-option.ng-scope[ng-value='inspector.inspectorid'] div.md-text.ng-binding"

CSS_FORESCOUT_UI_HOST_LINES = "[config-name='forescout'] [aria-hidden='false'] .ng-scope .ng-binding.property-value[aria-hidden='false']" #"[config-name='forescout'] .config-page p.ng-binding.property-value[ng-show='field.visibility'][ng-bind='field.model'][aria-hidden='false']"

req = Ops()


def configure_forescout(browserobj, **kwargs):
    _edit_configuration(browserobj)
    _configure_forescout_host(browserobj, kwargs["forescout_host"])
    _configure_forescout_username(browserobj, kwargs["forescout_user"])
    _configure_forescout_account(browserobj, kwargs["forescout_account"])
    _configure_forescout_password(browserobj, kwargs["forescout_pwd"])
    test = _configure_forescout_forwarding_inspector(browserobj, kwargs["inspector"])
    _save_configuration(browserobj)
    return test

def _edit_configuration(browserobj):
    #click edit
    forescout_edit = browserobj.findSingleCSS(selector=CSS_FORESCOUT_EDIT, timeout=3)
    if forescout_edit is not None:
        forescout_edit.click()

def _configure_forescout_host(browserobj, fs_host):
    #input host into CSS_FORESCOUT_HOST
    sendKey(browserobj, CSS_FORESCOUT_HOST, fs_host)

def _configure_forescout_username(browserobj, fs_user):
    #input username into CSS_FORESCOUT_USER
    sendKey(browserobj, CSS_FORESCOUT_USER, fs_user)

def _configure_forescout_account(browserobj, fs_account):
    #input account into CSS_FORESCOUT_ACCOUNT
    sendKey(browserobj, CSS_FORESCOUT_ACCOUNT, fs_account)

def _configure_forescout_password(browserobj, fs_pwd):
    #input password into CSS_FORESCOUT_PWD
    sendKey(browserobj, CSS_FORESCOUT_PWD, fs_pwd)

def _configure_forescout_forwarding_inspector(browserobj, inspector):
    #set dropdown from CSS_FORESCOUT_INSPECTOR_DROPDOWN
    browserobj.click(selector=CSS_FORESCOUT_INSPECTOR_DROPDOWN)
    rcode = browserobj.findMultiCSS(selector=CSS_FORESCOUT_INSPECTORS)
    if not rcode:
        raise Exception("zbUIAssetManagement/selectInspector: Asset Management cannot find inspector " + str(inspector))
    for insp in rcode:
        if inspector.strip() in insp.text.strip():
            test = str(insp.text.strip())
            insp.click()
            time.sleep(1)
            return test
    raise Exception("zbUIAssetManagement/selectInspector: Unable to find target inspector " + str(inspector))

def _save_configuration(browserobj):
    #click save
    browserobj.click(selector=CSS_FORESCOUT_SAVE)



class ForeScoutIntegration():

    def __init__(self, **kwargs):
        #delete previous configuration
        self.params = kwargs
        self.selenium = Login(**kwargs).login()

        rcode = self.selenium.getURL(kwargs["url"]+'/')
        if rcode: waitLoadProgressDone(self.selenium)

    def go_to_forescout(self, **kwargs):
        req.delete_request(kwargs['tenantid'], 'forescout', kwargs['site'])

        url = urlparse(self.params["url"])
        rcode = self.selenium.getURL(url.scheme+'://'+url.netloc+'/administration/integrations/networkAccessControl')

    def verify_forescout_configuration(self, **kwargs):
        self.go_to_forescout(**kwargs)
        browserobj = self.selenium
        test = configure_forescout(browserobj, **kwargs)
        hostlines = browserobj.findMultiCSS(selector=CSS_FORESCOUT_UI_HOST_LINES)
        verify_host = hostlines[0].text
        verify_inspector = hostlines[1].text
        if kwargs["forescout_host"] in str(verify_host) and verify_inspector in str(test):
            return True
        return False

    def close(self):
        if self.selenium:
            self.selenium.quit()

# def test_delete():
#     tenant_id = 'testing-soho'
#     system_type = 'forescout'
