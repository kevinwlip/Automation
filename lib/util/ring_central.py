#!/usr/bin/python

from common.zbConfig import defaultEnv
import requests, os, datetime

import logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

env = defaultEnv()

import urllib3

# Suppress InsecureRequestWarning: Unverified HTTPS request is made in this module
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


class RingCentral:

    def __init__(self, **kwargs):  # since kwargs can be empty, need to handle case when no params
        logger.info('RingCentral instance is initialized to receive SMS code')
        self.headers = {
            'Accept': 'application/json',
            'Content-Type': 'application/json'
        }

        self.url = kwargs["url"] if "url" in kwargs else env['ring_central_api']
        self.kwargs = dict()
        self.kwargs["auth"] = kwargs["auth"] if "auth" in kwargs else os.environ['RING_CENTRAL_AUTH_TOKEN']
        self.kwargs["password"] = kwargs["password"] if "password" in kwargs else os.environ['RING_CENTRAL_PWD']
        self.kwargs["username"] = kwargs["username"] if "username" in kwargs else os.environ['RING_CENTRAL_ACCOUNT']
        self.kwargs["extension"] = kwargs["extension"] if "extension" in kwargs else os.environ['RING_CENTRAL_EXT']

        try:
            self._authenticate()
        except Exception as e:
            logger.critical(e.message)

    def _get_sms(self, **kwargs):  # maybe use currentuser to set specific accountid and extensionid
        self.headers['Cache-Control'] = 'no-cache'

        accountid = '~' if not 'accountid' in kwargs else kwargs['accountid']
        extensionid = '~' if not 'extensionid' in kwargs else kwargs['extensionid']
        url = self.url + 'v1.0/account/' + accountid + '/extension/' + extensionid + '/sms'

        r = requests.get(url, params=kwargs, headers=self.headers, verify=False)

        if r.status_code is not requests.codes.ok:
            logger.critical(r, r.json()['errors'])
            logger.critical('Retrieve message list failed')
            return r.status_code

        logger.info('Response [{}]'.format(r.status_code))
        return r.json()

    def _authenticate(self):
        # self.kwargs should contain
        '''
        {
            'username': RING_CENTRAL_USER,
            'extension': RING_CENTRAL_EXT,
            'password': RING_CENTRAL_PW,
            'auth': RING_CENTRAL_AUTH_TOKEN
        }
        '''

        rcode = self._token_pw_flow()

        if rcode is False:
            raise Exception('Authentication failed')

        logger.info('access token authorized')
        self.headers['Authorization'] = 'Bearer ' + rcode

    def _token_pw_flow(self):
        self.headers['Content-Type'] = 'application/x-www-form-urlencoded'
        if 'auth' in self.kwargs:
            self.headers['Authorization'] = 'Basic ' + str(self.kwargs['auth']) if 'Basic' not in self.kwargs[
                'auth'] else str(self.kwargs['auth'])

        url = self.url + 'oauth/token'
        self.kwargs['grant_type'] = 'password'

        r = requests.post(url, headers=self.headers, data=self.kwargs, timeout=3, verify=False)

        if r.status_code is not requests.codes.ok:
            logger.info(r, r.json()['errors'])
            return False

        # return refresh token as well if needed
        return r.json()['access_token']

    def get_2fa_code(self):
        # query params for ring central Get Message List api
        message_list_query = {
            'availability': 'Alive',
            'direction': 'Inbound',
            'readStatus': 'Unread',
            'page': 1,
            'perPage': 10,
            'messageType': 'SMS',
            'distinctConversations': True,  # will retrieve latest message from each number
            'dateFrom': (datetime.datetime.utcnow() - datetime.timedelta(minutes=1500)).isoformat()  # IOS 8601
        }

        rcode = self._get_sms(**message_list_query)

        if isinstance(rcode, int):
            # get_sms method will return a dict if successful, error code if fail
            logger.error('Retrieve 2FA SMS code from Ring Central failed with error code: ' + str(rcode))
            return False

        logger.info(rcode['records'])
        for record in rcode['records']:
            if 'Your SMS code for Zingbox' in record['subject']:
                # api call for message list will return array of records sorted (desc) by creationTime
                # so first instance of Your SMS code for Zingbox should be newest 2FA code
                twofactor_code = record['subject']
                break

        # ring central developers app is stuck in sandbox mode so
        # all messages have this garbage string for sandbox accounts
        garbage_string = 'Test SMS using a RingCentral Developer account - Your SMS code for Zingbox is '
        return twofactor_code.replace(garbage_string, '')