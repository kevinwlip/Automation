#!/usr/bin/python
import time, pdb
from ui.login.zbUILoginCore import Login
from ui.zbUIShared import waitLoadProgressDone

CSS_SUBNET_ICON = '.md-toolbar-tools i.subnet-icon'
CSS_SUBNET_DOWNLOAD_BTN = "[tooltip-text='Download your Subnet Bubble']" #'.subnet-bubble ng-md-icon.table-downloader'
CSS_SUBNET_DOWNLOADED_DOM = '.subnet-bubble .zing-qa-hidden-dom'

CSS_SUBNET_ROW = '.subnet-bubble .subnet-row-content'
CSS_SUBNET_NAME = 'span.subnet-name' # Search inside CSS_SUBNET_ROW
CSS_SUBNET_VLAN_ID = '.subnet-vlan span[ng-if="subnet.vlan || subnet.updatedVlan"]' # Search inside CSS_SUBNET_ROW
CSS_SUBNET_DESCRIPTION = 'span[ng-bind="subnet.updatedVlanDescription || subnet.description"]' # Search inside CSS_SUBNET_ROW
CSS_SUBNET_EDIT_BTN = 'i.edit-pen' # Search inside CSS_SUBNET_ROW
CSS_SUBNET_CHECKBOX = 'md-checkbox[ng-model="subnet.selected"]' # Search inside CSS_SUBNET_ROW

CSS_ADD_SUBNET_PLUS_BTN = '.subnet-bubble i.add-circle'
CSS_ADD_CUSTOM_SUBNET_FIELD = '.subnet-bubble input[name="Input custom subnet name"]'
CSS_ADD_SUBNET_VLAN_ID_FIELD = '.subnet-bubble input[name="Input custom vlan name"]'
CSS_ADD_SUBNET_DESCRIPTION_FIELD = '.subnet-bubble input[name="Input custom vlan description"]'
CSS_ADD_SUBNET_SUBMIT_BTN = '.subnet-bubble .add-subnet-row button[ng-click="subnetBCtrl.add()"]'

CSS_UPDATE_SUBNET_VLAN_ID_FIELD = '.subnet-bubble input[ng-model="subnet.updatedVlan"]'
CSS_UPDATE_SUBNET_DESCRIPTION_FIELD = '.subnet-bubble input[ng-model="subnet.updatedVlanDescription"]'
CSS_UPDATE_SUBNET_SUBMIT_BTN = '.subnet-bubble button[ng-click="subnetBCtrl.triggerSubnetsWatch(subnet, false);"]'

CSS_SUBNET_DELETE_BTN = '.subnet-bubble button[ng-click="subnetBCtrl.openDeleteConfirmation();"]'
CSS_SUBNET_DELETE_NOT_MONITORED_BTN = '.subnet-bubble .bubble-header button.zing-hide-for-readonly'
CSS_SUBNET_STOP_MONITORING_BTN = '.subnet-bubble button[ng-click="subnetBCtrl.openStopMonitoringConfirmation()"]'
CSS_SUBNET_SAVE_BTN = '.subnet-bubble button[name="Save changes made"]'

CSS_CONFIRM_DELETE_BTN = '.zing-dialog button[name="Save changes made"]'
CSS_CONFIRM_STOP_MONITORING_BTN = '.zing-dialog button[ng-click="stopMonitoringConfirmationCtrl.stopMonitoring()"]'

def _verifyDownloadSubnet(browserobj):
    rcode = True
    rcode = rcode and browserobj.click(
        selector=CSS_SUBNET_DOWNLOAD_BTN,
        err_msg='zbUISubnet.py/_verifyDownloadSubnet: Not able to click download subnet button.'
    )
    rcode = rcode and browserobj.findSingleCSS(
        selector=CSS_SUBNET_DOWNLOADED_DOM,
        err_msg='zbUISubnet.py/_verifyDownloadSubnet: Not able to find downloaded indicator.'
    )
    rcode = rcode and _clickSave(browserobj)
    return rcode

def _verifyAddMonitoredSubnet(browserobj, **kwargs):
    rcode = True
    row = _findTargetRow(browserobj, **kwargs)
    if row:
        _clickSave(browserobj)
        return True
    rcode = rcode and _addSubnet(browserobj, **kwargs)
    rcode = rcode and _clickSave(browserobj)
    return rcode

