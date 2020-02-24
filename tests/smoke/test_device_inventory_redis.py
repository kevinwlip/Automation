#!/usr/bin/python
import re
import pdb, json, sys, os, pytest, datetime, random, time
import redis

try:
    env = os.environ['ZBAT_HOME']
except:
    print 'Test cannot run.  Please export ZBAT_HOME.'
    sys.exit()

if env+'lib' not in sys.path:
    sys.path.append(env+'lib')

from common.zbConfig import defaultEnv
env = defaultEnv()

def test_device_inventory_redis():
    host = env.get('redisHost', 'localhost')
    rd = redis.Redis(host=host, password=None, socket_timeout=300)
    BATCH_SIZE = 500
    MIN_CHECK_REQUIRED = 100
    checked = 0
    cursor = 0
    pattern = re.compile('.+([0-9A-Fa-f]{2}[:-]){5}([0-9A-Fa-f]{2})$')
    try:
        while checked < MIN_CHECK_REQUIRED:
            cursor, keys = rd.scan(cursor, count=BATCH_SIZE)
            for key in keys:
                if pattern.match(key) is not None and key[:3] != 'i-s':
                    print('Checking key {}'.format(key))
                    payload = json.loads(rd.get(key))
                    print payload
                    print key[:13]
                    if (key[:13] == "basic_anomaly"):
                        assert payload.get('tenant_id', None) is not None
                        assert payload.get('tenant_id', None) in key
                        assert payload.get('profile_id', None) is not None
                    else:
                        assert payload.get('tenantid', None) is not None
                        assert payload.get('tenantid', None) in key
                        assert payload.get('deviceid', None) is not None
                        assert payload.get('deviceid', None) in key
                    checked = checked + 1
                else:
                    print('Skipping key {}'.format(key))
    except Exception as err:
        print('test_device_inventory_redis: {}'.format(err))
        assert 0
