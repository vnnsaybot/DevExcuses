from flask import render_template, Flask, redirect, url_for, request, session
from sqlalchemy import func
from data import db_session
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from data import excuse_resources, user_resources, comments_resources
from data.__all_models import Excuse, Comment, User
from flask_restful import Api

app = Flask(__name__, template_folder='static/templates')
app.config['SECRET_KEY'] = 'hardhardhard'
api = Api(app)
login_manager = LoginManager()
login_manager.init_app(app)


# Главная
@app.route("/", methods=['GET', 'POST'])
def main():
    db_sess = db_session.create_session()
    
    selected_prof = request.form.get('profession')
    query = db_sess.query(Excuse)

    if selected_prof:
        query = query.filter(Excuse.profession == selected_prof)
    
    random_excuse = query.order_by(func.random()).first()
    if random_excuse:
        comments = db_sess.query(Comment).filter_by(excuse=random_excuse.id).all()
    else:
        comments = []
    
    db_sess.close()
    return render_template("main.html", excuse=random_excuse, comments=comments)


# Конкретная отмазка
@app.route("/excuse/<int:excuse_id>")
def show_excuse(excuse_id):
    session = db_session.create_session()
    excuse = session.get(Excuse, excuse_id)
    if not excuse:
        return redirect(url_for('main'))
    comments = session.query(Comment).filter_by(excuse=excuse.id).all()
    session.close()
    return render_template("main.html", excuse=excuse, comments=comments)


# лайк
@app.route("/vote/<int:excuse_id>/<string:action>", methods=['POST'])
def vote(excuse_id, action):
    if 'voted_excuses' not in session:
        session['voted_excuses'] = {}
    
    voted_excuses = dict(session['voted_excuses'])
    excuse_key = str(excuse_id)
    previous_action = voted_excuses.get(excuse_key)
    
    db_sess = db_session.create_session()
    
    try:
        excuse = db_sess.get(Excuse, excuse_id)
        if excuse:
            if previous_action == action:
                if action == "up":
                    excuse.rating -= 1
                elif action == "down":
                    excuse.rating += 1
                db_sess.commit()
                
                voted_excuses.pop(excuse_key, None)
                session['voted_excuses'] = voted_excuses
                return redirect(url_for('show_excuse', excuse_id=excuse_id))
            
            if previous_action:
                if previous_action == "up":
                    excuse.rating -= 1
                elif previous_action == "down":
                    excuse.rating += 1
            
            if action == "up":
                excuse.rating += 1
            elif action == "down":
                excuse.rating -= 1
            
            if excuse.rating >= 30:
                excuse.is_prime = True
            else:
                excuse.is_prime = False
                
            db_sess.commit()
            voted_excuses[excuse_key] = action
            session['voted_excuses'] = voted_excuses

    finally:
        db_sess.close()

    return redirect(url_for('show_excuse', excuse_id=excuse_id))



# коммент
@app.route("/comment/add/<int:excuse_id>/<string:author>", methods=['POST'])
@login_required
def commentadd(excuse_id, author):
    session = db_session.create_session()
    text = request.form.get('text')
    comment = Comment(author=author, content=text, excuse=excuse_id)
    session.add(comment)
    session.commit()
    return redirect(url_for('show_excuse', excuse_id=excuse_id))

# регистрация
@app.route("/register", methods=['GET', 'POST'])
def register():
    if request.method == 'GET':
        return render_template("register.html")
    
    username = request.form.get('username')
    email = request.form.get('email')
    password = request.form.get('password')
    
    session = db_session.create_session()

    user_exists = session.query(User).filter(
        (User.email == email) | (User.username == username)
    ).first()

    if user_exists:
        return "Такой пользователь уже есть! <a href='/login'>Назад</a>"

    user = User(
        username=username,
        email=email
    )
    user.set_password(password)
    
    session.add(user)
    session.commit()

    login_user(user)
    
    print("готово")
    return redirect(url_for('main'))

# Логин
@login_manager.user_loader
def load_user(user_id):
    session = db_session.create_session()
    return session.get(User, int(user_id))

@app.route("/login", methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        return render_template("login.html")
    
    login_data = request.form.get('email') 
    password = request.form.get('password')
    
    session = db_session.create_session()
    
    user = session.query(User).filter(
        (User.email == login_data) | (User.username == login_data)
    ).first()
    
    print(login_data) 
    
    if user:
        print(f"Пользователь найден: {user.username}")
        if user.check_password(password):
            login_user(user, remember=True)
            return redirect("/")
        else:
            print("Пароль НЕ совпал")
    else:
        print("Пользователь НЕ найден в БД")
        
    return "неверный логин или пароль <a href='/login'>Назад</a>"

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect("/")

# добавление отмазки
@app.route("/add", methods=['GET', 'POST'])
@login_required
def add():
    if request.method == 'GET':
        return render_template("adder.html")
    
    db_sess = db_session.create_session()
    
    content = request.form.get('content')
    selected_prof = request.form.get('profession')

    excuse = Excuse(
        author=current_user.username,
        content=content,
        rating=0,
        is_prime=0,
        profession=selected_prof
    )
    
    db_sess.add(excuse)
    db_sess.commit()
    generated_id = excuse.id
    db_sess.close()
    
    return redirect(url_for('show_excuse', excuse_id=generated_id))

if __name__ == '__main__':
    db_session.global_init("db/blogs.db")
    api.add_resource(excuse_resources.ExcusesListResource, "/api/excuses/")
    api.add_resource(excuse_resources.ExcuseResource, "/api/excuses/<excuses_id>")
    api.add_resource(user_resources.UserResource, '/api/users')
    api.add_resource(comments_resources.CommentsListResource, '/api/comments/<comment_id>')

    app.run(host='127.0.0.1', port=8081, debug=True)
