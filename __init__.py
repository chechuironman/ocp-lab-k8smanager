from flask import Flask, redirect, jsonify
from flasgger import Swagger
from flask import request
from flask import app
from server.routes.prometheus import track_requests
import sys
# import kubernetes
sys.path.append ("/project/userapp/libraries")
import engine,register
import json
from flask_cors import CORS, cross_origin
import os
from logging.config import dictConfig

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



# cors = CORS(app, resources={r"/": {"origins": "*"}})
# app.config['CORS_HEADERS'] = 'Content-Type'
app = Flask(__name__)
CORS(app)
swagger = Swagger(app, template=swagger_template)
# The python-flask stack includes the prometheus metrics engine. You can ensure your endpoints
# are included in these metrics by enclosing them in the @track_requests wrapper.
@app.route('/hello')
@track_requests
def HelloWorld():
    # To include an endpoint in the swagger ui and specification, we include a docstring that
    # defines the attributes of this endpoint.
    """A hello message
    Example endpoint returning a hello message
    ---
    responses:
      200:
        description: A successful reply
        examples:
          text/plain: Hello from Appsody!
    """
    return 'Hello from Appsody!'

@app.route('/namespaces')
@cross_origin(origin='*',headers=['Content-Type','Authorization'])
@track_requests
def _namespaces():
    response = engine.namespaces()
    print(response)
    return response
# It is considered bad form to return an error for '/', so let's redirect to the apidocs
@app.route('/create_user', methods = ['POST'])
@cross_origin(origin='*',headers=['Content-Type','Authorization'])
@track_requests
def _create_user():
    data  = json.loads(request.data.decode("utf-8"))
    app.logger.info('creating userv%s ', data['user'])
    print(data)
    # print(data['course']['text'])
    result = engine.user_create(data['user'],data['course']['text'])
    return result
@app.route('/course_info', methods = ['POST'])
# @cross_origin(origin='*',headers=['Content-Type','Authorization'])
@track_requests
def _course_info():
    data  = json.loads(request.data.decode("utf-8"))
    print(data)

    # print(data['course']['text'])
    # if data['selectedItem']:
    result = engine.course_info(data['user'],data['courseName'])
    return jsonify({"result": result}), 200
    # else:
    #   return(json.dumps({'loaded': 'False'}))
# @app.route('/register_user', methods = ['POST'])
# @cross_origin(origin='*',headers=['Content-Type','Authorization'])
# @track_requests
# def _regiser_user():
#     result  = json.loads(request.data.decode("utf-8"))
#     print(result)
#     response = register.register_user(result)
#     print(response)
#     return str(response)
@app.route('/')
def index():
    return redirect('/apidocs')

# If you have additional modules that contain your API endpoints, for instance
# using Blueprints, then ensure that you use relative imports, e.g.:
# from .mymodule import myblueprint
