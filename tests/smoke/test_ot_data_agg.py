#!/usr/bin/python
# from __future__ import (absolute_import, division, print_function, unicode_literals)

# from future.builtins import *

import os, sys, pytest
import pdb, datetime, json

try:
    env = os.environ['ZBAT_HOME']
except:
    print 'Test cannot run.  Please export ZBAT_HOME.'
    sys.exit()

if env+'lib' not in sys.path:
    sys.path.append(env+'lib')

from cron import query_agg
from zbAPI import zbAPI
from zb_logging import logger as logging

req = zbAPI()

# Populate to test more
tenantPayloads = {
    'unitedregional': {
        'url': 'unitedregional.zingbox.com',
        'category': 'X-Ray Machine'
    },
    'baycare': {
        'url': 'baycare.zingbox.com',
        'category': 'Infusion System'
    }
}

class Test_OT_Data_Agg:

    @pytest.mark.parametrize("interval", ['minutes', 'hour', 'day'])
    @pytest.mark.parametrize("tenant", ['unitedregional'])
    def test_agg(self, tenant, interval):
        payload = tenantPayloads[tenant]
        assert query_agg.runOTDataTest(payload['url'], payload['category'], interval) == True



class Test_OT_smoke:

    @pytest.mark.parametrize('time', ['oneday', 'week', 'month'])
    @pytest.mark.parametrize('tenant', ['baycare'])
    def test_infusion_pump_series(self, tenant, time):
        TIMEFORMAT = '%Y-%m-%dT%H:%MZ'
        TIMENOW = datetime.datetime.utcnow()

        payload = tenantPayloads[tenant]

        if time == 'oneday':
            stime = (TIMENOW - datetime.timedelta(days=1)).strftime(TIMEFORMAT)
            interval = 'minutes'

        if time =='week':
            stime = (TIMENOW - datetime.timedelta(weeks=1)).strftime(TIMEFORMAT)
            interval = 'hour'

        if time == 'month':
            stime = (TIMENOW - datetime.timedelta(days=30)).strftime(TIMEFORMAT)
            interval = 'day'

        input_dict = {
            'dateRangeName':time,
            'etime':'now',
            'filter_profile_category':payload['category'],
            'interval':interval,
            'stime':stime,
            'tenantid': tenant,
            'type':'used'
        }

        _query = req.ot_dashboard_iv_series(host=payload['url'], **input_dict)
        try:
            rcode = json.loads(_query)
        except e:
            logging.critical('Got exception {0}'.format(e))

        data_set = rcode['series']['used']
        last_data = len(data_set) - 1

        if interval == 'minutes':
            #1day
            logging.info('Smoke test, data for {0}'.format(time))
            if not data_set[last_data] and not data_set[last_data-1] and not data_set[last_data-2]:
                assert False, logging.error('Test fail, last 3 data points are 0')

        elif interval == 'hour':
            #1week
            logging.info('Smoke test, data for {0}'.format(time))
            if not data_set[last_data] and not data_set[last_data-1]:
                assert False, logging.error('Test fail, last 2 data points are 0')

        elif interval == 'day':
            #1month
            logging.info('Smoke test, data for {0}'.format(time))
            if not data_set[last_data]:
                assert False, logging.error('Test fail, last data point is 0')

        assert True, logging.info('Test passed')