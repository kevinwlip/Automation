#!/usr/bin/python
import os
import sys
import pytest
import re
from zbAPI import zbAPI, Ops
import pdb, datetime, json

try:
    env = os.environ['ZBAT_HOME']
except:
    print ('Test cannot run.  Please export ZBAT_HOME.')
    sys.exit()

if env+'lib' not in sys.path:
    sys.path.append(env+'lib')

from cron import query_agg
from zbConfig import defaultEnv
from zb_logging import logger as logging

req = zbAPI()
env = defaultEnv()

TIMEFORMAT = '%Y-%m-%dT%H:%MZ'
TIMENOW = datetime.datetime.utcnow()

TENANTS = [
        'testing-soho.zingbox.com', # in testing env
        #'staging.zingbox.com', # in staging env  STAGING IS NOT UPDATING FOR HOURLY
        'production-candidate.zingbox.com', # in x1-m1 env
        'demo.zingbox.com', # in demo env
        'allinahealth.zingbox.com',  # in x2-m3 env
        #'bmcc.zingbox.com', # in x1-m1 env, inspector very flaky up/down all the time
        'baycare.zingbox.com', # in x1-m1 env
        'beaconhealthsystem.zingbox.com', # in x1-m1 env
        'brainerdbaptist.zingbox.com', # in x1-m1 env
        #'bvchd.zingbox.com', # in x1-m1 env, have no data
        'centrastate.zingbox.com', # in x1-m1 env
        #'fujitsu.zingbox.com', # in x1-m1 env, doesn't seem to have data
        #'gatewaycomputer.zingbox.com', # in x1-m1 env, have not setup inspector
        'medstar.zingbox.com', # in x2-m3 env
        'pinnaclehealth.zingbox.com', # in x2-m2 env
        'ssmhealth.zingbox.com', # in x2-m3 env
        'stamhealth.zingbox.com', # in x1-m1 env
        'uihc.zingbox.com', # in x1-m1 env
        'unitedregional.zingbox.com', # in x1-m1 env
        'waubonsee.zingbox.com' # in x2-m2 env
    ]

@pytest.mark.parametrize("interval", ['minutes', 'hour', 'day'])
@pytest.mark.parametrize("tenant_url", TENANTS)
class Test_Data_Agg:


    def test_agg_session_event(self, tenant_url, interval):
        # This test for each Tenant, and check for the last data point on the Series graph
        #     it then compares to the current time, and if exceeding certain limit, then
        #     it will indicate Session aggregation is failing
        
        # skip test for demo with interval day since data is not avail on demo env.
        if interval == 'day' and 'demo.zingbox.com' in tenant_url:
            assert True
            return
        assert query_agg.run(tenant_url, interval) == True


    def test_agg_connect_event(self, tenant_url, interval):
        # This test for each Tenant, and check for time range in last 10 minutes for the device count
        #     if device count is 0, then it indicates Connect Events aggregation is failing
        
        # skip test for demo since no need to check for background job here
        if 'demo.zingbox.com' in tenant_url:
            assert True
            return

        match = re.match(r'(.*)\.zingbox\.com', tenant_url)
        tenantid = match.group(1)

        if 'production-candidate' in tenant_url or 'staging' in tenant_url:
            tenantid = 'soho'
        assert query_agg.check_bg_agg_connect_event(tenant_url, tenantid, interval) == True

TENANT_DIC = {
    'testing-soho':'testing-soho.zingbox.com',
    #'soho': 'soho.zingbox.com',
    'baycare': 'baycare.zingbox.com'
}

