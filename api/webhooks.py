import requests
import json

from flask import jsonify, Response, request
from flask_restful import Resource

from token import StrideJWT
from mentions import Mentions

class Webhooks(Resource):
    def post(self, webhook_type=None, thanks=None):
        s_jwt = StrideJWT()
        context = s_jwt.stride_context

        if 'error' in context:
            return Response('ERROR', status=500, mimetype='application/json')

        if webhook_type == 'mention':
            return self.mention(context)
        elif webhook_type == 'message':
            return self.message(context)
        elif thanks:
            return self.message(context, data="No Worries! :)")
        else:
            return jsonify({'error': 'nothing_mentioned'})

    def mention(self, context):
        mention_message = Mentions(request.data)

        url = 'https://api.atlassian.com/site/{cloudId}/conversation/{conversationId}/message'.format(**context)
        headers = {
        'authorization': 'Bearer {}'.format(context['access_token']),
        'content-type': mention_message.type
        }
        data = mention_message.text

        r = requests.post(url, headers=headers, data=data)

        print r.text

    def message(self, context, data=None):
        url = 'https://api.atlassian.com/site/{cloudId}/conversation/{conversationId}/message'.format(**context)
        headers = {
        'authorization': 'Bearer {}'.format(context['access_token']),
        'content-type': 'text/plain'
        }
        print context['access_token']

        userId = json.loads(request.data)['sender']['id']
        if userId == '5a26734395dac237f1299f01':
            data = data or 'Hi!'
        else:
            data = data or 'Hi!\n-Raajit'

        r = requests.post(url, headers=headers, data=data)

        print r.text
