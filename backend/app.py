import binascii
import hashlib
import os
import ast
import re
import sys
import uuid
from dotenv import load_dotenv, find_dotenv
from datetime import datetime
from functools import wraps

from flask import Flask, g, request, send_from_directory, abort, request_started
from flask_cors import CORS
from flask_restful import Resource, reqparse
from flask_restful_swagger_2 import Api, swagger, Schema
from flask_json import FlaskJSON, json_response

from neo4j import GraphDatabase, basic_auth
from neo4j.exceptions import Neo4jError
import neo4j.time

load_dotenv(find_dotenv())

app = Flask(__name__)

CORS(app)
FlaskJSON(app)

api = Api(app, title='Neo4j EPL Demo API', api_version='0.0.10')


@api.representation('application/json')
def output_json(data, code, headers=None):
    return json_response(data_=data, headers_=headers, status_=code)


def env(key, default=None, required=True):
    """
    Retrieves environment variables and returns Python natives. The (optional)
    default will be returned if the environment variable does not exist.
    """
    try:
        value = os.environ[key]
        return ast.literal_eval(value)
    except (SyntaxError, ValueError):
        return value
    except KeyError:
        if default or not required:
            return default
        raise RuntimeError("Missing required environment variable '%s'" % key)


DATABASE_USERNAME = env('DATABASE_USERNAME')
DATABASE_PASSWORD = env('DATABASE_PASSWORD')
DATABASE_URL = env('DATABASE_URL')

driver = GraphDatabase.driver(DATABASE_URL, auth=basic_auth(DATABASE_USERNAME, str(DATABASE_PASSWORD)))


def get_db():
    if not hasattr(g, 'neo4j_db'):
        g.neo4j_db = driver.session()
    return g.neo4j_db


@app.teardown_appcontext
def close_db(error):
    if hasattr(g, 'neo4j_db'):
        g.neo4j_db.close()


class AthleteModel(Schema):
    type = 'object'
    properties = {
        'label': {
            'type': 'string',
        },
        'worldfootball_url': {
            'type': 'string',
        },
        'whoscored_url': {
            'type': 'string',
        },
        'name' : {
            'type': 'string',
        },
        'birthDate': {
            'type': 'date',
        },
        'Placeofbirth': {
            'type': 'object',
        },
        'nationality': {
            'type': 'object',
        },
        'height': {
            'type': 'Float',
        },
        'weight': {
            'type': 'Float',
        },
        'position': {
            'type': 'object',
        },
        'foot': {
            'type': 'string',
        },
        'age': {
            'type': 'integer',
        }
    }

def serialize_athlete(athlete):
    return {
        'label': athlete['label'],
        'worldfootball_url': athlete['worldfootball_url'],
        'whoscored_url': athlete['whoscored_url'],
        'name': athlete['name'],
        'birthDate': athlete['birthDate'],
        'Placeofbirth': athlete['Placeofbirth'],
        'nationality': athlete['nationality'],
        'height': athlete['height'],
        'weight': athlete['weight'],
        'position': athlete['position'],
        'foot': athlete['foot'],
        'age': athlete['age'],
    }


class ApiDocs(Resource):
    def get(self, path=None):
        if not path:
            path = 'index.html'
        return send_from_directory('swaggerui', path)


class AthleteList(Resource):
    @swagger.doc({
        'tags': ['athletes'],
        'summary': 'Find all athletes',
        'description': 'Returns all athletes',
        'responses': {
            '200': {
                'description': 'A list of athletes',
                'schema': AthleteModel,
            }
        }
    })
    def get(self):
        def get_athletes(tx):
            return list(tx.run("match (n:ns0__athlete)-[r:ns0__nationality]-(a:ns0__Country{rdfs__label:'England'}) return n limit 5"))
        db = get_db()
        result = db.write_transaction(get_athletes)
        print(result)
        return [serialize_athlete(record['athlete']) for record in result]


api.add_resource(ApiDocs, '/docs', '/docs/<path:path>')
api.add_resource(AthleteList, '/api/v0/athletes')