def _verifyEditMonitoredSubnet(browserobj, **kwargs):
    row = _findTargetRow(browserobj, **kwargs)
    if not row:
        print(('zbUISubnet.py/_verifyEditMonitoredSubnet: Not able to find target row for subnet {}'.format(kwargs['subnet'])))
        return False
    browserobj.click(
        browserobj=row,
        selector=CSS_SUBNET_EDIT_BTN,
        err_msg='zbUISubnet.py/_verifyEditMonitoredSubnet: Not able to click edit button'
    )

    vlanInput = browserobj.findSingleCSS(
        browserobj=row,
        selector=CSS_UPDATE_SUBNET_VLAN_ID_FIELD,
        err_msg='zbUISubnet.py/_verifyEditMonitoredSubnet: Not able to find vlan id input'
    )
    if not vlanInput:
        return False
    vlanInput.click()
    vlanInput.clear()
    vlanInput.send_keys(kwargs['modifiedVlanId'])

    description = browserobj.findSingleCSS(
        browserobj=row,
        selector=CSS_UPDATE_SUBNET_DESCRIPTION_FIELD,
        err_msg='zbUISubnet.py/_verifyEditMonitoredSubnet: Not able to find subnet description input'
    )
    if not description:
        return False
    description.click()
    description.clear()
    description.send_keys(kwargs['modifiedDescription'])
    rcode = browserobj.click(
        browserobj=row,
        selector=CSS_UPDATE_SUBNET_SUBMIT_BTN,
        err_msg='zbUISubnet.py/_verifyEditMonitoredSubnet: Not able to click submit button'
    )
    rcode = rcode and _clickSave(browserobj)
    return True

def _verifyDeleteMonitoredSubnet(browserobj, **kwargs):
    row = _findTargetRow(browserobj, **kwargs)
    if not row:
        print(('zbUISubnet.py/_verifyDeleteMonitoredSubnet: Not able to find target row for subnet {}'.format(kwargs['subnet'])))
        return False
    rcode = browserobj.click(
        browserobj=row,
        selector=CSS_SUBNET_CHECKBOX,
        err_msg='zbUISubnet.py/_verifyDeleteMonitoredSubnet: Not able to click subnet checkbox',
        timeout=3
    )
    if kwargs['monitored'] is True:
        rcode = rcode and browserobj.click(
            selector=CSS_SUBNET_DELETE_BTN,
            err_msg='zbUISubnet.py/_verifyDeleteMonitoredSubnet: Not able to click delete button',
            timeout=3
        )
        time.sleep(2)
        rcode = rcode and browserobj.click(
            selector=CSS_CONFIRM_DELETE_BTN,
            err_msg='zbUISubnet.py/_verifyDeleteMonitoredSubnet: Not able to click confirm delete button',
            timeout=3
        )
    else:
        rcode = rcode and browserobj.click(
            selector=CSS_SUBNET_DELETE_NOT_MONITORED_BTN,
            err_msg='zbUISubnet.py/_verifyDeleteMonitoredSubnet: Not able to click delete button for not monitored subnet',
            timeout=3
        )
        rcode = rcode and _clickSave(browserobj)
    return rcode

def _stopMonitoringSubnet(browserobj, **kwargs):
    row = _findTargetRow(browserobj, **kwargs)
    if not row:
        print(('zbUISubnet.py/_stopMonitoringSubnet: Not able to find target row for subnet {}'.format(kwargs['subnet'])))
        return False
    rcode = browserobj.click(
        browserobj=row,
        selector=CSS_SUBNET_CHECKBOX,
        err_msg='zbUISubnet.py/_stopMonitoringSubnet: Not able to click subnet checkbox'
    )
    rcode = rcode and browserobj.click(
        selector=CSS_SUBNET_STOP_MONITORING_BTN,
        err_msg='zbUISubnet.py/_stopMonitoringSubnet: Not able to click stop monitoring button'
    )
    time.sleep(2)
    rcode = rcode and browserobj.click(
        selector=CSS_CONFIRM_STOP_MONITORING_BTN,
        err_msg='zbUISubnet.py/_stopMonitoringSubnet: Not able to click confirm stop monitoring button'
    )
    return rcode

