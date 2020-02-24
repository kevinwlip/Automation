#!/usr/bin/python

import os, json, time, hashlib, requests, pdb
from common.zbZAPI import sendZAPICommand

kwars = {}
kwars['query'] = 'projectId=10100&versionId=10300'
api = sendZAPICommand(**kwars)
print(api)