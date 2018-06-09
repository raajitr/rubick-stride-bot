# -*- coding: utf-8 -*-
import logging
import os
import sys
import json
from datetime import datetime
from flask import Flask, request, Response, url_for, jsonify, send_from_directory, render_template
from flask_restful import Api, Resource
from flask_pymongo import PyMongo

from api import application, cache
from api.descriptor import Descriptor
from api.webhooks import Webhooks
from api.lifecycle import Lifecycle

static_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "static")
template_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "template")

print "STATIC DIR: {}".format(static_dir)
print "TEMPLATE DIR: {}".format(template_dir)

application.logger.addHandler(logging.StreamHandler(sys.stdout))
application.logger.setLevel(logging.INFO)

@application.before_request
def before():
    req_data = None
    try:
        req_data = json.loads(str(request.data))
        application.logger.info("XDBG REQUEST= `{}` {}: {}".format(request.method, request.path, req_data))
    except Exception as e:
        application.logger.info("XDBG REQUEST= {}".format(request.path))
    application.logger.info("XDBG REQUEST_HEADER= {}".format(request.headers))

    if request.path == '/lifecycle/installed':
        return jsonify({"message": "working"})

    if req_data and req_data.get('message'):
        last_message = cache.get('last_message')
        if last_message == req_data['message']['ts']:
            raise Exception('Same message')
        cache.set('last_message', req_data['message']['ts'])


@application.after_request
def after(response):
    application.logger.info("XDBG RESPONSE= PATH: {}, STATUS: {}, DATA: {}".format(request.path, response.status, response.get_data()))
    return response


@application.errorhandler(Exception)
def handle_error(e):
    application.logger.info("XDBG EXCEPTION= {}".format(str(e)))
    if e.__class__.__name__ == 'MongoException':
        return Response(json.dumps({'info': 'INTERNAL SERVER info (CHECK LOGS)'}), status=200, mimetype='application/json')

    return Response(json.dumps({'info': 'INTERNAL SERVER info (CHECK LOGS)'}), status=500, mimetype='application/json')

class Index(Resource):
    def get(self):
        return jsonify({"message": "working"})


api = Api(application)
api.add_resource(Index, "/", endpoint="index")
api.add_resource(Descriptor, "/descriptor")
api.add_resource(Lifecycle, "/lifecycle/installed")
api.add_resource(Webhooks, "/webhooks/<string:webhook_type>", endpoint="webhooks")
api.add_resource(Webhooks, "/webhooks/message/<string:thanks>", endpoint="thanks")

@application.route('/dialog')
def dialog():
    return render_template("dialog.html")


if __name__ == "__main__":
    port = int(os.environ.get('PORT', 5000))
    application.run(host='0.0.0.0', port=port)
