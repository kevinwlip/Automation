# Import system default
import urllib.request, urllib.parse, urllib.error
import urllib.request, urllib.error, urllib.parse
import json

getTokenUrl = '/oauth_token.do?grant_type=password'
getSecurityEventUrl = '/api/x_ctv_sc/zingbox/getSecurityEvents?business_unit={}&active={}&limit={}'

class Connectiv:

    def __init__(self, host, username, password, client_id, client_secret):
        self.host = host
        self.token = self._getToken(username, password, client_id, client_secret)

    def _getToken(self, username, password, client_id, client_secret):
        if username is None:
            print('Connectiv/_getToken: username is None.')
            return ''
        elif password is None:
            print('Connectiv/_getToken: password is None.')
            return ''
        elif client_id is None:
            print('Connectiv/_getToken: client_id is None.')
            return ''
        elif client_secret is None:
            print('Connectiv/_getToken: client_secret is None.')
            return ''

        headers = {
            'Accept' : 'application/json',
            'Content-Type' : 'application/x-www-form-urlencoded'
        }

        params = {
            'client_id' : client_id,
            'client_secret' : client_secret,
            'username' : username,
            'password' : password
        }

        data = urllib.parse.urlencode(params)
        req = urllib.request.Request(self.host + getTokenUrl, data, headers)
      
        response = urllib.request.urlopen(req)
        result = response.read()
       
        return json.loads(result)['access_token']

    def getSecurityEvent(self, business_unit='htm', active=True, limit=100):
        print((self.token))
        if active is True:
            active = 'true'
        else:
            active = 'false'
        headers = {
            'Authorization': 'Bearer ' + self.token,
            'Content-Type' : 'application/json'
        }

        req = urllib.request.Request(
            (self.host + getSecurityEventUrl).format(business_unit, active, limit),
            None,
            headers
        )
             
        response = urllib.request.urlopen(req)
        result = response.read()

        return json.loads(result)['result']

'''
if __name__ == "__main__":
    connectiv = Connectiv(
      'https://ven01658.service-now.com',
      'zingbox',
      'PWD',
      'CLIENT_ID',
      'CLIENT_SECRET'
    )
    events = connectiv.getSecurityEvent()
    print(events)
'''
