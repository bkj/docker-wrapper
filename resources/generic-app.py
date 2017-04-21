#!/usr/bin/env python

"""
    generic-app.py
"""

from __future__ import division
import sys
import json
import argparse
import logging
from gunicorn_app import GunicornApplication
from gunicorn.glogging import loggers

from flask import abort
from flask import Flask, make_response, jsonify
from flask_restful import Api, Resource, reqparse
from flask_restful.representations.json import output_json

from redis_external import RedisExternal

output_json.func_globals['settings'] = {
    'ensure_ascii' : False,
    'encoding' : 'utf8'
}

app = Flask(__name__)
api = Api(app)

logging.basicConfig(format='%(levelname)s %(asctime)s %(filename)s %(lineno)d: %(message)s')
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

# --
# CLI Interface

def parse_arguments():
    parser = argparse.ArgumentParser(description='Generic classifier')
    parser._optionals.title = 'Options'
    parser.add_argument('-l', '--listen-host', help="Listen host", default="0.0.0.0:5000")
    parser.add_argument('-d', '--debug', help="Run in debug mode", action="store_true")
    parser.add_argument('-t', '--threads', help="Gunicorn threads", type=int, default=1)
    parser.add_argument('-w', '--workers', help="Gunicorn workers", type=int, default=1)
    parser.add_argument('-s', '--statsd-host', help="Statsd host", type=str)
    parser.add_argument('-p', '--prefix-statsd', help="Statsd prefix", type=str)
    return parser.parse_args()

# --
# Endpoints

class HealthCheck(Resource):
    def get(self):
        return make_response(jsonify({"status": "ok"}), 200)

class ModelAPI(Resource):
    def __init__(self, **kwargs):
        self.config = kwargs['config']
        self.external = RedisExternal()
        self.reqparse = reqparse.RequestParser()
        
        for rest_arg in self.config['rest_args']:
            if rest_arg.has_key('type'):
                self.reqparse.add_argument(rest_arg['field'], type=eval(rest_arg['type']), location=rest_arg['location'])
            else:
                self.reqparse.add_argument(rest_arg['field'], location=rest_arg['location'])
        
        super(ModelAPI, self).__init__()
        
    def post(self):
        args = self.reqparse.parse_args()
        print args
        response_queue = self.external.rand_write(args)
        res = self.external.read(queue=response_queue)
        req, pred, err = res
        if err:
            abort(err)
        else:
            return pred

# --
# Error handling

@app.errorhandler(400)
def bad_request(error):
    return make_response(jsonify({'error': 'Bad request'}), 400)

@app.errorhandler(404)
def not_found(error):
    return make_response(jsonify({'error': 'Not found'}), 404)


# --
# Run

if __name__ == '__main__':
    logger.info('Loading config.')
    config = json.load(open('/src/config.json'))
    args = parse_arguments()
    
    hostport = args.listen_host.split(':')
    port = int(hostport[1]) if len(hostport) == 2 else 5000
    
    logger.info('adding /api/health')
    api.add_resource(HealthCheck, '/api/health')
    options = {
        'bind': '{}:{}'.format(hostport[0], port),
        'threads': args.threads,
        'workers': args.workers
    }
    
    logger.info('adding /api/score')
    api.add_resource(ModelAPI, '/api/score', resource_class_kwargs={
        'config' : config
    })
    
    if args.statsd_host:
        options['statsd_host'] = args.statsd_host
    if args.prefix_statsd:
        options['statsd_prefix'] = args.prefix_statsd
    if args.debug:
        options['loglevel'] = 'debug'
    
    GunicornApplication(app, options).run()
