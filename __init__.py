from flask import Flask, redirect, jsonify
from flasgger import Swagger
from flask import request
from flask import app
from server.routes.prometheus import track_requests
import sys
sys.path.append ("/project/userapp/libraries")
import engine
import json
from flask_cors import CORS, cross_origin
import os
from logging.config import dictConfig
from pino import pino

dictConfig({
    'version': 1,
    'formatters': {'default': {
        'format': '[%(asctime)s] %(levelname)s in %(module)s: %(message)s',
    }},
    'handlers': {'wsgi': {
        'class': 'logging.StreamHandler',
        'stream': 'ext://flask.logging.wsgi_errors_stream',
        'formatter': 'default'
    }},
    'root': {
        'level': 'INFO',
        'handlers': ['wsgi']
    }
})
# The python-flask stack includes the flask extension flasgger, which will build
# and publish your swagger ui and specification at the /apidocs url. Here we set up
# the basic swagger attributes, which you should modify to match you application.
# See: https://github.com/rochacbruno-archive/flasgger
swagger_template = {
  "swagger": "2.0",
  "info": {
    "title": "Example API for python-flask stack",
    "description": "API for helloworld, plus health/monitoring",
    "contact": {
      "responsibleOrganization": "IBM",
      "responsibleDeveloper": "Henry Nash",
      "email": "henry.nash@uk.ibm.com",
      "url": "https://appsody.dev",
    },
    "version": "0.2"
  },
  "schemes": [
    "http"
  ],
}

logger = pino(
    bindings={"service": "k8smanager"}
)

app = Flask(__name__)
CORS(app)
swagger = Swagger(app, template=swagger_template)
# The python-flask stack includes the prometheus metrics engine. You can ensure your endpoints
# are included in these metrics by enclosing them in the @track_requests wrapper.

@app.route('/create_user', methods = ['POST'])
@cross_origin(origin='*',headers=['Content-Type','Authorization'])
@track_requests
def _create_user():
    data  = json.loads(request.data.decode("utf-8"))
    logger.info({'reqID': data['req_id'],'user':data['user'],'status': 'received'}, "Create user workspace for user: {} and course: {}".format(data['user'],data['course']['text']))
    result = engine.user_create(data['user'],data['course']['text'],data['req_id'])
    logger.info({'reqID': data['req_id'],'user':data['user'],'status': 'returned'}, "Create user workspace for user: {} and course: {}".format(data['user'],data['course']['text']))
    return result

@app.route('/')
def index():
    return redirect('/apidocs')

# If you have additional modules that contain your API endpoints, for instance
# using Blueprints, then ensure that you use relative imports, e.g.:
# from .mymodule import myblueprint
