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


class TeamModel(Schema):
    type = 'object'
    properties = {
        'name': {
            'type': 'string',
        },
        'founded_at' : {
            'type': 'object',
        },
        'chairman': {
            'type': 'string',
        },
        'owner': {
            'type': 'string',
        },
        'website': {
            'type': 'string',
        },
        'worldfootball_url': {
            'type': 'string',
        },
        'whoscored_url': {
            'type': 'string',
        },
        'wikipedia_url': {
            'type': 'string',
        },
    }


class PlayerModel(Schema):
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


def serialize_team(team):
    return {
        'name': team['ns0__name'],
        'founded_at': team['ns0__FoundedAt'].isoformat(),
        'chairman': team['ns0__Chairman'],
        'owner': team['ns0__owner'],
        'website': team['ns0__Website'],
        'worldfootball_url': team['ns0__worldfootball_url'],
        'whoscored_url': team['ns0__whoscored_url'],
        'wikipedia_url': team['ns0__wikipedia_url'],
    }


class ApiDocs(Resource):
    def get(self, path=None):
        if not path:
            path = 'index.html'
        return send_from_directory('swaggerui', path)


class TeamInformation(Resource):
    @swagger.doc({
        'tags': ['team information'],
        'summary': 'Team information',
        'description': 'Returns information of team',
        'parameters': [
            {
                'name': 'team',
                'description': 'team name',
                'in': 'query',
                'type': 'string',
                'required': True,
            }
        ],
        'responses': {
            '200': {
                'description': 'Team information',
                'schema': TeamModel,
            }
        }
    })
    def get(self):
        team = request.args['team']

        def get_team(tx, team):
            return list(tx.run(
                '''
                MATCH (n:ns1__SportsTeam)
                WHERE toLOWER(n.ns0__name) = toLower($team)
                RETURN n
                ''', {'team': team}
            ))

        db = get_db()
        result = db.read_transaction(get_team, team)
        print(result)
        return {"data":[serialize_team(record['n']) for record in result]}


api.add_resource(ApiDocs, '/docs', '/docs/<path:path>')
api.add_resource(TeamInformation, '/api/v0/team')

