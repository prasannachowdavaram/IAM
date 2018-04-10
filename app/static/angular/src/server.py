import os
from flask import Flask
from flask import redirect
from flask import request
from flask import render_template
from flask import url_for
from flask import Response
from flask import send_from_directory
from flask_login import LoginManager, UserMixin, \
login_required, login_user, logout_user, current_user

from sqlalchemy import create_engine, MetaData, Table
import json

from pandas import read_sql_table

from sqlalchemy import event

# def init_search_path(connection, conn_record):
#     cursor = connection.cursor()
#     try:
#         cursor.execute('ALTER USER prasanna WITH DEFAULT_SCHEMA=db_access_admin;')
#     finally:
#         cursor.close()



engine = create_engine('mssql+pyodbc://prasanna:prasanna@IAM')
# event.listen(engine, 'connect', init_search_path)
# table = 'assets'
# metadata = MetaData(bind=engine)
# con = engine.connect()

# # Add all the table names here.
# assets = Table('IAM1.dbo.ASSETS', metadata, autoload=True)


# df = read_sql_table(table, con=engine)

app = Flask(__name__)

# Change these value if login credentials for admin user needs to be changed.
ADMIN_USERNAME = 'admin'
ADMIN_PASSWORD = 'admin'

# config
app.config.update(
    DEBUG = True,
    SECRET_KEY = 'secret_xxx'
)

# flask-login
login_manager = LoginManager()
login_manager.init_app(app)

# Basic user model. Just supports admin.
class User(UserMixin):

    def __init__(self, id):
        self.id = id
        self.name = ADMIN_USERNAME
        self.password = ADMIN_PASSWORD

    def __repr__(self):
        return "%d/%s/%s" % (self.id, self.name, self.password)

@app.route("/", methods=['GET', 'POST'])
def index():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if (username == ADMIN_USERNAME and password == ADMIN_PASSWORD):
            user = User(1)
            login_user(user)
            return redirect(url_for('dashboard'))
        else:
            return "Wrong Credentials"
    return Response('''
        <form action="" method="post">
            <p><input type=text name=username>
            <p><input type=password name=password>
            <p><input type=submit value=Login>
        </form>
        ''')

@app.route("/dashboard", methods=['GET', 'POST'])
@login_required
def dashboard():
    return send_from_directory("./app/", "index.html")


@app.route('/<path:path>')
def files(path):
    return app.send_static_file(os.path.join('.', path).replace('\\','/'))
    # return send_from_directory('./'.replace('\\', '/'), path.replace('\\','/'))

@app.route("/logout")
@login_required
def logout():
    logout_user()
    return Response('<p>Logged out</p>')


@app.route("/api/assets", methods=['GET'])
def get_assets():
    # Both of the queries below does the same thing.
    # assets.select(assets.c.id == 1).execute().first()
    # r = engine.execute('select * from assets where id = :1', [1]).first()
    return json.dumps({'id': 'test_response'})


# Callback to reload the user object. More details at
# https://flask-login.readthedocs.io/en/latest/#how-it-works.
@login_manager.user_loader
def load_user(userid):
    return User(userid)

if __name__ == "__main__":
    app.run()
