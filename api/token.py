"""
Each request from Stride to your app contains a JWT token with the context of the call.
Validating this token ensures the request comes from Stride.
"""
import os
import json
import jwt
import requests
from flask import request

CLIENT_ID = os.environ['CLIENT_ID']
CLIENT_SECRET = os.environ['CLIENT_SECRET']


class StrideJWT(object):
    def __init__(self, *args, **kwargs):
        self.stride_context = self.get_context()

    def get_context(self):
        encoded_jwt = request.headers['Authorization'].split()[-1]
        try:
            decoded_jwt = jwt.decode(encoded_jwt, CLIENT_SECRET) # Verification is optional, but still verifying
            decoded_jwt = decoded_jwt['context']
        except jwt.InvalidTokenError:
            decoded_jwt = {'error': 'Invalid Token'}

        decoded_jwt.update({'access_token': self.get_access_token()})
        decoded_jwt.update(self.from_req_data())
        print decoded_jwt
        return decoded_jwt

    def get_access_token(self):
        header = {'content-type': 'application/json'}
        data = {
            'grant_type': 'client_credentials',
            'client_id': CLIENT_ID,
            'client_secret': CLIENT_SECRET
        }

        r = requests.post('https://api.atlassian.com/oauth/token',
                          json=data,
                          headers=header)

        return json.loads(r.text)['access_token']

    def from_req_data(self):
        req_data = json.loads(request.data)

        if not req_data.get('conversation') or not req_data.get('sender'):
            return {}
        
        return {
            "conversationId": req_data['conversation']['id'],
            "userId": req_data['sender']['id']
        }

        # url = 'https://api.atlassian.com/site/{cloudId}/conversation/user/{sub}'.format(**context)
        # r = requests.get(url, headers=headers)
        # print r.text
        # return json.loads(r.text)['id']