def _findTargetRow(browserobj, **kwargs):
    rows = browserobj.findMultiCSS(
        selector=CSS_SUBNET_ROW,
        err_msg='zbUISubnet.py/_verifyEditMonitoredSubnet: Not able to find subnet rows'
    )
    if not rows:
        return False
    for row in rows:
        subnet = browserobj.getText(
            browserobj=row,
            selector=CSS_SUBNET_NAME,
            err_msg='zbUISubnet.py/_verifyEditMonitoredSubnet: Unable to subnet name',
            timeout=3
        )
        if subnet == kwargs['subnet']:
            return row
        else:
            continue
    return False

def _addSubnet(browserobj, **kwargs):
    rcode = True
    rcode = rcode and browserobj.click(
        selector=CSS_ADD_SUBNET_PLUS_BTN,
        err_msg='zbUISubnet.py/_addSubnet: Not able to click plus button'
    )
    rcode = rcode and browserobj.sendKeys(
        selector=CSS_ADD_CUSTOM_SUBNET_FIELD,
        text=kwargs['subnet'],
        err_msg='zbUISubnet.py/_addSubnet: Not able to send key to custom subnet field'
    )
    rcode = rcode and browserobj.sendKeys(
        selector=CSS_ADD_SUBNET_VLAN_ID_FIELD,
        text=kwargs['vlanId'],
        err_msg='zbUISubnet.py/_addSubnet: Not able to send key to vlan id field'
    )
    rcode = rcode and browserobj.sendKeys(
        selector=CSS_ADD_SUBNET_DESCRIPTION_FIELD,
        text=kwargs['description'],
        err_msg='zbUISubnet.py/_addSubnet: Not able to send key to subnet description field'
    )
    rcode = rcode and browserobj.click(
        selector=CSS_ADD_SUBNET_SUBMIT_BTN,
        err_msg='zbUISubnet.py/_addSubnet: Not able to click submit button'
    )
    return rcode

def _clickSave(browserobj):
    return browserobj.click(
        selector=CSS_SUBNET_SAVE_BTN,
        err_msg='zbUISubnet.py/_clickSave: Not able to click save button'
    )

class Subnet():

    def __init__(self, **kwargs):
        self.params = kwargs
        self.selenium = Login(**kwargs).login()
        self.baseurl = kwargs["url"]+'/'

    def gotoSubnetPanel(self):
        time.sleep(3)
        self.selenium.click(
            selector=CSS_SUBNET_ICON,
            err_msg='zbUISubnet.py/gotoSubnetPanel: Not able to click subnet panel button',
            timeout=3
        )
        waitLoadProgressDone(self.selenium)

    def verifyDownloadSubnet(self):
        self.gotoSubnetPanel()
        return _verifyDownloadSubnet(self.selenium)

    def verifySubnet(self, monitored=True):
        rcode = True
        kwargs = {}
        if monitored:
            kwargs['subnet'] = '192.168.40.1/32'
        else:
            kwargs['subnet'] = '192.168.40.2/32'
        kwargs['vlanId'] = '123'
        kwargs['description'] = 'zbat description at {}'.format(time.time())
        kwargs['modifiedVlanId'] = '124'
        kwargs['modifiedDescription'] = kwargs['description'] + '1'
        kwargs['monitored'] = monitored
        
        # cleanup first
        self.gotoSubnetPanel()
        _verifyDeleteMonitoredSubnet(self.selenium, **kwargs)
        
        self.gotoSubnetPanel()
        rcode = rcode and _verifyAddMonitoredSubnet(self.selenium, **kwargs)
        if monitored is False:
            self.gotoSubnetPanel()
            rcode = rcode and _stopMonitoringSubnet(self.selenium, **kwargs)
        self.gotoSubnetPanel()
        rcode = rcode and _verifyEditMonitoredSubnet(self.selenium, **kwargs)
        self.gotoSubnetPanel()
        kwargs['vlanId'] = kwargs['modifiedVlanId']
        kwargs['description'] = kwargs['modifiedDescription']
        kwargs['monitored'] = monitored
        rcode = rcode and _verifyDeleteMonitoredSubnet(self.selenium, **kwargs)
        time.sleep(5)
        return rcode

    def close(self):
        if self.selenium:
            self.selenium.quit()
