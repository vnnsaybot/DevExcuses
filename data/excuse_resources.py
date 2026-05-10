import datetime
from flask import jsonify
from flask_restful import reqparse, abort, Resource

from . import db_session
from .__all_models import Excuse


def parse_date(s):
    return datetime.datetime.fromisoformat(s)


parser = reqparse.RequestParser()
parser.add_argument('id', required=False, type=int)
parser.add_argument('author', required=True, type=str)
parser.add_argument('content', required=True, type=str)
parser.add_argument('rating', required=True, type=int)
parser.add_argument('likes', required=True, type=int)
parser.add_argument('dislikes', required=True, type=int)
parser.add_argument('is_prime', required=True, type=bool)


def abort_if_excuses_not_found(excuses_id):
    session = db_session.create_session()
    jobs = session.get(Excuse, excuses_id)
    if not jobs:
        abort(404, message=f"excuses {excuses_id} not found")


class ExcusesResource(Resource):
    def get(self, excuses_id):
        abort_if_excuses_not_found(excuses_id)
        session = db_session.create_session()
        excuses = session.get(Excuse, excuses_id)
        return jsonify({'excuses': excuses.to_dict(
            only=('id', 'author', 'content', 'rating', 'likes', 'dislikes', 'is_prime'))})

    def delete(self, excuses_id):
        abort_if_excuses_not_found(excuses_id)
        session = db_session.create_session()
        excuses = session.get(Excuse, excuses_id)
        session.delete(excuses)
        session.commit()
        return jsonify({'success': 'OK'})


class ExcusesListResource(Resource):
    def get(self):
        session = db_session.create_session()
        excuses = session.query(Excuse).all()
        return jsonify({'jobs': [item.to_dict(
            only=('id', 'author', 'content', 'rating', 'likes', 'dislikes',
                   'is_prime')) for item in excuses]})

    def post(self):
        args = parser.parse_args()
        excuses = Excuse(
            id=args.get('id'),
            author=args['author'],
            content=args['content'],
            rating=args['rating'],
            likes=args['likes'],
            dislikes=args['dislikes'],
            is_prime=args['is_prime']
        )
        session = db_session.create_session()
        session.add(excuses)
        session.commit()
        return jsonify({'id': 1})
