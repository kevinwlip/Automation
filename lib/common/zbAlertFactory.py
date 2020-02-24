import time
import random
import string

from .zbAlertTemplates import policy_alert_default_dict, policy_alert_tag_default_dict, threat_alert_default_list, threat_alert_tag_default_list

def _get_timestamp():
    return int(time.time()) * 1000

def _add_key(key, payload, default_list=policy_alert_default_dict):
    if key is None:
        return payload
    if key in payload:
        print(('Key value {0} exists in payload, value is {1}'.format(key, payload[key])))
        return payload
    if key not in default_list:
        return payload
    payload[key] = default_list[key]
    return payload

def create_policy_alert(**kwars):
    if 'tenantid' not in kwars:
        print('Key "tenantid" not found in keyword arguments, returning empty payload')
        return {}

    payload = kwars

    payload['timestamp'] = _get_timestamp()

    payload['tags'] = _create_policy_alert_tag(**kwars)

    # Default params
    params = ['hostname', 'remoteIPAddr', 'evtType', 'appName', 'tenantid', 'iotDevid', 'evtContent', 'ruleid']
    for param in params:
        payload = _add_key(param, payload)

    return payload

def create_threat_alert(**kwars):
    if 'tenantid' not in kwars:
        print('Key "tenantid" not found in keyword arguments, returning empty payload')
        return {}

    payload = kwars

    payload['timestamp'] = _get_timestamp()

    key = 'deviceid'
    deviceid = threat_alert_default_list[key]
    if key in kwars:
        deviceid = kwars[key]
    payload['key'] = '{0}{1}'.format(kwars['tenantid'], deviceid)

    payload['tags'] = _create_threat_alert_tag(**kwars)

    # Default params
    params = ['remoteIPAddrList', 'evtType', 'type', 'iotDevid', 'appNameList', 'ttBytes', 'portList', 'encryptedBytes', 'accessCount', 'portCount',
              'rxBytes', '_date', 'evtContent', 'deviceid', 'remoteIPCount', 'unencryptedBytes', 'txBytes', 'interval', 'fields', 'ruleid', 'portSeq', 'ts']
    for param in params:
        payload = _add_key(param, payload, threat_alert_default_list)

    return payload

def _generate_id(length=5):
    return ''.join(random.choice(string.ascii_uppercase + string.ascii_lowercase + string.digits) for _ in range(length))

def _create_policy_alert_tag(**kwars):
    tag = []
    payload = kwars

    #severity = random.choice(['low', 'medium', 'high'])
    severity = random.choice(['medium', 'high'])
    key = 'severity'
    payload[key] = severity
    if key in kwars:
        payload[key] = kwars[key]

    payload['id'] = _generate_id(length=5)

    payload['alertKey'] = '{0}ba4:77:33:26:e1:38'.format(kwars['tenantid'])
    payload['acl'] = 'true'
    payload['userPolicy'] = 'true'

    # Default params
    params = ['name', 'description', 'taggedBy', 'appName', 'values',
              'toURL', 'toPort',  'toip', 'proto', 'fromip', 'status', 'ruleid']

    for param in params:
        payload = _add_key(param, payload, default_list=policy_alert_tag_default_dict)

    tag.append(payload)
    return tag

def _create_threat_alert_tag(**kwars):
    tag = []
    payload = kwars

    #severity = random.choice(['low', 'medium', 'high'])
    severity = random.choice(['medium', 'high'])
    key = 'severity'
    payload[key] = severity
    if key in kwars:
        payload[key] = kwars[key]

    payload['id'] = _generate_id(length=5)

    # Default params
    params = ['name', 'description', 'taggedBy', 'appName', 'values', 'status', 'ruleid', 'fromip']
    for param in params:
        payload = _add_key(param, payload, default_list=threat_alert_tag_default_list)

    tag.append(payload)
    return tag

def create_system_alert(**kwars):
    payload = {}

    timestamp = int(time.time()) * 1000
    payload['timestamp'] = timestamp

    return payload