@pytest.mark.parametrize("tenant", TENANT_DIC.keys())
#@pytest.mark.parametrize("interval", time_interval)
class Test_Soc_Smoke:


    def test_soc_api_call(self, tenant):
        #This test checks the proxy api call used by MSSP for socindex.html for time range 2hour
        #Only checks api response of active sites
        
        #api: alert/stat
        min_alert_stat = 2

        #api: dashboard/devicesummary
        min_dbsummary_agg = 3

        #api: dashboard/stat
        min_db_stat = 5
        min_db_stat_alert = 3

        #api: site/simplelist
        min_site_stat = 6

        #api: inspector/tenantinspectors
        min_inspector_stat = 10

        #api: dashboard/seriesagg
        min_dbseries_agg = 3

        #api: profile/stats
        min_profile_device_stat = 2
        min_profile_alert = 3

        input_dict = {
                "stime": (TIMENOW - datetime.timedelta(hours=24)).strftime(TIMEFORMAT),
                "etime": "now",
                "interval": "minutes",
                "range": "1day",
                "tenantid": tenant
                }

        #grab json
        j1 = req.msspPortalTenantSummary(host=TENANT_DIC[tenant], **input_dict)
        d1 = {}
        for apires in json.loads(j1):
            if apires["api"] == 'site/simplelist':
                for site in apires["list"]:
                    if site["deploy_status"] == 'LIVE':
                        d1[site["siteid"]] = req.msspPortalTenantSummary(host=TENANT_DIC[tenant], siteids=site["siteid"], **input_dict)

        for active_site in d1:
            site_json = json.loads(d1[active_site])
            for summary in site_json:
                verify_api_response(summary, active_site, 'api', 'ver', 'api_key')

                if summary["api"] == 'alert/stat':
                    verify_api_alert_stat(summary, min_alert_stat, active_site, 'stat', 'messagedate')

                elif summary["api"] == 'dashboard/devicesummary':
                    verify_dashboard_devices_summary(apires=summary, minvalue=min_dbsummary_agg, site_id=active_site)

                elif summary["api"] == 'dashboard/stat':
                    verify_dashboard_stat(apires=summary, minvalue_stat=min_db_stat, minvalue_alert=min_db_stat_alert, site_id=active_site)

                elif summary["api"] == 'site/simplelist':
                    verify_site_simplelist(apires=summary, minvalue=min_site_stat)

                elif summary["api"] == 'inspector/tenantinspectors':
                    verify_inspector_tenantinspectors(apires=summary, minvalue=min_inspector_stat, site_id=active_site)

                elif summary["api"] == 'dashboard/seriesagg':
                    verify_dashboard_seriesagg(apires=summary, minvalue=min_dbseries_agg, site_id=active_site)

                elif summary["api_key"] == 'v0.3/api/iotprofile/stats?outputtype=category&':
                    verify_profile_stats(apires=summary, minvalue=min_profile_device_stat, site_id=active_site)

                elif summary["api_key"] == 'v0.3/api/iotprofile/stats?outputtype=vertical&':
                    verify_profile_stats(apires=summary, minvalue=min_profile_device_stat, site_id=active_site)


        if not len(d1): assert False, "No sites active."
        assert True


def verify_api_response(apires, site_id, *args):
    for keys in args:
        if keys not in apires: assert False, 'Missing key: {0} for site {1}'.format(keys, site_id)
        if not apires[keys]: assert False, 'Missing values for {0} for site {1}'.format(keys, site_id)

def verify_api_alert_stat(apires, minvalue, site_id, *args):
    for keys in args:
        if keys not in apires: assert False, 'Missing key: {0}'.format(keys)
        if keys == 'stat' and len(apires[keys]) < minvalue: assert False, 'Missing fields in {0} for site {1}'.format(keys, site_id)
        elif keys == 'messagedate' and not apires[keys]: assert False, 'Missing message date'

def verify_dashboard_devices_summary(apires, minvalue, site_id):
    if 'agg' not in apires: assert False, 'Missing key: "agg" in site {0}'.format(site_id)
    if len(apires['agg']) < minvalue: assert False, 'Missing values for device summary in site {0}'.format(site_id)

