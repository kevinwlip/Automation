#!/usr/bin/python

# zbSnortRules.py

import os, sys, subprocess, pdb

zbathome = os.environ['ZBAT_HOME']
sys.path.append(zbathome+'util/sec-utils')
from config import get_config, get_config_section, update_config_section

from zb_logging import logger as logging


def get_common_rules(api_server, api_token, tenant):
	get_common_rules = subprocess.Popen(["python", "rules.py", "-a", api_server, "-j", api_token, "-t", tenant, "get"], stdout=subprocess.PIPE)
	get_rules_output = get_common_rules.communicate()
	get_rules_list = list(get_rules_output)
	get_rules_list = get_rules_list[0].split('\n')
	get_rules_list.pop(len(get_rules_list)-1)
	get_rules_list_length = len(get_rules_list)
	logging.info("Length of current common rules list: {}".format(get_rules_list_length))
	return [get_rules_list_length, get_rules_list]

def set_common_rules(api_server, api_token, tenant):
	set_common_rules = subprocess.Popen(["python", "rules.py", "-a", api_server, "-j", api_token, "-t", tenant, "set", "common_rules"], stdout=subprocess.PIPE)
	set_rules_output = set_common_rules.communicate()
	set_rules_list = list(set_rules_output)
	set_rules_list = set_rules_list[0].split('\n')
	set_rules_list.pop(len(set_rules_list)-1)
	
	filtered_set_rules_length = 0
	filtered_set_rules_list = []
	for rules in set_rules_list:
		if "sid:" in rules and len(rules) < 10000:
			filtered_set_rules_length += 1
			filtered_set_rules_list.append(rules)
	logging.info("Length of updated common rules list: {}".format(filtered_set_rules_length))
	return [filtered_set_rules_length, filtered_set_rules_list]

def pull_push_rules(min_rules = 400):
	changedir = os.chdir('../util/sec-utils')
	cwd = os.getcwd()

	logging.info("Getting rules list initially")
	if get_common_rules(api_server, api_token, tenant)[0] > min_rules:
		logging.info("Rules satisfy the minimum rules count of {}".format(min_rules))
	else:
		logging.error("Rules do not satisfy the minimum rules count of {}".format(min_rules))
		return False

	logging.info("Setting rules list")
	run_set_value = set_common_rules(api_server, api_token, tenant)[0]
	
	logging.info("Getting rules list again")
	run_get_value = get_common_rules(api_server, api_token, tenant)[0]
	logging.info("After setting the common rules and getting common rules again, the values should be equivalent")
	if run_set_value == run_get_value:
		logging.info("Success!!! Set and Get values are equivalent")
		return True
	else:
		logging.error("Failure!!! Please check 'rules.py' in 'zbat/util/sec-utils', may also have to examine the get/set common rules returned to resolve issues")
		return False


# Driver Code for testing
#env = os.environ.copy()
#api_server = "testing.zingbox.com"
#api_token = env['ZBAT_TEST_API_TOKEN'].split()[1]
#tenant = "testing-soho"
#pull_push_rules()


# Future code for upgrading inspector below, ${bamboo.buildNumber} is a number
#changedir = os.chdir('../zc-utils')
#upgrade_inspector = subprocess.Popen(["bash", "push_build", "-v", "testing", "testing-soho", "master", "${bamboo.buildNumber}"], stdout=subprocess.PIPE) 
