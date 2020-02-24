#!/usr/bin/python

import os, json, time, hashlib, requests, pdb
from .JWTGenerator import JWTGenerator

PROJECT_ID = 10100
VERSION_ID = 10300
GET_CYCLES_PATH = '/public/rest/api/1.0/cycles/search'
GET_CYCLES_QUERY = 'projectId={}&versionId={}'.format(PROJECT_ID, VERSION_ID)
GET_EXECUTIONS_PATH = '/public/rest/api/1.0/executions/search/cycle/{cycleId}'
GET_EXECUTIONS_QUERY = 'projectId={}&versionId={}'.format(PROJECT_ID, VERSION_ID)
UPDATE_EXECUTION_PATH = '/public/rest/api/1.0/execution/{executionId}'
EXECUTION_PASSED_ID = 1
EXECUTION_FAILED_ID = 2

def isJson(data):
    try:
        json.loads(data)
    except ValueError:
        return False
    return True

def getCycles(cycleKeyword=''):
    kwars = {}
    kwars['path'] = GET_CYCLES_PATH
    kwars['query'] = GET_CYCLES_QUERY
    respond = sendZAPICommand(**kwars)
    if isJson(respond) is False:
        return []
    respond = json.loads(respond)
    if type(respond) is not list:
        return []
    cycles = []
    for cycle in respond:
        if cycleKeyword.lower() in cycle['name'].lower():
            cycles.append(cycle)
    return cycles

def getExecutions(cycleId):
    kwars = {}
    kwars['path'] = GET_EXECUTIONS_PATH.format(cycleId=cycleId)
    kwars['query'] = GET_EXECUTIONS_QUERY
    respond = sendZAPICommand(**kwars)
    if isJson(respond) is False:
        return {}
    respond = json.loads(respond)
    return respond["searchObjectList"]

def updateExecution(executionId, issueId, passed=True, err=None):
    kwars = {}
    kwars['path'] = UPDATE_EXECUTION_PATH.format(executionId=executionId)
    kwars['method'] = 'PUT'
    statusId = EXECUTION_PASSED_ID
    comment = 'Test passed at {}'.format(time.time())
    if passed is False:
        statusId = EXECUTION_FAILED_ID
        comment = 'Test failed at {}\n\nError:\n{}'.format(time.time(), err)
    kwars['payload'] = {
        'status': {
            'id': statusId
        },
        'comment': comment,
        'issueId': issueId,
        'projectId': PROJECT_ID
    }
    sendZAPICommand(**kwars)

def sendZAPICommand(**kwargs):

    # USER from JIRA >> add-on >> ZAPI >> User
    USER = kwargs["user"] if "user" in kwargs else os.environ['ZAPI_USER']

    # ACCESS KEY from JIRA >> add-on >> ZAPI >> Access Keys
    ACCESS_KEY = kwargs["accesskey"] if "accesskey" in kwargs else os.environ['ZAPI_ACCESS_KEY']

    # SECRET KEY from JIRA >> add-on >> ZAPI >> API Keys
    SECRET_KEY = kwargs["secretkey"] if "secretkey" in kwargs else os.environ['ZAPI_SECRET_KEY']

    # JWT EXPIRE how long token been to be active? 3600 == 1 hour
    JWT_EXPIRE = kwargs["expire"] if "expire" in kwargs else 3600

    # BASE URL for Zephyr for Jira Cloud
    BASE_URL = kwargs["baseurl"] if "baseurl" in kwargs else "https://prod-api.zephyr4jiracloud.com/connect"

    # RELATIVE PATH for token generation and make request to api
    RELATIVE_PATH = kwargs["path"] if "path" in kwargs else "/public/rest/api/1.0/zlicense/addoninfo"

    # QUERY_STRING for sending parameters
    QUERY_STRING = kwargs["query"] if "query" in kwargs else ''

    # setting HTTP Method
    METHOD = kwargs["method"] if "method" in kwargs else "GET"

    # POST JSON PAYLOAD
    PAYLOAD = kwargs["payload"] if "payload" in kwargs else None

    # CANONICAL PATH (Http Method & Relative Path & Query String)
    CANONICAL_PATH = METHOD+"&"+RELATIVE_PATH+"&"+QUERY_STRING

    # generate JWT token
    gen = JWTGenerator(USER, ACCESS_KEY, SECRET_KEY, CANONICAL_PATH)
    token = gen.jwt
    headers = gen.headers

    # MAKE REQUEST:
    if METHOD.lower() == "post":
        rawResult = requests.post(BASE_URL + RELATIVE_PATH, headers=headers, json=PAYLOAD)
    if METHOD.lower() == "get":
        rawResult = requests.get(BASE_URL + RELATIVE_PATH + '?' + QUERY_STRING, headers=headers)
    if METHOD.lower() == "put":
        rawResult = requests.put(BASE_URL + RELATIVE_PATH, headers=headers, json=PAYLOAD)

    if isJson(rawResult.text):
        # JSON RESPONSE: convert response to JSON
        jsonResult = json.loads(rawResult.text)
        # PRINT RESPONSE: pretty print with 4 indent
        return(json.dumps(jsonResult, indent=4, sort_keys=True))
    else:
        return(rawResult.text)
