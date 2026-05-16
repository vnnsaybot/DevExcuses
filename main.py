import os
from flask import render_template, Flask, redirect, url_for, request, session
from sqlalchemy import func
from data import db_session
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from data import excuse_resources, comments_resources, profession_resources 
from data.__all_models import Excuse, Comment, User, Profession
from flask_restful import Api
from waitress import serve

app = Flask(__name__, template_folder='static/templates')
app.config['SECRET_KEY'] = 'hardhardhard'
api = Api(app)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

def first_start():
    db_sess = db_session.create_session()
    if db_sess.query(Profession).first():
        db_sess.close()
        return 
    
    profs = [
        Profession(name="frontend", title="Frontend Developer"),
        Profession(name="backend", title="Backend Developer"),
        Profession(name="devops", title="DevOps Engineer"),
        Profession(name="manager", title="Project Manager")
    ]
    db_sess.add_all(profs)
    db_sess.commit()
    db_sess.close()

@login_manager.user_loader
def load_user(user_id):
    db_sess = db_session.create_session()
    user = db_sess.get(User, int(user_id))
    db_sess.close()
    return user


# Главная страница
@app.route("/", methods=['GET', 'POST'])
def main():
    db_sess = db_session.create_session()
    all_professions = db_sess.query(Profession).all()
    selected_prof_name = request.form.get('profession')
    
    query = db_sess.query(Excuse)

    if selected_prof_name:
        query = query.join(Profession).filter(Profession.name == selected_prof_name)
    
    random_excuse = query.order_by(func.random()).first()

    if random_excuse and random_excuse.is_prime == False:
        another_attempt = query.order_by(func.random()).first()
        if another_attempt:
            random_excuse = another_attempt

    comments = []
    if random_excuse:
        comments = db_sess.query(Comment).filter_by(excuse=random_excuse.id).all()
    
    db_sess.close()
    return render_template("main.html", 
                           excuse=random_excuse, 
                           comments=comments, 
                           professions=all_professions)


# Конкретная отмазка
@app.route("/excuse/<int:excuse_id>")
def show_excuse(excuse_id):
    db_sess = db_session.create_session()
    excuse = db_sess.get(Excuse, excuse_id)
    
    if not excuse:
        db_sess.close()
        return redirect(url_for('main'))
    
    comments = db_sess.query(Comment).filter_by(excuse=excuse.id).all()
    all_professions = db_sess.query(Profession).all()
    
    db_sess.close()
    return render_template("main.html", 
                           excuse=excuse, 
                           comments=comments, 
                           professions=all_professions)


# Система голосования
@app.route("/vote/<int:excuse_id>/<string:action>", methods=['POST'])
def vote(excuse_id, action):
    if 'voted_excuses' not in session:
        session['voted_excuses'] = {}
    
    voted_excuses = dict(session['voted_excuses'])
    excuse_key = str(excuse_id)
    previous_action = voted_excuses.get(excuse_key)
    
    db_sess = db_session.create_session()
    excuse = db_sess.get(Excuse, excuse_id)
    
    if excuse:
        if previous_action == action:
            if action == "up":
                excuse.rating -= 1
            elif action == "down":
                excuse.rating += 1
            voted_excuses.pop(excuse_key, None)
        else:
            if previous_action:
                if previous_action == "up":
                    excuse.rating -= 1
                elif previous_action == "down":
                    excuse.rating += 1
            
            if action == "up":
                excuse.rating += 1
            elif action == "down":
                excuse.rating -= 1
            
            voted_excuses[excuse_key] = action
        
        excuse.is_prime = (excuse.rating >= 30)
        
        db_sess.commit()
        session['voted_excuses'] = voted_excuses
    
    db_sess.close()
    return redirect(url_for('show_excuse', excuse_id=excuse_id))


# Добавление комментария
@app.route("/comment/add/<int:excuse_id>/<string:author>", methods=['POST'])
@login_required
def commentadd(excuse_id, author):
    db_sess = db_session.create_session()
    text = request.form.get('text')
    
    if text:
        comment = Comment(author=author, content=text, excuse=excuse_id)
        db_sess.add(comment)
        db_sess.commit()
    
    db_sess.close()
    return redirect(url_for('show_excuse', excuse_id=excuse_id))


# Страница регистрации
@app.route("/register", methods=['GET', 'POST'])
def register():
    if request.method == 'GET':
        return render_template("register.html")
    
    username = request.form.get('username')
    email = request.form.get('email')
    password = request.form.get('password')
    
    db_sess = db_session.create_session()
    if db_sess.query(User).filter((User.email == email) | (User.username == username)).first():
        db_sess.close()
        return "Пользователь уже существует! <a href='/register'>Назад</a>"

    user = User(username=username, email=email)
    user.set_password(password)
    db_sess.add(user)
    db_sess.commit()
    
    login_user(user)
    db_sess.close()
    return redirect("/")


# Страница логина
@app.route("/login", methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        return render_template("login.html")
    
    login_data = request.form.get('email')
    password = request.form.get('password')
    
    db_sess = db_session.create_session()
    user = db_sess.query(User).filter((User.email == login_data) | (User.username == login_data)).first()
    
    if user and user.check_password(password):
        login_user(user, remember=True)
        db_sess.close()
        return redirect("/")
    
    db_sess.close()
    return "Неверный логин или пароль <a href='/login'>Назад</a>"


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect("/")


# Добавление новой отмазки
@app.route("/add", methods=['GET', 'POST'])
@login_required
def add():
    db_sess = db_session.create_session()
    
    if request.method == 'GET':
        all_profs = db_sess.query(Profession).all()
        db_sess.close()
        return render_template("adder.html", professions=all_profs)
    
    content = request.form.get('content')
    selected_prof_name = request.form.get('profession')

    prof_object = db_sess.query(Profession).filter(Profession.name == selected_prof_name).first()

    if not prof_object:
        return "Ошибка: Профессия не найдена", 400

    excuse = Excuse(
        author=current_user.username,
        content=content,
        rating=0,
        is_prime=False,
        profession_id=prof_object.id 
    )
    
    db_sess.add(excuse)
    db_sess.commit()
    generated_id = excuse.id
    db_sess.close()
    
    return redirect(url_for('show_excuse', excuse_id=generated_id))

if __name__ == '__main__':
    db_session.global_init("db/blogs.db")
    first_start()
    
    api.add_resource(excuse_resources.ExcusesListResource, "/api/excuses")
    api.add_resource(excuse_resources.ExcuseResource, "/api/excuses/<int:excuse_id>")
    api.add_resource(comments_resources.CommentsListResource, '/api/comments/')
    api.add_resource(comments_resources.CommentResource, '/api/comments/<int:comment_id>')
    api.add_resource(profession_resources.ProfessionListResource, '/api/professions/')
    api.add_resource(profession_resources.ProfessionResource, '/api/professions/<int:profession_id>')

    # app.run(host='127.0.0.1', port=8080, debug=True)
    serve(app, host='127.0.0.1', port=8081)