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
        'worldfootball_url': {
            'type': 'string',
        },
        'whoscored_url': {
            'type': 'string',
        },
        'birth_date': {
            'type': 'date',
        },
        'height': {
            'type': 'Float',
        },
        'foot': {
            'type': 'string',
        },
        'age': {
            'type': 'integer',
        }
    }

class TeamListModel(Schema):
    type = 'object'
    properties = {
        'team': {
            'type': 'string',
        }
    }

class BirthplaceModel(Schema):
    type = 'object'
    properties = {
        'birthplace': {
            'type': 'string',
        }
    }

class StyleModel(Schema):
    type = 'object'
    properties = {
        'style': {
            'type': 'string',
        }
    }

class RecordModel(Schema):
    type = 'object'
    properties = {
        'team': {
            'type': 'string',
        },
        'num_games': {
            'type': 'int',
        },
        'avg_rating': {
            'type': 'float',
        }
    }

class PlayerSkillModel(Schema):
    type = 'object'
    properties = {
        'name': {
            'type': 'string',
        },
        'strength': {
            'type': 'string',
        },
    }

class TeamBestModel(Schema):
    type = 'object'
    properties = {
        'name': {
            'type': 'string',
        },
        'avg_rating': {
            'type': 'float',
        },
    }

def serialize_athlete(athlete):
    return {
        'birth_date': athlete['ns1__birthDate'].isoformat(),
        'age': athlete['ns0__Age'],
        'height': athlete['ns1__height'],
        'foot': athlete['ns0__Foot'],
        'worldfootball_url': athlete['ns0__worldfootball_url'],
        'whoscored_url': athlete['ns0__whoscored_url'],
    }


def serialize_team(team):
    return {
        'founded_at': team['ns0__FoundedAt'].isoformat(),
        'chairman': team['ns0__Chairman'],
        'owner': team['ns0__owner'],
        'website': team['ns0__Website'],
        'worldfootball_url': team['ns0__worldfootball_url'],
        'whoscored_url': team['ns0__whoscored_url'],
        'wikipedia_url': team['ns0__wikipedia_url'],
    }

def serialize_team_season_list(team):
    return {
        'team': team['team'],
    }

def serialize_birthplace(player):
    return {
        'birthplace': player['birthplace'],
    }

def serialize_style(player):
    return {
        'style': player['style'],
    }

def serialize_record(player):
    return {
        'team': player['team'],
        'num_games': player['num_games'],
        'avg_rating': player['avg_rating'],
    }

def serialize_style_player(player):
    return {
        'name': player['name'],
        'strength': player['strength'],
    }

