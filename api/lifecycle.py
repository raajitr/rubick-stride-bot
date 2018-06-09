import requests

from flask import jsonify, Response
from flask_restful import Resource

from token import StrideJWT


class Lifecycle(Resource):
    def post(self, webhook_type=None):
        s_jwt = StrideJWT()
        context = s_jwt.stride_context
        url = 'https://api.atlassian.com/site/{cloudId}/conversation/{conversationId}/message'.format(**context)
        headers = {
        'authorization': 'Bearer {}'.format(context['access_token']),
        'content-type': 'text/plain'
        }
        data = 'I\'ve been deployed'

        r = requests.post(url, headers=headers, data=data)
