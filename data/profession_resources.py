from flask import jsonify
from flask_restful import reqparse, abort, Resource
from . import db_session
from .__all_models import Profession

parser = reqparse.RequestParser()
parser.add_argument('name', required=True, type=str)
parser.add_argument('title', required=True, type=str)

def abort_if_profession_not_found(profession_id):
    session = db_session.create_session()
    profession = session.get(Profession, profession_id)
    if not profession:
        abort(404, message=f"Profession {profession_id} not found")

class ProfessionResource(Resource):
    def get(self, profession_id):
        abort_if_profession_not_found(profession_id)
        session = db_session.create_session()
        profession = session.get(Profession, profession_id)
        return jsonify({'profession': profession.to_dict(
            only=('id', 'name', 'title'))})

    def delete(self, profession_id):
        abort_if_profession_not_found(profession_id)
        session = db_session.create_session()
        profession = session.get(Profession, profession_id)
        session.delete(profession)
        session.commit()
        return jsonify({'success': 'OK'})

class ProfessionListResource(Resource):
    def get(self):
        session = db_session.create_session()
        professions = session.query(Profession).all()
        return jsonify({'professions': [item.to_dict(
            only=('id', 'name', 'title')) for item in professions]})

    def post(self):
        args = parser.parse_args()
        session = db_session.create_session()
        
        if session.query(Profession).filter(Profession.name == args['name']).first():
            return jsonify({'error': 'Profession name already exists'})

        profession = Profession(
            name=args['name'],
            title=args['title']
        )
        session.add(profession)
        session.commit()
        return jsonify({'id': profession.id, 'success': 'OK'})