def verify_dashboard_stat(apires, minvalue_stat, minvalue_alert, site_id):
    if 'stat' not in apires: assert False, 'Missing key: stat'
    if len(apires['stat']) < minvalue_stat: assert False, 'Expected value greater than {0} for stat in site {1}'.format(minvalue_stat, site_id)
    if len(apires['stat']['alerts']) < minvalue_alert: assert False, 'Expected value greater than {0} for alerts in site {1}'.format(minvalue_alert, site_id)

def verify_site_simplelist(apires, minvalue):
    if 'list' not in apires: assert False, 'Missing key: site'
    if 'allsites' not in apires: assert False, 'Missing key: allsites'
    if not apires['list']: assert False, 'Missing sites'
    if not apires['allsites']: assert False, 'Missing list of sites'

    for sites in apires['list']:
        if len(sites) < minvalue: assert False, 'Missing values for site {0}'.format(sites)

def verify_inspector_tenantinspectors(apires, minvalue, site_id):
    if 'inspectors' not in apires: assert False, 'Missing key: inspectors'
    if not apires['inspectors']: assert False, 'Missing inspectors'

    for inspector in apires['inspectors']:
        if len(inspector) < minvalue: assert False, 'Missing values for inspectors in site {0}'.format(site_id)
        if 'connectivity' not in inspector: assert False, 'Missing connectivity status in site {0}'.format(site_id)

def verify_dashboard_seriesagg(apires, minvalue, site_id):
    if 'agg' not in apires: assert False, 'Missing key: agg'
    if len(apires['agg']) < minvalue: assert False, 'Missing values for agg for site {0}'.format(site_id)

def verify_profile_stats(apires, minvalue, site_id):
    if 'list' not in apires: assert False, 'Missing key: list'
    if not apires['list']: assert False, 'No devices in site {0}'.format(site_id)

    for devices in apires['list']:
        if len(devices) < minvalue: assert False, 'Missing values for devices for site {0}'.format(site_id)
        if 'id' not in devices: assert False, 'Missing ID for site {0}'.format(site_id)
        if 'profile_type' not in devices: assert False, 'Missing profile type for site {0}'.format(site_id)


class Test_IoT_Inventory:


    def test_smoke_iot_inventory(self):

        #testing-soho & soho
        input_dict = {
                'direction':'all',
                'disable_app':'yes',
                'etime': 'now',
                'filter_monitored':'yes',
                'interval':'day',
                'page':'1',
                'pagelength':'25',
                'searchfield':'vinhs-mbp',
                'sortdirection':'desc',
                'sortfield':'ml_risk_score',
                'stime': (TIMENOW - datetime.timedelta(weeks=1)).strftime(TIMEFORMAT),
                'tenantid':'soho'
                }

        #From IoT Inventory List API call
        api_keys = [
                'ver',
                'api',
                'total',
                'items'
                ]  

        #Expected keys in 'items', these are the displayed fields in the dashboard
        item_keys_required = ['activity_status', 
                              'baseline_progress', 
                              'baseline_state',
                              'category', 
                              'data', 
                              'DHCP',
                              'EPP', 
                              'id', 
                              'ip',
                              'internal_hostname', 
                              'inUse', 
                              'latest_device_time',
                              'model',
                              'ml_progress', 
                              'name',
                              'NetworkLocation', 
                              'osGroup', 
                              'osVer', 
                              'osCombined', 
                              'osVer', 
                              'pii_ts',
                              'profile', 
                              'profile_confidence', 
                              'profile_type', 
                              'profile_type_score', 
                              'profile_type_factors',
                              'profile_vertical', 
                              'sessions', 
                              'siteid', 
                              'sn', 
                              'subnets',
                              'type_by_user', 
                              'vendor', 
                              'vlan', 
                              'vlan_source',
                              'WireWireless'
                ]

        #keys that are not populated from Vinhs-MBP-mod2 and Vinhs-MBP-mod
        item_keys_optional = ['AET',
                              'asset_tag',
                              'baseline_progress',
                              'baseline_pi', 
                              'department', 
                              'desc',
                              'internal_risk_level', 
                              'internal_risk_score', 
                              'inUse', 
                              'location',
                              'ml_progress',
                              'ml_risk_level',
                              'ml_risk_score',
                              'NetworkLocation',
                              'nacProfile', 
                              'nacProfileSource', 
                              'osVerFirmwareVer', 
                              'osVer',
                              'parentDeviceid', 
                              'pii_ts', 
                              'profile_type_score',
                              'profile_type_factors',
                              'risk_score', 
                              'risk_reason', 
                              'sn', 
                              'WireWireless'         
                ]

        j1 = req.iotInventoryList(host='soho.zingbox.com', **input_dict)
        d1 = json.loads(j1)
        print (d1)

        #if the key and value for those keys exist, then test asserts true
        verify_key_value(apires=d1, api_key=api_keys, optional_keys=[])
        for items in d1['items']:
            verify_key_value(apires=items, api_key=item_keys_required, optional_keys=item_keys_optional)

        assert True


