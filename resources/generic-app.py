from __future__ import division
import sys
import json
import argparse
import logging
from gunicorn_app import GunicornApplication
from gunicorn.glogging import loggers
from flask import Flask, make_response, jsonify
from flask.ext.restful import Api, Resource, reqparse
from flask.ext.restful.representations.json import output_json

from model_class import apiModel

output_json.func_globals['settings'] = {
    'ensure_ascii' : False,
    'encoding' : 'utf8'
}

app = Flask(__name__)
api = Api(app)

logging.basicConfig(format='%(levelname)s %(asctime)s %(filename)s %(lineno)d: %(message)s')
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

def parse_arguments():
    parser = argparse.ArgumentParser(description='Generic classifier')
    parser._optionals.title = 'Options'
    parser.add_argument('-l', '--listen-host', help="Listen host", default="0.0.0.0:5000")
    parser.add_argument('-d', '--debug', help="Run in debug mode", action="store_true")
    parser.add_argument('-t', '--threads', help="Gunicorn threads", type=int, default=1)
    parser.add_argument('-w', '--workers', help="Gunicorn workers", type=int, default=1)
    parser.add_argument('-s', '--statsd-host', help="Statsd host", type=str)
    parser.add_argument('-p', '--prefix-statsd', help="Statsd prefix", type=str)
    parser.add_argument('-m', '--model', help='Specify model file.', type=str, required=True)
    return parser.parse_args()


class ClassifierAPI(Resource):
    def __init__(self, **kwargs):
        self.model = kwargs['model']
        self.config = kwargs['config']
        self.reqparse = reqparse.RequestParser()

        for rest_arg in self.config['rest_args']:
            if rest_arg.has_key('type'):
                self.reqparse.add_argument(rest_arg['field'], type=eval(rest_arg['type']), location=rest_arg['location'])
            else:
                self.reqparse.add_argument(rest_arg['field'], location=rest_arg['location'])

        super(ClassifierAPI, self).__init__()

    def post(self):
        args = self.reqparse.parse_args()
        return model.predict_api(**args)


class HealthCheck(Resource):
    def get(self):
        return make_response(jsonify({"status": "ok"}), 200)


@app.errorhandler(400)
def bad_request(error):
    return make_response(jsonify({'error': 'Bad request'}), 400)


@app.errorhandler(404)
def not_found(error):
    return make_response(jsonify({'error': 'Not found'}), 404)


if __name__ == '__main__':
    logger.info('Loading config.')
    config = json.load(open('/src/config.json'))

    logger.info('Starting service.')
    args = parse_arguments()

    hostport = args.listen_host.split(':')
    if len(hostport) == 2:
        port = int(hostport[1])
    else:
        port = 5000

    logger.info('Loading model.')
    model = apiModel(args.model, config['model_name'])

    logger.info('Starting service.')
    api.add_resource(ClassifierAPI, '/api/score', resource_class_kwargs={
        'model' : model,
        'config' : config
    })

    print loggers()

    api.add_resource(HealthCheck, '/api/health')
    options = {
        'bind': '{}:{}'.format(hostport[0], port),
        'threads': args.threads,
        'workers': args.workers
    }

    if args.statsd_host:
        options['statsd_host'] = args.statsd_host
    if args.prefix_statsd:
        options['statsd_prefix'] = args.prefix_statsd
    if args.debug:
        options['loglevel'] = 'debug'
    GunicornApplication(app, options).run()
