#!/usr/bin/python

#######################################################################################
#  Author : Vinh Nguyen
#    Date : 3/18/17
#######################################################################################

import pdb, urllib3, requests, jsondiff, json, re, sys
from datetime import datetime
from requests_toolbelt import MultipartEncoder
from requests.packages.urllib3.exceptions import InsecureRequestWarning
if sys.version_info < (3, 0):
    from ordereddict import OrderedDict
else:
    from collections import OrderedDict

urllib3.disable_warnings()
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)
from common.zb_logging import logger as logging

class zbHTTP():
    """
    Example:

    Attributes:

    Todo:

    """

    def __init__(self, **kwargs):
        if not "timeout" in kwargs:  self.timeout = 100
        if not "strict" in kwargs:  self.strict = False

        self.headers = {
                "User-Agent": "curl/7.37.0",
                "Accept-Language": "en-US,en;q=0.8",
                "Accept": "application/json, text/plain, */*"
        }
        #if "auth" in kwargs: self.headers["Authorization"] = kwargs["auth"]

    def get(self, url, **kwargs):
        if "auth" in kwargs: 
            self.headers["Authorization"] = kwargs["auth"]
            del kwargs["auth"]
        stream = False
        if 'stream' in kwargs:
            stream = kwargs['stream']

        r = requests.get(url, verify=self.strict, params=kwargs, headers=self.headers, timeout=self.timeout, stream=stream)
        logging.info(r.request.url)

        if r.status_code == requests.codes.ok:
            if stream is True:
                return r
            else:
                return r.text

        # got something else other than 200 OK
        logging.error("Got code={0} response={1}".format(r.status_code, r.text))
        return r.status_code

    def post(self, url, **kwargs):
        if "auth" in kwargs: 
            self.headers["Authorization"] = kwargs["auth"]
            del kwargs["auth"]

            # note that data must be a json type
            data = kwargs["data"]
            del kwargs["data"]

        r = requests.post(url, verify=self.strict, params=kwargs, headers=self.headers, json=data, timeout=self.timeout)
        logging.info(r.request.url)

        if r.status_code == requests.codes.ok:
            return r.text

        # got something else other than 200 OK
        logging.error("Got code={0} response={1}".format(r.status_code, r.text))
        return r.status_code

    def delete(self, url, **kwargs):
        if "auth" in kwargs:
            self.headers["Authorization"] = kwargs["auth"]
            del kwargs["auth"]

        r = requests.delete(url, verify=self.strict, params=kwargs, headers=self.headers, timeout=self.timeout)
        logging.info(r.request.url)

        if r.status_code == requests.codes.ok:
            return r.text

        # got something else other than 200 OK
        logging.error("Got code={0} response={1}".format(r.status_code, r.text))
        return r.status_code