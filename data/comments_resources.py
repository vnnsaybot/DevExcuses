from flask import jsonify
from flask_restful import reqparse, abort, Resource

from . import db_session
from .__all_models import Excuse, Comment


parser = reqparse.RequestParser()
parser.add_argument('id', required=False, type=int)
parser.add_argument('author', required=True, type=str)
parser.add_argument('content', required=True, type=str)
parser.add_argument('excuse', required=True, type=int)



def abort_if_comment_not_found(comments_id):
    session = db_session.create_session()
    jobs = session.get(Comment, comments_id)
    if not jobs:
        abort(404, message=f"comments {comments_id} not found")


class CommentResource(Resource):
    def get(self, comment_id):
        abort_if_comment_not_found(comment_id)
        session = db_session.create_session()
        comment = session.get(Excuse, comment_id)
        return jsonify({'comment': comment.to_dict(
            only=('id', 'author', 'content', 'excuse'))})

    def delete(self, comment_id):
        abort_if_comment_not_found(comment_id)
        session = db_session.create_session()
        comment = session.get(Excuse, comment_id)
        session.delete(comment)
        session.commit()
        return jsonify({'success': 'OK'})


class CommentsListResource(Resource):
    def get(self):
        session = db_session.create_session()
        comments = session.query(Comment).all()
        return jsonify({'comment': [item.to_dict(
            only=('id', 'author', 'content', 'excuse')) for item in comments]})

    def post(self):
        args = parser.parse_args()
        comment = Comment(
            id=args.get('id'),
            author=args['author'],
            content=args['content'],
            excuse=args['excuse'],
        )
        session = db_session.create_session()
        session.add(comment)
        session.commit()
        return jsonify({'id': comment.id})
