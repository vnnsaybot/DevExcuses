from flask import render_template, Flask, redirect, url_for, request 
from sqlalchemy import func
from data import db_session
from data.__all_models import Excuse, Comment
from data import excuse_resources
from flask_restful import Api

app = Flask(__name__, template_folder='static/templates')
app.config['SECRET_KEY'] = 'hardhardhard'
api = Api(app)

# Главная
@app.route("/", methods=['GET', 'POST'])
def main():
    session = db_session.create_session()
    random_excuse = session.query(Excuse).order_by(func.random()).first()
    comments = session.query(Comment).filter_by(excuse=random_excuse.id).all()
    return render_template("main.html", excuse=random_excuse, comments=comments )

# Конкретная отмазка
@app.route("/excuse/<int:excuse_id>")
def show_excuse(excuse_id):
    session = db_session.create_session()
    excuse = session.get(Excuse, excuse_id)
    if not excuse:
        return redirect(url_for('main'))
    comments = session.query(Comment).filter_by(excuse=excuse.id).all()
    return render_template("main.html", excuse=excuse, comments=comments)

# лайк
@app.route("/vote/<int:excuse_id>/<string:action>", methods=['POST'])
def vote(excuse_id, action):
    session = db_session.create_session()
    excuse = session.get(Excuse, excuse_id)
    if excuse:
        if action == "up":
            excuse.rating += 1
        elif action == "down":
            excuse.rating -= 1
        session.commit()
    return redirect(url_for('show_excuse', excuse_id=excuse_id))


if __name__ == '__main__':
    db_session.global_init("db/blogs.db")
    api.add_resource(excuse_resources.ExcusesListResource, "/api/excuses/")
    api.add_resource(excuse_resources.ExcuseResource, "/api/excuses/<excuses_id>")
    app.run(host='127.0.0.1', port=8080, debug=True)