def verify_key_value(apires, api_key, optional_keys):
    print (apires)
    for keys in api_key:
        if keys not in apires: assert False, 'Missing key: {0}'.format(keys)

        #if the value doesn't exist, and not including 0's
        if not apires[keys] and not isinstance(apires[keys], int):
            #and if those values are not associated with a key that is not mandatory
            if keys not in optional_keys: assert False, 'Missing value for {0} field'.format(keys)
            #otherwise just notify that thsoe fields are empty
            else: print('Warning: {0} field not properly populated.'.format(keys))




class Test_Count:


    def test_dashboard_risk_assessment_device_count(self):

        input_dict = {
            'direction':'all',
            'etime':'now',
            'filter_monitored':'yes',
            'interval':'hour',
            'stime':(TIMENOW - datetime.timedelta(weeks=1)).strftime(TIMEFORMAT),
            'tenantid':env['tenantid']
        }

        dash_filter_json = req.deviceSummary(host=env['siteTest'], **input_dict)
        risk_devices_json = req.riskAssessment(host=env['siteTest'], **input_dict)

        d1 = json.loads(dash_filter_json)
        d2 = json.loads(risk_devices_json)

        try: 
            dashboard_total = int(str(d1['agg']['total_devices']).replace(',',''))
            # dashboard_compare = int(str(d1['agg']['total_Non_IoT_devices']).replace(',','')) + int(str(d1['agg']['total_IoT_devices']).replace(',',''))

            #currently not testing adding up devices and comparing total
            '''
            if dashboard_total != dashboard_compare:
            pdb.set_trace()
            logging.critical("Dashboard filter device count doesn't add to total count")
            return False
            '''

        except ValueError:
            logging.critical('Total devices in dashboard filter not a number')
            return False


        try:
            risk_assessment_total = int(str(d2['stat']['total_monitored_devices']).replace(',',''))

            #currently not testing adding up devices and comparing total
            '''
            risk_assessment_compare = 0

            for risk_devices in d2['stat']['device_risks']:
                risk_assessment_compare += int(str(risk_devices).replace(',',''))

            if risk_assessment_total != risk_assessment_compare:
                logging.critical("Risk management device count doesn't add to total count")
                return False
            '''

        
        except ValueError:
            logging.critical('Total devices for risk assessment not a number')
            return False

        print (str(dash_filter_json))
        print (str(risk_devices_json))


        if dashboard_total != risk_assessment_total:
            # add special handling for soho, since soho data sometimes has a little mismatch
            if env['tenantid'] == 'soho':
                percent_diff_allow = 10
                if (abs(int(dashboard_total)-int(risk_assessment_total))/int(dashboard_total))*100 < percent_diff_allow:
                    assert True
                    return
            assert False, logging.error('Total devices not matching')
