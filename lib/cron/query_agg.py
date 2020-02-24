import os
import sys
import json
import pdb
import schedule
import time
import datetime
from dateutil.parser import parse
from urllib.parse import urlparse
import requests


try:
    env = os.environ['NODE_ENV']
    zbat_home = os.environ['ZBAT_HOME']
    test_server_api_token = os.environ['ZBAT_TEST_API_TOKEN']
    staging_server_api_token = os.environ['ZBAT_STAGING_API_TOKEN']
    prod_server_api_token = os.environ['ZBAT_PROD_API_TOKEN']
except:
    print('Test cannot run.  Please set NODE_ENV to testing|staging|production.')
    print('Test cannot run.  Please set ZBAT_HOME.')
    print('Test cannot run.  Please set ZBAT_TEST_API_TOKEN.')
    print('Test cannot run.  Please set ZBAT_PROD_API_TOKEN.')
    sys.exit()

'''
if env not in ['testing']:
    print('Query agg cron job can only be triggered in testing env.')
    sys.exit()
'''

if zbat_home+'lib' not in sys.path:
    sys.path.append(zbat_home+'lib')

from common.zbSlack import zbSlack
from zbAPI import zbAPI


query = 'https://{base_path}/v0.3/api/dashboard/series?direction=all&interval={interval}&tenantid={tenantid}&stime={stime}&etime=now'
ot_data_query = 'https://{base_path}/v0.3/api/otdashboard/series?etime=now&filter_profile_category={category}&interval={interval}&stime={stime}&tenantid={tenantid}'
slack = zbSlack()

def is_json(data):
    try:
        json.loads(data)
    except ValueError:
        return False
    return True

def query_agg_data(base_path='testing-soho.zingbox.com', tenantid='testing-soho', interval='day'):
    #old code, causing issue with dailylight saving time.

    # today = datetime.datetime.today() - datetime.timedelta(days=1)
    # year = str(today.year).zfill(4)
    # month = str(today.month).zfill(2)
    # day = str(today.day).zfill(2)
    # stime = '{year}-{month}-{day}T17%3A58'.format(
    #     year=year,
    #     month=month,
    #     day=day
    # )

    # if 'demo' in base_path:
    #     stime = (datetime.datetime.utcnow() - datetime.timedelta(hours=25)).strftime('%Y-%m-%dT%H:%MZ')
    # else:
    #     stime = (datetime.datetime.utcnow() - datetime.timedelta(days=1)).strftime('%Y-%m-%dT%H:%MZ')

    stime = (datetime.datetime.utcnow() - datetime.timedelta(days=1)).strftime('%Y-%m-%dT%H:%MZ')

    headers = {
        'Authorization': token_for_url(base_path)
    }

    _query = query.format(base_path=base_path, interval=interval, tenantid=tenantid, stime=stime)
    raw_result = requests.get(_query, headers=headers)
    result = None
    if is_json(raw_result.text):
        result = json.loads(raw_result.text)
    else:
        result = raw_result.text

    return result

def query_ot_agg_data(base_path='testing-soho.zingbox.com', tenantid='testing-soho', category='X-Ray Machine', interval='day'):
    days_map = {
        'minutes': 1,
        'hour': 7,
        'day': 30
    }
    today = datetime.datetime.today() - datetime.timedelta(days=days_map[interval])
    year = str(today.year).zfill(4)
    month = str(today.month).zfill(2)
    day = str(today.day).zfill(2)
    stime = '{year}-{month}-{day}T17%3A58'.format(
        year=year,
        month=month,
        day=day
    )
    headers = {
        'Authorization': token_for_url(base_path)
    }
    _query = ot_data_query.format(base_path=base_path, category=category, interval=interval, tenantid=tenantid, stime=stime)
    raw_result = requests.get(_query, headers=headers)
    result = None
    if is_json(raw_result.text):
        result = json.loads(raw_result.text)
    else:
        result = raw_result.text
    return result

def is_within_time_range_for_interval(interval, _date):
    timeformat = '%y-%m-%d %H:%M'
    _now = datetime.datetime.utcnow().strftime(timeformat)
    _now = datetime.datetime.strptime(_now, timeformat)
    _date = _date.strftime(timeformat)
    _date = datetime.datetime.strptime(_date, timeformat)
    diff = int((_now - _date).total_seconds())

    if interval == 'day':
        return  diff <= (86400 + 3600), diff # give 1 hour buffer
    elif interval == 'hour':
        return diff <= (60*60 + 10*60), diff # give 10 minutes buffer
    elif interval == 'minutes':
        return diff <= 20*60, diff # give 20 minute buffer
    print('is_within_time_range_for_interval: unsupported interval.')
    return False

