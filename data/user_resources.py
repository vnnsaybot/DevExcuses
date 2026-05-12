from flask import jsonify
from flask_restful import Resource, reqparse
from . import db_session
from .__all_models import User

parser = reqparse.RequestParser()
parser.add_argument('username', required=True)
parser.add_argument('email', required=True)
parser.add_argument('password', required=True)

class UserResource(Resource):
    def post(self):
        args = parser.parse_args()
        session = db_session.create_session()
        
        if session.query(User).filter(User.email == args['email']).first():
            return jsonify({'error': 'User already exists'})

        user = User(username=args['username'], email=args['email'])
        user.set_password(args['password'])
        
        session.add(user)
        session.commit()
        return jsonify({'success': 'OK', 'id': user.id})