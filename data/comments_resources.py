from flask import jsonify, request
from flask_restful import reqparse, abort, Resource
from . import db_session
from .__all_models import Comment

parser = reqparse.RequestParser()
parser.add_argument('id', required=False, type=int)
parser.add_argument('author', required=True, type=str)
parser.add_argument('content', required=True, type=str)
parser.add_argument('excuse', required=True, type=int)

def abort_if_comment_not_found(comment_id):
    session = db_session.create_session()
    comment = session.get(Comment, comment_id)
    if not comment:
        abort(404, message=f"Comment {comment_id} not found")

class CommentResource(Resource):
    def get(self, comment_id):
        abort_if_comment_not_found(comment_id)
        session = db_session.create_session()
        comment = session.get(Comment, comment_id)
        return jsonify({'comment': comment.to_dict(
            only=('id', 'author', 'content', 'excuse'))})

    def delete(self, comment_id):
        abort_if_comment_not_found(comment_id)
        session = db_session.create_session()
        comment = session.get(Comment, comment_id)
        session.delete(comment)
        session.commit()
        return jsonify({'success': 'OK'})

class CommentsListResource(Resource):
    def get(self):
        session = db_session.create_session()
        
        excuse_id = request.args.get('excuse_id')
        if excuse_id:
            comments = session.query(Comment).filter(Comment.excuse == excuse_id).all()
        else:
            comments = session.query(Comment).all()
            
        return jsonify({'comments': [item.to_dict(
            only=('id', 'author', 'content', 'excuse')) for item in comments]})

    def post(self):
        args = parser.parse_args()
        session = db_session.create_session()
        comment = Comment(
            author=args['author'],
            content=args['content'],
            excuse=args['excuse']
        )
        session.add(comment)
        session.commit()
        return jsonify({'id': comment.id, 'success': 'OK'})