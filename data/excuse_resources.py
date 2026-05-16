from flask import jsonify, request
from flask_restful import reqparse, abort, Resource

from . import db_session
from .__all_models import Excuse, Profession 

parser = reqparse.RequestParser()
parser.add_argument('id', required=False, type=int)
parser.add_argument('author', required=False, type=str)
parser.add_argument('content', required=False, type=str)
parser.add_argument('rating', required=False, type=int)
parser.add_argument('is_prime', required=False, type=bool)
parser.add_argument('profession_id', required=True, type=int)


def abort_if_excuse_not_found(excuse_id):
    session = db_session.create_session()
    excuse = session.get(Excuse, excuse_id)
    session.close()
    if not excuse:
        abort(404, message=f"excuse {excuse_id} not found")


class ExcuseResource(Resource):
    def get(self, excuse_id):
        abort_if_excuse_not_found(excuse_id)
        session = db_session.create_session()
        excuse = session.get(Excuse, excuse_id)
        
        data = excuse.to_dict(only=(
            'id', 'author', 'content', 'rating', 'is_prime', 
            'profession_relation.id', 'profession_relation.name'
        ))
        session.close()
        return jsonify({'excuse': data})

    def delete(self, excuse_id):
        abort_if_excuse_not_found(excuse_id)
        session = db_session.create_session()
        excuse = session.get(Excuse, excuse_id)
        session.delete(excuse)
        session.commit()
        session.close()
        return jsonify({'success': 'OK'})


class ExcusesListResource(Resource):
    def get(self):
        session = db_session.create_session()
        prof = request.args.get('profession') 
        
        if prof:
            excuses = session.query(Excuse).join(Excuse.profession_relation).filter(Profession.name == prof).all()
        else:
            excuses = session.query(Excuse).all()
            
        result = [
            item.to_dict(only=(
                'id', 'author', 'content', 'rating', 'is_prime', 
                'profession_relation.name'
            )) 
            for item in excuses
        ]
        
        session.close()
        return jsonify({'excuses': result})

    def post(self):
        args = parser.parse_args()
        session = db_session.create_session()
        
        excuse = Excuse(
            id=args.get('id'),
            author=args['author'],
            content=args['content'],
            rating=args['rating'],
            is_prime=args['is_prime'],
            profession_id=args['profession_id']
        )
        session.add(excuse)
        session.commit()
        
        res_id = excuse.id
        session.close()
        return jsonify({'id': res_id})
