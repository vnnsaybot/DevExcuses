from flask import Flask, render_template
from data import db_session, excuse_resources


app = Flask(__name__, template_folder='static/templates')
app.config['SECRET_KEY'] = 'hardhardhard'

@app.route("/")
def main():
    return render_template("main.html")


if __name__ == '__main__':
    db_session.global_init("db/blogs.db")
    app.run(host='127.0.0.1', port=8080, debug=True)
