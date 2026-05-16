from flask import jsonify
from flask_restful import reqparse, abort, Resource
from flask import request 

from . import db_session
from .__all_models import Excuse



parser = reqparse.RequestParser()
parser.add_argument('id', required=False, type=int)
parser.add_argument('author', required=False, type=str)
parser.add_argument('content', required=False, type=str)
parser.add_argument('rating', required=False, type=int)
parser.add_argument('is_prime', required=False, type=bool)
parser.add_argument('profession', required=True, type=str) 


def abort_if_excuse_not_found(excuse_id):
    session = db_session.create_session()
    excuse = session.get(Excuse, excuse_id)
    if not excuse:
        abort(404, message=f"excuse {excuse_id} not found")


class ExcuseResource(Resource):
    def get(self, excuse_id):
        abort_if_excuse_not_found(excuse_id)
        session = db_session.create_session()
        excuse = session.get(Excuse, excuse_id)
        return jsonify({'excuse': excuse.to_dict(
            only=('id', 'author', 'content', 'rating', 'is_prime', 'profession'))})

    def delete(self, excuse_id):
        abort_if_excuse_not_found(excuse_id)
        session = db_session.create_session()
        excuse = session.get(Excuse, excuse_id)
        session.delete(excuse)
        session.commit()
        return jsonify({'success': 'OK'})


class ExcusesListResource(Resource):
    def get(self):
        session = db_session.create_session()
        prof = request.args.get('profession') 
        
        if prof:
            excuses = session.query(Excuse).filter(Excuse.profession == prof).all()
        else:
            excuses = session.query(Excuse).all()
            
        return jsonify({'excuses': [item.to_dict(
            only=('id', 'author', 'content', 'rating', 'is_prime', 'profession')) 
            for item in excuses]})

    def post(self):
        args = parser.parse_args()
        excuse = Excuse(
            id=args.get('id'),
            author=args['author'],
            content=args['content'],
            rating=args['rating'],
            is_prime=args['is_prime'],
            profession=args['profession']
        )
        session = db_session.create_session()
        session.add(excuse)
        session.commit()
        return jsonify({'id': excuse.id})