def serialize_team_best(player):
    return {
        'name': player['name'],
        'avg_rating': player['avg_rating'],
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
        return {"data":[serialize_team(record['n']) for record in result]}


class PlayerInformation(Resource):
    @swagger.doc({
        'tags': ['player information'],
        'summary': 'Player information',
        'description': 'Returns information of player',
        'parameters': [
            {
                'name': 'player',
                'description': 'player name',
                'in': 'query',
                'type': 'string',
                'required': True,
            }
        ],
        'responses': {
            '200': {
                'description': 'Player information',
                'schema': PlayerModel,
            }
        }
    })
    def get(self):
        player = request.args['player']

        def get_player(tx, player):
            return list(tx.run(
                '''
                MATCH (n:ns1__athlete)
                WHERE toLOWER(n.ns1__name) = toLower($player)
                RETURN n
                ''', {'player': player}
            ))

        db = get_db()
        result = db.read_transaction(get_player, player)
        print(result)
        return {"data":[serialize_athlete(record['n']) for record in result]}


class SeasonTeam(Resource):
    @swagger.doc({
        'tags': ['Season team list'],
        'summary': 'Season team list',
        'description': 'Returns list of team in the season',
        'parameters': [
            {
                'name': 'season',
                'description': 'season',
                'in': 'query',
                'type': 'string',
                'required': True,
            }
        ],
        'responses': {
            '200': {
                'description': 'Season team list',
                'schema': TeamListModel,
            }
        }
    })
    def get(self):
        season = request.args['season']

        def get_team(tx, season):
            return list(tx.run(
                '''
                MATCH (event:ns0__event)-[:ns0__awayTeam]->(team:ns1__SportsTeam), (event:ns0__event)-[:ns0__seasonOf]->(season:ns0__season)
                WHERE season.rdfs__label = $season
                RETURN distinct team.ns0__name as team
                ''', {'season': season}
            ))

        db = get_db()
        result = db.read_transaction(get_team, season)
        print(result)
        return {"data": [serialize_team_season_list(record) for record in result]}

class PlayerBirthplace(Resource):
    @swagger.doc({
        'tags': ['Birth place of Player'],
        'summary': 'Birth place of Player',
        'description': 'Returns Birth place of Player',
        'parameters': [
            {
                'name': 'player',
                'description': 'player',
                'in': 'query',
                'type': 'string',
                'required': True,
            }
        ],
        'responses': {
            '200': {
                'description': 'Birth place of player',
                'schema': BirthplaceModel,
            }
        }
    })
    def get(self):
        player = request.args['player']

        def get_birthplace(tx, player):
            return list(tx.run(
                '''
                MATCH (n:ns1__athlete)-[:ns1__birthPlace]->(a)
                WHERE toLOWER(n.ns1__name) = toLOWER($player)
                return a.rdfs__label as birthplace
                ''', {'player': player}
            ))

        db = get_db()
        result = db.read_transaction(get_birthplace, player)
        print(result)
        return {"data": [serialize_birthplace(record) for record in result]}

class PlayerStyle(Resource):
    @swagger.doc({
        'tags': ['Play style of Player'],
        'summary': 'Play style of Player',
        'description': 'Returns Play style of Player',
        'parameters': [
            {
                'name': 'player',
                'description': 'player',
                'in': 'query',
                'type': 'string',
                'required': True,
            }
        ],
        'responses': {
            '200': {
                'description': 'Play style of Player',
                'schema': StyleModel,
            }
        }
    })
    def get(self):
        player = request.args['player']

        def get_style(tx, player):
            return list(tx.run(
                '''
                MATCH (n:ns1__athlete)-[:ns0__Style_of_Play]-(a)
                WHERE toLOWER(n.ns1__name) = toLOWER($player)
                return a.ns0__Style_of_Play as style
                ''', {'player': player}
            ))

        db = get_db()
        result = db.read_transaction(get_style, player)
        print(result)
        return {"data": [serialize_style(record) for record in result]}


class PlayerRecord(Resource):
    @swagger.doc({
        'tags': ['Play record of Player against Team'],
        'summary': 'Play record of Player against Team',
        'description': 'Returns Play record of Player against Team',
        'parameters': [
            {
                'name': 'player',
                'description': 'player',
                'in': 'query',
                'type': 'string',
                'required': True,
            }
        ],
        'responses': {
            '200': {
                'description': 'Play style of Player',
                'schema': RecordModel,
            }
        }
    })
    def get(self):
        player = request.args['player']

        def get_records(tx, player):
            return list(tx.run(
                '''
                MATCH (n:ns1__athlete)-[:ns0__participate_in]->(a)-[:ns0__participate_in]->(event:ns0__event), (a)-[:ns0__teamAgainst]->(team:ns1__SportsTeam)
                WHERE toLOWER(n.ns1__name) = toLOWER($player)
                return n.ns1__name as player, team.ns0__name as team, count(a) as num_games, avg(toFloat(a.ns0__rating)) as avg_rating
                ''', {'player': player}
            ))

        db = get_db()
        result = db.read_transaction(get_records, player)
        print(result)
        return {"data": [serialize_record(record) for record in result]}

class PlayerSkill(Resource):
    @swagger.doc({
        'tags': ['Players who has skill in Team'],
        'summary': 'Players who has skill in Team',
        'description': 'Returns Players who has skill in Team',
        'parameters': [
            {
                'name': 'team',
                'description': 'team',
                'in': 'query',
                'type': 'string',
                'required': True,
            },
            {
                'name': 'skill',
                'description': 'skill',
                'in': 'query',
                'type': 'string',
                'required': True,
            }
        ],
        'responses': {
            '200': {
                'description': 'Players who has skill in Team',
                'schema': PlayerSkillModel,
            }
        }
    })
    def get(self):
        team = request.args['team']
        skill = request.args['skill']

        def get_records(tx, team, skill):
            return list(tx.run(
                '''
                MATCH (n:ns1__athlete)-[:ns0__strength]->(a), (n)-[:ns0__Current_Team]->(team)
                WHERE toLOWER(team.ns0__team_name) = toLOWER($team) and toLower(a.ns0__strength) contains toLower($skill)
                return n.ns1__name as name, a.ns0__strength as strength
                ''', {'team': team, 'skill': skill}
            ))

        db = get_db()
        result = db.read_transaction(get_records, team, skill)
        print(result)
        return {"data": [serialize_style_player(record) for record in result]}


class BestPlayer(Resource):
    @swagger.doc({
        'tags': ['Best players in [Team1] against [Team2]'],
        'summary': 'Best players in [Team1] against [Team2]',
        'description': 'Best players in [Team1] against [Team2]',
        'parameters': [
            {
                'name': 'team1',
                'description': 'team1',
                'in': 'query',
                'type': 'string',
                'required': True,
            },
            {
                'name': 'team2',
                'description': 'team2',
                'in': 'query',
                'type': 'string',
                'required': True,
            }
        ],
        'responses': {
            '200': {
                'description': 'Best players in [Team1] against [Team2]',
                'schema': TeamBestModel,
            }
        }
    })
    def get(self):
        team1 = request.args['team1']
        team2 = request.args['team2']

        def get_records(tx, team1, team2):
            return list(tx.run(
                '''
                MATCH (player:ns1__athlete)-[:ns0__Current_Team]->(a)-[:ns0__memberOf]->(team:ns1__SportsTeam), (player)-[:ns0__participate_in]->(blank)-[:ns0__participate_in]->(event:ns0__event), (blank)-[:ns0__teamAgainst]->(team2:ns1__SportsTeam)
                WHERE toLOWER(team.ns0__name) = toLOWER($team1) and toLOWER(team2.ns0__name) = toLOWER($team2)
                return player.ns1__name as name, avg(toFloat(blank.ns0__rating)) as avg_rating
                order by avg_rating desc
                ''', {'team1': team1, 'team2': team2}
            ))

        db = get_db()
        result = db.read_transaction(get_records, team1, team2)
        print(result)
        return {"data": [serialize_team_best(record) for record in result]}


api.add_resource(ApiDocs, '/docs', '/docs/<path:path>')
api.add_resource(PlayerInformation, '/api/v0/player')
api.add_resource(TeamInformation, '/api/v0/team')
api.add_resource(SeasonTeam, '/api/v0/season')
api.add_resource(PlayerBirthplace, '/api/v0/birthplace')
api.add_resource(PlayerStyle, '/api/v0/style')
api.add_resource(PlayerRecord, '/api/v0/record')
api.add_resource(PlayerSkill, '/api/v0/skill')
api.add_resource(BestPlayer, '/api/v0/best')

