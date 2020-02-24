import os
import sys
import json
import base64

import requests

from . import zbZAPI

JIRA_ISSUE_PATH = 'https://zingbox.atlassian.net/rest/api/2/issue/{issue_key}'
AUTOMATION_ID_FIELD = 'customfield_11200'

def _isJson(data):
    try:
        json.loads(data)
    except ValueError:
        return False
    return True

def _getAutomationIdMap(executions=[]):
    _map = {}

    jira_uname = os.environ['ZBAT_JIRA_UNAME']
    jira_pwd = os.environ['ZBAT_JIRA_PWD']
    access_token = base64.b64encode(jira_uname + ':' + jira_pwd)
    headers = {
        'Authorization': 'Basic ' + access_token,
        'Content-Type': 'application/json'
    }

    for execution in executions:
        url = JIRA_ISSUE_PATH.format(issue_key=execution['issueKey'])
        rawResult = requests.get(url, headers=headers)
        if _isJson(rawResult.text) is False:
            continue
        response = json.loads(rawResult.text)
        fields = response['fields']
        if fields[AUTOMATION_ID_FIELD] is not None:
            execution_id = execution['execution']['id']
            _map[execution_id] = {
                'automation_id': fields[AUTOMATION_ID_FIELD],
                'issue_id': execution['execution']['issueId'],
                'issue_key': execution['issueKey']
            }
    return _map

def _generatePytestCommand(automation_id):
    return 'pytest $ZBAT_HOME{} -v'.format(automation_id)

def _isTestPass(output):
    last_line = output[-1].lower()
    if 'passed' in last_line:
        return True
    elif 'skipped' in last_line:
        return True
    return False

def _run_ui_test(automation_id):
    command = _generatePytestCommand(automation_id)
    output = os.popen(command).readlines()
    return _isTestPass(output), output

def main(cycleKeyword=''):
    cycles = zbZAPI.getCycles(cycleKeyword)
    # get execution of those cycle
    executions = []
    for cycle in cycles:
        cycle_id = cycle['id']
        executions.extend(zbZAPI.getExecutions(cycle_id))
    # use issueId to get automation ids from JIRA
    automation_id_map = _getAutomationIdMap(executions)
    print(('Executions {}'.format(automation_id_map)))
    # run automation test
    for execution_id, payload in list(automation_id_map.items()):
        passed, output = _run_ui_test(payload['automation_id'])
        # postback results
        zbZAPI.updateExecution(
            execution_id,
            payload['issue_id'],
            passed,
            output
        )
        print(('{} updated'.format(payload['issue_key'])))

if __name__ == "__main__":
    try:
        zbat_home = os.environ['ZBAT_HOME']
        jira_uname = os.environ['ZBAT_JIRA_UNAME']
        jira_pwd = os.environ['ZBAT_JIRA_PWD']
    except:
        print('Test cannot run.  Please set ZBAT_HOME.')
        print('Test cannot run.  Please set ZBAT_JIRA_UNAME.')
        print('Test cannot run.  Please set ZBAT_JIRA_PWD.')
        sys.exit()
    arguments = sys.argv[1:]
    if type(arguments) != list or len(arguments) < 1:
        print('Please specify keywords for cycle.')
        print('Example: python lib/common/zbJIRA.py "sprint 44"')
        sys.exit()
    main(arguments[0])