def is_ot_data_within_time_range_for_interval(interval, _date):
    timeformat = '%y-%m-%d %H:%M'
    _now = datetime.datetime.utcnow().strftime(timeformat)
    _now = datetime.datetime.strptime(_now, timeformat)
    _date = _date.strftime(timeformat)
    _date = datetime.datetime.strptime(_date, timeformat)
    diff = int((_now - _date).total_seconds())

    consecutive_count = 3
    if interval == 'day':
        return  diff <= (86400*1.5), diff # give 1.5 days
    elif interval == 'hour':
        return diff <= (60*60*consecutive_count), diff # give 3 hours
    elif interval == 'minutes':
        #return diff <= (60*5*consecutive_count), diff # give 15 minutes
        return diff <= (60*5*12), diff # give 60 minutes,
    print('is_ot_data_within_time_range_for_interval: unsupported interval.')
    return False

def tenantid_for_url(url):
    if 'testing-soho' in url:
        return 'testing-soho'
    elif 'staging' in url:
        return 'soho'
    elif 'production-candidate' in url:
        return 'soho'
    elif 'demo' in url:
        return 'healthcare'
    else:
        return url[:url.find('.')]

def token_for_url(url):
    if 'testing-soho' in url:
        return test_server_api_token
    if 'staging' in url:
        return staging_server_api_token
    return prod_server_api_token

def _statisfy_skip_option(url, interval):
    if interval == 'day' and 'demo.zingbox.com' in url:
        return True
    return False

def check_bg_agg_connect_event(tenanturl, tenantid, interval):
    req = zbAPI()
    timeFormat = '%Y-%m-%dT%H:%M'
    timenow = datetime.datetime.utcnow().strftime(timeFormat)
    timestart = (datetime.datetime.utcnow() - datetime.timedelta(minutes=10)).strftime(timeFormat)

    defaultParams = {
        "stime": timestart,
        "etime": "now",
        "tenantid": tenantid,
        "interval": interval,
        "filter_monitored": "yes",
        "direction": "all"
    }

    result = req.deviceSummary(host=tenanturl, **defaultParams)
    result = json.loads(result)
    if result["agg"]["total_devices"] < 1:
        print ("Issue with not seeing connected event data")
    else:
        return True


def run(tenant_url, interval):
    ret = True
    tenantid = tenantid_for_url(tenant_url)
    try:
        daily_agg = query_agg_data(tenant_url, tenantid, interval)
        latest_daily_agg = daily_agg["series"]["data"][0]
        _date = parse(latest_daily_agg['dateISO'])
        is_within_time_range, time_diff = is_within_time_range_for_interval(interval, _date)
        if is_within_time_range is True:
            pass
        else:
            raise Exception('Latest "{}" agg is too long ago for {}, time difference is {}'.format(interval, tenant_url, time_diff))
    except Exception as err:
        print(('Data aggregation missing for {} interval {}.'.format(tenant_url.split(".")[0], interval)))
        print(err)
        ret = False
    return ret

def runOTDataTest(tenant_url, category, interval):
    ret = True
    tenantid = tenantid_for_url(tenant_url)
    try:
        agg = query_ot_agg_data(tenant_url, tenantid, category, interval)
        agg = agg["series"]["data"]
        if isinstance(agg, list) is False or len(agg) < 4:
            raise Exception('No OT agg data for {} interval {}, data is {}.'.format(tenant_url.split(".")[0], interval, agg))
        latest_agg = agg[-1]
        _date = parse(latest_agg['dateISO'])
        is_within_time_range, time_diff = is_ot_data_within_time_range_for_interval(interval, _date)
        if is_within_time_range is True:
            pass
        else:
            raise Exception('Latest "{}" ot data agg is too long ago for {}, time difference is {}'.format(interval, tenant_url.split(".")[0], time_diff))
    except Exception as err:
        print(('OT data aggregation missing for {} interval {}.'.format(tenant_url.split(".")[0], interval)))
        print(err)
        ret = False
    return ret

def main():
    intervals = ['day', 'hour', 'minutes']
    tenant_urls = ['testing-soho.zingbox.com', 'demo.zingbox.com', 'production-candidate.zingbox.com']
    for tenant_url in tenant_urls:
        for interval in intervals:
            run(tenant_url, interval)

if __name__ == "__main__":
    main()
    schedule.every(10).minutes.do(main)
    while True:
        schedule.run_pending()
        time.sleep(601)
        
