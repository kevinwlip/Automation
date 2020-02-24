import jwt
import time
import hashlib


class JWTGenerator:

    def __init__(self, user, access_key, secret_key, canonical_path):
        self.user = user
        self.access_key = access_key
        self.secret_key = secret_key
        self.expire = 3600
        self.canonical_path = canonical_path

    @property
    def jwt(self):
        payload = {
            'sub': self.user,
            'qsh': hashlib.sha256(self.canonical_path.encode('utf-8')).hexdigest(),
            'iss': self.access_key,
            'exp': time.time()+self.expire,
            'iat': time.time()
        }
        token = jwt.encode(payload, self.secret_key, algorithm='HS256')
        return token

    @property
    def headers(self):
        headers = {
            'Authorization': 'JWT '+self.jwt,
            'zapiAccessKey': self.access_key
        }
        return headers

