
import os, sys, json, requests


# https://testing.zingbox.com/v0.3/api/getconfig?tenantid=testing-soho
def get_config(host, jwt, tenant):
    url = 'https://' + host + '/v0.3/api/getconfig?tenantid=' + tenant
    headers = {'Accept': 'application/json', 'Content-Type': 'application/json'}
    headers['Authorization'] = 'Bearer ' + jwt

    try:
        r = requests.get(url, headers=headers, timeout=30)
    except requests.exceptions.Timeout:
        print("Timed out for url: {}".format(url))
        return None

    if r.status_code == 200:
        response = r.json()
    else:
        print("Got error code: {}, err: {}".format(r.status_code, r.text))
        return None

    return response

def get_config_section (config, section, inspector=None):
    try:
        common_config = config[section]
    except:
        common_config = {}

    try:
        inspectors = config['inspector_configs']
    except:
        inspectors = []

    inspector_configs = {}
    for one_inspector in inspectors:
        try:
            this_inspector = one_inspector['inspector_id']
            if inspector is None:
                inspector_configs[this_inspector] = one_inspector[section]
            else:
                if inspector == this_inspector:
                    inspector_configs[this_inspector] = one_inspector[section]
                    break
        except:
            continue

    return (common_config, inspector_configs)

def validate_config (config):
    if 'schema_version' not in config:
        print("Missing 'schema_version'")
        return False

    return True

def validate_rules (rules):
    unsupported_kws = [ "classtype:", "byte_math:", "ssl_state:", "dce_iface:", "ssl_version:"]
    for rule in rules:
        for kw in unsupported_kws:
            if kw in rule:
                return (False, "Rule option %s not supported" % (kw))
    return (True, "ok")

def validate_services (services):
    return (True, "ok")

internal_sections = {
  'rules': validate_rules,
  'services': validate_services
}

# not providing a global post_config to reduce chance of mistakes
def update_config_section(host, jwt, tenant, section, data, inspector=None):
    if section is None:
        return {'error': 'missing section'}
    if section not in internal_sections:
        return {'error': 'updating section %s not allowed' % (section)}

    validator = internal_sections[section]

    validate_res = validator(data)
    if not validate_res[0]:
        return {'error': 'failed validating data for section %s: %s' % (section, validate_res[1])}

    config = get_config(host, jwt, tenant)
    if config is None:
        return {'error': 'failed to retrive configuration first'}

    if not validate_config(config):
        return {'error': 'Invalid existing configuration'}

    if inspector is None:
        config[section] = data
    else:
        try:
            inspector_configs = config['inspector_configs']
        except:
            inspector_configs = []
            config['inspector_configs'] = inspector_configs

        ins_config = None
        for one_inspector in inspector_configs:
            try:
                if one_inspector['inspector_id'] == inspector:
                    ins_config = one_inspector
                    break
            except:
                continue

        if ins_config:
            ins_config[section] = data
        else:
            ins_config = {'inspector_id':inspector, section: data}
            inspector_configs.append(ins_config)

    print("Config to push:\n{}".format(json.dumps(config)))

    # config is ready to push
    url = 'https://' + host + '/v0.3/api/publishconfig?tenantid=' + tenant
    headers = {'Accept': 'application/json', 'Content-Type': 'application/json'}
    headers['Authorization'] = 'Bearer ' + jwt

    try:
        r = requests.post(url, headers=headers, json=config, timeout=30)
    except requests.exceptions.Timeout:
        return {'error': "Timed out for posting to url " + url}

    if r.status_code == 200:
        response = r.json()
        return response
    else:
        return {'error': 'got error code %d, err:%s ' % (r.status_code, r.text)}
