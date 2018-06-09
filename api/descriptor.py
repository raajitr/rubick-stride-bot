import json
from flask import request, jsonify
from flask_restful import Resource


class Descriptor(Resource):

    def get(self):
        with open('/app/api/descriptor.json', 'r') as f:
            DESCRIPTOR = json.load(f)

        DESCRIPTOR['baseUrl'] = request.url_root
        return jsonify(DESCRIPTOR)


"""
{
    "chat:bot:messages": [
    {
        "key": "hello-ping",
        "pattern": "^(?i)(hello|hi|good m|hey|good e|good a).*$",
        "url": "/webhooks/message"
        },
        {
        "key": "thanks-ping",
        "pattern": "^.*(?i)(thank(s| you)).*$",
        "url": "/webhooks/message/thanks"
        }
    ],
}
"""
